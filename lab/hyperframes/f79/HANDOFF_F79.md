# HANDOFF F79 — aire muerto fuera: intro, title card sobre la voz, pausa tras cita

Rama `f11-guion-v4`, base `210873b` (F78d). Analista, 2026-11-09. Aprobado por Omar 2026-11-09 22:13 (orden de trabajo, punto 4) y 22:17 («si dale»). Auditado por subagente (15 correcciones aplicadas; esta es la versión corregida).
Sin render, sin TTS, sin tocar ningún prompt del pipeline. Costo esperado: centavos de Gemini (ver §5.4).

## 1. Por qué
En el render de Wittenoom el 28,4 % del video no tiene voz: 226,5 s de 798 (296 silencios medidos con `silencedetect`; `lab/_gpt_probe_analista/auditoria_2026-11-09/silencios_sin_musica.txt`). Tres fuentes las pone el código, no la voz:

| Fuente | Dónde | Cuánto en Wittenoom |
|---|---|---|
| Intro: primer cuadro congelado, sin voz | `fase2b.py:153` `INITIAL_SILENCE_SEC` | 2,5 s |
| Title card de capítulo sin voz (pre-roll), caps 2–7 | `gfx_config.py:197` `title_pre_roll`, `fase2b.py:1161` `_pre_roll_de` | 6 × 3,0 = 18,0 s |
| `[long pause]` después de cada oración con cita | `script_engine/tts_tags.py:73-74` | 14 pausas (los segundos se miden al grabar la próxima voz) |

Lo que Omar aprobó: intro fuera, title card encima de la voz, sin pausa fija tras cita.

## 2. Orden re-derivado
- ¿Construye sobre código que ya se decidió reemplazar? No. Omar aprobó «tarjeta encima de la voz» (2026-11-09 22:13): el title card se queda. Quitar el pre-roll no depende de cuántos caps haya.
- ¿Alguna decisión de hoy cambia el orden? Sí: del handoff único «2 + 3 + 4» sale primero el punto 4 (este), que es solo código. Los puntos 2 y 3 (paquete antes de la escaleta, quitar el molde) tocan prompts y van en F80, con laboratorio propio.

## 3. Constantes
| Valor | Origen | Quién |
|---|---|---|
| Intro del mp4: se borra (hoy 2,5 s, Chat 32) | DECISIONES 2026-11-09 22:13, punto 4 | Omar |
| Pre-roll del title card: se borra (hoy = `title_dur`, F30b B.3) | ídem («tarjeta encima de la voz») | Omar |
| `title_dur` 3,0 s · `title_fade_out` 0,4 s · `title_dim` 0,4 · `title_scale` 0,7 | identidad F3, `gfx_config.py:192-195`. NO cambian | existente |
| Negro entre caps 1,0 s | `black_hold_sec`, `gfx_profiles/misterio.json:57`. NO cambia | existente |
| Subida desde negro, 10 cuadros | identidad F3. NO cambia | existente |
| `[long pause]` tras oración con cita: se borra | DECISIONES 2026-11-09 22:13, punto 4 | Omar |
| `[long pause]` de cierre de cap: queda | F9 §3.3, `tts_tags.py:79-80` | existente |
| 777,766 s esperados en Wittenoom | derivado: 798,266 − 2,5 − 6 × 3,0 | analista |
| ± 0,23 s | derivado: 1 cuadro (1/30 s) por cada uno de los 7 tramos que se quitan (1 intro + 6 pre-rolls) | analista |
| `[long pause]`: Wittenoom 21 → 7, Colza 22 → 7 | simulación del analista (§5.2), recontada por el auditor | analista |

Ningún número nuevo entra al código: esta tanda solo borra.

## 4. Reglas: qué se quita y qué reemplaza a qué
| Regla que se va | Dónde está escrita | Qué queda en su lugar |
|---|---|---|
| Intro de 2,5 s («la música respira sola») | Chat 32, `fase2b.py:151-153`; DECISIONES l.44 la dejó «por decidir» | Nada. El mp4 arranca en el primer cuadro del cap 1, con la voz. |
| «Title card con aire = `title_dur` (3 s) sin voz» | DECISIONES l.94 (2026-10-26, F30b); l.76 catálogo componente 1 («3 s sin voz»); l.91 («entre caps negro → title card → voz»); l.234 lo menciona al describir la costura | El title card se dibuja igual (0,0–3,0 s del cap), pero la voz del cap arranca en 0: negro → voz con el title card encima. |
| «ch01 sin pre-roll» | DECISIONES l.35 (2026-10-26 14:22), solo esa cláusula | Ningún cap tiene pre-roll. Y, en la Etapa A2: **el primer cap del video no lleva title card** (voto del analista; Omar lo confirma al mandar el prompt). |
| `[long pause]` después de cada cita | F9 §3.3 | Nada. La oración con cita se graba como cualquier otra. |

