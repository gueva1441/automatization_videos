# RESUMEN F4b — 2026-10-20 (12:00 → 15:00)

Rama `f3-lab-identidad` · `main` = `43f528a` intacta · F4 §5 + F4b se mergean juntos con tu OK. Detalle: `F4b_REPORT.md` · decisiones: `DECISIONES_F4b.md` (E1–E42).

## Cerró con commit (revisor: CUMPLE CON OBSERVACIONES en todas)
- `1762916` §1 **director de intensidad**: Flash marca pico, intensidad y palabras de carga, siempre literales. Picos de Orleans: 7 de 7 (antes 2). El nivel de agua de ch02 se conserva.
- `f1af5de` §2 **fragmento más impactante**: Flash elige un número entre los fragmentos literales. Recortes nuevos:
  - «agua contaminada subió implacable» (ch01)
  - «Katrina desató su furia implacable» (ch02)
  - «cadáveres flotando en las aguas de la inundación» (ch05)
- `93064c8` §3 **zoom foto-primero**: visión mira cada foto antes del director y cada zoom se verifica recortando la caja. Los 7 zooms caen en un detalle real (rostros, cicatriz, candado, zapatilla); ninguno en agua o aceite.
- `93064c8` §4 **íconos gratis**: game-icons (4.239 SVG, fuera de git) + índice en español; Flash elige entre candidatos; crédito en la descripción. En Orleans no se usó ninguno (los propios alcanzaron).
- (este commit) §5: render completo de Orleans con todo lo anterior. Están `…_final_gfx.mp4` (712.2 s), `AB_…_f4b.mp4`, y cues + revisión de los 7 caps. 0 fallbacks, 0 violaciones; md5 sin `--gfx` intacto.

## No cerró / pendiente
- **§0.3 marca del canal:** el código está y apagado. Falta que elijas candidata en `tira_marca_canal.jpg`. Va en el cosido FFmpeg: se agrega re-cosiendo + re-ensamble, sin volver a renderizar HyperFrames.
- 3 picos sin bloque grande (ch01, ch06, ch07): el LLM pone el pico en la última frase del cap.
- Incremental sin medir.

## Decisiones por defecto que más cambian lo que ves
- Recorte = documento con fuente: de la narración solo entran fragmentos que comparten palabra con el fact.
- Dato: conserva todas sus cifras y nombres.
- Zoom: nombrado → de editor (rostro/manos) → textura. Siempre con recorte verificado.
- Solo palabras de carga concretas buscan ícono automático; si ninguno dibuja la palabra, sin ícono.
- No cerré Firefox (de día, la regla era del modo nocturno de F4).

## Gasto y tiempos
- Gemini F4b ≈ **US$ 0.2** (tope $3); fal (marca) ≈ US$ 0.09.
- Render completo: 69.5 min (F4: 38.3). Rehízo los 7 caps, con Firefox abierto y más escenas enteras en HyperFrames.

## Preguntas para vos (con lo que ya apliqué)
1. ¿Qué marca: 1, 2 o 3? **Apliqué:** ninguna (apagada) hasta tu elección.
2. El pico cae casi siempre en la última frase del cap (cierre de suspenso). ¿Lo dejo así o excluyo la última frase? **Apliqué:** se deja (es lo que marca el LLM).
3. ¿Mergeo F4 + F4b a `main`? **Apliqué:** nada; espero tu OK.
