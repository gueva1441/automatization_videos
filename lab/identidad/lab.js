/* lab.js — Laboratorio de identidad (F3). Vanilla, sin build.
 * §A: historia (palabras Whisper + audio + tira de fotos) + preview real (<hyperframes-player>) del plan. */
"use strict";

// Nombres en español de los bloques (el técnico va en gris). §B los pasa a catalogo.json.
const NOMBRES = {
  title_card: "Título de capítulo", data_callout: "Dato", source_tag: "Fuente", count_up: "Contador",
  archive_clipping: "Recorte de archivo", evidence_zoom: "Zoom de evidencia", punch_in: "Golpe de zoom",
  keyword_emphasis: "Sello rojo + mood", icon_callout: "Ícono", icon_array: "Matriz de figuras",
  chapter_question: "Pregunta de cierre",
  "shot_transition:dissolve": "Fundido cruzado", "shot_transition:dip": "Fundido a negro",
  "shot_transition:flash": "Flash", "shot_transition:cut_punch": "Corte + golpe", "shot_transition:cut": "Corte",
};
const MOODS = { veneno_enfermedad: "veneno", agua: "agua", muerte: "muerte", oscuridad_encierro: "oscuridad" };

const $ = (sel) => document.querySelector(sel);
const S = { story: null, plan: null, cues: [], wordEls: [], photoEls: [], playing: false, busy: false };

function fmt(t) {
  t = Math.max(0, t || 0);
  const m = Math.floor(t / 60), s = (t % 60).toFixed(1).padStart(4, "0");
  return `${String(m).padStart(2, "0")}:${s}`;
}
function nombre(block) {
  if (NOMBRES[block]) return NOMBRES[block];
  const [b, cat] = block.split(":");
  if (b === "keyword_emphasis" || b === "icon_callout") return `${NOMBRES[b]} (${MOODS[cat] || cat})`;
  return block;
}
function kindClass(block) {
  if (block.startsWith("shot_transition")) return "k-trans";
  if (block === "punch_in" || block === "evidence_zoom") return "k-zoom";
  return "k-text";
}
function setStatus(msg, cls = "") { const el = $("#status"); el.textContent = msg; el.className = "status " + cls; }

async function api(path, body) {
  const r = await fetch(path, body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || r.statusText);
  return j;
}

// ── Historia
function renderStory() {
  const box = $("#words");
  box.innerHTML = "";
  S.wordEls = S.story.words.map((w) => {
    const el = document.createElement("span");
    el.className = "w";
    el.textContent = w.word;
    el.title = fmt(w.start);
    el.addEventListener("click", () => { seek(w.start); selectWord(el); });
    box.appendChild(el);
    box.appendChild(document.createTextNode(" "));
    return el;
  });
  const strip = $("#strip");
  strip.innerHTML = "";
  S.photoEls = S.story.photos.map((p) => {
    const el = document.createElement("div");
    el.className = "ph";
    el.title = `Foto ${p.idx + 1} · ${fmt(p.start)}–${fmt(p.end)} · ${p.rank}${p.safe ? " · movimiento seguro" : ""}`;
    el.innerHTML = (p.thumb ? `<img loading="lazy" src="${p.thumb}" alt="">` : `<img alt="">`) +
      `<span class="n">${p.idx + 1}</span><span class="t">${fmt(p.start)}–${fmt(p.end)}</span>`;
    el.addEventListener("click", () => seek(p.start + 0.05));
    strip.appendChild(el);
    return el;
  });
}
function selectWord(el) {
  S.wordEls.forEach((w) => w.classList.remove("sel"));
  el.classList.add("sel");
}

// palabra más cercana a t (la que está sonando o la próxima)
function wordIndexAt(t) {
  const ws = S.story.words;
  let lo = 0, hi = ws.length - 1, ans = -1;
  while (lo <= hi) { const m = (lo + hi) >> 1; if (ws[m].start <= t) { ans = m; lo = m + 1; } else hi = m - 1; }
  return ans;
}

function markCues() {
  S.wordEls.forEach((el) => { el.classList.remove("cue", "k-zoom", "k-trans", "k-text"); el.removeAttribute("data-cue"); });
  for (const c of S.cues) {
    const i = Math.max(0, wordIndexAt(c.t + 0.05));
    const el = S.wordEls[i];
    if (!el) continue;
    el.classList.add("cue", kindClass(c.block));
    el.title = `${fmt(S.story.words[i].start)} · ${nombre(c.block)}${c.text ? " · " + c.text : ""}`;
  }
  const ol = $("#cues");
  ol.innerHTML = "";
  for (const c of S.cues) {
    const li = document.createElement("li");
    li.innerHTML = `<span class="when">${fmt(c.t)}</span>${nombre(c.block)}` +
      (c.text ? ` — <em></em>` : "") + `<span class="tech">${c.block}</span>`;
    if (c.text) li.querySelector("em").textContent = c.text;
    li.addEventListener("click", () => seek(c.t));
    c.el = li;
    ol.appendChild(li);
  }
}