Siguen vigentes y se cumplen solas: «la música del cap arranca con su title card» (l.35: el title card queda en el 0,0 del cap, y la música también) y «nunca dos bloques al mismo tiempo» (l.70, 2026-10-26 17:58).

Por qué el primer cap sin title card: hoy «CAPÍTULO 1» ya se dibuja encima del gancho (2,5–5,5 s del mp4; la voz entra a los 2,66 s) con el video oscurecido 40 %. Sin intro quedaría en 0,0–3,0 s: lo primero que ve quien entra. Además reserva esos 3 s y ningún reloj, ficha o sello puede ir ahí. Es una regla que quita algo que hoy se ve (y su golpe de sonido): por eso va sola en A2. Caso límite: un video de un solo cap no lleva ningún title card.

## 5. Simulación contra la data real
**5.1 Línea de tiempo** — `output/123bbb64-9fca-4395-8bf4-57d60e219ef1/GUION_PANTALLA.json` (Wittenoom, F72d). 135 eventos: 85 transiciones, 14 costuras, 7 title cards y 29 bloques.

| Cap | pre-roll hoy | voz a (s del cap) hoy | bloques anclados en los primeros 3 s de voz |
|---|---|---|---|
| ch01 | 0,0 (intro 2,5 aparte) | 0,16 | 0 |
| ch02 | 3,0 | 3,08 | 1: reloj «16 SEP · 1961» (3,08 s, dura 9,55 s) |
| ch03–ch04 | 3,0 | 3,08 | 0 |
| ch05–ch07 | 3,0 | 3,10 | 0 |

Qué va a pasar con ese reloj: al quedar la voz en 0, cae bajo la reserva del title card (`pantalla_colocar.py:309-310`, `(0.0, title_dur)`). El reloj está en el chequeo «dos bloques al mismo tiempo» (`gfx_guion.py:39` `ANIMACIONES`, l.443) y `repartir` lo prueba contra esa reserva (`pantalla_colocar.py:361-387`): lo corre a la oración siguiente si le quedan ≥ `TICKER_MIN` en pantalla, o lo saca. **Se deja decidir a la regla que ya existe; no se agrega ninguna.** En Wittenoom es 1 bloque de 29. Se reporta adónde fue y cuánto dura.

**5.2 Pausas** — `data/scripts/_steps/<tid>/01b_narration.json`, campo `narration_tts`:

| Topic | `[long pause]` hoy, por cap | oraciones con cita, por cap | quedan |
|---|---|---|---|
| Wittenoom `123bbb64…` | 21 (1, 3, 7, 2, 2, 4, 2) | 14 (0, 2, 6, 1, 1, 3, 1) | 7 (1 por cap) |
| Colza `c4934b7d…` | 22 (2, 1, 3, 2, 5, 5, 4) | 15 (1, 0, 2, 1, 4, 4, 3) | 7 (1 por cap) |

Ningún cap cierra en oración con cita, así que la fusión de pausas dobles (`tts_tags.py:81`) no cambia la cuenta.

**5.3 El golpe (sfx) del title card** — `gfx_layer.sfx_title_card` no se toca. Predicción leyendo su regla (l.407-420): en ch02–ch04 la primera palabra arranca a 0,08 s, el golpe a 0,05 s cae sobre ella y, por empezar con mayúscula, se descarta salvo que haya un hueco a ≤ `sfx_shift_max_ms`; en ch05–ch07 (primera palabra a 0,10 s) va a 0,05 s, pegado al ataque. Se reporta qué hizo en cada cap. Si el golpe se queda, se va o se mueve lo decide Omar al oírlo (catálogo, componente 9); no es de esta tanda.

