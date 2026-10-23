# F12 — Ficha del caso (Ycuá) — REPORTE → PARADA

CC · 2026-10-23 · rama `f11-guion-v4` (desde `967859f`). Handoff: `HANDOFF_F12_ficha_del_caso.md`. Solo datos: no se corrió ni la escaleta ni el guion.

**En una línea:** la ficha de Ycuá salió de una sola llamada a Sol high (**US$ 0.339** de 0.50). Trae 24 contradicciones, entre ellas **la de Paiva hijo** (Emiliano / Víctor Daniel / Víctor / Daniel), además de 99 personas, 61 cifras con unidad, 20 eventos de cronología, 76 hechos, 25 citas y 34 descartados. El chequeo determinista no sacó nada en la versión final.

Para leer: `FICHA_ycua.md` (contradicciones arriba) y `ficha_caso.json`. Las dos están en esta carpeta y en `data/scripts/_steps/f8s1-ycua-bolanos/`.

## 0. Qué se hizo

1. **`researcher_steps/ficha_caso.py`:**
   - **Llamada:** una sola, a `gpt-6.1-sol` en esfuerzo high, con la estructura de F11c (`<rol>` y `<tarea>` en el sistema; en el usuario, `<caso>` → `<pool>` → `<tarea>` al final).
   - **Pool en el prompt:** van los 509 ítems completos (82 personajes, 76 de cronología, 227 datos, 82 citas, 42 lugares). Cada ítem lleva su id, sus campos y **todas** sus evidencias con `doc_id@offset` y el pasaje.
     - Una evidencia que ya apareció en otro ítem va como «(= arriba)» (122 casos), para no repetir el mismo pasaje.
     - Sin esa deduplicación, el pool completo (690k caracteres) no entraba en el tope. Así quedó en ≈ 46k tokens.
   - **Esquema:** las siete secciones del handoff. Las cifras llevan `unidad` obligatoria; cada versión de una contradicción lleva `doc_id`, `offset` e `ids`; cada cita lleva `original`.
   - **Chequeo determinista (`check`):** cada ítem tiene que citar ids que existen; cada cifra, hora (`hh:mm`) y fecha ISO del ítem tiene que aparecer en el texto de esos ids (texto, campos, cita literal y evidencias); una cita corregida tiene que estar a ≤ 3 de su original (Levenshtein).
     - Lo que falla va a `descartados` como «no respaldado: …», sin reintento.
     - Dos agregados que el handoff no enumera explícitamente:
       - el original de una cita (o su texto, si no se corrigió) tiene que estar en su id;
       - en una contradicción, cada `doc_id@offset` tiene que ser una evidencia de los ids de esa versión.

       Los dos son control de la ficha, no reglas del guion. Si el analista prefiere sacarlos, son dos condiciones dentro de `problems()`.
   - **Salidas:** `ficha_caso.json` (secciones, conteos crudo y final, lo sacado, md5 del pool y costo) y `FICHA_<tag>.md` (ids en `<sub>`, conteos arriba y las contradicciones primero).
2. **Sol high por defecto en el guion v4:** `guion_v4.DEFAULT_MODELO = "gpt-6.1-sol"`.
   - `call_for(None)`, `write(call=None)` y `reparar(call=None)` usan Sol con esfuerzo high; `--modelo gemini-pro` sigue disponible.
   - En `guion_v4.py` solo cambió eso; `config.py` no se tocó.
3. **`gpt_helpers.call_json(max_completion_tokens=)`**: parámetro opcional (por defecto, el de siempre) para el freno de costo.
4. **Tests sin red:**
   - `test_module_f12.py` (12): el esquema; la estructura del prompt; la deduplicación; lo respaldado se queda; id inexistente; cifra y hora no respaldadas; cita corregida dentro y fuera del límite; contradicción con doc/offset ajeno; números con separadores e ids que no cuentan como cifras; el orden del MD; Sol high por defecto (también en `write` sin `call`).
   - Se adaptaron dos aserciones que fijaban `call_for(None)` como Gemini Pro: `test_module_f11b.py` y `test_module_f11c.py`.
   - **Suite amplia: 591 verdes + las 5 fallas previas** (3 `01b_pauses`, 2 `m03_merge_timing`). `test_v3_byte_identico`, verde.
