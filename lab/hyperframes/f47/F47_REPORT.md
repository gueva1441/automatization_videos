# F47 — ¿Sirve C2 para cualquier historia? Medido solo en texto + D (Claude Fable llenando los casilleros) — REPORTE

CC · 2026-10-28 · rama `f11-guion-v4` · handoff `lab/hyperframes/f47/HANDOFF_F47_c2_en_texto.md` (md5 `a9f039e25b84ee5bb9e014485fe1b5ab` ✓). Paso 0 → parte única, sin parada entre ellas (lo pidió Omar). Tope US$ 6,00; **gasto real US$ 3,6833**, leído de `cost_history` (`f47-lab`). **Cero fotos, cero llamadas a fal. PARADA:** no se elige variante ni se toca producción.

## Lecturas declaradas
- `CLAUDE.md`, `DECISIONES.md` (cola, hasta 2026-10-28 02:24), `lab/ESTADO_SESION.md` (cabecera, F46b y F46), el handoff entero.
- Lo que manda leer la sesión que me arrancó: `lab/hyperframes/f46/f46b/f46b_corridas.py` entero, `lab/hyperframes/f46/f46b/F46b_REPORT.md` (abierto i1–i14) y `lab/hyperframes/f46/f46_corridas.py` (lo importa f46b).
- Código de producción leído (no editado): `claude_helpers.py` (`call_json`, `PRICES`, reintentos, `refusal`), `m03_visual._call_with_validation_retry` y `_seedream_slots_schema`, `gemini_helpers.call_pro_json` y `_try_json_parse`, `guion_v4.ESFUERZO`.
- La referencia de structured outputs del skill `claude-api`: soporta `enum`, `required` y `additionalProperties: false`. Que la raíz pueda ser un array no está documentado; la llamada pasó.

## Módulos (paso 2 de /tanda)
- **Producción: ninguno se edita.** Se importan `m03_visual`, `m03_imagenes_v3`, `name_matching`, `engine_profiles`, `fase1_5` (lectura), `claude_helpers`, `guion_v4` (solo la constante `ESFUERZO`) y `cost_tracker`. Como no se tocó ningún archivo de producción, `MAPA_PROYECTO` no cambia.
- **Lab nuevo:** `lab/hyperframes/f47/f47_corridas.py`. Hoy: no existía. Después de la tanda: mide C2 y D en texto. Importa `f46b_corridas` (`anios`, `expedientes`, `slots`, `armar`, `f8`) y `f46_corridas` (`STEPS`, `CANON_KEYS`, `_w`, `_j`), sin copiarlos. El mapa no incluye lab, así que no hay sticker que agregar.
- **Una variable por etapa:** C2 contra D cambia solo el modelo que llena los casilleros. El cap 2 de C2 es el `C2.json` de F46b, que ya tiene fotos.
- **Constantes nuevas, con origen en su línea:**
  - `TOPE_USD` 6,00 (Omar);
  - `CAPS_C2` (5, 6, 7) y `CAPS_D` (2, 5, 6, 7) (handoff §Constantes);
  - `MODELO_D` `claude-fable-5-1` (handoff §Constantes);
  - el effort se lee de `guion_v4.ESFUERZO["claude-fable-5-1"]` = `high` (existente).
- **Simulador (paso 5): no aplica.** El handoff no trae regla ni filtro de contenido: mide.

## Qué se corrió (parte única)
`python lab/hyperframes/f47/f47_corridas.py prompts` (03:05:55 → 03:09:52, `corrida.log`).

1. **Expedientes de los caps 2, 5, 6, 7 → `expedientes_F47.md`.**
   - Salen de `f46b.anios` y `f46b.expedientes`, con el cap como parámetro (`f46b.CAP` se fija en secuencia, antes del paralelo) y el canon `f46b/canon_C.json` sin regenerar.
   - `cargar(cap)` es el `f46.cargar` con el cap como parámetro. En el cap 7 (Veo) toma los 12 `supplemental_image_prompts`.
2. **Llamadas:**
   - 7 en paralelo (`ThreadPoolExecutor`, 7 workers): C2 = Pro en los caps 5, 6, 7; D = Fable en los caps 2, 5, 6, 7.
   - Las 7 pasan por **la misma** `f46b.slots`, es decir el mismo SI v3 + `people_group`, el mismo user-prompt con beats + expediente, el mismo esquema y el mismo `validar`.
   - Dentro del proceso, `m03_visual.call_pro_json` se reemplaza por un ruteador por hilo: C2 va al `call_pro_json` original; D va a `claude_helpers.call_json(model="claude-fable-5-1", effort="high")`.
   - Freno antes de cada llamada; gasto en `cost_tracker` con `start_video("f47-lab")` / `end_video()`.
   - **Un ajuste de transporte, no de texto:** si Fable devuelve un array en la raíz, se envuelve en `{"image_prompts": …}`. Es lo mismo que hace `gemini_helpers._try_json_parse` para Pro (línea 100).
   - `f46b.slots` escribe su `prompt_slots_pro.txt` en `f46b.LAB`. Para no pisar el de F46b, `f46b.LAB` apunta a una carpeta temporal del sistema.
3. **Pedidos idénticos, verificado:**
   - el md5 de system, user y esquema de C2 y de D coincide en cada cap (tabla de abajo);
   - el pedido de D en el cap 2 (`pedidos/pedido_D_ch02.txt`) es **byte-idéntico** al `prompt_slots_pro.txt` de F46b (`cmp`, md5 `36ba2962…`).
   - **Ningún texto nuevo para los LLM.**
4. **Armado por código + F8:** `f46b.armar(..., con_aspecto=False)` + `f46b.f8`, igual que C2 de F46b.
5. **Salidas:**
   - `PROMPTS_F47.md` (por cap y foto: ancla, año y fuente, DÓNDE, grupos C2 | D, los dos prompts enteros y palabras; después la tabla de los 8 chequeos con totales por cap, grupos y setting por foto, y el `video_prompt` del cap 7 entero);
   - `PROMPTS_F47.json`;
   - crudos `slots_C2_ch05–07.json` y `slots_D_ch02/05–07.json` (respuesta cruda de cada intento, segundos, md5 del pedido, casilleros finales);
   - `pedidos/` (system + user del 1.er intento de cada llamada);
   - `COSTOS.md`.
6. **Prueba en seco antes de gastar:** `f47_corridas.py seco <dir>` (sin API, con proxy muerto y casilleros falsos sacados de 03_visual). Sirvió para verificar el armado, las tablas y la igualdad de pedidos.

## Salida

### Estado de cada llamada (0 negativas, 0 JSON roto, 1 intento cada una)
| variante | cap | estado | intentos | md5 system / user / esquema (1.er intento) |
|---|---|---|---|---|
| D | 2 | ok | 1 | 65d7f452 / fb15ec01 / bcb706ab |
| C2 | 5 | ok | 1 | 65d7f452 / 6615abac / bcb706ab |
| D | 5 | ok | 1 | 65d7f452 / 6615abac / bcb706ab |
| C2 | 6 | ok | 1 | 65d7f452 / 89ae9f12 / bcb706ab |
| D | 6 | ok | 1 | 65d7f452 / 89ae9f12 / bcb706ab |
| C2 | 7 | ok | 1 | 65d7f452 / 1f7547ed / bcb706ab |
| D | 7 | ok | 1 | 65d7f452 / 1f7547ed / bcb706ab |

