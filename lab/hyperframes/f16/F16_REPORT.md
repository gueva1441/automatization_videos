# F16 — Escaleta v2: 13 bloqueantes, oficio, Sol · Ycuá y Orleans completos — REPORTE → PARADA

CC · 2026-10-23 · rama `f11-guion-v4` (desde `fa1d02b`). Handoff: `HANDOFF_F16_escaleta_v2.md`. Ficha → escaleta → guion.

**En una línea:** con la escaleta v2 (prompt literal del analista, Sol high, solo 13 bloqueantes), **Ycuá y Orleans salieron completos**, cada uno con una sola regeneración. En los dos temas, la escaleta:
- eligió un humano candidato de la ficha;
- usó el pico de la ficha, con su escena en el gancho (marcado flash-forward) y en el pico;
- usó 8 escenas y los 6 giros.

Los guiones v5.1 duran **11.3 min (Ycuá, 1,384 palabras)** y **11.7 min (Orleans, 1,443)**, con 0 bloqueantes.

**Para llegar ahí hubo un primer pase que terminó en PARADA en los dos temas.** Sol escribía en `dato_central` el id seguido de una explicación («Q19: Liz siente una avalancha…»), como en el ejemplo del prompt. Le pregunté a Omar y eligió **leer el id del texto** (`ids_v2`), sin tocar los 13 bloqueantes ni la regla de una sola regeneración. Costo: **US$ 1.359** de 2.00.

Para leer:
- `compara_f16.html`: la escaleta y el guion de F15b al lado de los de F16. Se lee en el teléfono.
- `ESCALETA_{ycua,orleans}_f16.md`.
- `NARRACION_{ycua,orleans}_f16.md`.

## 1. md5 del prompt contra el archivo

