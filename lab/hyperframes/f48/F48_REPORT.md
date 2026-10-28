# F48 — Que al prompt de foto le llegue lo que el research ya tiene (S1 en producción + S1 → S5 en texto con Opus) — REPORTE

CC · 2026-10-28 · rama `f11-guion-v4` · handoff `lab/hyperframes/f48/HANDOFF_F48_entrada_del_prompt_de_foto.md` (md5 `9aabfd5b4ff2e8cc201b4426728d617f` ✓). Paso 0 → S1 en producción → S1…S5 en lab, sin parada entre partes (lo pidió Omar). Tope US$ 7,00; **gasto real US$ 5,7588**, leído de `cost_history` (`f48-lab`). **Cero fotos, cero llamadas a fal. PARADA:** nada más va a producción.

## Commits
- `220d32e`: paso 0 (DECISIONES 03:34 tal cual + el handoff).
- `0ec8e7b`: S1 en producción (`m03_visual.py`, tests, sticker y mapa).
- El commit de esta parte del lab: `f48_corridas.py`, salidas, reporte y ESTADO.

## Lecturas declaradas
- `CLAUDE.md`, `DECISIONES.md` (cola, hasta 03:19), `lab/ESTADO_SESION.md` (cabecera, F47b y F47) y el handoff entero.
- Producción: `script_engine/m03_visual.py` en sus partes relevantes:
  - el bloque de ubicaciones, líneas 290–361 antes del cambio;
  - `_format_seedream_canon_block`;
  - `_build_topic_block`, con GEO/ERA en la línea 1468;
  - `assign_visual_prompts`.
- Los tests `test_module_f5b.py::test_s6_ubicaciones_documentadas_solo_con_pool` y `test_module_f5d.py::test_canon_m03_ningun_menor_en_celdas_de_adultos`.
- `voz_utils.numeros` y `_steps/<id>/_perfil.json` de Wittenoom.
- El pool de Wittenoom: `datos`, `cronologia` y `personajes` (35, con rol, lugar y `fechas_presente`).
- La base de F47/F47b (código y `PROMPTS_F47b.json`).

## Módulos (paso 2 de /tanda)
- **`script_engine/m03_visual.py` (producción).**
  - Sticker de hoy: «escribe, para cada capítulo, la descripción de cada imagen que pinta Seedream…».
  - Antes armaba el pedido de los casilleros con `GEO: (sin geo)` y `ERA: (sin era)`, más el bloque «UBICACIONES DOCUMENTADAS» con el hardcode de Orleans.
  - **Después:** `_geo_era(topic_id, narration)` pone GEO = `lugar_principal` del perfil del research y ERA = «primer–último año» dichos en la narración. Lo llama `assign_visual_prompts` y queda solo en el `topic` en memoria; no se escribe en `topics_db`.
  - Se borraron `_format_documented_locations`, `_documented_places`, `_LOC_GROUPS`, `_LOC_DEST` y su uso en `_format_seedream_canon_block`.
  - El sticker se reescribió en `lab/mapa/stickers/fase2a.json` (md5 nuevo, «recibe» con el perfil, líneas de las funciones muertas) y se regeneró `MAPA_PROYECTO`. `--check` da 0.
- **Tests de producción:**
  - borrados: `test_s6_ubicaciones_documentadas_solo_con_pool` (f5b) y `test_canon_m03_ningun_menor_en_celdas_de_adultos` (f5d);
  - nuevo: `test_module_f48.py`, con 4 tests: Wittenoom → `Wittenoom` / `1943–2024`; perfil y años en letras; sin datos queda el respaldo «(sin geo)»; no quedan el bloque ni «Ningún menor».
- **Lab nuevo: `lab/hyperframes/f48/f48_corridas.py`.**
  - Importa `f47b_corridas` (chequeos 9 y 10, historia de costos), `f47_corridas` (ruteador, `una_variante`, `armar_c2`, `chequeos`, freno) y `f46b_corridas` (expedientes, `slots`, `armar`, `f8`, `canon_c`).
  - S2–S5 viven solo en el lab: se parchean dentro del proceso, etapa por etapa.
- **Una variable por etapa:** las etapas son acumuladas y cada una suma un solo cambio. Lo muestra el diff del pedido del cap 6 de cada etapa contra la anterior, pegado abajo.
- **Constantes nuevas, con origen en su línea:**
  - 1800–2100 en `_geo_era` y en el año del casillero (`# derivado: handoff F48 §Constantes`);
  - `TOPE_USD` 7,00 (Omar);
  - `MODELO` `claude-opus-5-5` (handoff §Constantes, Omar);
  - `CAPS` (handoff).
  - `test_constantes_con_origen.py` está verde.
- **Simulador: no aplica.** Ni S4 (regla del año) ni el resto son reglas o filtros sobre el guion de pantalla (`GUION_PANTALLA.json`), que es lo que el simulador mide. Son la entrada del pedido de los casilleros de foto, y se miden en texto, que es lo que hace esta tanda.

## Parte 1 — S1 en producción (`0ec8e7b`)
- **Salida de `_geo_era` para Wittenoom:** `{'canonical_geo': 'Wittenoom', 'canonical_era': '1943–2024'}`. El perfil dice `anio_fin` 2007, pero no se usa.
- **Suites antes del commit:**
  - rápida: 55 verdes, 3 saltados;
  - `test_module_f48.py` + f5b + f5d: 18 verdes;
  - amplia: **921 verdes y 4 fallas** (`m03_merge_timing` ×2, previas; `gfx_lab` ×2, de las 3 que ya fallaban en F47; esta vez una pasó), 30 saltados (`verif_s1/`);
  - `mapa --check`: 0.
- **Lo que cambia en el pedido** se ve en el diff de S1 contra S0, abajo: GEO y ERA con valor y 12 líneas menos (todo el bloque de ubicaciones con «→ Madrid» y «Ningún menor…»).

## Parte 2 — S1 → S5 en texto con Opus
`python lab/hyperframes/f48/f48_corridas.py prompts` (03:47:35 → 03:57:36, `corrida.log`).
- **Etapas en secuencia** (cada una acumula sobre la anterior). Dentro de cada etapa, **las 4 llamadas en paralelo** (caps 2, 5, 6 y 7). Freno antes de cada llamada, y `cost_tracker` con `f48-lab`.
- **20 llamadas a Opus 5.5 con effort high**, todas **ok al 1.er intento**: 0 negativas, 0 JSON roto. Más 1 llamada a Flash para el canon de S5.
- **S1:** el pedido de producción tal como queda después del commit. Se verificó por código, con un `assert`, que el bloque del expediente de S1 es byte a byte el de F46b.
- **S2:** suma la línea `FACTS: «…» | «…»` por foto: `datos.texto` y `cronologia` «fecha · evento» de los ids del beat, enteros. Va antes de `QUOTES`.
- **S3:** `PEOPLE (role · where · years): …`, que reemplaza a `PEOPLE (roles)`.
  - Toma los `personajes` de los ids del beat, más los que el ancla nombra con su `nombre` entero.
  - Queda con personas en 11 fotos (cap 2: 3, cap 5: 2, cap 6: 4, cap 7: 2), lo mismo que simuló el analista.
- **S4:**
  - suma la línea del texto S4 en el SI, después de `people_group`, y `year` en el esquema;
  - la línea YEAR del expediente muestra solo el año del ancla, o «-»;
  - año final: 1) ancla; 2) `year` del modelo (1800–2100); 3)–5) respaldo;
  - en la prosa no se agrega `, {año}` si el `setting` ya trae un año o una década; `style_head` lleva el año final.
- **S5:** canon regenerado por `step_4e` (Flash), con el texto 1 de F46b + el texto S5 + la lista de los 35 `personajes` (rol · lugar · años). **Del canon regenerado se toman solo los `people_groups`**: el resto del canon sigue siendo el de F46b, «de base». El canon regenerado entero está en `canon_S5_regenerado.json`, y el que se usó en `canon_S5.json`.
- **Chascada:** el chequeo 5 busca solo el `nombre` entero. Desaparece el falso positivo «Subcomité de Wittenoom» (S0 baja de 2 a 0).
- **Prueba en seco** antes de gastar (`f48_corridas.py seco <dir>`, sin API).
- **Salidas** (en `lab/hyperframes/f48/`):
  - `PROMPTS_F48.md`: estado, tablas por cap y por etapa, chequeo 13, diffs del cap 6, prompts enteros de S5 y costos;
  - `PROMPTS_F48.json`;
  - crudos `slots_S1…S5_ch02/05/06/07.json`;
  - `pedidos/pedido_S{n}_chNN.txt`;
  - `canon_S5.json` y `canon_S5_regenerado.json`.

### Estado de cada llamada

| etapa | cap | estado | intentos | md5 system / user / esquema (1.er intento) |
|---|---|---|---|---|
| S1 | 2 | ok | 1 | 65d7f452 / 60ba353c / bcb706ab |
| S1 | 5 | ok | 1 | 65d7f452 / 7e2f5c02 / bcb706ab |
| S1 | 6 | ok | 1 | 65d7f452 / 0629fa77 / bcb706ab |
| S1 | 7 | ok | 1 | 65d7f452 / c29c9fb2 / bcb706ab |
| S2 | 2 | ok | 1 | 65d7f452 / 64b434d9 / bcb706ab |
| S2 | 5 | ok | 1 | 65d7f452 / 0de3308a / bcb706ab |
| S2 | 6 | ok | 1 | 65d7f452 / c4d7e4ef / bcb706ab |
| S2 | 7 | ok | 1 | 65d7f452 / 033d6ea4 / bcb706ab |
| S3 | 2 | ok | 1 | 65d7f452 / 91f905e1 / bcb706ab |
| S3 | 5 | ok | 1 | 65d7f452 / 06e022ab / bcb706ab |
| S3 | 6 | ok | 1 | 65d7f452 / 3f2cacda / bcb706ab |
| S3 | 7 | ok | 1 | 65d7f452 / 03300564 / bcb706ab |
| S4 | 2 | ok | 1 | 19428a86 / 8f5375b3 / fa1ebfd1 |
| S4 | 5 | ok | 1 | 19428a86 / 331cd11a / fa1ebfd1 |
| S4 | 6 | ok | 1 | 19428a86 / 108823b0 / fa1ebfd1 |
| S4 | 7 | ok | 1 | 19428a86 / be44b66e / fa1ebfd1 |
| S5 | 2 | ok | 1 | 19428a86 / bcaec272 / fa1ebfd1 |
| S5 | 5 | ok | 1 | 19428a86 / 6b68e86e / fa1ebfd1 |
| S5 | 6 | ok | 1 | 19428a86 / d86840e0 / fa1ebfd1 |
| S5 | 7 | ok | 1 | 19428a86 / 99d2c12b / fa1ebfd1 |

S1–S3 usan el mismo system y el mismo esquema (md5 `65d7f452` / `bcb706ab`, iguales a los de F47b). S4 y S5 cambian los dos: la línea `year` en el SI y en el esquema. Lo que varía entre etapas es el user-prompt.

### Tabla de los chequeos por foto (S0 \| S1 \| S2 \| S3 \| S4 \| S5)

1 año (fuente) · 2 año en `spans` · 3 lugar del DÓNDE en la prosa · 4 gente sin grupo · 5 nombre entero del ancla en la prosa · 6 `text_in_image` · 7 F8 · 8 palabras · 9 años/décadas del setting ≠ año de la foto · 10 negaciones en el setting · 11 año final (fuente) y si choca con el año/década del setting · 12 persona del pool (regla S3) y si la prosa dice su origen · 13 `people_group` (cap 7 fotos 7 y 8 abajo)

#### Cap 2

