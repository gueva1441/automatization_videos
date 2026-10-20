# RESUMEN F4c — Doctrina del director + marca sin pixelado

Rama `f3-lab-identidad`. `main` intacta (`43f528a`). Sin render completo: solo `--only-cap ch02` y `ch05`.

## A — Las reglas del análisis (R1–R8; la R9 saltada por pedido de Omar)

| Regla | Qué hace ahora | Dónde |
|---|---|---|
| R1 | Cargas: Flash propone hasta 10; quedan las 5 de **más peso** (empate: la más rara del video). Peso 1 nunca es carga. El léxico manda sobre las palabras que ya conoce (Flash ya no infla «agua» a 2). | `gfx_intensity.py` |
| R2 | Prompt: lo que se puede oler, tocar o ver > las palabras-resumen, con 5 pares de ejemplo. El cache se invalida por versión del prompt. | `gfx_intensity.py` |
| R3 | El pico lleva su palabra más fuerte (sello + mood + ícono) encima del bloque grande; la limpieza de ±5 s no la saca. | `gfx_peak.py` |
| R4 | Ícono por categoría con peso ≥ 2 (el de la palabra si existe; si no, el de la categoría). Peso 1 no dispara sello. «agua» sola nunca lleva gota. | `gfx_director.py`, `gfx_fragments.py` |
| R5 | Las 5 categorías de reserva quedan activas con capa mínima (desaturación + viñeta) y un SFX propio cada una (brasa, rumor, zumbido, viento, vacío). | perfil, `gfx_project.py`, `make_sfx.py` |
| R6 | El recorte es un documento: sale solo del fact, tiene que sumar algo que la voz no dice, y el kicker es obligatorio (fuente → año → fecha → año del cap). Si no hay opción que cumpla, el recorte no sale. | `gfx_fragments.py` |
| R7 | Si la voz dice el dato literal en ese tramo, el dato no sale. Una cifra en dígitos que la voz dice en letras se queda. | `gfx_fragments.py` |
| R8 | Pregunta de cierre: Flash propone 3, un filtro duro descarta las que no sirven (nombres nuevos, términos administrativos, nada conocido) y un segundo paso elige la que más engancha. La pregunta manual de Omar nunca se pisa. | `gfx_question.py` |

Tabla completa por bloque: `TABLA_antes_despues.md`. En corto:

- **ch02** (9 → 7 bloques). Salen AGUA, OSCURO (peso 1) y el dato «Prisión Parroquial de Orleans» (la voz lo dice). Entran ENGULLIDA y PUTREFACTA (veneno + ícono) como sellos. Los recortes ya no repiten la voz: «tierra el 29 de agosto» · 2005 y «prisioneros quedaron atrapados durante días en celdas inundadas» · 2005. La pregunta de Omar queda igual.
- **ch05** (10 → 9 bloques). Salen LÍQUIDA y FLOTANDO, y los datos «Human Rights Watch» y «Templeman III» (la voz los dice). Entran DESVANECIDAS y DESAPARECIDOS (silencio, capa mínima + SFX «vacío») y DISOLVIÓ. CADÁVERES queda como palabra del pico. La pregunta pasa de «¿Cómo obtuvieron Waganfeald y Kunkel su indemnización?» a **«¿Quién abandonó a los desaparecidos?»**.
- Candado literal: 0 rechazos en los dos caps. Sin `--gfx`, el md5 de ch02 sigue en `38e5ba14…` (`corrida/onlycap_ch02_nogfx_f4c.log`). Tests: 305 verdes.

