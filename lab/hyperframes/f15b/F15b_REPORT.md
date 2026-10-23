# F15b — v5.1: la escena merece un párrafo · Ycuá y Orleans — REPORTE → PARADA

CC · 2026-10-23 · rama `f11-guion-v4` (desde `0055e14`). Handoff: `HANDOFF_F15b_escena_por_parrafo.md`. Solo ficha → escaleta → guion.

**En una línea:** el v5.1 hace lo que pide. **Las frases por párrafo se duplican** (Ycuá de 2.0 a 4.0, Orleans de 2.2 a 3.9) y **los párrafos de una sola frase bajan** (Ycuá de 14 a 3, Orleans de 7 a 3). El gancho de Ycuá vuelve a abrir con las cenizas. Los dos guiones duran **7.0 min**, sin bloqueantes ni preguntas.

**Pero la escaleta nueva de Ycuá no salió:** 3 pases y 7 intentos, todos rechazados por reglas que ya existían. El freno de costo cortó y la dejo en **PARADA**. Para que el analista pueda leer el v5.1 en Ycuá, corrí su guion v5.1 **sobre la escaleta de F15**: es un sustituto, marcado así en todos lados. Costo: **US$ 1.321** de 1.50.

Para leer:
- `compara_f15b.html`: F15 al lado de F15b por cap. Se lee en el teléfono.
- `NARRACION_orleans_f15b.md` y `NARRACION_ycua_f15b_escf15.md` (el sustituto).
- `ESCALETA_orleans_f15b.md`.
- `ficha_{ycua,orleans}/FICHA_*_f15b.md` (las fichas re-chequeadas).

## 1. md5 del prompt v5.1 contra el archivo

