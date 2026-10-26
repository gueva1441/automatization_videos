# F32 — El guion de pantalla: todo lo que se verá, en texto, antes de renderizar · REPORTE

CC · 2026-10-26 · rama `f11-guion-v4`, base `0253672` (F31). Handoff `HANDOFF_F32_guion_de_pantalla.md`. Pedido de Omar: A → B → C, **un commit por parte** (el handoff pedía uno por arreglo en B; mandó Omar). **Ningún render en esta tanda.**
Commits: **A `308032a`** · **B `2fde994`** · **C** = el commit de este reporte.
Costos de la tanda: **Claude US$ 0.2668** de 1 (el rotulista: el prompt cambió una línea, así que no hubo caché) · **Gemini US$ 0.0016** de 0.5 (crítico sobre la foto y visión; 0.0005 en la primera corrida de A, 0.0011 en la de B) · ElevenLabs 0.

**En una línea:** `fase2b --plan-only` escribe el guion de pantalla de Vajont (`GUION_PANTALLA.md/.json`: 200 eventos, 82 de ellos propuestas cortadas) y la mezcla de previsualización en **2 min 42 s** (5 min 2 s la primera vez, con el rotulista llamando a Claude), sin navegador ni render. Los 8 arreglos de B están en el código; en Vajont quedan **2 textos en pantalla** (D128, D245), `a_pantalla` 2/5, 10 sellos, preguntas de cierre con lectura 7/7 e inicio de voz con rampa 6/7. Un hallazgo cambia el diagnóstico de B.1: **la voz de v5 no perdía el ataque**.

## Decisiones de Omar aplicadas como «voto del analista» (§0)
1. **2 `a_pantalla` en el mismo beat si van en escenas distintas**: aplicado (`gfx_rotulista.finalizar`, `A_PANTALLA_POR_BEAT = 2`; la segunda ficha espera otra escena del beat en `escena_final`).
2. **Texto en el beat pico: solo `a_pantalla`**: aplicado (lo demás, 0).
3. **Pre-roll del title card de 3 s; ch01 sin pre-roll; la música del cap arranca con el title card**: aplicadas las tres.

## A — El guion de pantalla (`308032a`)
| archivo | qué |
|---|---|
| `script_engine/gfx_guion.py` (nuevo) | eventos (§A.1) en el tiempo del mp4: intro 2.5 s + offset del cap (los segmentos, redondeados a cuadro como el `-t` del render) + tiempo del plan (con el pre-roll). Tipos: title card, ficha, persona, recorte, cita, lupa, sello, reloj, nivel de agua, contador, punch, pregunta de cierre, transición (tipo, razón, escena saliente → entrante), costura (negro → corte → sube desde negro → title card → voz, con los segundos), silencio de voz. Cada línea: `mm:ss · chNN · beat (función) · tipo · «etiqueta \| texto» · dura (lectura mínima) · escena (de a) · voz −1 / ancla / +1 · aporta · fuente · filtro`. Lo propuesto y cortado sale con `✂` y «cortó *quién*: *por qué*» (rotulista por regla, zona, catálogo de sellos, realizador, crítico, candado). Resumen por beat (§A.2) con `⚠ BEAT VACÍO` y `⚠ CAP SIN TEXTO`. 8 chequeos (§A.3). Salida `.md` y `.json` (la misma información) |
| `fase2b.py` | `--plan-only` (implica `--gfx --reuse-visuals`; los visuales base tienen que estar cocidos): prefetch de director y rotulista como siempre → re-codificación -g30 de los 7 caps **en paralelo** (7 hilos) → plan de cada cap **en fila** (cada cap lee lo que ya mostraron los anteriores) → mezcla → guion. `--plan-edit archivo.json`: suma las ediciones a `_fase2b_work/plan_edits.json` y regenera el guion (el rotulista sale de caché). `_mezcla_preview` (§A.4): voz + sfx por cap con el mismo grafo del segmento, unidos sin solapar (como el corte a negro), y la música por el mismo camino del render; el grafo de la mezcla con música quedó en un solo lugar (`_grafo_musica`, el render usa el mismo texto) |
| `script_engine/gfx_layer.py` | `apply_gfx(plan_only=True)`: sin `hyperframes doctor`, sin re-codificar el base para la pausa (la duración se suma), sin proponer léxico (`record_proposals`, como las simulaciones de F5), `reencoded=True` para no re-codificar dos veces; escribe `gfx_escenas_chNN.json` (escenas y duración del cap) en los dos caminos; aplica las ediciones a mano |
| `script_engine/gfx_rotulista.py` | ediciones (§A.5): `texto`, `etiqueta`, `word_idx`, `sentence_idx`, `tipo`, `aporta`, `borrar`, `agregar` (sobre una copia de la respuesta: la caché no se toca; el bloque editado pasa por todas las reglas) y `escena` (arranca en el corte de la escena k) |
| `script_engine/gfx_vision.py` | la caché compartida de visión con candado (re-lee y suma bajo el candado) |

**Tests sin red (§A.6)**, `test_module_f32.py`: guion de un cap de fixture con todos los tipos · beat vacío marcado · cap sin texto marcado · silencio contra la pausa más larga del guion · inicio de voz **sin rampa con el audio de v5 ch01** (fixture `lab/hyperframes/f32/fixtures/v5_mezcla_0a10s.wav`: `✗ … medida 5.62 s · llega a −18 dB en 5.66 s sin rampa (100 ms previos: −34.7 dB …)`) · **con rampa con el de v3b** · corrido 0.2 s falla por tiempo · `--plan-edit` cambia una etiqueta y el guion lo refleja (más borrar, agregar y escena). Suite amplia **983 + 5 previas**, rápida 58, md5 `--only-cap ch02` sin `--gfx` (`--sw-encode`) **`38e5ba14…`** (`a/`).

Línea de base (Vajont en el estado de v5, con el código de A): `a/GUION_PANTALLA_A.md/.json`, 159 s, US$ 0.

### Ejemplo: el cap ch06 entero, tal como sale en `GUION_PANTALLA.md`
(Las transiciones `cut` también son líneas; los `✂` son propuestas cortadas.)

