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