**5.4 El crítico de pantalla vuelve a llamar** — la clave de su caché lleva el segundo del bloque (`gfx_critic.py:152`, `round(t, 2)`). Al bajar 3,0 s los tiempos de ch02–ch07, esas claves no existen y `--plan-only` vuelve a preguntarle a Gemini, con veredicto que puede variar. Costo de referencia: US$ 0,0356 el plan-only completo de F72. Es esperado y se acepta: se reporta cuántas llamadas hizo y qué bloque cambió de veredicto. `ent["pre_roll"]` (`pantalla_entrada.py:155`) no llega a ningún prompt ni a disco: es un campo muerto.

**5.5 `inicio_de_voz` mide mal sin intro** — `gfx_guion.py:134-141`: la ventana de búsqueda arranca en `esperado − primera − buscar_s`, que con la voz de ch01 a 0,16 s es negativa; `_pcm` recorta a 0 pero el `lag` usa el valor sin recortar, y la rampa (l.143, `desde = esperado − 2·RAMPA_S`) también queda antes de 0. Daría ✗ falso en ch01. Es parte de esta tanda (§6).

## 6. Módulos que toca
Un solo concepto (dónde arranca el video y dónde arranca cada cap) repartido en cinco archivos, más uno independiente (`tts_tags`). Por eso va en un handoff, con etapas que se miden por separado.

| Módulo | Hoy | Después |
|---|---|---|
| `fase2b.py` | Intro: `INITIAL_SILENCE_SEC`, `intro_sec`, `tpad`/`adelay`, clip `_pad.ts`, `_con_intro`, `mezcla["intro"]`, `_medir_inicio_musica(intro)`. Pre-roll: `_pre_roll_de`, `_visual_con_pre_roll`, `pre_sec=prerolls`, `pre_sec` de `_build_music_piece_for_chapter`, `_segmento_de_cap["pre_roll"]`, `_correr_tramos`, `_costura_medida`, l.3591-3597, y el `+ pre_roll` de `pre_pad` (l.1203, 2948, 3180, 3596). `titulo` del cap sale del title card (l.3217). | Ni intro ni pre-roll: el mp4 arranca con el cap 1 y cada cap con su voz. `pre_pad` queda solo con `HOOK_DURATION` (que no se toca). `titulo` del cap sale de `ctx["skeleton"]["title"]` (no depende de que haya title card). |
| `gfx_config.py` | `GfxRules.title_pre_roll: bool = True`. | El campo no existe. El `GfxBlock` `title_card` (`description`, `rules`: texto que lee un modelo) NO se toca. |
| `script_engine/gfx_layer.py` | `build_scenes` / `apply_gfx` reciben y pasan `pre_roll` (l.133, 155, 533, 546, 606, 610, 764); `escenas_a_disco` lo guarda; `plan_base(ctx)` (l.454-465, único llamador l.664) pone title card a todo cap con título y no sabe cuál es el primero. | Sin `pre_roll` en ninguna firma ni archivo. A2: `apply_gfx` le pasa a `plan_base` el dato de primer cap que ya existe (`ChapterPlan.is_first`, `fase2b.py:2549`), y ese cap sale con `title_card: None`. `sfx_title_card` no se toca. |
| `script_engine/pantalla_entrada.py` | `preparar_cap(..., pre_roll=0.0)` y campo `pre_roll` (l.94, l.155). | Sin parámetro ni campo. |
| `script_engine/gfx_guion.py` | Escribe «intro 2.5 s…», «sin voz (pre-roll…)», `intro_s`, `pre_roll`, `tramos.intro_s`/`title_card_s`; el chequeo de música dice «title card» (l.555-558; `fase2b.py:3085`); `inicio_de_voz`/`_pcm` (l.85, l.134-143) asumen que hay aire antes de la voz. | Describe lo que hay: negro → sube desde negro → voz, con el title card encima donde lo haya. Sin `intro_s` ni `pre_roll`. Cap sin title card: `tramos` y el chequeo de música no lo nombran. `inicio_de_voz`: ninguna ventana empieza antes de 0 y el `lag` se calcula sobre la ventana real, con test. |
| `script_engine/tts_tags.py` | l.73-74: `[long pause]` tras cada oración con «» o “”. | Esas dos líneas no existen; docstring al día. La fusión de l.81 queda (sirve a la pausa de cierre). Las demás etiquetas, igual. |

