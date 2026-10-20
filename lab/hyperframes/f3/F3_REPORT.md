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


---

## §C — Casillas ✔/✖, deshacer, resumen en vivo, Guardar identidad

**Qué hay:**
- Cada tarjeta del catálogo tiene **✔ Se queda en el canal** (en piezas "futuro": **✔ Lo quiero**) y **✖ No lo quiero nunca**, con una línea opcional ("¿cuándo va?" / "¿por qué?"). Cada sugerencia tiene **✔ Acepto** (la aplica si no estaba probada) y **✖ No** (si se estaba probando, la revierte).
- Léxico: en el panel Aquí, cada palabra del léxico ofrece "nunca / casi nunca (1) / a veces (2) / siempre (3)". Si la ponés en "nunca", sale el mood de esa palabra del plan.
- **↶ ↷ / Ctrl+Z, Ctrl+Shift+Z**: deshacer y rehacer todo (200 pasos). "Volver al plan del director" conserva las casillas.
- **📄 Resumen para el analista**: panel que se actualiza solo con cada cambio. Trae las 5 secciones del §4: lo que se queda, lo que nunca, lo que falta (campo "quisiera que…" en la pestaña Global), plan dorado de ch02 y preguntas abiertas que el lab detecta solo.
- **💾 Guardar identidad** (pide confirmación) escribe tres cosas. `gfx_profiles/misterio.json` lleva tokens, fuentes, `blocks.*.enabled` por ✔/✖, pesos del léxico y la clave `identity` con marcas, anotados, sugerencias y lo que falta; antes de reemplazarlo se valida con el loader del pipeline y se respalda en `.bak_f3_*`. `gfx_profiles/misterio_golden_ch02.json` es el plan con candado tal como lo dejaste. `lab/identidad/IDENTIDAD_misterio.md` es el resumen.

**Medido:** en el navegador, S06 probar → ✖ revierte el mood de «ahogaba»; S16 ✔ sin probar aplica el acento; las marcas funcionan; «oscuro» en "nunca" saca su mood; deshacer y rehacer andan por botón y con Ctrl+Z real. El resumen en vivo trae las 5 secciones. Guardar se probó punta a punta con tests en directorios temporales: **CC no tocó el perfil real** (`git status gfx_profiles/` vacío). md5 sin `--gfx` re-medido después de tocar `gfx_config.py`: `38e5ba14…` ✔ (`onlycap_ch02_nogfx_C.log`). Tests: 187 verdes.