### Canon (uno por video, el de F46b)
Canon (uno por video): `primary_decade` 1960s · `spans` 1937-2007

`condition_evolution`: {'at_event': 'The town was active, with functioning buildings and infrastructure, though already heavily contaminated with visible asbestos dust and tailings used in construction and public spaces. Industrial areas like the mill were extremely dusty.', 'later': 'Progressive demolition and abandonment led to decaying, deserted buildings, widespread dispersal of asbestos tailings by wind and water, and permanent barricades blocking access to the now officially abolished and highly toxic forbidden zone.'}

`forbidden_anachronisms`: Smartphones, LED screens, modern flat panels, contemporary clothing (post-2000s), modern cars (post-1980), GPS devices, drones, modern industrial safety equipment, digital cameras, plastic packaging, modern logos and branding, clean and pristine environments.

### Tabla de los 8 chequeos (por foto; C2 | D)

1 año (fuente) · 2 año dentro de `spans` · 3 lugar del DÓNDE en la prosa · 4 gente sin grupo · 5 nombres reales en el ancla → en la prosa · 6 `text_in_image` (idioma de `place_language`) · 7 notas F8 · 8 palabras

| cap · foto | 1 año (fuente) | 2 en canon | 3 lugar C2 \| D | 4 gente sin grupo C2 \| D | 5 nombres ancla → prosa C2 \| D | 6 texto C2 \| D | 7 F8 C2 \| D | 8 palabras C2 \| D |
|---|---|---|---|---|---|---|---|---|
| 2 · 1 | 1961 (1) dicho en el ancla) | sí | Madrid \| Madrid | no \| no | Daniel Écija (padre), Daniel Écija padre, Arantxa Écija, María Bernal → no \| no | no \| no | — \| — | 134 \| 201 |
| 2 · 2 | 1962 (1) dicho en el ancla) | sí | Madrid \| Madrid | no \| no | — → no \| no | no \| no | — \| — | 123 \| 197 |
| 2 · 3 | 1962 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | — → no \| no | no \| no | — \| — | 144 \| 181 |
| 2 · 4 | 1962 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | Subcomité de Wittenoom → no \| no | no \| no | — \| — | 133 \| 176 |
| 2 · 5 | 1962 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | — → no \| no | no \| no | manos/cara: manos en plano close \| — | 111 \| 168 |
| 2 · 6 | 1962 (2) el de la foto anterior del cap) | sí | no \| Madrid | no \| no | John Patrick de Juan, Mercedes de Juan, Milagros Barroso, Ramón de Juan → no \| no | no \| no | — \| — | 130 \| 187 |
| 2 · 7 | 1962 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | — → no \| no | no \| no | — \| — | 127 \| 175 |
| 2 · 8 | 1962 (2) el de la foto anterior del cap) | sí | no \| Málaga | no \| no | Víctor Calvo → no \| no | no \| no | — \| — | 135 \| 191 |
| 2 · 9 | 1962 (2) el de la foto anterior del cap) | sí | no \| Málaga | no \| no | Víctor Calvo → no \| no | no \| no | — \| — | 135 \| 160 |
| 2 · 10 | 1962 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | — → no \| no | no \| no | — \| — | 145 \| 182 |
| 2 · 11 | 1962 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | — → no \| no | no \| no | — \| — | 139 \| 189 |
| 2 · 12 | 1962 (2) el de la foto anterior del cap) | sí | no \| Australia | no \| no | — → no \| no | no \| no | — \| — | 133 \| 158 |
| 2 · 13 | 1962 (2) el de la foto anterior del cap) | sí | no \| Wittenoom | no \| no | — → no \| no | no \| no | — \| — | 127 \| 171 |
| 2 · 14 | 1962 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom | no \| no | — → no \| no | no \| no | — \| — | 140 \| 218 |
| 2 · 15 | 1962 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom | no \| no | — → no \| no | no \| no | — \| — | 128 \| 173 |
| 2 · 16 | 1962 (2) el de la foto anterior del cap) | sí | no \| Wittenoom | sí \| no | — → no \| no | no \| no | — \| — | 144 \| 206 |
| **cap 2 total** (16 fotos) | — | **0 fuera** | **4 \| 10** | **1 \| 0** | **0 \| 0 con nombre en la prosa** | **0 \| 0** | **1 \| 0** | **133 prom. \| 183 prom.** |
| 5 · 1 | 1966 (1) dicho en el ancla) | sí | Australia \| Wittenoom | no \| no | Subcomité de Wittenoom, Sir James Vernon, James Vernon → no \| Subcomité de Wittenoom | no \| no | — \| — | 127 \| 265 |
| 5 · 2 | 1966 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom | no \| no | — → no \| no | no \| no | — \| — | 130 \| 191 |
| 5 · 3 | 1966 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom | no \| no | — → no \| no | no \| no | — \| — | 130 \| 180 |
| 5 · 4 | 1966 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom | no \| no | — → no \| no | no \| no | — \| — | 138 \| 205 |
| 5 · 5 | 1966 (2) el de la foto anterior del cap) | sí | Madrid \| Madrid | no \| no | Daniel Écija (padre), Daniel Écija padre, Arantxa Écija → no \| no | no \| no | — \| — | 135 \| 217 |
| 5 · 6 | 1971 (1) dicho en el ancla) | sí | no \| Madrid, Wittenoom | no \| no | John Patrick de Juan, Mercedes de Juan, Milagros Barroso, Ramón de Juan → no \| no | no \| no | — \| — | 129 \| 215 |
| 5 · 7 | 1971 (2) el de la foto anterior del cap) | sí | Wittenoom \| Australia, Wittenoom | no \| no | — → no \| no | no \| no | — \| — | 135 \| 177 |
| 5 · 8 | 1985 (1) dicho en el ancla) | sí | no \| no | no \| no | Daniel Écija (padre), Daniel Écija padre, Arantxa Écija → no \| no | no \| no | — \| — | 125 \| 208 |
| 5 · 9 | 1985 (2) el de la foto anterior del cap) | sí | Wittenoom \| no | no \| sí | Subcomité de Wittenoom → Subcomité de Wittenoom \| no | sí «WITTENOOM» (en) \| sí «WITTENOOM» (en) | camera_angle: from the traveler's point of view; lighting: Harsh overhead fluorescent light that highlights the sudden tension in his facial muscles \| — | 115 \| 169 |
| 5 · 10 | 1978 (1) dicho en el ancla) | sí | Wittenoom \| Australia, Wittenoom | no \| no | — → no \| no | no \| sí «DANGER ASBESTOS» (en) | — \| — | 127 \| 192 |
| 5 · 11 | 1986 (1) dicho en el ancla) | sí | Wittenoom \| Australia, Wittenoom | no \| no | — → no \| no | no \| no | — \| — | 124 \| 165 |
| 5 · 12 | 1993 (1) dicho en el ancla) | sí | Wittenoom \| Australia, Wittenoom | no \| no | — → no \| no | sí «AREA CLOSED» (en) \| no | — \| — | 137 \| 177 |
| 5 · 13 | 1991 (1) dicho en el ancla) | sí | no \| no | sí \| no | Daniel Écija (padre), Daniel Écija padre, Arantxa Écija → no \| no | no \| no | — \| — | 146 \| 202 |
| 5 · 14 | 1991 (2) el de la foto anterior del cap) | sí | no \| no | no \| sí | — → no \| no | no \| no | — \| — | 137 \| 183 |
| 5 · 15 | 1991 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | — → no \| no | no \| no | — \| — | 143 \| 214 |
| 5 · 16 | 1991 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | — → no \| no | no \| no | — \| — | 138 \| 203 |
| **cap 5 total** (16 fotos) | — | **0 fuera** | **10 \| 10** | **1 \| 2** | **1 \| 1 con nombre en la prosa** | **2 \| 2** | **1 \| 0** | **132 prom. \| 198 prom.** |
| 6 · 1 | 1989 (1) dicho en el ancla) | sí | no \| Australia | no \| no | Subcomité de Wittenoom → no \| no | no \| no | — \| — | 130 \| 162 |
| 6 · 2 | 1989 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | — → no \| no | no \| no | — \| — | 122 \| 192 |
| 6 · 3 | 1988 (1) dicho en el ancla) | sí | no \| Australia | no \| no | — → no \| no | no \| no | — \| — | 124 \| 190 |
| 6 · 4 | 1988 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | John Patrick de Juan, Mercedes de Juan, Ramón de Juan → no \| no | no \| no | — \| — | 131 \| 163 |
| 6 · 5 | 1988 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | — → no \| no | no \| no | — \| — | 118 \| 172 |
| 6 · 6 | 1988 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | — → no \| no | no \| no | — \| — | 116 \| 141 |
| 6 · 7 | 1988 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | — → no \| no | no \| no | manos/cara: manos en plano detail \| — | 110 \| 163 |
| 6 · 8 | 1988 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | Melita Markey → no \| no | no \| no | — \| — | 122 \| 169 |
| 6 · 9 | 1988 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | — → no \| no | no \| no | manos/cara: manos en plano close \| — | 118 \| 165 |
| 6 · 10 | 2007 (1) dicho en el ancla) | sí | no \| no | sí \| no | Subcomité de Wittenoom → Subcomité de Wittenoom \| Subcomité de Wittenoom | no \| sí «Wittenoom» (en) | — \| — | 135 \| 179 |
| 6 · 11 | 2007 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | — → no \| no | no \| sí «MEDIA STATEMENT» (en) | — \| — | 136 \| 155 |
| 6 · 12 | 1992 (1) dicho en el ancla) | sí | no \| no | no \| no | — → no \| no | sí «REJECTED» (en) \| no | — \| — | 129 \| 148 |
| 6 · 13 | 1992 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | Larry Graham → no \| no | no \| no | — \| — | 135 \| 164 |
| 6 · 14 | 1992 (2) el de la foto anterior del cap) | sí | no \| no | no \| no | Mark Nevill → no \| no | no \| no | — \| — | 139 \| 166 |
| 6 · 15 | 2016 (1) dicho en el ancla) | año fuera del canon | no \| no | sí \| sí | — → no \| no | no \| no | — \| — | 137 \| 147 |
| 6 · 16 | 2023 (1) dicho en el ancla) | año fuera del canon | no \| no | no \| no | — → no \| no | no \| no | — \| — | 152 \| 165 |
| **cap 6 total** (16 fotos) | — | **2 fuera** | **0 \| 2** | **2 \| 1** | **1 \| 1 con nombre en la prosa** | **1 \| 2** | **2 \| 0** | **128 prom. \| 165 prom.** |
| 7 · 1 | 2023 (3) el último del cap anterior) | año fuera del canon | Australia, Fortescue \| Wittenoom | no \| no | — → no \| no | no \| no | — \| — | 121 \| 168 |
| 7 · 2 | 2023 (2) el de la foto anterior del cap) | año fuera del canon | no \| Wittenoom | no \| sí | — → no \| no | no \| no | — \| — | 120 \| 163 |
| 7 · 3 | 2023 (2) el de la foto anterior del cap) | año fuera del canon | Fortescue \| Fortescue, Wittenoom | no \| no | — → no \| no | no \| no | — \| — | 127 \| 152 |
| 7 · 4 | 2023 (2) el de la foto anterior del cap) | año fuera del canon | Wittenoom \| Fortescue | no \| no | — → no \| no | no \| no | — \| — | 124 \| 147 |
| 7 · 5 | 2021 (1) dicho en el ancla) | año fuera del canon | no \| Wittenoom | no \| no | — → no \| no | no \| sí «ASBESTOS RISK AREA» (en) | — \| — | 128 \| 179 |
| 7 · 6 | 2021 (2) el de la foto anterior del cap) | año fuera del canon | Fortescue \| Fortescue | no \| no | — → no \| no | no \| no | props_detail: like veins across the land. \| — | 117 \| 147 |
| 7 · 7 | 2023 (1) dicho en el ancla) | año fuera del canon | no \| Wittenoom | no \| no | Johnnell Parker, Maitland Parker → no \| no | no \| no | — \| — | 139 \| 179 |
| 7 · 8 | 2023 (2) el de la foto anterior del cap) | año fuera del canon | no \| Wittenoom | no \| no | Johnnell Parker, Maitland Parker → no \| no | no \| no | — \| — | 147 \| 168 |
| 7 · 9 | 2024 (1) dicho en el ancla) | año fuera del canon | Wittenoom \| Wittenoom | no \| sí | Johnnell Parker, Maitland Parker → no \| no | no \| no | — \| — | 127 \| 139 |
| 7 · 10 | 2024 (2) el de la foto anterior del cap) | año fuera del canon | Australia, Federal \| Australia, Federal | no \| no | — → no \| no | no \| sí «FEDERAL COURT» (en) | — \| — | 120 \| 161 |
| 7 · 11 | 2024 (2) el de la foto anterior del cap) | año fuera del canon | Wittenoom \| Gorge, Wittenoom | no \| no | — → no \| no | no \| sí «DANGER ASBESTOS» (en) | — \| — | 137 \| 175 |
| 7 · 12 | 2024 (2) el de la foto anterior del cap) | año fuera del canon | Wittenoom \| Wittenoom | no \| sí | — → no \| no | sí «DANGER ASBESTOS CONTAMINATION» (en) \| no | mood: An open wound, \| — | 130 \| 168 |
| **cap 7 total** (12 fotos) | — | **12 fuera** | **8 \| 12** | **0 \| 3** | **0 \| 0 con nombre en la prosa** | **1 \| 3** | **2 \| 0** | **128 prom. \| 162 prom.** |