**Lo que no salió como en la simulación del análisis (§4):**
1. **El pico se movió.** Con el prompt nuevo, Flash puso otras intensidades. En ch02, la frase del agua quedó a 0.15 del máximo y la tolerancia es 0.1, así que el pico ya no es el nivel de agua 4.6 m + PUTREFACTA: ahora es «encierro» + zoom. PUTREFACTA igual sale, a 0:38.9. En ch05 el pico es «cadáveres» y no «pútrida». La intensidad queda en caché: una corrida nueva da lo mismo hasta que se borre (G23).
2. **Los recortes cumplen las reglas, pero Flash elige opciones flojas** («tierra el 29 de agosto»; ch02 perdió «aguas residuales»; ch05 se quedó con «Reclusos de la sección 'Templeman III' informaron»). Hicieron falta 3 corridas para cerrar dos fallas reales (kicker repetido, recorte rechazado por el candado; G20–G21). Arreglo propuesto, sin hacer: que Flash elija solo entre las 3–4 opciones que más suman (G22).
3. Toqué el léxico de Omar: `caos`, `nadie` y `nunca` bajaron a peso 1 para que, con las reservas activas, no salgan sellos de muletillas (G9; reversible).
4. Encontré un bug viejo: `_DATE_RE` de `gfx_fragments.py` tenía un byte 0x08 en lugar de `\b`, así que nunca reconocía fechas. Lo corregí (G16). Hay el mismo tipo de corrupción en `gfx_icons/__init__.py:70`; esa no la toqué (G17).

## B — Marca de la esquina

La silueta y la llama se rasterizan a 4× del alto final, con el +2 px escalado a +8 px. FFmpeg las baja con `scale=…:flags=lanczos` antes de la opacidad. El cierre no cambia.

Recortes 1:1 (200×200, sin escalar) en `capturas/`:
- `marca_ch02_antes_despues_1x1.png` y `marca_ch05_antes_despues_1x1.png`: el mismo cuadro con la marca de F4b (código de `f8b14d4`) y la de F4c, con los mismos filtros. El segmento `--only-cap` de F4b no tenía marca (en F4b se cosió solo sobre el final).
- `marca_chNN_render_f4c_1x1.png`: el cuadro real del render F4c.
- `marca_chNN_zoom3x_antes_despues_render.png`: lo mismo ampliado 3× (vecino más cercano), solo para mirar.

Resultado: antes, los bordes eran escalonados; ahora son suaves. **Pero con el +2 px la silueta queda bastante maciza y el grabado interior casi se pierde.** Si se ve así, se puede probar `corner_dilate_px: 1` en el perfil.

## Revisor (revisor-handoff), veredicto íntegro

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | R1 top-5 por peso, peso 1 fuera | OK | DECISIONES G1/G2. Tabla: ch02 propone 10 cargas con peso 2–3. |
| 2 | R2 prompt sensorial, 10 cargas, ejemplos | OK | G3. Cambia `PROMPT_VERSION` ("f4c-r2"), que entra al hash del caché. |
| 3 | R3 el pico lleva su palabra, y `clear_around` no la borra | OK | G5/G6. ch05 «cadáveres» queda como PALABRA DEL PICO. En ch02 el sello PUTREFACTA sale a 0:38.9 y el pico pasó a «encierro» (G23). |
| 4 | R4 ícono por categoría y peso ≥ 2 | OK | G7. ch02: AGUA (gota) ya no aparece. ch05: LÍQUIDA y FLOTANDO se quitan. |
| 5 | R5 reservas activas con capa mínima y SFX | OK | G8. En la tabla ch05 hay DESVANECIDAS y DESAPARECIDOS en capa `minima`. |
| 6 | R6 el recorte es un documento, con kicker | PARCIAL | Implementado (G10/G11/G21). Pero los recortes elegidos son flojos: «tierra el 29 de agosto» y, en ch05, «Reclusos de la sección 'Templeman III' informaron». Está documentado como G22 sin resolver. |
| 7 | R7 el dato no repite | OK | G13. En ch05 salen «Human Rights Watch» y «Templeman III». «1 de septiembre» queda. |
| 8 | R8 pregunta por rúbrica | OK | G14. La manual de ch02 se conserva. ch05 pasa a «¿Quién abandonó a los desaparecidos?». |
| 9 | Regla 9 no se hace | OK | No existe `DIRECTOR_TRACE` en ningún .py fuera de `lab/`. G18 lo declara. |
| 10 | Solo `--only-cap` ch02 y ch05, sin render completo | OK | Hay logs solo de ch02 y ch05, más el de ch02 sin `--gfx`. No encontré mp4 nuevos fuera de `_fase2b_work`. |
| 11 | Candado sin `--gfx` medido | OK | `lab/hyperframes/f4c/corrida/onlycap_ch02_nogfx_f4c.log:40` tiene md5 38e5ba14e3d24fd20f9297c9e1dfee24. |
| 12 | `main` intacta | OK | `git log main -1` da 43f528a. |
| 13 | Tabla antes/después refleja los planes reales | OK | Spot-check contra los `resolved.json`. `_bak_f4c_pre` ch02 tiene dato «Prisión Parroquial» a 43.419 y water_level a 33.7 «sumergidos». ch05 tiene HRW, 1 de septiembre, Templeman III y archive_clippings «cuerpos». El plan actual ch02 tiene evidence_zoom «encierro» a 79.8 y ch05 tiene emphasis «cadáveres» a 71.08. Coincide con la tabla. No comparé cada fila. |
| 14 | B: 4× + lanzcos, +2 px | OK | G19 y `gfx_bug.py` modificado. Los tests de `test_module_gfx_bug.py` pasan. |
| 15 | Recortes 1:1 en `capturas/` | OK | Los `*_1x1.png` miden 200×200 (el par antes/después mide 410×200), sin escalar. Los `zoom3x` están aparte y con nombre explícito. |
| 16 | Tests | OK | Corrí la suite pedida: 305 passed. |
| 17 | Desvíos documentados | OK | G9, G15, G16, G20–G23 en `DECISIONES_F4c.md`. |

