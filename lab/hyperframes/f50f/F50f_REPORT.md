# F50f — El canon pasa a Opus en producción + Wittenoom en texto (la D de F50d) · PARADA

Handoff `lab/hyperframes/f50f/HANDOFF_F50f_canon_opus_y_papel.md`, md5 `ac68add9aa78673b7ffdd1833b43c59e` (verificado). Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`, rama `f11-guion-v4`. Tope US$ 3,00; gastado **US$ 2,6735**: canon 0,3415 + m03 2,3320. **Cero fotos, cero clips.**

## Qué pasó, en llano
- **Producción:** el canon visual ahora lo arma Claude Opus 5.5, en una llamada sin esquema, igual que se midió en F50e.
  - Se borraron el camino Flash y sus esquemas.
  - Si el canon no sale, el pipeline frena; ya no hay canon vacío de respaldo.
  - La marca del canon incluye el modelo.
- **El canon nuevo de Wittenoom** cubre las 96 fotos con 4 tramos de época (1937-1945 · 1946-1966 · 1967-1992 · 1993-2026) y no deja ningún grupo con años sin ropa.
- **Los pedidos en seco** solo cambian en el bloque del canon y en los grupos. Los caps 5–7 ya traen la época de 1967 en adelante.
- **Wittenoom en texto (D):** 96 fotos, 0 sin tramo, 0 nombres propios. 2 fotos de 1967+ nombran los 60, y las dos están bien: una chica en 1971 con un vestido de fines de los 60, y fotos familiares de los 60 en una casa de 2023.
- **Bug nuevo, a arreglar antes de F51:** el canon de Opus trae personas documentadas solo por apellido, y algunos son palabras comunes. El filtro de nombres de la prosa reemplazó «Court» (Richard Court, premier) dentro de «Federal Court» y «Supreme Court». En 2 fotos (6/3 y 7/11) el prompt quedó roto, y en 7/11 también el cartel.

## Paso 0
- La línea de DECISIONES 23:34 está tal cual.
- `lab/TOPE_TANDA.json` = `{"usd": 3.0, "desde": "2026-10-28T23:38:47"}` (fuera de git).

## Commits
| parte | commit |
|---|---|
| A (código y tests) + paso 0 | `e4bb427` |
| B (canon) | `f4ddafc` |
| C (pedidos en seco) | `41e1e7a` |
| D (m03 en texto y papel) | `00b178b` |
| reporte | este commit |

## A. Código (US$ 0)
**Grep antes de borrar** (fuera de `lab/`, sin los scripts `_lab*`, `_probe*`, `_run*`, `diag_*` ni `_dump*`):
- `_VISUAL_CANON_SCHEMA` y `VISUAL_CANON_SCHEMA_FICHA`: solo los usaba `test_module_f50d.py`, en 2 tests de esquema, que se borraron o adaptaron.
- `_ERA_SCHEMA`, `_GRUPO_SCHEMA`, `_PERIODO_SCHEMA`, `_ROPA_TRAMO_SCHEMA` y `_empty_canon`: sin usos fuera de `step_4e`.
- `_STR` y `genai_types`: en `step_4e` solo servían para los esquemas. Los de otros módulos (`gfx_critic`, `gfx_vision`, `make_bug`, `m05_judge`…) son otros nombres u otro uso.
- `call_flash_json`: queda en `gemini_helpers` y lo siguen usando `qa_studio_server` y `cost_tracker`. Solo se sacó su import de `step_4e`.
- `extract_visual_canon`: lo usaba `test_module_00_4e.py`, el lab del camino Flash, que llama a la API. Se borró con el camino.
- `_probe_4e_schema_path.py`: no lo usa nadie y no estaba en git. Se borró. Solo aparece en `lab/mapa/tests_lab.json`, una foto fija.

Nada de producción usaba lo borrado.

Cambios:
- **`step_4e_visual_canon.py`**:
  - constantes `MODELO_CANON = "claude-opus-5-5"` y `ESFUERZO_CANON = "high"`, con su línea de DECISIONES;
  - `CanonError`;
  - `extract_visual_canon` hace **una** llamada `claude_helpers.call_json(prompt, model=MODELO_CANON, effort=ESFUERZO_CANON)`, sin `response_schema`;
  - `CanonError` sin hechos, si la llamada falla, si la respuesta no es un objeto o si no trae `era_visual_canon.periods` y `people_groups`;
  - la limpieza de campos se queda.
  - Se borraron el camino Flash con su respaldo sin esquema y el canon vacío, los esquemas `_VISUAL_CANON_SCHEMA`, `VISUAL_CANON_SCHEMA_FICHA`, `_ERA_SCHEMA`, `_GRUPO_SCHEMA`, `_PERIODO_SCHEMA` y `_ROPA_TRAMO_SCHEMA`, y además `_STR`, `_empty_canon` y los imports de genai y Flash.
  - **El texto del pedido no cambió:** md5 `d2568e2a…`, el mismo de F50e.
- **`fase1_5.asegurar_canon`**:
  - marca = md5(ficha + pedido + `MODELO_CANON|ESFUERZO_CANON`);
  - `CanonError` → Parada;
  - algún `periods[].years` que `m03_visual._tramo` no lee → Parada con la lista.
- **`m03_visual`**:
  - `_log_sin_period` deja una línea por cap: «cap N: X de Y fotos sin period → año: tramo dado». Solo mide, no frena, y no se imprime en las re-hechuras.
  - La regla del más cercano no cambia.
- **Tests:**
  - `test_module_f50f.py`, 11 tests nuevos:
    - la llamada va a Opus con effort y sin esquema (con un `_post` falso, sin red);
    - un canon sin periods o sin grupos da error;
    - sin hechos, o si la API falla, da error;
    - lo viejo ya no está;
    - la marca cambia con el modelo, con el esfuerzo y con una letra;
    - `years` ilegible es Parada, y `CanonError` también;
    - la línea de log.
  - `test_module_f50a` y `test_module_f50d` se adaptaron a Claude, y se borró el test de esquema de f50d.
  - `test_module_00_4e.py` se borró.
- **Stickers** (research `step_4e`, también su campo `modelo`; guion `fase1_5`; fase2a `m03_visual`) y `MAPA_PROYECTO`. `--check` da «157 archivos de producción · 0 fallas».

## B. Canon de Wittenoom (US$ 0,3415) → PASA
`lab/hyperframes/f50f/canon_b.py`:
- corre `fase1_5.asegurar_canon` (marca `696c0995` → `a08c790c`), que guarda en topics_db y en `05_visual_canon.json`;
- antes, copia en `f50f/antes/`;
- mide 4a–4g con `f50e/canon_modelos.medir`.

| medida | valor |
|---|---|
| periods | 1937-1945 · 1946-1966 · 1967-1992 · 1993-2026 |
| fotos cubiertas | **96/96** (todos los caps completos) |
| grupos | 12 · con años sin ropa: **0** |
| years ilegibles | ninguno |
| grupos sin appearance | 2/12: `international_un_official`, `airport_police` |

Criterio de la tabla de constantes (100 % de las fotos y 0 grupos con años sin ropa): **PASA**. Detalle en `CANON_F50f.md`.

## C. Pedidos en seco (US$ 0) → PASA
`pedidos_f50d.py --salida lab/hyperframes/f50f` (se le agregó `--salida`) y `pedidos_f50f.py`, que verifica.

| cap | periods que entran | líneas fuera del canon y de los grupos |
|---|---|---:|
| 1 | 1946-1966 | 0 |
| 2 | 1946-1966 | 0 |
| 3 | 1937-1945 · 1946-1966 | 0 |
| 4 | 1946-1966 | 0 |
| 5 | 1946-1966 · 1967-1992 · 1993-2026 | 0 |
| 6 | 1967-1992 · 1993-2026 | 0 |
| 7 | 1993-2026 | 0 |

Los bloques ERA de los caps 5–7 están pegados en `PEDIDOS_F50f.md`. El del cap 7, por ejemplo: «period 1993-2026: Contemporary casual wear for Banjima traditional owners and activists; modern business attire…».

## D. Wittenoom en texto con Opus (US$ 2,3320)
`fase1_5 --topic … --only m03`, exit 0:
- casilleros con Opus: 8 llamadas, US$ 2,2249;
- movimiento de los 2 clips: 3 llamadas, 0,0284;
- anclas con Flash: 8 llamadas, 0,0788.

Antes, copia de `03_visual.json` (el de F50b) en `f50f/antes/`. Papel: `f50/papel.py --salida lab/hyperframes/f50f`.
```
fotos 96 (antes 96) · fuentes {'2) el casillero `year` del modelo': 67, '1) dicho en el ancla': 29} · rehechas 1 (video 0) · carteles 9 · US$ 2.332
```
Las anclas se volvieron a planear: 35 de 96 iguales a F50b y ningún prompt idéntico. La re-hechura es la 5/16 (encuadre cerrado del beat).

Las 5 medidas (`MEDIDAS_D.md`, `medidas_d.py`):
1. **Fotos de 1967+ con ropa, vehículos o tecnología de los 40–60:**
   - F50b: 0 de 39; **F50f: 2 de 39**. Las dos son legítimas:
     - 5/6 (1971): «late-1960s knee-length dress»;
     - 5/16 (2023): fotos familiares «from the early 1960s» en la pared.
   - Es una medida de lab: una lista de marcas de época (décadas 1940s–1960s y objetos o prendas típicos) buscada como palabra entera.
   - Saqué «forties/fifties/sixties», que en los prompts son edades («in their sixties»). Con ellas, la primera cuenta daba 8 en F50f y 1 en F50b, todas edades.
2. **Nombres propios en la prosa final: 0.** Se buscaron 126 formas: `ficha.personas` + `documented_people`.
3. **Las 8 testigo de F50c:**
   - Como D re-planea las anclas, se buscan por el texto del ancla, y solo 3 siguen siendo ancla. Las 3 tienen el sujeto de la persona de PEOPLE (lectura de CC):
     - 2/1, «pareja española de veintipico»: Daniel y María;
     - 2/7, «chico español de unos siete años con su madre»: Víctor Calvo;
     - 5/13, «hombre español de cincuenta y pico, en el médico»: Daniel padre, 1991.
   - Las otras 5 (1/3, 1/4, 3/7, 3/16, 5/9) ya no son ancla.
   - Además, `MEDIDAS_D.md` lista las 36 fotos nuevas cuya ancla nombra a una persona, con su sujeto, para la revisión del analista.
4. **Log de m03, fotos sin period:** 0 en los 7 caps (`[03] cap N: 0 de N fotos sin period`).
5. **Gasto por paso:** canon 0,3415 (01_v3_costos «canon») · m03 2,3320 (01_v3_costos «m03», cost_history del tema). Total de la tanda, **US$ 2,6735**.

## Verificación
| | antes (F50e-B, `f41/f50e_b`) | después (`f41/f50f`) |
|---|---|---|
| suite rápida | 55 passed, 3 skipped | 55 passed, 3 skipped (`f41/f50f_2`) |
| suite amplia | 4 failed, 976 passed, 30 skipped | 4 failed, 985 passed, 30 skipped (`f41/f50f_2`; 976 → 985: + los 11 de `test_module_f50f.py`, − el test de esquema borrado de f50d, y el conjunto de la amplia cambió por `test_module_f50*`) |
| ch02 md5 | `f792f3d4…` | `f792f3d483a1fa42daed5f7f0e054f46` (igual) |

Primera corrida (`f41/f50f`): 6 failed, 983 passed. Las fallas además de las 4 de siempre:
- **`test_module_f50c.py::test_f50c_a_fotos_testigo_de_wittenoom`:** leía las anclas del `03_visual.json` vivo, y D las re-planeó. Lo apunté a la copia congelada `lab/hyperframes/f50f/antes/03_visual.json` (el de F50b, el que usó F50c). Es un cambio de dato del test, no de código: el test sigue midiendo lo mismo.
- **`test_module_gfx_lab.py::test_candado_en_el_preview`:** es la intermitente con `-n auto` (ya vista en F50c). Corrido solo, `test_module_gfx_lab.py` da «2 failed, 43 passed», las 2 de siempre.

Segunda corrida (`f41/f50f_2`): solo las 4 de siempre (`m03_merge_timing` ×2, `gfx_lab` ×2).

## Lo que queda abierto
1. **Bug del filtro de nombres con apellidos que son palabras comunes. Hay que arreglarlo antes de F51.**
   - El canon de Opus trae `documented_people` con nombres de un solo apellido: «Court», «Major», «Wright», «Mercedes», «Davidson», «Hancock», «Chifley».
   - `name_matching.scrub_documented_names` reemplaza cada nombre por su descriptor. Los nombres completos los busca sin distinguir mayúsculas; el apellido suelto, respetándolas (`(?-i:)`), y por eso «Court» con mayúscula, como en «Federal Court», rompe. `iter_name_patterns` solo descarta apellidos de menos de 5 letras o de su lista negra, y «Court» no está.
   - En el papel de F50f rompió **6/3** («A wood-panelled 1988 Perth Supreme a State premier whose government rejected … courtroom») y **7/11**: en el lugar y en el cartel «FEDERAL a State premier whose …».
   - Las otras palabras («major», «wright», «mercedes») no aparecen hoy en los prompts, pero el riesgo es el mismo en cualquier tema.
   - El arreglo (nombres solo completos, mayúscula, o no tomar un apellido suelto que es palabra común) es una regla nueva y va con el simulador. Es una decisión del analista.
2. **Grupos sin appearance:** `airport_police` y `international_un_official`. El pedido manda dejarlo vacío si el material no da el origen.
3. **La foto madre** sigue vacía en topics_db; se rehace en F51 (DECISIONES 21:23).
4. **La medida 1 es por lista de palabras:** no ve la ropa de época descrita sin marca («a pressed dark suit» puede ser de cualquier década). La revisión DEBERÍA del analista sobre el papel es la que cuenta.
5. **Testigo:** las anclas se re-planean en cada corrida, así que 5 de las 8 testigo de F50c ya no existen. Para medir «sujeto = persona» hace falta una lista de testigos por texto, no por posición.
6. **El mapa sigue listando `test_module_00_4e.py`** como «historia». La lista de tests sale de `lab/mapa/tests_collect.json` / `tests_lab.json`, fotos fijas que esta tanda no regenera, y `test_module_f50f.py` tampoco figura todavía.
7. **Cada canon cuesta ahora ~US$ 0,34** (Opus) contra ~0,03 (Flash), y tarda ~130 s.
8. **La regla del «más cercano»** sigue en el código y hoy no se activa en Wittenoom (0 fotos sin period).
9. **Carteles:** 9.
   - En 7/11, «Federal Court» lo rompió el bug del punto 1.
   - Las mayúsculas del modelo en los casilleros del cartel («Carved block capitals», «Over the main entrance») las baja `_minuscula_media`; en 7/11 no llegaron a verse por el bug.
10. **De tandas anteriores:**
    - F50e: el esquema de 46 opcionales ya no aplica, porque se borró.
    - F50d: la verificación de B con canon nuevo.
    - F50c: los nombres reales por las citas, que siguen entrando al pedido.
    - F50b: las notas F8 viejas.
    - F50: n2, n3, n7, n8, n10 y n12.
    - Veo 3.1 en fal se apaga el 2026-11-17.

## Procesos
En segundo plano corrieron `canon_b.py` (1 llamada a Opus; exit 0), `fase1_5 --only m03` (exit 0) y `verificar.sh f50f`; `f50f_2` corrió en primer plano. No queda nada corriendo. No se cerró ningún programa de Omar.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

Todo lo que el contrato pide se cumple y lo verifiqué. Las observaciones son de forma o de transparencia. No encontré ningún incumplimiento de fondo.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 0 | md5 del handoff, línea de DECISIONES tal cual, TOPE_TANDA 3,00 | OK | `md5sum` = ac68add9aa78673b7ffdd1833b43c59e. DECISIONES.md tiene la línea 23:34 idéntica al handoff. `lab/TOPE_TANDA.json` = {"usd":3.0,"desde":"2026-10-28T23:38:47"}. |
| 1a | step_4e hace UNA llamada a Opus, sin esquema, con constantes | OK | `step_4e_visual_canon.py`: `MODELO_CANON="claude-opus-5-5"`, `ESFUERZO_CANON="high"`, `claude_helpers.call_json(prompt, model=, effort=, description=)` sin `response_schema`. `test_f50f_la_llamada_va_a_opus...` verifica con un `_post` falso que `output_config` no trae `format`. |
| 1b | Excepción y no canon vacío | OK | `CanonError` cuando no hay hechos, falla la API, la respuesta no es un objeto, o faltan `periods` o `people_groups`. Hay 3 tests parametrizados y uno de API caída. |
| 1c | Borrados con su grep | OK | El grep está pegado en el reporte, sección A. Yo repetí el grep fuera de `lab/` y de los scripts `_lab/_probe/diag` sobre `_VISUAL_CANON_SCHEMA`, `_ERA_SCHEMA`, `_GRUPO_SCHEMA`, `_PERIODO_SCHEMA`, `_ROPA_TRAMO_SCHEMA`, `_empty_canon` y `_probe_4e_schema_path`: 0 usos. `call_flash_json` sigue en `gemini_helpers` porque otros módulos lo usan, y solo se quitó su import de step_4e. `test_module_00_4e.py` está borrado en el commit. `migrate_4e_into_topics_db.py` lo nombra solo en un comentario. |
| 1d | El texto del pedido no cambió (md5 d2568e2a…) | OK | Recalculé `pedido_canon` sobre la ficha y el topic de Wittenoom: md5 d2568e2a94c5db96f9836451b2f80cd7. |
| 2a | Marca = md5(ficha + pedido + modelo + esfuerzo) | OK | `marca_canon` en step_4e. `test_f50f_marca_cambia...` prueba que cambian el modelo, el esfuerzo y una letra. La marca de topics_db es a08c790c, igual a la de `CANON_F50f.md`. |
| 2b | Parada por `years` ilegible y por `CanonError` | OK | `fase1_5.asegurar_canon` usa `m03v._tramo`. Los tests `test_f50f_years_ilegible_es_parada` y `test_f50f_canon_que_no_sale_es_parada` pasan. |
| 3 | Línea de log de m03: medida, no freno | OK | `m03_visual._log_sin_period` solo hace `print`, sin raise, y no se imprime en las re-hechuras. Hay un test. El log de D muestra "0 de N fotos sin period" en los 7 caps. |
| 4B | B: canon por `asegurar_canon`, copia en antes/, medida 4a–4g | OK | `CANON_F50f.md`: 96/96 fotos, 4 tramos, 12 grupos, 0 con años sin ropa, 0 years ilegibles. Los 2 grupos sin appearance quedan declarados. `antes/` tiene los 3 archivos. |
| 4C | C: 0 líneas fuera del canon y de los grupos; caps 5–7 con 1967+ | OK | Corrí `pedidos_f50f.py`: fallas=[], 0 líneas fuera en los 7 caps. Cap 5: 1946-1966, 1967-1992 y 1993-2026. Cap 6: 1967-1992 y 1993-2026. Cap 7: 1993-2026. |
| 4D | D: papel en f50f/ y las 5 medidas | OK | Corrí `medidas_d.py`: 96 fotos, 2 con marcas de los 60 (F50b tenía 0), 0 con nombre, 0 sin period, US$ 2,332. `PAPEL_FOTOS_WITTENOOM.md/.json` y `MEDIDAS_D.md` existen. Hay cero fotos y cero clips: no hay mp4 ni png nuevos en el diff. |
| 5 | Medida 1: se sacaron «forties/fifties/sixties» | OK, declarado | Es honesto. Hice un barrido independiente de las 39 fotos de 1967+: todos los aciertos de forties/fifties/sixties/thirties son edades («in their sixties», «late sixties»). Las únicas marcas de época reales son 5/6 y 5/16, las mismas 2 que reporta CC. Está declarado en el docstring de `medidas_d.py` y en el reporte, pero NO en `MEDIDAS_D.md`, el entregable. |
| 6 | Medida 3: testigos buscados por texto de ancla | OK con límite | Es correcto porque D re-planeó las anclas (solo 35 de 96 iguales). Solo 3 de las 8 testigo siguen siendo ancla (2/1, 2/7, 5/13) y su sujeto coincide con PEOPLE. Las otras 5 no se pudieron comprobar con el criterio del handoff. CC las deja cubiertas con la lista de 36 fotos con persona en el ancla, y lo declara como abierto n.° 5. |
| 7 | Bug de `scrub_documented_names` con apellidos que son palabras comunes | OK, verificado y bien declarado | `canon_f50f.json:109` trae `"name": "Court"`. `name_matching.iter_name_patterns` (líneas 74–78) solo filtra apellidos de menos de 5 letras o de la blacklist, y «court» no está. El papel lo confirma: 6/3 dice «Perth Supreme a State premier whose government rejected…» y 7/11 dice «steps of the Federal a State premier…». En el papel hay 2 ocurrencias de «State premier whose». Reporte, abierto n.° 1: declarado, sin arreglar, con la decisión dejada al analista. `name_matching.py` no está en el diff. Imprecisión menor del reporte: dice «sin mayúsculas», pero el apellido suelto es sensible a mayúsculas (`(?-i:)`), y por eso «Court» capitalizado sí rompe. |
| 8 | Cambio de fixture en `test_module_f50c.py` | OK | El diff apunta las anclas a `f50f/antes/03_visual.json`, que es el de F50b, el que usó F50c. Cambia el dato y no la aserción, y el motivo está declarado. Los 43 tests de f50f/f50a/f50d/f50c pasan. Sigue sin commitear. |
| 9 | Costos y tope | OK | En `cost_history.json` (leído con cp1252) hay un registro del canon por 0,3415 (1 llamada a Opus) y otro de m03 por 2,332 (11 Opus + 8 Flash) para el tema 123bbb64. La suma es 2,6735, menor que 3,00. Coincide con `d_m03.log` ($2,3320). |
| 10 | Stickers / MAPA `--check` 0 | OK | `lab/tools/mapa_modulos.py --check`: «157 archivos de producción · 0 fallas». El diff tiene los 3 stickers y MAPA json/md. |
| 11 | Suite rápida, amplia y candado de ch02 | OK según logs | `f41/f50f_2`: rápida 55 passed y 3 skipped; amplia 4 failed (las 4 de siempre: `m03_merge_timing` ×2 y `gfx_lab` ×2), 985 passed; ch02 md5 f792f3d483a1fa42daed5f7f0e054f46, igual al anterior. No las corrí, solo leí los logs. |
| 12 | F50f_REPORT.md con lo abierto entero y veredicto íntegro | PARCIAL (esperado) | El reporte existe y trae lo abierto (10 puntos), pero el veredicto sigue como `{{VEREDICTO}}`, que se llena con este texto. |
| 13 | ESTADO actualizado | PARCIAL | `lab/ESTADO_SESION.md` tiene la entrada F50f (líneas 3, 17 y 26), pero está modificado sin commitear (+20/−1). |

Observaciones:
1. `lab/ESTADO_SESION.md`, `F50f_REPORT.md` y `test_module_f50c.py` siguen sin commitear. Falta el commit del reporte, que el reporte mismo anuncia como «este commit».
2. `MEDIDAS_D.md` no menciona la exclusión de las palabras de edad en la medida 1. Quien lea solo ese archivo ve «0 de 39 → 2 de 39» sin saber que la lista la armó CC y que se le quitaron esas palabras. La lista es de CC y no está en el handoff, y el reporte la califica como medida de lab (abierto n.° 4).
3. Al agregar `--salida` a `lab/hyperframes/f50d/pedidos_f50d.py` se tocó un script de lab anterior. Es razonable porque el handoff pide usarlo, pero no estaba listado explícitamente.
4. El reporte dice «guion» para el sticker de `fase1_5` y «research» para step_4e. Lo vi consistente con el diff de stickers.

Fuera de alcance: ninguno dentro de la tanda. En el árbol hay modificaciones previas a la tanda: `diag_234_cap4.py` y `lab/hyperframes/f28/a/f28a.log`, que ya estaban en el status inicial y no están en los commits F50f. `lab/TOPE_TANDA.json` está modificado, como pide el paso 0, y está fuera de git según el reporte.

Riesgos que el contrato no cubre:
- El bug de `Court` afecta a cualquier tema futuro cuyo canon traiga apellidos sueltos de 5 letras o más que sean palabras comunes (Major, Wright, Mercedes quedan latentes). Y F51 usaría ese papel con 2 prompts rotos (6/3, 7/11), uno de ellos con el cartel.
- Cada canon cuesta ahora unos US$ 0,34 y tarda unos 130 s, contra unos 0,03 con Flash. No hay respaldo si Opus o la API fallan: ahora hay Parada.
- Las medidas 1 y 3 son por lista de palabras o por texto de ancla. Ven poco de la ropa de época sin marca y solo 3 de los 8 testigos. La revisión DEBERÍA del analista sobre el papel es la que decide.

### Adenda de CC (después del veredicto)
- **Observación 1:** el reporte, ESTADO y la fixture de `test_module_f50c.py` van en el commit de este reporte.
- **Observación 2:** corregida. `MEDIDAS_D.md` explica ahora en la medida 1 que la lista es de lab, que la armó CC y que las palabras de edad quedan fuera (regenerado con `medidas_d.py`).
- **#7:** corregida la descripción en el reporte. Los nombres completos se buscan sin distinguir mayúsculas, pero el apellido suelto se busca respetando mayúsculas (`(?-i:)`): por eso «Court», con mayúscula como en «Federal Court», rompe, y «court» en minúscula no.