| foto | 1 año (fuente) S0–S3 | 2 canon | 3 lugar | 4 sin grupo | 5 nombre ancla → prosa | 6 texto | 7 F8 | 8 palabras | 9 año setting ≠ | 10 negaciones | 11 año final (fuente) · choca | 12 persona del pool · origen | grupos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1961 (1) dicho en el ancla) | sí | Madrid \| Madrid \| Madrid \| Madrid \| Madrid \| Madrid | no \| no \| no \| no \| no \| no | María Bernal → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 164 \| 168 \| 165 \| 159 \| 153 \| 182 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1961 (1) \| 1961 (1) \| 1961 (1) \| 1961 (1) \| 1961 (1) \| 1961 (1) | Esposa del minero Daniel Écija y residente de Wittenoom · Wittenoom · 1962, 1963 · rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen | european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| spanish_migrant_miners_wittenoom, spanish_migrant_wives_wittenoom |
| 2 | 1962 (1) dicho en el ancla) | sí | Madrid \| Madrid \| Madrid \| Madrid \| Madrid \| Madrid | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 139 \| 148 \| 141 \| 142 \| 152 \| 151 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (1) \| 1962 (1) \| 1962 (1) \| 1962 (1) \| 1962 (1) \| 1962 (1) | — · — \| — \| — \| — \| — \| — | european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| spanish_migrant_miners_wittenoom, spanish_migrant_wives_wittenoom |
| 3 | 1962 (2) el de la foto anterior del cap) | sí | no \| Australia \| Australia \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 130 \| 143 \| 150 \| 134 \| 137 \| 145 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) | — · — \| — \| — \| — \| — \| — | european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| spanish_migrant_miners_wittenoom, spanish_migrant_wives_wittenoom |
| 4 | 1962 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 111 \| 126 \| 130 \| 122 \| 127 \| 128 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) | — · — \| — \| — \| — \| — \| — | european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| spanish_migrant_miners_wittenoom, spanish_migrant_wives_wittenoom |
| 5 | 1962 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 125 \| 128 \| 130 \| 124 \| 132 \| 125 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) | — · — \| — \| — \| — \| — \| — | european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| spanish_migrant_wives_wittenoom, spanish_migrant_miners_wittenoom |
| 6 | 1962 (2) el de la foto anterior del cap) | sí | no \| Madrid \| Madrid \| no \| Madrid \| Madrid | no \| no \| no \| no \| no \| no | Milagros Barroso, Ramón de Juan → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 126 \| 136 \| 127 \| 129 \| 138 \| 139 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1963 (2) \| 1962 (2) | Esposa del minero Ramón de Juan y residente de Wittenoom · Wittenoom · 1962, 1963, 1964; Minero español en Wittenoom · Wittenoom · 1962, 1963, 1964 · español: sí \| español: sí \| español: sí \| español: sí \| español: sí \| español: sí | european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| spanish_migrant_wives_wittenoom, spanish_migrant_miners_wittenoom, wittenoom_child_residents |
| 7 | 1962 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 113 \| 129 \| 130 \| 132 \| 126 \| 121 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) | — · — \| — \| — \| — \| — \| — | wittenoom_children \| wittenoom_children \| wittenoom_children, european_migrant_families \| wittenoom_children \| european_migrant_families, wittenoom_children \| wittenoom_child_residents |
| 8 | 1962 (2) el de la foto anterior del cap) | sí | Málaga \| Málaga \| Málaga \| Málaga \| Málaga \| Málaga | no \| no \| no \| no \| no \| no | Víctor Calvo → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 118 \| 132 \| 129 \| 126 \| 130 \| 124 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) | Hijo de Milagros Barroso, vivió en Wittenoom de niño · Wittenoom · 1962, 1963, 1964 · rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen | european_migrant_families, wittenoom_children \| wittenoom_children, european_migrant_families \| european_migrant_families, wittenoom_children \| european_migrant_families, wittenoom_children \| european_migrant_families, wittenoom_children \| wittenoom_child_residents, spanish_migrant_wives_wittenoom |
| 9 | 1962 (2) el de la foto anterior del cap) | sí | Málaga \| Málaga \| Málaga \| Málaga \| Málaga \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 103 \| 113 \| 115 \| 110 \| 104 \| 105 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 10 | 1962 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 120 \| 139 \| 119 \| 116 \| 119 \| 120 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) | — · — \| — \| — \| — \| — \| — | european_migrant_families \| european_migrant_families, wittenoom_children \| european_migrant_families \| [] \| european_migrant_families \| [] |
| 11 | 1962 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 122 \| 136 \| 142 \| 129 \| 130 \| 148 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) | — · — \| — \| — \| — \| — \| — | european_migrant_families, wittenoom_children \| european_migrant_families, wittenoom_children \| european_migrant_families \| european_migrant_families, wittenoom_children \| european_migrant_families, wittenoom_children \| spanish_migrant_wives_wittenoom, spanish_migrant_miners_wittenoom, wittenoom_child_residents |
| 12 | 1962 (2) el de la foto anterior del cap) | sí | Australia \| Australia \| Australia \| Australia \| Australia \| Australia | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 106 \| 108 \| 109 \| 112 \| 113 \| 109 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 13 | 1962 (2) el de la foto anterior del cap) | sí | Australia \| Wittenoom \| Wittenoom \| no \| no \| Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | sí «WITTENOOM» (en) \| no \| no \| sí «WITTENOOM» (en) \| sí «WITTENOOM» (en) \| sí «WITTENOOM» (en) | — \| — \| — \| — \| — \| — | 129 \| 135 \| 133 \| 134 \| 134 \| 143 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) | — · — \| — \| — \| — \| — \| — | [] \| european_migrant_families \| european_migrant_families \| european_migrant_families \| [] \| [] |
| 14 | 1962 (2) el de la foto anterior del cap) | sí | no \| Wittenoom \| Wittenoom \| Wittenoom \| no \| Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| menor en daño: Wide shot, Eye-level behind the boy, Deep depth of field, 35mm lens. \| — \| — \| — \| — | 132 \| 122 \| 135 \| 134 \| 144 \| 166 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) | — · — \| — \| — \| — \| — \| — | european_migrant_families, wittenoom_children \| wittenoom_children, european_migrant_families \| european_migrant_families, wittenoom_children \| european_migrant_families, wittenoom_children \| european_migrant_families, wittenoom_children \| spanish_migrant_miners_wittenoom, spanish_migrant_wives_wittenoom, wittenoom_child_residents |
| 15 | 1962 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom \| Wittenoom \| no \| no \| Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 118 \| 137 \| 119 \| 127 \| 138 \| 125 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) | — · — \| — \| — \| — \| — \| — | mining_workers \| mining_workers \| mining_workers \| mining_workers \| mining_workers \| [] |
| 16 | 1962 (2) el de la foto anterior del cap) | sí | no \| Wittenoom \| Wittenoom \| Wittenoom \| no \| Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 138 \| 137 \| 139 \| 130 \| 140 \| 162 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) \| 1962 (2) | — · — \| — \| — \| — \| — \| — | european_migrant_families, wittenoom_children \| european_migrant_families, wittenoom_children \| wittenoom_children, european_migrant_families \| european_migrant_families, wittenoom_children \| wittenoom_children, european_migrant_families \| wittenoom_child_residents, spanish_migrant_wives_wittenoom |
| **total cap 2** | — | — | **7 \| 11 \| 11 \| 7 \| 6 \| 9** | **0 \| 0 \| 0 \| 0 \| 0 \| 0** | **0 \| 0 \| 0 \| 0 \| 0 \| 0** | **1 \| 0 \| 0 \| 1 \| 1 \| 1** | **0 \| 1 \| 0 \| 0 \| 0 \| 0** | **125 \| 134 \| 132 \| 129 \| 132 \| 137** | **0 \| 0 \| 0 \| 0 \| 0 \| 0** | **0 \| 0 \| 0 \| 0 \| 0 \| 0** | **0 chocan \| 0 chocan \| 0 chocan \| 0 chocan \| 0 chocan \| 0 chocan** | **1/1 con origen \| 1/1 con origen \| 1/1 con origen \| 1/1 con origen \| 1/1 con origen \| 1/1 con origen** | — |

#### Cap 5