**Veredicto revisor-handoff (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Barra con 💾 Guardar identidad y 📄 Resumen para el analista (§1) | OK | lab/identidad/index.html: `#btn-save`, `#btn-summary`, panel `#summary` |
| 2 | ✔ se queda / ✖ va a rechazados (§1.1 p.4) | OK | lab.js: marcas `S.marks` (segundo clic desmarca), `mutate("… ✔ aceptada / ✖ rechazada")`. Marcas ✔/✖ en navegador: no repetible, quedan por tu palabra. |
| 3 | Guardar escribe misterio.json (tokens, defaults, `enabled` true/false, variantes aprobadas), golden ch02 e IDENTIDAD_misterio.md (§1.1 p.6) | OK | script_engine/gfx_identity.py:176-250: `apply_identity` + `save_identity`. Valida con `load_profile` antes de reemplazar, hace respaldo `.bak_f3_*`, escribe `misterio_golden_ch02.json` y el md. Test: `test_save_identity_escribe_los_tres_archivos_y_respalda`. |
| 4 | Ctrl+Z, rehacer y "volver al plan del director" (§1.2) | OK | lab.js: `undo()`/`redo()`, listener `ctrlKey/metaKey+z`, `mutate("volver al plan del director")` (conserva las marcas). Botones `#btn-undo`/`#btn-redo`. |
| 5 | Léxico: activar/desactivar ajusta peso en el perfil (§2 C) | OK | lab.js `setLexWeight` + `S.lexicon`; gfx_identity.py:`apply_identity` ajusta `triggers[word]`. Peso 0 quita la palabra del léxico, algo más que el rango 1–3 del contrato. Es razonable pero no está en el contrato. |
| 6 | Resumen en vivo con 5 secciones (§4) | OK | GET/POST `/summary` devuelven las 5. Secciones 1, 4 y 5 probadas en vivo con el estado real. Sección 2 (por qué) y sección 3 (campo "quisiera que…") sin ejercer con datos reales; las cubre `test_summary_tiene_las_cinco_secciones`. |
| 7 | Candados §6: lock literal, main intacta, sin --gfx byte-idéntico | OK | `cues_for` usa `self.locked(plan)`. El log `onlycap_ch02_nogfx_C.log` termina en `38e5ba14e3d24fd20f9297c9e1dfee24`. El único cambio en gfx_config.py es agregar "identity" a `_PROFILE_KEYS`. No toqué ni verifiqué la rama main; "intacta" solo lo infiero de que el diff queda dentro del alcance. |
| 8 | Tests verdes | OK | Corrí la suite indicada: 186 passed en 15 s. |
| 9 | `gfx_profiles/` sin cambios (no se apretó Guardar con el perfil real) | OK | `git status --short gfx_profiles/` vacío. Solo existen finanzas.json, icons/ y misterio.json. |
| 10 | No hacer plantillas/Render/ícono/pausa (§D) ni director (§E) | OK | El diff no toca nada de eso: solo servidor, lab, config, DECISIONES y ESTADO. |
| 11 | Pruebas de navegador (S06, S16, léxico 'oscuro', Ctrl+Z por teclado) | NO VERIFICABLE | No repetible. Faltaría una grabación o captura. |

Fuera de alcance: ninguno. `diag_234_cap4.py` ya estaba modificado antes y no es de este paso. `lab/identidad/plan_ch02_lab.json` y `lab/hyperframes/_handoff_adjuntos/HANDOFF_F1_gfx_layer.md` aparecen sin trackear; no los commitees con este paso. `lab/ESTADO_SESION.md` y DECISIONES_F3.md están en el alcance declarado.

Observaciones:
- El md se escribe en `lab/identidad/IDENTIDAD_misterio.md` (`md_dir=LAB_DIR`). El contrato no fija la ruta.
- Con tu estado actual, GET /summary muestra "Lo que se queda" y "Lo que nunca" vacíos (todavía no marcaste nada). Eso es esperable, no un fallo.
- El resumen en vivo marca como pregunta abierta "3 moods y SFX 'sin elegir'". Es la detección automática funcionando.

Riesgos que el contrato no cubre: (1) Guardar es irreversible salvo por el respaldo `.bak_f3_*`; si Omar guarda dos veces en el mismo segundo, el segundo respaldo pisa al primero. (2) Las marcas ✖ solo afectan al motor para los elementos mapeados en `ENGINE_BLOCK`/`NEVER_TOKENS`; el resto queda solo en `identity`, que el motor ignora hasta §E.
```

**Respuesta de CC a las observaciones:**
- Riesgo 1: corregido después del veredicto. Si el respaldo del mismo segundo ya existe, se agrega `_1`, `_2`… (test `test_dos_guardados_seguidos_no_pisan_el_respaldo`; ahora son 187 tests).
- Riesgo 2: es así y está a propósito (C23). El resto de las marcas lo lee el director en §E desde `identity` y el plan dorado.
- #5 (peso 0): §2 C pide "activar/desactivar"; desactivar = sacar la palabra del léxico. Por eso el 0, anotado en C23.
- #11: la PARADA es justamente que Omar lo use.

---

## PARADA ÚNICA — turno de Omar

1. El lab está corriendo: **http://localhost:8765**. Si no responde, levantalo con `PYTHONIOENCODING=utf-8 python gfx_lab_server.py` desde la raíz del repo.
2. Arranca con el plan del director de ch02. Las 18 sugerencias del borrador aparecen en gris punteado en la Historia y en la pestaña "Sugerencias IA". Nada está aprobado todavía.
3. Jugá unos 30 minutos: ▶ Play, clic en palabras o fotos, "Probar sugerencia", atributos, ✔/✖. Ctrl+Z deshace.
4. Cuando estés conforme: **💾 Guardar identidad**. Eso escribe el perfil, el plan dorado y `IDENTIDAD_misterio.md`.
5. Para saber: lo marcado "anotado" (violeta) se guarda en la identidad pero todavía no se ve en el preview ni en el mp4: llega en §D. Los subtítulos y los SFX no están en el preview porque los agrega fase2b después. 🎬 Render llega en §D.


---

## §F — UI v2: foto por foto (HANDOFF_F3b)

**Qué cambió (solo la pantalla):**
- La vista por defecto en http://localhost:8765 tiene dos columnas. A la izquierda va la foto: escena grande, ◀ Anterior / Siguiente ▶, "La voz dice aquí" con las palabras del léxico en color y clic para escuchar desde ahí, y 15 círculos de progreso (amarillo = vista, verde = todo decidido). A la derecha, las tarjetas de los objetos de esa foto. Abajo: ▶ Ver capítulo completo, 🎬 Render (llega en §D), 💾 Guardar, 📄 Resumen, ↶ ↷.
- Todas las tarjetas son iguales: nombre + momento, una línea "IA: qué — por qué", ▶ Probar, ☐ Se queda, "Otras formas" (◉ = lo que hay hoy, etiqueta violeta "IA" = la forma sugerida, borde punteado = todavía no se dibuja, llega en §D) y "más opciones" (tamaño, posición en 9 zonas, duración, ✖ Nunca).
- ① siempre es el movimiento de la foto y la última tarjeta es la salida hacia la foto siguiente (en la 15, el final del capítulo, con la pregunta de cierre antes). En el medio: título, datos, recortes, mood y sello (dos tarjetas), íconos, golpes, sugerencias pendientes y propuestas de la IA.
- "+ Agregar algo a esta foto" (Dato · Sello · Ícono · Recorte · Contador · Mood · Cita · Tercio inferior · Pregunta de cierre) propone el lugar solo: la palabra del léxico, la cifra que está literal en un dato o el dato que más se parece a lo que dice la voz.
- La vista anterior sigue entera en `?modo=experto`, sin link en la pantalla. El servidor solo suma `GET /objetos?foto=N` (movimiento real + movimiento sugerido). `gfx_project.py`, `fase2b.py` y `gfx_config.py` no se tocaron.

**Prueba de CC (§3):**
- Las 15 fotos tienen entre 3 y 6 tarjetas: 6·3·3·5·6·3·3·4·4·4·3·4·3·3·4.
- ▶ Probar con la ventana visible, fotos 1–12: cada una reprodujo exactamente su ventana con el audio siguiendo (p. ej. foto 2: 8.98 → 14.93 para la ventana 8.9–14.9; foto 8: 49.02 → 53.42 para 49.0–53.5).
- Cambiar una forma ("sello → sin sello" en la foto 4) regeneró, volvió a reproducir 25.82–30.32 solo y el sello desapareció de la composición.
- ☑ en «Mood agua sumergidos» aparece en el resumen, en "Lo que se queda" y en la sección 6 "Recorrido foto por foto".
- **No verificado en tiempo real:** ▶ Probar de las fotos 13–15 y ▶ Ver capítulo completo de 0:00 a 1:37. El panel del navegador quedó oculto (la página dibujaba a 3.5 cuadros/s y después a 0) y el player no avanzaba. La lógica sí se probó: arranca en 0.13 s con el audio y, al pausar, salta a la tarjeta de esa foto. La corrida entera queda para cuando la ventana esté a la vista, o la hace Omar en la parada.
- Capturas: `capturas/F3b_foto01.png` (foto 1: movimiento, título apagado, look, golpes, salida) y `capturas/F3b_foto15.png` (foto 15: movimiento, golpe propuesto, **pregunta de cierre**, final).
- Tests: 195 verdes (+8 de §F).

**Ojo con la sesión de Omar (22:31):** el título del capítulo está apagado y hay un golpe de zoom en «Aquel» (0.08 s). Se respetó tal cual; la foto 1 muestra "Título del capítulo (apagado)" para volver a prenderlo. Las pruebas de CC se hicieron sobre una copia: su estado se restauró desde `plan_ch02_lab.omar_2231.json`.

**Veredicto revisor-handoff (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Una foto a la vez, Anterior/Siguiente, puntos, 2 columnas + barra inferior | OK | index.html:26-59; lab_foto.css:3,30; captura F3b_foto15.png |
| 2 | Tarjetas por foto (3-6), última con pregunta de cierre, 1.ª con movimiento y última con salida | PARCIAL | Código lo arma (lab_foto.js:43-162, 312). La captura de la foto 15 muestra 4 tarjetas con pregunta. Las 3-6 en las 15 fotos las afirma CC; yo no pude contarlas: /objetos devuelve datos crudos y las tarjetas se derivan en el cliente |
| 3 | Tarjeta uniforme: "IA: qué — por qué", ▶ Probar, ☐ Se queda, Otras formas, "más opciones" (tamaño/posición/duración, ✖ Nunca) | OK | lab_foto.js:557-581; captura (formato IA correcto) |
| 4 | Botones ○/◉ de mínimo 36 px, fuente 15 px | OK | lab_foto.css:2,55 |
| 5 | "Otras formas" máx 6 | NO VERIFICABLE | No encontré un tope explícito de 6 en el código; faltaría correr la UI en cada tipo de objeto |
| 6 | ▶ Probar reproduce [t−1, fin+1] con audio; cambiar ○ regenera y reproduce solo | PARCIAL | Código: lab_foto.js:105,200,330,684 (algunas ventanas son [t−1, t+3.5] y no fin+1). La prueba en tiempo real de CC cubre fotos 1-12; yo no pude repetirla. Fotos 13-15 sin probar |
| 7 | + Agregar con la lista pedida (Dato, Sello, Ícono, Recorte, Contador, Mood, Cita, Tercio inferior, Pregunta de cierre) | OK | lab_foto.js:421-422 |
| 8 | ▶ Ver capítulo completo de 0 a 1:37 sin cortes, pausa salta a la tarjeta | NO VERIFICABLE | Botón existe (index.html:58, lab_foto.js:624-707). CC no pudo correrlo de punta a punta (panel oculto, player sin avanzar). Falta una corrida real con el navegador visible |
| 9 | ☑ aparece en el resumen; pendientes listados | PARCIAL | Cambio en gfx_identity.py y 195 tests verdes. La prueba de "Mood agua" en el resumen es de CC, no repetible por mí (no hice POST) |
| 10 | Servidor sin cambios salvo GET /objetos | PARCIAL | gfx_lab_server.py +70 líneas. Incluye /objetos (responde 200 en las 15 fotos) y suggest_movement, que el contrato no menciona explícitamente |
| 11 | Modo viejo en ?modo=experto, sin link desde la UI | OK | index.html:9 redirige a /lab/experto.html (200); no hay link visible |
| 12 | Candados: sin cambios en gfx_project.py, fase2b.py, gfx_config.py | OK | `git diff --stat 04a6025 -- <los 3>` vacío |
| 13 | Tests | OK | Los corrí: 195 passed |
| 14 | Capturas foto 1 y última en el reporte | OK | capturas/F3b_foto01.png (658 KB) y F3b_foto15.png (571 KB) existen; vi la 15, con pregunta de cierre |
| 15 | Render mp4 deshabilitado (llega en §D) | OK | index.html:59 |

Fuera de alcance:
- script_engine/gfx_identity.py: la sección 6 y las preguntas pendientes en el resumen. El contrato dice "el resumen se queda como está", pero la regla 5 exige que el resumen liste pendientes. Lo trato como tolerable y justificado, pero es una decisión que debe ver Omar.
- gfx_lab_server.py: suggest_movement va más allá de "solo GET /objetos".
- Sin commitear y no son de §F, no deben entrar: diag_234_cap4.py, lab/identidad/plan_ch02_lab.json, lab/identidad/plan_ch02_lab.omar_2231.json, lab/hyperframes/f3/_lab_server.log.
- Ninguno de los tres archivos de candado fue tocado.

Riesgos que el contrato no cubre:
- Sin prueba humana en tiempo real de ▶ Probar en las fotos 13-15 ni del capítulo completo de 0 a 1:37. Es justo lo que Omar va a hacer en la PARADA, así que ahí puede fallar.
- Las ventanas de Probar no son uniformemente [t−1, fin+1]: varias usan t+3.5.
- Los archivos de sesión de Omar (plan_ch02_lab*.json) están sin trackear y pueden colarse en el commit.
```

**Respuesta de CC a las observaciones:**
- #5: ninguna lista de formas pasa de 6 (`FORMAS` en lab_foto.js: movimiento 6, salida 6, texto 6, recorte 4, sello 3, ícono 3 + 4).
- #6 / riesgo 2: las ventanas `t+3.5` son las de moods, sellos y sugerencias, cuyo fin es t+2.5. O sea que son [t−1, fin+1], igual que las demás.
- #8 / riesgo 1: confirmado, no se pudo correr. Se declara arriba.
- #10 (`suggest_movement`): es la "IA:" de la tarjeta ① (hint del catálogo aplicado al prompt de la foto) y vive dentro de `GET /objetos`, el endpoint que permite el handoff. Anotado en C36.
- Fuera de alcance (`gfx_identity.py`): la regla 5 pide que el resumen liste los pendientes. Se agregó como sección 6 sin cambiar el resto (C38). Queda para que Omar lo vea.
- Riesgo 3: el commit se arma con `git add` por ruta; los `plan_ch02_lab*.json` y el log no entran.


---

## §F2 — Correcciones de Omar: tramo por tramo, Probar aislado, ver con todo

**Qué cambió:**
1. **Tramo, no foto.** "TRAMO N de 15" arriba y "Tramo N de 15" abajo. Si dos tramos comparten imagen, el movimiento del segundo ofrece ◉ continuar / ○ nuevo. ch02 no tiene ningún caso así.
2. **▶ Probar = ese objeto solo, sobre la foto fija** (PNG de fase1_5, quieta), en un proyecto aparte armado con las mismas plantillas. Marcás el sello → se ve solo el sello. Marcás 3D → se ve solo el clip 3D.
3. **"▶ Ver este tramo con todo"** (bajo la escena): el tramo con lo marcado "Se queda", con voz. Lo no marcado no aparece: sin ☑ en el movimiento, la foto queda quieta; sin ☑ en la salida, el cambio es corte seco.
4. **"▶ Ver capítulo completo"**: los 15 tramos con lo aprobado, seguidos.
5. **Movimiento sobre el PNG:** acercar, alejar, paneo y golpe se animan en vivo con GSAP; 3D usa el clip DepthFlow; quieta no se mueve (arreglado el bug). El templater suma `alejar` y `quieta` sin cambiar lo existente: md5 sin `--gfx` = `38e5ba14…` ✔ (`onlycap_ch02_nogfx_F2.log`).
6. **Solo formas que se ven al Probar** (lista en C47). Las salidas por tramo (corte, fundido negro, flash, fundido cruzado) ahora se ven de verdad.

**Prueba de CC:** revisé las composiciones generadas. Probar del sello: 1 tramo, foto quieta, sello, sin mood. Quieta: sin tween. Alejar: 1.08 → 1. 3D: el clip. Paneo: en x. Fundido negro entre los tramos 4 y 5. "Con todo" con sello y alejar aprobados: el mood no aprobado no aparece y el tramo 5 queda quieto con corte. El resumen lo lista. Los 15 tramos tienen entre 3 y 6 tarjetas. Tests: 200 verdes. **No vista en tiempo real** (reproducción con audio): la ventana de la app no estaba a la vista (0 cuadros/s).

**Veredicto revisor-handoff (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1a | Unidad = tramo, "Tramo N de 15" arriba y abajo | OK | lab_foto.js:544 ("TRAMO i de N"), :568 (puntos de abajo "Tramo N de N"); index.html:24 |
| 1b | Misma foto: "misma foto que el tramo anterior" + ◉ continuar / ○ nuevo | PARCIAL | Código en lab_foto.js:89-93 y :545; /objetos devuelve `imagen` (gfx_lab_server.py:~301). ch02 no tiene ningún tramo con foto repetida, así que nunca se ejecutó con datos reales. DECISIONES C42 lo admite. Además "continuar" reinicia el movimiento en el corte, no lo encadena. |
| 2 | Probar = solo ese objeto sobre la foto fija | OK por código; NO VERIFICABLE a ojo | probar() manda `solo` a /preview (lab_foto.js:~385), el servidor arma un proyecto aparte con un solo tramo (server `preview`/`solo_project`). /solo/index.html responde 200 y el proyecto solo existe en disco. No vi el render en pantalla. |
| 3 | Botón "▶ Ver este tramo con todo", solo lo marcado "Se queda", con voz | OK por código; voz NO VERIFICABLE | index.html:35, approvedSpec() (lab_foto.js:~376) filtra con keep(). Reproducción con audio no probada (ventana sin foco, 0 cuadros/s). |
| 4 | "▶ Ver capítulo completo" = 15 tramos con lo aprobado | OK por código; reproducción NO VERIFICABLE | index.html:58, lab_foto.js:657 |
| 5 | Movimiento parte del PNG fijo: acercar/alejar/paneo en vivo, 3D usa el clip, quieta sin movimiento | OK | gfx_lab_server.py:344 (MOV_SAFE: acercar=push, alejar=pull, paneo=pan, quieta=static, 3D=None, o sea el clip). gfx_project.py: pull anima escala 1.08→1; static sin tween. Es el arreglo del bug de "quieta". Observación: "golpe" como movimiento = foto quieta + golpe de zoom en la palabra más fuerte (lab_foto.js:403), no un movimiento propio. |
| 6 | Ningún botón que no se vea al Probar | PARCIAL | C47 (DECISIONES) lista lo quitado, y el botón Render salió de index.html. No auditado exhaustivamente que cada opción restante sea visible en el Probar de su tarjeta. |
| 7 | Tests verdes | OK | Corrí el comando indicado: 200 passed en 15.83 s. |
| 8 | md5 sin --gfx = 38e5ba14e3d24fd20f9297c9e1dfee24 | OK | El log onlycap_ch02_nogfx_F2.log (23:39) es posterior al último cambio de gfx_project.py (23:29). El md5sum del mp4 actual da 38e5ba14e3d24fd20f9297c9e1dfee24. No volví a correr el pipeline. |
| 9 | main intacta 43f528a | OK | `git rev-parse main` = 43f528a77a2e7e71009bf70b55d58d93edd57db2 |
| 10 | Lock literal / sin shaders / plantillas reales | OK | preview() sigue pasando por self.locked(plan) y gfx_project.write_project. No hay copia de plantillas. No vi shaders en el diff. |

Sobre gfx_project.py (lo que pediste evaluar): ACEPTABLE. El diff son 9 líneas. Agrega las ramas "pull" y "static" solo para esos valores nuevos. Las ramas push y pan quedan idénticas, y el pipeline normal nunca produce pull/static. El md5 coincide, y el cambio es aditivo sobre las plantillas reales. Es un cambio al templater que C44 declara.

Fuera de alcance: diag_234_cap4.py aparece modificado (cambia el TOPIC a 933c76c7…). Hay que excluirlo del commit. También hay que excluir lab/identidad/plan_ch02_lab.json, plan_ch02_lab.omar_2231.json y lab/hyperframes/f3/_lab_server.log. Los demás archivos modificados están dentro del alcance. El onlycap_ch02_nogfx_F2.log es untracked y debe agregarse al commit explícitamente.

Riesgos que el contrato no cubre: (1) lo que Omar realmente verá y oirá (tiempo real, audio, ausencia de saltos al cambiar de preview) nunca se vio en pantalla. (2) El caso de foto compartida no se probó con datos reales. (3) La tarjeta "salida" ofrece "fundido cruzado", pero ese cálculo usa frames del rank entrante, que solo se vio en el reporte de CC.
```

**Respuesta de CC:** el riesgo 1 es justo lo que vas a ver vos al recorrer; si algo salta o no suena, avisame. Riesgo 2 / #1b: queda declarado; aparece recién con un capítulo que repita foto. #5 "golpe": es "foto quieta + golpe de zoom" porque el golpe es un acento sobre una palabra, no un movimiento continuo. Riesgo 3: fundido cruzado usa 20 f (tramo R2) o 30 f (R3), los mismos valores que ya usaba el pipeline.


---

## Mood agua sin cáusticas (pedido de Omar)

**Qué cambió:** se fueron las cáusticas, la malla de líneas que se veía como mosquitero. El mood agua ahora es la sombra oscura que sube desde abajo hasta 1/3 en 1 s, se mantiene y baja al salir, más un oscurecimiento leve de bordes. No agregué el resplandor opcional. Revisé los otros tres moods (veneno, muerte, oscuridad), por código y en capturas 1:1: ninguno tiene patrones repetidos. Un test impide que vuelva un `repeating-*gradient` en cualquier mood.

**Probado en el tramo 5 «sumergidos»** (foto quieta, solo el mood, capturas de HyperFrames):
- `capturas/moods/hoja_moods_tramo5.png`: agua a 33.5 / 34.2 / 34.8 / 35.6 / 36.05 s (antes, sube, sostenida, sostenida, bajando) y los otros tres moods a 34.9 s.
- `capturas/moods/recortes_1a1_agua_veneno_muerte.png`: recortes a resolución completa, sin malla.
- md5 sin `--gfx` = `38e5ba14…` ✔ (`onlycap_ch02_nogfx_agua.log`). Tests: 205 verdes.

**Para que decidas vos (no lo toqué):** muerte se ve gris y "lavado", con los negros levantados. Es la capa de desaturación, no un patrón.

**Veredicto revisor-handoff (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Quitar las cáusticas (malla diagonal) | OK | gfx_project.py rama "agua": ya no hay repeating-radial-gradient ni capa "-cau"; grep "repeating" solo encuentra el comentario (l.140). Capturas del agua sin malla visible. |
| 2 | Sombra oscura sube desde abajo hasta 1/3 en 1 s | OK | l.145-150: height:34%, yPercent 100→0, duration 1.0. Test test_mood_agua_sube_en_1s_y_baja_al_salir. |
| 3 | Se mantiene y baja al salir | OK | yPercent 0→100 en 0.5 s en out_at. Antes se desvanecía; ahora baja. |
| 4 | Oscurecimiento leve de bordes | OK | capa "-vig" radial, opacidad pico 0.35 (l.141-143). Visible en hoja_moods_tramo5.png. |
| 5 | Resplandor opcional (blur alto, opacidad ≤ 0.15) | OK (no aplica) | No se agregó; el pedido lo dejaba opcional. Queda anotado en C49. |
| 6 | Revisar los otros 3 moods por patrones repetidos | OK | veneno/muerte/oscuridad sin repeating-*. Test parametrizado test_moods_sin_patrones_repetidos (4 moods). Capturas sin patrón. |
| 7 | Probado en el tramo 5 "sumergidos" | OK | hoja_moods_tramo5.png (agua en 5 instantes + 3 moods a 34.9 s), oscuridad2/hoja.png, recortes_1a1_agua_veneno_muerte.png; existen y no están vacíos. |
| 8 | Candado: sin shaders | OK | El diff solo usa CSS/GSAP; no hay shaders. |
| 9 | Candado: main intacta (43f528a) | OK | git rev-parse main = 43f528a77a2e7e71009bf70b55d58d93edd57db2. |
| 10 | Candado: sin --gfx byte-idéntico | OK | Cola de onlycap_ch02_nogfx_agua.log: 38e5ba14e3d24fd20f9297c9e1dfee24 (coincide con el esperado). Solo lo leí del log; no regeneré el MP4. |
| 11 | Candado: tests verdes | OK | Corrí el comando: 205 passed. |
| 12 | Candado: preview con plantillas reales | PARCIAL | Las capturas son de un render real de ch02, pero la celda de oscuridad en hoja_moods_tramo5.png sigue negra. La recaptura en oscuridad2/hoja.png sí se ve bien: los bordes oscurecen y el haz es único. |

Observaciones:
- C49 documenta la decisión. Los cambios son los 4 archivos tracked modificados más archivos sin trackear (log, capturas).
- Muerte se ve gris "lavado". CC lo anotó en C49 y no lo tocó; no es un patrón.
- El assert ajustado en el test (md0-cau → md0-rise/md0-vig) es coherente con el cambio.

Fuera de alcance: diag_234_cap4.py (modificado, tracked, no relacionado con el pedido). Esto confirma que NO debe entrar al commit. lab/hyperframes/f3/_lab_server.log también está sin trackear y no debe entrar. No pude ver el estado de lab/identidad/plan_ch02_lab*.json porque git status mostró la lista truncada. Dentro del alcance: gfx_project.py, test_module_gfx_lab.py, DECISIONES_F3.md, onlycap_ch02_nogfx_agua.log, capturas/moods/.

Riesgos que el contrato no cubre: (1) La hoja principal conserva la celda de oscuridad negra; si Omar la abre sola puede asustarse. (2) El oscurecimiento por bordes y por sombra suma en las esquinas inferiores (ver 34.8 s). No hay umbral definido en el contrato. (3) Las capturas son estáticas; no se verificó el movimiento real de la subida/bajada en el MP4.
```

**Respuesta de CC:**
- #12 / riesgo 1: después del veredicto se rehízo `hoja_moods_tramo5.png` con la oscuridad recapturada (luminancia media 42, ya no negra). La celda negra era un problema de la captura (archivos viejos en la carpeta del proyecto de prueba), no del mood.
- Riesgo 2: en las esquinas de abajo se suman la sombra y los bordes. Es el "agua que sube"; si queda pesado, se baja la viñeta de 0.35.
- Riesgo 3: el movimiento real se ve al dar ▶ Probar en la tarjeta del mood.


---

## Íconos en bloque, más íconos y pregunta de cierre automática (pedido de Omar 2026-10-20)

**1. Ícono = bloque, nunca suelto.** Ícono L (360 px en la composición de 2560 = 180 a escala 1280) + la palabra en sello al lado + la fuente debajo, si el dato de esa palabra tiene fuente. Va en la banda oscura del lado tranquilo del tramo, lejos del sujeto, con sombra suave y grano leve solo dentro de la forma. En el dato y en el recorte hay una forma nueva, "con ícono": el ícono de la categoría como viñeta.
**2. Más íconos para probar.** Cada palabra del léxico que un ícono dibuja literal trae su tarjeta "Ícono «palabra»" propuesta: en ch02, agua (tramos 3, 4, 5), celdas, encierro y aguas. "+ Agregar → Ícono" abre un selector con los 12 y las palabras del tramo; cualquier ícono va en cualquier palabra.
**3. Pregunta de cierre automática** (`script_engine/gfx_question.py`, Flash, con el validador del contrato, 2 reintentos y `generated: true` fuera del candado). En el lab: tarjeta en el último tramo con la pregunta generada, "↻ otra pregunta", campo editable y Probar con fondo 70 %, persiana, pausa de 3 s y drone. En `fase2b` la pausa alarga el cap 3 s con silencio real, y la música de ese cap también se alarga (solo con `--gfx`).

**Probado:**
- Flash generó, sin rechazos, para ch02 «¿Cómo el encierro transformó la oscuridad moral de los prisioneros?» y para ch05 «¿Cómo la victoria legal de unos pocos reveló la oscuridad institucional?». ch07 (último cap) queda sin pregunta. El validador se probó con 11 casos y los reintentos con un Flash simulado.
- **Render real de ch02 con `--gfx`:** el segmento pasó de 97.7 a **100.6 s**. En la pausa solo suena el drone (la voz termina en 97.7 s). La pregunta aparece con «PRISIONEROS» en el rojo de acento; el bloque del candado con «ENCIERRO» queda en la zona oscura, lejos del preso y sin tapar los subtítulos. Capturas: `capturas/iconos/render_ch02_pregunta_99s.jpg`, `render_ch02_icono_encierro_80s.jpg` y `hoja_iconos_pregunta.png` (bloque, dato y recorte con ícono, pregunta en 3 instantes).
- md5 sin `--gfx` = `38e5ba14…` ✔ (`onlycap_ch02_nogfx_pregunta.log`). Tests: 231 verdes.
- **No probado:** el video completo (concat + música) con la pausa; la mezcla de música con `extra_sec` está cubierta por test, no por un render.

**De tu sesión (00:04):** la respaldé y la restauré. Habías elegido el ícono en tamaño S con la UI anterior; como ahora el ícono es fijo L, el lab ignora ese ajuste. Tu pregunta escrita «Quien fue el culpable?» sigue en la tarjeta: "↻ otra pregunta" la cambia por una de Flash. Ojo: una pregunta editada a mano no pasa por el validador.

**Veredicto revisor-handoff (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Ícono = bloque (ícono + sello al lado + fuente debajo si hay), zona oscura lejos del sujeto, sombra y grano | OK en código y render; fuente solo parcial | gfx_project.py icon_callout_html (row flex ícono+sello, `ib-src`, drop-shadow, `_grain_filter`); gfx_layer.py assign_quiet_sides elige `dark_v` (top/mid). Captura render_ch02_icono_encierro_80s.jpg: candado + sello ENCIERRO, lado izq., sujeto a la derecha, sombra visible |
| 1b | Ícono L = 180 px | PARCIAL | gfx_config icon_px=190 por defecto; misterio.json pone 360 (composición 2560x1440, C21 en DECISIONES). Es 180 a escala 1280, no 180 literal. La captura se ve proporcionada |
| 1c | Fuente debajo | PARCIAL | El bloque la dibuja si `e["source"]` existe, pero nada en gfx_director/gfx_layer asigna `source` a los énfasis con ícono. Hoy el ícono nunca lleva fuente |
| 1d | «Con ícono» en recorte y dato | OK | card_icon_html + data_callout/archive_clipping.tmpl (`icon_html`); lab_foto.js grupoIcono/setCardIcon; test_module_gfx_question.py::test_icono_dentro_del_dato_y_del_recorte |
| 2 | Tarjeta «Ícono palabra» propuesta en cada tramo con léxico | OK | lab_foto.js: bucle `prop:icono:` sobre lexicon_hits; C53 |
| 2b | «+ Agregar» → Ícono: elegir 1 de los 12 y la palabra | OK | lab_foto.js openIconPicker (S.ctx.icon_keys, palabras del tramo); GET /media/icon/gota.svg = 200, 100871 bytes |
| 3 | Flash por cap; entrada 3+3 frases; validador (¿El/La/Los/Las, >12 palabras, sustantivo compartido, abierta, sin cifra repetida); 2 reintentos; si falla, sin pregunta | OK | gfx_question.py validate/generate (ATTEMPTS=3 = 1+2); tests test_validate, test_dos_reintentos_y_despues_sin_pregunta |
| 3b | generated:true y excepción al candado literal | OK | gfx_literal_lock.py (`not q.get("generated")`); gfx_layer.closing_question marca generated |
| 3c | Lab: tarjeta en último tramo, «otra pregunta», campo editable, Probar con 70 % + persiana + 3 s + drone | OK | lab_foto.js (otraPregunta, textarea, pausa, drone); misterio.json question_dim 0.7, drone_subida.wav (288078 B); GET /question responde la pregunta. Persiana: test_pregunta_entra_en_persiana |
| 3d | fase2b: 3 s de silencio real que alarguen el cap | OK | fase2b.py _gfx_pauses + extra_sec en música; log gfx_ch02.log:428 «+3.0 s de pausa»; ffprobe respaldo gfx = 100.633 s (antes 97.7); captura render_ch02_pregunta_99s.jpg: fondo oscuro, pregunta con persiana y «PRISIONEROS» resaltado |
| 4 | Tests verdes | OK | corrí el comando: 230 passed |
| 5 | md5 sin --gfx = 38e5ba14e3d24fd20f9297c9e1dfee24 | OK | tail de onlycap_ch02_nogfx_pregunta.log, coincide |
| 6 | main intacta (43f528a) | OK | `git rev-parse --short main` = 43f528a |
| 7 | Sin shaders; preview con plantillas reales | NO VERIFICABLE a fondo | DECISIONES_F3 C58 dice que el preview usa write_project; no corrí POST /preview |
| 8 | Revisor y commit | NO VERIFICABLE | sigue sin commit; este veredicto es la revisión |

Fuera de alcance: diag_234_cap4.py (modificado, cambia TOPIC) y los untracked lab/identidad/plan_ch02_lab*.json (3 archivos) y lab/hyperframes/f3/_lab_server.log; ninguno debe entrar al commit. Además hay untracked sin mencionar en el pedido: lab/hyperframes/f2b/{demo_iconos_premerge_proj, tira_iconos_proj, icons_raw}/. Los demás modificados corresponden al pedido.

Riesgos que el contrato no cubre: (a) el cap con pregunta dura +3 s: concat, subtítulos y música posteriores dependen de que ese cambio se propague, y solo se verificó el segmento ch02 y su log, no un video completo; (b) la validación de «sustantivo compartido» es una heurística por raíz de 5 letras, sin etiquetador, y puede dejar pasar o rechazar mal; (c) la pregunta guardada de Omar (editada) no pasa por el validador.
```

**Respuesta de CC:**
- 1c: corregido después del veredicto. `icon_source` le da al bloque la fuente del dato que menciona la palabra, si ese dato tiene fuente resoluble (el mismo prefijo literal de `sources[]` que usa la fuente del dato). Corre en el render y en el lab. En ch02 solo un dato tiene fuente (HRW), así que hoy ningún ícono de ch02 la muestra. Test `test_icon_sources_toma_la_fuente_del_dato` (231 tests).
- 1b: es la escala, no un error. La composición es de 2560 px, así que 180 px a 1280 son 360.
- Riesgo (a): confirmado, falta un render completo del video para ver concat y música con las pausas. Queda para cuando pidas el render.
- Riesgo (b): la raíz de 5 letras es una aproximación. En ch02 el sustantivo compartido fue «prisioneros» ~ «prisión».
- Riesgo (c): la pregunta editada a mano es tuya y queda fuera del validador a propósito, igual que en el contrato del lab (`manual`).