Observaciones:
1. ch02 pierde el nivel de agua 4.6 m y el dato «Prisión Parroquial». Pasa porque el pico se movió por variación del LLM (G23). El «con doctrina» del análisis §4 esperaba nivel de agua + PUTREFACTA en el pico. Omar debe saber que el resultado no reproduce la simulación del análisis.
2. La calidad de los recortes (R6) queda sin resolver. Hay un arreglo propuesto en G22 y no se hizo.
3. Bajé a peso 1 `caos`, `nadie` y `nunca` en el léxico (G9). Es un cambio de perfil fuera del §3, pero está documentado y es reversible.
4. G17 es un bug viejo, el mismo tipo de corrupción 0x08 en `gfx_icons/__init__.py:70`. Está sin tocar y reportado.
5. `git diff` muestra ~21 archivos modificados. Incluye `diag_234_cap4.py` y `gfx_profiles/lexico_propuestas.json`, que no figuran en la lista de "qué se hizo". Ya estaban modificados en el `git status` inicial, pero no pude confirmar que sean previos a F4c.

Fuera de alcance: ninguno claro. Dudosos: `diag_234_cap4.py` y `lexico_propuestas.json` (ver observación 5). Los untracked como `lab/hyperframes/AB*.mp4` y `lab/outputs/probe_orphan_mothers/` son preexistentes al trabajo.

Riesgos que el contrato no cubre: el caché de intensidad congela la variación del LLM, así que ch02 y ch05 quedan con el pico movido hasta que se borre el caché. La regla 6 puede dejar caps sin recorte. Un render completo podría mostrar otros picos.

**Sobre la observación 5:** `diag_234_cap4.py` ya estaba modificado al arrancar y no es nuestro: no se commitea. `lexico_propuestas.json` lo escribe el pipeline solo en cada corrida (`record_proposals`). Suma 4 propuestas de Flash (engullida, putrefacta, disolvió, macabras) y no promovió ninguna al perfil, porque hace falta un segundo video. Va en el commit de A.

## Archivos
- Código: `script_engine/gfx_{intensity,director,peak,fragments,question,layer,project,bug}.py`, `gfx_config.py`, `gfx_profiles/misterio.json`, `script_engine/sfx/make_sfx.py` + 5 wav.
- Evidencia: `DECISIONES_F4c.md` (G1–G23), `TABLA_antes_despues.md`, `corrida/` (3.ª corrida, la que vale), `corrida_v1/` y `corrida_v2/`, `capturas/`.
- Respaldos: `_fase2b_work/_bak_f4c_pre` (F4b), `_bak_f4c_v1`, `_bak_f4c_v2`.