| foto | 1 año (fuente) S0–S3 | 2 canon | 3 lugar | 4 sin grupo | 5 nombre ancla → prosa | 6 texto | 7 F8 | 8 palabras | 9 año setting ≠ | 10 negaciones | 11 año final (fuente) · choca | 12 persona del pool · origen | grupos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1966 (1) dicho en el ancla) | sí | Wittenoom \| Wittenoom \| Wittenoom \| Australia, Wittenoom \| Wittenoom \| Australia, Wittenoom | no \| no \| no \| no \| no \| no | James Vernon → no \| no \| no \| no \| no \| no | no \| sí «WITTENOOM MINE CLOSES» (en) \| sí «MINE CLOSING» (en) \| sí «MINE CLOSED» (en) \| sí «WITTENOOM MINE CLOSES» (en) \| no | — \| — \| — \| — \| — \| — | 177 \| 167 \| 158 \| 174 \| 181 \| 158 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1966 (1) \| 1966 (1) \| 1966 (1) \| 1966 (1) \| 1966 (1) \| 1966 (1) | Presidente de CSR · - · 1966 · rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen | mining_workers \| [] \| [] \| [] \| [] \| [] |
| 2 | 1966 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no \| sí \| sí | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 152 \| 141 \| 148 \| 139 \| 156 \| 129 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1966 (2) \| 1966 (2) \| 1966 (2) \| 1966 (2) \| 1966 (2) \| 1966 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 3 | 1966 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Australia, Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 141 \| 136 \| 136 \| 130 \| 151 \| 125 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1966 (2) \| 1966 (2) \| 1966 (2) \| 1966 (2) \| 1966 (2) \| 1966 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 4 | 1966 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 151 \| 137 \| 150 \| 135 \| 168 \| 153 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1966 (2) \| 1966 (2) \| 1966 (2) \| 1966 (2) \| 1966 (2) \| 1966 (2) | — · — \| — \| — \| — \| — \| — | mining_workers \| mining_workers \| mining_workers \| mining_workers \| mining_workers \| spanish_migrant_miners_wittenoom, wittenoom_general_workers |
| 5 | 1966 (2) el de la foto anterior del cap) | sí | Madrid \| Australia, Madrid \| Madrid \| Madrid \| Madrid \| Madrid | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 166 \| 148 \| 138 \| 133 \| 149 \| 152 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1966 (2) \| 1966 (2) \| 1966 (2) \| 1966 (2) \| 1966 (2) \| 1966 (2) | — · — \| — \| — \| — \| — \| — | european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| spanish_migrant_miners_wittenoom, spanish_migrant_wives_wittenoom, wittenoom_child_residents |
| 6 | 1971 (1) dicho en el ancla) | sí | Wittenoom \| Wittenoom \| no \| no \| no \| Australia, Madrid | no \| no \| no \| no \| no \| no | Mercedes de Juan → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| menor en daño: Wide shot, Low angle from behind the girl, Deep depth of field, 35mm lens. \| — \| — | 159 \| 138 \| 138 \| 116 \| 149 \| 123 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1971 (1) \| 1971 (1) \| 1971 (1) \| 1971 (1) \| 1971 (1) \| 1971 (1) | Hija de Ramón de Juan, vivió en Wittenoom de niña · Wittenoom · 1962, 1963, 1964 · rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen | european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| european_migrant_families \| wittenoom_child_residents |
| 7 | 1971 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 133 \| 134 \| 122 \| 126 \| 143 \| 125 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1971 (2) \| 1971 (2) \| 1971 (2) \| 1971 (2) \| 1966 (2) \| 1967 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 8 | 1985 (1) dicho en el ancla) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| sí | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| sí «WITTENOOM» (en) \| sí «WITTENOOM» (en) | — \| — \| — \| — \| — \| — | 158 \| 158 \| 137 \| 150 \| 174 \| 140 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1985 (1) \| 1985 (1) \| 1985 (1) \| 1985 (1) \| 1985 (1) \| 1985 (1) | — · — \| — \| — \| — \| — \| — | european_migrant_families \| european_migrant_families \| european_migrant_families \| officials_regulators, european_migrant_families \| wittenoom_children, officials_regulators \| [] |
| 9 | 1985 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | sí \| no \| sí \| sí \| no \| no | — → no \| no \| no \| no \| no \| no | sí «WITTENOOM» (en) \| sí «WITTENOOM» (en) \| no \| sí «WITTENOOM» (en) \| no \| no | — \| — \| — \| — \| — \| — | 127 \| 116 \| 126 \| 136 \| 143 \| 134 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1985 (2) \| 1985 (2) \| 1985 (2) \| 1985 (2) \| 1985 (2) \| 1985 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| wittenoom_children, officials_regulators \| wittenoom_child_residents |
| 10 | 1978 (1) dicho en el ancla) | sí | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Australia, Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | sí «ASBESTOS HAZARD» (en) \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 138 \| 134 \| 123 \| 130 \| 136 \| 124 | 1985 \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1978 (1) · choca 1985 \| 1978 (1) \| 1978 (1) \| 1978 (1) \| 1978 (1) \| 1978 (1) | — · — \| — \| — \| — \| — \| — | [] \| european_migrant_families \| [] \| european_migrant_families \| [] \| [] |
| 11 | 1986 (1) dicho en el ancla) | sí | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 130 \| 132 \| 117 \| 126 \| 137 \| 119 | 1992 \| 1992 \| — \| — \| 1992 \| — | — \| — \| — \| — \| — \| — | 1986 (1) · choca 1992 \| 1986 (1) · choca 1992 \| 1986 (1) \| 1986 (1) \| 1986 (1) · choca 1992 \| 1986 (1) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 12 | 1993 (1) dicho en el ancla) | sí | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Australia, Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| sí «AIRPORT CLOSED» (en) \| no \| no \| no | — \| — \| — \| — \| — \| — | 118 \| 111 \| 120 \| 118 \| 124 \| 115 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1993 (1) \| 1993 (1) \| 1993 (1) \| 1993 (1) \| 1993 (1) \| 1993 (1) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 13 | 1991 (1) dicho en el ancla) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 140 \| 151 \| 127 \| 136 \| 138 \| 130 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1991 (1) \| 1991 (1) \| 1991 (1) \| 1991 (1) \| 1991 (1) \| 1991 (1) | — · — \| — \| — \| — \| — \| — | asbestos_advocates_victims \| asbestos_advocates_victims \| [] \| asbestos_advocates_victims \| asbestos_advocates_victims \| spanish_migrant_miners_wittenoom |
| 14 | 1991 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| sí | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 121 \| 127 \| 119 \| 131 \| 129 \| 130 | — \| 1992 \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1991 (2) \| 1991 (2) · choca 1992 \| 1991 (2) \| 1991 (2) \| 1992 (2) \| 1991 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| european_migrant_families \| [] |
| 15 | 1991 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 146 \| 141 \| 143 \| 139 \| 148 \| 131 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1991 (2) \| 1991 (2) \| 1991 (2) \| 1991 (2) \| 2023 (2) \| 2024 (2) | — · — \| — \| — \| — \| — \| — | european_migrant_families \| european_migrant_families \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| spanish_migrant_wives_wittenoom |
| 16 | 1991 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 144 \| 138 \| 142 \| 135 \| 138 \| 139 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1991 (2) \| 1991 (2) \| 1991 (2) \| 1991 (2) \| 2023 (2) \| 2024 (2) | — · — \| — \| — \| — \| — \| — | european_migrant_families \| european_migrant_families \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| spanish_migrant_wives_wittenoom |
| **total cap 5** | — | — | **10 \| 10 \| 9 \| 9 \| 9 \| 10** | **1 \| 0 \| 1 \| 1 \| 1 \| 3** | **0 \| 0 \| 0 \| 0 \| 0 \| 0** | **2 \| 2 \| 2 \| 2 \| 2 \| 1** | **0 \| 0 \| 0 \| 1 \| 0 \| 0** | **144 \| 138 \| 134 \| 135 \| 148 \| 133** | **2 \| 2 \| 0 \| 0 \| 1 \| 0** | **0 \| 0 \| 0 \| 0 \| 0 \| 0** | **2 chocan \| 2 chocan \| 0 chocan \| 0 chocan \| 1 chocan \| 0 chocan** | **0/0 con origen \| 0/0 con origen \| 0/0 con origen \| 0/0 con origen \| 0/0 con origen \| 0/0 con origen** | — |

#### Cap 6

| foto | 1 año (fuente) S0–S3 | 2 canon | 3 lugar | 4 sin grupo | 5 nombre ancla → prosa | 6 texto | 7 F8 | 8 palabras | 9 año setting ≠ | 10 negaciones | 11 año final (fuente) · choca | 12 persona del pool · origen | grupos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1989 (1) dicho en el ancla) | sí | no \| no \| no \| no \| Australia \| Australia | no \| no \| no \| no \| sí \| sí | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 151 \| 126 \| 122 \| 144 \| 147 \| 122 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1989 (1) \| 1989 (1) \| 1989 (1) \| 1989 (1) \| 1989 (1) \| 1989 (1) | — · — \| — \| — \| — \| — \| — | asbestos_advocates_victims \| [] \| [] \| asbestos_advocates_victims \| [] \| [] |
| 2 | 1989 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 174 \| 150 \| 152 \| 158 \| 171 \| 162 | 1979 \| 1979 \| — \| 1979 \| — \| — | — \| — \| — \| — \| — \| — | 1989 (2) · choca 1979 \| 1989 (2) · choca 1979 \| 1989 (2) \| 1989 (2) · choca 1979 \| 1979 (2) \| 1979 (2) | — · — \| — \| — \| — \| — \| — | asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_society_advocates |
| 3 | 1988 (1) dicho en el ancla) | sí | no \| no \| no \| no \| Australia \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 155 \| 155 \| 146 \| 144 \| 170 \| 154 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1988 (1) \| 1988 (1) \| 1988 (1) \| 1988 (1) \| 1988 (1) \| 1988 (1) | — · — \| — \| — \| — \| — \| — | asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims, officials_regulators \| officials_regulators, asbestos_advocates_victims \| asbestos_advocates_victims, officials_regulators \| wittenoom_general_workers |
| 4 | 1988 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | Mercedes de Juan → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 137 \| 130 \| 124 \| 129 \| 133 \| 118 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1988 (2) \| 1988 (2) \| 1988 (2) \| 1988 (2) \| 2023 (2) \| 2023 (2) | Hija de Ramón de Juan, vivió en Wittenoom de niña · Wittenoom · 1962, 1963, 1964 · rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen | asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| wittenoom_child_residents |
| 5 | 1988 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 137 \| 128 \| 119 \| 118 \| 128 \| 123 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1988 (2) \| 1988 (2) \| 1988 (2) \| 1988 (2) \| 2023 (2) \| 2023 (2) | — · — \| — \| — \| — \| — \| — | asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| wittenoom_child_residents |
| 6 | 1988 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 117 \| 108 \| 95 \| 101 \| 119 \| 103 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1988 (2) \| 1988 (2) \| 1988 (2) \| 1988 (2) \| 2023 (2) \| 2023 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 7 | 1988 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 127 \| 130 \| 108 \| 119 \| 121 \| 106 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1988 (2) \| 1988 (2) \| 1988 (2) \| 1988 (2) \| 2023 (2) \| 2023 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 8 | 1988 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | Melita Markey → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 143 \| 131 \| 128 \| 136 \| 151 \| 110 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1988 (2) \| 1988 (2) \| 1988 (2) \| 1988 (2) \| 2023 (2) \| 2023 (2) | CEO de la Asbestos Deseases Society of Australia · - · - · rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen | asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| [] |
| 9 | 1988 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 119 \| 122 \| 107 \| 106 \| 122 \| 115 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1988 (2) \| 1988 (2) \| 1988 (2) \| 1988 (2) \| 2006 (2) \| 2006 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 10 | 2007 (1) dicho en el ancla) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| sí | — → no \| no \| no \| no \| no \| no | no \| no \| sí «WITTENOOM» (en) \| no \| sí «WITTENOOM» (en) \| sí «WITTENOOM» (en) | — \| — \| — \| — \| — \| — | 139 \| 123 \| 125 \| 127 \| 160 \| 132 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2007 (1) \| 2007 (1) \| 2007 (1) \| 2007 (1) \| 2007 (1) \| 2007 (1) | — · — \| — \| — \| — \| — \| — | officials_regulators \| officials_regulators \| officials_regulators \| officials_regulators \| officials_regulators \| [] |
| 11 | 2007 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | sí «WITTENOOM ABOLISHED» (en) \| sí «Wittenoom Abolished» (en) \| no \| sí «WITTENOOM ABOLISHED» (en) \| no \| no | — \| — \| — \| — \| — \| — | 126 \| 110 \| 98 \| 113 \| 125 \| 100 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2007 (2) \| 2007 (2) \| 2007 (2) \| 2007 (2) \| 2007 (2) \| 2007 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| officials_regulators \| [] |
| 12 | 1992 (1) dicho en el ancla) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 115 \| 107 \| 103 \| 97 \| 129 \| 130 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1992 (1) \| 1992 (1) \| 1992 (1) \| 1992 (1) \| 1992 (1) \| 1992 (1) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| parliamentary_inquiry_members |
| 13 | 1992 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | Larry Graham → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 122 \| 122 \| 110 \| 111 \| 125 \| 104 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1992 (2) \| 1992 (2) \| 1992 (2) \| 1992 (2) \| 1994 (2) \| 1994 (2) | Presidente de comité parlamentario · - · 1994 · rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen | [] \| [] \| [] \| [] \| [] \| [] |
| 14 | 1992 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | Mark Nevill → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 119 \| 119 \| 113 \| 105 \| 135 \| 108 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 1992 (2) \| 1992 (2) \| 1992 (2) \| 1992 (2) \| 1992 (2) \| 1992 (2) | Líder de investigación parlamentaria · - · 1992 · rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen \| rol sin origen | [] \| [] \| [] \| [] \| [] \| [] |
| 15 | 2016 (1) dicho en el ancla) | año fuera del canon | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| sí \| no | — → no \| no \| no \| no \| no \| no | no \| sí «Asbestos Danger» (en) \| sí «ASBESTOS DANGER» (en) \| no \| no \| sí «Wittenoom Gorge» (en) | — \| — \| — \| — \| — \| — | 117 \| 126 \| 121 \| 98 \| 128 \| 105 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2016 (1) \| 2016 (1) \| 2016 (1) \| 2016 (1) \| 2016 (1) \| 2016 (1) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 16 | 2023 (1) dicho en el ancla) | año fuera del canon | no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| sí «DANGER ASBESTOS» (en) \| sí «DANGER ASBESTOS» (en) \| no | — \| — \| — \| — \| — \| — | 148 \| 124 \| 113 \| 119 \| 164 \| 125 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2023 (1) \| 2023 (1) \| 2023 (1) \| 2023 (1) \| 2023 (1) \| 2023 (1) | — · — \| — \| — \| — \| — \| — | asbestos_advocates_victims \| [] \| [] \| [] \| asbestos_advocates_victims \| banjima_elders_activists |
| **total cap 6** | — | — | **0 \| 0 \| 0 \| 0 \| 2 \| 1** | **0 \| 0 \| 0 \| 0 \| 2 \| 2** | **0 \| 0 \| 0 \| 0 \| 0 \| 0** | **1 \| 2 \| 2 \| 2 \| 2 \| 2** | **0 \| 0 \| 0 \| 0 \| 0 \| 0** | **134 \| 126 \| 118 \| 120 \| 139 \| 120** | **1 \| 1 \| 0 \| 1 \| 0 \| 0** | **0 \| 0 \| 0 \| 0 \| 0 \| 0** | **1 chocan \| 1 chocan \| 0 chocan \| 1 chocan \| 0 chocan \| 0 chocan** | **0/0 con origen \| 0/0 con origen \| 0/0 con origen \| 0/0 con origen \| 0/0 con origen \| 0/0 con origen** | — |

