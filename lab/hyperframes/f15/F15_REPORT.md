# F15 — Prompt del guionista v5 + ficha con historia y escenas (Ycuá y Orleans) — REPORTE → PARADA

CC · 2026-10-23 · rama `f11-guion-v4` (desde `1920d40`). Handoff: `HANDOFF_F15_prompt_v5.md`. Solo ficha → escaleta → guion.

**En una línea:** los dos prompts van literales; el del guionista, **después de un arreglo** (ver «Incidente» abajo). Con el v5, **los dos guiones salen cortos**: Ycuá tiene **755 palabras (6.1 min)**, contra 1,153 en F13, y Orleans **866 (7.0 min)**, contra 1,451 en F14. En los dos hay 0 bloqueantes, 0 preguntas y 0 frases de analista. La escaleta de Orleans quedó rechazada en los 3 intentos la primera vez (por una regla que ya existía) y salió en un segundo pase de esa etapa. Costo: **US$ 2.116** de 2.50.

> **Incidente (encontrado por el revisor-handoff en su primera pasada):**
> - **Qué pasó:** el código y el test sacaban el bloque SISTEMA del `.md` con `md.index("<rol>")`, pero la primera aparición de `<rol>` está en el párrafo introductorio del archivo (línea 3), no en el bloque (línea 11). Así, el sistema que se mandó en las dos primeras corridas de guion llevaba adelante la introducción («Escrito por el analista… Base: técnicas de narradores reales…»): md5 `f157a2ce…`, 8,247 caracteres. El test pasaba porque usaba la misma extracción.
> - **Arreglo:** la extracción se ancla en «## SISTEMA», y el test también (además, verifica que el texto empiece en `<rol>` seguido de «Sos el guionista» y que no traiga «Base: técnicas»). El sistema que se manda ahora es el bloque exacto: md5 **`2ff2a5cd7bc63a2fa9fc0faa2117ac65`**, 7,692 caracteres.
> - **Re-corrida:** volví a correr **solo los dos guiones**; las fichas y las escaletas no dependen de ese prompt. Los guiones contaminados quedan como registro en `guion_*_f15_preambulo.json`, `NARRACION_*_f15_preambulo.md` y `prompt_*_f15_guion_preambulo.txt`.
> - **Resultado:** la introducción no explicaba el largo. Con el sistema correcto, Ycuá pasa de 718 a 755 palabras y Orleans de 763 a 866.
> - Las dos re-corridas se lanzaron primero juntas. El freno de costo del runner reservaba US$ 1.00 para «Orleans entero» (que ya tenía la ficha y la escaleta) y frenó la primera llamada, sin gastar. Después corrieron por separado.

Para leer:
- `compara_f15.html`: por tema, la versión anterior y F15, cap por cap. Se lee en el teléfono.
- `ficha_ycua/FICHA_ycua_f15.md` y `ficha_orleans/FICHA_orleans_f15.md`: historia y escenas arriba de todo.
- `ESCALETA_{ycua,orleans}_f15.md`.
- `NARRACION_{ycua,orleans}_f15.md`.

> **Advertencia del analista (va tal cual):** los ejemplos del prompt v5 salen de Orleans y de Ycuá. En estos dos temas Sol tiene una ventaja que no va a tener en un tema nuevo. Se acepta, porque son los únicos párrafos probados de 8 o más. Con el primer tema nuevo se mide de verdad.

## 1. md5 de los prompts contra los archivos del analista

