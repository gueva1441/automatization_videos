# F11b — v4 con largo + comparación de modelos (Ycuá) — REPORTE

CC · 2026-10-23 · rama `f11-guion-v4` (desde `6264058`) · handoff `HANDOFF_F11b_largo_y_modelos.md`. **Solo narración.** Sin merge, sin producción. **PARADA.**

Para leer: `compara_f11b.html` (en el teléfono: tabla con scroll propio y desplegables por cap y versión) y las tres narraciones `NARRACION_ycua_v4b_{gem,sol,astra}.md`. Prompt único: `prompt_ycua_v4b.txt` (10,757 caracteres). El md5 del texto que se le mandó al modelo es `18618ded…`, y es el mismo en las tres corridas (`prompt_md5` en cada `guion_ycua_v4b_*.json`). Cada corrida comparó ese texto, carácter por carácter, con el del archivo. El archivo en disco da otro md5 (`37d34c4f…`) porque `write_text` en Windows lo guarda con fin de línea CRLF.

## Resultado en una línea

Con la línea de largo, **los dos GPT escriben el largo** (Sol high: 1,501 palabras crudas; Astra: 1,489) **con 0 bloqueantes**. Gemini Pro no: 896. **Ninguna versión final cumple el criterio** (1,350–1,700 palabras), porque la pasada del editor m01c, que está en la ronda de reparación, recorta ≈ 220–270 palabras de las versiones GPT (quedan en 1,229 y 1,270). Los textos **crudos** de Sol y Astra sí cumplen el criterio. Costo de la tanda: **US$ 1.204** de 2.00.

## Lo que se hizo (§1, ninguna regla nueva)

1. **Línea de largo** (`script_engine/guion_v4.py`, `PROMPT_VERSION = "f11b-1"`): encabezado `── CAP n · ≈ N palabras` y, al final del prompt: «Cada cap tiene que tener cerca de las palabras que dice su encabezado: es su largo, no un máximo. El video completo ≈ 1,500 palabras.» (el total es la suma de los `palabras_objetivo` de la escaleta).
2. **Guardia de la regeneración** (bloqueante c): `m01c_editor.lexical_guard(before, after, checks=GUARD_ALL)` con un parámetro nuevo, por defecto todo, como siempre. `m01d.regenerate_cap_v3(..., guard=None)`: el v4 pasa `REGEN_GUARD = ("cifras", "nombres", "citas")`. Con esa guardia, la línea de REGLAS del prompt de regeneración deja de prohibir adjetivos. Sin `guard`, el prompt y la guardia quedan como estaban, así que m01c, v3 y `f10_quirurgico` no cambian. El test dorado de v3 sigue verde.
3. **Modelo enchufable**:
   - `gpt_helpers.py` (nuevo): chat completions, salida JSON (el esquema de Gemini va como `json_schema` no estricto; el prompt no cambia), `reasoning_effort`, reintentos 429/5xx y JSON roto. Un 4xx (modelo inexistente) es un `GPTError` que se reporta y no se reemplaza.
   - `guion_v4.call_for(modelo)`: toda la cadena v4 (guionista + regeneración + edición de oración + editor) usa ese `call`. `ESFUERZO = {"gpt-6.1-sol": "high"}`; Astra usa el esfuerzo por defecto de la API.
   - `fase1_5 --guion v4 --modelo gemini-pro|gpt-6.1-sol|gpt-6-astra`.
   - El juez (m05, determinista) y la partición (m01d: acortar y títulos con Flash) son los de siempre en las tres corridas.
   - **Llave:** `OPENAI_API_KEY` se lee del entorno o de `.env`, y nunca se imprime. `.env` está en `.gitignore` (línea 66, sin trackear; `git check-ignore` OK). No está en logs, reportes ni git.
   - **Costo:** `usage` × precio. Sol US$ 2 / 10 y Astra US$ 10 / 50 por millón de tokens de entrada / salida; el razonamiento factura como salida. **Fuente del precio: HANDOFF_F11b §1.3** (lo pasó el analista; no lo verifiqué contra la página de precios de OpenAI). Va a `cost_tracker` como cualquier llamada.
   - Humo previo (`f11b_humo.py`): una llamada mínima por modelo, los dos existen y aceptan esquema y esfuerzo. US$ 0.0013.
