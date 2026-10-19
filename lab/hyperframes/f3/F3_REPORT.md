# F3_REPORT — Laboratorio de identidad

Rama `f3-lab-identidad` (desde `31c671c`). `main` intacta en `43f528a`. F2b NO se mergea todavía (decisión de Omar).
Decisiones: `DECISIONES_F3.md`. Veredictos del revisor-handoff pegados íntegros por sección.

---

## §A — Servidor + historia + preview

**Qué hay:**
- `gfx_lab_server.py`: servidor en http://localhost:8765 (`http.server`, sin dependencias nuevas). Sirve la página, la narración de ch02 (con Range), las fotos (con miniaturas) y las palabras de Whisper ya remapeadas (las mismas que los subs). El preview sale del plan vía `gfx_project.write_project`, o sea con las plantillas reales. El `<hyperframes-player>` y el runtime son los del paquete pineado, inyectados igual que en `hyperframes play`.
- `lab/identidad/index.html`, `lab.js`, `lab.css`: tres columnas. **Historia** muestra las palabras (clic = ir a ese momento; subrayado = ahí pasa algo; se resalta la que suena) y la tira de 15 fotos con su rango. **Escena** tiene el player con play/pausa, scrub y los bloques activos en este momento. **Catálogo** es por ahora la lista de lo que hay en el cap, en español con el nombre técnico en gris; las pestañas llegan en §B. En la barra: Preview y Volver al plan del director. Render, Guardar y Resumen quedan deshabilitados hasta §C/§D.
- Arranca con el plan del director de ch02 (`gfx_plan_ch02.resolved.json`).

**Medido:**
- Las 15 `compositions/scene_NN.html` del preview son idénticas byte a byte a las del último render de ch02.
- Preview repetido: 22–25 ms en el servidor y ~1.0 s ida y vuelta con la recarga del player, conservando el instante (antes 2.0 s; ver C7).
- Sincronía audio↔escena: 16 ms de deriva a los 6 s, con play por clic real en el navegador.
- Candado sin `--gfx`: md5 de ch02 `--only-cap` = `38e5ba14e3d24fd20f9297c9e1dfee24` ✔ (`onlycap_ch02_nogfx_A.log`).
- Tests: 172 verdes (155 + 17 nuevos en `test_module_gfx_lab.py`).