Documentación que nombra lo viejo y se pone al día (no son prompts del pipeline): docstrings de `gfx_critic.py:53-55`, `gfx_guion.py:7` y `123-124`, comentario de `mixer_server.py:261`, y `.claude/skills/guion-de-pantalla/SKILL.md:23` («intro de 2.5 s y pre-roll ya sumados»).

Tests que hoy fijan lo viejo: `test_module_audio_mixer_floor.py`, `test_module_concat_windowed.py`, `test_module_f30b.py`, `test_module_f32.py`, `test_module_f34.py`, `test_module_f36.py`, `test_module_f38e_a.py`, `test_module_f38e_d.py` (intro / pre-roll) y `test_module_f9.py`, `test_module_f10.py`, `test_module_f23.py`, `test_module_f32.py`, `tests/test_m01f_compuerta.py` (etiquetas). El que solo existe para afirmar lo viejo se borra; el que prueba otra cosa y usa el valor se actualiza. Cada uno va en el reporte con «borrado / actualizado» y por qué.

Lo viejo se borra, no se apaga: nada de `INITIAL_SILENCE_SEC = 0.0`, `title_pre_roll = False` ni un flag. Los `chXX_visual_preroll.mp4` que queden en `_fase2b_work/` de topics viejos no los debe leer nadie: decirlo en el inventario.

## 7. Etapas (seguidas, sin parar entre una y otra; cada una deja su salida en texto en el reporte)

### Etapa 0 — línea base, sin tocar código
1. Copiar a `lab/hyperframes/f79/antes/`, de `output/123bbb64-9fca-4395-8bf4-57d60e219ef1/`: `GUION_PANTALLA.json` y `.md`; de `_fase2b_work/`: `gfx_plan_ch*.resolved.json`, `gfx_escenas_ch*.json`, `gfx_sfx_ch*.json`, `gfx_critic_rot_ch*.json` y `gfx_ch*.log`.
2. Correr `python fase2b.py 123bbb64-9fca-4395-8bf4-57d60e219ef1 --plan-only` con el código de `210873b`. Copiar los mismos archivos a `lab/hyperframes/f79/0/`.
3. Comparar `0/` contra `antes/`: `duracion_s` (798,266) y, por cap, los eventos (`tipo`, `texto`, `queda`, `t`). Anotar con su valor los chequeos que ya vienen en ✗ en la línea base: no cuentan como falla de F79.
4. Inventario en tabla: cada lugar que lee o escribe `INITIAL_SILENCE_SEC`, `intro_sec`, `intro`, `intro_s`, `title_pre_roll`, `pre_roll`, `prerolls`, `pre_sec` (archivo:línea, qué hace) y si el valor llega (i) al texto de un prompt, (ii) a una clave de caché, (iii) a una imagen que ve un modelo, o (iv) a la clave de un caché de capas o segmentos renderizados.

Aviso: este plan-only borra el `aprobado` del guion de Wittenoom (Omar, 2026-11-03). Es el único guion aprobado que hay en disco. No se restaura: después de F79 ningún guion aprobado antes sirve para render, porque sus tiempos llevan intro y pre-roll.

**PARADA en esta etapa** (reportar y no seguir) solo si: (a) la línea base no reproduce el guion guardado sin haber tocado código; o (b) el inventario muestra que la intro o el pre-roll entran al **texto de un prompt**. Las claves de caché del crítico (§5.4) ya están aceptadas.

### Etapa A1 — sin intro y sin pre-roll (commit propio)
Borrar según §4 y §6 (todo menos el title card del primer cap), con sus tests y el arreglo de `inicio_de_voz`. `--plan-only` de Wittenoom → `lab/hyperframes/f79/a1/`.

**Salida A1 — tabla Etapa 0 / A1 contra este contrato:**

