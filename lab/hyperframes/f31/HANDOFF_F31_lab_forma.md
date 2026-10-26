# HANDOFF F31 — Laboratorio de forma: variantes para que Omar elija (no se decide nada)

Analista · 2026-10-26 · Para CC. Base: el commit final de F30b. Una parte; **PARADA al final**. API: 0. Banco: `f8s3-vajont-f30`, **solo `--only-cap ch06`** con los planes de v5 (bloques y transiciones en caché). **Esta tanda no cambia el video: produce variantes lado a lado y medidas. Ningún valor queda commiteado como default; cada variante vive detrás de un flag `--forma-variante X` y el default sigue siendo el de hoy.**

## 0. Qué se compara y por qué (todo lo de forma que no tiene número propio: lo elige Omar viendo)
Hoy: ficha/title card entra con wipe de máscara y sale con fundido; recorte entra a máquina de escribir y sale en seco; sello entra con stamp y sale con fundido; el sello mide ~110 px de ancho a 2560 (invisible a 360 px); nada lleva placa.

## A. Variantes (cada una = un flag; los valores de cada variante son los que se comparan, no una decisión)
1. **Entrada/salida de ficha y recorte** (misma curva para los dos):
   - `V1` como hoy (wipe / máquina de escribir; salida fundido / seco).
   - `V2` fundido simple en los dos sentidos, con la duración del fundido del title card que ya existe en la plantilla.
   - `V3` fundido + desplazamiento vertical de la altura de la raya roja del title card (`#tc-line`, 6 px → se usa su alto como unidad; sin px nuevos), ease del title card.
2. **Sello**: tamaño `S1` como hoy · `S2` el doble · `S3` el triple; cada uno con y sin placa (la placa = el `rgba(10,10,10,.35)` que ya usa `.co-text.stamp`).
3. **Reloj** (`time_ticker`): `R1` como hoy · `R2` al tamaño del kicker del title card (`tc_kicker_px`, valor existente).

## B. Salidas (sin render completo)
1. Por cada combinación que importe (V1–V3 × S1–S3 con/sin placa × R1–R2 es demasiado): **V1/V2/V3 con S2+placa y R2**, más **S1/S2/S3 con/sin placa con V2 y R2**, más **R1/R2 con V2 y S2+placa** → 3 + 6 + 2 = **11 renders de `--only-cap ch06`** (~6 min cada uno con F30 → ~66 min). Ventana de cada clip: solo los tramos con bloque ± la oración (recortar con ffmpeg), concatenados: `lab/hyperframes/f31/ch06_<variante>.mp4` de ~40 s cada uno.
2. **Hoja `VARIANTES_ch06.jpg`**: una fila por bloque de ch06, una columna por variante, cada celda = tira de 6 cuadros (entrada, mitad, salida) **a 360 px de ancho** (celular) y debajo el cuadro a 2560. Es lo que Omar mira.
3. **Medidas por bloque y variante** (reporte): contraste texto/fondo según WCAG (≥ 4.5:1 es el estándar; se mide con la luma media bajo el bloque y la del texto, no se decide); cuadros de entrada y salida reales; legible o no a 360 px (altura de x del texto en px a 360: se reporta, no se juzga).
4. Nada se commitea como default: solo los flags, los clips, la hoja y el reporte.

## Frenos
- No se toca contenido (rotulista, planes), transiciones (F30b), subtítulos, velocidad. `gfx_templates`/CSS: solo detrás de los flags de variante; el default de cada propiedad queda exactamente como está.
- Ningún valor nuevo que no sea una variante etiquetada. Firefox cerrado antes de cada render. Un commit. Sin merge, sin publicar, sin borrar. md5 ch02 sin gfx `38e5ba14…`. `lab/ESTADO_SESION.md` al final.

## Reporte `lab/hyperframes/f31/F31_REPORT.md`
Lista de flags, los 11 clips, la hoja, la tabla de medidas. Veredicto íntegro del revisor-handoff. **PARADA.** La decisión es de Omar al despertar; con ella se escribe F31b (fijar defaults).
