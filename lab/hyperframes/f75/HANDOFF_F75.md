# HANDOFF F75 — personaje medido por la narración · segundos entre promesas nuevas · master −14 LUFS
Fecha: 2026-11-04 · Analista → CC · Rama `f11-guion-v4` (HEAD `63ff8af`) · `main` no se toca.
Decisión de Omar 2026-11-04 14:49 («dale a eso»): arreglar el bug del personaje y la métrica de re-gancho antes del tema 2 (Palomares), en la misma tanda que el master −14 LUFS + limitador (DECISIONES línea 237).
Origen: `claude/MEJORAS_GUION.md` puntos 2 y 4.

## 0. Antes de escribir (método)
- ¿Construye sobre algo que se va a reemplazar? No: m05 `retencion` (F67 A), m01f (F67) y la mezcla de fase2b siguen vigentes.
- ¿Una decisión de hoy cambia el orden? No. Palomares corre fase 1 en paralelo; F75 solo tiene que estar antes de su juez (A, B) y antes de su render (C).
- **La simulación cambió la métrica de B:** «segundos sin promesa abierta» no discrimina en Wittenoom: el loop de los relaves (ch01:11 → ch06:19) tapa casi todo el video y solo quedan 2 huecos de 6 s y 9 s. Lo que sí coincide con el valle que vio el crítico es **cuánto pasa entre una promesa NUEVA y la siguiente** (139 / 150 / 182 s). Esa es la métrica que va.

## 1. Constantes
| valor | qué es | origen | quién |
|---|---|---|---|
| seg/palabra | segundos estimados por palabra antes de la voz | ya existe: `retencion.seg_por_palabra` de las métricas que vio el crítico (sale de `m01e_pantalla.velocidad()`, mediana de las voces generadas; Wittenoom 0,34; hoy daría 0,337). Nunca se vuelve a llamar a `velocidad()` en B | proyecto |
| −14 LUFS integrados | nivel del master final | DECISIONES 2026-11-04 (línea 237) | Omar |
| −2 dBFS (muestra) | techo del limitador antes de loudnorm | derivado: margen para picos entre muestras que agrega el AAC, para que el pico real final quede ≤ −1,5 | analista (técnico) |
| −1,5 dBTP | techo de pico real del master | ya existe en el proyecto: `audio_manager.py:463` (`loudnorm … TP=-1.5`) | proyecto |
| LRA | rango de sonoridad del master | derivado: el medido en la 1.ª pasada de la mezcla (no se fija) | material |
| 60 s | largo de cada extracto para que Omar escuche (solo lab, no producción) | analista, para el lab; no entra al código de producción | analista |
| — | umbral de segundos entre promesas | **ninguno**: se reporta el número, igual que el resto de `retencion` («sin umbral», F67 A 2026-10-31 18:43). La referencia 90–180 s (blog sin metodología) no entra al código | — |

## 2. Módulos que toca
1. `script_engine/m05_narrative.py` (juez m05, métricas de retención): hoy toma el personaje de `escaleta.humano.id`; después lo elige de la narración (A).
2. `script_engine/m01f_critico.py` (crítico de retención): hoy imprime los loops como texto; después además calcula «segundos entre promesas nuevas» a partir de `loops[*].abre` y lo pone en el JSON y en el `.md` (B). La línea «Personaje según la escaleta» pasa a «Personaje según la narración».
3. `script_engine/m01f_prompts/SYSTEM.txt`: **una sola sustitución** en el punto 2 (A3). No se agrega ninguna regla.
5. `qa_studio_server.py` + `qa_studio.html` (pestaña NARRACIÓN): hoy dice «Personaje según la escaleta» (`qa_studio.html:1210`) y no muestra `validacion`; después dice «según la narración» + oraciones, y muestra una línea con `entre_promesas` junto a «loops» (el dict `critico` de `qa_studio_server.py:2362` suma `validacion.entre_promesas`).
4. `fase2b.py` (ensamble): hoy el mp4 final sale con la mezcla a −24 LUFS; después pasa por un master −14 LUFS / −1,5 dBTP (C).
Tests de cada uno. Nada más. (Son 5 módulos: A+B tocan juez/crítico/QA, C toca solo fase2b; se miden por separado.)

