# HANDOFF F73 — miniaturas con foto madre y sello de narración; chascada: QA muestra toda la voz de cada foto

Modelo CC: Opus medium. Correr DESPUÉS de que termine F72 (no en paralelo con run_pipeline). Usar subagentes en paralelo donde se pueda (tests, lecturas).
Topic de prueba: 123bbb64-9fca-4395-8bf4-57d60e219ef1 (Wittenoom), rama f11-guion-v4.

## Por qué
- Las miniaturas no pasan por lo nuevo: paquetes 02/03 del 30-oct (Seedream, narración sin aprobar); paquete 01 rehecho el 1-nov con nb2_lite pero `referencias_md5: []` → la cara no es Daniel. El ancla del paquete 01 («Ese pie va a cerrar…») ya no existe en la narración aprobada.
- Causa 1: `m09_packaging.foto_paquete` llama `am._generate_image_raw(prompt, out, use_ultra=False)` sin madres.
- Causa 2: `metadata.json` no guarda de qué narración salieron los paquetes (abierto de F67c: «el empaquetado del 30-oct sigue reusable»).
- Chascada: el QA muestra debajo de cada foto solo `narration_anchor`; las oraciones sin foto propia suenan encima de la anterior y no se ven. Medido (analista): ch01 86 %, ch03 76 % (7 oraciones), ch06 95 %, ch07 86 %; ch02/04/05 100 %.

## Constantes
Ninguna nueva. Tope 2 madres = el de `_madres_para_item` (F60 B). `N_PAQUETES` = el que ya existe en m09.

## Módulos
| Módulo | Hoy | Después |
|---|---|---|
| `script_engine/m09_packaging.py` | foto del paquete sin madres; paquetes sin sello | A: madres con la regla única; B: sello `narracion_md5` |
| `script_engine/m09_review_server.py` | sirve lo que haya | B: si el sello no coincide, avisa y no muestra paquetes viejos como vigentes |
| `qa_studio_server.py` + `qa_studio.html` | debajo de la foto, solo el ancla | C: el ancla + toda la voz de esa foto |

## A — madres en la foto del paquete
1. `_foto_del_paquete` / `foto_paquete` eligen madres con `am._madres_para_item(item.persona, refs de item.foto_madre_ref, item.anio, script.foto_madre_registry, script.foto_madre_personas, item.prompt)` — los mismos argumentos que `qa_studio_server._madres_de_entrada` (guion vivo `data/scripts/<tid>.json`). Pasarlas como `foto_madre_data_uris` (`am._path_to_data_uri`). Sin madres → igual que hoy (t2i).
2. Guardar en el paquete `foto_madre_refs` (las que anclaron) y en `paquete_NN_base.llamada.json` que salga `referencias_md5` lleno cuando hay persona.
3. Borrar la llamada vieja sin madres (no dejar dos caminos). `rehacer_foto` pasa por lo mismo.

## B — sello de narración
1. `run_candidates` escribe `metadata.json.narracion_md5` = `aprobado.md5` de `01b_narracion_v3.json` (`fase1_5.estado_narracion`). Narración no aprobada → no genera paquetes (mensaje claro).
2. Si `metadata.narracion_md5` falta o ≠ el aprobado vigente: mover `thumb_candidates/` y los `paquetes` de metadata a `publish/_desfasado_<ts>/` (como `_archivar_fondos_desfasados`) y generar de cero. Igual al abrir el review server (`serve`) y en el paso `packaging` de run_pipeline.
3. Prueba real en Wittenoom: hoy no hay sello → se archivan los 3 viejos y salen 3 nuevos.

## C (chascada) — toda la voz debajo de cada foto en QA
1. Cada segmento lleva `voz`: el texto de la narración del cap desde el ancla de esa foto hasta el ancla siguiente (el último, hasta el final; el clip cubre lo que hay antes de la primera supp si va primero, o desde su ancla si va al final). Del texto original del guion, no de los tiempos. Si un ancla no se encuentra en el texto → `voz` = solo el ancla (nunca inventar).
2. `qa_studio.html`: debajo del ancla, el resto de `voz` en gris. Sin tocar tiempos, anclas ni el video.
3. Check en texto: por cap, palabras de la narración vs suma de `voz` = 100 % en los 7 caps de Wittenoom (pegar la tabla).

## D (chascada, decidida por Omar 2026-11-03 21:05) — el chequeo «inicio de música por cap» no cae en el silencio de las citas
Por qué: F72b C probó que `fase2b._medir_inicio_musica` (fase2b.py:3090-3099) elige el `argmax` dentro de tramos en ceros (silencio de cita de testigo, music_intensity.py:113-121): norma = 1e-9 y el ruido de la FFT en float32 da puntajes de 10³. En el guion F72b marca ✗ falsos en ch03 (+6,72 s), ch04 (−18,76 s) y ch07 (+15,21 s).
Constantes: ninguna nueva. Reemplaza el «+1e-9 como única guarda» por dos cosas sin número: (1) la correlación y la norma en float64; (2) solo son candidatas las posiciones cuya ventana tiene al menos una muestra ≠ 0 (conteo exacto con cumsum de enteros). Se borra la guarda vieja, no se deja apagada.
Módulo: `fase2b.py` (`_medir_inicio_musica`) — hoy elige en silencio digital; después nunca.
1. ANTES de cambiar: simulación en texto sobre el `_fase2b_work/_preview_music_ducked.wav` y las piezas actuales de Wittenoom (si una pieza ya no está, usar la aproximación de F72b C y decirlo): tabla cap · desvío hoy · desvío con el cambio. Esperado: ch03/ch04/ch07 ≈ 0; ch01/02/05/06 sin cambio. Si cambia otro cap, PARADA. (El analista no lo simuló: no tiene las piezas.)
2. Después del cambio: la misma tabla corriendo la función real, SOLO LECTURA sobre los archivos de hoy. NO correr `--plan-only` (el guion está aprobado y el render hecho; re-planear rompe la aprobación).
3. Test sin red en `test_module_f73.py`: pista sintética con un tramo en ceros dentro de la ventana de búsqueda → el inicio medido es el real.

## Salida en texto (cada etapa)
- A: tabla de los 3 paquetes nuevos: n · ancla · persona · foto_madre_refs · endpoint · referencias_md5. Las 3 miniaturas compuestas en el reporte.
- B: antes/después de `metadata.json` (sello), ruta del `_desfasado_*`.
- C: tabla de cobertura por cap + ejemplo de ch03 con las 7 oraciones que antes no se veían.
- D: las dos tablas de desvío (simulación y función real).

## Reglas fijas
- No tocar prompts de paquetes (`pedir_paquetes`) ni de fotos; no tocar fondos, GUION_PANTALLA ni render (D solo cambia la función de medida, sin re-planear); no `main`.
- Tests nuevos `test_module_f73.py` sin red; suite amplia como en F71b; veredicto del revisor-handoff íntegro.
- Costo se reporta después (no hay tope).
- PARADA al final: reporte `lab/hyperframes/f73/F73_REPORT.md`, ESTADO_SESION al día, commit.