| archivo del analista | md5 del archivo | lo que se usa | md5 de lo que se manda |
|---|---|---|---|
| `lab/hyperframes/f15/PROMPT_GUIONISTA_v5_1.md` | `6dcc4294660082645a02f6fc1bba747d` | bloque SISTEMA (desde «## SISTEMA», de `<rol>` a `</errores>`) = `guion_v4.SYSTEM_V5_1` | **`cdce609abea95ee36d0eb4f44d74dda8`** (8,772 caracteres), igual en los dos temas |

- El v5.1 es el v5 más los tres agregados del analista, literales:
  - en `<voz>`: «Una escena merece un párrafo entero…»;
  - en `<estructura>` 7: «…bien contado significa con su escena…»;
  - en `<errores>`: «Telegrama» y «Gancho abstracto».
- La `<tarea>` del archivo es la misma que la del v5 (verificado), así que el usuario no cambia.
- `PROMPT_VERSION = "f15b-1"`. El v5 sigue disponible con `version="f15-1"` y es byte-idéntico (el test lo compara contra el .md del v5).
- `test_module_f15b.py` lee el `.md` del v5.1 y lo compara byte a byte con `system()`; también verifica que los cuatro textos nuevos estén en el v5.1 y no en el v5. Los .md se leen en LF, por `autocrlf`.
- Se ajustaron 5 aserciones de `test_module_f15.py` para pedir el v5 explícitamente, y 1 por el mensaje nuevo de los sentidos (§1.3).

## 2. Lo que se implementó

- **Escaleta** (`m01a_escaleta`, solo con ficha):
  - El encabezado de ESCENAS dice ahora, literal: «El beat 1 (gancho) y el beat del pico toman su `imagen_sensorial` de una escena de la ficha cuando hay una para ese momento; los demás beats, cuando sirva.» Agregué: «El beat que usa una escena lleva su número en `escena_idx`.»
  - Si el beat 1 no cita escena, va a `_avisos` «gancho sin escena de la ficha». No rechaza nada.
  - Sin ficha, el prompt sigue byte-idéntico (test con los md5 de F14).
- **Chequeo de la ficha** (`ficha_caso.problems`), dos aflojes:
  - **Cifras:** los dos lados se normalizan como pide el handoff (sin separadores de miles, «G.», «$», «US$», «°» ni espacios entre grupos: 4.500 = 4500 = 4,500 = 4 500).
    - **Ese afloje literal no recuperaba ninguna de las 12 cifras de Ycuá:** 8 están en letras en el pool («seis personas», «cinco integrantes», «quince días», «diez días»…) y 4 en millones («G. 4.500 millones»; la ficha escribe «4.500.000.000»).
    - Le pregunté a Omar y eligió ampliarlo: ahora también se leen los **números en letras** (de «cero» a «novecientos», con decenas y «mil»; un número no cruza la puntuación) y la **escala** («millones», «mil millones», «mil»).
    - Lo que no está sigue afuera; el test lo verifica con «7» y «4.600.000.000». «un» y «una» no cuentan como números (son artículos); esto se arregló después del veredicto del revisor y no cambia el re-chequeo.
  - **Sentidos:** alcanza con **una** palabra de contenido del campo `sentidos` (con su raíz de 5 letras) presente en el texto de sus ids. Antes hacía falta una por tramo.
- **Tests:** `test_module_f15b.py` (7, sin red).
  - v5.1 byte-idéntico, y el usuario igual al del v5.
  - Escaleta sin ficha intacta, y con ficha el texto nuevo.
  - El aviso «gancho sin escena».
  - **Las 12 cifras de Ycuá respaldadas**, con sus pasajes literales.
  - La normalización.
  - Una escena con un solo sentido respaldado.
  - **Suite amplia: 628 verdes + las 5 fallas previas** (3 `01b_pauses`, 2 `m03_merge_timing`). `test_v3_byte_identico`, verde.

## 3. Re-chequeo de las fichas (sin llamada)

Se usaron las fichas v2 de F15: el crudo del modelo, `lab/hyperframes/f15/ficha_crudo_*.json`, con `ficha_caso.save`. Antes, se respaldó la de F15 en `_steps/<topic>/ficha_caso_f15.json`.

| | sacados F15 | sacados F15b | vuelven | lo que vuelve |
|---|---|---|---|---|
| Ycuá | 17 | **0** | **17** | **las 12 cifras** (desaparecidos, hijas de Ángela Pujol, familias López y Roa, internaciones, puertas, las 4 indemnizaciones) y **5 escenas** (la cena y el baile de Blas y Estela, el primer sueldo de Mario, Sosa y las llamas, la cajera que salta, la marcha) |
| Orleans | 20 | 14 | 6 | 5 escenas (el colectivo a OPP, el humo de los incendios, las mujeres atadas, el gas pimienta, los sándwiches por encima de la cerca) y 1 cifra (la duración de la investigación de la ACLU) |

- Ycuá queda con **41 cifras y 14 escenas**; Orleans, con **23 cifras y 15 escenas**.
- Los 14 de Orleans que **siguen afuera** no están respaldados por sus ids:
  - 5 internos «#5», «#6»… en `personas_descartadas` (no están entre los descartados del pool);
  - 2 citas corregidas a 13 y 94 caracteres del original;
  - cifras que no aparecen en sus ids: «84» (fin de la evacuación), «91» (cocina de Hunt), «0» (muertes reconocidas por el sheriff), «175» y «220» (números de internos usados como hora);
  - la fecha 2005-08-27;
  - 1 descartado sin ids.

## 4. Tabla F15 | F15b

### Ycuá

| versión | palabras | min | párrafos | frases por párrafo | párrafos de 1 frase | escenas usadas | gancho / pico con escena | bloq. | duras v3 | citas | preguntas | humano (caps en escena) | pico |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F15 · v5 | 755 | 6.1 | 37 | **2.0** | **14** | — | no / no | 0 | 31 | 10 | 0 | Liz Torres (1) | beat 8 · Q20 |
| **F15b · v5.1 sobre la escaleta F15** (sustituto) | **858** | **7.0** | 20 | **4.0** | **3** | — (la misma escaleta) | no / no | 0 | 32 | 9 | 0 | Liz Torres (1) | beat 8 · Q20 |

- Frases por párrafo, por cap: F15 2.3 · 2.6 · 1.8 · 1.5 · 1.9 · 2.0 · 2.0; **F15b 3.5 · 4.7 · 3.7 · 2.7 · 4.2 · 5.0 · 4.3**.
- **Gancho:**
  - F15: «Una avalancha de cuerpos empuja hacia adentro. Según una sobreviviente, cuando empezó el fuego alguien dio la orden…»
  - **F15b:** «Las cenizas flotan en el aire caliente. Según una sobreviviente, cuando empezó el fuego alguien dio la orden de cerrar las puertas, y cientos de personas no consiguieron salir. Liz Torres, sobreviviente y activista, está atrapada en una avalancha de cuerpos que empuja hacia adentro. Piensa en los hijos adolescentes que puede dejar solos. "Cuando sentí la avalancha, dije acá nos morimos todos, no me voy a salvar", recordó Liz.»
- **Cierre:** «Liz pide: "Que nunca más ocurra un 1A".»
- Las dos usan la misma escaleta (la de F15, sin escenas), así que **la diferencia es solo del prompt**. El mensaje de usuario cambia un poco (md5 `81fba5af…` contra `0a0bf276…` en F15), porque la ficha re-chequeada devuelve cifras que dan el texto de algunos ids.

### Orleans

| versión | palabras | min | párrafos | frases por párrafo | párrafos de 1 frase | escenas usadas | gancho / pico con escena | bloq. | duras v3 | citas | preguntas | humano (caps en escena) | pico |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F15 · v5 | 866 | 7.0 | 32 | **2.2** | **7** | E2, E3, E5, E7, E10 | no / sí (E7) | 0 | 36 | 9 | 0 | Brady Richard (1, 2, 4, 5, 7) | beat 9 · D155 |
| **F15b · v5.1** | **867** | **7.0** | 19 | **3.9** | **3** | E9, E11 | **no / sí (E9)** | 0 | 31 | 6 | 0 | **Edward «Edgar» Burton** (1, 3, 4, 5, 6, 7) | beat 8 · D155 |

- Frases por párrafo, por cap: F15 1.7 · 2.5 · 2.8 · 2.0 · 2.8 · 2.0 · 1.3; **F15b 3.5 · 5.5 · 5.5 · 3.7 · 3.8 · 3.0 · 3.5**.
- **Escaleta:** el humano es otro candidato de la ficha (Burton). El pico (D155, Iris Hardeman sostenida sobre el agua) toma una escena (E9). **El gancho no**: su imagen es «oscuridad total que no te deja ver la mano delante de la cara», sin `escena_idx`, y queda el aviso «gancho sin escena de la ficha».
- **Gancho:** «La oscuridad no deja ver una mano delante de la cara. Miles de prisioneros han quedado atrapados en celdas inundadas; una orden los dejó fuera de la evacuación. Edward "Edgar" Burton, preso de Old Parish, sigue encerrado. Nadie viene a abrir su celda. Dan Bright lo recuerda así: "Nos dejaron morir allí."»
- **Cierre:** «Burton recuerda lo que aquellos hombres le dijeron: "Nos dijeron que no quedaba nadie."»
- **Lectura:** el mismo largo (867 palabras), pero en 19 párrafos en lugar de 32.

## 5. La escaleta de Ycuá (PARADA)

| pase | intentos | US$ | lo que rechazó (reglas que ya existían) |
|---|---|---|---|
| 1 | 3 | 0.3243 | la intensidad baja en el beat 2 (sin `flash_forward`); Liz Torres en escena en el beat 7 sin un dato suyo verificado (Q20 está sin verificar); preguntas de pantalla; la última frase repite textual Q14 |
| 2 | 2 (el freno de costo cortó el 3.º) | 0.2305 | dato central L40 (un lugar); la intensidad baja en el beat 2; Liz en escena sin dato verificado (beats 8 y 12) |
| 3 | 2 (el freno cortó el 3.º) | 0.2340 | dato central P70 (una persona); preguntas de pantalla; la intensidad baja en el beat 2; Liz en escena sin dato verificado (beat 8) |

- **Lo que se repite:** la curva de intensidad cae en el beat 2 en los tres pases; la escaleta no marca `flash_forward` aunque el gancho sale de un momento posterior y más intenso (las cenizas). Y Liz Torres aparece en escena con Q20, que está sin verificar.
- La instrucción nueva («el gancho toma su imagen de una escena») empuja el beat 1 hacia el peor momento, y eso choca con la regla de la curva si el modelo no lo marca como flash-forward.
- No toqué ninguna regla: queda para el analista. Opciones: un pase más con presupuesto, o que el texto de ESCENAS nombre `flash_forward`.
- **El freno funcionó como está escrito:** antes de cada intento exige que lo gastado + US$ 0.30 (peor caso de un intento de Pro) + la reserva para lo que falta no pase US$ 1.50.
- El sustituto (guion v5.1 sobre la escaleta F15) costó US$ 0.163. Lo agregué para que el analista pueda leer la voz v5.1 en Ycuá; **no es la corrida que pide el handoff**.

## 6. Costo y tokens

| tema · etapa | modelo | intentos o llamadas | entrada | salida | razonamiento / thinking | US$ | resultado |
|---|---|---|---|---|---|---|---|
| (fichas) re-chequeo | — | 0 | — | — | — | 0.0000 | sin llamada |
| Ycuá · escaleta, pase 1 | gemini-2.5-pro | 3 | ≈ 24.3 k c/u | ≈ 3.0 k c/u | 5,591 / 4,126 / 4,535 | 0.3243 | rechazada |
| Ycuá · escaleta, pase 2 | gemini-2.5-pro | 2 | ≈ 24.3 k c/u | ≈ 3.1 k c/u | 5,556 / 5,240 | 0.2305 | freno de costo |
| Orleans · escaleta | gemini-2.5-pro | 2 | 21,539 / 21,721 | 3,389 / 3,673 | 5,965 / 3,768 | 0.2220 | aceptada |
| Orleans · guion v5.1 | gpt-6.1-sol high | 1 | 6,129 | 1,658 | 11,832 | 0.1472 | 867 palabras |
| Ycuá · escaleta, pase 3 | gemini-2.5-pro | 2 | ≈ 24.4 k c/u | ≈ 3.4 k c/u | 5,085 / 5,329 | 0.2340 | freno de costo |
| Ycuá · guion v5.1 sobre la escaleta F15 (sustituto) | gpt-6.1-sol high | 1 | 6,190 | 1,750 | 13,308 | 0.1630 | 858 palabras |
| **tanda F15b** | | | | | | **1.3210** (tope 1.50) | |

Las md5 de cada prompt están en `prompt_<tema>_f15b*_{escaleta,guion}.txt`.

## 7. Frenos

- No se tocaron el pool (md5 verificados), `research_v3`, `m05`, `evidence.py`, `guion_v3_reglas.py`, `config.py` ni `topics_db`.
- Cero reglas nuevas para el guion: los tres cambios del prompt son texto al modelo. En la escaleta solo hay un aviso nuevo, que no rechaza nada. Los aflojes son de la ficha.
- Nada anterior se pisó:
  - fichas F15 respaldadas como `ficha_caso_f15.json`;
  - escaletas: las de F15 quedan como `_f15`, y la nueva de Orleans es `01a_escaleta_f15b.json`;
  - guiones nuevos con sufijo `_f15b`.
- **Ojo:** `_steps/<topic>/ficha_caso.json` es ahora la versión re-chequeada (F15b) en los dos temas, y el pipeline la lee solo.
- Sin merge. `.env` y `lab/_gpt_probe_analista/` no se commitean. Sin producción.

## 8. Veredicto del revisor-handoff (íntegro)

Notas de CC, después del veredicto:
- **Riesgo 1 (artículos como «1»):** arreglado. «un» y «una» ya no cuentan como números en letras; «uno» sí. Agregué un test: «1 sobreviviente» contra «una vez, un día…» → «cifra 1» queda afuera. Re-chequeé las dos fichas con y sin el arreglo y **el resultado es idéntico** (mismos conteos y mismos sacados), así que las escaletas y los guiones de esta tanda no cambian.
- **Observación 3 (la frase agregada al texto de ESCENAS):** está declarada en §2 del reporte. Es la mecánica de `escena_idx`, que el handoff nombra en §1.2 («si no cita escena…»).
- **`PROMPT_GUIONISTA_v5_1.md`:** va en este commit, junto con el handoff de F15b.

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Prompt v5.1 literal en el bloque SISTEMA | OK | Calculé el bloque desde el .md (de "## SISTEMA", `<rol>`, a `</errores>`): 8,772 caracteres, md5 cdce609a…, y `guion_v4.system()==bloque` da True. Ese bloque está dentro de `prompt_orleans_f15b_guion.txt` y de `prompt_ycua_f15b_escf15_guion.txt`; ambos traen en la cabecera el mismo md5. El md5 del archivo, 6dcc4294…, coincide con el reporte. |
| 2 | Cambios del v5.1 = solo los 3 pedidos | OK | `diff` del v5 contra el v5.1: título, línea en `<voz>`, frase en `<estructura>` 7 y dos errores («Telegrama», «Gancho abstracto»). Nada más. `PROMPT_VERSION="f15b-1"`; el v5 sigue con `version="f15-1"`. |
| 3 | Escaleta: texto de ESCENAS, aviso, sin ficha byte-idéntico | OK con una observación | `m01a_escaleta.py` `ficha_section` trae el texto literal del handoff. Agregó una frase no pedida: «El beat que usa una escena lleva su número en `escena_idx`». `ficha_notes` solo agrega a `_avisos` «gancho sin escena de la ficha» y no rechaza. En `escaleta_orleans_f15b.json` el aviso aparece. El diff de la escaleta toca solo el bloque con ficha; el test de "sin ficha" pasa. |
| 4 | Afloje de sentidos: basta una palabra de contenido | OK | `ficha_caso.sentidos_problems`. Lo que no tiene respaldo sigue a descartados. `test_module_f15` quedó ajustado al mensaje nuevo. |
| 5 | Afloje de cifras | OK con una observación | La normalización literal del handoff está en `_canon`. La ampliación (números en letras y escala) está en `_SCALE` y `word_numbers`. Lo que no está sigue afuera: `unsupported('… 7 … 4.600.000.000 … 3 hijos', …)` devolvió `['cifra 7','cifra 4.600.000.000','cifra 3']`, y «G. 4.500 millones» contra «4.500.000.000» sí pasa. Ver riesgo 1. |
| 6 | Tests y suites | OK | Corrí las 8 suites: 82 passed en 4.99 s. No volví a medir la suite amplia (628 verdes + 5 previas). |
| 7 | Corridas y costo | OK | Las 7 filas de costo del reporte suman 1.3210 (0.3243+0.2305+0.2220+0.1472+0.2340+0.1630), bajo el tope de 1.50. Los intentos de Ycuá, 3+2+2=7, coinciden con la §5. `f15b_compara.py` corre sin APIs y reproduce la tabla: Ycuá F15 755 palabras, 2.0 frases por párrafo y 14 párrafos de una frase, contra F15b 858, 4.0 y 3; Orleans 866 / 2.2 / 7 contra 867 / 3.9 / 3. `compara_f15b.html` existe (38 KB). |
| 8 | Escaleta nueva de Ycuá | FALLA, declarada | No salió: la §5 y `costos_f15b.json` registran PARADA con `EscaletaValidationError`. El handoff pedía esta escaleta. |
| 9 | Sustituto de Ycuá (guion v5.1 sobre la escaleta F15) | OK | Está marcado como sustituto en el reporte (líneas 7, 75, 82, 109), en el nombre del archivo (`_escf15`) y en el prompt. Dice "no es la corrida que pide el handoff". Con la escaleta F15, gancho y pico no tienen escena, así que no prueba la hipótesis de las escenas. Sí aísla el efecto del prompt, y el reporte lo dice. |
| 10 | Reporte | PARCIAL | La §4 del handoff pide cuatro puntos y los cuatro están. Los números del reporte coinciden con los archivos. El quinto punto es el veredicto, el que va en la §8. |
| 11 | Frenos (pool, research_v3, m05, evidence.py, guion_v3_reglas.py, config.py, topics_db) | OK | El `git diff --stat` muestra solo ficha_caso.py, guion_v4.py, m01a_escaleta.py, los tests y ESTADO_SESION. No hay reglas nuevas para el guion: el aviso no rechaza y los aflojes son de la ficha. |

Evaluación de los desvíos:
- (1) Afloje de cifras: está bien justificado y bien declarado. Omar lo eligió en el chat, y el reporte dice que el literal no recuperaba ninguna de las 12 cifras. Los casos que debían quedar afuera siguen afuera. Pero es un desvío del literal del handoff y conviene que el analista lo apruebe expresamente.
- (2) Ycuá en PARADA con sustituto: está bien declarado. El reporte distingue qué mide el sustituto y qué no.

Resultado de fondo (verificado en los archivos):
- La escaleta de Orleans cita escena en el pico (E9) y en un segundo beat (E11), pero no en el gancho. Queda el aviso «gancho sin escena de la ficha».
- Con el v5.1 suben las frases por párrafo y bajan los párrafos de una frase, en los dos temas.
- Lo único que cambia el texto del guion es el prompt. En Ycuá el usuario también varía algo (md5 81fba5af… contra 0a0bf276…), por las cifras que volvieron con el re-chequeo.

Fuera de alcance: ninguno entre los archivos versionados con cambios (`diag_234_cap4.py` y `gfx_profiles/*` ya estaban modificados antes y los ignoré, como pediste). `PROMPT_GUIONISTA_v5_1.md` aparece sin trackear (es el prompt del analista y es entregable). Los archivos de `_steps` y `lab/hyperframes/f15b/` quedan sin commitear.

Riesgos que el contrato no cubre:
1. Con los números en letras, «un», «una», «uno» y «dos» cuentan como cifras del texto fuente. Probé `numbers('una vez, un día, tres veces')` y devolvió {'1','3'}. Por eso cualquier cifra «1» de la ficha queda respaldada por un artículo cualquiera del pool. Es un hueco real del afloje ampliado, no de la parte literal.
2. `_steps/<tema>/ficha_caso.json` quedó reemplazado por la versión re-chequeada, y el pipeline la lee solo. La de F15 queda como `ficha_caso_f15.json`.
3. El choque entre «el gancho toma la imagen más fuerte» y la regla de la curva de intensidad (sin `flash_forward`) quedó como decisión pendiente para el analista.