| Qué | Antes | Esperado |
|---|---|---|
| `duracion_s` | 798,266 | 777,766 ± 0,23 |
| `offset` de ch02…ch07 | 69,3 · … | 66,8 · 166,633 · 336,333 · 433,033 · 561,866 · 687,366 (baja 2,5 + 3,0 × (n − 2)) |
| Inicio de voz en el mp4, ch01…ch07 | 2,66 · 72,38 · 175,213 · 347,913 · 447,633 · 579,466 · 707,966 | 0,16 · 66,88 · 166,713 · 336,413 · 433,133 · 561,966 · 687,466, medido ✓ a 1 cuadro (salvo los ✗ que ya traía la línea base) |
| ch01 | title card en 2,5–5,5 s del mp4; voz a 2,66 s | title card en 0,0–3,0 s del mp4; voz a 0,16 s |
| ch02–ch07, costura | negro 1,0 → sube 0,333 → title card 3,0 sin voz → voz a 3,08–3,10 s del cap | negro 1,0 → sube 0,333 → voz a 0,08–0,10 s del cap, con el title card encima 0,0–3,0 s |
| `seg_dur` de ch02–ch07 | — | cada uno 3,0 s menos (± 1 cuadro) |
| Eventos de ch02–ch07 | — | Todo evento con `t` > 0 baja 3,0 s (± 1 cuadro). Quedan en `t` = 0,0: la costura de apertura (su `texto` cambia, describe la costura nueva), el title card y los cortados sin instante (2 sellos: ch04 CALMA, ch05 SILENCIO). |
| Eventos de ch01 | — | `t` igual; `t_mp4` baja 2,5 s; cambia el `texto` de su costura de apertura. |
| Reloj «16 SEP · 1961» (ch02) | 3,08 s, dura 9,55 s | Lo decide `repartir`: corrido a otra oración o fuera. Reportar adónde fue, cuánto dura y el motivo que da el código. |
| Otros bloques movidos o cortados por la reserva del title card | — | Ninguno esperado. Si aparece, se lista con texto y motivo; no se parcha. |
| Chequeo «dos bloques al mismo tiempo» | ✓ | ✓ |
| Golpe del title card, por cap | lo que dé la Etapa 0 | va a 0,05 s / se corrió N ms / descartado, y sobre qué palabra (predicción §5.3) |
| Música, inicio por cap | valores de la Etapa 0 | arranca en el 0,0 del cap; mismo desvío que en la Etapa 0 salvo el corrimiento de tiempo |
| Crítico de pantalla | — | nº de llamadas, US$, y bloques cuyo veredicto cambió respecto de la Etapa 0 |

Toda diferencia de eventos se clasifica: tiempo / reserva del title card / crítico / otra. Las «otra» son las que importan. Nada se corrige en esta tanda.

### Etapa A2 — el primer cap sin title card (commit propio)
`apply_gfx` pasa a `plan_base` el dato de primer cap; ese cap sale con `title_card: None`. `--plan-only` → `lab/hyperframes/f79/a2/`.

**Salida A2 — tabla A1 / A2:** ch01 sin evento `title card` y sin su golpe; `titulo` de ch01 en el guion sigue siendo «La herida que no cerraba» (ahora del skeleton) y el encabezado `## ch01 — …` no queda vacío; `tramos` y el chequeo de música de ch01 no nombran un title card que no existe; ch02–ch07 idénticos a A1 (mismos eventos, mismos `t`); `duracion_s` igual a A1. Si al liberarse los primeros 3 s de ch01 algún bloque se mueve ahí, se lista.

### Etapa B — pausa tras cita (commit propio)
Borrar `tts_tags.py:73-74` y la línea del docstring; tests al día.
Sin llamar a ElevenLabs y sin escribir en `data/scripts/` ni en `output/`: recalcular `narration_tts` de Wittenoom y de Colza con la función de producción (`m01c_editor.narration_tts` → `tts_tags.caps_tts`, con los mismos insumos que usa `m01d_particion`: `01a_escaleta.json`, los párrafos de `01b_narracion_v3.json`, `slowly_dev=False` como en `m01d_particion.py:237`) y guardar el resultado en `lab/hyperframes/f79/b/`.

**Salida B — por topic y por cap, etiquetas antes / después:** `[long pause]` Wittenoom 21 (1, 3, 7, 2, 2, 4, 2) → 7 (1 por cap); Colza 22 (2, 1, 3, 2, 5, 5, 4) → 7; `[short pause]`, `[quietly]`, `[whispers]`, `[slowly]` idénticas cap por cap. md5 de los dos `01b_narration.json` igual antes y después. Si el «antes» recalculado no da 21 y 22, decirlo antes de borrar nada.

