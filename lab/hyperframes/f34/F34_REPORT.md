# F34 — Reporte PARCIAL (cortado por límite de uso de CC)

Base `fc889c9`. Commit A `24d9dad` (reglas; detalle y salidas en `a/salida_a.txt`, simulación previa en `a/simulacion_previa.md`).
Commit B: guion de Vajont regenerado con `fase2b f8s3-vajont-f30 --plan-only --rotulista --rotulista-tope 1.50` (sin `--gfx`, sin aprobar, sin render):
`GUION_PANTALLA.md/.json` en esta carpeta; mezcla en `output/f8s3-vajont-f30/_fase2b_work/mezcla_preview.wav` (fuera de git). Log `b/plan_only.log`.
Costos B: Claude US$ 0.4633 (≤ 1) · Gemini US$ 0.2392 (≤ 0.5). Verificación A: md5 ch02 sin gfx `38e5ba14…`, rápida 58, amplia 1021 + 5 previas.

## Lo que salió (resumen por cap, lo que queda en pantalla)
- ch01: tarjeta «9 OCT 1963 · 22:39» (0:00) · sello PÁNICO · reloj 9 OCT 1963. **Sin texto** (D118 no salió).
- ch02: recorte D117 «CONSEJO SUPERIOR DE OBRAS PÚBLICAS, 1943 · Aprobó la presa con 13 de 34 representantes presentes». Sin sellos.
- ch03: agua OLA 20 m · sello AMENAZA · ficha D71 «L'UNITÀ · Diario del Partido Comunista Italiano» (esperado D49: el modelo puso D71 rank 1).
- ch04: reloj 4 NOV 1960 · ficha T39 «ROCA EN RIESGO DE DERRUMBE SOBRE ERTO · 50 millones de m³» · sello AMENAZA · agua COTA AUTORIZADA 715 m.
- ch05: sellos AMENAZA, INMINENTE · reloj 9 OCT 1963. Q50 cortado por lectura.
- ch06: sello SILENCIO · ficha D192. D128 cortado por el realizador («contador de una cifra que dice la voz»: bug, el contador del rotulista cae en `finalizar`).
- ch07: sello AMENAZA · reloj 20 FEB 1968 · ficha D245. T85 no salió.
Totales: 6 textos (esperado 9) · 4 relojes + tarjeta (= §1) · 2 aguas (= §1) · 8 sellos (= 8, pero AMENAZA ×4 en caps distintos) · 6 punches (= §1).
Chequeos: música alineada ✓ 7/7 (desvío 0 cuadros) · gancho no vacío ✓ · tarjeta ✓ · ✗ agua ch04 cruza el corte 0.5 s y «contradice» 650/700 m de la voz (falso positivo: es otra magnitud) · ✗ a_pantalla 3/5 · ✗ inicio de voz ch07 (previo).

## Lo que queda abierto (sin hacer en esta tanda)
1. **Comparación línea por línea con el agente `simulador` contra §1: NO corrida** (límite de uso). El resumen de arriba es de CC, no del simulador.
2. **Veredicto de `revisor-handoff`: NO corrido.** Este reporte no cumple CLAUDE.md hasta que se corra.
3. Bugs vistos en B: D128 lo saca `gfx_realizador.finalizar` (quita todo `count_up`, también el del rotulista); el agua de la voz de ch04 cruza el corte; `contradicciones` compara la cota con el nivel del mar; ch01 sin texto (D118 en el gancho no salió: mirar `rotulista_ch01.raw.json`); prefetch del rotulista: el tope con 7 llamadas en vuelo frenó ch01/ch02 (se rehicieron en fila).
4. Tarjeta fecha-hora: está en el plan y en el guion a 0:00; **no se dibuja** todavía (la intro es de 2.5 s y la tarjeta dura `title_dur` 3 s: decidir antes del render).
5. DECISIONES: el handoff cita líneas 14:28 y 14:36 que no existen; «unidad = oración en caps de una escena» sigue «pendiente de confirmar».
6. `sellos_clima` está solo en `gfx_profiles/misterio.json` (fuera de git): Omar lo commitea si quiere.