// ── Escena (player)
const player = () => $("#player");
const narr = () => $("#narr");
// La narración es un <audio> del lab que SIGUE al player (fuente de verdad = currentTime del player).
const DRIFT_MAX = 0.08;
function syncAudio(force = false) {
  const p = player(), a = narr();
  const t = p.currentTime || 0;
  if (p.paused) { if (!a.paused) a.pause(); if (force) a.currentTime = t; return; }
  if (force || Math.abs(a.currentTime - t) > DRIFT_MAX) a.currentTime = t;
  if (a.paused) a.play().catch(() => setStatus("el navegador bloqueó el audio: tocá ▶ Play", "err"));
}
function seek(t) {
  const p = player();
  t = Math.max(0, Math.min(t, S.story.duration - 0.05));
  try { p.seek(t); } catch (e) { p.currentTime = t; }
  syncAudio(true);
  tick(true);
}
function togglePlay() {
  const p = player();
  if (p.paused) { p.play(); } else { p.pause(); }
  syncAudio(true);
  syncPlayButton();
}
function syncPlayButton() { $("#btn-play").textContent = player().paused ? "▶ Play" : "❚❚ Pausa"; }

let lastWord = -2, lastPhoto = -2;
function tick(force = false) {
  const p = player();
  const t = p.currentTime || 0;
  const d = S.story.duration;
  $("#tc").textContent = `${fmt(t)} / ${fmt(d)}`;
  if (!S.scrubbing) $("#scrub").value = String(Math.round((t / d) * 1000));
  const wi = wordIndexAt(t);
  if (wi !== lastWord || force) {
    S.wordEls.forEach((el, i) => { el.classList.toggle("now", i === wi); el.classList.toggle("past", i < wi); });
    const el = S.wordEls[wi];
    if (el && !p.paused) el.scrollIntoView({ block: "nearest" });
    lastWord = wi;
  }
  const pi = S.story.photos.findIndex((ph) => ph.start <= t && t < ph.end);
  if (pi !== lastPhoto || force) { S.photoEls.forEach((el, i) => el.classList.toggle("now", i === pi)); lastPhoto = pi; }
  const active = S.cues.filter((c) => c.t <= t && t < c.t + Math.max(c.dur, 0.4));
  S.cues.forEach((c) => c.el && c.el.classList.toggle("now", active.includes(c)));
  $("#now-line").innerHTML = active.map((c) => `<span class="chip">${nombre(c.block)}</span>`).join("") || "&nbsp;";
}
function loop() { tick(); syncAudio(); syncPlayButton(); requestAnimationFrame(loop); }

// ── Preview: plan → plantillas reales → nuevo src (se conserva el instante)
async function preview() {
  if (S.busy) return;
  S.busy = true;
  setStatus("generando preview…", "busy");
  const p = player();
  const t = p.currentTime || 0;
  const wasPlaying = !p.paused;
  try {
    const r = await api("/preview", { plan: S.plan });
    S.cues = r.cues;
    markCues();
    await loadSrc(r.src, t, wasPlaying);
    setStatus(`preview listo (${r.ms} ms)`);
  } catch (e) {
    setStatus("error: " + e.message, "err");
  } finally { S.busy = false; }
}
function loadSrc(src, t, play) {
  return new Promise((resolve) => {
    const p = player();
    let fired = false;
    const done = () => {
      if (fired) return;
      fired = true;
      p.removeEventListener("ready", done);
      if (t > 0) seek(t);
      if (play) p.play();
      syncPlayButton();
      resolve();
    };
    p.addEventListener("ready", done);
    p.pause();
    syncAudio(true);
    p.setAttribute("src", src);
    setTimeout(done, 15000);             // si "ready" no llega, no colgar el lab
  });
}

async function backToDirector() {
  const r = await api("/api/plan?origin=director");
  S.plan = r.plan;
  await api("/api/plan", { plan: S.plan });
  await preview();
}

async function init() {
  try {
    S.story = await api("/api/story");
    $("#cap-label").textContent = `· ${S.story.cap} · ${S.story.video_id.slice(0, 8)}… · ${fmt(S.story.duration)}`;
    const pr = await api("/api/plan");
    S.plan = pr.plan;
    renderStory();
    const p = player();
    ["play", "pause", "ended"].forEach((ev) => p.addEventListener(ev, syncPlayButton));
    $("#btn-play").addEventListener("click", togglePlay);
    $("#btn-preview").addEventListener("click", preview);
    $("#btn-director").addEventListener("click", backToDirector);
    const sc = $("#scrub");
    sc.addEventListener("input", () => { S.scrubbing = true; seek((sc.value / 1000) * S.story.duration); });
    sc.addEventListener("change", () => { S.scrubbing = false; });
    document.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
      if (e.code === "Space") { e.preventDefault(); togglePlay(); }
    });
    await preview();
    requestAnimationFrame(loop);
  } catch (e) {
    setStatus("error al cargar: " + e.message, "err");
  }
}
init();