#### Cap 7 (Veo: suplementarias)

| foto | 1 año (fuente) S0–S3 | 2 canon | 3 lugar | 4 sin grupo | 5 nombre ancla → prosa | 6 texto | 7 F8 | 8 palabras | 9 año setting ≠ | 10 negaciones | 11 año final (fuente) · choca | 12 persona del pool · origen | grupos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2023 (3) el último del cap anterior) | año fuera del canon | Wittenoom \| Wittenoom \| Wittenoom \| Australia \| Wittenoom \| Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 146 \| 133 \| 151 \| 150 \| 130 \| 146 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2023 (3) \| 2023 (3) \| 2023 (3) \| 2023 (3) \| 2021 (2) \| 2021 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 2 | 2023 (2) el de la foto anterior del cap) | año fuera del canon | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| no \| Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | color_palette: faint blue-grey veins of tailings in the gullies; props_detail: a single deep erosion gully linking the dump to the creek bed like an open vein \| — \| — \| — \| — \| — | 114 \| 126 \| 147 \| 149 \| 130 \| 134 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2023 (2) \| 2023 (2) \| 2023 (2) \| 2023 (2) \| 2021 (2) \| 2021 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| western_australian_officials_modern |
| 3 | 2023 (2) el de la foto anterior del cap) | año fuera del canon | Fortescue, Wittenoom \| Fortescue, Wittenoom \| Fortescue \| Fortescue, Wittenoom \| Fortescue, Wittenoom \| Fortescue, Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 131 \| 132 \| 142 \| 140 \| 124 \| 138 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2023 (2) \| 2023 (2) \| 2023 (2) \| 2023 (2) \| 2021 (2) \| 2021 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 4 | 2023 (2) el de la foto anterior del cap) | año fuera del canon | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 131 \| 123 \| 134 \| 133 \| 118 \| 127 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2023 (2) \| 2023 (2) \| 2023 (2) \| 2023 (2) \| 2021 (2) \| 2021 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 5 | 2021 (1) dicho en el ancla) | año fuera del canon | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 134 \| 126 \| 141 \| 132 \| 122 \| 138 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2021 (1) \| 2021 (1) \| 2021 (1) \| 2021 (1) \| 2021 (1) \| 2021 (1) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 6 | 2021 (2) el de la foto anterior del cap) | año fuera del canon | Fortescue \| Fortescue, Wittenoom \| Fortescue \| Fortescue, Wittenoom \| Fortescue \| Fortescue | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 123 \| 122 \| 137 \| 129 \| 116 \| 123 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| no human presence | 2021 (2) \| 2021 (2) \| 2021 (2) \| 2021 (2) \| 2021 (2) \| 2021 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 7 | 2023 (1) dicho en el ancla) | año fuera del canon | Wittenoom \| Wittenoom \| Wittenoom \| no \| Wittenoom \| Wittenoom | no \| no \| no \| no \| no \| no | Maitland Parker → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 141 \| 134 \| 161 \| 149 \| 128 \| 154 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2023 (1) \| 2023 (1) \| 2023 (1) \| 2023 (1) \| 2023 (1) \| 2023 (1) | Anciano Banjima, activista y víctima de mesotelioma · Wittenoom · 2023, 2024 · banjima: sí \| banjima: sí \| banjima: sí \| banjima: sí \| banjima: sí \| banjima: sí | asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| banjima_elders_activists |
| 8 | 2023 (2) el de la foto anterior del cap) | año fuera del canon | Wittenoom \| Wittenoom \| Wittenoom \| no \| Wittenoom \| Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 145 \| 127 \| 159 \| 140 \| 131 \| 142 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2023 (2) \| 2023 (2) \| 2023 (2) \| 2023 (2) \| 2023 (2) \| 2023 (2) | — · — \| — \| — \| — \| — \| — | asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| asbestos_advocates_victims \| banjima_elders_activists |
| 9 | 2024 (1) dicho en el ancla) | año fuera del canon | Wittenoom \| Wittenoom \| Wittenoom \| no \| Wittenoom \| Wittenoom | no \| no \| no \| no \| no \| no | Maitland Parker → no \| no \| no \| no \| no \| no | no \| no \| no \| no \| no \| no | — \| — \| — \| — \| — \| — | 120 \| 119 \| 131 \| 125 \| 113 \| 122 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2024 (1) \| 2024 (1) \| 2024 (1) \| 2024 (1) \| 2024 (1) \| 2024 (1) | Anciano Banjima, activista y víctima de mesotelioma · Wittenoom · 2023, 2024 · banjima: sí \| banjima: sí \| banjima: sí \| banjima: sí \| banjima: sí \| banjima: sí | [] \| [] \| [] \| [] \| [] \| [] |
| 10 | 2024 (2) el de la foto anterior del cap) | año fuera del canon | Australia, Federal \| Australia, Federal \| no \| Federal \| Federal \| Australia, Federal | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | sí «FEDERAL COURT» (en) \| no \| sí «BANJIMA SUE STATE» (en) \| sí «FEDERAL COURT» (en) \| no \| no | — \| — \| — \| — \| — \| — | 126 \| 127 \| 135 \| 141 \| 128 \| 132 | — \| — \| — \| 2026 \| — \| — | — \| — \| — \| — \| — \| — | 2024 (2) \| 2024 (2) \| 2024 (2) \| 2024 (2) · choca 2026 \| 2026 (2) \| 2026 (2) | — · — \| — \| — \| — \| — \| — | asbestos_advocates_victims \| asbestos_advocates_victims \| [] \| asbestos_advocates_victims \| asbestos_advocates_victims \| bntac_representatives |
| 11 | 2024 (2) el de la foto anterior del cap) | año fuera del canon | Wittenoom \| Gorge, Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom \| Gorge, Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | sí «ROAD CLOSED» (en) \| no \| no \| sí «ROAD CLOSED» (en) \| sí «ROAD CLOSED» (en) \| sí «DANGER ASBESTOS» (en) | — \| — \| — \| — \| — \| — | 137 \| 126 \| 133 \| 131 \| 126 \| 142 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2024 (2) \| 2024 (2) \| 2024 (2) \| 2024 (2) \| 2026 (2) \| 2026 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| 12 | 2024 (2) el de la foto anterior del cap) | año fuera del canon | Wittenoom \| Gorge, Wittenoom \| Gorge, Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no \| no \| no | — → no \| no \| no \| no \| no \| no | no \| sí «DANGER ASBESTOS» (en) \| sí «ASBESTOS DANGER» (en) \| no \| no \| no | — \| — \| — \| — \| — \| — | 123 \| 124 \| 140 \| 127 \| 115 \| 126 | — \| — \| — \| — \| — \| — | — \| — \| — \| — \| — \| — | 2024 (2) \| 2024 (2) \| 2024 (2) \| 2024 (2) \| 2026 (2) \| 2026 (2) | — · — \| — \| — \| — \| — \| — | [] \| [] \| [] \| [] \| [] \| [] |
| **total cap 7** | — | — | **12 \| 12 \| 11 \| 9 \| 11 \| 12** | **0 \| 0 \| 0 \| 0 \| 0 \| 0** | **0 \| 0 \| 0 \| 0 \| 0 \| 0** | **2 \| 1 \| 2 \| 2 \| 1 \| 1** | **1 \| 0 \| 0 \| 0 \| 0 \| 0** | **131 \| 127 \| 143 \| 137 \| 123 \| 135** | **0 \| 0 \| 0 \| 1 \| 0 \| 0** | **0 \| 0 \| 0 \| 0 \| 0 \| 1** | **0 chocan \| 0 chocan \| 0 chocan \| 1 chocan \| 0 chocan \| 0 chocan** | **2/2 con origen \| 2/2 con origen \| 2/2 con origen \| 2/2 con origen \| 2/2 con origen \| 2/2 con origen** | — |

#### Totales por etapa (los 4 caps, 60 fotos)

| etapa | fotos | 3 lugar | 4 sin grupo | 5 nombre en la prosa | 6 texto | 7 F8 | 8 palabras prom. | 9 año setting ≠ | 10 negaciones | 11 choca | 12 origen dicho / fotos con persona de origen conocido |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 | 60 | 29 | 1 | 0 | 6 | 1 | 134 | 3 | 0 | 3 | 3/3 |
| S1 | 60 | 33 | 0 | 0 | 5 | 1 | 131 | 3 | 0 | 3 | 3/3 |
| S2 | 60 | 31 | 1 | 0 | 6 | 0 | 131 | 0 | 0 | 0 | 3/3 |
| S3 | 60 | 25 | 1 | 0 | 7 | 1 | 130 | 2 | 0 | 2 | 3/3 |
| S4 | 60 | 28 | 3 | 0 | 6 | 0 | 136 | 1 | 0 | 1 | 3/3 |
| S5 | 60 | 32 | 5 | 0 | 5 | 0 | 131 | 0 | 1 | 0 | 3/3 |

En S0–S3, «2)» es «el de la foto anterior del cap» (regla de F46b). En S4–S5, «2)» es el casillero `year` del modelo. La columna 1 muestra el año de S0–S3; el de cada etapa está en la columna 11.

### Año por etapa (medido sobre `PROMPTS_F48.json` y `PROMPTS_F47b.json`)
| etapa | fuente del año: 1) ancla / 2) / 3)–5) respaldo | año dos veces en «setting, año» | casillero `year` lleno |
|---|---|---|---|
| S0 | 18 / 41 (foto anterior) / 1 | 33 | — |
| S1 | 18 / 41 / 1 | 40 | — |
| S2 | 18 / 41 / 1 | 31 | — |
| S3 | 18 / 41 / 1 | 34 | — |
| S4 | 18 / 42 (`year`) / 0 | **0** | 60/60 |
| S5 | 18 / 42 (`year`) / 0 | **0** | 60/60 |

- **S4 cambia el año de 20 fotos respecto de S3:**
  - cap 2: 6 (1962→1963);
  - cap 5: 7 (1971→1966), 14 (1991→1992), 15 y 16 (1991→2023);
  - cap 6: 2 (1989→**1979**), 4–8 (1988→2023), 9 (1988→2006), 13 (1992→1994);
  - cap 7: 1–4 (2023→2021), 10–12 (2024→2026).
  - En los casos que miré, el año sigue a la voz: cap 6 foto 2, «diez años antes» de 1989 → 1979, y el prompt ya no dice 1989; cap 7 foto 10, «dos años después» de 2024 → 2026; cap 6 fotos 4–8, «ahora», Mercedes en el escáner → 2023.
- **S5** coincide con S4 salvo en 5 fotos: cap 2 foto 6 vuelve a 1962, cap 5 foto 7 da 1967, cap 5 foto 14 da 1991 (no 1992), y cap 5 fotos 15–16 dan 2024 (no 2023).

### Chequeo 13: `people_group` de las fotos 7 y 8 del cap 7, y los `people_groups` del canon

| etapa | cap 7 foto 7 | cap 7 foto 8 |
|---|---|---|
| S0 | asbestos_advocates_victims | asbestos_advocates_victims |
| S1 | asbestos_advocates_victims | asbestos_advocates_victims |
| S2 | asbestos_advocates_victims | asbestos_advocates_victims |
| S3 | asbestos_advocates_victims | asbestos_advocates_victims |
| S4 | asbestos_advocates_victims | asbestos_advocates_victims |
| S5 | banjima_elders_activists | banjima_elders_activists |

**S0–S4 (canon C de F46b)** — 5 grupos:

