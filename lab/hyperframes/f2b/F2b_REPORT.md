# F2b_REPORT — Director v2 (énfasis, íconos, recortes de verdad) + concat sin re-encode

Rama `f2-gfx-director` (base `0cc1997`). `main` intacta. Decisiones: `DECISIONES_F2b.md`.
Este reporte se completa sección por sección; los números finales (recortes, densidad, tiempos, PSNR, Gemini) van al cierre, después del render completo.

## §1 — Correcciones al director (v1 → v1.5)

- 1.1 Titular determinista: el LLM elige solo `fact_idx` + `scene_idx`; `build_headline` arma ≤ 8 palabras literales (la cláusula con la cifra, si la hay) y `build_kicker` pone fuente o año.
- 1.2 Zoom guiado por narración: el LLM marca la frase ancla (`anchor_word_idx` + `anchor_len`, dentro de la escena). Visión busca **esa** frase. Sin box o con confianza < 0.7 → sin zoom.
- 1.3 `chapter_question` OFF en el perfil. **Deuda de guion:** reactivarla cuando m01b emita `cliffhanger` por cap.
- 1.4 Densidad: máximo 18 s sin bloque (antes 35).
- 1.5 Router: visión solo sobre imágenes con persona en el prompt (40/81 en Orleans; 29 sin veredicto previo).
- 1.6 Grano 0, viñeta 0.15 (revierte D21).
- Candado sin `--gfx`: md5 de ch02 `--only-cap` = `38e5ba14e3d24fd20f9297c9e1dfee24` ✔ (log `onlycap_ch02_nogfx_s1.log`).
- Tests: 97 verdes.

### Veredicto revisor-handoff §1 (íntegro)

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1.1 | Titular determinista: el LLM manda fact_idx+scene_idx, el validador arma headline (≤8 palabras, cláusula con cifra) y kicker (fuente/año) | OK | gfx_director.py build_headline/build_kicker (~l.326-400); validate_plan l.485-489 ignora headline/kicker del LLM; schema archive_clippings solo pide fact_idx/scene_idx (l.244). Probado a mano: "Partes de Nueva Orleans quedaron bajo 15 pies". Test test_titular_lo_arma_el_validador |
| 1.1b | Objetivo 1–2 recortes por cap | NO VERIFICABLE | Hace falta el render de ch02/Orleans (cues/reporte). Es criterio de resultado, no de código |
| 1.2 | Zoom guiado por frase ancla; box de visión o null; sin box → sin zoom; umbral de confianza explícito | OK | zoom_anchor, _ZOOM_SYSTEM/judge_zoom_box(image, anchor), apply_zoom_vision (conf < zoom_conf_min=0.7 → sin zoom); gfx_config.py:225, misterio.json; test_zoom_sin_ancla_en_su_escena_no_va |
| 1.3 | chapter_question OFF por default en el perfil, el código queda | OK | misterio.json enabled=false; max_per_cap('chapter_question')=0 (corrido); _QUESTION_RULE condicional; la deuda "m01b cliffhanger" está en B8 (falta mencionarla en el reporte final, pendiente) |
| 1.4 | Intervalo máximo 18 s (antes 35); relleno: énfasis de palabra, callout de fact, punch_in | PARCIAL | interrupt_max_sec=18 (corrido: 18.0) y min 12. El orden de relleno queda callout→punch_in; el énfasis de palabra depende de §2, que aún no existe (B9 lo declara; sin tests nuevos de densidad) |
| 1.5 | Visión para retratos solo sobre imágenes con persona/rostro/retrato/manos/cuerpo; alimenta router (high si retrato) | OK | depth_probe.portrait_candidates (l.~193-210) + fase2b.py:2093-2119 (solo candidatos sin veredicto previo, cacheado en zoom_verdicts.json); alto = cara_closeup sin cambios; test en test_module_gfx_router.py (+10 líneas) |
| 1.6 | Grano 0, viñeta 0.15, quitar desviación D21 | OK | misterio.json grain 0.0 / vignette 0.15; gfx_rules cargado: 0.0/0.15 (corrido); gfx_layer.py:260 no genera textura si grain=0; B11 anota la reversión de D21. El default en código (gfx_config.py:282) sigue en 0.15, lo pisa el perfil |
| 6a | Tests verdes | OK | pytest gfx_* + reassemble + hwencode: 97 passed in 14.61s |
| 6b | Lock literal | OK | Headline se re-chequea con _literal_in (build_headline devuelve "" si no es literal) y sigue pasando por script_engine.gfx_literal_lock en gfx_layer.py. El ancla del zoom son palabras literales de la voz |
| 6c | Ningún texto/ícono inventado por el LLM | OK | El LLM ya no escribe headline/kicker; solo índices. Íconos no existen aún (§3) |
| 6d | Sin --gfx segmentos byte-idénticos | NO VERIFICABLE | Depende del md5 del render en curso que corre CC. Por diff: fase2b.py solo cambia _route_safe (ruta con gfx), así que no hay riesgo estático evidente |

Fuera de alcance: ninguno. Hay 12 archivos tocados, todos los declarados (diag_234_cap4.py excluido por indicación); lab/hyperframes/f2b/ existe y no está vacío (DECISIONES_F2b.md y un .log). Sin commits.

Riesgos que el contrato no cubre: (1) fase2b.py:2112 envuelve la visión nueva en un except genérico, así que una falla de Gemini se degrada en silencio a veredictos cacheados (queda un print). (2) El zoom ahora depende de que el LLM acierte anchor_word_idx dentro de ±1 s de la escena. Si falla más seguido de lo esperado, el zoom desaparece (conservador, pero baja la densidad). (3) El filtro de retratos usa regex en inglés/español sobre el prompt. Términos como "figure" o "silhouette" pueden disparar llamadas de visión de más (29 en Orleans, según B10), con costo de Gemini acotado.
```

Respuesta de CC a las observaciones: 1.4 se completa en §2 (el énfasis de palabra entra primero en el orden de relleno). 6d verificado después del veredicto: md5 `38e5ba14…` ✔.
