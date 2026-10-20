/* lab.js — Laboratorio de identidad (F3). Vanilla, sin build.
 * NÚCLEO (estado, mutate/deshacer, preview, player + narración, guardado, resumen) + la vista "experto" (§A–§C).
 * §F: la vista por defecto es foto por foto (lab_foto.js define window.LAB_UI); la experta queda en experto.html.
 * §A: historia (palabras Whisper + audio + tira de fotos) + preview real (<hyperframes-player>) del plan.
 * §B: catálogo (catalogo.json) con hints, "Probar sugerencia" y atributos; sugerencias_ch02.json en gris;
 *     panel "Aquí" al hacer clic en una palabra o una foto. Todo cambio pasa por mutate(). */
"use strict";

const $ = (sel, root = document) => root.querySelector(sel);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const clone = (o) => JSON.parse(JSON.stringify(o));

const S = {
  story: null, plan: null, tokens: {}, anotado: {}, sugState: {}, rules: {}, catalog: null, sugs: [], ctx: null,
  cues: [], rejected: [], wordEls: [], photoEls: [], tab: "sugerencias", here: null, busy: false, queued: false,
  history: [], future: [],
  // §C: casillas, léxico, lo que falta, piezas tocadas, cómo deshacer cada sugerencia
  marks: {}, lexicon: {}, faltan: "", touched: [], sugUndo: {},
  // §F: objetos de cada foto (aprobado / rechazado / forma elegida), foto actual, fotos vistas
  obj: {}, fotoActual: 0, visitadas: [],
};
const STATE_KEYS = ["plan", "tokens", "anotado", "sugState", "marks", "lexicon", "faltan", "touched", "sugUndo",
                    "obj", "visitadas"];
function labState() {
  const st = { plan: S.plan, tokens: S.tokens, anotado: S.anotado, sugerencias: S.sugState, marks: S.marks,
               lexicon: S.lexicon, faltan: S.faltan, touched: S.touched, sug_undo: S.sugUndo,
               objetos: S.obj, foto_actual: S.fotoActual, visitadas: S.visitadas };
  if (UI.recorrido) st.recorrido = UI.recorrido();          // §F: resumen foto por foto (lo arma la vista)
  return st;
}
function touch(id) { if (id && !S.touched.includes(id)) S.touched.push(id); }

// ── utilidades
function fmt(t) {
  t = Math.max(0, t || 0);
  const m = Math.floor(t / 60), s = (t % 60).toFixed(1).padStart(4, "0");
  return `${String(m).padStart(2, "0")}:${s}`;
}
const MOODS = { veneno_enfermedad: "veneno", agua: "agua", muerte: "muerte", oscuridad_encierro: "oscuridad" };
const BLOCK_TO_ELEM = {
  title_card: "title_card", data_callout: "data_callout", source_tag: "source_tag", count_up: "count_up",
  archive_clipping: "archive_clipping", evidence_zoom: "punch_in", punch_in: "punch_in", keyword_emphasis: "keyword_emphasis",
  icon_callout: "icon_callout", icon_array: "icon_array", chapter_question: "chapter_question",
  "shot_transition:dissolve": "crossfade", "shot_transition:dip": "dip_to_black", "shot_transition:flash": "flash",
  "shot_transition:cut_punch": "cut", "shot_transition:cut": "cut",
};
function elemOf(block) { return BLOCK_TO_ELEM[block] || BLOCK_TO_ELEM[block.split(":")[0]] || block; }
function catEl(id) { return S.catalog.elementos.find((e) => e.id === id); }
function nombre(block) {
  if (block === "evidence_zoom") return "Zoom de evidencia";
  if (block === "source_tag") return "Fuente";
  if (block === "shot_transition:cut_punch") return "Corte + golpe";
  const el = catEl(elemOf(block));
  const [b, cat] = block.split(":");
  const base = el ? el.nombre : block;
  return (b === "keyword_emphasis" || b === "icon_callout") && cat ? `${base} (${MOODS[cat] || cat})` : base;
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
const cleanWord = (w) => w.replace(/^[¿¡"«(]+|[.,;:!?"»)]+$/g, "");
function wordIndexAt(t) {
  const ws = S.story.words;
  let lo = 0, hi = ws.length - 1, ans = -1;
  while (lo <= hi) { const m = (lo + hi) >> 1; if (ws[m].start <= t) { ans = m; lo = m + 1; } else hi = m - 1; }
  return ans;
}
const wordByI = (i) => S.story.words.find((w) => w.i === i);
const photoAt = (t) => S.story.photos.find((p) => p.start <= t && t < p.end) || S.story.photos[S.story.photos.length - 1];
const lexAt = (i) => S.ctx.lexicon_hits.find((h) => h.i === i);
const near = (a, b, tol = 0.15) => Math.abs(a - b) <= tol;

// ═══════════════════════════════════════════════════════════════
//  Estado: mutate() = snapshot (deshacer en §C) + preview + autoguardado
// ═══════════════════════════════════════════════════════════════
function snapshot() { const o = {}; STATE_KEYS.forEach((k) => { o[k] = S[k]; }); return clone(o); }
function restore(s) { Object.assign(S, clone(s)); }
function afterChange(label, opts = {}) {
  setStatus(label, opts.preview === false ? "" : "busy");
  if (opts.preview === false) autosave();           // cambio que no toca lo que se dibuja: sin recargar el player
  else schedulePreview();
  UI.afterChange();
  syncUndoButtons();
}
function mutate(label, fn, opts = {}) {
  const before = snapshot();
  fn();
  S.history.push({ state: before, label });
  if (S.history.length > 200) S.history.shift();
  S.future = [];
  afterChange(label, opts);
}
// Ctrl+Z / Ctrl+Shift+Z (o Ctrl+Y): deshacer / rehacer cualquier cambio
function undo() {
  const h = S.history.pop();
  if (!h) return setStatus("nada para deshacer");
  S.future.push({ state: snapshot(), label: h.label });
  restore(h.state);
  afterChange(`deshecho: ${h.label}`);
}
function redo() {
  const f = S.future.pop();
  if (!f) return setStatus("nada para rehacer");
  S.history.push({ state: snapshot(), label: f.label });
  restore(f.state);
  afterChange(`rehecho: ${f.label}`);
}
function syncUndoButtons() {
  $("#btn-undo").disabled = !S.history.length;
  $("#btn-redo").disabled = !S.future.length;
  $("#btn-undo").title = S.history.length ? `Deshacer: ${S.history[S.history.length - 1].label} (Ctrl+Z)` : "Nada para deshacer";
}
let saveTimer = null;
function autosave() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => api("/api/plan", labState())
    .catch((e) => setStatus("no se pudo guardar el estado: " + e.message, "err")), 400);
  refreshSummary();
}
let pvTimer = null;
function schedulePreview() { clearTimeout(pvTimer); pvTimer = setTimeout(preview, 250); }