- `mining_workers` — who: Workers employed in the crocidolite asbestos mines and mill, including both local and migrant laborers. · where_when: Wittenoom mines and mill, predominantly 1937-1966, but especially in the 1950s-1960s. · appearance: Men of various ethnicities (Australian, European), typically robust builds for manual labor, often covered in asbestos dust. · clothing: Basic, durable workwear: sturdy shirts, trousers, boots, sometimes with simple protective gear, all heavily soiled with dust.
- `european_migrant_families` — who: Families from European countries, particularly Spain, recruited to work and live in Wittenoom. · where_when: Arriving in Wittenoom, living in the town from the late 1940s through the mid-1960s. · appearance: People of European descent, including young adults, women, and children, adjusting to an arid environment. · clothing: Everyday civilian clothing typical of mid-20th century European styles, adapted for hot weather, often showing signs of wear and dust.
- `wittenoom_children` — who: Children born or raised in Wittenoom, exposed to asbestos through play and daily life. · where_when: Playing in the town's patios, roads, and public spaces, 1950s-1960s. · appearance: Young children, often seen playing outdoors, with faces and clothes dusty from the environment. · clothing: Simple, functional play clothes typical of mid-20th century children's wear, suited for a hot climate, often dirty.
- `officials_regulators` — who: Mine inspectors, state engineers, company representatives (e.g., CSR), and government officials. · where_when: Visiting the mine and town in various capacities from the 1940s to the 1960s. · appearance: Typically men, appearing professional and authoritative, often in contrast to the dusty environment of the workers. · clothing: Formal or semi-formal business attire (shirts, trousers, jackets) of the mid-20th century, possibly adapted for fieldwork.
- `asbestos_advocates_victims` — who: Former workers and residents suffering from asbestos-related diseases, and their legal/health advocates. · where_when: From the 1970s onwards, in Australia and elsewhere, involved in lawsuits and advocacy. · appearance: People of various ages, often elderly and showing signs of illness, or legal professionals. · clothing: Contemporary civilian clothing for the period they are depicted, reflecting the late 20th and early 21st centuries.

**S5 (regenerado)** — 15 grupos:

- `mine_regulatory_officials` — who: Australian government mine inspectors and deputy state mining engineers · where_when: Reporting on dust problems in Wittenoom from 1944 onwards · appearance: Middle-aged Caucasian men, typically in official attire. · clothing: Formal shirts, trousers, and possibly ties or light jackets, typical of mid-20th century civil servants.
- `early_mine_operators` — who: Early prospectors and mine operators, co-owners of the mining interests (e.g., Hancock and Wright) · where_when: Operating the crocidolite industry in Wittenoom Gorge from 1937 to 1943 · appearance: Adult Caucasian men, likely rugged, showing signs of hard manual labor in a remote environment. · clothing: Practical, durable work clothes like shirts, trousers, boots, suitable for mining and the desert climate of the 1930s-1940s.
- `public_health_professionals` — who: Australian public health doctors, commissioners, and industrial hygienists investigating asbestos-related diseases and conditions · where_when: Reporting on dust levels, diagnosing illnesses, and assessing workplace safety in Wittenoom from the 1940s to 1960s · appearance: Adult Caucasians, professional and authoritative demeanor. · clothing: Formal or semi-formal attire, such as shirts, ties, lab coats, and possibly safety glasses, typical for medical and technical professionals in mid-20th century Australia.
- `csr_executives` — who: Executives and chairmen of CSR, the company operating the Wittenoom mine · where_when: Managing mining operations, making decisions regarding safety, and announcing closure from the 1940s to 1960s · appearance: Older Caucasian men, professional and authoritative in appearance. · clothing: Business suits, shirts, and ties, representing corporate management of the mid-20th century.
- `parliamentary_inquiry_members` — who: Australian politicians leading parliamentary inquiries into the Wittenoom disaster · where_when: Recommending clean-up programs and remediation actions in the early 1990s and beyond · appearance: Middle-aged to older Caucasians, professional and serious demeanor. · clothing: Formal business attire, suits, and ties, appropriate for Australian parliamentarians in the 1990s.
- `banjima_elders_activists` — who: Banjima Indigenous elders and activists affected by the Wittenoom contamination · where_when: Advocating for remediation and justice in Wittenoom from 2023 onwards · appearance: Elderly Indigenous Australians, often showing the physical toll of illness and determination. · clothing: Practical, comfortable clothing, reflecting their connection to the land and modern-day activism.
- `bntac_representatives` — who: Representatives of the Banjima Native Title Aboriginal Corporation (BNTAC) · where_when: Pursuing legal action against the State of Western Australia in 2026 · appearance: Adult Indigenous Australians, professional and resolute, representing their community's interests. · clothing: Contemporary business or semi-formal attire, suitable for legal and advocacy contexts in the 2020s.
- `spanish_migrant_wives_wittenoom` — who: Spanish migrant women, wives of miners, residing in Wittenoom · where_when: Living in Wittenoom from the early to mid-1960s, managing family life in harsh conditions · appearance: Young to middle-aged Caucasian women of Southern European descent, often depicted in simple, practical attire for daily life. · clothing: Modest dresses or skirts and blouses, often homemade or simple, in light fabrics suitable for a hot desert climate of the 1960s.
- `wittenoom_child_residents` — who: Children of miners and other residents growing up in Wittenoom's dusty and asbestos-laden environment · where_when: Playing in the town's streets, patios, and schools from the 1940s to the 1960s · appearance: Young, often dusty, Caucasian children, some of Southern European descent. · clothing: Simple, practical, and light clothing suitable for hot desert conditions, often worn and soiled from play.
- `spanish_migrant_miners_wittenoom` — who: Spanish migrant men working as miners in Wittenoom · where_when: Working in the Wittenoom mines and mill from the late 1950s to mid-1960s · appearance: Young to middle-aged Caucasian men of Southern European descent, often covered in dust, with visible signs of hard labor. · clothing: Rugged work shirts, trousers, boots, hard hats, often stained with dust and grime from the mines and mill, typical of 1950s-1960s industrial workers.
- `asbestos_society_advocates` — who: Leaders and advocates of the Asbestos Diseases Society of Australia · where_when: Formed in 1979 to support victims and pursue legal action against companies responsible for asbestos exposure · appearance: Adult Caucasians, often professionals, conveying empathy and advocacy. · clothing: Contemporary professional or semi-formal attire of the late 20th to early 21st century.
- `australian_prime_ministers` — who: Australian Prime Ministers during the operational period of Wittenoom · where_when: Making statements about mine life and related policies in the mid-20th century, such as Chifley in 1947 · appearance: Middle-aged to older Caucasian men, formal and authoritative. · clothing: Formal suits, shirts, and ties, representing political leadership in 1940s-1960s Australia.
- `wittenoom_general_workers` — who: General laborers and mill workers of various nationalities in Wittenoom · where_when: Performing various tasks at the mine and mill throughout the operational period (1937-1966) · appearance: Adult men, often of diverse European descent, appearing physically worn from labor, covered in dust. · clothing: Durable work shirts, trousers, boots, and rudimentary safety gear, heavily soiled with mine dust and grime.
- `aba_management` — who: Management personnel of Australian Blue Asbestos (ABA) · where_when: Responsible for mine operations and safety during the 1940s-1950s · appearance: Middle-aged Caucasian men, in roles of authority, often in professional or semi-professional attire. · clothing: Business casual or semi-formal attire, such as collared shirts, trousers, and possibly jackets, suitable for a mine manager in mid-20th century Australia.
- `western_australian_officials_modern` — who: Western Australian state government ministers and officials in the 21st century · where_when: Commenting on remediation costs, pollution, and ongoing issues regarding Wittenoom in recent years · appearance: Middle-aged to older Australians, professional and politically astute. · clothing: Modern business suits and professional attire.

### Ejemplo: cap 7, foto 7 en S5 (el del handoff)
**Cap 7 · foto 7** · año 2023 (1) dicho en el ancla) · grupos banjima_elders_activists · 154 palabras

Ancla: «Es tierra Banjima. En dos mil veintitrés, Marcos Orellana visitó Australia y se sentó con Maitland Parker, un anciano Banjima.»

> An elderly Aboriginal Banjima man around 70, thin frame and hollowed cheeks from illness, seated on a camp chair beside a Latin American man in his fifties in a plain shirt. The a couple of men sit side by side on Banjima country, the elder speaking and gesturing toward the gorge. Elder looks out toward the red cliffs, the visitor turned toward him listening, notebook resting on his knee. A battered tin mug of tea set on the red ground between the chairs. Red earth clearing near Wittenoom Gorge, spinifex and a river gum, 2023. Grainy 35mm documentary photograph, 2023, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Low golden late-afternoon sun. Red earth, ochre cliffs, faded khaki and white shirts, dusty blue sky. Medium shot, eye-level, shallow depth of field, 50mm lens. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

### Diff del pedido del cap 6, etapa contra la anterior (system + user del 1.er intento)

#### S1 contra S0 (E de F47b) (2 líneas +, 12 líneas −)

```diff
--- pedido_E_ch06.txt
+++ pedido_S1_ch06.txt
@@ -103,2 +103,2 @@
-GEO     : (sin geo)
-ERA     : (sin era)
+GEO     : Wittenoom
+ERA     : 1943–2024
@@ -177,10 +176,0 @@
-
-UBICACIONES DOCUMENTADAS (no mezclar en una misma escena):
-- Esposa del minero Daniel Écija y residente de Wittenoom. → Madrid.
-- Hija de minero, directora y productora audiovisual. → Madrid.
-- Esposa del minero Ramón de Juan y residente de Wittenoom. → Madrid.
-- Minero español en Wittenoom. → Madrid.
-- Hija de Ramón de Juan, vivió en Wittenoom de niña. → Madrid.
-- Hijo de minero nacido en Wittenoom. → Madrid.
-- Organismo gubernamental → Wittenoom Gorge, Meekatharra.
-- Ningún menor en celdas de adultos en ninguna escena.
```

#### S2 contra S1 (16 líneas +, 0 líneas −)