Cómo se mide:
- **3** usa la misma regla de F46b: palabras con mayúscula de 4 letras o más del DÓNDE que aparecen en la prosa.
- **5** busca el nombre entero, o su último token con mayúscula de 4 letras o más (el apellido), en el ancla y en la prosa armada.
- **6** toma el idioma de `place_language` (Wittenoom: `en`).

### Lo que se ve en la tabla (hechos medidos, sin elegir variante)
- **Año fuera del canon:**
  - cap 7: 12 de 12 (2021–2024);
  - cap 6: 2 de 16 (fotos 15 y 16, 2016 y 2023);
  - caps 2 y 5: 0.
  - `spans` es 1937-2007 para todo el video. `forbidden_anachronisms` prohíbe «contemporary clothing (post-2000s)… digital cameras… clean and pristine environments» también en esas 14 fotos.
- **El lugar del DÓNDE en la prosa (C2 | D):**
  - cap 2: 4 | 10;
  - cap 5: 10 | 10;
  - cap 6: 0 | 2;
  - cap 7: 8 | 12.
  - D escribe más seguido «Wittenoom / Australia / Pilbara» en el setting.
- **Banjima:**
  - ningún `people_group` es Banjima (el canon no lo tiene);
  - las fotos 7 y 8 del cap 7 (Maitland y Johnnell Parker) caen en `asbestos_advocates_victims` en las dos variantes;
  - «Banjima» llega a la prosa porque está en el ancla: C2 2/12, D 3/12; D además pone «Aboriginal» 2 veces en el cap 7 y 1 en el cap 6.