4. **Ids por beat**: `with_ids(parrafos, pool, esc)` = `used_items(texto) ∩ beat_ids(beat)`, donde `beat_ids` = dato central + apoyos + `evidence_ids` del cap. Se usa en todo el v4. Sin `esc` se comporta como F11.

**Tests:**
- `test_module_f11b.py` (15, sin red):
  - guardia por defecto igual / v4 sin adjetivos;
  - regeneración rechaza o acepta prosa nueva según la guardia, y `reparar` le pasa `REGEN_GUARD`;
  - helper GPT: cuerpo, esfuerzo, esquema, costo, 404, reintentos;
  - `call_for`; toda la cadena por el mismo `call` (Gemini parcheado para explotar si se lo llama);
  - `fase1_5` pasa `--modelo`;
  - ids por beat; promedio antes/después;
  - línea de largo.
- Suite (`test_module_f[0-9]*`, `gfx_*`, `01a*`, `01b*`, `m03_*`, fase2b reassemble/hwencode, concat, transition): **571 verdes + las 5 fallas previas** (3 `01b_pauses`, 2 `m03_merge_timing`). Antes de los cambios eran 556 + las mismas 5. `test_v3_byte_identico` verde.

## 1. Tabla resumen (la del html)

Todo re-medido con el código de hoy (bloqueantes a–e, duras v3, ids por beat). Las filas «crudo» son el texto del guionista antes de la ronda de reparación. El costo del crudo es solo la llamada del guionista.

| versión | palabras | por cap / objetivo | bloq. | duras v3 | cierre | ids/párrafo antes → después | US$ | seg. | criterio |
|---|---|---|---|---|---|---|---|---|---|
| v3 (v1) | 1,235 | 121/110 · 214/250 · 214/250 · 181/250 · 195/250 · 214/250 · 96/140 | 3 | 23 | resumen | 1.54 → 0.96 | 0.880 | — | no |
| Gemini v4 A (F11) | 619 | 84/110 · 118/250 · 99/250 · 73/250 · 97/250 · 103/250 · 45/140 | 6 | 28 | resumen | 4.42 → 1.17 | 0.481 | 424 | no |
| GPT Sol medio (prueba del analista) | 1,456 | 107/110 · 246/250 · 245/250 · 241/250 · 241/250 · 244/250 · 132/140 | 0 | 22 | cita | 4.42 → 1.33 | 0.033 | 67 | cumple |
| v4b gem · Gemini Pro | 882 | 53/110 · 142/250 · 120/250 · 91/250 · 125/250 · 236/250 · 115/140 | 5 | 28 | resumen | 5.33 → 1.25 | 0.611 | 540 | no |
| v4b gem — crudo | 896 | 57/110 · 168/250 · 139/250 · 157/250 · 154/250 · 150/250 · 71/140 | 12 | 33 | resumen | 5.25 → 1.42 | 0.048 | 39 | no |
| v4b sol · gpt-6.1-sol high | 1,229 | 93/110 · 205/250 · 192/250 · 207/250 · 203/250 · 217/250 · 112/140 | 0 | 27 | cita | 4.25 → 1.17 | 0.187 | 348 | no |
| v4b sol — crudo | 1,501 | 110/110 · 247/250 · 250/250 · 248/250 · 254/250 · 252/250 · 140/140 | 0 | 22 | cita | 4.42 → 1.17 | 0.076 | 154 | cumple |
| v4b astra · gpt-6-astra | 1,270 | 106/110 · 193/250 · 189/250 · 242/250 · 197/250 · 198/250 · 145/140 | 0 | 25 | cita | 3.92 → 1.08 | 0.405 | 142 | no |
| v4b astra — crudo | 1,489 | 106/110 · 250/250 · 252/250 · 242/250 · 249/250 · 245/250 · 145/140 | 0 | 24 | cita | 4.08 → 1.08 | 0.157 | 60 | cumple |

Notas:
- La fila v3 (v1) usa los ids que declaró el modelo («antes»). El US$ 0.88 es el del guion de F10 (ESTADO_SESION) y no tiene segundos medidos.
- La prueba del analista se re-midió desde `lab/_gpt_probe_analista/ycua_gpt.json`. Su costo sale de su `usage` × precio y no tiene reparación ni juez.
- El juez m05 (el de siempre) dio, en densidad / adjetivos cada 100 palabras: gem 1.70 / 2.04, sol 1.14 / 0.98, astra 1.02 / 0.71. Antagonista nombrado (Paiva) en las tres.
- Costo por corrida (`costos_f11b.json`):

