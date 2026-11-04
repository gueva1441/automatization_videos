# F76: master −14 LUFS con pico real controlado (cierra C2 de F75) — PARADA
2026-11-04 · rama f11-guion-v4 · base ff368d4 · handoff `HANDOFF_F76.md`, md5 `cd173fc84754f88e96b23a4ca286c050` (verificado antes de arrancar)

## En corto
- El master quedó cableado en fase2b, en el lugar común de los 3 caminos.
- En la copia de Wittenoom cerró en **2 pasadas, sin ⚠: I −14,2 LUFS, pico real −1,6 dBTP** sobre el AAC. Los dos cumplen.
- Video intacto: el md5 del stream de video es el mismo. Sincronía audio/video: desfase de 0 ms por correlación cruzada.
- US$ 0, ninguna llamada a API.
- El mp4 publicado de Wittenoom sigue con md5 `1fb47948e43951d4c009e13c0131d184` antes y después. No se escribió nada en `output/`.
- El −2 dBFS de F75 no está en el código.
- Subagentes en paralelo: E1 (cableado + tests) y E2 (lab). El módulo base `audio_master.py` lo escribí yo antes de lanzarlos, para que E2 tuviera la función desde el principio.

## E1: código y tests
### Módulos
**`script_engine/audio_master.py` (nuevo)** tiene la receta del handoff, en un solo camino:
- `master_mp4(path)` mide el original y corre el `bucle`. Cada pasada: `volume=G` → `aresample=176400` (×4) → `alimiter=level=disabled:latency=1:limit=10^(techo/20)` → `aresample=44100` → AAC 192k. Mide el AAC con `ebur128=peak=true`.
- Falla = exceso de pico + exceso de sonoridad fuera de ±0,5 LU.
- Si falla, baja el techo en lo que se pasó el pico y suma a G lo que faltó de sonoridad.
- Para cuando cumple, o cuando una pasada no baja la falla. En ese caso se queda con la mejor que cumple el pico (o la de menor pico) y deja un ⚠ en el log, sin frenar.
- Al final hace remux con `-map 0:v -map 1:a -c copy` a un temporal y lo reemplaza de forma atómica.
- El log imprime la tabla de pasadas.
- Después de E1 le agregué que borre el `._master_tmp` si falla el remux (lo marcó E1).

**`audio_profiles.py`**: junto a `voice_lufs_v4` hay 5 constantes nuevas, cada una con su comentario de origen:

| constante | valor |
|---|---|
| `master_lufs` | −14 |
| `master_tp_dbtp` | −1,5 |
| `master_oversample` | 4 |
| `master_lufs_tol_lu` | 0,5 |
| `aac_bitrate` | "192k" |

**`audio_manager.py:464`**: lee `master_tp_dbtp` en lugar del literal −1.5. Es el mismo valor.

**Cambio de rutina, el `"192k"`**:
- `fase2b.py` 1346, 1353, 2044, 2086 y 2174 usan `AAC_BITRATE` (`fase2b.py:103`, sale del perfil).
- `script_engine/transition_applier.py:432` lee el perfil.
- La salida no cambia.

**`fase2b.py`**: diff alrededor de la llamada (`:3660-3664`):
```
         music_floor_path.unlink(missing_ok=True)
         print(f"     ✅ música mezclada en {final_path.name}")
 
+    # F76: master del mp4 final (−14 LUFS, pico real ≤ −1,5 dBTP), común a los 3 caminos (sin música / audio solo /
+    # clásica); el video sale con -c:v copy. _final_gfx_no_music.mp4 y mezcla_preview.wav quedan a −24 (no se publican).
+    print(f"\n  🔊 Master del audio final ({final_path.name})...")
+    master_mp4(final_path, ffmpeg=FFMPEG, log=print)
     final_dur = _get_duration(final_path)
```
La llamada está a nivel de función, después del if/else de la música, así que la toman los caminos (a), (b) y (c). El import está en `fase2b.py:65`.

