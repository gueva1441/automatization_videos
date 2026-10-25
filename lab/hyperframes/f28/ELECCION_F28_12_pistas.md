# F28 — Elección de las 12 pistas (analista · 2026-10-25)

Reglas aplicadas sobre `F28A_REPORT.md`: (1) el fade de entrada/salida NO descarta: se recorta al cargar (ver abajo); (2) «D major» con r ≥ 0.6 sobre drone cuenta como Re (la medida no separa modo en drones); La menor se acepta (relativa cercana). Descartan: melodía, tráiler o compite según Gemini; pulso > 0.35 o pulso lento > 0.4; hueco interno; tonalidad fuera de Re / La menor.

| intent (producción) | a | b | reserva |
|---|---|---|---|
| hook | hook_03 | hook_05 | hook_04 |
| setup | setup_03 | outro_03 (→ `setup_f28_b`) | — |
| rising_tension | rising_tension_04 | rising_tension_05 | — |
| shock | shock_03 | shock_04 | shock_01 |
| consequences | consequences_03 | consequences_04 | consequences_01 |
| outro | outro_01 | outro_02 | — |

`resolution` usa las de consequences. Las 12 son nota 10 de Gemini salvo consequences_04 (9); ninguna con melodía; pulso ≤ 0.15; LRA 2.1–9.7; banda de voz ≤ 0.006.

## Lo que B.1 tiene que hacer con cada pista al pasarla a producción
1. **Recorte del fade**: cortar los segundos de fade medidos (`fade in/out` de la tabla) + 0.5 s de margen; la pista queda entre 150 y 175 s. Guardar recortada.
2. **Loop**: cuando el cap es más largo que la pista, el empalme va con `acrossfade` de 3 s (no `-stream_loop` seco).
3. **Nivel**: todas están a −11…−15 LUFS; calibrar `music_volume`/`floor` por pista con el método del chat 40 al mismo objetivo que las curated (la mezcla final con música debe quedar ≤ 0.5 LU por encima de la voz sola, como hoy).
4. Nombres: `audio_library/<intent>_f28_<a|b>.mp3` + `.json` (con `origen: _paleta_f28/<id>`, plan, medidas, nota Gemini). Las curated a `audio_library/_retiradas/`.