- **Gente sin grupo (C2 | D):**
  - cap 2: 1 | 0;
  - cap 5: 1 | 2;
  - cap 6: 2 | 1;
  - cap 7: 0 | 3.
- **Nombres reales en la prosa:** 0 en las dos variantes. Los «1 con nombre» de los caps 5 y 6 son **falsos positivos** del chequeo 5: «Subcomité de Wittenoom» es un `personaje` del pool y su «apellido» es el lugar «Wittenoom».
- **`text_in_image` (C2 | D):**
  - cap 2: 0 | 0;
  - cap 5: 2 | 2;
  - cap 6: 1 | 2;
  - cap 7: 1 | 3.
  - Todos en inglés, el idioma del lugar.
- **F8 (C2 | D):**
  - cap 2: 1 | 0;
  - cap 5: 1 | 0;
  - cap 6: 2 | 0;
  - cap 7: 2 | 0.
  - D no disparó ninguna regla F8.
- **Palabras (promedio, C2 | D):**
  - cap 2: 133 | 183;
  - cap 5: 132 | 198;
  - cap 6: 128 | 165;
  - cap 7: 128 | 162.
- **El año sale dos veces en la prosa de D:** el `setting` de D ya trae el año en 47 de 60 fotos (cap 2: 12/16, cap 5: 15/16, cap 6: 9/16, cap 7: 11/12; C2 lo trae en 13/60), y el código vuelve a agregarlo (`{setting}, {año}.`). Ejemplo: «…Pilbara, 2023, the gorge walls and creek line behind him, 2023.».
- **D mete negaciones en el setting** («no people», «no vehicles», «no one present»): 5 de 12 fotos del cap 7.

### Ejemplo: cap 7, foto 8 (la del handoff)
#### Cap 7 · foto 8 · beat 13

- ancla: ««Todavía lloro por mi territorio, pero eso está arraigado en mí; simplemente no puedo alejarme de él», dijo Parker.»
- año: 2023 (2) el de la foto anterior del cap)
- DÓNDE: Wittenoom; Australia; Tribunal Federal; Cauces, pozas y llanuras de inundación hasta el río Fortescue.
- grupos C2 | D: asbestos_advocates_victims | asbestos_advocates_victims

**C2** (147 palabras):

> The elderly Banjima man, bearing the signs of illness, his face lined with determination and sorrow. Turning his head to face the camera, his gaze steady and direct. Looking directly into the lens, his eyes holding the weight of memory and loss, his expression not of tears but of profound weariness. The deep lines etched around his eyes and mouth, telling a story of a long life and a long fight. Outdoors, against the soft-focus backdrop of his red, dusty homeland, 2023. Grainy 35mm documentary photograph, 2023, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Soft, frontal golden hour light, catching the texture of his skin. Warm skin tones, grey hair, against the ochre and red of the outback. Medium shot, eye-level, shallow depth of field. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

**D** (168 palabras):

> The elderly Aboriginal Banjima man around seventy, gaunt and stooped with the signs of illness, standing alone on a rise above the creek country. He stands with his feet planted in the red soil, one hand holding his hat against his chest, the wind pulling at his loose shirt. His face turned toward the camera, eyes wet and steady, shoulders drawn down and chest sunken, weathered lined features. A battered wide-brimmed hat held against his chest. A low ridge over Banjima country near Wittenoom Gorge, Pilbara, 2023, the gorge walls and creek line behind him, 2023. Grainy 35mm documentary photograph, 2023, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Late afternoon golden hour, warm low sun across the gorge. Red earth, ochre cliffs, dusty green spinifex, faded cotton shirt, warm amber light. Medium shot, slightly low angle from below the rise, shallow depth of field, 85mm lens. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

### Por cap: `people_group` y el setting de cada foto (estado de `condition_evolution`: lo lee el analista)

#### Cap 2

