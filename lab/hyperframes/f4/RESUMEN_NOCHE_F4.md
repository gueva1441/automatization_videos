# RESUMEN NOCHE F4 — 2026-10-20 (01:30 → 03:00)

Rama `f3-lab-identidad` · `main` = `43f528a` intacta · **sin merge** (espera tu OK, §5). Detalle: `F4_REPORT.md` · decisiones: `DECISIONES_F4.md` (D1–D22).

## Cerró con commit (revisor: CUMPLE CON OBSERVACIONES en las 4)
- `4f05f66` §1: tu identidad (01:20) entra al perfil; la pregunta de cierre ahora es concreta (≤ 8 palabras, sin abstractas, con tus 3 preguntas como ejemplo). ch02 conserva la tuya, «¿Quién fue el culpable?».
- `f5c54bd` §2: el director aplica la identidad solo. Movimiento por foto, fundido cruzado por defecto con 1 corte cada 3 como mínimo, máx 4 golpes de zoom (1 por frase, lejos del pico), tu plan de ch02 como ejemplo en el prompt. **PARADA 1:** ch05 hecho desde cero, sin violaciones (`capturas/hoja_ch05_f4.png`).
- `b8e6c8e` §3: medí que HyperFrames **sí** escala el clip de video en el render (golpe 1.015 medido en ch01 Veo y ch04 3D; empuje de muerte en ch07). Lo de F3 (C64) no se sostenía. Saqué el cuadro congelado del zoom: el 3D sigue moviéndose.
- `321c489` §4: **PARADA 2:** video completo listo.
  - `output/ba6c3cac…/…_final_gfx.mp4` (712.2 s) y `AB_…_f4.mp4`.
  - 0 fallbacks, 0 errores de lint, 0 textos rechazados por el candado.
  - 6 pausas de pregunta + negro, sin saltos en las fronteras.

## No cerró / pendiente
- **§5 merge a main:** solo con tu OK. Las docs de §5 (REPO_MAP, ARCHITECTURE, DOC_MAESTRO v1.2, CLAUDE.md) van con el merge.
- **Incremental:** no medido (regla de un solo render completo).
- **Mood agua:** el fix de F3 sigue esperando tu mirada.
- **Preview del lab:** sigue con el cuadro congelado en el zoom (no pude verificar su player).

## Decisiones por defecto (las que más cambian lo que ves)
- La pregunta no la vuelve a elegir el director (`chapter_question` OFF; tu ✔ prende `question_auto`).
- El reloj sale solo con ≥ 2 horas verificadas (handoff §1.1): **en ch02 el reloj «29 AGO · 2005» que aprobaste ya no aparece**.
- Negro después de la pregunta: 1 s (se ve ~0.8 s). Sin `--hw-encode` (NVENC < 50 dB).
- Los 7 caps llegan siempre al tope de 4 golpes de zoom.

## Gasto y tiempos
- Gemini F4 ≈ **US$ 0.12** (tope $2).
- Render completo: 38.3 min (concat + música 84 s). Capas: 134–518 s por cap, más lentas que F2b porque ahora casi todas las fotos se mueven sobre el PNG.

## Preguntas para vos (máx 3, con lo que ya apliqué)
1. ¿El reloj de fecha de ch02 vuelve? **Apliqué:** no sale (regla ≥ 2 horas del handoff).
2. ch06 cerró con «¿Cómo la indiferencia sepultó a esos prisioneros?», abstracta («indiferencia» no estaba en el filtro). ¿La regenero? **Apliqué:** queda, anotada como deuda.
3. ¿Mergeo `f3-lab-identidad` → `main` (F1+F2+F2b+F3+F4) y dejo `--gfx` por default? **Apliqué:** nada; espero tu OK.
