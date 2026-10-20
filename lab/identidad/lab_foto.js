/* lab_foto.js — el lab tramo por tramo (HANDOFF_F3b + correcciones de Omar §F2). Solo presentación.
 * Usa el núcleo de lab.js (S, mutate/deshacer, player + narración, sugerencias, guardar).
 * Unidad = TRAMO (anchor del guion). Cada tramo muestra SUS objetos como tarjetas iguales:
 *   "IA: qué — por qué" · ▶ Probar (ese objeto SOLO, sobre la foto fija) · ☐ Se queda · Otras formas · más opciones.
 * "▶ Ver este tramo con todo" y "▶ Ver capítulo completo" muestran SOLO lo marcado "Se queda".
 * Regla: ningún botón que no se vea al dar Probar (las formas que el preview no dibuja no aparecen). */
"use strict";
(function () {
  const F = { infos: [], probar: null, full: false, more: {}, addOpen: false, autoKey: null, cueTimer: null,
              loaded: null, ready: false };
  const CIRC = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳";

  // ── formas que el preview SÍ dibuja (regla 6)
  const TEXTO = { cascade: "cascada", slide: "persiana", stamp: "sello", number_pop: "golpe" };
  const TEXTO_INV = { cascada: "cascade", persiana: "slide", sello: "stamp", golpe: "number_pop" };
  const SALIDA = { dissolve: "fundido cruzado", dip: "fundido negro", flash: "flash", cut: "corte", cut_punch: "corte" };
  const opt = (v, label = v) => ({ v, label });
  const FORMAS = {
    mov: ["acercar", "alejar", "paneo", "3D", "golpe", "quieta"].map((v) => opt(v)),
    salida: ["corte", "fundido negro", "flash", "fundido cruzado"].map((v) => opt(v)),
    sello: [opt("sello"), opt("sin sello")],
    icono: [opt("tinta"), opt("prensa"), opt("sello")],
    golpe: [opt("suave"), opt("normal"), opt("fuerte")],
    texto: ["cascada", "persiana", "sello", "golpe"].map((v) => opt(v)),
    vineta: [opt(0, "sin viñeta"), opt(0.15, "viñeta 0.15"), opt(0.3, "viñeta 0.30")],
  };
  const ICON_ANIM = { tinta: "ink_bleed", prensa: "press_wipe", sello: "stamp" };
  const ICON_ANIM_INV = { ink_bleed: "tinta", press_wipe: "prensa", stamp: "sello", engrave: "tinta" };
  const PUNCH = { suave: 1.015, normal: 1.025, fuerte: 1.04 };

  // ── utilidades
  const tok = (k) => (k in S.tokens ? S.tokens[k] : S.rules[k]);
  const tramos = () => S.story.photos;                 // un tramo = una escena del cap (anchor)
  const tramo = (i) => tramos()[i];
  const last = () => tramos().length - 1;
  const ob = (key) => S.obj[key] || {};
  const tkey = (t) => (+t).toFixed(1);
  const wordAtT = (t) => S.story.words[Math.max(0, wordIndexAt(t + 0.05))];
  const sugFor = (elems, t, tol = 0.6) => S.sugs.find((s) => elems.includes(s.elemento) && s.word_i &&
    wordByI(s.word_i) && Math.abs(wordByI(s.word_i).start - t) <= tol);
  const iaLine = (que, porque) => `IA: ${que} — ${porque}`;
  const keepOf = (key) => ob(key).v === "si";
  function setObj(key, patch) { S.obj[key] = { ...(S.obj[key] || {}), ...patch }; }
  function setForma(key, grupo, v) { const o = ob(key); setObj(key, { formas: { ...(o.formas || {}), [grupo]: v } }); }
  const basePlan = () => ({ chapter_number: S.plan.chapter_number, callouts: [], punch_in: [], emphasis: [], archive_clippings: [] });
  const mismaFoto = (i) => i > 0 && F.infos[i] && F.infos[i - 1] && F.infos[i].imagen && F.infos[i].imagen === F.infos[i - 1].imagen;

  // movimiento efectivo de un tramo (forma del lab; "continuar" = el del tramo anterior)
  function movDe(i) {
    const f = ob(`mov:${i}`).formas || {};
    if (mismaFoto(i) && (f.continuar ?? "continuar") === "continuar") return movDe(i - 1);
    const def = (F.infos[i] || {}).hay_3d === false ? "quieta" : "3D";      // hoy el pipeline anima con DepthFlow
    return f.mov || def;
  }
  const salidaDe = (i) => (ob(`salida:${i}`).formas || {}).salida || salidaHoy(i);
  function salidaHoy(i) {
    const nx = tramo(i + 1);
    const tr = nx && S.cues.find((c) => c.block.startsWith("shot_transition") && near(c.t, nx.start, 0.2));
    return tr ? SALIDA[tr.block.split(":")[1]] || "corte" : "corte";
  }

  // ═══════════════════════════════════════════════════════════════
  //  Objetos de un tramo (derivados del plan + sugerencias + estado)
  // ═══════════════════════════════════════════════════════════════
  function objetos(i) {
    const p = tramo(i), out = [];
    const inTramo = (t) => (i === 0 ? t < p.end - 0.05 : t >= p.start - 0.05 && t < p.end - 0.05);
    const info = F.infos[i] || {};
    const quieta = { [i]: "quieta" };

    // ① movimiento del tramo
    const movIA = (info.movimiento_ia || {}).forma || "acercar";
    const formasMov = FORMAS.mov.filter((x) => x.v !== "3D" || info.hay_3d !== false);
    const mov = {
      key: `mov:${i}`, elem: "movimiento", nombre: "Movimiento de la foto", t: p.start, tEnd: p.end,
      ia: iaLine(movIA === "3D" ? "profundidad 3D" : movIA, (info.movimiento_ia || {}).motivo || "base del documental"),
      grupos: [{ id: "mov", opciones: formasMov, actual: movDe(i), ia: movIA }],
      onForm(g, v) {
        if (g === "continuar") setForma(this.key, "continuar", v);
        else { setForma(this.key, "mov", v); if (mismaFoto(i)) setForma(this.key, "continuar", "nuevo"); }
      },
      solo() {
        const plan = basePlan();
        if (movDe(i) === "golpe") { const w = strongestWord(i); if (w) plan.punch_in = [w.start]; }
        return { plan, movimientos: { [i]: movDe(i) }, tramos: [i] };
      },
      win: [p.start, p.end],
    };
    if (mismaFoto(i)) {                                                   // §F2.1: misma foto que el tramo anterior
      const cont = (ob(mov.key).formas || {}).continuar ?? "continuar";
      mov.nombre = "Movimiento (misma foto que el tramo anterior)";
      mov.grupos = [{ id: "continuar", label: "Misma foto", opciones: [opt("continuar", "continuar movimiento"), opt("nuevo", "nuevo movimiento")],
                      actual: cont, ia: "continuar" },
                    ...(cont === "nuevo" ? [{ ...mov.grupos[0], label: "Nuevo" }] : [])];
    }
    out.push(mov);

    // look del capítulo (tramo 1): viñeta y grano, que se ven sobre la foto quieta
    if (i === 0) {
      out.push({
        key: "look", elem: "vignette", nombre: "Look del capítulo (todos los tramos)", t: 0, tEnd: 5,
        ia: iaLine("viñeta 0.15, sin grano", "el look aprobado"),
        grupos: [{ id: "vineta", opciones: FORMAS.vineta, actual: tok("vignette_opacity"), ia: 0.15 }],
        onForm(g, v) { S.tokens.vignette_opacity = v; },
        mas: [masToken("Grano", "grain_opacity", [[0, "0"], [0.08, "0.08"], [0.15, "0.15"]])],
        solo: () => ({ plan: basePlan(), movimientos: quieta, tramos: [i] }), win: [0, 5],
      });
    }

    // objetos del plan que caen en el tramo
    const cues = S.cues.filter((c) => !c.block.startsWith("shot_transition") && c.block !== "chapter_question" && inTramo(c.t))
      .sort((a, b) => a.t - b.t);
    for (const c of cues) out.push(...objetosDeCue(c, i));
    if (i === 0 && !S.plan.title_card) out.splice(1, 0, tituloApagado());

    // sugerencias que todavía no están en el plan (solo las que el preview dibuja)
    for (const s of S.sugs) {
      if (S.sugState[s.id] || !s.word_i || !["add_emphasis", "add_punch"].includes(s.accion.tipo)) continue;
      const w = wordByI(s.word_i);
      if (!w || !inTramo(w.start)) continue;
      if (s.accion.tipo === "add_emphasis" && emphasisAt(w.start)) continue;
      if (s.accion.tipo === "add_punch" && (S.plan.punch_in || []).some((x) => near(x, w.start))) continue;
      const el = catEl(s.elemento);
      out.push({
        key: `sug:${s.id}`, elem: s.elemento, nombre: `${el ? el.nombre : s.elemento} «${cleanWord(w.word)}»`, t: w.start, tEnd: w.start + 2.5,
        ia: iaLine(s.titulo.replace(/^'[^']*':\s*/, "").toLowerCase(), cortar(s.por_que)), sug: s, grupos: [],
        nota: "Sugerido: todavía no está en el plan. ☐ Se queda lo agrega.",
        solo: () => soloHipotetico(i, s.accion.tipo === "add_punch" ? { tipo: "punch", i: s.word_i } :
          { tipo: "emph", i: s.word_i, stamp: s.accion.stamp !== false, icon: !!s.accion.icon }),
        win: [w.start - 1, w.start + 3.5],
      });
    }

    // propuestas de la IA (también cuando lo recomendado es NO ponerlo)
    const lexFree = S.ctx.lexicon_hits.filter((h) => inTramo(h.start) && !emphasisAt(h.start) &&
      !out.some((o) => o.sug && o.sug.word_i === h.i)).sort((a, b) => b.weight - a.weight);
    if (lexFree.length) {
      const h = lexFree[0], mood = MOODS[h.category] || h.category;
      const same = (S.plan.emphasis || []).find((e) => e.category === h.category && Math.abs(e.start - h.start) < 20);
      const [que, why] = same ? ["no poner", `otro mood ${mood} a ${Math.round(Math.abs(h.start - same.start))} s`]
        : h.weight <= 1 ? ["no poner sello", "palabra común"] : ["mood + sello", "palabra con carga"];
      const pr = { tipo: "emph", i: h.i, stamp: true, icon: false };
      out.push({ key: `prop:sello:${tkey(h.start)}`, elem: "keyword_stamp", nombre: `Sello rojo «${cleanWord(h.word).toUpperCase()}»`,
        t: h.start, tEnd: h.start + 2.5, ia: iaLine(que, why), prop: pr, grupos: [],
        nota: "Propuesta de la IA: no está en el plan. ☐ Se queda lo agrega.",
        solo: () => soloHipotetico(i, pr), win: [h.start - 1, h.start + 3.5] });
    }
    if (out.length < 2) {
      const w = longestWord(i), nPunch = (S.plan.punch_in || []).length;
      if (w) {
        const pr = { tipo: "punch", i: w.i };
        out.push({ key: `prop:golpe:${tkey(w.start)}`, elem: "punch_in", nombre: `Golpe de zoom «${cleanWord(w.word)}»`,
          t: w.start, tEnd: w.start + 0.8, prop: pr,
          ia: nPunch >= 3 ? iaLine("no poner", `ya hay ${nPunch} golpes (máx 3)`) : iaLine(`golpe en «${cleanWord(w.word)}»`, "subraya sin texto"),
          grupos: [], nota: "Propuesta de la IA: no está en el plan. ☐ Se queda lo agrega.",
          solo: () => soloHipotetico(i, pr), win: [w.start - 1, w.start + 2] });
      }
    }

    // pregunta de cierre (último tramo) y salida hacia el tramo siguiente
    if (i === last()) out.push(preguntaObj());
    if (i < last()) {
      const nx = tramo(i + 1);
      const s12 = sugFor(["dip_to_black"], nx.start, 2.5);
      const [iaF, why] = s12 ? ["fundido negro", "antes de un dato duro"] : nx.rank === "R1" ? ["flash", "golpe de impacto"] : ["corte", "ritmo del documental"];
      out.push({
        key: `salida:${i}`, elem: "salida", nombre: `Salida hacia el tramo ${i + 2}`, t: nx.start - 0.5, tEnd: nx.start + 0.5,
        ia: iaLine(iaF === "corte" ? "corte seco" : iaF, why),
        grupos: [{ id: "salida", opciones: FORMAS.salida, actual: salidaDe(i), ia: iaF }],
        onForm(g, v) { setForma(this.key, "salida", v); },
        solo: () => ({ plan: basePlan(), movimientos: { [i]: "quieta", [i + 1]: "quieta" }, salidas: { [i]: salidaDe(i) }, tramos: [i, i + 1] }),
        win: [nx.start - 1.5, nx.start + 1.5],
      });
    }
    return out;
  }

  function cortar(txt) { return txt.split(/[.:;]/)[0].split(/\s+/).slice(0, 6).join(" ").toLowerCase(); }
  function strongestWord(i) {
    const p = tramo(i);
    const ws = S.story.words.filter((w) => w.start >= p.start && w.start < p.end);
    const hits = S.ctx.lexicon_hits.filter((h) => h.start >= p.start && h.start < p.end).sort((a, b) => b.weight - a.weight);
    return hits.length ? wordByI(hits[0].i) : ws[Math.floor(ws.length / 2)];
  }
  function longestWord(i) {
    const p = tramo(i);
    const ws = S.story.words.filter((w) => w.start >= p.start && w.start < p.end && cleanWord(w.word).length > 4);
    return ws.sort((a, b) => cleanWord(b.word).length - cleanWord(a.word).length)[0];
  }
  // pieza que agregaría una propuesta/sugerencia (sin tocar el plan: para Probar)
  function piezaHipotetica(pr) {
    const w = wordByI(pr.i), hit = lexAt(pr.i), ph = photoAt(w.start);
    if (pr.tipo === "punch") return { punch_in: [w.start] };
    return { emphasis: [{ word: cleanWord(w.word), category: hit.category, layer: hit.layer, icon: pr.icon && hit.icon ? hit.icon : null,
      icon_anim: hit.icon_anim || "stamp", start: w.start, duration: moodDur(), side: ph.quiet_side || "right",
      stamp: pr.stamp !== false, sid: ph.idx, rarity: 0, weight: hit.weight, icon_callout: !!(pr.icon && hit.icon) }] };
  }
  function soloHipotetico(i, pr) { return { plan: { ...basePlan(), ...piezaHipotetica(pr) }, movimientos: { [i]: "quieta" }, tramos: [i] }; }
  function applyProp(pr) {
    const w = wordByI(pr.i);
    if (pr.tipo === "emph") addEmphasis(pr.i, { stamp: pr.stamp !== false, icon: !!pr.icon });
    else addPunch(w.start);
    return tkey(w.start);
  }
  function masToken(label, token, opts) {
    return { label, opciones: opts.map(([v, l]) => ({ v, label: l })), get: () => tok(token), set: (v) => { S.tokens[token] = v; } };
  }
  function masPiece(label, piece, field, opts) {
    return { label, opciones: opts.map(([v, l]) => ({ v, label: l })), get: () => piece[field], set: (v) => { piece[field] = v; } };
  }
  const soloDe = (i, frag) => () => ({ plan: { ...basePlan(), ...frag() }, movimientos: { [i]: "quieta" }, tramos: [i] });

  function tituloApagado() {
    return {
      key: "title", elem: "title_card", nombre: "Título del capítulo (apagado)", t: 0, tEnd: 3.5, win: [0, 4],
      ia: iaLine("ponerlo, con 'CAPÍTULO 2'", "ordena al espectador"),
      grupos: [{ id: "usar", opciones: [opt("sí"), opt("no")], actual: "no", ia: "sí" }],
      onForm(g, v) { S.plan.title_card = v === "sí" ? clone(S.directorPlan.title_card) : null; },
      solo: soloDe(0, () => ({ title_card: clone(S.directorPlan.title_card) })),
    };
  }

  function objetosDeCue(c, i) {
    const b = c.block.split(":")[0], pc = pieceOf(c), t = c.t, out = [];
    const piece = pc && pc.obj;
    const base = { t, tEnd: t + c.dur, win: [t - 1, t + c.dur + 1], cue: c };
    if (b === "title_card") {
      out.push({ ...base, key: "title", elem: "title_card", nombre: "Título del capítulo",
        ia: iaLine("título con 'CAPÍTULO 2', 3 s", "ordena al espectador"), sug: S.sugs.find((s) => s.id === "S01"), grupos: [],
        mas: [masToken("Duración", "title_dur", [[2, "2 s"], [2.5, "2.5 s"], [3, "3 s"]])],
        solo: soloDe(i, () => ({ title_card: piece || S.plan.title_card })),
        quitar: () => { S.plan.title_card = null; } });
    } else if (b === "data_callout" && piece) {
      const tokName = piece.kind === "figure" ? "anim_figure" : piece.kind === "year" ? "anim_year" : "anim_name_place";
      const s = sugFor(["data_callout"], t);
      out.push({ ...base, key: `dato:${tkey(t)}`, elem: "data_callout", nombre: `Dato «${piece.text}»`, sug: s,
        ia: s && s.id === "S10" ? iaLine("dato, no contador", "6,500 ya se contó") : iaLine("cascada, del lado tranquilo", "fija el dato duro"),
        grupos: [{ id: "entrada", opciones: FORMAS.texto, actual: TEXTO[tok(tokName)] || "golpe", ia: "cascada" }],
        nota: "La entrada es una sola para todos los datos del canal.",
        onForm(g, v) { S.tokens[tokName] = TEXTO_INV[v]; },
        mas: [masToken("Tamaño", "callout_anton_px", [[130, "S"], [168, "M"], [200, "L"]]),
              masPiece("Duración", piece, "duration", [[2.5, "2.5 s"], [3.5, "3.5 s"], [4.5, "4.5 s"]])],
        posicion: piece, solo: soloDe(i, () => ({ callouts: [{ ...piece, source: "" }] })),
        quitar: () => { S.plan.callouts = S.plan.callouts.filter((x) => x !== piece); } });
    } else if (b === "count_up" && piece) {
      out.push({ ...base, key: `contador:${tkey(t)}`, elem: "count_up", nombre: `Contador «${c.text}»`,
        ia: iaLine("contador para la cifra más dura", "una vez por video"), grupos: [],
        mas: [masToken("Rampa", "count_dur", [[0.8, "0.8 s"], [1.2, "1.2 s"], [1.6, "1.6 s"]]),
              masToken("Quieto al final", "count_hold_sec", [[1.5, "1.5 s"], [2.5, "2.5 s"], [3.5, "3.5 s"]])],
        solo: soloDe(i, () => ({ count_up: piece })), quitar: () => { S.plan.count_up = null; } });
    } else if (b === "source_tag") {
      const host = (S.plan.callouts || []).find((x) => near(x.start, t, 0.6) && x.source) || (S.plan.count_up && near(S.plan.count_up.start, t, 0.6) ? S.plan.count_up : null);
      out.push({ ...base, key: `fuente:${tkey(t)}`, elem: "source_tag", nombre: `Fuente «${c.text}»`,
        ia: iaLine("fuente bajo el dato", "nadie la lee, todos la sienten"), grupos: [],
        solo: soloDe(i, () => (host && host.value_text ? { count_up: host } : { callouts: host ? [host] : [] })),
        quitar: () => { if (host) host.source = ""; } });
    } else if (b === "archive_clipping" && piece) {
      out.push({ ...base, key: `recorte:${tkey(t)}`, elem: "archive_clipping", nombre: `Recorte «${piece.headline}»`,
        sug: S.sugs.find((x) => x.elemento === "archive_clipping" && x.accion.fact_idx === piece.fact_idx),
        ia: iaLine("recorte de periódico, 4 s", "hecho público, se lee rápido"), grupos: [],
        mas: [masPiece("Duración", piece, "duration", [[3, "3 s"], [4, "4 s"], [5, "5 s"], [6, "6 s"]]),
              masToken("Ancho", "archive_max_w_frac", [[0.24, "24 %"], [0.28, "28 %"], [0.3, "30 %"]])],
        posicion: piece, solo: soloDe(i, () => ({ archive_clippings: [piece] })),
        quitar: () => { S.plan.archive_clippings = S.plan.archive_clippings.filter((x) => x !== piece); } });
    } else if ((b === "keyword_emphasis" || b === "icon_callout") && piece) {
      const hit = S.ctx.lexicon_hits.find((h) => near(h.start, piece.start)) || { weight: piece.weight || 1 };
      const mood = MOODS[piece.category] || piece.category;
      out.push({ ...base, key: `mood:${tkey(t)}`, elem: "keyword_emphasis", nombre: `Mood ${mood} «${piece.word}»`,
        sug: sugFor(["keyword_emphasis", "icon_callout"], t),
        ia: iaLine(`sí, ${piece.duration} s, suave`, "un momento, no un filtro"), grupos: [],
        mas: [masPiece("Duración", piece, "duration", [[1.5, "1.5 s"], [2.5, "2.5 s"], [4, "4 s"]])],
        solo: soloDe(i, () => ({ emphasis: [{ ...piece, stamp: false, icon_callout: false, icon: null }] })),
        quitar: () => { S.plan.emphasis = S.plan.emphasis.filter((e) => e !== piece); } });
      if (piece.icon_callout) {
        out.push({ ...base, key: `icono:${tkey(t)}`, elem: "icon_callout", nombre: `Ícono ${piece.icon} «${piece.word}»`,
          ia: iaLine(`${ICON_ANIM_INV[piece.icon_anim] || "sello"}, con la palabra`, "dibuja lo que dice la voz"),
          grupos: [{ id: "entrada", opciones: FORMAS.icono, actual: ICON_ANIM_INV[piece.icon_anim] || "sello",
                     ia: mood === "oscuridad" ? "sello" : mood === "agua" ? "prensa" : "tinta" }],
          onForm(g, v) { piece.icon_anim = ICON_ANIM[v]; },
          mas: [masToken("Tamaño", "icon_px", [[130, "S"], [190, "M"], [280, "L"]]),
                masPiece("Con la palabra en sello", piece, "stamp", [[true, "sí"], [false, "no"]])],
          posicion: piece, solo: soloDe(i, () => ({ emphasis: [{ ...piece, layer: "" }] })),
          quitar: () => { piece.icon_callout = false; piece.icon = null; } });
      } else {
        const iaF = hit.weight <= 1 ? "sin sello" : "sello";
        const why = hit.weight >= 3 ? "palabra rara" : hit.weight <= 1 ? "palabra común" : "palabra con carga";
        out.push({ ...base, key: `sello:${tkey(t)}`, elem: "keyword_stamp", nombre: `Sello rojo «${String(piece.word).toUpperCase()}»`,
          ia: iaLine(iaF === "sin sello" ? "no poner sello" : "sello rojo", why),
          grupos: [{ id: "forma", opciones: FORMAS.sello, actual: piece.stamp ? "sello" : "sin sello", ia: iaF }],
          onForm(g, v) { piece.stamp = v === "sello"; },
          mas: [masToken("Tamaño", "emphasis_stamp_px", [[84, "S"], [112, "M"], [140, "L"]])],
          posicion: piece, solo: soloDe(i, () => ({ emphasis: [{ ...piece, layer: "", stamp: true }] })),
          quitar: () => { piece.stamp = false; } });
      }
    } else if (b === "punch_in" && pc && pc.t !== undefined) {
      const w = wordAtT(t), s = sugFor(["punch_in"], t);
      const fz = Object.entries(PUNCH).find(([, v]) => v === tok("punch_scale"));
      out.push({ ...base, win: [t - 1, t + 2], key: `golpe:${tkey(t)}`, elem: "punch_in", nombre: `Golpe de zoom «${cleanWord(w.word)}»`, sug: s,
        ia: iaLine(`golpe en «${cleanWord(w.word)}»`, s ? "gira el capítulo" : "subraya sin texto"),
        grupos: [{ id: "fuerza", opciones: FORMAS.golpe, actual: fz ? fz[0] : "normal", ia: "normal" }],
        nota: "La fuerza del golpe es una sola para todo el canal.",
        onForm(g, v) { S.tokens.punch_scale = PUNCH[v]; },
        solo: soloDe(i, () => ({ punch_in: [pc.t] })),
        quitar: () => { S.plan.punch_in = S.plan.punch_in.filter((x) => x !== pc.t); } });
    } else if (b === "evidence_zoom" && S.plan.evidence_zoom) {
      out.push({ ...base, key: `zoom:${tkey(t)}`, elem: "punch_in", nombre: "Zoom de detalle", ia: iaLine("acercar al detalle", "muestra la prueba"), grupos: [],
        solo: () => ({ plan: { ...basePlan(), evidence_zoom: S.plan.evidence_zoom }, movimientos: {}, tramos: [i] }),
        quitar: () => { S.plan.evidence_zoom = null; } });
    } else if (b === "icon_array" && S.plan.icon_array) {
      out.push({ ...base, key: `matriz:${tkey(t)}`, elem: "icon_array", nombre: `Matriz «${c.text}»`, ia: iaLine("figuras en filas de 10", "hace contable la proporción"), grupos: [],
        solo: soloDe(i, () => ({ icon_array: S.plan.icon_array })), quitar: () => { S.plan.icon_array = null; } });
    }
    return out;
  }

  function preguntaObj() {
    const q = S.plan.chapter_question, k = "pregunta", d = S.story.duration;
    return {
      key: k, elem: "chapter_question", nombre: "Pregunta de cierre", t: Math.max(0, d - 3.5), tEnd: d,
      ia: iaLine("escribí una pregunta", "gancho para el capítulo 3"), pregunta: true, texto: q && q.manual ? q.text : "",
      grupos: [],
      mas: [masToken("Fondo oscurecido", "question_dim", [[0.5, "50 %"], [0.7, "70 %"]]),
            ...(q ? [masPiece("Duración", q, "duration", [[2.5, "2.5 s"], [3, "3 s"], [3.5, "3.5 s"]])] : [])],
      solo: soloDe(last(), () => ({ chapter_question: S.plan.chapter_question })),
      quitar: () => { S.plan.chapter_question = null; },
      win: [Math.max(0, d - 4.5), d],
    };
  }

  // ═══════════════════════════════════════════════════════════════
  //  Previews: SOLO (Probar) y CON TODO (tramo / capítulo, solo lo aprobado)
  // ═══════════════════════════════════════════════════════════════
  async function loadComposition(body, label) {
    setStatus(`${label}…`, "busy");
    const r = await api("/preview", { tokens: S.tokens, ...body });
    if (r.rejected && r.rejected.length) setStatus(`candado quitó ${r.rejected.map((x) => `«${x.text}»`).join(", ")}`, "err");
    await loadSrc(r.src, 0, false);
    F.loaded = body.solo ? "solo" : "todo";
    return r;
  }
  function playWindow(from, to, full = false) {
    const d = S.story.duration;
    F.full = full;
    F.probar = full ? null : { from: Math.max(0, from), to: Math.min(d - 0.05, to) };
    seek(Math.max(0, from));
    player().play();
    syncAudio(true);
    syncPlay();
  }
  async function probar(o) {
    try {
      if (o.pregunta) {
        const txt = ($(`[data-q="${o.key}"]`) || {}).value || o.texto;
        if (!txt || !txt.trim()) { setStatus("escribí la pregunta en la tarjeta y tocá ▶ Probar", "err"); $(`[data-q="${o.key}"]`)?.focus(); return; }
        if (!S.plan.chapter_question || S.plan.chapter_question.text !== txt.trim()) {
          F.autoKey = o.key;
          mutate("pregunta de cierre", () => { setQuestion(txt); setObj(o.key, { probado: true }); });
          return;
        }
      }
      const g = (o.grupos || [])[0];
      if (g && g.ia !== undefined && !ob(o.key).probado && !same(g.actual, g.ia) && o.onForm) {   // 1er Probar = forma de la IA
        F.autoKey = o.key;
        mutate(`${o.nombre}: forma de la IA → ${g.ia}`, () => { o.onForm(g.id, g.ia); setObj(o.key, { probado: true }); touch(o.elem); });
        return;
      }
      if (!ob(o.key).probado) mutate(`probando ${o.nombre}`, () => { setObj(o.key, { probado: true }); touch(o.elem); }, { preview: false });
      const sp = o.solo();
      await loadComposition({ plan: sp.plan, movimientos: sp.movimientos, salidas: sp.salidas || {}, solo: sp.tramos }, `probando ${o.nombre} (solo)`);
      setStatus(`▶ ${o.nombre} — solo, sobre la foto${movFijo(sp) ? " quieta" : ""}`);
      playWindow(...o.win);
    } catch (e) { setStatus("error: " + e.message, "err"); }
  }
  const movFijo = (sp) => Object.values(sp.movimientos || {}).every((v) => v === "quieta");
  function chooseForma(o, gid, v) {
    F.autoKey = o.key;
    mutate(`${o.nombre}: ${v}`, () => { o.onForm(gid, v); setObj(o.key, { probado: true }); touch(o.elem); });
  }

  // plan con SOLO lo marcado "Se queda" (lo no marcado no aparece)
  function approvedSpec() {
    const p = clone(S.plan), keep = keepOf;
    const pl = { ...basePlan(), chapter_number: p.chapter_number };
    if (p.title_card && keep("title")) pl.title_card = p.title_card;
    pl.callouts = (p.callouts || []).filter((c) => keep(`dato:${tkey(c.start)}`)).map((c) => ({ ...c, source: keep(`fuente:${tkey(c.start)}`) ? c.source : "" }));
    if (p.count_up && keep(`contador:${tkey(p.count_up.start)}`)) pl.count_up = { ...p.count_up, source: keep(`fuente:${tkey(p.count_up.start)}`) ? p.count_up.source : "" };
    pl.archive_clippings = (p.archive_clippings || []).filter((a) => keep(`recorte:${tkey(a.start)}`));
    pl.emphasis = [];
    for (const e of p.emphasis || []) {
      const k = tkey(e.start), m = keep(`mood:${k}`), s = keep(`sello:${k}`), ic = keep(`icono:${k}`);
      if (!m && !s && !ic) continue;
      pl.emphasis.push({ ...e, layer: m ? e.layer : "", stamp: e.icon_callout ? (ic && e.stamp) : (s && e.stamp),
                         icon_callout: !!(e.icon_callout && ic), icon: e.icon_callout && ic ? e.icon : null });
    }
    pl.punch_in = (p.punch_in || []).filter((t) => keep(`golpe:${tkey(t)}`));
    if (p.evidence_zoom && keep(`zoom:${tkey(p.evidence_zoom.start ?? 0)}`)) pl.evidence_zoom = p.evidence_zoom;
    if (p.icon_array && keep(`matriz:${tkey(p.icon_array.start)}`)) pl.icon_array = p.icon_array;
    if (p.chapter_question && keep("pregunta")) pl.chapter_question = p.chapter_question;
    const movimientos = {}, salidas = {};
    tramos().forEach((_, i) => {
      const mv = keep(`mov:${i}`) ? movDe(i) : "quieta";
      movimientos[i] = mv;
      if (mv === "golpe") { const w = strongestWord(i); if (w) pl.punch_in.push(w.start); }
      if (i < last()) salidas[i] = keep(`salida:${i}`) ? salidaDe(i) : "corte";
    });
    pl.punch_in.sort((a, b) => a - b);
    return { plan: pl, movimientos, salidas };
  }
  async function verTramo(fromT) {
    const p = tramo(S.fotoActual);
    try {
      await loadComposition(approvedSpec(), "armando el tramo con lo que se queda");
      const n = objetos(S.fotoActual).filter((o) => keepOf(o.key)).length;
      setStatus(`▶ tramo ${S.fotoActual + 1} con todo lo que se queda (${n} objeto${n === 1 ? "" : "s"})`);
      playWindow(fromT ?? p.start, p.end);
    } catch (e) { setStatus("error: " + e.message, "err"); }
  }
  async function verCapitulo() {
    try {
      await loadComposition(approvedSpec(), "armando el capítulo con lo que se queda");
      setStatus("▶ capítulo completo con todo lo que se queda");
      playWindow(0, S.story.duration, true);
    } catch (e) { setStatus("error: " + e.message, "err"); }
  }

  // ═══════════════════════════════════════════════════════════════
  //  Se queda / Nunca / Agregar
  // ═══════════════════════════════════════════════════════════════
  function toggleKeep(o, on) {
    const changesPlan = on && (o.prop || (o.sug && o.key.startsWith("sug:")));
    mutate(`${o.nombre}: ${on ? "☑ se queda" : "☐ pendiente"}`, () => {
      if (on && o.key.startsWith("sug:")) {                          // aprobar una sugerencia = agregarla
        if (!S.sugUndo[o.sug.id]) S.sugUndo[o.sug.id] = sugUndoInfo(o.sug);
        applyPreset(catEl(o.sug.elemento) || { id: o.sug.elemento }, o.sug.preset || {});
        runAction(o.sug.accion, o.sug.word_i, catEl(o.sug.elemento));
        S.sugState[o.sug.id] = "si";
        approveNew(tkey(wordByI(o.sug.word_i).start), o.sug.accion.tipo === "add_punch" ? ["golpe"] : ["mood", "sello", "icono"]);
      } else if (on && o.prop) {                                      // aprobar una propuesta = agregarla
        approveNew(applyProp(o.prop), o.prop.tipo === "emph" ? ["mood", "sello"] : ["golpe"]);
      }
      if (o.sug && !o.key.startsWith("sug:")) S.sugState[o.sug.id] = on ? "si" : "probando";
      setObj(o.key, { nombre: o.nombre });
      if (on) S.obj[o.key].v = "si"; else delete S.obj[o.key].v;
      const el = catEl(o.elem);
      if (el) {
        if (on && !S.marks[el.id]) S.marks[el.id] = { v: "si", auto: true };
        if (!on && S.marks[el.id]?.auto && !Object.entries(S.obj).some(([k, x]) => x.v === "si" && k !== o.key && objElem(k) === el.id)) delete S.marks[el.id];
      }
      touch(o.elem);
    }, { preview: changesPlan ? undefined : false });
  }
  function approveNew(t, kinds) { kinds.forEach((k) => setObj(`${k}:${t}`, { v: "si" })); }
  function objElem(key) {
    const t = key.split(":")[0];
    return { mov: "movimiento", look: "vignette", title: "title_card", dato: "data_callout", contador: "count_up", fuente: "source_tag",
             recorte: "archive_clipping", mood: "keyword_emphasis", icono: "icon_callout", sello: "keyword_stamp", golpe: "punch_in",
             salida: "salida", pregunta: "chapter_question" }[t] || t;
  }
  function nunca(o, tipo) {
    mutate(tipo ? `${o.nombre}: ✖ nunca este tipo` : `${o.nombre}: ✖ nunca`, () => {
      if (tipo) { const el = catEl(o.elem); if (el) S.marks[el.id] = { v: "no" }; return; }
      if (o.sug) S.sugState[o.sug.id] = "no";
      if (o.quitar) o.quitar();
      setObj(o.key, { v: "no", nombre: o.nombre, t: o.t, foto: S.fotoActual });
      touch(o.elem);
    });
  }

  const AGREGAR = [["dato", "Dato"], ["sello", "Sello"], ["icono", "Ícono"], ["recorte", "Recorte"], ["contador", "Contador"],
                   ["mood", "Mood"], ["pregunta", "Pregunta de cierre"]];
  function agregar(tipo) {
    const i = S.fotoActual, p = tramo(i);
    const ws = S.story.words.filter((w) => w.start >= p.start && w.start < p.end);
    const hits = S.ctx.lexicon_hits.filter((h) => h.start >= p.start && h.start < p.end && !emphasisAt(h.start)).sort((a, b) => b.weight - a.weight);
    F.addOpen = false;
    try {
      if (tipo === "sello" || tipo === "mood" || tipo === "icono") {
        const h = tipo === "icono" ? hits.find((x) => x.icon) : hits[0];
        if (!h) throw new Error(tipo === "icono" ? "en este tramo no hay una palabra que un ícono dibuje literalmente" : "en este tramo no hay palabras del léxico libres");
        F.autoKey = `${tipo === "icono" ? "icono" : tipo === "mood" ? "mood" : "sello"}:${tkey(h.start)}`;
        mutate(`agregado ${tipo} en «${h.word}»`, () => addEmphasis(h.i, { stamp: tipo !== "mood", icon: tipo === "icono" }));
      } else if (tipo === "recorte") {
        const words = new Set(ws.map((w) => cleanWord(w.word).toLowerCase()).filter((w) => w.length > 3));
        const used = new Set((S.plan.archive_clippings || []).map((a) => a.fact_idx));
        const f = S.ctx.facts.filter((x) => x.eligible && !used.has(x.idx))
          .map((x) => ({ x, n: x.text.toLowerCase().split(/\W+/).filter((w) => words.has(w)).length })).sort((a, b) => b.n - a.n)[0];
        if (!f) throw new Error("no quedan datos elegibles para un recorte");
        F.autoKey = `recorte:${tkey(p.start + 0.3)}`;
        mutate(`agregado recorte del dato ${f.x.idx}`, () => addArchive(f.x.idx, p.start + 0.3));
      } else if (tipo === "dato" || tipo === "contador") {
        const found = cifraEnTramo(ws);
        if (!found) throw new Error("la voz no dice ninguna cifra de los datos en este tramo");
        F.autoKey = `${tipo === "dato" ? "dato" : "contador"}:${tkey(found.w.start)}`;
        mutate(`agregado ${tipo} «${found.text}»`, () => {
          if (tipo === "dato") {
            planList("callouts").push({ text: found.text, start: found.w.start, kind: "figure", duration: 2.5,
              side: p.quiet_side === "left" ? "left" : "right", fact_idx: found.f.idx, source: found.f.source || "", manual: true });
            S.plan.callouts.sort((a, b) => a.start - b.start);
          } else {
            S.plan.count_up = { value_text: found.num, unit: found.unit, start: found.w.start, fact_idx: found.f.idx, source: found.f.source || "", manual: true };
          }
        });
      } else if (tipo === "pregunta") {
        if (i !== last()) { goTramo(last()); setStatus("la pregunta de cierre va en el último tramo: escribila en su tarjeta"); }
        else $('[data-q="pregunta"]')?.focus();
      }
    } catch (e) { setStatus(e.message, "err"); renderObjs(); }
  }
  function cifraEnTramo(ws) {
    for (const w of ws) {
      const num = cleanWord(w.word);
      if (!/\d/.test(num)) continue;
      for (const f of S.ctx.facts.filter((x) => x.eligible)) {
        const m = f.text.match(new RegExp(`(^|[^\\d])(${num.replace(/[.]/g, "\\.")})\\s+([a-záéíóúñ]+)`, "i"));
        if (m) return { w, f, num: m[2], unit: m[3], text: `${m[2]} ${m[3]}` };
      }
    }
    return null;
  }

  // ═══════════════════════════════════════════════════════════════
  //  Pantalla
  // ═══════════════════════════════════════════════════════════════
  function goTramo(i) {
    i = Math.max(0, Math.min(last(), i));
    S.fotoActual = i;
    if (!S.visitadas.includes(i)) S.visitadas.push(i);
    F.more = {};
    F.addOpen = false;
    F.probar = null;
    F.full = false;
    player().pause();
    seek(tramo(i).start + 0.02);
    render();
    autosave();
  }
  function estadoTramo(i) {
    const objs = objetos(i);
    const dec = objs.filter((o) => ob(o.key).v === "si" || ob(o.key).v === "no").length;
    return { total: objs.length, dec, done: dec === objs.length && objs.length > 0 };
  }
  function render() {
    const i = S.fotoActual, p = tramo(i);
    $("#f-num").textContent = `TRAMO ${i + 1} de ${tramos().length}`;
    $("#f-range").textContent = `${fmt(p.start)}–${fmt(p.end)}${mismaFoto(i) ? " · misma foto que el tramo anterior" : ""}`;
    $("#f-prev").disabled = i === 0;
    $("#f-next").disabled = i === last();
    renderWords();
    renderDots();
    renderObjs();
  }
  function renderWords() {
    const p = tramo(S.fotoActual);
    const ws = S.story.words.filter((w) => w.start >= p.start - 0.05 && w.start < p.end - 0.05);
    const cueWords = new Set(S.cues.filter((c) => !c.block.startsWith("shot_transition")).map((c) => wordAtT(c.t).i));
    $("#f-words").innerHTML = ws.map((w) => {
      const h = lexAt(w.i);
      const cls = ["w", h ? "lex lex-w" + h.weight : "", cueWords.has(w.i) ? "cue" : ""].join(" ");
      return `<span class="${cls}" data-i="${w.i}" title="${fmt(w.start)}${h ? " · " + (MOODS[h.category] || h.category) + " · peso " + h.weight : ""}">${esc(w.word)}</span>`;
    }).join(" ");
    $("#f-words").querySelectorAll(".w").forEach((el) => el.addEventListener("click", () => verTramo(wordByI(+el.dataset.i).start - 0.3)));
  }
  function renderDots() {
    $("#f-dots").innerHTML = tramos().map((p, i) => {
      const st = estadoTramo(i);
      const cls = i === S.fotoActual ? "cur" : st.done ? "done" : S.visitadas.includes(i) ? "seen" : "";
      return `<button class="dot ${cls}" data-f="${i}" title="Tramo ${i + 1} · ${st.dec}/${st.total} decididos${st.done ? " · listo" : ""}">${i + 1}</button>`;
    }).join("") + `<span class="dots-count">Tramo ${S.fotoActual + 1} de ${tramos().length}</span>`;
    $("#f-dots").querySelectorAll(".dot").forEach((b) => b.addEventListener("click", () => goTramo(+b.dataset.f)));
  }
  function formaButtons(g) {
    return g.opciones.map((x) => {
      const on = same(x.v, g.actual), isIA = g.ia !== undefined && same(x.v, g.ia);
      return `<button class="forma ${on ? "on" : ""}" data-g="${g.id}" data-v='${esc(JSON.stringify(x.v))}'>${esc(x.label)}${isIA ? '<span class="iatag">IA</span>' : ""}</button>`;
    }).join("");
  }
  function masBox(o) {
    let h = "";
    (o.mas || []).forEach((m, k) => {
      const cur = m.get();
      h += `<div class="mas-row"><span class="ml-l">${esc(m.label)}</span>` +
        m.opciones.map((x) => `<button class="mini ${same(x.v, cur) ? "on" : ""}" data-m="${k}" data-v='${esc(JSON.stringify(x.v))}'>${esc(x.label)}</button>`).join("") + "</div>";
    });
    if (o.posicion) {
      const side = o.posicion.side === "left" ? "left" : "right";
      h += `<div class="mas-row"><span class="ml-l">Posición</span>` +
        [["left", "izquierda"], ["right", "derecha"]].map(([v, l]) => `<button class="mini ${side === v ? "on" : ""}" data-side="${v}">${l}</button>`).join("") + "</div>";
    }
    if (!o.key.startsWith("sug:") && !o.key.startsWith("prop:")) {
      h += `<div class="mas-row nunca"><button class="mini no" data-nunca="1">✖ Nunca (sacar esto)</button>` +
        (catEl(o.elem) ? ` <button class="mini no" data-nunca-tipo="1">✖ No quiero ${esc(catEl(o.elem).nombre.toLowerCase())} en el canal</button>` : "") + "</div>";
    }
    return h;
  }
  function card(o, n) {
    const st = ob(o.key).v;
    if (st === "no") {
      return `<div class="ocard st-no" data-k="${esc(o.key)}"><div class="oc-head"><span class="num">${CIRC[n] || n + 1}</span>
        <b>${esc(o.nombre)}</b> <span class="when">${fmt(o.t)}</span> <span class="badge fut">✖ nunca</span>
        <button class="mini" data-undo-no="1">volver a ponerlo</button></div></div>`;
    }
    const cls = st === "si" ? "st-si" : o.key.startsWith("sug:") || o.key.startsWith("prop:") ? "st-sug" : "";
    const groups = (o.grupos || []).map((g) => `<div class="formas"><span class="fl">${esc(g.label || "Otras formas")}:</span>${formaButtons(g)}</div>`).join("");
    const q = o.pregunta ? `<textarea class="qtxt" data-q="${esc(o.key)}" rows="2" maxlength="140" placeholder="¿…? (la escribís vos)">${esc(o.texto || "")}</textarea>` : "";
    const hasMore = (o.mas && o.mas.length) || o.posicion || !(o.key.startsWith("sug:") || o.key.startsWith("prop:"));
    return `<div class="ocard ${cls}" data-k="${esc(o.key)}">
      <div class="oc-head"><span class="num">${CIRC[n] || n + 1}</span> <b>${esc(o.nombre)}</b> <span class="when">${fmt(o.t)}</span>
        ${o.key.startsWith("sug:") || o.key.startsWith("prop:") ? '<span class="badge sugd">propuesto</span>' : ""}</div>
      <div class="ia">${esc(o.ia)}</div>
      ${q}
      <div class="oc-actions"><button class="btn probar" data-probar="1">▶ Probar</button>
        <label class="keep"><input type="checkbox" data-keep="1" ${st === "si" ? "checked" : ""}> Se queda</label></div>
      ${groups}
      ${o.nota ? `<div class="onota">${esc(o.nota)}</div>` : ""}
      ${hasMore ? `<a href="#" class="more" data-more="1">${F.more[o.key] ? "menos opciones" : "más opciones"}</a>
      <div class="more-box" ${F.more[o.key] ? "" : "hidden"}>${F.more[o.key] ? masBox(o) : ""}</div>` : ""}
    </div>`;
  }
  function renderObjs() {
    const objs = objetos(S.fotoActual);
    F.current = objs;
    $("#f-objs").innerHTML = objs.map(card).join("");
    $("#f-objs").querySelectorAll(".ocard").forEach((el) => {
      const o = objs.find((x) => x.key === el.dataset.k);
      if (!o) return;
      el.querySelector("[data-probar]")?.addEventListener("click", () => probar(o));
      el.querySelector("[data-keep]")?.addEventListener("change", (e) => toggleKeep(o, e.target.checked));
      el.querySelectorAll(".forma").forEach((b) => b.addEventListener("click", () => chooseForma(o, b.dataset.g, JSON.parse(b.dataset.v))));
      el.querySelector("[data-more]")?.addEventListener("click", (e) => { e.preventDefault(); F.more[o.key] = !F.more[o.key]; renderObjs(); });
      el.querySelectorAll("[data-m]").forEach((b) => b.addEventListener("click", () => {
        const m = o.mas[+b.dataset.m], v = JSON.parse(b.dataset.v);
        F.autoKey = o.key;
        mutate(`${o.nombre}: ${m.label} → ${b.textContent}`, () => { m.set(v); touch(o.elem); });
      }));
      el.querySelectorAll("[data-side]").forEach((b) => b.addEventListener("click", () => {
        F.autoKey = o.key;
        mutate(`${o.nombre}: ${b.textContent}`, () => { o.posicion.side = b.dataset.side; });
      }));
      el.querySelector("[data-nunca]")?.addEventListener("click", () => nunca(o, false));
      el.querySelector("[data-nunca-tipo]")?.addEventListener("click", () => nunca(o, true));
      el.querySelector("[data-undo-no]")?.addEventListener("click", () => mutate(`${o.nombre}: vuelve`, () => { delete S.obj[o.key].v; }, { preview: false }));
      el.querySelector("[data-q]")?.addEventListener("change", (e) => {
        if ((S.plan.chapter_question || {}).text === e.target.value.trim()) return;
        F.autoKey = o.key;
        mutate("pregunta de cierre", () => setQuestion(e.target.value));
      });
    });
    const gone = Object.entries(S.obj).filter(([k, x]) => x.v === "no" && x.foto === S.fotoActual && !objs.some((o) => o.key === k));
    if (gone.length) {
      $("#f-objs").insertAdjacentHTML("beforeend", `<div class="gone">Sacaste: ${gone.map(([, x]) => esc(x.nombre)).join(" · ")} <span class="tech">(Ctrl+Z para volver)</span></div>`);
    }
    $("#f-add-list").hidden = !F.addOpen;
  }
  function syncPlay() {
    const playing = !player().paused;
    $("#btn-play").textContent = playing && !F.full && F.loaded === "todo" ? "❚❚ Pausa" : "▶ Ver este tramo con todo";
    $("#btn-full").textContent = F.full && playing ? "❚❚ Pausar capítulo" : "▶ Ver capítulo completo";
  }

  // recorrido para el resumen (aprobado / pendiente / rechazado por tramo)
  function recorrido() {
    if (!F.infos.length) return undefined;
    return tramos().map((p, i) => ({
      foto: i + 1, desde: fmt(p.start), hasta: fmt(p.end), vista: S.visitadas.includes(i),
      objetos: [...objetos(i).map((o) => ({
        nombre: o.nombre, t: fmt(o.t), estado: ob(o.key).v === "si" ? "si" : ob(o.key).v === "no" ? "no" : "pendiente",
        forma: (o.grupos || []).map((g) => typeof g.actual === "number" ? String(g.actual) : g.actual).filter(Boolean).join(" · "), ia: o.ia,
      })), ...Object.entries(S.obj).filter(([k, x]) => x.v === "no" && x.foto === i && !objetos(i).some((o) => o.key === k))
        .map(([, x]) => ({ nombre: x.nombre, t: fmt(x.t || p.start), estado: "no", forma: "", ia: "" }))],
    }));
  }

  // cues del plan COMPLETO (las tarjetas salen de acá; el preview "con todo" usa solo lo aprobado)
  async function refreshCues() {
    const r = await api("/cues", { plan: S.plan, tokens: S.tokens });
    S.cues = r.cues;
    S.rejected = r.rejected || [];
    if (S.rejected.length) setStatus(`candado quitó ${S.rejected.map((x) => `«${x.text}»`).join(", ")}`, "err");
  }

  // ═══════════════════════════════════════════════════════════════
  //  Ganchos para el núcleo (lab.js)
  // ═══════════════════════════════════════════════════════════════
  window.LAB_UI = {
    async init() {
      F.infos = await Promise.all(tramos().map((_, i) => api(`/objetos?foto=${i}`)));
      $("#f-prev").addEventListener("click", () => goTramo(S.fotoActual - 1));
      $("#f-next").addEventListener("click", () => goTramo(S.fotoActual + 1));
      $("#f-add").addEventListener("click", () => {
        F.addOpen = !F.addOpen;
        $("#f-add-list").innerHTML = AGREGAR.map(([k, l]) => `<button class="btn ghost" data-add="${k}">${l}</button>`).join("");
        $("#f-add-list").querySelectorAll("[data-add]").forEach((b) => b.addEventListener("click", () => agregar(b.dataset.add)));
        $("#f-add-list").hidden = !F.addOpen;
      });
      $("#btn-full").addEventListener("click", () => {
        if (F.full && !player().paused) { player().pause(); return; }
        verCapitulo();
      });
      player().addEventListener("pause", () => {
        if (F.full) {                                         // al pausar el capítulo, el lab salta a ese tramo
          F.full = false;
          const idx = photoAt(player().currentTime || 0).idx;
          if (idx !== S.fotoActual) { S.fotoActual = idx; if (!S.visitadas.includes(idx)) S.visitadas.push(idx); render(); autosave(); }
        }
        syncPlay();
      });
      player().addEventListener("ended", () => { F.full = false; syncPlay(); });
      const qf = +new URLSearchParams(location.search).get("tramo") || +new URLSearchParams(location.search).get("foto");
      if (qf >= 1 && qf <= tramos().length) S.fotoActual = qf - 1;
      if (!S.visitadas.includes(S.fotoActual)) S.visitadas.push(S.fotoActual);
    },
    async firstPreview() {
      await refreshCues();
      render();
      await loadComposition(approvedSpec(), "cargando");
      seek(tramo(S.fotoActual).start + 0.02);
      setStatus("listo");
      F.ready = true;
    },
    onPlanChanged() {                                         // cambio en el plan: cues + (si vino de una tarjeta) Probar de nuevo
      clearTimeout(F.cueTimer);
      F.cueTimer = setTimeout(async () => {
        try {
          await refreshCues();
          renderObjs(); renderDots(); renderWords();
          autosave();
          const k = F.autoKey;
          F.autoKey = null;
          if (k) {
            const o = objetos(S.fotoActual).find((x) => x.key === k);
            if (o) await probar(o); else setStatus("listo");
          } else setStatus("listo");
        } catch (e) { setStatus("error: " + e.message, "err"); }
      }, 200);
    },
    afterChange() { renderObjs(); renderDots(); renderWords(); },
    afterCues() { renderObjs(); renderDots(); renderWords(); },
    ownsPlayButton: true,
    onPlayButton() {
      if (!player().paused) { player().pause(); F.probar = null; F.full = false; syncAudio(true); syncPlay(); return; }
      verTramo();
    },
    tick(t) {
      $("#tc").textContent = `${fmt(t)}`;
      if (F.probar && t >= F.probar.to) { player().pause(); F.probar = null; syncAudio(true); }
      const objs = F.current || [];
      document.querySelectorAll("#f-words .w").forEach((el) => {
        const w = wordByI(+el.dataset.i);
        el.classList.toggle("now", w.start <= t && t < w.end + 0.15);
      });
      document.querySelectorAll(".ocard").forEach((el) => {
        const o = objs.find((x) => x.key === el.dataset.k);
        el.classList.toggle("playing", !!o && !player().paused && t >= o.t && t <= o.tEnd);
      });
      $("#now-line").textContent = F.loaded === "solo" ? "probando un objeto solo" : F.loaded === "todo" ? "con todo lo que se queda" : "";
      if (F.full) {
        const idx = photoAt(t).idx;
        document.querySelectorAll("#f-dots .dot").forEach((b) => b.classList.toggle("running", +b.dataset.f === idx));
        $("#f-num").textContent = `TRAMO ${idx + 1} de ${tramos().length}`;
      }
      syncPlay();
    },
    onKey(e) {
      if (e.key === "ArrowRight" && !e.ctrlKey) { goTramo(S.fotoActual + 1); return true; }
      if (e.key === "ArrowLeft" && !e.ctrlKey) { goTramo(S.fotoActual - 1); return true; }
      return false;
    },
    recorrido,
    _debug: { F, objetos, probar, chooseForma, toggleKeep, nunca, agregar, goTramo, playWindow, approvedSpec, verTramo, verCapitulo, movDe },
  };
})();