```diff
--- pedido_S1_ch06.txt
+++ pedido_S2_ch06.txt
@@ -264,0 +265 @@
+      FACTS: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» | «En 1988, un juez determinó que la compañía minera CSR actuó con un 'continuo, consciente y contumaz' desprecio por la seguridad de sus trabajadores.» | «1979 · Los afectados por el amianto constituyeron la Asbestos Diseases Society of Australia.» | «La exposición al asbesto puede causar asbestosis, mesotelioma y cáncer de pulmón.»
@@ -269,0 +271 @@
+      FACTS: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» | «En 1988, un juez determinó que la compañía minera CSR actuó con un 'continuo, consciente y contumaz' desprecio por la seguridad de sus trabajadores.» | «1979 · Los afectados por el amianto constituyeron la Asbestos Diseases Society of Australia.» | «La exposición al asbesto puede causar asbestosis, mesotelioma y cáncer de pulmón.»
@@ -274,0 +277 @@
+      FACTS: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» | «En 1988, un juez determinó que la compañía minera CSR actuó con un 'continuo, consciente y contumaz' desprecio por la seguridad de sus trabajadores.» | «1979 · Los afectados por el amianto constituyeron la Asbestos Diseases Society of Australia.» | «La exposición al asbesto puede causar asbestosis, mesotelioma y cáncer de pulmón.»
@@ -279,0 +283 @@
+      FACTS: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» | «En 1988, un juez determinó que la compañía minera CSR actuó con un 'continuo, consciente y contumaz' desprecio por la seguridad de sus trabajadores.» | «1979 · Los afectados por el amianto constituyeron la Asbestos Diseases Society of Australia.» | «La exposición al asbesto puede causar asbestosis, mesotelioma y cáncer de pulmón.»
@@ -284,0 +289 @@
+      FACTS: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» | «En 1988, un juez determinó que la compañía minera CSR actuó con un 'continuo, consciente y contumaz' desprecio por la seguridad de sus trabajadores.» | «1979 · Los afectados por el amianto constituyeron la Asbestos Diseases Society of Australia.» | «La exposición al asbesto puede causar asbestosis, mesotelioma y cáncer de pulmón.»
@@ -289,0 +295 @@
+      FACTS: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» | «En 1988, un juez determinó que la compañía minera CSR actuó con un 'continuo, consciente y contumaz' desprecio por la seguridad de sus trabajadores.» | «1979 · Los afectados por el amianto constituyeron la Asbestos Diseases Society of Australia.» | «La exposición al asbesto puede causar asbestosis, mesotelioma y cáncer de pulmón.»
@@ -294,0 +301 @@
+      FACTS: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» | «En 1988, un juez determinó que la compañía minera CSR actuó con un 'continuo, consciente y contumaz' desprecio por la seguridad de sus trabajadores.» | «1979 · Los afectados por el amianto constituyeron la Asbestos Diseases Society of Australia.» | «La exposición al asbesto puede causar asbestosis, mesotelioma y cáncer de pulmón.»
@@ -299,0 +307 @@
+      FACTS: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» | «En 1988, un juez determinó que la compañía minera CSR actuó con un 'continuo, consciente y contumaz' desprecio por la seguridad de sus trabajadores.» | «1979 · Los afectados por el amianto constituyeron la Asbestos Diseases Society of Australia.» | «La exposición al asbesto puede causar asbestosis, mesotelioma y cáncer de pulmón.»
@@ -304,0 +313 @@
+      FACTS: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» | «En 1988, un juez determinó que la compañía minera CSR actuó con un 'continuo, consciente y contumaz' desprecio por la seguridad de sus trabajadores.» | «1979 · Los afectados por el amianto constituyeron la Asbestos Diseases Society of Australia.» | «La exposición al asbesto puede causar asbestosis, mesotelioma y cáncer de pulmón.»
@@ -309,0 +319 @@
+      FACTS: «En junio de 2007, el sitio del pueblo de Wittenoom fue oficialmente desclasificado y su nombre eliminado de los mapas y señales de tráfico oficiales.» | «Un Subcomité de Wittenoom determinó en 2023 que todos los informes sobre el alcance de la contaminación ya no son aplicables y que la contaminación se ha extendido.» | «La investigación parlamentaria de Australia Occidental de 1992 recomendó que los relaves en el sitio de la mina se limpiaran en un período de 5 a 10 años.» | «Documentos de 2016 indican que no se ha tomado ninguna medida para asegurar los relaves en Wittenoom Gorge debido al costo.»
@@ -314,0 +325 @@
+      FACTS: «En junio de 2007, el sitio del pueblo de Wittenoom fue oficialmente desclasificado y su nombre eliminado de los mapas y señales de tráfico oficiales.» | «Un Subcomité de Wittenoom determinó en 2023 que todos los informes sobre el alcance de la contaminación ya no son aplicables y que la contaminación se ha extendido.» | «La investigación parlamentaria de Australia Occidental de 1992 recomendó que los relaves en el sitio de la mina se limpiaran en un período de 5 a 10 años.» | «Documentos de 2016 indican que no se ha tomado ninguna medida para asegurar los relaves en Wittenoom Gorge debido al costo.»
@@ -319,0 +331 @@
+      FACTS: «En junio de 2007, el sitio del pueblo de Wittenoom fue oficialmente desclasificado y su nombre eliminado de los mapas y señales de tráfico oficiales.» | «Un Subcomité de Wittenoom determinó en 2023 que todos los informes sobre el alcance de la contaminación ya no son aplicables y que la contaminación se ha extendido.» | «La investigación parlamentaria de Australia Occidental de 1992 recomendó que los relaves en el sitio de la mina se limpiaran en un período de 5 a 10 años.» | «Documentos de 2016 indican que no se ha tomado ninguna medida para asegurar los relaves en Wittenoom Gorge debido al costo.»
@@ -324,0 +337 @@
+      FACTS: «En junio de 2007, el sitio del pueblo de Wittenoom fue oficialmente desclasificado y su nombre eliminado de los mapas y señales de tráfico oficiales.» | «Un Subcomité de Wittenoom determinó en 2023 que todos los informes sobre el alcance de la contaminación ya no son aplicables y que la contaminación se ha extendido.» | «La investigación parlamentaria de Australia Occidental de 1992 recomendó que los relaves en el sitio de la mina se limpiaran en un período de 5 a 10 años.» | «Documentos de 2016 indican que no se ha tomado ninguna medida para asegurar los relaves en Wittenoom Gorge debido al costo.»
@@ -329,0 +343 @@
+      FACTS: «En junio de 2007, el sitio del pueblo de Wittenoom fue oficialmente desclasificado y su nombre eliminado de los mapas y señales de tráfico oficiales.» | «Un Subcomité de Wittenoom determinó en 2023 que todos los informes sobre el alcance de la contaminación ya no son aplicables y que la contaminación se ha extendido.» | «La investigación parlamentaria de Australia Occidental de 1992 recomendó que los relaves en el sitio de la mina se limpiaran en un período de 5 a 10 años.» | «Documentos de 2016 indican que no se ha tomado ninguna medida para asegurar los relaves en Wittenoom Gorge debido al costo.»
@@ -334,0 +349 @@
+      FACTS: «En junio de 2007, el sitio del pueblo de Wittenoom fue oficialmente desclasificado y su nombre eliminado de los mapas y señales de tráfico oficiales.» | «Un Subcomité de Wittenoom determinó en 2023 que todos los informes sobre el alcance de la contaminación ya no son aplicables y que la contaminación se ha extendido.» | «La investigación parlamentaria de Australia Occidental de 1992 recomendó que los relaves en el sitio de la mina se limpiaran en un período de 5 a 10 años.» | «Documentos de 2016 indican que no se ha tomado ninguna medida para asegurar los relaves en Wittenoom Gorge debido al costo.»
@@ -339,0 +355 @@
+      FACTS: «En junio de 2007, el sitio del pueblo de Wittenoom fue oficialmente desclasificado y su nombre eliminado de los mapas y señales de tráfico oficiales.» | «Un Subcomité de Wittenoom determinó en 2023 que todos los informes sobre el alcance de la contaminación ya no son aplicables y que la contaminación se ha extendido.» | «La investigación parlamentaria de Australia Occidental de 1992 recomendó que los relaves en el sitio de la mina se limpiaran en un período de 5 a 10 años.» | «Documentos de 2016 indican que no se ha tomado ninguna medida para asegurar los relaves en Wittenoom Gorge debido al costo.»
```

#### S3 contra S2 (16 líneas +, 16 líneas −)

```diff
--- pedido_S2_ch06.txt
+++ pedido_S3_ch06.txt
@@ -267 +267 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): -
@@ -273 +273 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): -
@@ -279 +279 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): -
@@ -285 +285 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): Hija de Ramón de Juan, vivió en Wittenoom de niña · Wittenoom · 1962, 1963, 1964
@@ -291 +291 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): -
@@ -297 +297 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): -
@@ -303 +303 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): -
@@ -309 +309 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): CEO de la Asbestos Deseases Society of Australia · - · -
@@ -315 +315 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): -
@@ -321 +321 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): -
@@ -327 +327 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): -
@@ -333 +333 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): -
@@ -339 +339 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): Presidente de comité parlamentario · - · 1994
@@ -345 +345 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): Líder de investigación parlamentaria · - · 1992
@@ -351 +351 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): -
@@ -357 +357 @@
-      PEOPLE (roles): -
+      PEOPLE (role · where · years): -
```

#### S4 contra S3 (21 líneas +, 20 líneas −)

```diff
--- pedido_S3_ch06.txt
+++ pedido_S4_ch06.txt
@@ -22,0 +23 @@
+- year: the year (YYYY) in which THIS image's scene takes place, read from the narration fragment, its paragraph and the case file (a year said earlier in the paragraph, «ten years before» a stated year, «now» = the most recent year in the case file). Routing only — not rendered as text.
@@ -268 +269 @@
-  [2] YEAR: 1989 · WHERE: Australia
+  [2] YEAR: - · WHERE: Australia
@@ -280 +281 @@
-  [4] YEAR: 1988 · WHERE: Australia
+  [4] YEAR: - · WHERE: Australia
@@ -286,13 +287,13 @@
-  [5] YEAR: 1988 · WHERE: Australia
-      PARAGRAPH: «En mil novecientos ochenta y nueve ya habían muerto más de quinientos antiguos trabajadores y residentes de Wittenoom. Los que seguían vivos se habían juntado diez años antes en la Asbestos Diseases Society of Australia. En mil novecientos ochenta y ocho un juez leyó su veredicto: la compañía había mostrado un desprecio continuo, consciente y contumaz por la seguridad y la salud de sus trabajadores. Mercedes de Juan, que se quedó en Australia, entra en un escáner y después sopla en un tubo. «Nos hacen un escáner y una prueba de función pulmonar», dice Mercedes. Las fibras pueden causar mesotelioma, asbestosis y cáncer de pulmón.»
-      SCENES: -
-      FACTS: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» | «En 1988, un juez determinó que la compañía minera CSR actuó con un 'continuo, consciente y contumaz' desprecio por la seguridad de sus trabajadores.» | «1979 · Los afectados por el amianto constituyeron la Asbestos Diseases Society of Australia.» | «La exposición al asbesto puede causar asbestosis, mesotelioma y cáncer de pulmón.»
-      QUOTES: «Nos hacen un escáner y una prueba de función pulmonar.» | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.»
-      PEOPLE (role · where · years): -
-  [6] YEAR: 1988 · WHERE: Australia
-      PARAGRAPH: «En mil novecientos ochenta y nueve ya habían muerto más de quinientos antiguos trabajadores y residentes de Wittenoom. Los que seguían vivos se habían juntado diez años antes en la Asbestos Diseases Society of Australia. En mil novecientos ochenta y ocho un juez leyó su veredicto: la compañía había mostrado un desprecio continuo, consciente y contumaz por la seguridad y la salud de sus trabajadores. Mercedes de Juan, que se quedó en Australia, entra en un escáner y después sopla en un tubo. «Nos hacen un escáner y una prueba de función pulmonar», dice Mercedes. Las fibras pueden causar mesotelioma, asbestosis y cáncer de pulmón.»
-      SCENES: -
-      FACTS: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» | «En 1988, un juez determinó que la compañía minera CSR actuó con un 'continuo, consciente y contumaz' desprecio por la seguridad de sus trabajadores.» | «1979 · Los afectados por el amianto constituyeron la Asbestos Diseases Society of Australia.» | «La exposición al asbesto puede causar asbestosis, mesotelioma y cáncer de pulmón.»
-      QUOTES: «Nos hacen un escáner y una prueba de función pulmonar.» | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.»
-      PEOPLE (role · where · years): -
-  [7] YEAR: 1988 · WHERE: Australia
+  [5] YEAR: - · WHERE: Australia
+      PARAGRAPH: «En mil novecientos ochenta y nueve ya habían muerto más de quinientos antiguos trabajadores y residentes de Wittenoom. Los que seguían vivos se habían juntado diez años antes en la Asbestos Diseases Society of Australia. En mil novecientos ochenta y ocho un juez leyó su veredicto: la compañía había mostrado un desprecio continuo, consciente y contumaz por la seguridad y la salud de sus trabajadores. Mercedes de Juan, que se quedó en Australia, entra en un escáner y después sopla en un tubo. «Nos hacen un escáner y una prueba de función pulmonar», dice Mercedes. Las fibras pueden causar mesotelioma, asbestosis y cáncer de pulmón.»
+      SCENES: -
+      FACTS: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» | «En 1988, un juez determinó que la compañía minera CSR actuó con un 'continuo, consciente y contumaz' desprecio por la seguridad de sus trabajadores.» | «1979 · Los afectados por el amianto constituyeron la Asbestos Diseases Society of Australia.» | «La exposición al asbesto puede causar asbestosis, mesotelioma y cáncer de pulmón.»
+      QUOTES: «Nos hacen un escáner y una prueba de función pulmonar.» | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.»
+      PEOPLE (role · where · years): -
+  [6] YEAR: - · WHERE: Australia
+      PARAGRAPH: «En mil novecientos ochenta y nueve ya habían muerto más de quinientos antiguos trabajadores y residentes de Wittenoom. Los que seguían vivos se habían juntado diez años antes en la Asbestos Diseases Society of Australia. En mil novecientos ochenta y ocho un juez leyó su veredicto: la compañía había mostrado un desprecio continuo, consciente y contumaz por la seguridad y la salud de sus trabajadores. Mercedes de Juan, que se quedó en Australia, entra en un escáner y después sopla en un tubo. «Nos hacen un escáner y una prueba de función pulmonar», dice Mercedes. Las fibras pueden causar mesotelioma, asbestosis y cáncer de pulmón.»
+      SCENES: -
+      FACTS: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» | «En 1988, un juez determinó que la compañía minera CSR actuó con un 'continuo, consciente y contumaz' desprecio por la seguridad de sus trabajadores.» | «1979 · Los afectados por el amianto constituyeron la Asbestos Diseases Society of Australia.» | «La exposición al asbesto puede causar asbestosis, mesotelioma y cáncer de pulmón.»
+      QUOTES: «Nos hacen un escáner y una prueba de función pulmonar.» | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.»
+      PEOPLE (role · where · years): -
+  [7] YEAR: - · WHERE: Australia
@@ -304 +305 @@
-  [8] YEAR: 1988 · WHERE: Australia
+  [8] YEAR: - · WHERE: Australia
@@ -310 +311 @@
-  [9] YEAR: 1988 · WHERE: Australia
+  [9] YEAR: - · WHERE: Australia
@@ -322 +323 @@
-  [11] YEAR: 2007 · WHERE: -
+  [11] YEAR: - · WHERE: -
@@ -334 +335 @@
-  [13] YEAR: 1992 · WHERE: -
+  [13] YEAR: - · WHERE: -
@@ -340 +341 @@
-  [14] YEAR: 1992 · WHERE: -
+  [14] YEAR: - · WHERE: -
```