### Tests (`test_module_f76.py`, 12/12)
1. Cierra en 1 pasada (G 10,0, techo −1,5).
2. Cierra en 3 pasadas como la tabla del handoff: (10,0, −1,5) → (10,3, −2,7) → (10,8, −3,2), con falla 1,2 → 0,5 → 0.
3. G y techo se actualizan según la receta: el techo solo baja si el pico se pasó; G sube o baja según −14 − I.
4. Sin progreso, queda la mejor que cumple el pico, con ⚠.
5. Sin progreso y ninguna cumple el pico, queda la de menor pico, con ⚠ «NINGUNA».
6. La falla sale con la fórmula del handoff.
7. La cadena lleva `latency=1`, `aresample=176400`, `limit=10^(techo/20)` y termina en `aresample=44100`.
8. `audio_master` no tiene el −2 dBFS de F75 (regex + AST).
9. Las constantes del perfil.
10. fase2b llama al master una sola vez, a nivel de función, y la línea siguiente es `final_dur`.
11. No queda ningún literal `"192k"` en fase2b ni en transition_applier, y audio_manager usa la constante.
12. ffmpeg real sobre un mp4 sintético de 4 s (lavfi): el md5 del stream de video es igual, la duración del audio cambia como mucho 1 cuadro y cumple −14 ± 0,5 y el techo de pico. Una senoidal pura no llega al limitador: la corrección del techo con audio real la prueba E2.

## E2: lab sobre una copia de Wittenoom
Script `lab/hyperframes/f76/e2_master_lab.py`, log `e2.log` y resultado `e2_result.json`. ffmpeg 8.1. Copia: `lab/hyperframes/f76/wittenoom_copia.mp4` (masterizada, 531 MB, queda para que Omar la vea).

### Tabla de pasadas (medida sobre el AAC)
| pasada | G | techo limitador | I | LRA | pico real (AAC) | falla |
|---|---|---|---|---|---|---|
| original | — | — | −24,0 | 6,6 | −6,6 | — |
| 1 (×4) | +10,00 | −1,50 | −14,3 | 6,0 | −1,2 ✗ | 0,3 |
| **2 ← elegida** | +10,30 | −1,80 | −14,2 | 5,9 | **−1,6 ✓** | 0,0 |

- Sin ⚠. En 8.1 el AAC sumó +0,3 dB de pico en la 1.ª pasada, y la 2.ª bajó el techo exactamente 0,3 y cerró. Es lo que esperaba el handoff, que lo cerrara en 1 o 2 pasadas.
- El «después» lo medí aparte del módulo, con ebur128 sobre el mp4 final: I −14,2, LRA 5,9, pico real −1,6. Coincide con la pasada 2.

### Sincronía y video
| | antes | después |
|---|---|---|
| md5 del stream de video | `aa4e36ccafa6c270419285a5080fe4ce` | `aa4e36ccafa6c270419285a5080fe4ce` (igual) |
| duración del video | 798,266667 s | 798,266667 s |
| duración del audio | 798,255011 s | 798,255011 s |
| audio − video | −11,66 ms | −11,66 ms (≤ 33 ms ✓; ya venía así en el publicado) |

Correlación cruzada original vs. master, en ventanas de 4 s a 30, 400, 660 y 790 s: retardo **0 ms** en las 4, con correlación de 0,990 a 0,999. Con `latency=1` no hay atraso.

### Los 4 extractos nuevos (60 s, wav 24 bit 44,1 kHz)
Son los mismos tramos que en F75, para escuchar:

| archivo | I | LRA | pico real |
|---|---|---|---|
| `lab/hyperframes/f76/extracto_gancho_0000-0100_original.wav` | −23,8 | 6,2 | −6,6 |
| `lab/hyperframes/f76/extracto_gancho_0000-0100_master.wav` | −14,6 | 4,5 | −1,7 |
| `lab/hyperframes/f76/extracto_fuerte_1044-1144_original.wav` | −21,8 | 3,4 | −6,8 |
| `lab/hyperframes/f76/extracto_fuerte_1044-1144_master.wav` | −12,2 | 2,4 | −1,7 |

La I de cada extracto es la de ese tramo; el ±0,5 se aplica al archivo entero. Los wav y los mp4 no van a git.

## Verificación
- Suite rápida (`f25c`, `f24`, `f21`) más `f76`: 65 passed, 3 skipped.
- Suite amplia, como en F73/F75 (incluye `tests/` y `test_qa_studio.py`): **3 failed, 1584 passed, 29 skipped, 2 xfailed** (`lab/hyperframes/f76/suite.log`). Las 3 son las heredadas: `f51c[1-start-paredes de chapa.]` y `m03_merge_timing` ×2.
- `mapa_modulos --check`: 162 archivos · **0 fallas**.
  - Sticker nuevo de `audio_master.py` en `fase2a.json`, que es su zona según `--zonas`.
  - md5 al día de `audio_manager.py` y `audio_profiles.py` (en `fase2a.json`) y de `fase2b.py` y `transition_applier.py` (en `fase2b_gfx.json`).