| archivo del analista | md5 del archivo | lo que se usa | md5 de lo que se manda |
|---|---|---|---|
| `lab/hyperframes/f16/PROMPT_ESCALETA_v2.md` | `8d57328891732e3e5ee147dc124161d7` | bloque SISTEMA (desde «## SISTEMA», de `<rol>` a `</errores>`) = `m01a_escaleta.SYSTEM_V2`; `<tarea>` del bloque USUARIO = `TAREA_V2` | sistema **`49ed74d941def064cdda077212629ff1`** (5,769 caracteres), igual en los dos temas |

- `test_module_f16.py` lee el `.md` (en LF) y compara byte a byte.
- **Usuario:** `<caso>` (título, ángulo, misterio, revelación) · `<ficha>` (en este orden: historia, escenas, personas, personas descartadas, cronología, hechos nivel 1, hechos nivel 2, cifras, citas, versiones en disputa) · `<tarea>` literal.
- Sin `escaleta_notas`, sin FEWSHOT, sin `rules_text`. El feedback solo existe en la única regeneración, como bloque `<rechazo>` antes de la tarea. `PROMPT_VERSION_V2 = "f16-1"`.
- **Sin ficha, todo es byte-idéntico:** los md5 del prompt de HEAD en los dos temas (Orleans `379d8405…`, Ycuá `f17b1b25…`, con y sin feedback) y `RULES` coinciden. El camino sin ficha sigue con `SYSTEM`, `SCHEMA` y `validate` completos (test).
- La escaleta v2 corre solo con la ficha v2 (la que trae `historia`). Con la ficha de F14, el camino es el de siempre.

## 2. Lo que se implementó

- **Modelo:** la escaleta con ficha v2 usa `gpt-6.1-sol` high por `guion_v4.call_for` (test). El esquema es el contrato de hoy (`SCHEMA_FICHA`: los campos de siempre más `escena_idx` y `justificacion_humano`; `flash_forward` ya estaba).
- **Los 13 bloqueantes** (`m01a_escaleta.bloqueantes`): son los chequeos de `validate`, **tal cual**. `bloqueantes` corre `validate` y se queda solo con los mensajes de los 13 (`BLOQUEANTES_V2`, por patrón de mensaje); lo demás va a `metricas_escaleta`. No se agregó ninguno. De los 13:
  - 9 rechazan con su mensaje de siempre: beats entre 7 y 14; caps 1–7 en orden; beat 1 = gancho; el dato central existe; el pico es un beat; el pico no es el último; el humano es una persona; el antagonista es una persona; `a_pantalla` no repite un id de un beat;
  - 2 rechazan y además reparan, como siempre: un id en un solo beat (dato central repetido → rechazo; apoyo repetido → sale) y otra cifra del mismo conteo (dato central → rechazo; apoyo → sale);
  - 2 eran y siguen siendo solo reparaciones: el nombre exacto del humano y la cita sin verificar fuera de `a_pantalla`;
  - más la precondición de siempre: cap e intensidad tienen que ser numéricos, porque sin eso `validate` corta antes del resto.
- **Una sola regeneración** con los bloqueantes como feedback; si vuelve a fallar, `EscaletaValidationError` (PARADA). Test.
- **Métricas** (`_metricas` en la escaleta; no rechazan):
  - curva de intensidad y flash-forward;
  - el humano en escena (caps, cap de entrada, con una cita suya sin verificar);
  - promesa e imagen del gancho con cifras; imágenes abstractas;
  - escenas usadas (gancho y pico); giros con beat; humano entre los candidatos; pico igual al de la ficha;
  - palabras objetivo por cap; cifra en pantalla repetida; última frase que repite una cita; última frase sin humano;
  - preguntas de pantalla, y el resto de lo que `validate` marcaba como duro.
  - «Preguntas abiertas retóricas» no tiene un cálculo determinista: se listan para leer.
- **Sin `instrucciones_guionista` con ficha v2:** `apply_pool_plan(instrucciones=False)`. Sin ficha, igual que antes (test).
- **`ids_v2`** (agregado después del primer pase, por decisión de Omar):
  - lee el id del texto: el primer D/T/Q de `dato_central`, todos los D/T/Q de cada apoyo, y el id de `a_pantalla`, del pico, del humano y del antagonista;
  - anota cada lectura como reparación («id leído de «Q19: …» → Q19»);
  - no rechaza nada: si no hay id, el texto sigue y lo rechaza el bloqueante «el dato central existe» (test).
- **Tests:** `test_module_f16.py` (22, sin red).
  - Sistema v2 byte-idéntico; la forma del usuario.
  - Sin ficha, byte-idéntico y por el camino viejo.
  - Los 13 bloqueantes (un caso cada uno, sobre los fixtures de `test_module_f6b`), incluidas las reparaciones que no rechazan.
  - Lo demás de `validate` no rechaza; una sola regeneración y PARADA; regeneración que pasa sin instrucciones y con métricas.
  - Sol high por defecto; `ids_v2`.
  - **Suite amplia: 650 verdes + las 5 fallas previas** (3 `01b_pauses`, 2 `m03_merge_timing`), con `ids_v2` y su test. `test_v3_byte_identico`, verde.

## 3. Por tema: escaleta

### Ycuá

| | F15b (escaleta F15, Pro, todas las reglas) | **F16 (escaleta v2, Sol, 13 bloqueantes)** |
|---|---|---|
| beats (por cap) | 13 (1 · 2 · 2 · 2 · 2 · 2 · 2) | 14 (1 · 2 · 2 · 2 · 1 · 3 · 3) |
| humano | Liz Torres (candidata) | **Liz Torres (candidata)** |
| pico | beat 8 · Q20 (el de la ficha) | **beat 8 · Q20 (el de la ficha)** |
| curva | 5 2 3 3 4 4 5 5 1 3 3 2 2 | **4 1 1 3 4 4 4 5 2 2 3 3 3 3** (flash-forward) |
| escenas | ninguna | **E2, E3, E5, E7, E8, E9, E10, E12 · gancho E8 · pico E8** |
| giros de la ficha con beat | 6 de 6 | **6 de 6** (beats 5, 6, 9, 10, 11, 14) |
| bloqueantes | 0 | 0 (intento 1: 11 → regeneración: 0) |

**Métricas que antes rechazaban y ahora solo se ven (F16 Ycuá):**
- «falta un beat de intensidad 1 (respiro) después del pico» (el respiro es de intensidad 2);
- «caps de desarrollo con menos de 2 beats: [5]»;
- la humana en escena en el beat 8 con una cita suya sin verificar (Q20; el oficio 12 del prompt lo permite);
- la última frase «no nombra al humano ni a un testigo verificado» y «repite textual la cita Q77»: la escaleta cierra con la cita de Liz, que el oficio 9 pide;
- 7 preguntas de pantalla con observaciones de la rúbrica.

### Orleans

| | F15b (escaleta F15b, Pro) | **F16 (escaleta v2, Sol)** |
|---|---|---|
| beats (por cap) | 13 (1 · 2 · 2 · 2 · 3 · 2 · 1) | 14 (1 · 1 · 3 · 4 · 1 · 2 · 2) |
| humano | Edward «Edgar» Burton (candidato) | **Joyce Gilson (candidata; 0 citas verificadas según la ficha)** |
| pico | beat 8 · D155 (el de la ficha) | **beat 10 · D155 (el de la ficha)** |
| curva | 3 2 3 3 4 4 4 5 1 2 3 4 2 | **4 1 2 3 3 4 4 4 4 5 2 3 3 3** (flash-forward) |
| escenas | E9, E11 · gancho: no · pico E9 | **E1, E3, E6, E8, E9, E11, E12, E15 · gancho E9 · pico E9** |
| giros con beat | 5 de 6 | **6 de 6** (beats 3, 4, 5, 7, 9, 13) |
| bloqueantes | 0 | 0 (intento 1: 17 → regeneración: 0) |

- **Métricas (F16 Orleans):**
  - «falta un respiro de intensidad 1 después del pico»;
  - «caps de desarrollo con menos de 2 beats: [2, 5]»;
  - «la imagen sensorial del gancho no lleva cifras» (la imagen lleva una cifra);
  - la última frase no nombra a un testigo verificado: cierra con la pregunta final de la ficha;
  - 7 observaciones de preguntas de pantalla.
- **El humano sigue cambiando:** Reed → Pearl → Richard → Burton → **Gilson**. La v2 elige entre los candidatos, pero no siempre el mismo. El oficio 1 dice «más momentos concretos y más citas verificadas», y Gilson tiene 0 citas verificadas según la ficha.

### Reparaciones de las escaletas F16

- Ycuá: 70. Orleans: 73.
- La mayoría son lecturas de id de `ids_v2`: 14 + 38 apoyos en Ycuá y 14 + 45 en Orleans.
- Solo se cayeron 4 apoyos que eran personas (P##), no datos: P80, P01 y P70 en Ycuá; P64 en Orleans.
- `a_pantalla`: se sacaron los que llenaban un cap (más de 2), como siempre.

## 4. Guion F15b | F16

| tema | versión | palabras | min | párrafos | frases por párrafo | párrafos de 1 frase | bloq. | duras v3 | citas | preguntas | cierre |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Ycuá | F15b (escaleta F15 + v5.1, sustituto) | 858 | 7.0 | 20 | 4.0 | 3 | 0 | 32 | 9 | 0 | cita |
| Ycuá | **F16** | **1,384** | **11.3** | 25 | **4.0** | 2 | **0** | 40 | 9 | 0 | cita (Q77, la de Liz) |
| Orleans | F15b | 867 | 7.0 | 19 | 3.9 | 3 | 0 | 31 | 6 | 0 | cita |
| Orleans | **F16** | **1,443** | **11.7** | 30 | **3.8** | 1 | **0** | 44 | 7 | 1 | pregunta (la de la ficha) |

- **Palabras por cap:**
  - Ycuá F16: 94 · 129 · 295 · 177 · 46 · 340 · 303 (el cap 5 es el pico, con un solo beat);
  - Orleans F16: 92 · 117 · 373 · 375 · 61 · 183 · 242.
- **Embudo** (pool → ficha → escaleta → guion):
  - Ycuá: 509 → 319 → **63** → 12 (F15b: → 46 → 11);
  - Orleans: 1,033 → 366 → **71** → 10 (F15b: → 51 → 10).
- **Ganchos:**
  - Ycuá: «Los cuerpos empujan hacia adentro y una mujer ya no puede avanzar hacia la salida. Ese acceso terminará discutido en un juicio…»;
  - Orleans: «Una mujer no consigue mantenerse erguida dentro del agua. Salir de las celdas inundadas no bastará para estar a salvo…».
- Las duras v3 (métrica del v3, no bloqueante) suben con el largo: incluyen las de largo de cap del v3 y las reglas de cifras y nombres por cap.
- «Humano por nombre en N caps» da [1] en los guiones F16. Es una limitación de la métrica: busca el apellido, y el v5.1 dice «Liz» o «Joyce». No es que la humana falte.

## 5. Costo y tokens

| tema · etapa | modelo | intentos | entrada | salida | razonamiento | US$ | resultado |
|---|---|---|---|---|---|---|---|
| Ycuá · escaleta, pase 1 (sin `ids_v2`) | gpt-6.1-sol high | 2 | 16,127 / 17,316 | 5,993 / 5,267 | 3,817 / 3,584 | 0.2535 | PARADA (el id con una explicación; después, `a_pantalla` repetidos) |
| Orleans · escaleta, pase 1 | gpt-6.1-sol high | 2 | 14,304 / 15,347 | 6,253 / 4,932 | 5,285 / 2,711 | 0.2511 | PARADA (lo mismo) |
| Ycuá · escaleta, pase 2 (frenada por la reserva) | — | 0 | — | — | — | 0.0000 | el freno cortó antes de llamar (reserva demasiado alta con dos temas) |
| Orleans · escaleta, pase 2 (con `ids_v2`) | gpt-6.1-sol high | 2 | 14,304 / 14,873 | 6,850 / 6,198 | 6,658 / 4,608 | 0.3015 | aceptada en la regeneración |
| Orleans · guion v5.1 | gpt-6.1-sol high | 1 | 7,476 | 2,588 | 7,678 | 0.1176 | 1,443 palabras |
| Ycuá · escaleta, pase 2 (con `ids_v2`) | gpt-6.1-sol high | 2 | 16,127 / 16,474 | 6,237 / 6,284 | 5,632 / 5,122 | 0.2980 | aceptada en la regeneración |
| Ycuá · guion v5.1 | gpt-6.1-sol high | 1 | 7,043 | 2,487 | 9,846 | 0.1374 | 1,384 palabras |
| **tanda F16** | | | | | | **1.3591** (tope 2.00) | |

- Las md5 de los usuarios están en `prompt_<tema>_f16_{escaleta,guion}.txt`.
- El sistema del guion es el v5.1 (`cdce609a…`).

## 6. Frenos

- No se tocaron el pool (md5 verificados), `research_v3`, `m05`, `evidence.py`, `guion_v3_reglas.py`, `config.py`, `topics_db`, `m03*` ni `gfx_*`.
- **Cero reglas nuevas:** los 13 bloqueantes son mensajes de `validate`, sin cambios; lo demás pasó de rechazar a métrica. `ids_v2` lee el formato de la salida y no rechaza nada.
- Las escaletas anteriores no se pisaron: las nuevas son `01a_escaleta_f16.json`.
- La ficha que se usó es la v2 re-chequeada de F15b, la que ya estaba en `_steps`; no se rehízo.
- Sin merge. `.env` y `lab/_gpt_probe_analista/` no se commitean. Sin producción.

## 7. Veredicto del revisor-handoff (íntegro)

Notas de CC, después del veredicto:
- **#12 (lo que el revisor no verificó):** comprobé `data/scripts/_steps/`.
  - Las escaletas anteriores siguen con sus archivos: Orleans `01a_escaleta.json` (F7c-3, md5 `2f794418…`), `_f7c3`, `_f14`, `_f15` y `_f15b`; Ycuá `01a_escaleta.json`, `_v1` (md5 `e1ba1a48…`), `_ajuste` y `_f15`.
  - Las nuevas son `01a_escaleta_f16.json` en los dos temas.
  - `data/` está en `.gitignore`.
- **Obs. B (`ids_v2` puede sumar apoyos):** es cierto que lee todos los D/T/Q de un apoyo. El tope de 6 apoyos y «un id en un solo beat» los sigue aplicando `validate` después. Queda como riesgo para el analista.
- La decisión de Omar sobre `ids_v2` está en el chat de esta sesión («Leer el id y re-correr»).

VEREDICTO: CUMPLE CON OBSERVACIONES

Tabla: # | requisito | estado | evidencia
1 | Sistema v2 literal | OK | Calculé el bloque desde `<rol>` hasta `</errores>` del .md (LF) y es igual a `m01a_escaleta.SYSTEM_V2`: True, 5,769 caracteres, md5 `49ed74d9…`. Es la misma md5 de la línea de sistema de `prompt_ycua_f16_escaleta.txt` y `prompt_orleans_f16_escaleta.txt`. El md5 del .md (`8d573288…`) coincide con el reporte.
2 | `<tarea>` literal al final del usuario | OK | `TAREA_V2` coincide con la del .md y es lo último en `prompt_ycua_f16_escaleta.txt`. El usuario lleva `<caso>`, `<ficha>`, `<tarea>`, sin FEWSHOT, sin `escaleta_notas` y sin reglas. El feedback aparece solo en la regeneración, como `<rechazo>`.
3 | 13 bloqueantes sin cambios; ninguno nuevo | OK | `validate`, `question_problems`, `writer_instructions`, `caps_view` y `_screen_by_date` son idénticos a HEAD (comparé el código fuente). El diff solo toca `apply_pool_plan` (parámetro `instrucciones=True`) y `generate_escaleta` (desvío a v2), y agrega código nuevo. `BLOQUEANTES_V2` son patrones sobre mensajes de `validate` que existen en las líneas 534–717. Solo se agregó una lista de selección.
4 | Clasificación del reporte §2 | OK | Cuadra: 9 rechazan, 2 rechazan y reparan (un id en un solo beat; otra cifra del conteo), 2 solo reparan (nombre exacto; cita sin verificar fuera de `a_pantalla`), más la precondición numérica. Las 12 entradas de la tupla son 11 bloqueantes más la precondición. Ver observación A.
5 | Sin ficha byte-idéntico | OK | Cargué el módulo de HEAD y comparé `RULES`, `SCHEMA`, `SYSTEM`, `SCHEMA_FICHA` y `FEWSHOT`: todos iguales. `build_prompt` da igual salida que HEAD en `ba6c3cac-f7r3` y `f8s1-ycua-bolanos`, con y sin ficha, con y sin feedback. Los md5 sin ficha coinciden con el reporte (`379d8405…` Orleans, `f17b1b25…` Ycuá).
6 | Sol high, una sola regeneración, PARADA, sin `instrucciones_guionista` | OK | `generate_escaleta_v2` (`REGENERACIONES_V2 = 1`, `call_for`, `apply_pool_plan(instrucciones=False)`). Los dos JSON F16 no traen `instrucciones_guionista`. Los `_intentos` muestran Ycuá 11 → 0 y Orleans 17 → 0 (el 17 de Orleans lo tomé del reporte, no lo recontré).
7 | `ids_v2`: no rechaza nada nuevo y está declarado | OK | Solo extrae el id D/T/Q (o P) del texto y registra cada lectura como reparación. Si no encuentra id deja el texto, y rechaza el bloqueante «dato central existe». En el intento 1 del pase 2 se ve: `dato_central` «P13 / P80 …» siguió rechazado. Está en el docstring, en el reporte §En una línea y §2, y en test. Omar lo eligió en el chat, según el reporte; no pude verificar eso. Ver observación B.
8 | Pase 2 de Ycuá frenado por la reserva, sin gasto | OK | `costos_f16.json`: etapa Ycuá escaleta con usd 0.0 y 0 llamadas, error «tope de costo… reserva 1.30 > 2.00». La corrida posterior de Ycuá está en `corridas_ycua.out`.
9 | Costos y tokens del reporte | OK | Sumé `costos_f16.json`: 0.2535 + 0.2511 + 0.3015 + 0.1176 + 0.2980 + 0.1374 = 1.3591, igual al reporte, y menor que el tope de 2.00. Los tokens por etapa coinciden con el §5.
10 | Números de escaletas y guiones | OK | Los JSON F16 dan: Ycuá 14 beats, Liz Torres, pico beat 8/Q20, curva `4 1 1 3 4 4 4 5 2 2 3 3 3 3`, escenas `[2,3,5,7,8,9,10,12]`, gancho y pico E8, giros 6/6. Orleans 14 beats, Joyce Gilson, pico beat 10/D155, escenas `[1,3,6,8,9,11,12,15]`, gancho y pico E9, giros 6/6. Los guiones dan 1,384 y 1,443 palabras, con 0 bloqueantes (`corridas*.out`). Ycuá tiene 14 + 38 lecturas de id, igual que el reporte; no recontré las de Orleans (reporte: 14 + 45).
11 | Tests y compara | OK | Los 7 archivos de test que me indicaron: 113 passed. `python -I f16_compara.py` corre sin APIs y regenera `compara_f16.html`. No corrí la suite amplia (650 + 5 previas): es dato del reporte.
12 | Frenos y entregables | OK | `git status` sin tocar: pool, research_v3, m05, evidence.py, guion_v3_reglas.py, config.py, topics_db, m03*, gfx_*; solo cambian `m01a_escaleta.py` y `lab/ESTADO_SESION.md` (17 líneas nuevas, 2 borradas). `test_module_f16.py` y `lab/hyperframes/f16/` son nuevos y están sin commitear (los gfx_profiles y diag_234 ya venían modificados). Todos los entregables listados existen. No hay `data/` modificado en git (probablemente ignorado); no verifiqué `01a_escaleta_f16.json` ni que las escaletas anteriores estén intactas.

Observaciones (no tumban el contrato):
A. Los «13» son 13 en el handoff, pero en código solo 11 pueden rechazar. «Nombre exacto» y «a_pantalla sin citas sin verificar» nunca rechazan (solo reparan). El reporte lo declara. Es consistente con «extraer tal cual», pero el handoff las lista como bloqueantes.
B. `ids_v2` es código no previsto en el handoff. Cambia qué pasa el filtro, porque antes ese texto rechazaba y ahora se lee. Lee todos los D/T/Q de un apoyo, y un apoyo con ids de contraste en el texto sumaría apoyos que el modelo no eligió (el tope de apoyos lo aplica `validate`).
C. Orleans eligió a Joyce Gilson, con 0 citas verificadas, contra el oficio 1; el humano cambió de nuevo (Reed → Pearl → Richard → Burton → Gilson). El reporte lo dice. Es hallazgo de contenido, no incumplimiento. Ycuá y Orleans necesitaron la regeneración en la escaleta, dentro de lo permitido.
D. §7 sigue «(pendiente)»: este veredicto va ahí.

Fuera de alcance: ninguno (`diag_234_cap4.py` y `gfx_profiles/*` ya estaban modificados antes de F16 y no los evalué).

Riesgos que el contrato no cubre: (1) la elección del humano no es estable entre corridas y ninguna regla la fija, solo una métrica. (2) `ids_v2` puede enmascarar salidas mal formadas del modelo que antes se rechazaban. (3) Con una muestra de dos temas y escaleta aceptada solo en la regeneración, no se sabe cuántas veces cae en PARADA.