| archivo del analista | md5 del archivo | lo que se usa | md5 de lo que se manda |
|---|---|---|---|
| `PROMPT_GUIONISTA_v5.md` | `411782fa70f31269bfc60018ff560df8` | bloque SISTEMA (desde «## SISTEMA», de `<rol>` a `</errores>`) = `guion_v4.SYSTEM_V5`, y bloque `<tarea>` del USUARIO = `guion_v4.TAREA_V5` | sistema del guion **`2ff2a5cd7bc63a2fa9fc0faa2117ac65`** (en los dos temas, después del arreglo; antes `f157a2ce…`, con la introducción) |
| `PROMPT_FICHA_v2.md` | `1fdbd0b90b4666e3bb15887dbec26fd4` | bloque «Lo que se agrega al `<tarea>`» insertado literal en `ficha_caso.system()`, antes de la línea de hechos | sistema de la ficha **`2e151732da47e09acf0cb48eb7089fcb`** (en los dos temas) |

- `test_module_f15.py` lee los dos `.md` y compara.
  - El sistema v5 tiene que ser **byte-idéntico** al bloque SISTEMA (extraído desde «## SISTEMA»), y el usuario termina en la `<tarea>` del bloque USUARIO del archivo.
  - El bloque de la ficha v2 tiene que estar **literal** en el sistema de la ficha.
- Los textos se copiaron con un script que lee el `.md`, no a mano.

**Cómo se implementó y qué no se pudo hacer tal cual** (sin reinterpretar):
1. **Sistema v5:** reemplaza entero a `system()`. El de F11c queda como `system_f11c()`, y con `version="f11c-1"` se pueden reproducir F11c–F14 byte a byte. `PROMPT_VERSION = "f15-1"`.
2. **Usuario v5:**
   - `<caso>`: tema · humano (nombre, rol, «por qué:» de la escaleta) · promesa · pico (beat N, «por qué:») · cierre humano.
   - `<escaleta>`:
     - Por cap: «CAP n (función)»; la función del cap son las funciones de sus beats.
     - Por beat: función · emoción · intensidad, imagen sensorial, dato central, apoyos, «el espectador se pregunta» y cierre.
     - Quedan las líneas «en pantalla:» (datos con la marca PANTALLA, que el sistema v5 nombra).
     - Se sacó «lo que abre el cap N»: no está en el formato del analista.
   - `<tarea>`: literal.
   - Largo abierto siempre. El parámetro `largo` sigue existiendo, pero no cambia el v5, y su valor por defecto pasa a `abierto` en el prompt, en los bloqueantes y en la reparación.
3. **«VERSIÓN DE: quién»:** las `versiones` de la ficha no traen un campo de quién. Quién = el autor del ítem si es una cita; si no, su fuente en el pool.
4. Los tests viejos que fijaban los valores por defecto de F11c y F13 ahora piden `version="f11c-1"` y `largo="objetivo"` explícitamente: 9 aserciones en `test_module_f11`, `f11b`, `f11c` y `f13`, más 2 de esquema y versión en `f12` y `f14`. Siguen protegiendo la byte-identidad de esas versiones.

## 2. Ficha v2, escaleta y bloqueante (d)

- **Ficha** (`researcher_steps/ficha_caso.py`, `f15-1`):
  - Esquema con `historia` (humanos_candidatos, giros, pico, pregunta_final), `escenas` y `nivel`/`sirve_para` en `hechos`.
  - Chequeo: lo nuevo pasa por el mismo control (ids que existen; cifras, horas y fechas respaldadas). Además, **los sentidos de una escena tienen que estar en el texto de sus ids**: se parten en tramos (por `;`, `,` o «y») y cada tramo necesita una palabra de contenido cuya raíz de 5 letras aparezca en esos ids. Si no, la escena va a `descartados` («no respaldado»).
  - El `.md` muestra historia y escenas primero.
  - Antes de escribir, se respaldaron las fichas anteriores: Orleans F14 → `ficha_caso_f14.json`; Ycuá F12 → `ficha_caso_f12.json`.
- **Escaleta** (`m01a_escaleta`):
  - Con la ficha v2, la sección de la ficha arranca con HISTORIA (los humanos candidatos, con la indicación de elegir entre ellos o justificar en `justificacion_humano`; giros, pico, pregunta final) y ESCENAS (E1…, con la indicación de citar `escena_idx`). Después siguen personas, cronología, hechos (con nivel y para qué sirven) y lo demás.
  - Con ficha v2 se manda un esquema aparte (`SCHEMA_FICHA`: `escena_idx` por beat y `justificacion_humano`). `ficha_notes` saca un `escena_idx` que no existe (reparación) y manda a `_avisos` un humano que no está entre los candidatos. No rechaza nada.
  - **Sin ficha, el prompt es byte-idéntico:** los md5 de HEAD (Orleans `379d8405…`, Ycuá `f17b1b25…`, con y sin feedback, y `RULES`) coinciden, y `SCHEMA` no cambió.
- **Bloqueante (d):** `guion_v4.bloqueantes(..., ficha=)` le pasa a `m05.contamination` una copia del pool **sin las personas que la ficha rescató** (`personas_descartadas`). El pool no se toca y `m05` tampoco.
  - Medido con el código de hoy, F14 Orleans pasa de 2 bloqueantes (Burl Cain y Katherine Mattes) a **0**.
- **Tests:** `test_module_f15.py` (12, sin red). **Suite amplia: 621 verdes + las 5 fallas previas** (3 `01b_pauses`, 2 `m03_merge_timing`). `test_v3_byte_identico`, verde.

## 3. Tabla resumen y embudo, por tema

### Ycuá (`f8s1-ycua-bolanos`, pool de 509 ítems)

| versión | palabras | **min** | palabras por cap (1–7) | bloq. | duras v3 | citas | preguntas | frases de analista | humano (caps en escena) | pico | cierre | US$ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F13 abierto (digest + escaleta v1) | 1,153 | **9.4** | 110 · 197 · 180 · 183 · 184 · 202 · 97 | 0 | 22 | 10 | 6 | 0 | Liz Torres (1, 2, 5, 6, 7) | beat 8 · T21 | cita | 0.064 (solo guion) |
| **F15** | **755** | **6.1** | 72 · 151 · 102 · 72 · 132 · 127 · 99 | 0 | 31 | 10 | **0** | 0 | Liz Torres (1) | beat 8 · Q20 | cita | 0.871 (con las dos corridas de guion) |

Embudo (pool → selección → escaleta → guion): F13 509 → 325 (digest) → 40 → 17; **F15 509 → 314 (ficha v2) → 46 → 11**.

Primera corrida, con la introducción (registro): 718 palabras, 5.8 min, 0 bloqueantes, 0 preguntas.

### Orleans (`ba6c3cac-f7r3`, pool de 1,033 ítems)

| versión | palabras | **min** | palabras por cap (1–7) | bloq. | duras v3 | citas | preguntas | frases de analista | humano (caps en escena) | pico | cierre | US$ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F14 (ficha f14 + escaleta f14) | 1,451 | **11.8** | 115 · 209 · 205 · 190 · 207 · 316 · 209 | 0* | 36 | 8 | 2 | 0 | Pearl Cornelia Bland (1, 2, 3, 7) | beat 9 · D120 | pregunta | 0.811 |
| **F15** | **866** | **7.0** | 77 · 149 · 125 · 136 · 159 · 145 · 75 | 0 | 36 | 9 | **0** | 0 | Brady Richard (1, 2, 4, 5, 7) | beat 9 · D155 | cita | 1.245 (con las dos corridas de guion) |

\* En F14 eran 2 bloqueantes; con el (d) de §1.4 y su propia ficha quedan en 0.

Embudo: F14 1,033 → 378 → 53 → 18; **F15 1,033 → 363 → 47 → 10**.

Primera corrida, con la introducción (registro): 763 palabras, 6.2 min, 0 bloqueantes, 0 preguntas.

**Lectura de los números** (la nota la da el analista):
- **El v5 escribe bastante menos.** Con la ficha v2 y escaletas de 13 beats en los dos temas, Sol escribe 755 y 866 palabras (entre un 35 % y un 40 % menos que la mejor versión anterior). Con la introducción eran 718 y 763: no es eso lo que acorta.
  - El prompt v5 dice «Cada cap dura lo que su historia necesita. Ni relleno ni resumen. Si un beat tiene tres datos, son tres datos bien contados, no diez frases», y no hay ninguna cifra de largo.
  - Los ids que usa el guion también bajan: Ycuá de 17 a 11, Orleans de 18 a 10.
  - No lo toqué: no hay criterio de largo en este handoff, y agregar uno sería una regla.
- **Preguntas: 0 en los dos** (antes 6 y 2). Es lo que pide el v5: «No preguntás por costumbre».
- **Cierres:** los dos terminan en una cita.
  - Ycuá: «Liz sobrevive a la avalancha y convierte su experiencia en una lucha por la memoria. Su reclamo sigue siendo: "Que nunca más ocurra un 1A"».
  - Orleans: «Años después, Richard sigue volviendo a la decisión anterior al agua y a los disparos: "La gente necesita entender que simplemente nunca deberíamos haber estado allí en primer lugar"».
- **Ganchos:**
  - Ycuá: «Una avalancha de cuerpos empuja hacia adentro. Según una sobreviviente, cuando empezó el fuego alguien dio la orden de cerrar las puertas.»
  - Orleans: «Los francotiradores disparan desde un techo, bajo un cielo gris de tormenta. Miles de personas han quedado atrapadas en una cárcel inundada; las autoridades dirán que no hubo muertos y otras voces las contradirán.»
- **Duras v3** (métrica del v3, no bloqueante): Ycuá sube de 22 a 31 y Orleans queda en 36. Incluyen las de largo de cap del v3, que el texto corto dispara.
- **Humano en escena:** en Ycuá, Liz Torres aparece por nombre solo en el cap 1 (en F13, en 5 caps). El cierre la nombra como «Liz»; la métrica busca el apellido.

## 4. Qué eligió la ficha y qué tomó la escaleta

### Ycuá

- **Humanos candidatos:**
  - Tatiana Gabaglio (3 citas verificadas: niña atrapada bajo un panel → pierde una pierna → abogada);
  - Mariana Aquino de Chamorro (3);
  - Blas Cristaldo (0, «lo decís»);
  - **Liz Torres** (4).
- **Giros:**
  1. la explosión;
  2. el blíndex y el portón cerrados;
  3. el boquete;
  4. la búsqueda que se vuelve identificación de cuerpos;
  5. la pericia que contradice los testimonios del cierre;
  6. la condena con el principal demandado ya muerto.
- **Pico:** Liz atrapada entre cuerpos, «como un horno», con los gritos que se apagan (Q19, Q20, Q77).
- **Pregunta final:** ¿podrá cobrarse la reparación, si el principal demandado murió y no se sabe si quedan bienes?
- **Escenas:** 9 (14 crudas; el chequeo sacó 5). Hechos de nivel 1: 20.
- **Lo que tomó la escaleta:** humano **Liz Torres** (candidata), pico en el beat 8, sobre **Q20** (uno de los ids del pico de la ficha). **No usó ninguna escena** (`escena_idx` vacío en los 13 beats). No hay avisos de humano.

### Orleans

- **Humanos candidatos:**
  - Pearl Cornelia Bland (1 cita verificada);
  - **Brady Richard** (3);
  - Joyce Gilson (0);
  - Edward «Edgar» Burton (2).
- **Giros:**
  1. la evacuación excluye a los presos y Gusman rechaza la ayuda;
  2. OPP no se vacía;
  3. entra el agua, fallan los generadores y los oficiales se van;
  4. el pedido tardío al DOC;
  5. Central Lock-Up como espera dentro del agua;
  6. la dispersión en Hunt.
- **Pico:** Iris Hardeman, sostenida sobre el agua por sus compañeras en Central Lock-Up (D76, D78, D155).
- **Pregunta final:** ¿qué pasó con cada persona que no figuraba en la lista de evacuados?
- **Escenas:** 10 (15 crudas). Hechos de nivel 1: 18.
- **Lo que tomó la escaleta:** humano **Brady Richard** (candidato), pico en el beat 9, sobre **D155** (el pico de la ficha). **Usó 5 escenas** (E2, E3, E5, E7 y E10). No hay avisos de humano.
- **Primer pase de la escaleta de Orleans (rechazado):** los 3 intentos fallaron por reglas que ya existían. El último solo por «un hecho, una cifra»: D533 es otra cifra del conteo 5.919 [D214], y la ficha presenta las dos. Volví a correr esa etapa una vez, dentro del tope, y salió en el segundo intento. Los dos pases están en `costos_f15.json`.

## 5. Paiva hijo, Nagin, Cain y Mattes

- **Paiva hijo (Ycuá):**
  - La ficha v2 lo tiene dos veces: como **decisión con criterio 2** («se usa Víctor Daniel Paiva porque esa forma y Víctor Paiva aparecen en más documentos») y como **contradicción** («Emiliano frente a Víctor Daniel»).
  - **El guion F15 nombra al hijo sin nombre:** «Juan Pío Paiva es condenado a 12 años de prisión. Su hijo, a 10 años.» (beat 12). También nombra a Juan Pío Paiva por la orden que le atribuye una sobreviviente y por su muerte. No dice ni «Emiliano» ni «Víctor Daniel». En la corrida con la introducción no lo nombraba.
  - La decisión sobre el nombre sigue siendo de Omar.
- **Nagin, Cain y Mattes (Orleans):**
  - Los tres están en `personas_descartadas` de la ficha v2. Nagin sostiene el primer giro; Mattes «proporciona el desenlace documentado del arco de Pearl Bland»; Cain está vinculado a la llegada de los oficiales estatales.
  - **El guion F15 no nombra a ninguno**, porque la escaleta eligió a Brady Richard y no usó esos ids.
  - Con el (d) nuevo, ya no serían bloqueantes aunque aparecieran: F14 re-medido da 0.

## 6. Lo que sacó el chequeo de las fichas

| | Ycuá | Orleans |
|---|---|---|
| escenas | 5 de 14 | 5 de 15 |
| cifras | 12 | 2 |
| cronología | 0 | 3 |
| citas | 0 | 2 (corregidas a 13 y 94 caracteres del original) |
| personas descartadas | 0 | 5 (internos «#5», «#6»…, que no están en los descartados del pool) |
| decisiones y versiones | 0 | 1 y 1 |
| descartados sin ids | 0 | 1 |
| **total** | **17** | **20** |

**Dos límites del chequeo que se ven acá** (no los corregí; no es parte del pedido):
- **Cifras con otra forma:** en Ycuá sacó 12 cifras porque la ficha las escribe completas (por ejemplo «4.500.000.000» guaraníes) y el pool dice «G. 4.500 millones», o porque el pool las tiene en letras («seis», «dos hijas»). Son falsos positivos de formato. Con esto, las cifras de Ycuá bajan de 41 a 29.
- **Sentidos:** saca escenas por tramos que no son sentidos («según ella», «según el testimonio», «movimiento de huida»). Es más estricto de lo que pide el handoff.

Las dos cosas se pueden ajustar sin agregar ninguna regla al guion. Lo decide el analista.

## 7. Costo y tokens

| tema · etapa | modelo | llamadas | entrada | salida | razonamiento / thinking | US$ | segundos |
|---|---|---|---|---|---|---|---|
| Ycuá · ficha | gpt-6.1-sol high | 1 | 48,904 | 24,962 | 5,237 | 0.3998 | 546 |
| Ycuá · escaleta | gemini-2.5-pro | 2 intentos | 23,193 / 23,455 | 3,188 / 3,526 | 5,641 / 3,753 | 0.2194 | 142 |
| Ycuá · guion, con la introducción (registro) | gpt-6.1-sol high | 1 | 6,085 | 1,785 | 11,011 | 0.1401 | 274 |
| Ycuá · guion (sistema correcto) | gpt-6.1-sol high | 1 | 5,929 | 1,824 | 8,191 | 0.1120 | 253 |
| Orleans · ficha | gpt-6.1-sol high | 1 | 91,985 | 22,990 | 3,587 | 0.4497 | 451 |
| Orleans · escaleta, pase 1 (rechazado) | gemini-2.5-pro | 3 intentos | ≈ 21.1 k c/u | ≈ 3.4 k c/u | 5,634 / 4,784 / 6,652 | 0.3514 | 228 |
| Orleans · escaleta, pase 2 | gemini-2.5-pro | 2 intentos | 21,061 / 21,309 | 3,367 / 3,572 | 5,132 / 4,619 | 0.2199 | 139 |
| Orleans · guion, con la introducción (registro) | gpt-6.1-sol high | 1 | 5,782 | 1,610 | 6,595 | 0.0936 | 203 |
| Orleans · guion (sistema correcto) | gpt-6.1-sol high | 1 | 5,626 | 1,868 | 10,012 | 0.1301 | 315 |
| **tanda F15** | | | | | | **2.1160** (tope 2.50) | |

Las md5 de cada prompt están en `prompt_<tema>_f15_{ficha,escaleta,guion}.txt`.

## 8. Frenos

- No se tocaron `00_pool_v3.json` (md5 verificados), `research_v3.py`, `m05`, `evidence.py`, `guion_v3_reglas.py`, `config.py` ni `topics_db`.
- Cero reglas nuevas para el guion: el v5 trae todo en el prompt y nada de eso se convirtió en validador. Los controles nuevos son de la ficha. El (d) cambió de fuente, no de criterio.
- Las fichas y escaletas anteriores no se pisaron:
  - fichas: `ficha_caso_f12.json` (Ycuá) y `ficha_caso_f14.json` (Orleans);
  - escaletas: `01a_escaleta_v1`, `_f7c3` y `_f14` intactas; las nuevas son `01a_escaleta_f15.json`.
- **Ojo:** `_steps/<topic>/ficha_caso.json` es ahora la v2 en los dos temas, y la escaleta y el guion v4 la leen solos (`ficha="auto"`).
- Sin merge. `.env` y `lab/_gpt_probe_analista/` no se commitean. Sin imágenes, voz ni producción.

## 9. Veredicto del revisor-handoff (íntegro)

### Segunda revisión, después del arreglo (vigente)

VEREDICTO: CUMPLE CON OBSERVACIONES

La falla de la primera revisión quedó corregida. Los prompts van literales, el sistema del guion es el bloque exacto, y los números del reporte coinciden con los artefactos. Lo que queda abierto son observaciones sobre el alcance del diff, no incumplimientos del contrato.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | SYSTEM_V5 byte-idéntico al bloque SISTEMA del .md | OK | Calculé el bloque desde `PROMPT_GUIONISTA_v5.md` (líneas 11 a 92, de `<rol>` a `</errores>`): md5 `2ff2a5cd7bc63a2fa9fc0faa2117ac65`. `guion_v4.system()` == bloque (True) y `SYSTEM_V5` tiene el mismo md5. |
| 2 | Línea de sistema de las corridas guardadas | OK | `prompt_{ycua,orleans}_f15_guion.txt` llevan en la cabecera ese md5, y el texto entre cabeceras es igual al bloque (True en ambos). `guion_*_f15.json` registra `prompt_md5.sistema` = `2ff2a5cd…`. |
| 3 | `<tarea>` del usuario literal | OK | La `<tarea>` del .md está contenida en el usuario de ambos prompts, y el usuario termina en `</tarea>`. Los md5 de usuario coinciden entre .txt y .json (Ycuá `0a0bf276…`). |
| 4 | Test ancla bien | OK | `test_module_f15.py:34` ancla en `"\n## SISTEMA\n\n"`; ya no usa `index("<rol>")`. |
| 5 | Ficha v2: bloque literal en `ficha_caso.system()` | OK | Todas las líneas del bloque "Lo que se agrega al `<tarea>`" de `PROMPT_FICHA_v2.md` están en `system()` (`blk in fs` True). Está antes de la línea de hechos, y la `<tarea>` del usuario menciona historia y escenas. `PROMPT_VERSION` = `f15-1`. |
| 6 | Esquema de la ficha | OK | `ficha_caso.py` SCHEMA: `historia` (humanos_candidatos, giros, pico, pregunta_final), `escenas`, y `nivel`/`sirve_para` en `hechos`, todos en `required`. |
| 7 | Chequeo de escenas | OK | `sentidos_problems` y `problems("escenas")`: la escena cuyos tramos de sentidos no están en el texto de sus ids va a `descartados` con "no respaldado". `check()` aplica el mismo control a `historia`. Hay test en f15. Es una heurística (raíz de 5 letras y lista de stopwords), más estricta que el handoff. El reporte §6 lo admite: sacó 5 de 14 escenas en Ycuá y 5 de 15 en Orleans. |
| 8 | `.md` de la ficha con historia y escenas arriba | OK | `markdown()`: Historia y Escenas van antes de Contradicciones (test f15). |
| 9 | Bloqueante (d) mira `personas_descartadas` | OK | `guion_v4.pool_sin_rescatados` pasa a `contamination` una copia del pool sin esas personas. `m05` y el pool no se tocan, y el test lo verifica. Pasa y no se pisa. |
| 10 | Escaleta sin ficha byte-idéntica | OK | Ejecuté `HEAD:script_engine/m01a_escaleta.py` contra el actual. `build_prompt` con TOPIC11/POOL11 es igual con y sin feedback, y `SYSTEM` y `SCHEMA` son iguales. Con ficha v2 va `SCHEMA_FICHA`. |
| 11 | Escaleta con ficha: historia y escenas antes de hechos; `escena_idx`; humano fuera de candidatos va a `_avisos` | OK | Diff de `m01a_escaleta.py` (`ficha_section`, `ficha_notes`), con test. |
| 12 | Marca "VERSIÓN DE: quién" | OK | `guion_v4.version_marks` y `escaleta_section_v5`. El quién sale del autor o la fuente, porque las `versiones` no traen ese campo. El reporte lo declara. |
| 13 | Suites | OK | Corrí las 7 suites indicadas: 75 passed. No re-medí la suite amplia de 621 + 5; sigue siendo la cifra del reporte. |
| 14 | `f15_compara.py` | OK | Corre sin APIs. Sus números coinciden con el reporte: Ycuá 755 palabras / 6.1 min, embudo 509→314→46→11; Orleans 866 / 7.0 min, embudo 1033→363→47→10; 0 preguntas, 0 bloqueantes, humanos Liz Torres y Brady Richard, picos Q20 y D155, Orleans con escenas 2, 3, 5, 7 y 10. |
| 15 | Números del reporte | OK | `guion_*_f15.json`: palabras por cap, minutos, duras (31 y 36), citas (10 y 9) y cierre (cita) coinciden. `NARRACION_*` no tiene ningún "?". `costos_f15.json` suma 0.8713 (Ycuá) + 1.2447 (Orleans) = 2.1160, bajo el tope de 2.50. Los `corridas*.out` marcan tanda 2.1160 y los costos individuales coinciden. Los `*_preambulo` están conservados. |
| 16 | Frenos | OK | No aparecen cambios en `00_pool_v3`, `research_v3`, `m05`, `evidence`, `guion_v3_reglas`, `config` ni `topics_db`. Hay cero validadores nuevos para el guion. Existen `ficha_caso_f12.json`, `ficha_caso_f14.json` y `01a_escaleta_f14.json` (también `_f7c3`). Nada de merge ni commit, y `.env` no aparece. |
| 17 | Pedidos del reporte | PARCIAL | §9 dice "(pendiente)", esperado porque este veredicto lo llena. Falta el "Paiva hijo" en términos de decisión, que el reporte deja a Omar; está documentado en §5. |
| 18 | `lab/ESTADO_SESION.md` actualizado | OK | El diff tiene la sección F15 con las cifras nuevas y el incidente. |

Fuera de alcance:
- `fase1_5.py` (+2 líneas, `reparar(..., ficha=ficha)`). El handoff no lo lista; es cableado necesario para que (d) mire la ficha en producción.
- `diag_234_cap4.py` y `gfx_profiles/*`: ignorados por instrucción.
- Los tests f11, f11b, f11c, f12, f13 y f14 se editaron para fijar `version="f11c-1"` y `largo="objetivo"`. El reporte lo declara y las aserciones siguen protegiendo la byte-identidad de esas versiones.

Observaciones:
1. El default de `largo` pasa a `abierto` también en `bloqueantes`, `reparar` y `write`, y el prompt por defecto pasa a v5. Por eso `run_guion_v4` en producción ya usa v5 y largo abierto. El handoff lo pide para el prompt; el efecto sobre el bloqueante (c) en producción queda implícito.
2. `pool_sin_rescatados` rescata por coincidencia de subcadena (`t in x or x in t`) sobre el nombre normalizado. Un descartado con texto corto podría rescatarse de más. No se verificó con casos reales.
3. Corrí `f15_compara.py` y reescribió `compara_f15.html` (45,609 → 44,768 bytes). Es un artefacto regenerable; si importa la versión exacta, hay que revisarlo.
4. La escaleta de Ycuá no usó ninguna escena (`escena_idx` vacío en los 13 beats) y Orleans usó 5. El reporte lo informa.

Riesgos que el contrato no cubre:
- Con v5 y largo abierto los guiones salen entre 35 y 40 % más cortos (755 y 866 palabras). El reporte lo señala y no pone un criterio de largo, así que depende de la decisión del analista.
- Los falsos positivos del chequeo de cifras y sentidos (12 cifras de Ycuá) reducen lo que llega a la escaleta y no es un cambio de reglas; el reporte lo deja al analista.
- `_steps/<tema>/ficha_caso.json` es ahora la v2 y la escaleta y el guion v4 la leen solos (`ficha="auto"`). Las versiones anteriores solo están respaldadas bajo los nombres `_f12` y `_f14`.

### Primera revisión, antes del arreglo (registro)

VEREDICTO: NO CUMPLE (un defecto bloqueante en el requisito central: el prompt del guionista NO va literal)

Hallazgo principal, verificado ejecutando el código. `guion_v4.SYSTEM_V5` (script_engine/guion_v4.py, alrededor de la línea 75) arranca con el párrafo introductorio del archivo del analista, no con el bloque SISTEMA. Empieza en "<rol>`, `<voz>`, `<estructura>`, `<oficio>`, `<ejemplos>` y `<errores>` son el mensaje de sistema completo. No se resume, no se reordena, no se le agregan reglas." Después trae "Base: técnicas de narradores reales…", "---", "## SISTEMA" y recién ahí el `<rol>` real.
- Causa: el test y el código extraen con `md.index("<rol>")`. Esa primera aparición cae en la línea 3 del .md (texto meta), no en la línea 11 (el bloque real). El test (test_module_f15.py:34-35) usa la misma extracción defectuosa, por eso pasa en verde: compara el código contra su propio error.
- Medido: el sistema enviado mide 8,247 caracteres y su md5 es f157a2ce… (el del reporte §1). El bloque correcto, de la línea 11 a `</errores>`, da md5 2ff2a5cd…. El enviado termina igual que el correcto, pero no es igual (`s == good` da False).
- Los dos prompts reales de Sol (prompt_ycua_f15_guion.txt y prompt_orleans_f15_guion.txt, línea 1) llevan ese preámbulo, con "Ken Burns / David McCullough", "Orleans F7c-3 y F14" y "lo que fallaba en los demás".
- Consecuencia: los dos guiones F15 (718 y 763 palabras) se generaron con un sistema contaminado. Eso viola el §0 del handoff ("Van literales") y vuelve dudosa la lectura del reporte §3, "el v5 escribe la mitad". No sé si el preámbulo causó la caída de largo; hay que re-correr para saberlo. El reporte (§1, 1.ª fila) afirma "byte-idéntico" y eso es falso. Tampoco hay que pegar el md5 del reporte como prueba: es el md5 del texto equivocado.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Sistema v5 literal, `PROMPT_VERSION="f15-1"` | FALLA | ver arriba. La versión sí es "f15-1" (guion_v4.py:41) |
| 2 | `<tarea>` literal al cierre del usuario | OK | `TAREA_V5` termina el prompt; coincide con el .md |
| 3 | `largo` default "abierto", sin cifras de largo | OK | guion_v4.prompt/write/bloqueantes; no aparece "≈" |
| 4 | Marca «VERSIÓN DE: quién» | OK con criterio propio | `version_marks`. El quién sale del autor, de la fuente o del `doc_id` (decisión declarada §1.3, razonable) |
| 5 | Ficha v2: bloque literal en `system()`, esquema, `nivel`/`sirve_para`, `f15-1` | OK | `fc.system()` contiene el bloque; el test compara con el índice correcto. Queda duplicada la línea vieja "- hechos: entre 60 y 80" justo después de la nueva (cosmético) |
| 6 | Chequeo determinista: ids, cifras, horas, fechas, sentidos | OK | `sentidos_problems`, `check` de historia, `counts`, `markdown`. Tests verdes. El propio reporte §6 admite que es más estricto que lo pedido (descartó 5 de 14 y 5 de 15 escenas) |
| 7 | `.md` con historia y escenas arriba | OK | `markdown()`; test `test_markdown_historia_y_escenas_arriba` |
| 8 | Escaleta con ficha: historia y escenas antes de hechos, `escena_idx`, esquema aparte | OK | `ficha_section`, `SCHEMA_FICHA`, `ficha_notes`. `ficha_notes` no rechaza nada, solo avisa |
| 9 | Escaleta sin ficha byte-idéntica | OK | Lo corrí contra `git show HEAD:script_engine/m01a_escaleta.py`: `build_prompt` igual con `fb=None` y con feedback; `SYSTEM`, `SCHEMA` y `RULES` iguales |
| 10 | Bloqueante (d) mira `personas_descartadas` | OK | `pool_sin_rescatados` pasa una copia del pool (no lo toca) a `m05.contamination`. Cambia la fuente, no el criterio. `reparar`, `editor_pass` y fase1_5.py:260 propagan la ficha. Test propio verde |
| 11 | Tests y suites | OK | `pytest f15, f14, f13, f12, f11, f11b, f11c`: 75 passed. No corrí la suite amplia (621 + 5 previas) ni el dorado v3: NO VERIFICABLE por mí. Los tests de F15 no detectaron el defecto del punto 1 |
| 12 | Corridas: Ycuá y Orleans, Sol high, sin reparación ni editor | PARCIAL | Existen las salidas pedidas. Pero el guion de ambas corridas usó el sistema contaminado (punto 1) |
| 13 | Costo de US$ 2.50 o menos | OK | costos_f15.json suma 1.8739, igual que el reporte §7 |
| 14 | `compara_f15.html` y salidas | OK | `f15_compara.py` corre sin API: 1451 → 763 palabras y 11.8 → 6.2 min en Orleans, bloq 0, preguntas 0. Los números de §3 coinciden con la salida |
| 15 | Frenos | OK | `git status` no muestra pool_v3, research_v3, m05, evidence, guion_v3_reglas, config ni topics_db. Fichas previas respaldadas en `_f12` y `_f14` |
| 16 | `ESTADO_SESION.md` actualizado | OK | Está modificado; no leí su contenido línea por línea |

Evaluaciones pedidas
- (a) Reintento de la escaleta de Orleans: rechazada en 3 intentos por una regla ya existente (un hecho, una cifra: D533 contra D214, 5.919). Se volvió a correr la etapa entera, otros 2 intentos, dentro del tope. Está declarado y costeado por separado (0.3514 + 0.2199). Aun así es un segundo sorteo sobre una etapa que había fallado. No consta que se haya registrado qué cambió entre pases (el prompt era el mismo). Es una observación, no una falla.
- (b) Decisiones de §1: «CAP n (función)» como unión de las funciones de sus beats, quién de la VERSIÓN DE y quitar «lo que abre el cap N» son interpretaciones del formato USUARIO del .md. Las dos primeras se declaran y son aceptables. Quitar «lo que abre» es una omisión declarada que el analista debe aprobar.
- (c) Números del reporte contra archivos: coinciden el costo, las palabras, minutos, embudos y bloqueantes (por `f15_compara.py`). No coincide el md5/literalidad del sistema de guion (§1, 1.ª fila).

Fuera de alcance: ninguno. Los archivos tocados son los declarados: fase1_5.py, ficha_caso.py, guion_v4.py, m01a_escaleta.py, los test_module_f11 a f14 y test_module_f15.py, ESTADO_SESION.md y lab/hyperframes/f15/. No toqué diag_234_cap4.py ni gfx_profiles/*.

Qué hay que arreglar antes de avanzar: extraer el bloque desde "## SISTEMA\n\n<rol>" o desde el `<rol>` de la línea 11; corregir el test para que ancle en ese punto y compare contra el bloque real; re-correr los dos guiones (unos 0.23 USD, entran en el tope, quedan unos 0.63) y rehacer §1, §3 y los números de largo del reporte.

Riesgos que el contrato no cubre
- El bloqueante (d) matchea por subcadena de nombre; un apellido corto en `personas_descartadas` podría silenciar contaminación real.
- El control de sentidos por raíz de 5 letras descarta escenas válidas (§6) y deja pasar algunas inventadas.
- `_steps/<tema>/ficha_caso.json` quedó en v2 y se lee solo (`ficha="auto"`). Re-correr F13 o F14 desde ahí usa otra ficha.