// ── helpers de plan (estructuras iguales a las del resolver del director)
function planList(key) { if (!Array.isArray(S.plan[key])) S.plan[key] = []; return S.plan[key]; }
function addPunch(t) {
  const l = planList("punch_in");
  if (!l.some((x) => near(x, t))) { l.push(+t.toFixed(3)); l.sort((a, b) => a - b); }
}
function emphasisAt(t) { return planList("emphasis").find((e) => near(e.start, t)); }
function moodDur() { const e = planList("emphasis")[0]; return e ? e.duration : (S.rules.mood_dur || 2.5); }
function addEmphasis(i, { stamp = true, icon = false } = {}) {
  const w = wordByI(i), hit = lexAt(i);
  if (!w || !hit) throw new Error("esa palabra no está en el léxico de moods");
  if (emphasisAt(w.start)) return;
  const ph = photoAt(w.start);
  planList("emphasis").push({
    word: cleanWord(w.word), category: hit.category, layer: hit.layer, icon: icon && hit.icon ? hit.icon : null,
    icon_anim: hit.icon_anim || "stamp", start: w.start, duration: moodDur(), side: ph.quiet_side || "right",
    stamp, sid: ph.idx, rarity: 0, weight: hit.weight, icon_callout: !!(icon && hit.icon), manual: true,
  });
  S.plan.emphasis.sort((a, b) => a.start - b.start);
}
function archiveDur() { const a = (S.plan.archive_clippings || [])[0]; return a ? a.duration : 4; }
function headlineOf(text) {
  const first = text.split(/[,;:(]/)[0].replace(/\.$/, "").trim();
  return first.split(/\s+/).slice(0, 8).join(" ");
}
function addArchive(factIdx, t) {
  const f = S.ctx.facts.find((x) => x.idx === factIdx);
  if (!f) return;
  const ph = photoAt(t), year = (f.text.match(/\b(1[6-9]\d\d|20\d\d)\b/) || [])[1];
  planList("archive_clippings").push({
    kicker: year || "", headline: headlineOf(f.text), body: "", scene_idx: ph.idx, fact_idx: factIdx,
    era_decade: year ? Math.floor(+year / 10) * 10 : 2000, start: +t.toFixed(3), duration: archiveDur(),
    side: ph.quiet_side === "left" ? "left" : "right", manual: true,
  });
  S.plan.archive_clippings.sort((a, b) => a.start - b.start);
}
function setQuestion(text) {
  const d = S.story.duration;
  const prev = S.plan.chapter_question || {};
  const dur = prev.duration || 3;
  S.plan.chapter_question = text.trim()
    ? { text: text.trim(), start: +(d - dur).toFixed(3), duration: dur, keyword: "", manual: true } : null;
}

// pieza del plan detrás de un cue (para editarla o quitarla desde "Aquí")
function pieceOf(c) {
  const p = S.plan, b = c.block.split(":")[0];
  if (b === "title_card") return { key: "title_card", obj: p.title_card };
  if (b === "chapter_question") return { key: "chapter_question", obj: p.chapter_question };
  if (b === "count_up") return { key: "count_up", obj: p.count_up };
  if (b === "icon_array") return { key: "icon_array", obj: p.icon_array };
  if (b === "data_callout") return { key: "callouts", obj: (p.callouts || []).find((x) => near(x.start, c.t, 0.6) && x.text === c.text) };
  if (b === "archive_clipping") return { key: "archive_clippings", obj: (p.archive_clippings || []).find((x) => near(x.start, c.t, 0.6)) };
  if (b === "keyword_emphasis" || b === "icon_callout") return { key: "emphasis", obj: (p.emphasis || []).find((x) => near(x.start, c.t, 0.6)) };
  if (b === "punch_in") return { key: "punch_in", t: (p.punch_in || []).find((x) => near(x, c.t)) };
  return null;
}
function removePiece(c) {
  const pc = pieceOf(c);
  if (!pc) return;
  mutate(`quitado: ${nombre(c.block)}`, () => {
    if (pc.key === "punch_in") S.plan.punch_in = S.plan.punch_in.filter((x) => x !== pc.t);
    else if (Array.isArray(S.plan[pc.key])) S.plan[pc.key] = S.plan[pc.key].filter((x) => x !== pc.obj);
    else S.plan[pc.key] = null;
  });
}

// ── atributos: valor actual y aplicar
function attrValue(el, a, piece) {
  const [kind, path] = a.aplica.split(":");
  if (kind === "token") return path in S.tokens ? S.tokens[path] : S.rules[path];
  if (kind === "all") {
    const [list, field] = path.split(".");
    const first = (S.plan[list] || []).find((x) => field !== "icon_anim" || x.icon_callout);
    return first ? first[field] : a.default;
  }
  if (kind === "elem") {
    if (a.id === "usar") return !!S.plan.title_card;
    return piece && piece[path] !== undefined ? piece[path] : a.default;
  }
  return (S.anotado[el.id] || {})[a.id] ?? a.default;
}
function applyAttr(el, a, v, piece) {
  const [kind, path] = a.aplica.split(":");
  mutate(`${el.nombre}: ${a.nombre} → ${labelOf(a, v)}`, () => {
    touch(el.id);
    if (kind === "token") S.tokens[path] = v;
    else if (kind === "all") {
      const [list, field] = path.split(".");
      (S.plan[list] || []).forEach((x) => { if (field !== "icon_anim" || x.icon_callout) x[field] = v; });
    } else if (kind === "elem") {
      if (a.id === "usar") S.plan.title_card = v ? (S.plan.title_card || clone(S.directorPlan.title_card)) : null;
      else if (piece) {
        piece[path] = v;
        if (path === "icon_callout") {
          const hit = S.ctx.lexicon_hits.find((h) => near(h.start, piece.start));
          piece.icon = v && hit && hit.icon ? hit.icon : null;
          piece.icon_callout = !!piece.icon;
        }
      }
    } else (S.anotado[el.id] = S.anotado[el.id] || {})[a.id] = v;
  });
}
function labelOf(a, v) {
  const o = (a.opciones || []).find((x) => JSON.stringify(x.v) === JSON.stringify(v));
  return o ? o.label : String(v);
}
function applyPreset(el, preset) {
  for (const [k, v] of Object.entries(preset.tokens || {})) S.tokens[k] = v;
  for (const [path, v] of Object.entries(preset.all || {})) {
    const [list, field] = path.split(".");
    (S.plan[list] || []).forEach((x) => { x[field] = v; });
  }
  for (const [k, v] of Object.entries(preset.anotado || {})) {
    if (v && typeof v === "object" && !Array.isArray(v) && catEl(k)) S.anotado[k] = { ...(S.anotado[k] || {}), ...v };
    else (S.anotado[el.id] = S.anotado[el.id] || {})[k] = v;
  }
}

// ── acciones de sugerencia / ejemplo
function runAction(acc, i, el) {
  const w = i !== undefined ? wordByI(i) : null;
  const t = w ? w.start : 0;
  switch (acc.tipo || acc.accion) {
    case "add_punch": addPunch(t); break;
    case "add_emphasis": addEmphasis(i, { stamp: acc.stamp !== false, icon: !!acc.icon }); break;
    case "set_emphasis": { const e = emphasisAt(t); if (e) Object.assign(e, acc.campos || {}); break; }
    case "set_archive": {
      const a = (S.plan.archive_clippings || []).find((x) => x.fact_idx === acc.fact_idx);
      if (a) Object.assign(a, acc.campos || {});
      break;
    }
    case "add_question": S.tab = "cierre"; break;
    default: break;                                   // marca / tokens / anotado / focus
  }
  return t;
}
// cómo deshacer UNA sugerencia aunque después haya otros cambios (✖ sobre algo que se estaba probando)
function sugUndoInfo(s) {
  const w = wordByI(s.word_i), t = w ? w.start : 0, acc = s.accion, pre = s.preset || {};
  const u = { tokens: {}, anotado: [], tipo: acc.tipo, t };
  for (const [k, v] of Object.entries(pre.anotado || {})) {            // pares [elemento, atributo] con su valor previo
    if (v && typeof v === "object" && !Array.isArray(v) && catEl(k)) Object.keys(v).forEach((a) => u.anotado.push([k, a, (S.anotado[k] || {})[a] ?? null]));
    else u.anotado.push([s.elemento, k, (S.anotado[s.elemento] || {})[k] ?? null]);
  }
  for (const k of Object.keys(pre.tokens || {})) u.tokens[k] = k in S.tokens ? S.tokens[k] : null;
  if (acc.tipo === "set_emphasis") { const e = emphasisAt(t); u.old = e ? Object.fromEntries(Object.keys(acc.campos).map((k) => [k, e[k]])) : null; }
  if (acc.tipo === "set_archive") {
    const a = (S.plan.archive_clippings || []).find((x) => x.fact_idx === acc.fact_idx);
    u.old = a ? Object.fromEntries(Object.keys(acc.campos).map((k) => [k, a[k]])) : null;
  }
  if (acc.tipo === "add_emphasis") u.added = !emphasisAt(t);
  if (acc.tipo === "add_punch") u.added = !(S.plan.punch_in || []).some((x) => near(x, t));
  return u;
}
function revertSuggestion(s) {
  const u = S.sugUndo[s.id];
  if (!u) return;
  for (const [k, v] of Object.entries(u.tokens || {})) { if (v === null) delete S.tokens[k]; else S.tokens[k] = v; }
  for (const [el, a, prev] of u.anotado || []) {
    if (!S.anotado[el]) continue;
    if (prev === null) delete S.anotado[el][a]; else S.anotado[el][a] = prev;
  }
  if (u.tipo === "add_emphasis" && u.added) S.plan.emphasis = (S.plan.emphasis || []).filter((e) => !near(e.start, u.t));
  if (u.tipo === "add_punch" && u.added) S.plan.punch_in = (S.plan.punch_in || []).filter((x) => !near(x, u.t));
  if (u.tipo === "set_emphasis" && u.old) { const e = emphasisAt(u.t); if (e) Object.assign(e, u.old); }
  if (u.tipo === "set_archive" && u.old) {
    const a = (S.plan.archive_clippings || []).find((x) => x.fact_idx === s.accion.fact_idx);
    if (a) Object.assign(a, u.old);
  }
  delete S.sugUndo[s.id];
}
function trySuggestion(s) {
  const el = catEl(s.elemento);
  let t = 0;
  try {
    mutate(`probando ${s.id}: ${s.titulo}`, () => {
      if (!S.sugUndo[s.id]) S.sugUndo[s.id] = sugUndoInfo(s);
      applyPreset(el || { id: s.elemento }, s.preset || {});
      t = runAction(s.accion, s.word_i, el);
      S.sugState[s.id] = "probando";
      touch(s.elemento);
    });
  } catch (e) { setStatus(e.message, "err"); return; }
  if (UI.onTried) return UI.onTried(s, t);
  seek(t + 0.05);
  openHere({ kind: "word", i: s.word_i });
}
function decideSuggestion(s, v) {
  mutate(`${s.id} ${v === "si" ? "✔ aceptada" : "✖ rechazada"}`, () => {
    if (v === "si" && S.sugState[s.id] !== "probando") {          // aceptar sin probar = aplicarla
      if (!S.sugUndo[s.id]) S.sugUndo[s.id] = sugUndoInfo(s);
      applyPreset(catEl(s.elemento) || { id: s.elemento }, s.preset || {});
      runAction(s.accion, s.word_i, catEl(s.elemento));
    }
    if (v === "no") revertSuggestion(s);
    S.sugState[s.id] = S.sugState[s.id] === v ? (v === "si" ? "probando" : undefined) : v;
    if (S.sugState[s.id] === undefined) delete S.sugState[s.id];
  });
}
function tryCatalog(el) {
  let t = null;
  try {
    mutate(`probando: ${el.nombre}`, () => {
      touch(el.id);
      applyPreset(el, el.preset_sugerido || {});
      if (el.ejemplo_en_ch02) t = runAction(el.ejemplo_en_ch02, el.ejemplo_en_ch02.word_i, el);
    });
  } catch (e) { setStatus(e.message, "err"); return; }
  if (t !== null && el.ejemplo_en_ch02.word_i !== undefined) { seek(t + 0.05); openHere({ kind: "word", i: el.ejemplo_en_ch02.word_i }); }
}

// ═══════════════════════════════════════════════════════════════
//  Historia
// ═══════════════════════════════════════════════════════════════
function renderStory() {
  const box = $("#words");
  box.innerHTML = "";
  S.wordEls = S.story.words.map((w) => {
    const el = document.createElement("span");
    el.className = "w";
    el.textContent = w.word;
    el.dataset.i = w.i;
    const hit = lexAt(w.i);
    if (hit) { el.classList.add("lex", "lex-w" + hit.weight); el.dataset.lex = `${MOODS[hit.category] || hit.category} · peso ${hit.weight}`; }
    el.addEventListener("click", () => { seek(w.start); openHere({ kind: "word", i: w.i }); });
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
    el.addEventListener("click", () => { seek(p.start + 0.05); openHere({ kind: "photo", idx: p.idx }); });
    strip.appendChild(el);
    return el;
  });
}
function markStory() {
  S.wordEls.forEach((el) => { el.classList.remove("cue", "k-zoom", "k-trans", "k-text", "sug"); el.title = fmt(+wordByI(+el.dataset.i).start) + (el.dataset.lex ? " · léxico " + el.dataset.lex : ""); });
  for (const c of S.cues) {
    const i = Math.max(0, wordIndexAt(c.t + 0.05));
    const el = S.wordEls[i];
    if (!el) continue;
    el.classList.add("cue", kindClass(c.block));
    el.title += ` · ${nombre(c.block)}${c.text ? " · " + c.text : ""}`;
  }
  for (const s of S.sugs) {
    const el = S.wordEls.find((x) => +x.dataset.i === s.word_i);
    if (el && !S.sugState[s.id]) { el.classList.add("sug"); el.title += ` · sugerido ${s.id}: ${s.titulo}`; }
    else if (el && S.sugState[s.id] === "no") el.title += ` · ${s.id} rechazada`;
  }
  const ol = $("#cues");
  ol.innerHTML = "";
  for (const c of S.cues) {
    const li = document.createElement("li");
    li.innerHTML = `<span class="when">${fmt(c.t)}</span>${esc(nombre(c.block))}` +
      (c.text ? ` — <em>${esc(c.text)}</em>` : "") + `<span class="tech">${esc(c.block)}</span>`;
    li.addEventListener("click", () => { seek(c.t + 0.05); openHere({ kind: "word", i: S.story.words[Math.max(0, wordIndexAt(c.t + 0.05))].i }); });
    c.el = li;
    ol.appendChild(li);
  }
}

// ═══════════════════════════════════════════════════════════════
//  Panel "Aquí": qué hay en este momento y qué más podría ir
// ═══════════════════════════════════════════════════════════════
function openHere(h) { S.here = h; renderHere(); }
function hereTime() {
  if (!S.here) return 0;
  if (S.here.kind === "photo") return S.story.photos[S.here.idx].start;
  return wordByI(S.here.i).start;
}
function renderHere() {
  const box = $("#here");
  if (!S.here) { box.innerHTML = '<p class="hint">Clic en una palabra o una foto para ver qué hay ahí.</p>'; return; }
  const t = hereTime();
  const ph = photoAt(t);
  const w = S.here.kind === "word" ? wordByI(S.here.i) : null;
  const span = S.here.kind === "photo" ? [ph.start, ph.end] : [t - 0.6, t + 1.2];
  const active = S.cues.filter((c) => !c.block.startsWith("shot_transition") && c.t < span[1] && c.t + Math.max(c.dur, 0.4) > span[0]);
  const hit = w ? lexAt(w.i) : null;
  let html = `<div class="here-head">${w ? `«${esc(w.word)}»` : `Foto ${ph.idx + 1}`} <span class="tc">${fmt(t)}</span>` +
    ` <span class="tech">foto ${ph.idx + 1} · lado tranquilo: ${ph.quiet_side === "left" ? "izquierda" : "derecha"}</span></div>`;
  if (hit) {
    const key = cleanWord(hit.word).toLowerCase();
    const cur = key in S.lexicon ? S.lexicon[key] : hit.weight;
    html += `<p class="hint">Palabra del léxico: <b>${esc(MOODS[hit.category] || hit.category)}</b>${hit.icon ? ` · ícono literal: ${esc(hit.icon)}` : ""}.</p>
      <div class="attr"><span class="an">¿Dispara mood?</span><span class="opts">` +
      [[0, "nunca"], [1, "casi nunca (1)"], [2, "a veces (2)"], [3, "siempre (3)"]].map(([v, l]) =>
        `<button class="opt ${cur === v ? "on" : ""}" data-lexw="${v}">${l}</button>`).join("") +
      `</span></div><p class="nota">Cambia el peso de «${esc(key)}» en el perfil (lo usa el director en los próximos videos)${key in S.lexicon ? ` · antes: ${hit.weight}` : ""}.</p>`;
  }
  html += '<h4>Lo que hay acá</h4>';
  html += active.length ? active.map((c, k) => pieceCard(c, k)).join("") : '<p class="hint">Nada.</p>';
  html += '<h4>Qué más podría ir</h4><div class="opts">';
  if (w) html += `<button class="btn sm" data-do="punch">Golpe de zoom aquí</button>`;
  if (hit && !emphasisAt(w.start)) {
    html += `<button class="btn sm" data-do="mood">Mood ${esc(MOODS[hit.category])} + sello</button>`;
    if (hit.icon) html += `<button class="btn sm" data-do="icon">Ícono ${esc(hit.icon)}</button>`;
  }
  html += `<button class="btn sm ghost" data-do="facts">Poner recorte aquí…</button>`;
  html += '</div><div id="facts-pick" class="facts-pick" hidden></div>';
  const sugs = S.sugs.filter((s) => { const sw = wordByI(s.word_i); return sw && Math.abs(sw.start - t) < 3 && s.word_i !== 0; });
  if (sugs.length) html += '<h4>Sugerido cerca</h4>' + sugs.map(sugRow).join("");
  box.innerHTML = html;
  box.querySelectorAll("[data-do]").forEach((b) => b.addEventListener("click", () => hereAction(b.dataset.do, w, t)));
  box.querySelectorAll("[data-lexw]").forEach((b) => b.addEventListener("click", () => setLexWeight(hit, +b.dataset.lexw)));
  bindPieceCards(box, active);
  bindSugRows(box);
}
function setLexWeight(hit, v) {
  const key = cleanWord(hit.word).toLowerCase();
  mutate(`léxico «${key}» → ${v === 0 ? "apagada" : "peso " + v}`, () => {
    if (v === hit.weight) delete S.lexicon[key]; else S.lexicon[key] = v;
    if (v === 0) S.plan.emphasis = (S.plan.emphasis || []).filter((e) => !near(e.start, hit.start));   // apagar = sale del plan
    touch("keyword_emphasis");
  });
}
function pieceCard(c, k) {
  const el = catEl(elemOf(c.block));
  const pc = pieceOf(c);
  const editable = el ? el.atributos.filter((a) => a.aplica.startsWith("elem:") && a.id !== "usar" && a.tipo !== "texto") : [];
  const attrs = pc && pc.obj ? editable.map((a) => attrControl(el, a, pc.obj, `p${k}`)).join("") : "";
  return `<div class="piece" data-k="${k}"><div><b>${esc(nombre(c.block))}</b> <span class="tech">${esc(c.block)}</span>` +
    (c.text ? ` — <em>${esc(c.text)}</em>` : "") + ` <span class="tc">${fmt(c.t)} · ${c.dur.toFixed(1)} s</span>` +
    (pc ? ` <button class="btn sm ghost" data-rm="${k}">Quitar</button>` : "") + `</div>${attrs}</div>`;
}
function bindPieceCards(box, active) {
  box.querySelectorAll("[data-rm]").forEach((b) => b.addEventListener("click", () => removePiece(active[+b.dataset.rm])));
  box.querySelectorAll(".piece").forEach((div) => {
    const c = active[+div.dataset.k], el = catEl(elemOf(c.block)), pc = pieceOf(c);
    if (el && pc && pc.obj) bindAttrControls(div, el, pc.obj);
  });
}
function hereAction(what, w, t) {
  try {
    if (what === "punch") mutate(`golpe de zoom en «${w.word}»`, () => addPunch(w.start));
    else if (what === "mood") mutate(`mood en «${w.word}»`, () => addEmphasis(w.i, { stamp: true, icon: false }));
    else if (what === "icon") mutate(`ícono en «${w.word}»`, () => addEmphasis(w.i, { stamp: true, icon: true }));
    else if (what === "facts") {
      const box = $("#facts-pick");
      box.hidden = !box.hidden;
      box.innerHTML = S.ctx.facts.filter((f) => f.eligible).map((f) =>
        `<div class="fact"><button class="btn sm" data-f="${f.idx}">Recorte</button> <span class="tech">F${f.idx}</span> ${esc(headlineOf(f.text))}` +
        `<span class="tech"> · ${esc(f.text.slice(0, 90))}…</span></div>`).join("") || '<p class="hint">Sin facts elegibles.</p>';
      box.querySelectorAll("[data-f]").forEach((b) => b.addEventListener("click", () =>
        mutate(`recorte del fact ${b.dataset.f} en ${fmt(t)}`, () => addArchive(+b.dataset.f, t))));
    }
  } catch (e) { setStatus(e.message, "err"); }
}

// ═══════════════════════════════════════════════════════════════
//  Catálogo
// ═══════════════════════════════════════════════════════════════
const ESTADO_CLS = { en_vivo: "ok", parcial: "part", pipeline: "pipe", nuevo_D: "new", futuro: "fut" };
function renderTabs() {
  const tabs = [{ id: "sugerencias", nombre: "Sugerencias IA" }, ...S.catalog.tabs];
  $("#tabs").innerHTML = tabs.map((t) => `<button data-tab="${t.id}" class="${S.tab === t.id ? "on" : ""}">${esc(t.nombre)}</button>`).join("");
  $("#tabs").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { S.tab = b.dataset.tab; renderTabs(); renderCatalog(); }));
}
function renderCatalog() {
  renderTabs();
  const box = $("#catalog");
  if (S.tab === "sugerencias") {
    box.innerHTML = `<p class="hint">${esc(S.sugMeta.estado)}</p>` + S.sugs.map(sugRow).join("");
    bindSugRows(box);
    return;
  }
  let html = "", group = "";
  for (const el of S.catalog.elementos.filter((e) => e.tab === S.tab)) {
    if (el.grupo !== group) { group = el.grupo; html += `<h4 class="grp">${esc(group)}</h4>`; }
    html += elementCard(el);
  }
  if (S.tab === "cierre") html = questionBox() + html;
  if (S.tab === "global") html += faltanBox();
  box.innerHTML = html;
  box.querySelectorAll(".card").forEach((card) => {
    const el = catEl(card.dataset.id);
    bindAttrControls(card, el, null);
    const b = card.querySelector("[data-try]");
    if (b) b.addEventListener("click", () => tryCatalog(el));
    bindMarks(card, el);
  });
  bindQuestionBox(box);
  bindFaltan(box);
}
function elementCard(el) {
  const st = S.catalog.estados[el.estado] || el.estado;
  const attrs = el.atributos.filter((a) => !a.aplica.startsWith("elem:") || a.id === "usar")
    .filter((a) => a.tipo !== "texto").map((a) => attrControl(el, a, null, el.id)).join("");
  const elemAttrs = el.atributos.filter((a) => a.aplica.startsWith("elem:") && a.id !== "usar" && a.tipo !== "texto");
  const canTry = el.estado !== "futuro" && (Object.keys(el.preset_sugerido || {}).length || el.ejemplo_en_ch02);
  const m = S.marks[el.id] || {};
  return `<div class="card mark-${m.v || "none"}" data-id="${el.id}">
    <div class="card-head"><b>${esc(el.nombre)}</b> <span class="tech">${esc(el.id)}</span>
      <span class="badge ${ESTADO_CLS[el.estado] || ""}" title="${esc(el.nota_estado || st)}">${esc(st)}</span></div>
    <div class="que">${esc(el.que_hace)}</div>
    <div class="hint3"><div><span>Cuándo</span>${esc(el.hint.cuando)}</div><div><span>Dónde</span>${esc(el.hint.donde)}</div><div><span>Por qué</span>${esc(el.hint.por_que)}</div></div>
    ${el.nota_estado ? `<div class="nota">${esc(el.nota_estado)}</div>` : ""}
    ${canTry ? `<button class="btn sm" data-try="1">Probar sugerencia</button>` : ""}
    ${attrs}
    ${elemAttrs.length ? `<div class="nota">${esc(elemAttrs.map((a) => a.nombre).join(", "))}: elegí la pieza en la Historia (panel Aquí).</div>` : ""}
    ${markBox(el, m)}
  </div>`;
}
function markBox(el, m) {
  const yes = el.estado === "futuro" ? "✔ Lo quiero" : "✔ Se queda en el canal";
  return `<div class="marks">
    <button class="mk si ${m.v === "si" ? "on" : ""}" data-mark="si">${yes}</button>
    <button class="mk no ${m.v === "no" ? "on" : ""}" data-mark="no">✖ No lo quiero nunca</button>
    ${m.v === "si" ? `<input class="mk-txt" data-mtxt="regla" maxlength="140" placeholder="¿Cuándo va? (en tus palabras, opcional)" value="${esc(m.regla || "")}">` : ""}
    ${m.v === "no" ? `<input class="mk-txt" data-mtxt="por_que" maxlength="140" placeholder="¿Por qué? (opcional)" value="${esc(m.por_que || "")}">` : ""}
  </div>`;
}
function setMark(el, v) {
  mutate(`${el.nombre}: ${v === "si" ? "✔ se queda" : "✖ nunca"}`, () => {
    const cur = S.marks[el.id] || {};
    if (cur.v === v) delete S.marks[el.id];                       // segundo clic = desmarcar
    else S.marks[el.id] = { ...cur, v };
  });
}
function bindMarks(card, el) {
  card.querySelectorAll("[data-mark]").forEach((b) => b.addEventListener("click", () => setMark(el, b.dataset.mark)));
  card.querySelectorAll("[data-mtxt]").forEach((inp) => inp.addEventListener("change", () => {
    const val = inp.value.trim();
    if ((S.marks[el.id] || {})[inp.dataset.mtxt] === val) return;
    mutate(`${el.nombre}: nota`, () => { S.marks[el.id][inp.dataset.mtxt] = val; });
  }));
}
function attrControl(el, a, piece, scope) {
  const cur = attrValue(el, a, piece);
  const live = !a.aplica.startsWith("anotado");
  const tag = live ? "" : '<span class="anot" title="Se guarda en la identidad; el preview todavía no lo dibuja">anotado</span>';
  let opts = "";
  if (a.tipo === "anim") {
    opts = a.opciones.map((o) => `<button class="opt anim ${same(o.v, cur) ? "on" : ""}" data-a="${a.id}" data-v='${esc(JSON.stringify(o.v))}' title="${esc(o.label)}">
      <span class="ap-wrap"><span class="ap ap-${o.anim}">${miniContent(o.anim)}</span><span class="lbl">${esc(o.label)}</span></span></button>`).join("");
  } else if (a.tipo === "paleta") {
    opts = a.opciones.map((o) => `<button class="opt sw ${same(o.v, cur) ? "on" : ""}" data-a="${a.id}" data-v='${esc(JSON.stringify(o.v))}' title="${esc(o.label)}">
      <span class="swatch" style="background:${esc(o.color)}"></span>${esc(o.label)}</button>`).join("");
  } else {
    opts = a.opciones.map((o) => `<button class="opt ${same(o.v, cur) ? "on" : ""}" data-a="${a.id}" data-v='${esc(JSON.stringify(o.v))}'>${esc(o.label)}</button>`).join("");
  }
  return `<div class="attr" data-scope="${esc(scope)}"><span class="an">${esc(a.nombre)}</span>${tag}<span class="opts">${opts}</span></div>`;
}
function miniContent(anim) {
  if (["ink_bleed", "press_wipe", "caer", "desdoblar", "respirar", "deriva", "pulso"].includes(anim)) return '<span class="box"></span>';
  if (anim === "cascada") return '<span class="t"><span>D</span><span>A</span><span>T</span><span>O</span><span>S</span></span>';
  if (anim === "sello") return '<span class="t"><b>SELLO</b></span>';
  if (anim === "maquina") return '<span class="t">¿POR QUÉ?</span>';
  return '<span class="t">TEXTO</span>';
}
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
function bindAttrControls(root, el, piece) {
  root.querySelectorAll(".opt").forEach((b) => {
    if (b.closest(".card, .piece") !== root) return;
    b.addEventListener("click", () => {
      const a = el.atributos.find((x) => x.id === b.dataset.a);
      applyAttr(el, a, JSON.parse(b.dataset.v), piece);
    });
  });
}
function sugRow(s) {
  const st = S.sugState[s.id];
  const el = catEl(s.elemento);
  const w = wordByI(s.word_i);
  const badge = { probando: "probando", si: "✔ aceptada", no: "✖ rechazada" }[st];
  return `<div class="sugrow ${st ? "st-" + st : "st-sug"}" data-s="${s.id}">
    <div><span class="sid">${s.id}</span> <b>${esc(s.titulo)}</b> <span class="tc">${w && s.word_i ? fmt(w.start) + " «" + esc(w.word) + "»" : "todo el cap"}</span>
    ${st ? `<span class="badge ${st === "si" ? "ok" : st === "no" ? "fut" : "part"}">${esc(badge)}</span>` : '<span class="badge sugd">sugerido</span>'}</div>
    <div class="hint">${esc(s.por_que)} <span class="tech">${esc(el ? el.nombre : s.elemento)} · ${esc(s.accion.tipo)}</span></div>
    <button class="btn sm" data-try-s="${s.id}">Probar sugerencia</button>
    <button class="mk si sm ${st === "si" ? "on" : ""}" data-dec-s="${s.id}" data-v="si">✔ Acepto</button>
    <button class="mk no sm ${st === "no" ? "on" : ""}" data-dec-s="${s.id}" data-v="no">✖ No</button></div>`;
}
function bindSugRows(root) {
  root.querySelectorAll("[data-try-s]").forEach((b) => b.addEventListener("click", () => trySuggestion(S.sugs.find((x) => x.id === b.dataset.tryS))));
  root.querySelectorAll("[data-dec-s]").forEach((b) => b.addEventListener("click", () => decideSuggestion(S.sugs.find((x) => x.id === b.dataset.decS), b.dataset.v)));
}
function faltanBox() {
  return `<div class="card qbox"><div class="card-head"><b>Lo que falta</b> <span class="tech">para el analista</span></div>
    <p class="hint">Cosas que quisieras y el catálogo no tiene. Va tal cual al resumen.</p>
    <textarea id="faltan" rows="3" maxlength="1200" placeholder="Quisiera que…">${esc(S.faltan)}</textarea></div>`;
}
function bindFaltan(root) {
  const ta = $("#faltan", root);
  if (ta) ta.addEventListener("change", () => { if (ta.value !== S.faltan) mutate("lo que falta", () => { S.faltan = ta.value; }); });
}
function questionBox() {
  const q = S.plan.chapter_question;
  return `<div class="card qbox"><div class="card-head"><b>Tu pregunta de cierre</b> <span class="tech">chapter_question · manual</span></div>
    <p class="hint">La única pieza con texto libre: la escribís vos y queda marcada como manual (fuera del candado literal).</p>
    <textarea id="qtext" rows="2" maxlength="140" placeholder="¿…?">${esc(q && q.manual ? q.text : "")}</textarea>
    <button class="btn sm" id="qapply">Poner al final del capítulo</button> <button class="btn sm ghost" id="qclear">Quitar</button></div>`;
}
function bindQuestionBox(root) {
  const ap = $("#qapply", root), cl = $("#qclear", root);
  if (ap) ap.addEventListener("click", () => mutate("pregunta de cierre", () => setQuestion($("#qtext").value)));
  if (cl) cl.addEventListener("click", () => mutate("pregunta quitada", () => { S.plan.chapter_question = null; }));
}