- `DECISIONES.md`: la línea 241 (F75 C) **se reemplazó** por la receta nueva. Es 1 línea cambiada, no una sumada.

## diff --stat (sin los ajenos)
```
 DECISIONES.md                       |  2 +-
 audio_manager.py                    |  5 +++--
 audio_profiles.py                   | 11 +++++++++++
 fase2b.py                           | 17 ++++++++++++-----
 lab/mapa/stickers/fase2a.json       | 25 ++++++++++++++++++++-----
 lab/mapa/stickers/fase2b_gfx.json   |  8 ++++----
 script_engine/transition_applier.py |  3 ++-
 nuevos: script_engine/audio_master.py, test_module_f76.py, lab/hyperframes/f76/{F76_REPORT.md, e2_master_lab.py, e2.log, e2_result.json, suite.log}
```

## Abierto
- **Omar escucha los 4 extractos nuevos de F76** (no los de F75) antes del render de Palomares. Si quiere verlo con imagen, puede abrir la copia masterizada `lab/hyperframes/f76/wittenoom_copia.mp4`.
- **Wittenoom publicado sigue a −24 LUFS.** Si se quiere re-subir masterizado, la copia ya está hecha; decide Omar. El pipeline no lo re-renderiza.
- **El remux se queda solo con 1 video y 1 audio.** `master_mp4` hace `-map 0:v -map 1:a`, así que si el mp4 trae otro stream (subtítulos, datos), se pierde. Hoy fase2b no lo pone.
- **Tiempo de render.** El master suma cada pasada sobre unos 13 min de audio (en Wittenoom, 2 pasadas más la medición). No lo cronometré dentro de fase2b porque no hubo render.
- **Archivos que siguen a −24 LUFS.** `_final_gfx_no_music.mp4` y `mezcla_preview.wav` no pasan por el master. Así se aceptó en F75 y no se publican.
- **`_perfil` privado.** `audio_manager.py`, `transition_applier.py` y `fase2b.py` importan `_perfil`, un nombre privado de `audio_master` (lo observó el revisor).
- **Test sintético.** El test 12 usa una senoidal, que nunca llega al limitador, así que la corrección del techo con ffmpeg real solo queda probada por E2.
- **Pendientes heredados de F75 que esta tanda no toca:**
  - el pool fusiona homónimos padre/hijo;
  - la escaleta no comprueba que `humano.id` corresponda al `rol`;
  - las rachas no cuentan pronombres ni «el hombre»;
  - los personajes con partícula no se encuentran.