| corrida | US$ |
|---|---|
| humo | 0.001 |
| gem | 0.611 |
| sol | 0.187 |
| astra | 0.405 |
| **total** | **1.204** |

## 2. Qué hizo la ronda de reparación en cada corrida

- **gem (Gemini Pro), 12 → 5 bloqueantes, 896 → 882 palabras:**
  - Crudo: los 7 caps cortos, igual que F11. La línea de largo subió el texto de 619–676 a 896 palabras, pero no lo llevó al objetivo. Cierre «resumen».
  - Regeneración (c) en los 7 caps, con la guardia nueva: **pasaron 2 de 7** (cap 6, 150 → 290; cap 7, 71 → 115).
    - Los otros 5 se rechazaron ya no por adjetivos, sino por **«citas nuevas»** (caps 1–4): el modelo trae entre comillas citas del pool que no estaban en el texto del cap ni en los permitidos, o pone entre comillas su propia prosa (cap 3).
    - Y un **«nombre nuevo» `celsius`** (cap 5: «grados Celsius» en mayúscula se lee como nombre).
  - Edición de oración: 4 de 4 aceptadas (comillas fuera del pool y citas SIN VERIFICAR con nombre: Q35/Q34 de Digna Felicia Cáceres, Q29 de Benedicto Pérez, Q53 de Nelson Astigarraga).
  - Fechas: sin cambios. Editor m01c: 10 aceptados, 2 rechazados (subían los bloqueantes 5 → 6).
  - Quedan 5 bloqueantes: caps 1–5 cortos.
- **sol (gpt-6.1-sol high), 0 → 0 bloqueantes, 1,501 → 1,229 palabras:**
  - Crudo: caps en su objetivo, cierre en cita, 0 bloqueantes. No hubo regeneración ni edición.
  - **El editor m01c** (su prompt: cortar relleno y ecos) cambió los 12 párrafos y se aceptaron 7. Los 5 rechazados subían los bloqueantes 0 → 1. Los aceptados **recortaron 272 palabras**, y los caps quedaron en 77–87 % del objetivo (dentro de ±25 %, sin bloqueante), pero el total quedó por debajo de 1,350.
- **astra (gpt-6-astra), 0 → 0 bloqueantes, 1,489 → 1,270 palabras:** igual que Sol. El editor aceptó 4 y rechazó 8, y recortó 219 palabras.
- **Lectura (no se cambió nada):**
  - Con un texto GPT de 0 bloqueantes, la única acción de la ronda es la pasada del editor. Esa pasada corre siempre (F11 §1.3) y su aceptación mira solo los bloqueantes, no el total.
  - Es lo que saca a Sol y a Astra del criterio.
  - Si el criterio se mide sobre el texto que sale del guionista (o si el editor no corre cuando no hay bloqueantes), Sol y Astra cumplen. Lo deciden Omar y el analista; no lo toqué porque sería un cambio de la ronda, no del handoff.

## 3. Ids antes y después, y la causa de D80/D81/D97

- **Promedio de ids por párrafo** (antes = todo lo que `used_items` matchea en el pool; después = ∩ ids del beat): v3 1.54 → 0.96 · Gemini v4 A 4.42 → 1.17 · prueba Sol 4.42 → 1.33 · gem 5.33 → 1.25 · sol 4.25 → 1.17 · astra 3.92 → 1.08. El corte deja ≈ 1 id por párrafo, del orden de lo que declaraba v3.
- **Causa de D80, D81 y D97** (Orleans `ba6c3cac-f7r3`). No es una lista: es **el ancla**.
  - `evidence.anchors` de un dato `cifra`/`magnitud` sin dígitos en el `valor` toma los números del `texto`:
    - D80, valor «altura de la cintura», texto «En la Unidad **A-1**…» → ancla `"1"`;
    - D81 → `["1", "5", "6 pies"]` (el `1` de «A-1»);
    - D140 → «aproximadamente 1 año» → `"1"`.
  - Después, `evidence._num_forms("1")` expande el ancla a `["una", "uno", "1"]`, y `literal_in` la encuentra en **cualquier artículo «una» / «uno»** del párrafo.
  - D97 tiene `valor: "una"` y su ancla es la palabra «una», literal.
  - Resultado: todo párrafo con «una» «usa» D80, D81, D97, D140…
  - En el pool de Orleans hay **9 ítems** con un ancla así (D80, D81, D97, D140, D182, D186, D312, D375, D463). En el de Ycuá, **2** (D154 «1 millón», D219 «1 año y 6 meses»): por eso en F11 aparecían en 6 de 12 párrafos.
  - Con los ids por beat dejan de salir donde no corresponden. El ancla sigue igual: no se parcheó (§1.4). Afecta a todo lo que use `used_items` sin declaración, como la densidad y la repetición del juez.