## Etapa A — el personaje sale de la narración (bug de `metricas.personaje`)
**Por qué:** en Wittenoom la escaleta escribió `humano.id = P16` (María Bernal) con el rol de Daniel («Minero emigrante español, esposo de María Bernal»). m05 confía en el id: todas las rachas «sin personaje» se midieron con María, y el crítico tuvo que recalcularlas a mano. Además `nombres.terminos` no busca el nombre de pila solo: la narración dice «Daniel» 16 veces y «Daniel Écija» 6 veces, así que aunque eligiera bien contaría 6.
**Causa más arriba (no se arregla acá, va a «se arregla si se repite»):** el pool fusionó padre e hijo en `P17 «Daniel Écija (padre)»` con rol de hijo, y la escaleta no tiene chequeo de que su `id` corresponda a su `rol`.

A1. En `m05_narrative.py` se **reemplaza** `_persona_de(skeleton, escaleta)` por una elección desde la narración:
- Candidatos: `pool.personajes` con `nombres.es_persona(nombre)` (el pool no trae `tipo`: el filtro por `tipo` no hace nada).
- Términos para buscar a cada uno en la voz (solo para retención): los de `nombres.terminos` **que tengan nombre y apellido** («daniel ecija»), más el **nombre de pila solo** si ningún otro del pool comparte ese nombre de pila **y solo cuando aparece con mayúscula inicial en el texto original de la oración** (no sobre `norm`): así «el inspector de minas» no cuenta para «Inspector de Salud Regional», ni subcomité/junta/sir/prime/mines/state. El apellido solo **no** se usa para elegir, porque «Subcomité de Wittenoom» tiene «wittenoom» como «apellido» y saldría en 11 oraciones. Esta función de términos es nueva y la usa solo `retencion`; `nombres.terminos` no cambia (la usan research_v3, guion_v3_reglas, evidence y ficha_caso).
- Gana quien aparece en más oraciones de la narración que se juzga. Empate → el de `escaleta.humano.id` **si está entre los empatados**; si no está o no hay escaleta → el de la primera oración (índice global) donde aparece (el que el espectador conoce primero). Nadie nombrado → `personaje: null` con motivo «nadie del pool se nombra en la voz».
- Las rachas y `oraciones_con_personaje` se cuentan con esos mismos términos.
- `escaleta.humano` deja de ser la fuente; se borran el camino viejo y sus tests (no se deja apagado por flag).
- Campo nuevo en `retencion.personaje`: `"elegido_por": "narracion"` y `"oraciones": <n>`; `"escaleta_id"` con lo que decía la escaleta, solo informativo. `terminos` = los términos nuevos de retención (los que cuentan rachas), no `nombres.terminos`. `retencion()` deja de usar `skeleton.personajes` (el skeleton queda solo para títulos).
- Tests que hoy afirman lo viejo y se reemplazan: `tests/test_m05_retencion.py:97-109` (parametrize skeleton/institución/sin humano) → «nadie nombrado → null», «empate → escaleta», «empate sin escaleta → primero», «pila compartido no cuenta», «el inspector con minúscula no cuenta»; `tests/test_m05_retencion.py:112` (igualdad exacta de `personaje`, ahora con los campos nuevos); `tests/test_m01f_compuerta.py:152` («Personaje según la escaleta…» → «según la narración»).

A2. **Simulación del analista sobre Wittenoom** (narración `01b_narration_normalized.json`, 139 oraciones, `oraciones_de_texto`), contrato de A:
| candidato | términos | oraciones |
|---|---|---|
| P17 Daniel Écija (padre) | daniel ecija, daniel | **16 → gana** |
| P16 María Bernal | maria bernal, maria | 7 |
| P21 Víctor Calvo | victor calvo, victor | 3 |
| P20 Ramón de Juan | ramon juan, ramon | 3 |

Rachas con Daniel (contrato): ch01 14 or./1 con/racha 7 · ch02 18/1/16 · ch03 25/3/10 · ch04 19/2/12 · ch05 23/6/8 · ch06 25/2/12 · ch07 15/1/10.
Límite conocido, no se arregla: «el hombre», «ese hombre» y los pronombres no cuentan (por eso ch01 da 1 con).

A3. `SYSTEM.txt` punto 2, sustitución exacta:
- Ubicación: `SYSTEM.txt:7` (aparece una sola vez).
- Antes: `2. Hilo humano: el personaje del video es el de \`escaleta_video\` y de los beats con \`humano_en_escena\`.`
- Después: `2. Hilo humano: el personaje del video es \`metricas.personaje\` (lo elige el código: la persona del archivo más nombrada en la narración); los beats con \`humano_en_escena\` dicen dónde la escaleta lo quería en escena; si \`escaleta_video.humano\` dice otro, manda \`metricas.personaje\`; si es null, decilo.`
- El resto del punto 2 queda igual. `PROMPT_VERSION` (`m01f_critico.py:24`) pasa a `m01f-2`; docstring `m01f_critico.py:8` al día. El candado del SYSTEM (`tests/test_m01f_compuerta.py:93-96`, hoy contra `lab/hyperframes/f67/a/md5.json` y el bloque §4 de `HANDOFF_F67a`) pasa a `lab/hyperframes/f75/a/md5.json` + el SYSTEM completo nuevo copiado en `lab/hyperframes/f75/a/SYSTEM_m01f-2.txt`; el test se actualiza a eso.