## Veredicto del revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | `script_engine/audio_master.py` nuevo, con `master_mp4`, el bucle y el remux `-c copy` por temporal y reemplazo atómico | OK | audio_master.py:74-133. La receta (volume, aresample ×4, alimiter con latency=1, aresample 44100, AAC) está en :57-67. La falla, el fin del bucle y el ⚠ están en :70-98. |
| 2 | Llamada en fase2b una sola vez, antes de `final_dur`, común a los 3 caminos | OK | fase2b.py:3660-3663, a nivel de función, después del if/else de música; import en :65. |
| 3 | Constantes nuevas en `audio_profiles.py`, cada una con comentario de origen | OK | audio_profiles.py: `master_lufs`, `master_tp_dbtp`, `master_oversample`, `master_lufs_tol_lu`, `aac_bitrate`, todas junto a `voice_lufs_v4`. |
| 4 | `audio_manager.py:463` lee `master_tp_dbtp` | OK | Diff de audio_manager.py: `TP={_master_perfil('master_tp_dbtp')}`. |
| 5 | Sin literales "192k" en fase2b ni en transition_applier | OK | `grep 192k` sobre ambos archivos da 0 coincidencias. fase2b usa `AAC_BITRATE` (:103); transition_applier usa el perfil. |
| 6 | El −2 dBFS de F75, la 2.ª pasada de loudnorm y `-ar 48000` no están en el código | OK | `grep` sobre los 4 archivos de código no encontró ninguno. El test 8 también lo cubre. |
| 7 | `DECISIONES.md` línea 241 reemplazada, no sumada | OK | `git diff`: 1 línea − y 1 línea +, sobre la de F75 C. |
| 8 | Tests de E1 (bucle en 1 y 3 pasadas, sin progreso, llamada única, md5 de video) | OK | `python -m pytest test_module_f76.py -q` da 12 passed. |
| 9 | Suite rápida verde + las 3 heredadas | OK | suite.log: 3 failed (f51c paredes de chapa, m03_merge_timing ×2), 1584 passed. Las 3 son las heredadas. No la volví a correr; leí el log de CC. |
| 10 | `mapa_modulos --check` con 0 fallas | OK | Lo corrí: 162 archivos · 0 fallas. El sticker de audio_master está en fase2a.json. |
| 11 | E2 sobre una copia, con tabla de pasadas y ffmpeg 8.1 | OK | e2.log y e2_result.json: 2 pasadas, la elegida es la 2 (G +10,3, techo −1,8, I −14,2, LRA 5,9, pico −1,6), aviso None. Coincide con la tabla del reporte. Medí la copia: I −14,2, LRA 5,9, pico real −1,6. |
| 12 | md5 del stream de video igual antes y después | OK | Recalculé: la copia da aa4e36ccafa6c270419285a5080fe4ce y el publicado da el mismo valor. |
| 13 | Sincronía audio/video ≤ 33 ms | NO VERIFICABLE | El desfase de −11,66 ms y la correlación cruzada de 0 ms vienen del reporte. No los recalculé. No hay contradicción con lo que medí. |
| 14 | 4 extractos nuevos de 60 s (0:00–1:00 y 10:44–11:44, original y master) | PARCIAL | Existen los 4 wav, de 7,9 MB cada uno, con nombres coherentes. No los escuché ni medí. Los nombres dicen `0000-0100` y `1044-1144` (el reporte los describe como 60 s). |
| 15 | mp4 publicado de Wittenoom sin tocar y nada en `output/` | OK | md5 1fb47948e43951d4c009e13c0131d184 verificado ahora. `git status` de `output` no muestra nada. |
| 16 | US$ 0, ninguna API | OK | audio_master.py y e2_master_lab.py solo usan subprocess a ffmpeg. |
| 17 | Reporte con E1, E2, «abierto» completo y veredicto | PARCIAL | F76_REPORT.md tiene E1, E2 y «Abierto». La sección del veredicto está como placeholder («pegado abajo»), a completar con este texto. |
| 18 | Sin 3.ª pasada ni número de vueltas | OK | El bucle termina por la regla, sin tope. |

Fuera de alcance: ninguno de CC. Los modificados ajenos (diag_234_cap4.py, f28a.log, pedido_paquetes_wittenoom.txt) no fueron tocados por la tanda. Los archivos nuevos están en `lab/hyperframes/f76/`, y la copia mp4 y los wav son binarios que no deben entrar al commit. Al hacer commit hay que agregar archivo por archivo, sin `git add -A`, porque hay muchos `??` ajenos en el repo.

Observaciones:
- `audio_manager.py` y `transition_applier.py` importan `_perfil`, que es privado, desde `audio_master`. Funciona, pero acopla módulos por un nombre con guion bajo.
- Si el mp4 trae más de 1 stream de video o de audio, `-map 0:v -map 1:a` los pierde. El reporte lo declara.
- Los extractos tienen LRA 4,5 y 2,4 contra 6,6 originales: el limitador comprime el rango dinámico. Es para el oído de Omar, que es la PARADA.

Riesgos que el contrato no cubre:
- Nadie midió el tiempo de render de las 2 o más pasadas dentro de fase2b: no hubo render real. El test de integración real de fase2b con master no existe; solo se comprobó por AST que la llamada está en el lugar correcto.
- El test sintético usa una senoidal, así que solo E2 prueba el limitador con audio real (una sola muestra: Wittenoom). Con material más denso, el bucle podría terminar en ⚠.
- Wittenoom publicado sigue a −24 LUFS.

### Adenda de CC
- **Punto 13:** E2 midió el desfase con ffprobe, por stream: −11,66 ms antes y después (ya venía así en el publicado). Hizo además la correlación cruzada en 4 ventanas, con retardo 0. El script de la correlación quedó fuera del repo, en el scratchpad de la sesión.
- **Punto 14:** cada extracto dura 60 s (0–60 s y 644–704 s). Los nombres usan mm:ss, no la duración. E2 midió los 4: I/LRA/pico están en la tabla del reporte.
- **Punto 17:** con este pegado queda cerrado. ESTADO_SESION entra en el mismo commit.
- **`_perfil` privado:** de acuerdo, es un acople por un nombre privado. No lo renombro en esta tanda para no tocar más archivos; lo dejo anotado en «abierto».
- **Material más denso:** si el bucle no cierra, termina con ⚠ en el log y sigue, sin frenar el render. Eso lo cubren los tests 4 y 5. El primer render real de Palomares lo va a mostrar.