Alcance de B: vale para los topics que se partan de F79 en adelante. Los ya partidos (Wittenoom, Colza) conservan su `narration_tts` guardado: `audio_manager.py:619-621` lee ese campo, y regenerarlo cambiaría `md5_narracion` (`m01d_particion.py:36-42`) e invalidaría la aprobación de la narración y el sello del papel. No hay migración.

### Cierre
`DECISIONES.md`: la línea «2026-11-09 · F79» ya está escrita por el analista; marcarla «aplicada F79» y, en l.35, l.76, l.91 y l.94, anotar «anulada por F79» solo en la cláusula que §4 nombra. Mapa de módulos con `--check` en 0. Suite completa. Veredicto del subagente `revisor-handoff`, íntegro, en `lab/hyperframes/f79/F79_REPORT.md`. `lab/ESTADO_SESION.md` al final. **PARADA.**

## 8. Fuera de esta tanda (no tocar)
- Cualquier prompt o texto que lea un modelo del pipeline.
- `title_dur`, negro entre caps, subida desde negro, `HOOK_DURATION`, `sfx_title_card`, las reglas de `pantalla_colocar`.
- El `[long pause]` de cierre de cap y las pausas propias de la voz (0,8–1,2 s por oración según `claude/GUION_QUE_RETIENE_2026-11-09.md` §4): no las pone el código.
- Comprimir silencios después del TTS.
- Regrabar voces, render, QA Studio. De producción solo se reescribe lo que `--plan-only` reescribe solo (`GUION_PANTALLA.*`, `_fase2b_work/` de Wittenoom y `data/cost_history.json`).

## 9. Lo que queda abierto a propósito
- Cuántos segundos ahorra quitar la pausa tras cita: se sabe al grabar la próxima voz.
- El golpe del title card con voz debajo, y cómo se ve el title card junto a los subtítulos: Omar lo decide al verlo y oírlo.
- La voz de cada cap arranca a 0,08–0,10 s, dentro de la subida desde negro (0,333 s): la primera sílaba suena sobre imagen todavía oscura.
- Si la regla que ya existe saca un reloj o una ficha por caer bajo el title card más seguido que en Wittenoom (1 de 29), se revisa con el segundo tema.

## 10. Prompt para CC
```
Modelo: Opus, esfuerzo medio.

Tanda F79 — aire muerto fuera. Rama f11-guion-v4, base 210873b.

Leé ENTERO lab/hyperframes/f79/HANDOFF_F79.md y verificá su md5 contra el que te pasa Omar. Ese archivo manda; esto es solo el orden de trabajo.

Reglas fijas:
- No se toca ningún prompt ni texto que lea un modelo del pipeline. Sin render. Sin llamadas a ElevenLabs. No escribir en data/scripts/ ni en output/ fuera de lo que --plan-only reescribe solo.
- Lo viejo se borra con sus tests; nada de dejarlo en 0, en False o detrás de un flag.
- Ningún número nuevo en el código. Si necesitás uno, PARADA y preguntá.
- Usá subagentes en paralelo en todo lo que se pueda (inventario de la Etapa 0, lectura de módulos, tests).
- Hacé la tanda entera de corrido: 0 → A1 → A2 → B → cierre. No pares entre etapas; cada una deja su salida en texto en el reporte antes de empezar la siguiente.
- Lo que el contrato dice «se lista, no se parcha», se lista.

Orden:
1. Etapa 0 (sin tocar código): copia a lab/hyperframes/f79/antes/, plan-only de Wittenoom (123bbb64-9fca-4395-8bf4-57d60e219ef1) como línea base, comparación e inventario. Parás ahí solo si se da (a) o (b) de la PARADA de esa etapa.
2. Etapa A1: borrar intro y pre-roll, arreglar inicio_de_voz, tests, plan-only, tabla contra el contrato de §7. Commit.
3. Etapa A2: el primer cap sin title card, tests, plan-only, tabla A1/A2. Commit.
4. Etapa B: borrar el [long pause] tras cita, tests, recalcular narration_tts de Wittenoom y Colza en lab/hyperframes/f79/b/, tabla. Commit.
5. Cierre: DECISIONES.md, mapa --check, suite completa, revisor-handoff con su veredicto íntegro en lab/hyperframes/f79/F79_REPORT.md, ESTADO_SESION.md.

PARADA al terminar. No sigas con nada más.
```
