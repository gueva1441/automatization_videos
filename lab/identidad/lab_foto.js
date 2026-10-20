/* lab_foto.js — §F (HANDOFF_F3b): el lab foto por foto. Solo presentación.
 * Usa el núcleo de lab.js tal cual (S, mutate/deshacer, preview, player + narración, sugerencias, guardar).
 * Cada foto muestra SUS objetos como tarjetas iguales: nombre + momento · "IA:" · ▶ Probar · ☐ Se queda ·
 * "Otras formas" (máx 6) · "más opciones" (tamaño, posición, duración, ✖ Nunca). */
"use strict";
(function () {
  const F = { infos: [], probar: null, autoProbar: null, full: false, more: {}, addOpen: false, lastFoto: -1 };
  const CIRC = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮";

  // ── formas por tipo de objeto (rule 6 del handoff). live=false → se guarda, el preview todavía no la dibuja
  const TEXTO = { cascade: "cascada", slide: "persiana", stamp: "sello", number_pop: "golpe" };
  const SALIDA = { dissolve: "fundido cruzado", dip: "fundido negro", flash: "flash", cut: "corte", cut_punch: "corte" };
  const opt = (v, live = false, label = v) => ({ v, label, live });
  const FORMAS = {
    mov: [opt("acercar"), opt("alejar"), opt("paneo"), opt("3D"), opt("golpe", true), opt("quieta")],
    salida: [opt("corte"), opt("fundido negro"), opt("flash"), opt("fundido cruzado"), opt("tinta"), opt("zoom")],
    sello: [opt("sello", true), opt("golpe"), opt("sin sello", true)],
    recorte: [opt("periódico", true), opt("post-it"), opt("ficha"), opt("carpeta")],
    icono: [opt("tinta", true), opt("prensa", true), opt("sello", true)],
    icono_hold: [opt("respira"), opt("deriva"), opt("pulso"), opt("quieto")],
    mood: [opt("suave", true), opt("media")],
    golpe: [opt("suave", true), opt("normal", true), opt("fuerte", true)],
  };
  const ICON_ANIM = { tinta: "ink_bleed", prensa: "press_wipe", sello: "stamp" };
  const ICON_ANIM_INV = { ink_bleed: "tinta", press_wipe: "prensa", stamp: "sello", engrave: "tinta" };
  const PUNCH = { suave: 1.015, normal: 1.025, fuerte: 1.04 };

  // ── utilidades
  const tok = (k) => (k in S.tokens ? S.tokens[k] : S.rules[k]);
  const photos = () => S.story.photos;
  const photo = (i) => photos()[i];
  const last = () => photos().length - 1;
  const ob = (key) => S.obj[key] || {};
  const tkey = (t) => (+t).toFixed(1);
  const wordAtT = (t) => S.story.words[Math.max(0, wordIndexAt(t + 0.05))];
  const sugFor = (elems, t, tol = 0.6) => S.sugs.find((s) => elems.includes(s.elemento) && s.word_i &&
    wordByI(s.word_i) && Math.abs(wordByI(s.word_i).start - t) <= tol);
  const iaLine = (que, porque) => `IA: ${que} — ${porque}`;
  function setObj(key, patch) { S.obj[key] = { ...(S.obj[key] || {}), ...patch }; }
  function setForma(key, grupo, v) { const o = ob(key); setObj(key, { formas: { ...(o.formas || {}), [grupo]: v } }); }

  // ═══════════════════════════════════════════════════════════════
  //  Objetos de una foto (se derivan del plan + sugerencias + estado; nunca se guardan aparte)
  // ═══════════════════════════════════════════════════════════════
  function objetos(i) {
    const p = photo(i), out = [];
    const inPhoto = (t) => (i === 0 ? t < p.end - 0.05 : t >= p.start - 0.05 && t < p.end - 0.05);
    const info = F.infos[i] || {};

    // ① movimiento de la foto (lo anima el pipeline; "golpe" sí se ve en vivo)
    const movIA = (info.movimiento_ia || {}).forma || "acercar";
    out.push({
      key: `mov:${i}`, elem: "movimiento", nombre: "Movimiento de la foto", t: p.start, tEnd: p.end,
      ia: iaLine(`${movIA === "3D" ? "profundidad 3D" : movIA}`, (info.movimiento_ia || {}).motivo || "base del documental"),
      grupos: [{ id: "mov", opciones: FORMAS.mov, actual: ob(`mov:${i}`).formas?.mov || (info.movimiento_pipeline || {}).forma || "3D", ia: movIA }],
      nota: "Hoy lo anima DepthFlow (" + ((info.movimiento_pipeline || {}).crudo || "?") + "); tu elección queda anotada para el render.",
      onForm(g, v) {
        setForma(this.key, "mov", v);
        if (v === "golpe") { const w = strongestWord(i); if (w) addPunch(w.start); }
      },
      win: [p.start, Math.min(p.end, p.start + 6)],
    });

    // look del capítulo (solo en la foto 1): acento + viñeta + grano + desaturación
    if (i === 0) {
      const s16 = S.sugs.find((s) => s.id === "S16");
      out.push({
        key: "look", elem: "paleta", nombre: "Look del capítulo (todas las fotos)", t: 0, tEnd: 4,
        ia: iaLine("rojo del handoff, viñeta 0.15", "acento menos saturado"),
        grupos: [{ id: "acento", opciones: [opt("#c8102e", true, "rojo actual"), opt("#c2302f", true, "rojo handoff"), opt("#9e1b1b", true, "rojo sangre"), opt("#d4a017", true, "ámbar")], actual: tok("accent_hex"), ia: s16 ? s16.preset.tokens.accent_hex : null, swatch: true }],
        onForm(g, v) { S.tokens.accent_hex = v; },
        mas: [masToken("Viñeta", "vignette_opacity", [[0, "0"], [0.15, "0.15"], [0.3, "0.30"]]),
              masToken("Grano", "grain_opacity", [[0, "0"], [0.08, "0.08"], [0.15, "0.15"]]),
              masAnot("Desaturación", "desat", "porcentaje", [[0, "0 %"], [20, "20 %"], [40, "40 %"]])],
        win: [0, 4],
      });
    }

    // objetos del plan que caen en la foto (en orden de aparición)
    const cues = S.cues.filter((c) => !c.block.startsWith("shot_transition") && c.block !== "chapter_question" && inPhoto(c.t))
      .sort((a, b) => a.t - b.t);
    for (const c of cues) out.push(...objetosDeCue(c, i));
    if (i === 0 && !S.plan.title_card) {                      // título apagado: la tarjeta queda para poder prenderlo
      out.splice(1, 0, {
        key: "title", elem: "title_card", nombre: "Título del capítulo (apagado)", t: 0, tEnd: 3.5, win: [0, 4],
        ia: iaLine("ponerlo, con persiana y 'CAPÍTULO 2'", "ordena al espectador"),
        grupos: [{ id: "usar", opciones: [opt("sí", true), opt("no", true)], actual: "no", ia: "sí" }],
        onForm(g, v) { S.plan.title_card = v === "sí" ? clone(S.directorPlan.title_card) : null; },
      });
    }

    // sugerencias que todavía no están en el plan
    for (const s of S.sugs) {
      if (S.sugState[s.id] || !s.word_i) continue;
      const w = wordByI(s.word_i);
      if (!w || !inPhoto(w.start)) continue;
      if (!["add_emphasis", "add_punch"].includes(s.accion.tipo) && !(s.accion.tipo === "anotado" && s.elemento === "spotlight")) continue;
      if (s.accion.tipo === "add_emphasis" && emphasisAt(w.start)) continue;              // ya está en el plan
      if (s.accion.tipo === "add_punch" && (S.plan.punch_in || []).some((x) => near(x, w.start))) continue;
      const el = catEl(s.elemento);
      out.push({
        key: `sug:${s.id}`, elem: s.elemento, nombre: `${el ? el.nombre : s.elemento} «${cleanWord(w.word)}»`, t: w.start, tEnd: w.start + 2.5,
        ia: iaLine(s.titulo.replace(/^'[^']*':\s*/, "").toLowerCase(), cortar(s.por_que)), sug: s, grupos: [],
        nota: s.accion.tipo === "anotado" ? "Pieza que todavía no se dibuja: se guarda para §D." : "Sugerido: ▶ Probar lo agrega.",
        win: [w.start - 1, w.start + 3.5],
      });
    }

    // propuestas de la IA: la palabra del léxico más fuerte que quedó libre y, si la foto sigue vacía, un golpe
    const lexFree = S.ctx.lexicon_hits.filter((h) => inPhoto(h.start) && !emphasisAt(h.start) &&
      !out.some((o) => o.sug && o.sug.word_i === h.i)).sort((a, b) => b.weight - a.weight);
    if (lexFree.length) {
      const h = lexFree[0], mood = MOODS[h.category] || h.category;
      const same = (S.plan.emphasis || []).find((e) => e.category === h.category && Math.abs(e.start - h.start) < 20);
      const [que, why, rec] = same ? ["no poner", `otro mood ${mood} a ${Math.round(Math.abs(h.start - same.start))} s`, false]
        : h.weight <= 1 ? ["no poner sello", "palabra común", false] : ["mood + sello", "palabra con carga", true];
      out.push({ key: `prop:sello:${tkey(h.start)}`, elem: "keyword_stamp", nombre: `Sello rojo «${cleanWord(h.word).toUpperCase()}»`,
        t: h.start, tEnd: h.start + 2.5, ia: iaLine(que, why), prop: { tipo: "emph", i: h.i, rec }, grupos: [],
        nota: rec ? "Propuesta: ▶ Probar lo agrega." : "La IA no lo pondría; ▶ Probar lo agrega igual para que lo veas.",
        win: [h.start - 1, h.start + 3.5] });
    }
    const nPunch = (S.plan.punch_in || []).length;
    if (out.length < 2) {                                    // solo el movimiento: nada pasa en esta foto
      const w = longestWord(i);
      if (w) out.push({ key: `prop:golpe:${tkey(w.start)}`, elem: "punch_in", nombre: `Golpe de zoom «${cleanWord(w.word)}»`,
        t: w.start, tEnd: w.start + 0.8, prop: { tipo: "punch", i: w.i, rec: nPunch < 3 },
        ia: nPunch >= 3 ? iaLine("no poner", `ya hay ${nPunch} golpes (máx 3)`) : iaLine(`golpe en «${cleanWord(w.word)}»`, "subraya sin texto"),
        grupos: [], nota: "Propuesta: ▶ Probar lo agrega.", win: [w.start - 1, w.start + 2] });
    }

    // salida hacia la foto siguiente (o final del capítulo)
    if (i < last()) {
      const nx = photo(i + 1);
      const tr = S.cues.find((c) => c.block.startsWith("shot_transition") && near(c.t, nx.start, 0.2));
      const cur = tr ? SALIDA[tr.block.split(":")[1]] || "corte" : "corte";
      const s12 = sugFor(["dip_to_black"], nx.start, 2.5);
      const [iaF, why] = s12 ? ["fundido negro", "antes de un dato duro"] : nx.rank === "R1" ? ["flash", "golpe de impacto"] : ["corte", "ritmo del documental"];
      out.push({
        key: `salida:${i}`, elem: "salida", nombre: `Salida hacia la foto ${i + 2}`, t: nx.start - 0.5, tEnd: nx.start + 0.5,
        ia: iaLine(iaF === "corte" ? "corte seco" : iaF, why),
        grupos: [{ id: "salida", opciones: FORMAS.salida, actual: ob(`salida:${i}`).formas?.salida || cur, ia: iaF }],
        nota: `Hoy sale: ${cur}. Elegir por cambio llega en §D; tu elección queda anotada.`,
        onForm(g, v) { setForma(this.key, "salida", v); },
        win: [nx.start - 1.5, nx.start + 1.5],
      });
    } else {
      out.push(preguntaObj(p));
      out.push({
        key: `salida:${i}`, elem: "salida", nombre: "Final del capítulo", t: p.end - 1, tEnd: p.end,
        ia: iaLine("fundido a negro", "termina el capítulo"),
        grupos: [{ id: "salida", opciones: FORMAS.salida, actual: ob(`salida:${i}`).formas?.salida || "corte", ia: "fundido negro" }],
        nota: "El fundido final llega en §D; tu elección queda anotada.",
        onForm(g, v) { setForma(this.key, "salida", v); },
        win: [p.end - 3, p.end],
      });
    }

    // extras agregados a mano que todavía no se dibujan (cita, tercio inferior)
    for (const [k, o] of Object.entries(S.obj)) {
      if (o.extra && o.foto === i) {
        out.push({ key: k, elem: o.elem, nombre: o.nombre, t: o.t, tEnd: o.t + 3, ia: iaLine(o.ia || "probalo en el render", "plantilla nueva en §D"),
                   grupos: [], nota: "Pieza nueva: la plantilla llega en §D. Queda anotada.", win: [o.t - 1, o.t + 4] });
      }
    }
    return out;
  }

  function cortar(txt) { return txt.split(/[.:;]/)[0].split(/\s+/).slice(0, 6).join(" ").toLowerCase(); }
  function strongestWord(i) {
    const p = photo(i);
    const ws = S.story.words.filter((w) => w.start >= p.start && w.start < p.end);
    const hits = S.ctx.lexicon_hits.filter((h) => h.start >= p.start && h.start < p.end).sort((a, b) => b.weight - a.weight);
    return hits.length ? wordByI(hits[0].i) : ws[Math.floor(ws.length / 2)];
  }
  function longestWord(i) {
    const p = photo(i);
    const ws = S.story.words.filter((w) => w.start >= p.start && w.start < p.end && cleanWord(w.word).length > 4);
    return ws.sort((a, b) => cleanWord(b.word).length - cleanWord(a.word).length)[0];
  }
  function applyProp(pr) {                                   // propuesta de la IA → pieza del plan
    const w = wordByI(pr.i);
    if (pr.tipo === "emph") addEmphasis(pr.i, { stamp: true, icon: false });
    else addPunch(w.start);
    return tkey(w.start);
  }
  function masToken(label, token, opts) {
    return { label, opciones: opts.map(([v, l]) => ({ v, label: l })), get: () => tok(token), set: (v) => { S.tokens[token] = v; } };
  }
  function masAnot(label, elem, attr, opts) {
    return { label, anotado: true, opciones: opts.map(([v, l]) => ({ v, label: l })),
             get: () => (S.anotado[elem] || {})[attr] ?? opts[0][0], set: (v) => { (S.anotado[elem] = S.anotado[elem] || {})[attr] = v; } };
  }
  function masPiece(label, piece, field, opts) {
    return { label, opciones: opts.map(([v, l]) => ({ v, label: l })), get: () => piece[field], set: (v) => { piece[field] = v; } };
  }

  function objetosDeCue(c, i) {
    const b = c.block.split(":")[0], pc = pieceOf(c), t = c.t, out = [];
    const piece = pc && pc.obj;
    const base = { t, tEnd: t + c.dur, win: [t - 1, t + c.dur + 1], cue: c };
    if (b === "title_card") {
      const s01 = S.sugs.find((s) => s.id === "S01");
      out.push({ ...base, key: "title", elem: "title_card", nombre: "Título del capítulo", texto: c.text,
        ia: iaLine("persiana con 'CAPÍTULO 2', 3 s", "ordena al espectador"), sug: s01,
        grupos: [{ id: "entrada", opciones: [opt("persiana", true), opt("cascada"), opt("máquina"), opt("sello"), opt("fade")],
                   actual: ob("title").formas?.entrada || "persiana", ia: "persiana" }],
        onForm(g, v) { setForma(this.key, "entrada", v); (S.anotado.title_card = S.anotado.title_card || {}).entrada = v; },
        mas: [masToken("Duración", "title_dur", [[2, "2 s"], [2.5, "2.5 s"], [3, "3 s"]])], posicion: false });
    } else if (b === "data_callout" && piece) {
      const tokName = piece.kind === "figure" ? "anim_figure" : piece.kind === "year" ? "anim_year" : "anim_name_place";
      const s = sugFor(["data_callout"], t);
      const anot = ob(`dato:${tkey(t)}`).formas?.entrada;
      out.push({ ...base, key: `dato:${tkey(t)}`, elem: "data_callout", nombre: `Dato «${piece.text}»`, sug: s,
        ia: s && s.id === "S10" ? iaLine("dato, no contador", "6,500 ya se contó") : iaLine("cascada, del lado tranquilo", "fija el dato duro"),
        grupos: [{ id: "entrada", opciones: [opt("cascada", true), opt("persiana", true), opt("máquina"), opt("sello", true), opt("fade"), opt("golpe", true)],
                   actual: anot && ["máquina", "fade"].includes(anot) ? anot : TEXTO[tok(tokName)] || "golpe", ia: "cascada" }],
        nota: "La entrada de los datos es una sola para todo el canal: cambiarla acá cambia todos los datos.",
        onForm(g, v) {
          setForma(this.key, "entrada", v);
          const inv = { cascada: "cascade", persiana: "slide", sello: "stamp", golpe: "number_pop" };
          if (inv[v]) S.tokens[tokName] = inv[v];
        },
        mas: [masToken("Tamaño", "callout_anton_px", [[130, "S"], [168, "M"], [200, "L"]]),
              masPiece("Duración", piece, "duration", [[2.5, "2.5 s"], [3.5, "3.5 s"], [4.5, "4.5 s"]])],
        posicion: piece });
    } else if (b === "count_up") {
      out.push({ ...base, key: `contador:${tkey(t)}`, elem: "count_up", nombre: `Contador «${c.text}»`,
        ia: iaLine("contador para la cifra más dura", "una vez por video"), grupos: [],
        mas: [masToken("Rampa", "count_dur", [[0.8, "0.8 s"], [1.2, "1.2 s"], [1.6, "1.6 s"]]),
              masToken("Quieto al final", "count_hold_sec", [[1.5, "1.5 s"], [2.5, "2.5 s"], [3.5, "3.5 s"]])] });
    } else if (b === "source_tag") {
      out.push({ ...base, key: `fuente:${tkey(t)}`, elem: "source_tag", nombre: `Fuente «${c.text}»`,
        ia: iaLine("fuente bajo el dato", "nadie la lee, todos la sienten"), grupos: [] });
    } else if (b === "archive_clipping" && piece) {
      const s = S.sugs.find((x) => x.elemento === "archive_clipping" && (x.accion.fact_idx === piece.fact_idx ||
        (x.word_i && wordByI(x.word_i) && near(wordByI(x.word_i).start, t, 1.5))));
      const iaF = s && s.id === "S03" ? "ficha" : "periódico";
      out.push({ ...base, key: `recorte:${tkey(t)}`, elem: "archive_clipping", nombre: `Recorte «${piece.headline}»`, sug: s,
        ia: iaF === "ficha" ? iaLine("ficha forense", "dato de víctimas") : iaLine("periódico, 4 s", "hecho público, se lee rápido"),
        grupos: [{ id: "estilo", opciones: FORMAS.recorte, actual: ob(`recorte:${tkey(t)}`).formas?.estilo || "periódico", ia: iaF }],
        onForm(g, v) {
          setForma(this.key, "estilo", v);
          const m = { "periódico": "periodico", "post-it": "postit", ficha: "ficha", carpeta: "carpeta" };
          (S.anotado.archive_clipping = S.anotado.archive_clipping || {}).estilo = m[v];
          if (v === "periódico" && s && s.id === "S02") piece.duration = 4;
        },
        mas: [masPiece("Duración", piece, "duration", [[3, "3 s"], [4, "4 s"], [5, "5 s"], [6, "6 s"]]),
              masToken("Ancho", "archive_max_w_frac", [[0.24, "24 %"], [0.28, "28 %"], [0.3, "30 %"]])],
        posicion: piece });
    } else if ((b === "keyword_emphasis" || b === "icon_callout") && piece) {
      const hit = S.ctx.lexicon_hits.find((h) => near(h.start, piece.start)) || { weight: piece.weight || 1 };
      const mood = MOODS[piece.category] || piece.category;
      const sMood = sugFor(["keyword_emphasis", "icon_callout"], t);
      out.push({ ...base, key: `mood:${tkey(t)}`, elem: "keyword_emphasis", nombre: `Mood ${mood} «${piece.word}»`, sug: sMood,
        ia: iaLine(`sí, ${piece.duration} s, suave`, "un momento, no un filtro"),
        grupos: [{ id: "intensidad", opciones: FORMAS.mood, actual: ob(`mood:${tkey(t)}`).formas?.intensidad || "suave", ia: "suave" }],
        onForm(g, v) { setForma(this.key, "intensidad", v); (S.anotado.keyword_emphasis = S.anotado.keyword_emphasis || {}).intensidad = v === "suave" ? "baja" : "media"; },
        mas: [masPiece("Duración", piece, "duration", [[1.5, "1.5 s"], [2.5, "2.5 s"], [4, "4 s"]])],
        quitar: () => { S.plan.emphasis = S.plan.emphasis.filter((e) => e !== piece); } });
      if (piece.icon_callout) {
        const k = `icono:${tkey(t)}`;
        out.push({ ...base, key: k, elem: "icon_callout", nombre: `Ícono ${piece.icon} «${piece.word}»`,
          ia: iaLine(`${ICON_ANIM_INV[piece.icon_anim] || "sello"}, con la palabra`, "dibuja lo que dice la voz"),
          grupos: [{ id: "entrada", label: "Entrada", opciones: FORMAS.icono, actual: ICON_ANIM_INV[piece.icon_anim] || "sello",
                     ia: mood === "oscuridad" ? "sello" : mood === "agua" ? "prensa" : "tinta" },
                   { id: "hold", label: "Mientras está", opciones: FORMAS.icono_hold, actual: ob(k).formas?.hold || "respira", ia: "respira" }],
          onForm(g, v) {
            if (g === "entrada") piece.icon_anim = ICON_ANIM[v];
            else { setForma(this.key, "hold", v); (S.anotado.icon_callout = S.anotado.icon_callout || {}).hold = { respira: "respirar", deriva: "deriva", pulso: "pulso", quieto: "quieto" }[v]; }
          },
          mas: [masToken("Tamaño", "icon_px", [[130, "S"], [190, "M"], [280, "L"]]),
                masPiece("Con sello de palabra", piece, "stamp", [[true, "sí"], [false, "no"]])],
          posicion: piece, quitar: () => { piece.icon_callout = false; piece.icon = null; } });
      } else {
        const k = `sello:${tkey(t)}`;
        const iaF = hit.weight >= 3 ? "sello" : hit.weight <= 1 ? "sin sello" : "sello";
        const why = hit.weight >= 3 ? "palabra rara" : hit.weight <= 1 ? "palabra común" : "palabra con carga";
        out.push({ ...base, key: k, elem: "keyword_stamp", nombre: `Sello rojo «${String(piece.word).toUpperCase()}»`,
          ia: iaLine(iaF === "sin sello" ? "no poner sello" : "sello rojo", why),
          grupos: [{ id: "forma", opciones: FORMAS.sello, actual: !piece.stamp ? "sin sello" : ob(k).formas?.forma || "sello", ia: iaF }],
          onForm(g, v) {
            piece.stamp = v !== "sin sello";
            setForma(this.key, "forma", v);
            if (v !== "sin sello") (S.anotado.keyword_stamp = S.anotado.keyword_stamp || {}).entrada = v;
          },
          mas: [masToken("Tamaño", "emphasis_stamp_px", [[84, "S"], [112, "M"], [140, "L"]])],
          posicion: piece, quitar: () => { piece.stamp = false; } });
      }
    } else if (b === "punch_in" && pc && pc.t !== undefined) {
      const w = wordAtT(t), s = sugFor(["punch_in"], t);
      const fz = Object.entries(PUNCH).find(([, v]) => v === tok("punch_scale"));
      out.push({ ...base, key: `golpe:${tkey(t)}`, elem: "punch_in", nombre: `Golpe de zoom «${cleanWord(w.word)}»`, sug: s,
        ia: iaLine(`golpe en «${cleanWord(w.word)}»`, s ? "gira el capítulo" : "subraya sin texto"),
        grupos: [{ id: "fuerza", opciones: FORMAS.golpe, actual: fz ? fz[0] : "normal", ia: "normal" }],
        nota: "La fuerza del golpe es una sola para todo el canal.",
        onForm(g, v) { S.tokens.punch_scale = PUNCH[v]; },
        quitar: () => { S.plan.punch_in = S.plan.punch_in.filter((x) => x !== pc.t); } });
    } else if (b === "evidence_zoom") {
      out.push({ ...base, key: `zoom:${tkey(t)}`, elem: "punch_in", nombre: "Zoom de detalle", ia: iaLine("acercar al detalle", "muestra la prueba"), grupos: [],
        quitar: () => { S.plan.evidence_zoom = null; } });
    } else if (b === "icon_array") {
      out.push({ ...base, key: `matriz:${tkey(t)}`, elem: "icon_array", nombre: `Matriz «${c.text}»`, ia: iaLine("figuras en filas de 10", "hace contable la proporción"), grupos: [],
        quitar: () => { S.plan.icon_array = null; } });
    }
    return out;
  }

  function preguntaObj(p) {
    const q = S.plan.chapter_question;
    const k = "pregunta";
    return {
      key: k, elem: "chapter_question", nombre: "Pregunta de cierre", t: Math.max(0, S.story.duration - 3.5), tEnd: S.story.duration,
      ia: iaLine("escribí una pregunta", "gancho para el capítulo 3"), pregunta: true, texto: q && q.manual ? q.text : "",
      grupos: [{ id: "entrada", opciones: [opt("persiana"), opt("máquina")], actual: ob(k).formas?.entrada || "persiana", ia: "persiana" }],
      nota: "La entrada y la pausa de 3 s con la voz en silencio llegan en §D. El texto y el fondo se ven ya.",
      onForm(g, v) { setForma(k, "entrada", v); (S.anotado.chapter_question = S.anotado.chapter_question || {}).entrada = v === "máquina" ? "maquina" : v; },
      mas: [masToken("Fondo oscurecido", "question_dim", [[0.5, "50 %"], [0.7, "70 %"]]),
            ...(q ? [masPiece("Duración", q, "duration", [[2.5, "2.5 s"], [3, "3 s"], [3.5, "3.5 s"]])] : [])],
      quitar: () => { S.plan.chapter_question = null; },
      win: [Math.max(0, S.story.duration - 4.5), S.story.duration],
    };
  }

  // ═══════════════════════════════════════════════════════════════
  //  Acciones: Probar, forma, Se queda, Nunca
  // ═══════════════════════════════════════════════════════════════
  function playWindow(from, to) {
    const d = S.story.duration;
    F.full = false;
    F.probar = { from: Math.max(0, from), to: Math.min(d - 0.05, to) };
    seek(F.probar.from);
    player().play();
    syncAudio(true);
    syncPlay();
  }
  function probar(o) {
    if (o.pregunta) {
      const txt = ($(`[data-q="${o.key}"]`) || {}).value || o.texto;
      if (!txt || !txt.trim()) { setStatus("escribí la pregunta en la tarjeta y tocá ▶ Probar", "err"); $(`[data-q="${o.key}"]`)?.focus(); return; }
      F.autoProbar = o.win;
      mutate("pregunta de cierre", () => { setQuestion(txt); setObj(o.key, { probado: true }); });
      return;
    }
    if (o.prop) {                                              // propuesta de la IA: Probar la agrega
      F.autoProbar = o.win;
      mutate(`probando: ${o.nombre}`, () => { applyProp(o.prop); touch(o.elem); });
      return;
    }
    if (o.sug && !S.sugState[o.sug.id] && o.key.startsWith("sug:")) {   // sugerencia que todavía no está en el plan
      F.autoProbar = o.win;
      if (o.sug.accion.tipo === "anotado") {
        mutate(`probando ${o.sug.id}`, () => { applyPreset(catEl(o.sug.elemento) || { id: o.sug.elemento }, o.sug.preset || {}); S.sugState[o.sug.id] = "probando"; touch(o.sug.elemento); });
        setStatus("esta pieza todavía no se dibuja (llega en §D): se guardó tu elección", "busy");
      } else trySuggestion(o.sug);
      return;
    }
    const g = (o.grupos || [])[0];
    if (g && g.ia && !ob(o.key).probado && g.actual !== g.ia && o.onForm) {   // 1er Probar = la forma de la IA
      F.autoProbar = o.win;
      mutate(`${o.nombre}: forma de la IA → ${g.ia}`, () => { o.onForm(g.id, g.ia); setObj(o.key, { probado: true }); touch(o.elem); });
      const live = (g.opciones.find((x) => x.v === g.ia) || {}).live;
      if (!live) setTimeout(() => setStatus(`«${g.ia}» todavía no se dibuja (llega en §D): se ve la forma actual`, "busy"), 600);
      return;
    }
    if (!ob(o.key).probado) mutate(`probando ${o.nombre}`, () => { setObj(o.key, { probado: true }); touch(o.elem); }, { preview: false });
    playWindow(...o.win);
  }
  function chooseForma(o, gid, v) {
    const g = o.grupos.find((x) => x.id === gid);
    const fo = g && g.opciones.find((x) => x.v === v);
    F.autoProbar = o.win;
    mutate(`${o.nombre}: ${v}`, () => { o.onForm(gid, v); setObj(o.key, { probado: true }); touch(o.elem); });
    if (fo && !fo.live) setTimeout(() => setStatus(`«${v}» queda anotado: el preview todavía no lo dibuja (llega en §D)`, "busy"), 600);
  }
  function toggleKeep(o, on) {
    const changesPlan = on && ((o.prop) || (o.sug && o.key.startsWith("sug:") && o.sug.accion.tipo !== "anotado" && S.sugState[o.sug.id] !== "probando"));
    mutate(`${o.nombre}: ${on ? "☑ se queda" : "☐ pendiente"}`, () => {
      if (o.sug && o.key.startsWith("sug:") && on) {               // aprobar algo sugerido = aplicarlo
        if (o.sug.accion.tipo !== "anotado" && S.sugState[o.sug.id] !== "probando") {
          if (!S.sugUndo[o.sug.id]) S.sugUndo[o.sug.id] = sugUndoInfo(o.sug);
          applyPreset(catEl(o.sug.elemento) || { id: o.sug.elemento }, o.sug.preset || {});
          runAction(o.sug.accion, o.sug.word_i, catEl(o.sug.elemento));
        }
        S.sugState[o.sug.id] = "si";
        const t = tkey(wordByI(o.sug.word_i).start);       // la tarjeta que reemplaza a la sugerida nace aprobada
        ["mood", "sello", "icono", "golpe"].forEach((k) => setObj(`${k}:${t}`, { v: "si" }));
      }
      if (o.prop && on) {
        const t = applyProp(o.prop);
        (o.prop.tipo === "emph" ? ["mood", "sello"] : ["golpe"]).forEach((k) => setObj(`${k}:${t}`, { v: "si" }));
      }
      if (o.sug && !o.key.startsWith("sug:")) S.sugState[o.sug.id] = on ? "si" : "probando";
      setObj(o.key, { v: on ? "si" : undefined, nombre: o.nombre });
      if (!on) delete S.obj[o.key].v;
      const el = catEl(o.elem);
      if (el) {
        if (on && !S.marks[el.id]) S.marks[el.id] = { v: "si", auto: true };
        if (!on && S.marks[el.id]?.auto && !Object.entries(S.obj).some(([k, x]) => x.v === "si" && k !== o.key && objElem(k) === el.id)) delete S.marks[el.id];
      }
      touch(o.elem);
    }, { preview: changesPlan ? undefined : false });
  }
  function objElem(key) {
    const t = key.split(":")[0];
    return { mov: "movimiento", look: "paleta", title: "title_card", dato: "data_callout", contador: "count_up", fuente: "source_tag",
             recorte: "archive_clipping", mood: "keyword_emphasis", icono: "icon_callout", sello: "keyword_stamp", golpe: "punch_in",
             salida: "salida", pregunta: "chapter_question" }[t] || t;
  }
  function nunca(o, tipo) {
    mutate(tipo ? `${o.nombre}: ✖ nunca este tipo` : `${o.nombre}: ✖ nunca`, () => {
      if (tipo) { const el = catEl(o.elem); if (el) S.marks[el.id] = { v: "no" }; return; }
      if (o.sug && o.key.startsWith("sug:")) { revertSuggestion(o.sug); S.sugState[o.sug.id] = "no"; }
      else if (o.sug) S.sugState[o.sug.id] = "no";
      if (o.quitar) o.quitar();
      setObj(o.key, { v: "no", nombre: o.nombre, t: o.t, foto: S.fotoActual });
      touch(o.elem);
    });
  }

  // ── + Agregar algo a esta foto
  const AGREGAR = [["dato", "Dato"], ["sello", "Sello"], ["icono", "Ícono"], ["recorte", "Recorte"], ["contador", "Contador"],
                   ["mood", "Mood"], ["cita", "Cita"], ["tercio", "Tercio inferior"], ["pregunta", "Pregunta de cierre"]];
  function agregar(tipo) {
    const i = S.fotoActual, p = photo(i);
    const ws = S.story.words.filter((w) => w.start >= p.start && w.start < p.end);
    const hits = S.ctx.lexicon_hits.filter((h) => h.start >= p.start && h.start < p.end && !emphasisAt(h.start)).sort((a, b) => b.weight - a.weight);
    F.addOpen = false;
    try {
      if (tipo === "sello" || tipo === "mood" || tipo === "icono") {
        const h = tipo === "icono" ? hits.find((x) => x.icon) : hits[0];
        if (!h) throw new Error(tipo === "icono" ? "en esta foto no hay una palabra que un ícono dibuje literalmente" : "en esta foto no hay palabras del léxico libres");
        F.autoProbar = [h.start - 1, h.start + 3.5];
        mutate(`agregado ${tipo} en «${h.word}»`, () => addEmphasis(h.i, { stamp: tipo !== "mood", icon: tipo === "icono" }));
      } else if (tipo === "recorte") {
        const words = new Set(ws.map((w) => cleanWord(w.word).toLowerCase()).filter((w) => w.length > 3));
        const used = new Set((S.plan.archive_clippings || []).map((a) => a.fact_idx));
        const f = S.ctx.facts.filter((x) => x.eligible && !used.has(x.idx))
          .map((x) => ({ x, n: x.text.toLowerCase().split(/\W+/).filter((w) => words.has(w)).length })).sort((a, b) => b.n - a.n)[0];
        if (!f) throw new Error("no quedan datos elegibles para un recorte");
        F.autoProbar = [p.start, p.start + 5];
        mutate(`agregado recorte del dato ${f.x.idx}`, () => addArchive(f.x.idx, p.start + 0.3));
      } else if (tipo === "dato" || tipo === "contador") {
        const found = cifraEnFoto(ws);
        if (!found) throw new Error("la voz no dice ninguna cifra de los datos en esta foto");
        F.autoProbar = [found.w.start - 1, found.w.start + 4];
        const ph = photo(i);
        mutate(`agregado ${tipo} «${found.text}»`, () => {
          if (tipo === "dato") {
            planList("callouts").push({ text: found.text, start: found.w.start, kind: "figure", duration: 2.5,
              side: ph.quiet_side === "left" ? "left" : "right", fact_idx: found.f.idx, source: found.f.source || "", manual: true });
            S.plan.callouts.sort((a, b) => a.start - b.start);
          } else {
            S.plan.count_up = { value_text: found.num, unit: found.unit, start: found.w.start, fact_idx: found.f.idx, source: found.f.source || "", manual: true };
          }
        });
      } else if (tipo === "cita" || tipo === "tercio") {
        const k = `extra:${tipo}:${i}`;
        const nombre = tipo === "cita" ? "Cita" : "Tercio inferior";
        mutate(`agregado ${nombre} (anotado)`, () => setObj(k, { extra: true, elem: tipo === "cita" ? "quote_card" : "lower_third", nombre, t: p.start + 0.5, foto: i,
          ia: tipo === "cita" ? "solo con cita literal en los datos" : "cuando aparece una persona" }));
        setStatus(`${nombre}: la plantilla llega en §D; quedó anotada en esta foto`, "busy");
      } else if (tipo === "pregunta") {
        if (i !== last()) { goFoto(last()); setStatus("la pregunta de cierre va en la última foto: escribila en su tarjeta"); }
        else $('[data-q="pregunta"]')?.focus();
      }
    } catch (e) { setStatus(e.message, "err"); renderObjs(); }
  }
  // cifra que la voz dice en la foto y que está LITERAL en un dato elegible (si no, el candado la quitaría)
  function cifraEnFoto(ws) {
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
  function goFoto(i) {
    i = Math.max(0, Math.min(last(), i));
    S.fotoActual = i;
    if (!S.visitadas.includes(i)) S.visitadas.push(i);
    F.more = {};
    F.addOpen = false;
    F.probar = null;
    player().pause();
    seek(photo(i).start + 0.02);
    render();
    autosave();
  }
  function estadoFoto(i) {
    const objs = objetos(i);
    const dec = objs.filter((o) => ob(o.key).v === "si" || ob(o.key).v === "no").length;
    return { total: objs.length, dec, done: dec === objs.length && objs.length > 0 };
  }
  function render() {
    const i = S.fotoActual, p = photo(i);
    $("#f-num").textContent = `FOTO ${i + 1} de ${photos().length}`;
    $("#f-range").textContent = `${fmt(p.start)}–${fmt(p.end)}`;
    $("#f-prev").disabled = i === 0;
    $("#f-next").disabled = i === last();
    renderWords();
    renderDots();
    renderObjs();
  }
  function renderWords() {
    const p = photo(S.fotoActual);
    const ws = S.story.words.filter((w) => w.start >= p.start - 0.05 && w.start < p.end - 0.05);
    const cueWords = new Set(S.cues.filter((c) => !c.block.startsWith("shot_transition")).map((c) => wordAtT(c.t).i));
    $("#f-words").innerHTML = ws.map((w) => {
      const h = lexAt(w.i);
      const cls = ["w", h ? "lex lex-w" + h.weight : "", cueWords.has(w.i) ? "cue" : ""].join(" ");
      return `<span class="${cls}" data-i="${w.i}" title="${fmt(w.start)}${h ? " · " + (MOODS[h.category] || h.category) + " · peso " + h.weight : ""}">${esc(w.word)}</span>`;
    }).join(" ");
    $("#f-words").querySelectorAll(".w").forEach((el) => el.addEventListener("click", () => {
      const w = wordByI(+el.dataset.i);
      playWindow(w.start - 0.3, photo(S.fotoActual).end);
    }));
  }
  function renderDots() {
    $("#f-dots").innerHTML = photos().map((p, i) => {
      const st = estadoFoto(i);
      const cls = i === S.fotoActual ? "cur" : st.done ? "done" : S.visitadas.includes(i) ? "seen" : "";
      return `<button class="dot ${cls}" data-f="${i}" title="Foto ${i + 1} · ${st.dec}/${st.total} decididos${st.done ? " · lista" : ""}">${i + 1}</button>`;
    }).join("") + `<span class="dots-count">${S.fotoActual + 1}/${photos().length}</span>`;
    $("#f-dots").querySelectorAll(".dot").forEach((b) => b.addEventListener("click", () => goFoto(+b.dataset.f)));
  }
  function formaButtons(o, g) {
    return g.opciones.map((x) => {
      const on = x.v === g.actual, isIA = x.v === g.ia;
      const sw = g.swatch ? `<span class="swatch" style="background:${esc(x.v)}"></span>` : "";
      return `<button class="forma ${on ? "on" : ""} ${x.live ? "" : "soon"}" data-g="${g.id}" data-v="${esc(x.v)}"
        title="${x.live ? "Se ve en el preview" : "Se guarda; el preview todavía no lo dibuja (§D)"}">${sw}${esc(x.label)}${isIA ? '<span class="iatag">IA</span>' : ""}</button>`;
    }).join("");
  }
  function zonas(o) {
    const side = o.posicion.side || "right";
    const z = ob(o.key).formas?.zona || (side === "left" ? "ml" : "mr");
    return `<div class="mas-row"><span class="ml-l">Posición</span><span class="zonas">` +
      ["tl", "tc", "tr", "ml", "mc", "mr", "bl", "bc", "br"].map((k) =>
        `<button class="zona ${k === z ? "on" : ""} ${k[1] === "c" ? "soon" : ""}" data-z="${k}" title="${k[1] === "c" ? "centro: queda anotado (§D)" : k[1] === "l" ? "izquierda" : "derecha"}"></button>`).join("") +
      `</span></div>`;
  }
  function masBox(o) {
    let h = "";
    (o.mas || []).forEach((m, k) => {
      const cur = m.get();
      h += `<div class="mas-row"><span class="ml-l">${esc(m.label)}${m.anotado ? ' <span class="anot">anotado</span>' : ""}</span>` +
        m.opciones.map((x) => `<button class="mini ${same(x.v, cur) ? "on" : ""}" data-m="${k}" data-v='${esc(JSON.stringify(x.v))}'>${esc(x.label)}</button>`).join("") + "</div>";
    });
    if (o.posicion) h += zonas(o);
    h += `<div class="mas-row nunca"><button class="mini no" data-nunca="1">✖ Nunca (sacar esto)</button>` +
      (catEl(o.elem) ? ` <button class="mini no" data-nunca-tipo="1">✖ No quiero ${esc(catEl(o.elem).nombre.toLowerCase())} en el canal</button>` : "") + "</div>";
    return h;
  }
  function card(o, n) {
    const st = ob(o.key).v;
    const cls = st === "si" ? "st-si" : st === "no" ? "st-no" : o.key.startsWith("sug:") ? "st-sug" : "";
    if (st === "no") {
      return `<div class="ocard st-no" data-k="${esc(o.key)}"><div class="oc-head"><span class="num">${CIRC[n] || n + 1}</span>
        <b>${esc(o.nombre)}</b> <span class="when">${fmt(o.t)}</span> <span class="badge fut">✖ nunca</span>
        <button class="mini" data-undo-no="1">volver a ponerlo</button></div></div>`;
    }
    const groups = (o.grupos || []).map((g) => `<div class="formas">${g.label ? `<span class="fl">${esc(g.label)}:</span>` : '<span class="fl">Otras formas:</span>'}${formaButtons(o, g)}</div>`).join("");
    const q = o.pregunta ? `<textarea class="qtxt" data-q="${esc(o.key)}" rows="2" maxlength="140" placeholder="¿…? (la escribís vos)">${esc(o.texto || "")}</textarea>` : "";
    const hasMore = (o.mas && o.mas.length) || o.posicion || true;
    return `<div class="ocard ${cls}" data-k="${esc(o.key)}">
      <div class="oc-head"><span class="num">${CIRC[n] || n + 1}</span> <b>${esc(o.nombre)}</b> <span class="when">${fmt(o.t)}</span>
        ${o.key.startsWith("sug:") ? '<span class="badge sugd">sugerido</span>' : ""}</div>
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
      el.querySelectorAll(".forma").forEach((b) => b.addEventListener("click", () => chooseForma(o, b.dataset.g, b.dataset.v)));
      el.querySelector("[data-more]")?.addEventListener("click", (e) => { e.preventDefault(); F.more[o.key] = !F.more[o.key]; renderObjs(); });
      el.querySelectorAll("[data-m]").forEach((b) => b.addEventListener("click", () => {
        const m = o.mas[+b.dataset.m], v = JSON.parse(b.dataset.v);
        F.autoProbar = o.win;
        mutate(`${o.nombre}: ${m.label} → ${b.textContent}`, () => { m.set(v); touch(o.elem); });
      }));
      el.querySelectorAll("[data-z]").forEach((b) => b.addEventListener("click", () => {
        const z = b.dataset.z;
        F.autoProbar = o.win;
        mutate(`${o.nombre}: posición ${z}`, () => { setForma(o.key, "zona", z); if (z[1] !== "c") o.posicion.side = z[1] === "l" ? "left" : "right"; });
      }));
      el.querySelector("[data-nunca]")?.addEventListener("click", () => nunca(o, false));
      el.querySelector("[data-nunca-tipo]")?.addEventListener("click", () => nunca(o, true));
      el.querySelector("[data-undo-no]")?.addEventListener("click", () => mutate(`${o.nombre}: vuelve`, () => { delete S.obj[o.key].v; }, { preview: false }));
      el.querySelector("[data-q]")?.addEventListener("change", (e) => {
        if ((S.plan.chapter_question || {}).text === e.target.value.trim()) return;
        F.autoProbar = o.win;
        mutate("pregunta de cierre", () => setQuestion(e.target.value));
      });
    });
    // rechazados de esta foto que ya no están en el plan (para poder volver atrás)
    const gone = Object.entries(S.obj).filter(([k, x]) => x.v === "no" && x.foto === S.fotoActual && !objs.some((o) => o.key === k));
    if (gone.length) {
      $("#f-objs").insertAdjacentHTML("beforeend", `<div class="gone">Sacaste: ${gone.map(([, x]) => esc(x.nombre)).join(" · ")} <span class="tech">(Ctrl+Z para volver)</span></div>`);
    }
    $("#f-add-list").hidden = !F.addOpen;
  }
  function syncPlay() {
    $("#btn-play").textContent = !player().paused && !F.full ? "❚❚ Pausa" : "▶ Play esta foto";
    $("#btn-full").textContent = F.full && !player().paused ? "❚❚ Pausar capítulo" : "▶ Ver capítulo completo";
  }

  // recorrido para el resumen (§F: aprobado / pendiente / rechazado por foto)
  function recorrido() {
    if (!F.infos.length) return undefined;
    return photos().map((p, i) => ({
      foto: i + 1, desde: fmt(p.start), hasta: fmt(p.end), vista: S.visitadas.includes(i),
      objetos: [...objetos(i).map((o) => ({
        nombre: o.nombre, t: fmt(o.t), estado: ob(o.key).v === "si" ? "si" : ob(o.key).v === "no" ? "no" : "pendiente",
        forma: (o.grupos || []).map((g) => g.actual).filter(Boolean).join(" · "), ia: o.ia,
      })), ...Object.entries(S.obj).filter(([k, x]) => x.v === "no" && x.foto === i && !objetos(i).some((o) => o.key === k))
        .map(([, x]) => ({ nombre: x.nombre, t: fmt(x.t || p.start), estado: "no", forma: "", ia: "" }))],
    }));
  }

  // ═══════════════════════════════════════════════════════════════
  //  Ganchos para el núcleo (lab.js)
  // ═══════════════════════════════════════════════════════════════
  window.LAB_UI = {
    async init() {
      F.infos = await Promise.all(photos().map((_, i) => api(`/objetos?foto=${i}`)));
      $("#f-prev").addEventListener("click", () => goFoto(S.fotoActual - 1));
      $("#f-next").addEventListener("click", () => goFoto(S.fotoActual + 1));
      $("#f-add").addEventListener("click", () => {
        F.addOpen = !F.addOpen;
        $("#f-add-list").innerHTML = AGREGAR.map(([k, l]) => `<button class="btn ghost" data-add="${k}">${l}</button>`).join("");
        $("#f-add-list").querySelectorAll("[data-add]").forEach((b) => b.addEventListener("click", () => agregar(b.dataset.add)));
        $("#f-add-list").hidden = !F.addOpen;
      });
      $("#btn-full").addEventListener("click", () => {
        if (F.full && !player().paused) { player().pause(); return; }
        F.probar = null;
        F.full = true;
        seek(0);
        player().play();
        syncAudio(true);
      });
      player().addEventListener("pause", () => {
        if (F.full) {                                   // al pausar el capítulo, el lab salta a esa foto
          F.full = false;
          const idx = photoAt(player().currentTime || 0).idx;
          if (idx !== S.fotoActual) { S.fotoActual = idx; if (!S.visitadas.includes(idx)) S.visitadas.push(idx); render(); autosave(); }
        }
        syncPlay();
      });
      player().addEventListener("ended", () => { F.full = false; syncPlay(); });
      const qf = +new URLSearchParams(location.search).get("foto");          // ?foto=N abre directo en la foto N
      if (qf >= 1 && qf <= photos().length) S.fotoActual = qf - 1;
      if (!S.visitadas.includes(S.fotoActual)) S.visitadas.push(S.fotoActual);
      render();
    },
    afterChange() { renderObjs(); renderDots(); renderWords(); },
    afterCues() { renderObjs(); renderDots(); renderWords(); },
    afterPreview() {
      if (F.autoProbar) { const w = F.autoProbar; F.autoProbar = null; playWindow(w[0], w[1]); }
      else if (!F.ready) seek(photo(S.fotoActual).start + 0.02);      // 1er preview: ir a la foto donde quedó Omar
      F.ready = true;
    },
    ownsPlayButton: true,
    onTried(s, t) { F.autoProbar = [t - 1, t + 3.5]; },
    onPlayButton() {
      const p = photo(S.fotoActual);
      if (!player().paused) { player().pause(); F.probar = null; syncAudio(true); syncPlay(); return; }
      playWindow(p.start, p.end);
    },
    tick(t, force) {
      $("#tc").textContent = `${fmt(t)}`;
      if (F.probar && t >= F.probar.to) { player().pause(); F.probar = null; syncAudio(true); }
      const objs = F.current || [];
      const active = S.cues.filter((c) => !c.block.startsWith("shot_transition") && c.t <= t && t < c.t + Math.max(c.dur, 0.4));
      $("#now-line").innerHTML = active.map((c) => `<span class="chip">${esc(nombre(c.block))}</span>`).join("");
      document.querySelectorAll("#f-words .w").forEach((el) => {
        const w = wordByI(+el.dataset.i);
        el.classList.toggle("now", w.start <= t && t < w.end + 0.15);
      });
      document.querySelectorAll(".ocard").forEach((el) => {
        const o = objs.find((x) => x.key === el.dataset.k);
        el.classList.toggle("playing", !!o && !player().paused && t >= o.t && t <= o.tEnd);
      });
      if (F.full) {
        const idx = photoAt(t).idx;
        document.querySelectorAll("#f-dots .dot").forEach((b) => b.classList.toggle("running", +b.dataset.f === idx));
        $("#f-num").textContent = `FOTO ${idx + 1} de ${photos().length}`;
      }
      syncPlay();
    },
    onKey(e) {
      if (e.key === "ArrowRight" && !e.ctrlKey) { goFoto(S.fotoActual + 1); return true; }
      if (e.key === "ArrowLeft" && !e.ctrlKey) { goFoto(S.fotoActual - 1); return true; }
      return false;
    },
    recorrido,
    _debug: { F, objetos, probar, chooseForma, toggleKeep, nunca, agregar, goFoto, playWindow },
  };
})();