5. **Runner** `lab/hyperframes/f12/f12_ficha.py`:
   - fija el md5 del pool (`5f3c6d0b…`, no se modificó);
   - estima el costo de entrada por lo alto y fija `max_completion_tokens` en 38,403, para que el peor caso (US$ 0.495) no pase el tope;
   - permite una sola llamada que facture;
   - `--rechequear` re-aplica el chequeo sobre el crudo guardado (`ficha_crudo_ycua.json`) sin llamar al modelo.

## 1. Conteos y lo que sacó el chequeo

| sección | crudo (modelo) | ficha final |
|---|---|---|
| contradicciones | 24 | 24 |
| personas | 99 | 99 |
| cifras | 61 | 61 |
| cronología | 20 | 20 |
| hechos | 76 (pedido: 60–80 ✅) | 76 |
| citas | 25 (pedido: 15–25 ✅) | 25 |
| descartados | 34 | 34 |

**El chequeo, en dos tiempos (lo cuento tal cual):**
1. En la corrida, el chequeo sacó 12 ítems: 5 contradicciones, 1 cifra, 1 evento de cronología y 5 hechos. **Los 12 eran falsos positivos de mi chequeo:** leía como cifras los ids escritos dentro del texto («F15», «F09», «P62», «P74» → 15, 9, 62, 74). Ninguno era una cifra del caso.
2. Lo corregí: los tokens `[DTQPLF]NN` no cuentan como cifras, y agregué un test. Re-apliqué el chequeo sobre **la misma salida del modelo** (`--rechequear`, sin otra llamada). Resultado: **0 sacados**. La ficha final es la del rechequeo.

**Prueba de que el chequeo funciona sobre esta ficha:**
- Revisa 154 números en la ficha.
- Si le agrego un dígito al valor de cada una de las 61 cifras, saca las 61.

**Las contradicciones (24):**
- Total de fallecidos: 400 / 364 / 327 oficial / más de 400 / más de 500 (5 versiones).
- Total de heridos: 244 / 500.
- Ocupación: más de 1,000 / más de 1,500.
- **Nombre del hijo del propietario:**
  - «Emiliano Paiva»: F05@1484 (P07);
  - «Víctor Daniel Paiva»: F15@524 (P28, D215);
  - «Víctor Paiva»: F10@3282 (P28, D20);
  - «Daniel Paiva»: F09@143800 (P48), un testimonio que el analista no había nombrado.

  ✅ **Sale, como pedía el handoff.**
- Formas del nombre del propietario: Juan Pío Paiva / Juan Pío Helvidio Paiva Escobar / Juan Pío Paiva Escobar.
- Grafía de Ismachoviez / Ismachowiez.
- Antoliana / Antolina Burgos.
- Formas del nombre del abogado defensor.
- Formas del nombre del exempleado sobreviviente.
- Duración de la condena de Casaccia.
- Estado de las puertas (4 versiones).
- Accesos de la rampa y hacia la avenida Artigas (4 versiones).
- Configuración de las puertas.
- Salidas de emergencia.
- **Existencia y autoría de la orden de cerrar las puertas** (Digna Cáceres: «Pío Paiva»; la defensa la niega; Ismael Alcaraz y la radio).
- Hora del estallido (3 versiones).
- Temperaturas (600 °C, más de 1,000 grados…).
- Alcance de los delitos atribuidos a los condenados.
- La fecha de la muerte de Diana no coincide con el pasaje.
- El evento de Digna Cáceres no coincide con la acción narrada.
- **Identidades fusionadas en P62 y en P74**: errores del pool que la ficha señala.
- Autor de Q60 y autor de Q66.