// ═══════════════════════════════════════════════════════════════
//  Escena (player + narración)
// ═══════════════════════════════════════════════════════════════
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
function syncPlayButton() { if (UI.ownsPlayButton) return; const b = $("#btn-play"); if (b) b.textContent = player().paused ? "▶ Play" : "❚❚ Pausa"; }

function tick(force = false) { UI.tick(player().currentTime || 0, force); }
let lastWord = -2, lastPhoto = -2;
function expertTick(t, force = false) {
  const p = player();
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
  $("#now-line").innerHTML = active.map((c) => `<span class="chip">${esc(nombre(c.block))}</span>`).join("") || "&nbsp;";
}
function loop() { tick(); syncAudio(); syncPlayButton(); requestAnimationFrame(loop); }

// ── Preview: plan + tokens → candado → plantillas reales → nuevo src (se conserva el instante)
async function preview() {
  if (S.busy) { S.queued = true; return; }
  S.busy = true;
  setStatus("generando preview…", "busy");
  const p = player();
  const t = p.currentTime || 0;
  const wasPlaying = !p.paused;
  try {
    const r = await api("/preview", { plan: S.plan, tokens: S.tokens });
    S.cues = r.cues;
    S.rejected = r.rejected || [];
    UI.afterCues();
    await loadSrc(r.src, t, wasPlaying);
    autosave();
    if (UI.afterPreview) UI.afterPreview();
    setStatus(S.rejected.length
      ? `preview listo · candado quitó ${S.rejected.length}: ${S.rejected.map((x) => `${x.block} «${x.text}»`).join(", ")}`
      : `preview listo (${r.ms} ms)`, S.rejected.length ? "err" : "");
  } catch (e) {
    setStatus("error: " + e.message, "err");
  } finally {
    S.busy = false;
    if (S.queued) { S.queued = false; preview(); }
  }
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

// ── §C: resumen en vivo y Guardar identidad
let sumTimer = null;
function refreshSummary() {
  if (!$("#summary") || $("#summary").hidden) return;
  clearTimeout(sumTimer);
  sumTimer = setTimeout(async () => {
    try { $("#summary-md").textContent = (await api("/summary", labState())).md; }
    catch (e) { $("#summary-md").textContent = "error: " + e.message; }
  }, 300);
}
function toggleSummary(open) {
  $("#summary").hidden = open === undefined ? !$("#summary").hidden : !open;
  refreshSummary();
}
async function saveIdentity() {
  const si = Object.values(S.marks).filter((m) => m.v === "si").length, no = Object.values(S.marks).filter((m) => m.v === "no").length;
  const ok = confirm(`Guardar identidad:\n\n• perfil del canal (gfx_profiles/misterio.json): ${Object.keys(S.tokens).length} token(s), ` +
    `${si} ✔ y ${no} ✖, ${Object.keys(S.lexicon).length} palabra(s) del léxico\n• plan dorado de ${S.story.cap}\n• IDENTIDAD_misterio.md\n\n` +
    `El perfil anterior queda respaldado. ¿Guardar?`);
  if (!ok) return;
  setStatus("guardando identidad…", "busy");
  try {
    const r = await api("/save_identity", labState());
    setStatus("identidad guardada ✔ — " + Object.entries(r.archivos).map(([k, v]) => `${k}: ${v.split(/[\\/]/).pop()}`).join(" · "));
    toggleSummary(true);
  } catch (e) { setStatus("no se guardó: " + e.message, "err"); }
}

async function backToDirector() {
  mutate("volver al plan del director", () => {        // las casillas ✔/✖ y lo anotado se conservan
    S.plan = clone(S.directorPlan);
    S.tokens = {};
    S.sugState = {};
    S.sugUndo = {};
  });
}

async function init() {
  try {
    const [story, st, dir, ctx, prof, cat, sug] = await Promise.all([
      api("/api/story"), api("/api/plan"), api("/api/plan?origin=director"), api("/api/context"), api("/api/profile"),
      api("/lab/catalogo.json"), api("/lab/sugerencias_ch02.json")]);
    S.story = story; S.ctx = ctx; S.rules = prof.rules; S.catalog = cat;
    S.sugs = sug.sugerencias; S.sugMeta = sug;
    S.plan = st.plan; S.tokens = st.tokens || {}; S.anotado = st.anotado || {}; S.sugState = st.sugerencias || {};
    S.marks = st.marks || {}; S.lexicon = st.lexicon || {}; S.faltan = st.faltan || ""; S.touched = st.touched || [];
    S.sugUndo = st.sug_undo || {};
    S.obj = st.objetos || {}; S.fotoActual = st.foto_actual || 0; S.visitadas = st.visitadas || [];
    S.directorPlan = dir.plan;
    S.profileName = prof.name;
    $("#cap-label").textContent = `· ${story.cap} · ${story.video_id.slice(0, 8)}… · ${fmt(story.duration)} · perfil ${prof.name}`;
    await UI.init();
    const p = player();
    ["play", "pause", "ended"].forEach((ev) => p.addEventListener(ev, syncPlayButton));
    if ($("#btn-play")) $("#btn-play").addEventListener("click", UI.onPlayButton || togglePlay);
    $("#btn-undo").addEventListener("click", undo);
    $("#btn-redo").addEventListener("click", redo);
    $("#btn-save").addEventListener("click", saveIdentity);
    $("#btn-summary").addEventListener("click", () => toggleSummary());
    $("#summary-close").addEventListener("click", () => toggleSummary(false));
    $("#summary-copy").addEventListener("click", () => navigator.clipboard.writeText($("#summary-md").textContent).then(() => setStatus("resumen copiado")));
    syncUndoButtons();
    document.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
      if (e.code === "Space") { e.preventDefault(); (UI.onPlayButton || togglePlay)(); }
      if (UI.onKey && UI.onKey(e)) return;
      const mod = e.ctrlKey || e.metaKey;
      if (mod && e.key.toLowerCase() === "z" && !e.shiftKey) { e.preventDefault(); undo(); }
      else if (mod && (e.key.toLowerCase() === "y" || (e.key.toLowerCase() === "z" && e.shiftKey))) { e.preventDefault(); redo(); }
    });
    await preview();
    requestAnimationFrame(loop);
  } catch (e) {
    setStatus("error al cargar: " + e.message, "err");
  }
}

// ── vista experta (§A–§C): tres columnas, catálogo en pestañas, panel Aquí
const EXPERT_UI = {
  async init() {
    renderStory();
    renderCatalog();
    renderHere();
    $("#btn-preview").addEventListener("click", preview);
    $("#btn-director").addEventListener("click", backToDirector);
    const sc = $("#scrub");
    sc.addEventListener("input", () => { S.scrubbing = true; seek((sc.value / 1000) * S.story.duration); });
    sc.addEventListener("change", () => { S.scrubbing = false; });
  },
  afterChange() { renderCatalog(); if (S.here) renderHere(); },
  afterCues() { markStory(); if (S.here) renderHere(); },
  tick: expertTick,
};
let UI = EXPERT_UI;
window.addEventListener("DOMContentLoaded", () => { if (window.LAB_UI) UI = window.LAB_UI; init(); });