| foto | grupos C2 | grupos D | setting C2 | setting D |
|---|---|---|---|---|
| 1 | european_migrant_families | european_migrant_families | The ornate, crowded ballroom of the Círculo de Bellas Artes in Madrid, with high ceilings and classical decor. | grand belle-époque ballroom of a Madrid arts club, September 1961, tall mirrored walls, gilded mouldings, marble columns, a velvet-draped stage with a small dance orchestra |
| 2 | european_migrant_families | european_migrant_families | The weathered stone archway of a mid-century Madrid church. | stone façade and steps of a modest Madrid parish church, 20 September 1962, a black mid-century taxi waiting at the kerb, narrow street of balconied apartment blocks |
| 3 | european_migrant_families | european_migrant_families | A bustling Spanish port in 1962, with industrial cranes and the massive steel hull of the ship dominating the frame. | Málaga harbour quay, late September 1962, a tall white migrant liner with a single funnel, cranes and bollards, the Mediterranean behind |
| 4 | european_migrant_families | european_migrant_families | The windswept deck of a passenger liner at sea, only the sky and water are visible. | open stern deck of a 1960s passenger liner, lifeboats in davits, deck chairs, the wake spreading over the Mediterranean |
| 5 | european_migrant_families | european_migrant_families | At the railing of the ship, with the endless sea stretching out before them. | narrow side promenade of a 1960s migrant liner, riveted white bulkhead, round portholes, deck rail and sea beyond |
| 6 | european_migrant_families | european_migrant_families | A communal recreation area on the deck of a 1960s passenger ship. | veranda of a simple corrugated-iron and timber house in Wittenoom, 1962, the town active, red dirt yard, a mid-century truck parked beyond, dusty blue sky |
| 7 | european_migrant_families, wittenoom_children | wittenoom_children, european_migrant_families | The exposed deck of the ship, heat haze shimmering above the metal railings. | open sun deck of a 1960s migrant liner in tropical heat, canvas awnings, deck chairs, a glassy sea under a white sky |
| 8 | european_migrant_families, wittenoom_children | wittenoom_children, european_migrant_families | A crowded dockside, the boy dwarfed by the scale of the ship and the surrounding crowd. | steel gangway up the side of a white migrant liner at Málaga quay, September 1962, port warehouses and cranes behind |
| 9 | [] | european_migrant_families | The middle of the ocean, with no land in sight, under a vast, cloud-streaked sky. | Málaga harbour mouth, September 1962, breakwater and lighthouse, the cathedral and hills behind the city, cranes along the quay |
| 10 | european_migrant_families, wittenoom_children | european_migrant_families | The ship navigating the narrow Suez Canal, with flat, sun-scorched sandy banks visible close by. | Suez Canal, autumn 1962, flat desert banks, a distant palm cluster and low mud buildings, a cargo ship far ahead |
| 11 | wittenoom_children | european_migrant_families, wittenoom_children | A small, sparse passenger cabin on a ship, the room gently rocking with the motion of the waves. | narrow lower-deck passage of a 1960s migrant liner, riveted steel, sweating paint, a single porthole showing a tilted horizon |
| 12 | european_migrant_families | [] | The cramped, utilitarian interior of a 1960s propeller plane. | over the Pilbara desert of Western Australia, 1962, red iron-rich plains, dry creek lines, flat-topped ranges in haze |
| 13 | [] | [] | A rudimentary airstrip in the vast, empty Pilbara desert, surrounded by nothing but red earth and low scrub. | Wittenoom airstrip, Pilbara, 1962, a graded dirt strip surfaced with grey-blue mine tailings, red earth all around, a corrugated-iron shed and a mid-century truck, range escarpment behind |
| 14 | european_migrant_families, wittenoom_children | european_migrant_families, wittenoom_children | A newly-built street in 1962 Wittenoom. The houses are simple structures of corrugated iron, wood, and asbestos cement sheeting, under a dusty sky. | residential street of Wittenoom in its active 1962 state, a row of small occupied houses of corrugated iron, timber frames and asbestos-cement sheet walls on stumps, the road and yards surfaced with tailings, red desert and range behind |
| 15 | [] | mining_workers | The surface of a yard or pathway in Wittenoom, where the asbestos was used as landfill and surfacing. | Wittenoom Gorge mine and mill, 1962, red rock gorge walls, timber headframe, corrugated-iron mill sheds, ore trucks on narrow rails |
| 16 | [] | european_migrant_families, wittenoom_children | A sparse, wood-paneled company office, circa 1944. A geological map is partially visible on the wall. | backyard of an occupied Wittenoom house in 1962, corrugated iron and asbestos-cement walls, a clothesline, the yard surfaced with tailings, red desert and range beyond |

#### Cap 5

| foto | grupos C2 | grupos D | setting C2 | setting D |
|---|---|---|---|---|
| 1 | officials_regulators | mining_workers, officials_regulators | A sparse, wood-paneled corporate office in 1966 Australia, with a window showing a bright, dusty exterior | the asbestos mill office at Wittenoom Gorge, December 1966, corrugated iron walls and timber veranda, blue-grey tailings spread over the red earth yard, the gorge cliffs behind |
| 2 | [] | [] | The vast, dark interior of the asbestos processing mill, filled with silent industrial equipment | interior of the Wittenoom asbestos mill, December 1966, the day the plant shut down, industrial timber and iron structure, poorly ventilated, every surface coated in fiber dust |
| 3 | [] | [] | The Wittenoom gorges, an Australian outback landscape of red earth and rock | Wittenoom Gorge, December 1966, just after the mine closure, red iron-rock cliffs, dry creek bed, the mill sheds tiny at the gorge mouth |
| 4 | mining_workers | mining_workers | A dusty road leading away from the Wittenoom mine complex into the empty outback | the gorge road out of Wittenoom, December 1966, road surface made of blue asbestos tailings, the mill and red cliffs shrinking behind |
| 5 | european_migrant_families | european_migrant_families | The tiled, dimly lit hallway of a modest Madrid apartment building in 1966 | a Madrid periphery brick apartment block, winter 1966, terrazzo steps, green-painted plaster walls, a small frosted window on the landing, bare bulb overhead |
| 6 | european_migrant_families | european_migrant_families | A sun-baked, deserted airstrip in the Australian outback, surfaced with pale gravel | a corrugated iron and asbestos cement house in Wittenoom, 1971, patio surfaced with blue asbestos tailings, half the neighbouring houses already empty, red desert beyond |
| 7 | [] | [] | Wittenoom, years after its closure, with decaying corrugated iron buildings lining the street | Wittenoom, Western Australia, 1971, after the mine closure, the town still standing but thinning, red desert and gorge cliffs behind, no traffic |
| 8 | officials_regulators | european_migrant_families | An Australian airport immigration booth, circa 1985, with a Formica counter and sterile lighting | an Australian airport immigration checkpoint, 1985, beige laminate counters, fluorescent ceiling panels, a rope barrier and a queue blurred behind |
| 9 | officials_regulators | [] | The same airport immigration booth, now charged with tension | an Australian airport immigration checkpoint counter, 1985, laminate surface, a rubber stamp and ink pad at the edge of frame |
| 10 | european_migrant_families | [] | A suburban street in Wittenoom in the late 1970s, with other houses looking deserted | Wittenoom, Western Australia, 1978, the state government reducing the town, boarded windows, iron-roofed houses still standing, red plain and gorge cliffs behind |
| 11 | [] | [] | A deserted street in Wittenoom during the town's demolition phase, mid-1980s | Wittenoom, Western Australia, late 1980s, demolition of the town, neighbouring houses already reduced to slabs, red desert and cliffs behind |
| 12 | [] | [] | The derelict entrance to the Wittenoom airport, 1993 | Wittenoom airstrip, Western Australia, 1993, newly closed, red desert on both sides, the demolished town a scatter of slabs in the distance |
| 13 | [] | asbestos_advocates_victims | A dimly lit doctor's office in Madrid, 1991, with wood furniture and medical charts | a hospital consulting room in Madrid, 1991, pale green walls, a steel desk, a fluorescent light box on the wall with a chest radiograph, a paper file on the desk |
| 14 | [] | [] | The quiet living room of a Madrid home, decades after the photo was taken | a modest bedroom in a Madrid apartment, 1991, dark wood dresser, lace runner, a made bed with a wool blanket, a window with net curtains |
| 15 | european_migrant_families | european_migrant_families | A room filled with memories, the walls lined with sepia-toned family photographs | a modest Madrid living room, decades after 1991, cream walls, a dark wood table and sideboard, sepia photographs pinned to the wall and spread across the tablecloth, a window beside her |
| 16 | [] | european_migrant_families | A dark tabletop in a quiet room | the Madrid living room, decades after 1991, cream wall and window edge, sepia photographs spread on the tablecloth softly out of focus |