**Los casos conocidos del handoff:**
- **Q34 «portó» → «portón»:** ✅ en citas, con su `original` (Levenshtein 1). También corrigió Q35 (distancia 1): «si no cerraban las muertas iban a morir pocos» → «…las puertas…». La corrección es coherente con el contexto, pero cambia una palabra con sentido propio; conviene que el analista la mire.
- **El 600:** ✅ la temperatura va como «600 °C entre el cielorraso y el techo» (D101); su otra versión es «más de 1.000 grados; escala no indicada». Los G. 600 millones van como «guaraníes de indemnización» (D221). Ninguna cifra queda sin unidad.
  - El «600 personas» de D94 (ocupación máxima en Formosa) **no entró** a cifras; no es un conteo del caso.

**Cosas para el analista** (no rechazan nada; las anoto):
- **Cronología:** las fechas no van en ISO, como están en el pool, sino habladas («1 de agosto de 2004»), y algunas horas son literales del testimonio («siete de la mañana por ahí»). El chequeo las acepta: no hay ISO y los números coinciden.
- **Hechos que nombran la fuente:** 5 lo hacen en la prosa («F15 informa que…»). Es la ficha, no la voz, pero cuando se cablee al guionista conviene saberlo.
- **Personas:** son 99 (el pool tiene 82 personajes). Suma gente que aparece en datos y citas, y entradas como «Hijo de Juan Pío Paiva — nombre en conflicto», que no elige nombre, como pide el handoff.
- **Descartados (34), todos del modelo:** horas y fechas que la extracción del pool calculó o atribuyó mal (por ejemplo, la hora de T22 corresponde a otro relato, fechas absolutas sacadas de «ayer» o «cinco días después») y equivalencias de identidad que no se pueden sostener.

## 2. Costo y tokens

| llamada | entrada | salida | razonamiento | US$ | segundos |
|---|---|---|---|---|---|
| ficha_caso (gpt-6.1-sol high) | 46,217 | 18,969 | 5,634 | **0.3385** | 374 |

- Prompt: sistema 1,907 caracteres y usuario 164,535 (los 509 ítems).
- Tope de salida + razonamiento: 38,403 tokens (peor caso US$ 0.495).
- **Total de la tanda: US$ 0.339 de 0.50.** El rechequeo no costó nada.

## 3. Frenos

- No se tocaron `00_pool_v3.json` (md5 verificado antes de la llamada), la escaleta, `m01a`, `m05`, `evidence.py`, `config.py` ni `topics_db`.
- De `guion_v4.py` solo cambió el modelo por defecto.
- Cero reglas nuevas para el guion: el chequeo controla la ficha y no está cableado al guion.
- No se corrieron la escaleta, el guion, imágenes, voz ni producción. Sin merge; `.env` y `lab/_gpt_probe_analista/` no se commitean.
- La ficha **todavía no está cableada** a la escaleta ni al guionista: eso queda para otra tanda, después de que Omar decida las contradicciones.

