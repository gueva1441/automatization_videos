# F50e-A — ¿Qué modelo arma mejor el canon? Flash vs Sonnet 5.5 vs Opus 5.5, en texto · PARADA

Handoff `lab/hyperframes/f50e/HANDOFF_F50e_A_canon_por_modelo.md`, md5 `a6995de1f3b13333ec889128d98dec65` (verificado). Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`, rama `f11-guion-v4`. Tope US$ 1,00; gastado **US$ 0,8093**. Producción no se tocó: topics_db y `05_visual_canon.json` tienen el mismo md5 antes y después; no se tocó ningún módulo de producción. No elegí modelo y no corrí D de F50d.

## Qué pasó, en llano
- **Corrieron 7 de las 9 corridas.**
  - Flash, Sonnet y Opus 1 corrieron juntos (7 a la vez).
  - Opus 1 costó US$ 0,35, así que las otras 2 de Opus habrían llevado el total a ~US$ 1,50, por encima del tope de 1,00. **Opus 2 y 3 no corrieron (PARADA por tope).**
- **Los modelos Claude no usaron el esquema.** La API rechazó el esquema del canon con HTTP 400: «Schemas contains too many optional parameters (46)… (limit: 24)».
  - El código del canon de producción (`extract_visual_canon`) tiene un respaldo: vuelve a pedir el mismo texto sin esquema. Las respuestas de Sonnet y Opus que se miden salieron de ese segundo intento.
  - Flash corrió con el esquema.
  - El texto del pedido es el mismo en todos los intentos (md5 `d2568e2a94c5db96f9836451b2f80cd7`), pero la salida forzada no: **la variable «solo el modelo» no quedó pura.** Lo reporto, no lo fuerzo. Hacer obligatorios los campos para bajar de 24 cambiaría el esquema.
- **Flash 2 falló:** el canon salió sin `periods` y no se mide.
- **Resultado:**
  - Flash cubre 61 de 96 fotos en sus 2 corridas medidas. No tiene tramos después de 1966, y las fotos de los caps 5–7 caerían en un tramo de los 60.
  - Sonnet cubre 96/96 en sus 3 corridas, con 4 tramos: el último va de 1993 a 2026.
  - Opus 1 cubre 96/96, con 4 tramos.

## Paso 0
- La línea de DECISIONES 23:04 está tal cual.
- `lab/TOPE_TANDA.json` = `{"usd": 1.0, "desde": "2026-10-28T23:07:33"}` (fuera de git).

## Módulos
Producción: ninguno. Lab (nuevos):
- `lab/hyperframes/f50e/canon_modelos.py`: las llamadas, el ruteador y la medida.
- `canon_modelos_md.py`: la tabla.
- `canon_<modelo>_<n>.json` (7), `CANON_MODELOS.json/.md` y `canon_modelos.log`.

## Cómo se corrió
- **Armado:** `step_4e.canon_desde_ficha(topic, ficha)` de producción, tal cual. En este proceso, `step_4e.call_flash_json` se reemplaza por un ruteador por hilo:
  - Flash va a `gemini_helpers.call_flash_json`.
  - Sonnet y Opus van a `claude_helpers.call_json(..., effort="high")`.
- **Esquema para Claude:** el esquema de Gemini se pasa como dict (`model_dump`) sin `nullable`, que no es JSON Schema. Tiene los mismos campos y ninguno obligatorio. Igual la API lo rechazó por la cantidad de opcionales (ver arriba).
- **Fallas:** un canon vacío o sin `periods` cuenta como falla.
- **Costos:** van a una sola sesión de cost_tracker, `f50e-canon-modelos`, con la descripción `f50e canon <modelo>_<n> (intento k)`.
- **Tope:**
  - Tanda 1: 7 a la vez.
  - Tanda 2 (Opus 2 y 3): corría solo si lo gastado + 2 × Opus 1 ≤ tope. 0,8093 + 0,6928 = 1,5021 > 1,00, así que no corrió.
- **Años de las fotos:** `anio_ancla` o `respaldo[0]` del expediente, con el mismo cálculo que m03 (las 96 tienen año). Los tramos se leen con `m03_visual._tramo`, y el más cercano sale de `_periods_del_cap`.

## La tabla (de `CANON_MODELOS.md`)
| modelo | corridas medidas | fotos cubiertas mín · máx | grupos (por corrida) | grupos con años sin ropa | years ilegibles | US$ promedio por corrida | fallas |
|---|---|---|---|---|---|---:|---|
| flash | 2 de 3 | 61 · 61 de 96 | 22 / 5 | 1 / 0 | ninguno | 0.0255 | flash_2: canon sin periods |
| sonnet | 3 de 3 | 96 · 96 de 96 | 7 / 10 / 8 | 1 / 0 / 1 | ninguno | 0.1287 | — |
| opus | 1 de 3 (2 no corrieron: tope) | 96 · 96 de 96 | 13 | 0 | ninguno | 0.3464 | — |

| corrida | periods | cubiertas | grupos | US$ | s |
|---|---|---:|---:|---:|---:|
| flash_1 | 1937-1966 | 61/96 | 22 | 0.0397 | 69.0 |
| flash_2 | FALLA: canon sin periods | — | — | 0.0119 | 18.9 |
| flash_3 | 1937-1957 · 1958-1966 | 61/96 | 5 | 0.025 | 43.8 |
| sonnet_1 | 1937-1949 · 1950-1966 · 1967-1992 · 1993-2026 | 96/96 | 7 | 0.1241 | 65.8 |
| sonnet_2 | 1937-1949 · 1950-1966 · 1967-1992 · 1993-2026 | 96/96 | 10 | 0.1428 | 77.7 |
| sonnet_3 | 1937-1946 · 1947-1966 · 1967-1992 · 1993-2026 | 96/96 | 8 | 0.1193 | 65.3 |
| opus_1 | 1937-1947 · 1948-1966 · 1967-1992 · 1993-2026 | 96/96 | 13 | 0.3464 | 130.8 |

- **4c:** Flash 1 y Flash 3 dejan 35 fotos sin tramo. Son las de los caps 5 (1971–1993), 6 (1988–2016) y 7 (2021–2024). La regla del más cercano les daría el tramo 1937-1966 (Flash 1) o 1958-1966 (Flash 3). Sonnet y Opus: ninguna.
- **4d:** grupos con años sin ropa:
  - Flash 1: `asbestos_diseases_society_ceo`, 1979 (su ropa empieza en 1980).
  - Sonnet 1 y Sonnet 3: `spanish_migrant_families`, 1966 y 1971. Su ropa: Sonnet 1, 1962-1964 · 1985-2020s; Sonnet 3, 1962-1964 · 1985-1991.
  - Los demás, ninguno.
- **4e:** ningún `years` ilegible.
- **4f:** tokens, costo y segundos de cada corrida, en `CANON_MODELOS.md`. Para Claude, los tokens son los del intento que contestó: el 400 no trae uso. La salida incluye el razonamiento, que no viene aparte.

Los ejemplos que pide el handoff (los `periods` y el grupo con más años de la peor corrida de cada modelo) están en `CANON_MODELOS.md`, al final.

## Verificación
- Suite rápida: 55 passed, 3 skipped. La amplia también corrió: 976 passed + las 4 fallas previas.
- ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46`, igual. Logs en `lab/hyperframes/f41/f50e/`.
- `MAPA_PROYECTO`: no hace falta; no se tocó ningún archivo de producción.