## 4. Lo que el v4 sigue sin ver

- **Largo final vs. editor:** ver §2. Ningún bloqueante mide el total por debajo de 1,350 (la (c) solo mide caps a ±25 % y el tope de 1,700).
- **Gemini no escribe el largo** aunque el prompt lo pida: 896 palabras con el mismo prompt con el que los GPT escriben ≈ 1,500. Su regeneración choca ahora con la guardia de citas, porque copia citas del pool que no están en los permitidos del cap.
- **«Celsius»** (y cualquier palabra técnica en mayúscula) es un «nombre nuevo» para la guardia.
- **Relleno sin datos en los GPT:** las duras v3 (no bloquean) marcan párrafos de 11–15 frases sin ningún dato del pool (beats 6, 7, 9 y 11 en Sol y Astra). Parte del largo se logró con prosa sin datos. Lo juzga el analista leyendo.
- **Cap 4 sin sus datos asignados** en las tres v4b (0 de 3: Q35, la cita «El jefe mandó cerrar las puertas…», está SIN VERIFICAR, y los modelos la esquivan o la pierden). Tampoco suenan los «1 de agosto» de T15/T06/T21 (la regla del F10 pide una fecha completa por video).
- **«alguien ordenó»** sin nombre en el cap 1 de las tres, y ecos de frase entre caps («las primeras explosiones», «cerrar las puertas»).
- El texto de las duras v3 del gancho dice «Nueva Orleans, agosto de 2005» como ejemplo de ancla en un video sobre Ycuá. Es solo el mensaje de la regla v3 (no está en el prompt v4), pero si se vuelve a usar en v3 conviene saberlo.
- Lo de F11 sigue abierto: Nagin, comillas simples que no ve `false_quotes`, Q20 de Liz Torres (verificada_parcial, con nombre por §1.1).

## Archivos

- **Código:** `gpt_helpers.py` (nuevo), `script_engine/guion_v4.py`, `script_engine/m01c_editor.py` (`checks`), `script_engine/m01d_particion.py` (`guard`), `fase1_5.py` (`--modelo`), `test_module_f11b.py`.
- **Lab** (`lab/hyperframes/f11b/`): `f11b_corridas.py`, `f11b_compara.py`, `f11b_humo.py`, `prompt_ycua_v4b.txt`, `guion_ycua_v4b_{gem,sol,astra}.json`, `NARRACION_ycua_v4b_{gem,sol,astra}.md`, `compara_f11b.html`, `resumen_f11b.json`, `costos_f11b.json`, `humo_gpt.json`, `corridas.out`.
- **Pasos** (`data/scripts/_steps/f8s1-ycua-bolanos/`, fuera de git): `*_v4b_{gem,sol,astra}.json`.
- **No se pisó:** F11, `_v1`, `_ajuste`, `_v4A/_v4B`, los vigentes ni `topics_db`.
- **No se commitea:** `.env`, `lab/_gpt_probe_analista/` ni los modificados de siempre.

## 5. Veredicto del revisor-handoff (íntegro)