#### S5 contra S4 (15 líneas +, 5 líneas −)

```diff
--- pedido_S4_ch06.txt
+++ pedido_S5_ch06.txt
@@ -360,5 +360,15 @@
-  - mining_workers: Workers employed in the crocidolite asbestos mines and mill, including both local and migrant laborers. · Wittenoom mines and mill, predominantly 1937-1966, but especially in the 1950s-1960s.
-  - european_migrant_families: Families from European countries, particularly Spain, recruited to work and live in Wittenoom. · Arriving in Wittenoom, living in the town from the late 1940s through the mid-1960s.
-  - wittenoom_children: Children born or raised in Wittenoom, exposed to asbestos through play and daily life. · Playing in the town's patios, roads, and public spaces, 1950s-1960s.
-  - officials_regulators: Mine inspectors, state engineers, company representatives (e.g., CSR), and government officials. · Visiting the mine and town in various capacities from the 1940s to the 1960s.
-  - asbestos_advocates_victims: Former workers and residents suffering from asbestos-related diseases, and their legal/health advocates. · From the 1970s onwards, in Australia and elsewhere, involved in lawsuits and advocacy.
+  - mine_regulatory_officials: Australian government mine inspectors and deputy state mining engineers · Reporting on dust problems in Wittenoom from 1944 onwards
+  - early_mine_operators: Early prospectors and mine operators, co-owners of the mining interests (e.g., Hancock and Wright) · Operating the crocidolite industry in Wittenoom Gorge from 1937 to 1943
+  - public_health_professionals: Australian public health doctors, commissioners, and industrial hygienists investigating asbestos-related diseases and conditions · Reporting on dust levels, diagnosing illnesses, and assessing workplace safety in Wittenoom from the 1940s to 1960s
+  - csr_executives: Executives and chairmen of CSR, the company operating the Wittenoom mine · Managing mining operations, making decisions regarding safety, and announcing closure from the 1940s to 1960s
+  - parliamentary_inquiry_members: Australian politicians leading parliamentary inquiries into the Wittenoom disaster · Recommending clean-up programs and remediation actions in the early 1990s and beyond
+  - banjima_elders_activists: Banjima Indigenous elders and activists affected by the Wittenoom contamination · Advocating for remediation and justice in Wittenoom from 2023 onwards
+  - bntac_representatives: Representatives of the Banjima Native Title Aboriginal Corporation (BNTAC) · Pursuing legal action against the State of Western Australia in 2026
+  - spanish_migrant_wives_wittenoom: Spanish migrant women, wives of miners, residing in Wittenoom · Living in Wittenoom from the early to mid-1960s, managing family life in harsh conditions
+  - wittenoom_child_residents: Children of miners and other residents growing up in Wittenoom's dusty and asbestos-laden environment · Playing in the town's streets, patios, and schools from the 1940s to the 1960s
+  - spanish_migrant_miners_wittenoom: Spanish migrant men working as miners in Wittenoom · Working in the Wittenoom mines and mill from the late 1950s to mid-1960s
+  - asbestos_society_advocates: Leaders and advocates of the Asbestos Diseases Society of Australia · Formed in 1979 to support victims and pursue legal action against companies responsible for asbestos exposure
+  - australian_prime_ministers: Australian Prime Ministers during the operational period of Wittenoom · Making statements about mine life and related policies in the mid-20th century, such as Chifley in 1947
+  - wittenoom_general_workers: General laborers and mill workers of various nationalities in Wittenoom · Performing various tasks at the mine and mill throughout the operational period (1937-1966)
+  - aba_management: Management personnel of Australian Blue Asbestos (ABA) · Responsible for mine operations and safety during the 1940s-1950s
+  - western_australian_officials_modern: Western Australian state government ministers and officials in the 21st century · Commenting on remediation costs, pollution, and ongoing issues regarding Wittenoom in recent years
```

### Costos, tokens y tiempo por etapa y cap (`cost_history` f48-lab; S0 = E de f47b-lab)

| etapa | cap | estado | intentos | segundos | tokens in / out | US$ |
|---|---|---|---|---|---|---:|
| S0 | 2 | ok | 1 | 81.1 | 27354 / 8358 | 0.2766 |
| S0 | 5 | ok | 1 | 102.7 | 23807 / 10640 | 0.3080 |
| S0 | 6 | ok | 1 | 111.4 | 22743 / 11043 | 0.3118 |
| S0 | 7 | ok | 1 | 77.4 | 20039 / 7811 | 0.2364 |
| S1 | 2 | ok | 1 | 77.3 | 27096 / 8299 | 0.2744 |
| S1 | 5 | ok | 1 | 93.4 | 23549 / 9799 | 0.2902 |
| S1 | 6 | ok | 1 | 94.3 | 22485 / 9756 | 0.2851 |
| S1 | 7 | ok | 1 | 63.6 | 19781 / 6466 | 0.2084 |
| S2 | 2 | ok | 1 | 76.8 | 29842 / 8057 | 0.2805 |
| S2 | 5 | ok | 1 | 96.1 | 26641 / 9961 | 0.3058 |
| S2 | 6 | ok | 1 | 86.5 | 26097 / 9081 | 0.2860 |
| S2 | 7 | ok | 1 | 78.2 | 23275 / 7908 | 0.2513 |
| S3 | 2 | ok | 1 | 87.8 | 30047 / 9199 | 0.3042 |
| S3 | 5 | ok | 1 | 102.1 | 26746 / 10666 | 0.3203 |
| S3 | 6 | ok | 1 | 95.3 | 26247 / 9770 | 0.3004 |
| S3 | 7 | ok | 1 | 75.5 | 23383 / 7831 | 0.2502 |
| S4 | 2 | ok | 1 | 88.6 | 30121 / 8744 | 0.2954 |
| S4 | 5 | ok | 1 | 138.0 | 26835 / 13155 | 0.3704 |
| S4 | 6 | ok | 1 | 113.3 | 26333 / 11152 | 0.3284 |
| S4 | 7 | ok | 1 | 67.1 | 23472 / 6217 | 0.2182 |
| S5 | 2 | ok | 1 | 90.9 | 30805 / 9556 | 0.3143 |
| S5 | 5 | ok | 1 | 103.2 | 27519 / 10438 | 0.3188 |
| S5 | 6 | ok | 1 | 91.4 | 27017 / 9521 | 0.2985 |
| S5 | 7 | ok | 1 | 60.9 | 24156 / 6319 | 0.2230 |

| etapa | US$ (4 caps) |
|---|---:|
| S0 | 1.1328 |
| S1 | 1.0580 |
| S2 | 1.1236 |
| S3 | 1.1750 |
| S4 | 1.2124 |
| S5 | 1.1547 |

Otras llamadas de F48 (canon S5): Gemini 2.5 Flash · call_flash_json · US$ 0.0351

**Total F48 (`f48-lab`)**: US$ 5.7588 (tope 7.00)

## Lo que se ve (hechos medidos, sin elegir nada)
- **S1 (GEO/ERA y sin ubicaciones):**
  - lugar del DÓNDE en la prosa: 29 → 33;
  - gente sin grupo: 1 → 0;
  - palabras: 134 → 131.
  - El pedido ya no manda a la gente «→ Madrid» ni dice «Ningún menor en celdas de adultos».
- **S2 (FACTS):** el chequeo 9 (año del setting ≠ año de la foto) baja de 3 a 0, y el 11 (choca) también, de 3 a 0. El lugar queda en 31.
- **S3 (PEOPLE):**
  - el lugar baja a 25;
  - las fotos con persona del pool con origen conocido dicen el origen en la prosa en todas las etapas (3/3: «Minero español» y los dos Banjima);
  - el rol nuevo no movió el `people_group` de los Parker.
- **S4 (año):**
  - el año ya no sale dos veces en «setting, año» (33–40 → 0);
  - el modelo llena `year` en las 60 fotos y ninguna cae al respaldo;
  - el chequeo 11 da 1 choque (cap 5) en S4 y 0 en S5;
  - la gente sin grupo sube a 3.
- **S5 (canon con los personajes):**
  - **15 `people_groups`** en vez de 5, entre ellos `banjima_elders_activists` y `bntac_representatives`, con `appearance` «Elderly Indigenous Australians» y «Adult Indigenous Australians»;
  - las fotos 7 y 8 del cap 7 pasan de `asbestos_advocates_victims` a **`banjima_elders_activists`**;
  - el lugar sube a 32;
  - la gente sin grupo sube a 5 (cap 5: 3, cap 6: 2);
  - aparece 1 negación en el setting (cap 7).
- **Nombres reales de personas en la prosa:** 0 en las 6 columnas.
- **Costo por etapa (4 caps):** entre US$ 1,06 y 1,21. Los tokens de entrada suben con cada etapa: cap 2 de 27,1 k en S1 a 30,8 k en S5.

## Verificación (paso 8 de /tanda)
- **Commit de S1 (`0ec8e7b`):**
  - rápida: 55 verdes;
  - amplia: 921 verdes + 4 fallas previas (`m03_merge_timing` ×2, `gfx_lab` ×2);
  - `mapa --check` 0;
  - el hook `suite_rapida` corrió en el commit.
- **Commit final:** las suites se volvieron a correr (`verif/`); el resultado va en la adenda del veredicto.
- **Candado de ch02 (`fase2b … --only-cap ch02`): no corrido**, porque escribe en `output/`.
  - El cambio de S1 toca el pedido de los casilleros de m03 (Fase 1.5), no el render. El candado re-usa los visuales (`--reuse-visuals`), así que no pasa por m03.
