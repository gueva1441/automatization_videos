# DECISIONES F8 — tomadas solo (modo autónomo, Omar fuera)

Formato: Dn — qué se decidió · por qué · cómo se deshace.

## §2 — Cierre de parámetros de guion

- **D1 — Rama.** `f8-imagenes-v3` desde la punta de `f7-research-v3` (`524573d`, que contiene `560dcf7` + el handoff). El handoff dice «desde 560dcf7»; la punta solo suma docs de cierre de F7.
- **D2 — «Mínimo 2 beats por cap de desarrollo (total 10–12)».** La cuenta no cierra: 1 (gancho) + 2 × 5 + 1 (cierre) = 12 como mínimo. Dejé el tope del handoff (12) → en verde la escaleta tiene **exactamente 12 beats** (1 · 2 · 2 · 2 · 2 · 2 · 1). Parámetros en `video_length.DEFAULTS`: `min_beats` 7, `max_beats` 12, `min_beats_dev_cap` 2 (`config.long_video` los pisa). Si Omar prefiere holgura (dos beats en el gancho o en el cierre), sube `max_beats` a 13–14 sin tocar código. Riesgo: más reintentos de Pro por la cuenta exacta; no se midió (§2.3: no se re-corre Orleans).
- **D3 — Amarillo.** La regla de ≥ 2 por cap no aplica en amarillo (7–8 beats no alcanzan): `gate_yellow_min_beats_dev_cap` = 1, lo pone `pool_gate_profile` en `topic["_largo"]`.
- **D4 — Última frase = cita o pregunta.** Choca con la regla 17 de la escaleta y la 8 del guionista («con tus palabras, sin repetir una cita textual»). Manda el §2 (más nuevo, de Omar): la regla 17 ahora dice que el `cierre` del último beat **describe** la frase sin copiar la cita (el chequeo duro de «no repite textual» sobre el campo `cierre` de la escaleta queda: es un plan, no la narración); la regla 8 del guionista pide cita (fragmento literal del humano o de un testigo verificado) o pregunta, nunca resumen. Al editor va como blanda (`guion_v3_reglas.closing_soft`, prompt `f8-1`), con permiso explícito de tocar la última frase sin agregar nada (puede reordenar dentro del párrafo o cortar el resumen). Cuenta como cita cualquier frase con comillas (incluye la atribución «…», dijo Reed).
- **D5 — Tests viejos.** Las escaletas de prueba de `test_module_f6b/f6c` son de 8 beats: un fixture autouse les deja `MIN_BEATS_DEV_CAP = 1` (la regla nueva se prueba en `test_module_f8.py`). No cambié ninguna aserción vieja.