## 4. Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | `researcher_steps/ficha_caso.py` con 7 secciones, una sola llamada a Sol high, estructura F11c | OK | Archivo nuevo. `ficha_caso.json` tiene las 7 secciones y `modelo=gpt-6.1-sol`, `esfuerzo=high`. `costos_f12.json`: `llamadas`=1. |
| 2 | Salidas `ficha_caso.json` y `FICHA_ycua.md` en `_steps/` y en `lab/hyperframes/f12/` | OK | md5 idénticos entre copias: json `d6ce5362…`, md `ec3a248d…`. No están vacíos (88 KB y 58 KB). |
| 3 | Chequeo determinista (ids, cifras/horas/fechas, Levenshtein ≤ 3) → `descartados` "no respaldado", sin reintento | OK | `--rechequear` corrido por mí: crudo y final iguales y 0 sacados. El código no reintenta. |
| 4 | Conteos y dos tiempos del chequeo | OK | `ficha.out` (corrida): contradicciones 19, cifras 60, cronología 19, hechos 71, descartados 46, "sacados 12". Eso es 5+1+1+5 = 12, y 34+12 = 46. Coincide con el reporte. Los 12 mensajes son "cifra 15/09/62/74…", o sea ids leídos como cifras: falsos positivos como dice el reporte. Mi rechequeo da 24/99/61/20/76/25/34 y 0 sacados, igual al reporte. |
| 5 | Paiva hijo con `doc_id` y `offset` | OK | Contradicción en el json: Emiliano F05@1484 (P07); Víctor Daniel F15@524 (P28, D215); Víctor F10@3282 (P28, D20); Daniel F09@143800 (P48). Coincide con el reporte. |
| 6 | Q34 «portó» → «portón» con `original` | OK | Cita Q34: texto con "portón", `original` con "portó". Además Q35 ("muertas" → "puertas"), como dice el reporte. |
| 7 | El 600 con unidad | OK | D101: "600 °C entre el cielorraso y el techo", con otra versión "más de 1.000 grados". D221: "600 millones guaraníes de indemnización". No hay 600 sin unidad. |
| 8 | Costo ≤ US$ 0.50 y tokens | OK | `costos_f12.json`: US$ 0.3385, 46,217 entrada, 18,969 salida, 5,634 razonamiento, 374 s. Coincide con el reporte. |
| 9 | Sol high por defecto en `guion_v4`, y solo eso | OK | El diff de `guion_v4.py` tiene `DEFAULT_MODELO`, `call_for(None)` y `write`/`reparar` con `call=None`. `gpt_helpers.py`: solo `max_completion_tokens` opcional. `config.py` sin tocar. |
| 10 | Tests sin red; suites verdes + 5 previas | PARCIAL | Corrí las 4 suites indicadas: 45 passed. No corrí la suite amplia (591 + 5 previas): NO VERIFICABLE por mí, queda el número del reporte. |
| 11 | Frenos: `00_pool_v3.json` md5 `5f3c6d0b…`; escaleta, `m01a`, `m05`, `evidence`, `config`, `topics_db` sin tocar; cero reglas nuevas; sin merge | OK | md5 del pool verificado igual. `git status` no muestra esos archivos modificados. El diff de `guion_v4.py` no agrega reglas. |
| 12 | `lab/ESTADO_SESION.md` actualizado | OK | Diff: sección F12 y los conteos de la suite (591). Cuenta igual que el reporte los 12 falsos positivos → 0 en el rechequeo. |
| 13 | Orden del MD, ids y conteos arriba | NO VERIFICABLE | No leí el MD completo. Solo confirmé que existe y que las dos copias son idénticas. El test de orden está en `test_module_f12.py`. |
| 14 | §4 del reporte con el veredicto | PENDIENTE | Dice "(pendiente)": va este veredicto. |

Observaciones (no bloquean):
- Los 154 números revisados y las "61 cifras alteradas → 61 sacadas" del reporte no los reproduje, porque el runner no expone esa prueba. Quedan sin verificar.
- Hay dos chequeos que el handoff no pedía: original de la cita dentro de su id, y doc_id@offset de la contradicción dentro de las evidencias. El reporte los declara. Son control de la ficha, no reglas del guion.
- Las fechas de la cronología van habladas, no ISO. El reporte lo avisa.
- Cinco hechos nombran la fuente en la prosa ("F15 informa…"). El reporte lo avisa.
- En la corrida, la ficha guardada por el chequeo viejo tenía 12 ítems en `descartados`. La versión final los repone por el rechequeo. Es lo que el reporte cuenta, pero conviene que Omar sepa que la ficha final NO es la salida directa de la corrida: es el crudo del modelo + el chequeo corregido.

Fuera de alcance: ninguno propio de F12. Los `M` de `diag_234_cap4.py` y `gfx_profiles/*` no son de F12. Hay dos `topics_db_pre*.json` sin trackear en `lab/hyperframes/f5` y `f7`. Parecen viejos y no son de F12, pero conviene no commitearlos.

Riesgos que el contrato no cubre:
- El chequeo solo verifica que cifras, horas y fechas estén en el texto de los ids. No verifica que el hecho esté bien interpretado.
- La ficha tiene 99 personas contra 82 personajes del pool: la ficha agrega gente de datos y citas.
- Nada cablea la ficha a la escaleta ni al guion, así que hoy "lo que no está en la ficha no existe" todavía no se cumple en el pipeline.
