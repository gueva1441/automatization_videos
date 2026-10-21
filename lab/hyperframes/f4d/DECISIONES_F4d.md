# DECISIONES F4d — Pico con preferencia, recortes por cláusula, marca +1 px, \b de los íconos

Pedido de Omar (2026-10-20), sobre F4c (`59d5893`).

## 1 · Pico
- **H1** `WATER_PEAK_TOL` 0.1 → **0.2**: la frase con cifra de altura + palabra de agua es el pico salvo que otra la supere por más de 0.2 de intensidad (empate exacto en 0.2 → gana el agua).
- **H2** Orden de bloque del pico: **nivel de agua → recorte con fuente (con kicker) → zoom de evidencia sobre un detalle humano → recorte sin kicker → sello + mood**. Antes el zoom (de cualquier detalle) iba antes que el recorte. «Recorte con fuente» = recorte que arranca a ±5 s del pico y tiene kicker (desde R6 todos los recortes lo tienen).
- **H3** «Zoom humano» = detalle de visión de tipo rostro, manos o persona, confirmado por `verify_crop` (`gfx_layer._human_box`). Sin detalles de visión en el cap se usa la caja de siempre.
- **H4 (léxico)** El léxico de veneno tenía «putrefacción» pero no «putrefacta»: que PUTREFACTA apareciera dependía de que Flash la propusiera. Se suman `putrefacta`, `putrefactas`, `putrefacto` y `putrefactos` con peso 3.
- **H5** Caché de intensidad de ch02 y ch05 borrada (respaldada en `_fase2b_work/_bak_f4d_pre/`): Flash se re-llamó.

## 2 · Recortes
- **H6** `clause_options`: las opciones del recorte son cláusulas completas del fact (o sus colas), ≤ 10 palabras. Cada una termina donde termina la cláusula: coma, punto, paréntesis, o una subordinada que arranca («mientras», «cuando», «aunque», «porque», «donde»). Así «cadáveres flotando en las aguas de la inundación» es una cláusula aunque el fact siga con «mientras eran evacuados…». Tienen que arrancar en artículo, nombre (mayúscula) o sustantivo; no en verbo, participio («inundadas», «visto»), adverbio, palabra funcional o resto de comillas. Tienen que tener sujeto: «el 29 de agosto» sola no entra. Una fecha al final puede perder «de AAAA», porque el año va al kicker. Se conservan las comillas del fact, para que pase el candado.
- **H7** Orden por aporte (`_doc_rank`): primero los elementos duros (fecha, cifra, nombre, fuente), después las palabras que no suenan en todo el cap, después la cláusula más completa. Flash elige entre las **3 mejores** (`DOC_TOP`); la de hoy solo entra si está entre ellas.
- **H8 (no se hizo: atribución falsa)** Omar pidió el kicker «Human Rights Watch» para «cadáveres flotando…» de ch05. El research (`_steps/…/00_pool_etiquetado.json`) **no** atribuye ese fact a HRW. HRW es la fuente del dato de los 500 presos; lo de Templeman III es «algunos reclusos… informaron» y el research agrega que «estas denuncias nunca fueron verificadas oficialmente». `verified_facts[8]` no tiene fuente y no nombra a HRW. Poner HRW sería inventar la procedencia de un documento, así que el kicker sigue la cadena de R6 (fuente → año → fecha → año del cap) y sale «1 de septiembre». Si Omar tiene la fuente, hay que cargarla en el research o en el fact; el kicker la toma sola.

## 3 · Marca
- **H9** `corner_dilate_px: 1` en el perfil.
- **H10 (bug encontrado)** El PNG de la esquina se cacheaba por SVG + tamaño, pero no por engrosado ni halo: cambiar `corner_dilate_px` reusaba el PNG viejo. En esta corrida se borró la caché vieja antes del cosido, y ahora el nombre lleva `esq_d<dilate>_h<halo>`.

## 4 · `\b` de los íconos
- **H11** `script_engine/gfx_icons/__init__.py:70`: la regex que agrega `pathLength="1"` a los trazos Lucide tenía `\b` y `\1` convertidos en los bytes 0x08 y 0x01, así que nunca matcheaba. Se corrigió por bytes, porque los heredocs de bash con `\b` reproducían la corrupción. Efecto: los íconos Lucide de respaldo ahora traen `pathLength` y la animación de trazo puede dibujarlos. No hay otro 0x08 en los .py del pipeline. `m09_review_server.py:337` tiene un 0x01 dentro de un `join` de JS, que es otro uso y no se tocó.
