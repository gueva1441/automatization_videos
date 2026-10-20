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