**Veredicto revisor-handoff (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito (§A, §1, §5.1, §6, pedido de hoy) | Estado | Evidencia |
|---|---|---|---|
| 1 | Servidor local sirve lab/identidad, historia, audio, plan | OK | gfx_lab_server.py existe (17.9 KB). curl: /api/story 200 (14.7 KB, palabras Whisper con start/end, audio_url), /api/plan 200, /composition/index.html 200, /player.js 200, /runtime.js 200 |
| 2 | Audio con soporte Range | OK | GET /media/audio con Range bytes=0-99 devuelve 206 y 100 bytes |
| 3 | POST /preview con plan genera el HTML del iframe | OK | Devuelve {"src":"/composition/index.html?v=7","ms":31,"cues":[...]}. El servidor llama a gfx_project.write_project (gfx_lab_server.py:207-210) |
| 4 | Preview usa las plantillas reales, no una copia (§5.1, §6) | OK | `diff -r` de gfx_lab_ch02/compositions contra gfx_ch02/compositions: idénticas. Solo difiere index.html: el render viejo tenía el contador "6,500" (#cu) y el lab muestra un callout, por el dedupe de F2b. Coincide con DECISIONES C2. gfx_templates/ sin modificar (git diff) |
| 5 | Columnas Historia (palabras + fotos con rango) y Escena (iframe), barra | PARCIAL | lab.js:61-65 y 148 (tira de fotos con rango), lab.js:110-122 (audio sigue a currentTime del player). Barra inferior: no la revisé, y la pide §1 con Render/Guardar/Resumen que son §C/§D. Falta la columna Catálogo (§B, no es de este commit) |
| 6 | Audio sincronizado por currentTime, sin render de video | OK por código | lab.js:110-122, DRIFT_MAX 80 ms. La deriva de 16 ms y el play con clic real: NO VERIFICABLE (prueba de navegador de CC que no pude repetir) |
| 7 | Regeneración del preview ~1 s conservando el instante | NO VERIFICABLE | El servidor responde en 31 ms y el memo de freezes tiene test (test_module_gfx_lab.py:61). El ~1.0 s ida y vuelta con el instante conservado no lo pude medir |
| 8 | Candado: sin --gfx, byte-idéntico | OK | onlycap_ch02_nogfx_A.log (39 líneas) termina en md5 38e5ba14e3d24fd20f9297c9e1dfee24 y no tiene ninguna mención a gfx. Pero no re-corrí la corrida, solo leí el log |
| 9 | Candado: tests verdes | OK | Corrí la lista indicada: 172 passed (antes 155, +17 de test_module_gfx_lab.py) |
| 10 | Candado: main intacta | OK | `git rev-parse main` = 43f528a77a2e... |
| 11 | Rama f3-lab-identidad desde 31c671c | OK | `git branch --show-current` = f3-lab-identidad. `merge-base --is-ancestor 31c671c HEAD` = ok |
| 12 | Handoff copiado en lab/hyperframes/f3/ con el mismo nombre | OK | HANDOFF_F3_laboratorio_identidad.md, 18984 bytes |
| 13 | ESTADO_SESION actualizado (arranque F3 + no mergear F2b) | OK | lab/ESTADO_SESION.md:6-16 (rama, main=43f528a, F3, md5, decisiones C1–C11). El archivo estaba sin trackear: entra al commit como nuevo, entero |
| 14 | DECISIONES_F3.md con decisiones conservadoras | OK | Existe (3.9 KB), C0–C11 |
| 15 | Lock literal (texto de pantalla de narración/facts) | NO VERIFICABLE | §A no agrega textos nuevos. Los cues vienen de gfx_plan_ch02.resolved.json ya resuelto, que no auditó nadie en este paso |
| 16 | Sin shaders | NO VERIFICABLE | No hice grep de shaders |

Fuera de alcance: diag_234_cap4.py figura modificado en el working tree (1 línea), pero no es de F3. Hay que excluirlo del commit con `git add` selectivo. Lo demás sin trackear son archivos previos a F3 (_lab_*.py, QA_*.md, etc.) y tampoco deben entrar.
Del alcance declarado, trackeado solo cambió script_engine/gfx_project.py (+16/-3, memo de `_extract_freeze`), que es el cambio esperado. lab/ESTADO_SESION.md y los archivos nuevos son los declarados. No encontré archivos de más.

Riesgos que el contrato no cubre:
- El memo de `_extract_freeze` es un cambio en código compartido con el render real. Es por proceso y con clave (base, mtime, tamaño, t, salida), así que en teoría fase2b no cambia. El md5 sin --gfx no lo cubre porque ese camino no pasa por gfx_project.
- El runtime y el player se sirven con 127.0.0.1:8765 y un `<audio>` propio, no por `audio-src` del player. Por eso el sonido depende de que el navegador permita el autoplay tras un clic.
- Los subtítulos karaoke no aparecen en el preview (C8), así que el lab no es del todo "igual al mp4" en eso.
```

**Respuesta de CC a las observaciones:**
- #5: la barra existe (`index.html`, `<footer class="bar">`) con los 5 botones. Render, Guardar y Resumen están deshabilitados con el aviso "Llega en §C/§D". El Catálogo es §B.
- #16: verificado después del veredicto, `grep -niE "shader|webgl|getContext("` sobre el lab no da nada.
- Riesgo 1 (memo): en una corrida de fase2b cada cap tiene su propio `base.mp4`, así que la clave nunca se repite entre caps, y `write_project` se llama una sola vez por cap. Es el mismo comportamiento que antes. Igual queda como deuda re-medir un render ch02 `--gfx` contra el anterior cuando se haga el Render de §D.
- Riesgo 3: aceptado y anotado en C8 (los subs los quema fase2b después de HyperFrames).

---

## §B — Catálogo + hints + sugerencias

**Qué hay:**
- `lab/identidad/catalogo.json` cubre las 36 piezas del §2 A–J más 7 de soporte (43 entradas, 5 pestañas). Cada una trae nombre en español, qué hace, hint de 3 líneas (cuándo · dónde · por qué), estado, preset sugerido y atributos. Cada atributo dice si se ve **en vivo** en el preview (token del perfil o campo de la pieza) o si queda **anotado** (etiqueta violeta) para §D, el director o el pipeline (C12).
- `lab/identidad/sugerencias_ch02.json`: borrador de CC con 18 colocaciones para que el analista lo corrija (§5.3). Aparecen en gris punteado en la Historia y en la pestaña "Sugerencias IA", cada una con su "Probar sugerencia".
- `lab/identidad/anim_previews.css`: miniaturas de 17 animaciones que se mueven al pasar el mouse.
- Panel **Aquí**: clic en una palabra o una foto muestra lo que hay en ese momento (con lado, duración, sello e ícono editables, y Quitar) y lo que más podría ir: golpe de zoom, mood o ícono si la palabra es del léxico, o un recorte con un fact elegible.
- Servidor: tokens en vivo (override temporal de `gfx_rules`), candado literal en cada preview (salvo la pregunta manual de Omar), `/api/context` y `/api/profile`.

**Medido:** S06, S07, S04, S02 y S16 se aplicaron en el navegador sin rechazos del candado; el ícono gota se ve a 89.6 s; la miniatura "cascada" corre `ap-rise` en hover. Tests: 180 verdes (+8 de §B). En §B no se tocó `fase2b.py` ni `script_engine/` (el md5 de §A sigue valiendo).

**Veredicto revisor-handoff (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito (§B / §1–§3 / §5.1 / §6) | Estado | Evidencia |
|---|---|---|---|
| 1 | catalogo.json con 5 pestañas (Foto, Momento, Entre fotos, Cierre, Global) | OK | lab/identidad/catalogo.json: `tabs` tiene los 5 ids. 43 elementos: foto 13, momento 13, entre 8, global 6, cierre 3. |
| 2 | Cada elemento lleva nombre, que_hace, hint de 3 partes (cuándo/dónde/por qué), estado y preset_sugerido | OK | Script sobre `elementos`: los 43 tienen nombre, que_hace y hint con las 3 claves llenas. |
| 3 | Catálogo completo A–J | OK | Aparecen los ids de §2: ken_burns, pan, depthflow, veo, punch_in, hold, look, texto, recorte, íconos, transiciones, sfx, cierre y global. Estilos de recorte (post-it, ficha, telegrama) y entradas de ícono (ink_bleed, press_wipe) presentes. |
| 4 | Atributos como controles; paleta ≤ 4; texto libre solo en la pregunta de cierre | OK | Paleta: tint, paleta.acento y count_up.color, ninguna pasa de 4 opciones. El único atributo `texto` es `chapter_question` (catalogo.json). lab.js:475-476 y 132 marcan `manual:true`. |
| 5 | Miniaturas CSS que se mueven en hover | OK | anim_previews.css:2,13,19 (17 `@keyframes`, `.ap-wrap:hover`). El test `test_miniaturas_css_existen_para_cada_animacion` pasa. Que ap-rise corra en hover es una prueba de navegador de CC, no la repetí. |
| 6 | Botón "Probar sugerencia" aplica el preset en el lugar recomendado | OK | lab.js:244 (`applyPreset`), 415-422, 468. Es un botón por elemento y otro por sugerencia. |
| 7 | sugerencias_ch02.json con 15–20 colocaciones, en gris "sugerido" | OK | 18 entradas, marcadas BORRADOR de CC (§5.3). Todas apuntan a ids existentes. Insignia "sugerido" en lab.js:466 y clase `.sug` en lab.js:293. |
| 8 | Español sin jerga, técnico en gris | OK | Hay `<span class="tech">` y hints en español (lab.js:475). No revisé visualmente toda la UI. |
| 9 | Estados "anotado/nuevo_D/futuro" declarados con honestidad | OK | DECISIONES_F3.md C12-C21. El catálogo tiene un campo `estado` (en_vivo 9, parcial 12, pipeline 11, nuevo_D 10, futuro 1) y 47 atributos con `aplica:"anotado"`. Es honesto. |
| 10 | Candado literal, sin shaders, preview con plantillas reales | OK | Los tests `test_preview_usa_las_plantillas_reales` y `test_candado_en_el_preview` están en el set que pasa. No hay "shader" en lab.js. |
| 11 | Tests verdes | OK | Corrí el comando indicado: 180 passed en 14.93 s. |
| 12 | Sin --gfx intacto (fase2b.py y script_engine/ sin tocar) | OK | `git diff --stat` sobre fase2b.py y script_engine/ no da cambios; su último commit toca esa ruta antes de F3 (0902908). No re-ejecuté el md5 de §A; el log existe (38e5ba14...). |
| 13 | Entregables existen, no vacíos | OK | catalogo.json 42 KB, sugerencias_ch02.json 5.9 KB, anim_previews.css 5.2 KB. |
| 14 | `ejemplo_en_ch02` por elemento (§3) | PARCIAL | Solo 6 de 43 elementos lo tienen (punch_in, keyword_emphasis, data_callout, archive_clipping, icon_callout, chapter_question). El resto se cubre con `sugerencias_ch02.json`, pero el campo del esquema §3 casi no se usa. |
| 15 | Atributos y preset en todos los elementos | PARCIAL | 9 elementos tienen 0 atributos (hold, icon_array, regen_icon, cut, zoom_through, ink_wipe, burn, match_cut, next_chapter_card). 7 de ellos no tienen `preset_sugerido`: icon_array, regen_icon, zoom_through, ink_wipe, burn, match_cut y next_chapter_card. Los nuevos, de §D o futuros, son esperables. El handoff define atributos para zoom_through, ink_wipe, burn, next_chapter_card e icon_array, y no están. `cut` y `hold` sí cubren el "—" del handoff. |

Fuera de alcance: ninguno. Los 6 modificados y los 3 nuevos coinciden con lo declarado. diag_234_cap4.py ya estaba modificado antes. No vi cambios de este paso en fase2b.py ni en script_engine/.

Riesgos que el contrato no cubre:
- Los hints de las 43 entradas y las 18 sugerencias son un borrador de CC que el analista no ha validado todavía.
- Los 47 atributos "anotado" no se ven en el mp4. Omar puede creer que un ajuste se aplicó, y la etiqueta violeta es lo único que lo avisa.
- No pude repetir la prueba de navegador (hover, aplicar S06/S07/S04/S02/S16 sin rechazos del candado, ícono a 89.6 s). Es evidencia de CC y no la verifiqué.
```

**Respuesta de CC a las observaciones:**
- #15: después del veredicto se agregaron como atributos "anotado" los que el handoff sí define: barrido de tinta (duración 0.6 s), quemado (borde) y tarjeta "Capítulo N" (1.5 s). zoom_through y la matriz no tienen opciones en el handoff ("—" / "N figuras en filas de 10"). La matriz existe y la arma el director; ch02 no tiene un fact elegible para ella.
- #14: `ejemplo_en_ch02` está solo donde existe un lugar concreto en ch02 (6 elementos). Las colocaciones van en `sugerencias_ch02.json`, que es lo que §3 pide para ch02. No se inventan ejemplos para piezas que ch02 no tiene (citas, tercio inferior, matriz).
- Riesgo 2: además de la etiqueta violeta por atributo, cada tarjeta lleva un badge de estado y una nota ("Parte se ve en el preview; el resto queda anotado"). Va como pregunta para la PARADA.