#### Cap 6

| foto | grupos C2 | grupos D | setting C2 | setting D |
|---|---|---|---|---|
| 1 | mining_workers | asbestos_advocates_victims | A quiet, commemorative room in an advocacy group's office, circa 1989. | 1989 cemetery on the dry outskirts of Perth, Western Australia, brown grass, eucalyptus trees, low iron fence |
| 2 | asbestos_advocates_victims | asbestos_advocates_victims | A sparse community meeting room, late 1970s, with institutional furniture. | late-1970s rented hall, stacked chairs along the wall, ceiling fans, a tea urn on a side table |
| 3 | [] | asbestos_advocates_victims, officials_regulators | A formal, wood-paneled courtroom, circa 1988. | Supreme Court of Western Australia courtroom, 1988, jarrah timber panelling, tall windows, bar table with barristers from behind |
| 4 | asbestos_advocates_victims | asbestos_advocates_victims | A sterile hospital examination room from the late 1980s. | Perth hospital radiology room, 1989, beige scanner housing, tiled floor, lead-glass window to the control booth |
| 5 | asbestos_advocates_victims | asbestos_advocates_victims | A hospital testing room with medical equipment. | Perth hospital respiratory lab, 1989, a boxy spirometer on a trolley, a chart recorder, a technician's white coat at the edge of frame |
| 6 | [] | [] | A darkened radiologist's viewing room. | Perth hospital radiology reading room, late 1980s, lightboxes in a row, most of them switched off |
| 7 | [] | asbestos_advocates_victims | A cluttered government office desk, circa 2000. | small rented office, metal desks, a wall of filing cabinets, a kettle, a card index box, a wall calendar from the 1980s |
| 8 | asbestos_advocates_victims | asbestos_advocates_victims | A simple, public hospital room with minimal furnishings. | late-1980s hospital outpatient waiting room, vinyl chairs in a row, a water cooler, a noticeboard with pinned pamphlets |
| 9 | officials_regulators | officials_regulators | A bureaucratic office desk cluttered with papers and files. | Western Australian government boardroom, late 1980s, venetian blinds, a wall map, a carafe of water |
| 10 | [] | officials_regulators | A roadside in the vast, red-earthed Australian outback, circa 2007. | 2007 sealed highway junction in the Pilbara, Western Australia, red earth shoulders, spinifex, a white utility truck parked on the verge |
| 11 | officials_regulators | [] | A formal press briefing room with an official state crest on the wall behind the podium. | Western Australian minister's office in Perth, 2007, leather desk pad, a window with the city skyline behind blinds |
| 12 | [] | [] | A government office interior, suggesting the 1990s. | Parliament House committee room, Perth, 1992, dark timber panels, green leather chairs, tall windows |
| 13 | [] | [] | Wittenoom Gorge, Western Australia. | Wittenoom Gorge, Pilbara, Western Australia, 1992, a rusted ore chute, a collapsed mill shed, ghost gums along the creek |
| 14 | [] | [] | The edge of a massive tailings field in the Australian outback. | Wittenoom townsite 1992, half-demolished houses of corrugated iron and asbestos cement, a leaning power pole, red hills behind |
| 15 | [] | [] | A document laid out on an office desk, circa 2016. | Perth state department office, 2016, a plain desk, a brass lamp, blinds drawn |
| 16 | [] | [] | A darkened, modern geological survey office. | Wittenoom, Pilbara, Western Australia, 2023, the gorge and red ranges behind, the dry Fortescue floodplain in the distance |

#### Cap 7

| foto | grupos C2 | grupos D | setting C2 | setting D |
|---|---|---|---|---|
| 1 | [] | [] | The vast, arid floodplain of the Fortescue River basin in Western Australia, scarred by erosion. | Wittenoom Gorge mouth, Pilbara, 2023, abandoned tailings dump against red rock walls, no vehicles, no structures intact |
| 2 | [] | [] | A spartan office or research tent in a remote area, 2020s. | creek bed draining Wittenoom Gorge, Pilbara, 2023, spinifex and gum trees along the banks, red stone, no people |
| 3 | [] | [] | The lower catchment area of the Fortescue River, under a vast, empty sky. | Fortescue floodplain north of Wittenoom, Pilbara, 2023, open arid plain with scattered gum trees along the watercourses |
| 4 | [] | [] | The edge of a dried-up water pool in the Wittenoom area. | a shallow pool in a creek bed on the Fortescue floodplain, Pilbara, 2023, cracked mud and river stones |
| 5 | [] | [] | A remote, unmarked watercourse in the Western Australian outback, 2021. | edge of the Wittenoom contaminated area, Pilbara, 2021, fence line of steel posts and a single sign, creek bed crossing beneath |
| 6 | [] | [] | The entire Fortescue River basin, viewed from the air. | Fortescue River valley, Pilbara, 2021, broad floodplain with paperbark and river gums along the banks |
| 7 | asbestos_advocates_victims | asbestos_advocates_victims | A quiet, elevated spot in the Hamersley Range, overlooking the contaminated territory, 2023. | Banjima country near Wittenoom Gorge, Pilbara, 2023, spinifex, red rock and a dry creek bed behind them |
| 8 | asbestos_advocates_victims | asbestos_advocates_victims | Outdoors, against the soft-focus backdrop of his red, dusty homeland. | a low ridge over Banjima country near Wittenoom Gorge, Pilbara, 2023, the gorge walls and creek line behind him |
| 9 | [] | [] | The elevated lookout point over the Wittenoom landscape, at dawn. | a low ridge over Banjima country near Wittenoom Gorge, Pilbara, 2024, no one present |
| 10 | [] | asbestos_advocates_victims | An Australian city, outside the Federal Court. | Federal Court of Australia entrance, city street, overcast morning, no vehicles in frame |
| 11 | [] | [] | The access road to Wittenoom, with the red cliffs of the gorge visible in the distance. | road entrance to Wittenoom township and gorge, Pilbara, 2024, red plain, gorge walls rising behind |
| 12 | [] | [] | The barricaded entrance to the Wittenoom contaminated area. | Wittenoom and gorge entrance, Pilbara, 2024, red plain, decaying buildings, blue-grey tailings surfaces along the streets, no vehicles, no people |

### Cap 7 (Veo): el `video_prompt` del clip, entero y sin evaluar

Clips Veo en el cap: 1 (`veo_position` end). Ancla del clip: «No se ha retirado una sola palada de asbesto. ¿Quién va a sacar la primera palada de esa tierra?»

> The camera executes a very slow and subtle push-in, gradually closing in on the rusty shovel stuck in the desolate earth. A faint breeze stirs the air, causing fine particles of red dust and grey waste to drift across the ground and the sparse, dry vegetation to tremble almost imperceptibly.