- **No se corrió** `pytest --collect-only` ni `pytest test_*.py` en bloque: solo archivos `test_module_*` nombrados, con proxy muerto.
- **Archivos tocados:**
  - producción: solo `script_engine/m03_visual.py`;
  - tests: `test_module_f5b.py`, `test_module_f5d.py` y el nuevo `test_module_f48.py`;
  - mapa: `lab/mapa/stickers/fase2a.json` y `lab/MAPA_PROYECTO.md/.json`;
  - en `data/`, solo `cost_history.json`; nada en `output/` ni `topics_db`.

## Lo que queda abierto (entero)
- l1. **Pasar S2–S5 a producción:** no se hace en esta tanda; van con C2. Lo deciden Omar y el analista con estas tablas.
- l2. **S5 toma del canon regenerado solo los `people_groups`.** Lo leí de «el canon de F46b sigue de base».
  - Si la intención era usar el canon regenerado entero (época, ropa, anacronismos), habría que repetir S5.
  - El canon regenerado entero está en `canon_S5_regenerado.json`.
- l3. **S5 sube la gente sin grupo a 5**, contra 0–3 en S1–S4: hay más grupos y Opus no ubica a todos.
- l4. **S3 baja el lugar en la prosa** (31 → 25) y S4–S5 lo recuperan (28 y 32). Es una corrida por etapa; diferencias de 2–4 fotos pueden ser azar.
- l5. **Chequeo 12 (origen dicho):** solo 3 de las 11 fotos con persona del pool tienen un rol con origen («Minero español», «Anciano Banjima», «dueño tradicional Banjima»). Las demás («Esposa del minero…», «Hija de minero…») no dicen origen.
  - La heurística `ORIGEN` (español → Spanish, banjima → Banjima, aborigen → Aboriginal/Indigenous) está en el código.
- l6. **F8 deja una frase mal armada en S5** (cap 7 foto 7): «The a couple of men sit side by side…». `fix_counts_lr` de producción cambia «two men» por «a couple of men» después de «The». Es de producción (F8), no de esta tanda.
- l7. **Marcos Orellana** (relator de la ONU) no está en los `personajes` del pool. En la foto 7 del cap 7, Opus lo describe como «a Latin American man in his fifties».
- l8. **El año de S4 en las fotos 4–8 del cap 6** («ahora» → 2023) y 15–16 del cap 5 («décadas más tarde» → 2023/2024) es la lectura del modelo. Con el texto S4 corresponde, pero lo mira el analista.
- l9. **El canon sigue siendo de una sola época** (`spans` 1937-2007; 14 de 60 fotos fuera). Quedó fuera de esta tanda por decisión del handoff, con el estilo por época.
- l10. **Fuera de esta tanda (lista del handoff):**
  - imagen sensorial repetida por beat;
  - `hora` vacía en la cronología;
  - escenas de la ficha sin cruce en los beats 4, 8, 11 y 12;
  - idioma del cartel por foto;
  - clip Veo.
- l11. **Candado de ch02 no corrido** (escribe en `output/`). El cambio de producción no pasa por el render con `--reuse-visuals`, pero no está medido.
- l12. **`gfx_lab`** (2–3 fallas según la corrida): las mismas de F47 y F47b; no vienen de esta tanda.
- l13. **El form de Omar** no se tocó. La próxima vez que corra m03 en un topic nuevo, el pedido ya lleva GEO/ERA y no lleva el bloque de ubicaciones: es el único cambio de producción.

## Procesos y subagentes
- Shells en segundo plano: la corrida (`b5vjuiyeb`) y las suites (`blm652ckd`), terminadas.
- Subagente: el revisor-handoff, terminado.
- No quedó ningún proceso de la tanda vivo; no se cerró nada de Omar.

## Veredicto de revisor-handoff (íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | md5 del handoff | OK | `md5sum` da 9aabfd5b4ff2e8cc201b4426728d617f. |
| 2 | Paso 0: línea de DECISIONES tal cual y commit con el handoff | OK | `DECISIONES.md:133` coincide con el handoff. El commit 220d32e trae DECISIONES y el handoff. |
| 3 | S1: GEO = `lugar_principal` del perfil; ERA = primer–último año dicho en la narración | OK | `_geo_era` en `m03_visual.py`, llamada desde `assign_visual_prompts`. Da `Wittenoom` / `1943–2024`, y el pedido S1 del cap 6 lo muestra (`diff` contra E). |
| 4 | S1: se borran `_format_documented_locations`, `_documented_places`, `_LOC_GROUPS`, `_LOC_DEST`, su uso y sus tests de f5b/f5d | OK | `git show 0ec8e7b`: −24 líneas en f5b y −10 en f5d. Un `grep` en `*.py` fuera de lab y los `_*.py` de la raíz solo encuentra los nombres dentro del assert de `test_module_f48.py`. |
| 5 | Test nuevo de GEO/ERA con Wittenoom; suite rápida verde; commit | OK | `test_module_f48.py` tiene 4 tests. `verif_s1/suite_rapida.log`: 55 passed, 3 skipped. La amplia dio 921 passed y 4 failed. Esas 4 las declara como previas (`m03_merge_timing` ×2 y `gfx_lab` ×2); no las pude reproducir porque no corro pytest. |
| 6 | Etapas S1→S5 acumuladas, cada una = anterior + un cambio | OK | Diffs del cap 6 que corrí yo, `pedido_Sn` contra `pedido_Sn-1`. S1: solo GEO/ERA y el bloque borrado. S2: solo líneas `FACTS`. S3: solo el encabezado `PEOPLE` y su contenido. S4: la línea `year` en el SI y las líneas YEAR en `-` (con el año ancla donde lo hay). S5: solo el bloque `PEOPLE GROUPS`. |
| 7 | Modelo `claude-opus-5-5`, effort high, caps 2, 5, 6, 7, 4 llamadas en paralelo por etapa, freno antes de cada una | OK | `f48_corridas.py:43-46` y `ThreadPoolExecutor(max_workers=4)` por etapa. `corrida.log` sin PARADA ni Traceback. Hay 20 `slots_S*` y 20 `pedidos`. Que los 20 hayan salido ok al 1.er intento y el freno de `f47.una_variante` los tomo del reporte y del código importado, sin reproducirlos. |
| 8 | Textos nuevos para los LLM, tal cual y sin otros | OK | `TEXTO_S4_YEAR` y `TEXTO_S5` coinciden con el handoff carácter por carácter. Los encabezados `FACTS: «…» \| «…»` y `PEOPLE (role · where · years)` también. Única normalización no listada: `.rstrip('.')` al rol en PEOPLE y en la lista de S5. El esquema `year` es un STRING sin descripción. |
| 9 | Costos en `cost_tracker` con `f48-lab`, tope 7,00, cero fotos, cero fal | OK | `cost_history.json`: un solo registro `f48-lab` con 21 entradas (20 Opus y 1 Flash), `total_cost` 5,758806, igual al reporte (5,7588). Tope 7,00 en `TOPE_TANDA.json`. |
| 10 | `PROMPTS_F48.md`: tablas S0\|S1…S5 con totales por cap, diff del cap 6, prompts enteros de S5, crudos, `canon_S5.json`, costos | OK | `PROMPTS_F48.md` pesa 147 KB y trae tablas por cap, totales, chequeos 11–13, diffs y costos. `canon_S5.json` (15 grupos) y `canon_S5_regenerado.json` existen. Chascada del chequeo 5 aplicada (`_sale_entero`). |
| 11 | Números del reporte contra los archivos | PARCIAL | Coinciden: tabla de año por etapa (18/41/1; 18/42; «dos veces» 40/31/34/0/0; `year` 60/60), los 20 años cambiados S3→S4 y el chequeo 13 (foto 7 y 8 pasan a `banjima_elders_activists`). Falla uno: el reporte dice que S5 difiere de S4 en 4 fotos y son 5. Falta cap 5 foto 14 (1992→1991). |
| 12 | `F48_REPORT.md` con «lo que queda abierto» entero | OK | Líneas 554-575, l1–l13. |
| 13 | Veredicto íntegro de revisor-handoff en el reporte | NO VERIFICABLE | Línea 583 todavía tiene el marcador `{{VEREDICTO}}`. Es este paso. |
| 14 | `lab/ESTADO_SESION.md` actualizado y commit del lab | PARCIAL | `ESTADO_SESION.md` figura modificado. Lo del lab sigue sin commitear; es lo esperado hasta este veredicto. |

**Decisión l2.** S5 usa el canon de F46b y reemplaza solo los `people_groups` por los regenerados. Es defendible con el texto del handoff («el canon de F46b sigue de base», una variable por etapa), y queda declarada (l2) con el canon regenerado entero en `canon_S5_regenerado.json`. El handoff también dice «Canon regenerado» sin precisar el alcance, así que Omar debería confirmarla. Si quería el canon entero regenerado, S5 se repite.

**Observaciones**
- Corregir «4 fotos» por 5 en la comparación S5 contra S4 (hay un solo error de conteo; el resto de las cifras que comprobé coincide).
- El reporte declara el candado `fase2b --only-cap ch02` como no corrido (l11). No hay evidencia de que S1 no afecte el render.
- El costo del Flash del canon fue US$ 0,0351, contra los ~0,01 que estimaba el handoff. Sigue lejos del tope.

**Fuera de alcance:** ninguno de tanda.
- `diag_234_cap4.py`, `lab/TOPE_TANDA.json` y `lab/hyperframes/f28/a/f28a.log` ya venían modificados.
- `lab/mapa/stickers/fase2a.json` y `lab/MAPA_PROYECTO.*`, en 0ec8e7b, son consecuencia de cambiar `m03_visual.py` (el reporte dice que `mapa --check` da 0).
- `data/` solo registra `cost_history`. No hay cambios en `output/` ni en `topics_db`.

**Riesgos que el contrato no cubre**
- Es una sola corrida por etapa. El reporte reconoce que diferencias de 2–4 fotos pueden ser azar (l4), así que las comparaciones entre etapas son indicios.
- S5 sube la gente sin grupo a 5 y trae una negación en el setting. La frase mal armada «The a couple of men…» viene de F8 de producción (l6).
- `_geo_era` lee `_perfil.json` de `_steps/`. Un tema sin perfil o sin años en la narración vuelve al respaldo «(sin geo)/(sin era)»; ese caso está testeado pero no hay medición en un tema nuevo.

### Adenda de CC (después del veredicto)
- **#11:** corregido. S5 difiere de S4 en **5** fotos: cap 2 foto 6 (1963 → 1962), cap 5 foto 7 (1966 → 1967), **cap 5 foto 14 (1992 → 1991)** y cap 5 fotos 15–16 (2023 → 2024). Ya está en el reporte.
- **#13 / #14:** el veredicto está pegado y el commit del lab va con este reporte. Las suites del commit final (`verif/`) dan rápida 55 verdes, amplia 921 verdes + 4 previas (`m03_merge_timing` ×2 y `gfx_lab` ×2), y `mapa --check` 0.
- **Candado de ch02 (l11):**
  - sigue sin correrse, porque escribe en `output/`;
  - `_geo_era` solo se llama dentro de `assign_visual_prompts` (m03, Fase 1.5), que `fase2b --reuse-visuals` no ejecuta, y `_format_seedream_canon_block` también es de m03;
  - es un argumento de código, no una medición: queda abierto.
- **l2:** queda para que Omar o el analista confirmen. Si se quería el canon entero regenerado, S5 se repite (≈ US$ 1,2).
- **`.rstrip('.')` en el rol:** saca el punto final de algunos roles del pool («…residente de Wittenoom.»), para que el separador « · » no quede después de un punto. Es formato del dato, no texto nuevo.