**Salida de A (texto):** `retencion.personaje` y la tabla de rachas de Wittenoom recalculadas llamando a `retencion()` directo con los archivos del disco (sin LLM, US$ 0). Tiene que dar la tabla de A2. Si no da, PARADA y explicar la diferencia.

## Etapa B — segundos entre promesas nuevas (métrica en código, sin umbral)
**Por qué:** los canales que retienen meten una promesa nueva cada pocos minutos. En Wittenoom el crítico vio el valle después de ch05, pero el número no estaba en ninguna parte. El dato ya existe: el crítico devuelve `loops[*].abre` (`chNN:idx`). No se toca el formato del crítico.

B1. En `m01f_critico.py`, después de validar la respuesta:
- Ubicar cada `abre` en la narración (mismo corte e `idx` por cap que `entrada.caps`). Segundo de `chNN:idx` = palabras de todas las oraciones anteriores (todo el video, en orden) × `metricas["seg_por_palabra"]`; tramo = round(diferencia); dos loops que abren en la misma oración = una sola apertura. El cálculo va en `generar()` (o `validar` recibe `seg` explícito): `validar(resp, e)` hoy no lo tiene.
- Si `narracion_md5` del crítico ≠ md5 de la narración actual, el `.md` lleva «⚠ calculado sobre la narración actual, no la que vio el crítico».
- `entre_promesas`: lista de tramos entre aperturas consecutivas (ordenadas por posición) y el último tramo hasta el fin; cada tramo `{desde: "chNN:idx", hasta: "chNN:idx" | "fin", segundos, pregunta_que_abre}`. Más `max_segundos` y en qué tramo cae.
- Un `abre` que no existe en la narración va a `loops_invalidos` (como `oraciones_invalidas` de los DEBERÍA) y no entra a la cuenta. Se reporta, no falla.
- Va en `01f_critico.json` (`validacion.entre_promesas`) y en el `.md` como sección «## Promesas nuevas (código)» con una tabla. En el QA: módulo 5 (una línea junto a «loops»).
- Esto no reemplaza nada porque es una métrica nueva sin umbral. No decide nada: lo lee Omar en la pestaña NARRACIÓN y el crítico lo ve en la próxima corrida (no se agrega como entrada del prompt en esta tanda).

B2. **Simulación del analista sobre Wittenoom** (`01f_critico.json`, 7 loops), contrato de B. Narración del cálculo: la de disco `cd0fe3bf…` (≠ `3fc4168d…` que vio el crítico: los DEBERÍA 2 y 4 se aplicaron después y no tocan ningún `abre`; sobre la vieja daría 153 y 179). seg = 0,34 de `06_judge_narrative.json`. Los segundos son estimados por palabra (605 s de voz sin pausas ni title cards; el mp4 real dura 798 s):
| desde (abre) | hasta | s |
|---|---|---|
| ch01:2 | ch01:5 | 21 |
| ch01:5 | ch01:11 | 24 |
| ch01:11 | ch01:12 | 2 |
| ch01:12 | ch03:11 | 139 |
| ch03:11 | ch04:18 | 150 |
| ch04:18 | ch06:20 | **182 (máx.)** |
| ch06:20 | fin | 81 |
Re-generar el `.md` de Wittenoom desde el JSON que ya existe, **sin llamar a la API** (US$ 0), con una función nueva `critica_md(resp, val, metricas, cab)` (hoy no existe re-render desde el JSON), a `lab/hyperframes/f75/b/01f_critico.md` **sin pisar** el de `_steps`. `metricas` = la `retencion()` nueva de A (si no, imprime María). Tiene que dar esta tabla y la línea ⚠.

**Salida de B (texto):** la sección nueva del `.md` de Wittenoom pegada en el reporte.