### Costos reales (`data/cost_history.json`, `video_id = f47-lab`; detalle en `COSTOS.md`)
| servicio | descripción | tokens in / out | costo US$ |
|---|---|---|---:|
| Gemini 2.5 Pro | f47 C2 ch07 slots (intento 1) | 12152 / 4117 | 0.0854 |
| Gemini 2.5 Pro | f47 C2 ch06 slots (intento 1) | 13628 / 5547 | 0.1370 |
| Anthropic claude-fable-5-1 | f47 D ch07 slots (intento 1) | 20039 / 8027 | 0.6017 |
| Gemini 2.5 Pro | f47 C2 ch05 slots (intento 1) | 14201 / 5682 | 0.1525 |
| Anthropic claude-fable-5-1 | f47 D ch02 slots (intento 1) | 27354 / 10445 | 0.7958 |
| Anthropic claude-fable-5-1 | f47 D ch06 slots (intento 1) | 22743 / 12234 | 0.8391 |
| Anthropic claude-fable-5-1 | f47 D ch05 slots (intento 1) | 23807 / 16673 | 1.0717 |

- **Gemini 2.5 Pro**: US$ 0.3749
- **Anthropic claude-fable-5-1**: US$ 3.3084
- **Total**: US$ 3.6833 (tope 6.00)

Fable costó entre US$ 0,60 y 1,07 por cap (20–27 k tokens de entrada y 8–17 k de salida). Pro costó entre US$ 0,085 y 0,15 por cap. La estimación del handoff (Fable ≈ 4, Pro ≈ 0,36) se cumplió: 3,31 + 0,37.

## Verificación (paso 8 de /tanda)
- **Suite rápida** (`test_module_f25c.py test_module_f24.py test_module_f21.py`, proxy muerto): **55 verdes, 3 saltados**.
- **Suite amplia** (los patrones de `lab/hyperframes/f41/verificar.sh`, con `HTTP(S)_PROXY=127.0.0.1:9`, `NO_PROXY=localhost,127.0.0.1` y `-n auto`): **918 verdes, 5 fallas, 30 saltados** (`verif/suite_amplia.log`).
  - `m03_merge_timing` ×2: previas, conocidas.
  - `gfx_lab` ×3 (`test_preview_movimientos_y_salidas_por_tramo`, `test_cues_sin_escribir_el_proyecto`, `test_preview_usa_las_plantillas_reales`): F42b ya reportaba gfx_lab ×2 nuevas (datos de Orleans limpiados de `_steps/`).
  - Esta tanda no editó ningún archivo de producción ni de tests, así que no vienen de ella.
- **Candado de ch02 (`fase2b … --only-cap ch02`): no corrido.** Escribe en `output/`, y la regla de esta tanda prohíbe tocar `output/` (igual que en F42b).
- **No se corrió** `pytest --collect-only` ni `pytest test_*.py` en bloque.
- `git status`: lo único modificado fuera de `lab/hyperframes/f47/` es `DECISIONES.md` (paso 0, commiteado) y `lab/ESTADO_SESION.md`. `diag_234_cap4.py`, `lab/TOPE_TANDA.json` y `f28a.log` ya estaban modificados antes. En `data/` solo `cost_history.json`; nada en `output/` ni en `topics_db`.

## Lo que queda abierto (entero)
- j1. **Elegir variante y decidir los arreglos:** lo deciden Omar y el analista con esta tabla. Esta tanda mide; no arregla.
- j2. **Canon uno por video:** 14 de 60 fotos de los caps 5–7 tienen un año fuera de `spans` 1937-2007 (cap 7 entero, cap 6 fotos 15–16). Además, `forbidden_anachronisms`, que prohíbe ropa post-2000, cámaras digitales y entornos limpios, cae sobre fotos de 2016–2024.
  - Ninguna de las dos variantes lo «corrige»: el canon no llega a los casilleros como regla por foto.
  - La frase de `condition_evolution` que describe cada setting no se mide por código; está pegada por foto para el analista.
- j3. **Ningún `people_group` Banjima:** las fotos de Maitland y Johnnell Parker caen en `asbestos_advocates_victims`, cuyo `appearance` no trae origen aborigen. «Banjima» llega a la prosa solo cuando está en el ancla.
- j4. **El año duplicado en D:** el setting de D trae el año en 47/60 fotos y el armado de C2 lo vuelve a poner. Es la plantilla `{setting}, {año}.` de `f46b.armar`; no la toqué.
- j5. **Negaciones en el setting de D** («no people», «no vehicles»): 5/12 en el cap 7. Seedream suele dibujar lo que se nombra, aun negado (se ve con fotos, no en esta tanda).
- j6. **D escribe más largo:** entre 162 y 198 palabras de promedio, contra 128–133 de C2.
- j7. **Falsos positivos del chequeo 5:** «Subcomité de Wittenoom» (`personaje` del pool) se cuenta como «nombre en la prosa» porque su último token es el lugar. Además, en el ancla se listan todos los `documented_people` que comparten apellido (p. ej. «Arantxa Écija» cuando el ancla dice «Daniel Écija»). Nombres reales de personas en la prosa: 0.
- j8. **Lugar en la prosa, desparejo según el cap:**
  - C2: 4/16, 10/16, 0/16, 8/12;
  - D: 10/16, 10/16, 2/16, 12/12.
  - En el cap 6, el DÓNDE del expediente es solo «Australia» en las fotos 1–9 y está vacío en las 10–16: el chequeo 3 casi no tiene contra qué medir (los ids de esos beats no traen lugar).
- j9. **Idioma del cartel:** todos los `text_in_image` están en inglés (`place_language` = `en`). Las fotos de Madrid (cap 5, fotos 5, 13–16) no trajeron cartel, así que no se puso a prueba un cartel en español.
- j10. **El ajuste de transporte de D:** si la raíz llega como array, se envuelve como hace Gemini. No hizo falta saber si Fable la mandó como array u objeto: la validación pasó al 1.er intento en los 4 caps (ver `slots_D_*.json`).
- j11. **Costo de D:** Fable cuesta unas 7 veces lo que Pro por cap (≈ US$ 0,83 contra 0,125). En producción serían unos 7 caps por video.
- j12. **El cap 7 (Veo):** sus 12 suplementarias se midieron. El clip (`image_prompt` + `video_prompt`) queda fuera, como pide el handoff; el `video_prompt` está pegado entero.
- j13. **gfx_lab ×3 en la suite amplia** (F42b reportaba ×2): no vienen de esta tanda. Queda para quien toque gfx_lab.
- j14. **`f46b.LAB` apuntado a una carpeta temporal del sistema** (`%TEMP%\f47_*`), para que `f46b.slots` no pise `f46b/prompt_slots_pro.txt`. Ese archivo temporal no se usa.
- j15. **El form de Omar** no se tocó (no se revisó ni cerró ningún proceso suyo).

## Procesos y subagentes
- Shells en segundo plano: la corrida (`bls93cas6`) y las suites (`b9vva4mbf`), las dos terminadas.
- Subagente: el revisor-handoff, terminado.
- No quedó ningún proceso de la tanda vivo; no cerré nada de Omar.

## Veredicto de revisor-handoff (íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