## Lo que queda abierto
1. **La comparación no es solo de modelo.** Flash corrió con el esquema y Sonnet y Opus sin él, porque la API de Claude rechaza más de 24 campos opcionales y este esquema tiene 46. Para que la variable sea solo el modelo hay que:
   - correr los tres sin esquema; o
   - partir o achicar el esquema para Claude; o
   - correr Flash también por el camino sin esquema.

   Es decisión de Omar y del analista. Además, si en producción se usa un Claude, ese 400 pasa en cada canon: es una llamada perdida y siempre el camino sin esquema.
2. **Opus quedó con 1 corrida de 3.** Su mínimo de cobertura sale de una sola corrida, y no se ve su varianza. Las 2 que faltan costarían ~US$ 0,69.
3. **Flash 2 falló** (canon sin `periods`). De 3 corridas de Flash, una sin tramos y dos sin tramos después de 1966. En F50d, con el mismo pedido, Flash dio tramos hasta 2026 en 2 de 3 corridas. La varianza es alta.
4. **Sonnet 1 y Sonnet 3** dejan a las familias españolas sin ropa para 1966 y 1971.
5. **La regla del «más cercano»** (F50d) le da ropa de los 60 a las fotos de 1971–2024 cuando el canon no tiene tramos después de 1966. Con Sonnet u Opus no se activa en Wittenoom.
6. **Del handoff (hallazgo de la simulación):** si en algún momento hay que pasarle a un modelo la lista de años de la ficha, tiene que salir de un campo de fecha, no de una regex sobre el texto. La regex da falsos años (1040, 1160, … 1850).
7. **D de F50d** sigue pendiente; corre con el modelo que elija Omar. topics_db tiene el canon de Flash de F50d (corrida 1, tramos hasta 1966).
8. Sigue abierto lo de F50d, F50c, F50b y F50.
   - F50d: la verificación de B con un canon nuevo y la regla del más cercano.
   - F50c: los nombres reales por las citas.
   - F50b: las notas F8 viejas y la foto madre en F51.
   - F50: n2, n3, n7, n8, n10 y n12.
   - Veo 3.1 en fal se apaga el 2026-11-17.