Después del veredicto se corrigió la redacción del md5 del prompt (observación 1), y se hicieron el commit y la actualización de ESTADO_SESION (puntos 13 y 14).

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | `.env` en `.gitignore` y sin trackear | OK | `git check-ignore -v .env` da `.gitignore:66`. `git ls-files .env` no devuelve nada. |
| 2 | La llave se lee de `.env` y no se imprime ni aparece fuera de `.env` | OK | `gpt_helpers.py:35-44` la lee de entorno o `.env`. El único `print` (`:123`) es de reintentos y no incluye la llave. Busqué el valor completo en todo el repo (sin imprimirlo) y solo aparece en `./.env`. Tampoco hay patrones `sk-…` fuera de `.env`. |
| 3 | Línea de largo (encabezado «≈ N palabras» y total al final) | OK | `guion_v4.py` diff: encabezado `≈ {palabras_objetivo}` y cierre «El video completo ≈ {total:,} palabras». `PROMPT_VERSION` pasó a `f11b-1`. |
| 4 | Guardia de la regeneración solo para cifras, nombres y citas | OK | `m01c_editor.lexical_guard(..., checks=GUARD_ALL)` mantiene el valor por defecto. `m01d.regenerate_cap_v3(guard=None)` usa `GUARD_ALL` si no se le pasa nada. `guion_v4.REGEN_GUARD = ("cifras","nombres","citas")`. |
| 5 | Modelo enchufable (`--modelo`, `call_for`, esfuerzo, error sin reemplazo) | OK | `call_for` lanza `ValueError` si el modelo es desconocido. `ESFUERZO={"gpt-6.1-sol":"high"}` y Astra va por defecto. `fase1_5.py` agrega `--modelo` con esas tres opciones. |
| 6 | Ids por beat | OK | `beat_ids` y `with_ids(..., esc)` (`used_items ∩ beat_ids`) están en el diff. `ids_per_paragraph` da el antes y el después. El reporte §3 explica la causa de D80, D81 y D97 (anclas numéricas «1» expandidas a «una» o «uno») y no la parchea con listas. |
| 7 | Cero reglas nuevas | OK | En el diff de `guion_v4.py` el único `re.compile` (`:375`) ya estaba. Los cambios agregan parámetros y filtros por intersección, no regex ni listas que rechacen. |
| 8 | Mismo prompt exacto en las 3 corridas | OK | Los tres `guion_ycua_v4b_*.json` tienen `prompt_md5 = 18618dedff5081ae…`. `corridas.out` dice «prompt 10757 caracteres · md5 18618ded». |
| 9 | Tope de costo de US$ 2.00 | OK | Humo 0.0013 + gem 0.6113 + sol 0.1866 + astra 0.4047 = 1.2039, igual que `costos_f11b.json` y `corridas.out`. |
| 10 | Números del reporte contra `resumen_f11b.json` | OK | Revisé las 9 filas: palabras, bloqueantes, duras v3, cierre, ids antes/después, costo, segundos y criterio coinciden con el reporte. Los caps y el esfuerzo de los `guion_*.json` también. |
| 11 | Tests | OK | Corrí `test_module_f11b.py` y `test_module_f11.py`: 25 pasan, `test_v3_byte_identico` incluido. Las 571 verdes y las 5 fallas previas que cita el reporte no las corrí. |
| 12 | Entregables existentes y no vacíos | OK | Están todos los listados en `lab/hyperframes/f11b/`: HTML, JSON, narraciones, prompt, reporte y `corridas.out`. |
| 13 | Reporte con el veredicto íntegro del revisor | PARCIAL | `F11b_REPORT.md` §5 dice «(pendiente)». Hay que pegar este veredicto. |
| 14 | Commit, `ESTADO_SESION` y PARADA | NO VERIFICABLE | Nada está commiteado. `lab/ESTADO_SESION.md` figura modificado. Falta el commit por ruta, sin `.env` ni `lab/_gpt_probe_analista/`. |

Observaciones:
- El reporte dice «md5 18618ded…» para `prompt_ycua_v4b.txt`, pero el md5 del archivo es `37d34c4f…`. El 18618ded es el hash del prompt enviado al modelo, no el del archivo. La verificación byte a byte que describe el reporte está bien, pero la redacción confunde.
- El precio de Sol y Astra viene solo del handoff (el reporte lo admite) y no se contrastó con la página de OpenAI.
- Ninguna versión final cumple el criterio de 1,350–1,700 palabras. Solo los crudos de Sol (1,501) y Astra (1,489) lo cumplen, porque el editor m01c recorta unas 220–270 palabras. El reporte lo dice con claridad. Gemini llegó a 882 palabras y 5 bloqueantes.

Fuera de alcance: ninguno. Los archivos modificados son los declarados, más `diag_234_cap4.py` y `gfx_profiles/*`, que ya venían modificados de antes y no deben commitearse.

Riesgos que el contrato no cubre:
- El editor m01c acepta o rechaza solo por bloqueantes y no mira el largo total.
- Las duras v3 de los GPT marcan relleno sin datos (beats 6, 7, 9 y 11). Eso solo lo evalúa la lectura del analista.
- El cap 4 quedó sin sus datos asignados en las tres corridas (0 de 3).