Solo lectura. No corrí pytest ni scripts que llamen APIs. Usé git, md5sum y lectura de JSON.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | md5 del handoff = a9f039e2… | OK | `md5sum` da a9f039e25b84ee5bb9e014485fe1b5ab |
| 2 | Paso 0: las 2 líneas de DECISIONES tal cual, commiteadas con el handoff | OK | commit 8f43d8a (+2 en DECISIONES.md, +66 el handoff). El texto de las líneas 02:49 y 02:55 coincide con el handoff |
| 3 | C2 (Pro) en los caps 5, 6, 7 y D (Fable, effort high) en los caps 2, 5, 6, 7, en paralelo | OK | `slots_C2_ch05-07.json` y `slots_D_ch02/05-07.json`, los 7 con estado ok. Los timestamps de `cost_history` van de 03:07:05 a 03:09, solapados. `corrida.log` lo confirma |
| 4 | D cambia solo el modelo: mismo system, user y esquema | OK | md5 de `pedidos/` idénticos C2=D en los caps 5, 6 y 7 (04636fa2, 09a0e2ea, c2a21d6f). `pedido_D_ch02.txt` = `f46b/prompt_slots_pro.txt` (36ba2962) |
| 5 | Si Fable se niega o rompe el JSON, se reporta sin retocar el prompt | OK | No pasó: 7/7 ok al 1.er intento. Sin texto nuevo para los LLM |
| 6 | Costos en `cost_tracker` con video_id f47-lab; tope US$ 6,00 | OK | `cost_history` tiene 1 registro f47-lab con 7 entradas que suman 3,683256. Coincide con `COSTOS.md` y con el reporte (Pro 0,3749, Fable 3,3084, total 3,6833) |
| 7 | Armado por código + F8 igual que f46b, reusando f46b por import | OK | `f47_corridas.py` importa `f46_corridas` y `f46b_corridas` (líneas 34-35). `PROMPTS_F47.json` trae `f8_problemas` y `f8_slots_scrub` por foto |
| 8 | Cap 7 (Veo) sobre las suplementarias; `video_prompt` pegado entero sin evaluar | OK | El cap 7 tiene 12 fotos. El `video_prompt` está en el reporte y en la sección final de `PROMPTS_F47.md` |
| 9 | `PROMPTS_F47.md` con los prompts C2 \| D enteros y la tabla de los 8 chequeos | OK | `PROMPTS_F47.md` (170 KB) y `PROMPTS_F47.json` existen. La tabla está en el reporte con totales por cap |
| 10 | Crudos de cada modelo guardados | OK | Cada `slots_*.json` trae `crudos`, `pedidos` e `items` |
| 11 | Números del reporte contra los archivos | OK | Recalculé el año duplicado en el setting con el año exacto de cada foto: D 47/60 (cap 2: 12, cap 5: 15, cap 6: 9, cap 7: 11) y C2 13/60. Ambos coinciden con el reporte. Costo por cap y pedidos idénticos también coinciden |
| 12 | Cero fotos, cero fal | OK | Revisé `f47_corridas.py` con grep y no hay llamadas a fal ni a generación de imagen. Los costos son solo Gemini y Anthropic |
| 13 | Producción sin editar; nada en `data/` salvo `cost_history`, ni en `output/` ni `topics_db` | OK | `git status`: lo modificado fuera de f47 es `diag_234_cap4.py`, `lab/TOPE_TANDA.json` y `f28a.log`, que ya estaban antes, más `lab/ESTADO_SESION.md`, que el contrato exige. Los `topics_db_pre*.json` sin trackear son del 20 y 21 de octubre, previos a la tanda |
| 14 | `F47_REPORT.md` con «lo que queda abierto» entero | OK | Sección j1–j15, líneas 317-337 |
| 15 | Veredicto íntegro de revisor-handoff en el reporte | PARCIAL | El reporte termina en el marcador `{{VEREDICTO}}` (línea 345). Es el hueco para este veredicto |
| 16 | `lab/ESTADO_SESION.md` actualizado | OK | Diff con cabecera 03:25, bloque «Para Omar (F47)» y bloque F47 |
| 17 | Commit final de la tanda | NO VERIFICABLE | Todo f47 (menos handoff y paso 0) y `ESTADO_SESION.md` siguen sin commitear. El último commit es 8f43d8a. Falta que lo haga CC tras pegar este veredicto |
| 18 | Prohibido `pytest --collect-only` y `pytest test_*.py` en bloque | NO VERIFICABLE | El reporte dice que no se corrieron. `suite_amplia.log` muestra 918 verdes, 5 fallas y 30 saltados con patrones de `f41/verificar.sh`. Eso no es lo prohibido, pero tampoco tengo cómo comprobar los comandos exactos que se usaron |

Observaciones:
- Hay que pegar este veredicto en el marcador y hacer el commit; sin eso la tanda no está cerrada (filas 15 y 17).
- La suite amplia tiene 5 fallas (`m03_merge_timing` ×2 y `gfx_lab` ×3). El reporte las atribuye a causas previas porque no se editó producción. No lo verifiqué contra una línea base. El handoff no pedía suites, así que es un extra.
- El reporte usa «F47_REPORT: 7 caps por video» en j11 (el costo de D en producción) sin fuente. No está en el handoff.
- El chequeo 5 (nombres reales) tiene falsos positivos que el propio reporte declara en j7. La conclusión «0 nombres reales en la prosa» no depende de ellos.

Fuera de alcance: ninguno. Los tres archivos modificados fuera de f47 ya estaban modificados antes de la tanda; `lab/ESTADO_SESION.md` lo exige el contrato.

Riesgos que el contrato no cubre:
- El ruteador por hilo de `m03.call_pro_json` y el envoltorio de array para Fable son un ajuste de transporte en lab. Si alguna vez se pasa a producción, hay que revalidarlos.
- `lab/TOPE_TANDA.json` quedó en 6.0 con fecha 03:10. Eso es un candado de gasto que sigue abierto después de la tanda.
- La conclusión sobre el canon (14 de 60 fotos fuera de `spans`) depende de reusar el `canon_C.json` de F46b sin regenerar. Se declaró, pero no se contrastó con otro canon.

### Adenda de CC (después del veredicto)
- **#15 / #17:** el veredicto ya está pegado y el commit va con este reporte.
- **#18:** los comandos exactos fueron `python -m pytest -q test_module_f25c.py test_module_f24.py test_module_f21.py` y `python -m pytest -q -n auto test_module_f[0-9]*.py test_module_gfx_*.py test_module_01a*.py test_module_01b*.py test_module_m03_*.py test_module_fase2b_reassemble.py test_module_fase2b_hwencode.py test_module_concat_windowed.py test_module_transition_timeout.py test_constantes_con_origen.py`, con proxy muerto. Son archivos `test_module_*` nombrados (los del paso 8 de /tanda), no los `test_*.py` de lab de la raíz.
- **j11 («7 caps»):** es medido. `03_visual.json` de Wittenoom tiene 7 capítulos. Es un ejemplo de este video, no una regla.
- **`lab/TOPE_TANDA.json`:** queda en 6,00 desde 03:10, como en las tandas anteriores (fuera de git). Lo cambia la próxima tanda.