## Etapa C — master −14 LUFS / −1,5 dBTP
**Por qué:** YouTube normaliza a ~−14 LUFS. Wittenoom salió a −24,0 LUFS (medido por el analista con `ebur128` sobre `_final_gfx.mp4`: I −24,0, LRA 6,6, pico real −6,6 dBFS). Se escucha 10 dB más bajo que los otros videos y YouTube no lo sube. Para llegar a −14 hacen falta +10 dB, y el pico quedaría en +3,4: por eso hace falta el limitador.
**No se toca:** `AUDIO_STYLE["voice_lufs_v4"]` = −24 ni la mezcla voz/música. La música está calibrada contra la voz a −24 (`audio_profiles.py:21-23`). El master es un paso nuevo al final, sobre la mezcla terminada.

C0. **Solo lectura, PARADA corta dentro de la etapa.** El audio del mp4 final tiene 3 caminos (auditado): (a) `_mix_music_audio_only` (AAC :2169-2171 + remux `-c copy`, si existen `_concat_video.ts` y `_concat_audio.wav`); (b) `_mix_music_into_video` re-encode (:2028/:2069), respaldo de (a); (c) sin `music_map`, sale directo de `_concat_segments` (:3529). **No** es candidato `_mezcla_preview` (:2982-3060, previsualización de `--plan-only`). Lugar esperado del master: `fase2b.py:3657`, después de (a)/(b)/(c) y antes de `final_dur = _get_duration(final_path)`, como pasada sobre `final_path` con `-c:v copy`. Confirmar que nada posterior re-escribe el audio (`main` → `mark_as_generated`, fase3). `_final_no_music.mp4` (:3543) y `mezcla_preview.wav` quedan pre-master a −24 LUFS: decirlo en el reporte (el analista lo acepta: no se publican). Si el lugar no es común a los tres, PARADA.

C1. **Lab sin render (US$ 0):** extraer el audio de `output/123bbb64-…/<tid>_final_gfx.mp4` y aplicar el master así: G = −14 − I_medido (derivado). Cadena: `volume=+G dB, alimiter=level=disabled:limit=<−2 dBFS de muestra>` → **medir esa señal ya limitada** con `loudnorm=print_format=json` → 2.ª pasada `volume, alimiter (igual), loudnorm=I=-14:TP=-1.5:LRA=<mismo string que measured_LRA>:linear=true:measured_I/TP/LRA/thresh:offset` con `-ar 48000` (en dinámico loudnorm sube a 192 kHz). Leer `normalization_type` del JSON de la 2.ª pasada y decir si quedó `linear` o `dynamic`. El −2 dBFS del limitador es margen técnico derivado (pico de muestra vs. pico real tras el AAC), va al perfil con ese origen. El pico real se mide **sobre el archivo final codificado (AAC)**, no sobre el wav. Medir con `ebur128=peak=true` antes y después: I, LRA, pico real. Sacar 2 extractos de 60 s (0:00–1:00, gancho; y el minuto más fuerte según la medición) del original y del master, a `lab/hyperframes/f75/c/`. **No se toca el mp4 publicado.**

C2. Cablear el master en el lugar de C0, con las constantes de la tabla (sin números sueltos en el código: van en el perfil de audio con su comentario de origen).

**Salida de C (texto):** tabla antes/después (I, LRA, pico real, modo lineal o dinámico) + rutas de los 4 extractos. **PARADA: Omar escucha los extractos antes de que el master corra en el render de Palomares.**

## Reglas fijas
- Subagentes en paralelo donde se pueda (A y B son independientes; C0/C1 también).
- Ninguna llamada a API en toda la tanda: US$ 0 esperado. Si algo necesita API, PARADA.
- No escribir en `output/` salvo `lab/`. No re-renderizar Wittenoom.
- Lo viejo se borra con sus tests (A1). Suite rápida verde, más las 3 fallas heredadas.
- `DECISIONES.md`: anotar con fecha A1 (el personaje sale de la narración), B1 (métrica sin umbral), C (−14 LUFS, −1,5 dBTP del proyecto, LRA medido).
- Reporte `lab/hyperframes/f75/F75_REPORT.md` con la salida en texto de cada etapa, la sección «abierto» completa y el veredicto íntegro del `revisor-handoff`. Actualizar `ESTADO_SESION.md`. Commit y push en la rama.
- PARADA al final.

## Abierto que este handoff deja anotado (se arregla si se repite)
- El pool fusiona homónimos padre/hijo (P17 de Wittenoom).
- La escaleta no comprueba que `humano.id` corresponda a su `rol`.
- Las rachas no cuentan «el hombre», «ese hombre» ni pronombres.
- Personaje con partícula («Ramón de Juan» → término «ramon juan» nunca coincide): si comparte nombre de pila con otro del pool, queda imposible de encontrar.