## Procesos
En segundo plano corrieron `canon_modelos.py` (7 llamadas; terminó con exit 0) y `verificar.sh f50e` (exit 0). No queda nada corriendo. No se cerró ningún programa de Omar.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Paso 0: md5 del handoff | OK | `md5sum` = a6995de1f3b13333ec889128d98dec65 |
| 2 | Paso 0: línea de DECISIONES tal cual, al final | OK | comparada con el texto del handoff: idéntica y es la última línea |
| 3 | Paso 0: TOPE_TANDA = {"usd":1.0,"desde":…} | OK | `{"usd": 1.0, "desde": "2026-10-28T23:07:33"}` |
| 4 | 9 corridas (3x3), effort high en los Claude | PARCIAL | Corrieron 7; faltan opus_2 y opus_3 (`canon_modelos.log:2`, `canon_modelos.py:157-161`). `EFFORT="high"` en `canon_modelos.py:35`. |
| 5 | Mismo pedido, md5 pegado | OK | `d2568e2a94c5db96f9836451b2f80cd7` en los 14 intentos del `CANON_MODELOS.json` |
| 6 | Una sola variable: el modelo | PARCIAL | Flash recibió el esquema. Sonnet y Opus recibieron HTTP 400 y salieron por el intento 2, sin esquema (`con_esquema` True y luego False). Está reportado (REPORT:9-12 y 74). |
| 7 | Canon vacío o sin periods = falla con su error, no se mide | OK | `canon_modelos.py:174-178`; flash_2 queda como "canon sin periods" y no se mide |
| 8 | Medida 4a–4f por código | OK | `medir()` en `canon_modelos.py:103-131`; usa `m3._tramo` y `_periods_del_cap`. Las 96 fotos tienen año. Recalculé valores y coinciden con el JSON y el REPORT. |
| 9 | Resumen por modelo y ejemplos | OK | `canon_modelos_md.py` corre con exit 0 y reescribe `CANON_MODELOS.md` |
| 10 | Producción intacta | OK | `git diff --stat` de `researcher_steps`, `fase1_5.py` y `script_engine` vacío. `produccion_intacta` true en ambos. md5 actuales: topics_db 2be72528…, `05_visual_canon` 95f2b9f4…. |
| 11 | Costos en sesión f50e-canon-modelos | OK | `cost_history`: 7 entradas, total 0,809253 = lo reportado (0,8093); cada entrada coincide con su corrida |
| 12 | No elegir modelo, no correr D, PARADA | OK | el REPORT no elige modelo |
| 13 | Suite rápida, candado ch02, ESTADO | PARCIAL | Rápida: 55 passed, 3 skipped. Amplia: 976 passed, 4 failed (las previas). ch02 md5 f792f3d4…, igual. El ESTADO no lo verifiqué. El REPORT tiene `{{VEREDICTO}}` pendiente, lo esperado hasta este veredicto. |

Sobre los puntos que pediste juzgar:
1. Tope. La lectura es razonable, pero es un criterio de CC. El handoff dice «9 en paralelo» y «tope US$ 1», y las dos cosas nunca fueron compatibles: tres Opus costarían ~1,04 solos y el total ~1,85. Frenar fue prudente y se reportó en vez de forzarlo. Pero el contrato exigía Opus x3. La tanda de 7 y la regla de decidir Opus 2–3 por costo son invención de CC. Opus tiene una sola corrida: su «mínimo» no es mínimo de 3 y no se ve su varianza. Omar decide si autoriza ~US$ 0,69 más.
2. Esquema 400. Está bien reportado y el fallback es el de producción (`step_4e_visual_canon.py:784-790`). Sí rompe «una sola variable»: Flash va con esquema y Claude sin él. No forzarlo fue lo correcto, porque cambiar el esquema habría cambiado el pedido. El intento 1 fallido no figura en `cost_history`, coherente con un 400 sin costo.
3. La medida es correcta. El conteo de años de `where_when` usa una regex acotada a 1800–2099, aceptable aquí. Discrepancia menor: el REPORT dice que Sonnet 1 tiene ropa «de 1985 en adelante»; en el JSON, sonnet_1 es 1985-2020s y sonnet_3 es 1985-1991. No cambia el resultado.

Fuera de alcance: ninguno. Los archivos nuevos están solo en `lab/hyperframes/f50e/` y `lab/hyperframes/f41/f50e/`. DECISIONES.md es la línea autorizada. `diag_234_cap4.py` y `f28a.log` ya estaban modificados antes de la tanda.

Riesgos que el contrato no cubre:
- Si en producción se usa Claude, el 400 del esquema ocurre en cada canon: una llamada perdida y siempre el camino sin esquema.
- La comparación Flash contra Claude queda sesgada hasta correr todo sin esquema o con un esquema que Claude acepte.
- Flash tiene 1 falla de 3 y el contrato no dice cómo entra en el criterio de mínimos.

### Adenda de CC (después del veredicto)
- **Discrepancia del punto 3:** corregida en el reporte. Ahora dice que sonnet_1 tiene ropa 1962-1964 · 1985-2020s y sonnet_3 1962-1964 · 1985-1991.
- **ESTADO (#13):** actualizado en el mismo commit que este reporte.
- **Tope (punto 1):** la regla de las dos tandas es mía, como dice el revisor. Corrí primero 7 para no pasar el tope con llamadas en vuelo que no se pueden frenar. Las Opus 2 y 3 quedan para que Omar decida si autoriza ~US$ 0,69 más.

