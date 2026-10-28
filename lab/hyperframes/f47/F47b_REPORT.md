# F47b — ¿Qué modelo llena mejor los casilleros de foto? Opus 5.5 (E) y Sonnet 5.5 (F) contra Fable (D) y Pro (C2) — REPORTE

CC · 2026-10-28 · rama `f11-guion-v4` · handoff `lab/hyperframes/f47/HANDOFF_F47b_opus_sonnet.md` (md5 `90bc49e6554f032885eddbe3c1dbddde` ✓). Paso 0 → parte única. Tope US$ 4,00; **gasto real US$ 1,7210**, leído de `cost_history` (`f47b-lab`). **Cero fotos, cero llamadas a fal. PARADA:** no se elige modelo ni se toca producción.

## Lecturas declaradas
- `CLAUDE.md`, `DECISIONES.md` (cola, hasta 02:55), `lab/ESTADO_SESION.md` (cabecera, F47 y F46b) y el handoff entero.
- Base de F47 (de esta misma sesión): `f47_corridas.py`, `F47_REPORT.md`, `PROMPTS_F47.json`, crudos y pedidos de D.
- `claude_helpers.PRICES`: Opus 5.5 = 4 / 20 y Sonnet 5.5 = 2 / 10 US$ por millón de tokens de entrada y salida. Los dos ya están, así que el costo se calcula sin tocar producción.

## Módulos (paso 2 de /tanda)
- **Producción: ninguno se edita.** No cambia `MAPA_PROYECTO`.
- **Lab:**
  - **`f47_corridas.py`** (lab de F47). Un cambio mínimo: `MODELOS = {"D": MODELO_D}` y el ruteador usa `MODELOS[var]` en vez de `MODELO_D`. Para D da lo mismo que antes. El effort sigue siendo `guion_v4.ESFUERZO[MODELO_D]` = `high` para toda variante Claude, o sea el mismo de D.
  - **Nuevo `f47b_corridas.py`.** Importa `f47_corridas` y le cambia `LAB_ID` a `f47b-lab`, el tope a 4,00 y suma E y F a `MODELOS`. Reusa `cargar`, `ruteador`, `una_variante`, `armar_c2` y `chequeos` sin copiarlos. Agrega los chequeos 9 y 10 y las tablas de F47b.
- **Una variable:** el modelo. E y F usan el mismo system, user-prompt, esquema, validación (`f46b.slots`) y transporte (array → `{"image_prompts": …}`) que D.
- **Constantes nuevas, con origen en su línea:**
  - `TOPE_USD` 4,00 (Omar);
  - `CAPS` (2, 5, 6, 7) (handoff §Constantes);
  - E `claude-opus-5-5` y F `claude-sonnet-5-5` (handoff §Constantes, Omar 03:19).
- **Simulador: no aplica.** El handoff no trae regla ni filtro de contenido: mide.

## Qué se corrió
`python lab/hyperframes/f47/f47b_corridas.py prompts` (03:21:57 → 03:23:53, `corrida_f47b.log`).
- **8 llamadas en paralelo** (8 workers): E y F × caps 2, 5, 6, 7.
  - Freno antes de cada una (el de F47, con el id `f47b-lab` y tope 4,00).
  - Costos con `cost_tracker.start_video("f47b-lab")` / `end_video()`.
  - Las 8 salieron **ok al 1.er intento**: 0 negativas, 0 JSON roto, 0 reintentos de validación.
- **Armado por código + F8:** `f47.armar_c2`, que es `f46b.armar` sin aspecto + `f46b.f8`, igual que en F47.
- **C2 y D** se leen de `PROMPTS_F47.json`; no se re-corren. El C2 del cap 2 es el de F46b.
- **Prueba en seco** antes de gastar (`f47b_corridas.py seco <dir>`, sin API y con proxy muerto). Verificó la igualdad de pedidos y las tablas.
- **Salidas** (en `lab/hyperframes/f47/`):
  - `PROMPTS_F47b.md`: por cap y foto, ancla, año y fuente, grupos C2 | D | E | F, palabras de las 4 variantes y los prompts enteros de E y F (los de C2 y D están en `PROMPTS_F47.md`); después la tabla de los 10 chequeos con totales por cap y por variante, y la de costos;
  - `PROMPTS_F47b.json`;
  - crudos `slots_E_ch02/05/06/07.json` y `slots_F_ch02/05/06/07.json`;
  - `pedidos/pedido_E_chNN.txt` y `pedido_F_chNN.txt`;
  - `COSTOS_F47b.md`.

## Salida

### Pedido igual al de D (md5 del archivo `pedidos/pedido_X_chNN.txt`, system + user del 1.er intento)

| cap | D | E | F | E = D | F = D |
|---|---|---|---|---|---|
| 2 | 36ba2962 | 36ba2962 | 36ba2962 | sí | sí |
| 5 | 04636fa2 | 04636fa2 | 04636fa2 | sí | sí |
| 6 | 09a0e2ea | 09a0e2ea | 09a0e2ea | sí | sí |
| 7 | c2a21d6f | c2a21d6f | c2a21d6f | sí | sí |

md5 de system / user / esquema por intento (los guarda el ruteador):

| variante | cap | estado | intentos | md5 system / user / esquema (1.er intento) |
|---|---|---|---|---|
| E | 2 | ok | 1 | 65d7f452 / fb15ec01 / bcb706ab |
| F | 2 | ok | 1 | 65d7f452 / fb15ec01 / bcb706ab |
| E | 5 | ok | 1 | 65d7f452 / 6615abac / bcb706ab |
| F | 5 | ok | 1 | 65d7f452 / 6615abac / bcb706ab |
| E | 6 | ok | 1 | 65d7f452 / 89ae9f12 / bcb706ab |
| F | 6 | ok | 1 | 65d7f452 / 89ae9f12 / bcb706ab |
| E | 7 | ok | 1 | 65d7f452 / 1f7547ed / bcb706ab |
| F | 7 | ok | 1 | 65d7f452 / 1f7547ed / bcb706ab |

### Tabla de los 10 chequeos (por foto; C2 \| D \| E \| F)

1 año (fuente) · 2 año dentro de `spans` · 3 lugar del DÓNDE en la prosa · 4 gente sin grupo · 5 nombres reales en el ancla → en la prosa · 6 `text_in_image` · 7 notas F8 · 8 palabras · 9 años/décadas del `setting` crudo distintos del de la foto · 10 negaciones «no + palabra» en el `setting` crudo

| cap · foto | 1 año | 2 canon | 3 lugar | 4 sin grupo | 5 nombres ancla → prosa | 6 texto | 7 F8 | 8 palabras | 9 año del setting ≠ | 10 negaciones |
|---|---|---|---|---|---|---|---|---|---|---|
| 2 · 1 | 1961 (1) dicho en el ancla) | sí | Madrid \| Madrid \| Madrid \| Madrid | no \| no \| no \| no | Daniel Écija (padre), Daniel Écija padre, Arantxa Écija, María Bernal → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 134 \| 201 \| 164 \| 149 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 2 | 1962 (1) dicho en el ancla) | sí | Madrid \| Madrid \| Madrid \| Madrid | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 123 \| 197 \| 139 \| 150 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 3 | 1962 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 144 \| 181 \| 130 \| 146 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 4 | 1962 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | Subcomité de Wittenoom → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 133 \| 176 \| 111 \| 134 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 5 | 1962 (2) el de la foto anterior del cap) | sí | no \| no \| no \| Madrid | no \| no \| no \| sí | — → no \| no \| no \| no | no \| no \| no \| no | manos/cara: manos en plano close \| — \| — \| — | 111 \| 168 \| 125 \| 137 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 6 | 1962 (2) el de la foto anterior del cap) | sí | no \| Madrid \| no \| Madrid | no \| no \| no \| no | John Patrick de Juan, Milagros Barroso, Mercedes de Juan, Ramón de Juan → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 130 \| 187 \| 126 \| 147 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 7 | 1962 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 127 \| 175 \| 113 \| 142 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 8 | 1962 (2) el de la foto anterior del cap) | sí | no \| Málaga \| Málaga \| Málaga | no \| no \| no \| no | Víctor Calvo → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 135 \| 191 \| 118 \| 139 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 9 | 1962 (2) el de la foto anterior del cap) | sí | no \| Málaga \| Málaga \| no | no \| no \| no \| sí | Víctor Calvo → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 135 \| 160 \| 103 \| 118 | — \| — \| — \| — | with no land in sight \| — \| — \| — |
| 2 · 10 | 1962 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| sí | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 145 \| 182 \| 120 \| 123 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 11 | 1962 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 139 \| 189 \| 122 \| 164 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 12 | 1962 (2) el de la foto anterior del cap) | sí | no \| Australia \| Australia \| Australia | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 133 \| 158 \| 106 \| 137 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 13 | 1962 (2) el de la foto anterior del cap) | sí | no \| Wittenoom \| Australia \| Australia, Wittenoom | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| sí «WITTENOOM» (en) \| no | — \| — \| — \| — | 127 \| 171 \| 129 \| 162 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 14 | 1962 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom \| no \| Wittenoom | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 140 \| 218 \| 132 \| 145 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 15 | 1962 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 128 \| 173 \| 118 \| 141 | — \| — \| — \| — | — \| — \| — \| — |
| 2 · 16 | 1962 (2) el de la foto anterior del cap) | sí | no \| Wittenoom \| no \| Wittenoom | sí \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 144 \| 206 \| 138 \| 162 | 1944 \| — \| — \| — | — \| — \| — \| — |
| **cap 2 total** (16 fotos) | — | **0 fuera** | **4 \| 10 \| 7 \| 10** | **1 \| 0 \| 0 \| 3** | **0 \| 0 \| 0 \| 0 con nombre** | **0 \| 0 \| 1 \| 0** | **1 \| 0 \| 0 \| 0** | **133 prom. \| 183 prom. \| 125 prom. \| 144 prom.** | **1 \| 0 \| 0 \| 0** | **1 \| 0 \| 0 \| 0** |
| 5 · 1 | 1966 (1) dicho en el ancla) | sí | Australia \| Wittenoom \| Wittenoom \| Australia, Wittenoom | no \| no \| no \| no | Subcomité de Wittenoom, Sir James Vernon, James Vernon → no \| Subcomité de Wittenoom \| Subcomité de Wittenoom \| Subcomité de Wittenoom | no \| no \| no \| no | — \| — \| — \| — | 127 \| 265 \| 177 \| 166 | — \| — \| — \| — | — \| — \| — \| — |
| 5 · 2 | 1966 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 130 \| 191 \| 152 \| 163 | — \| — \| — \| — | — \| — \| — \| — |
| 5 · 3 | 1966 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 130 \| 180 \| 141 \| 152 | — \| — \| — \| — | — \| — \| — \| — |
| 5 · 4 | 1966 (2) el de la foto anterior del cap) | sí | Wittenoom \| Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 138 \| 205 \| 151 \| 150 | — \| — \| — \| — | — \| — \| — \| — |
| 5 · 5 | 1966 (2) el de la foto anterior del cap) | sí | Madrid \| Madrid \| Madrid \| Madrid | no \| no \| no \| no | Daniel Écija (padre), Daniel Écija padre, Arantxa Écija → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 135 \| 217 \| 166 \| 147 | — \| — \| — \| — | — \| — \| — \| — |
| 5 · 6 | 1971 (1) dicho en el ancla) | sí | no \| Madrid, Wittenoom \| Wittenoom \| Madrid | no \| no \| no \| no | John Patrick de Juan, Milagros Barroso, Mercedes de Juan, Ramón de Juan → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 129 \| 215 \| 159 \| 139 | — \| — \| — \| — | — \| — \| — \| — |
| 5 · 7 | 1971 (2) el de la foto anterior del cap) | sí | Wittenoom \| Australia, Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| sí | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 135 \| 177 \| 133 \| 140 | — \| — \| — \| — | — \| no traffic \| — \| — |
| 5 · 8 | 1985 (1) dicho en el ancla) | sí | no \| no \| no \| no | no \| no \| no \| sí | Daniel Écija (padre), Daniel Écija padre, Arantxa Écija → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 125 \| 208 \| 158 \| 162 | — \| — \| — \| — | — \| — \| — \| — |
| 5 · 9 | 1985 (2) el de la foto anterior del cap) | sí | Wittenoom \| no \| no \| Wittenoom | no \| sí \| sí \| sí | Subcomité de Wittenoom → Subcomité de Wittenoom \| no \| no \| Subcomité de Wittenoom | sí «WITTENOOM» (en) \| sí «WITTENOOM» (en) \| sí «WITTENOOM» (en) \| sí «Wittenoom» (en) | camera_angle: from the traveler's point of view; lighting: Harsh overhead fluorescent light that highlights the sudden tension in his facial muscles \| — \| — \| — | 115 \| 169 \| 127 \| 163 | — \| — \| — \| — | — \| — \| — \| — |
| 5 · 10 | 1978 (1) dicho en el ancla) | sí | Wittenoom \| Australia, Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no | — → no \| no \| no \| no | no \| sí «DANGER ASBESTOS» (en) \| sí «ASBESTOS HAZARD» (en) \| no | — \| — \| — \| — | 127 \| 192 \| 138 \| 147 | — \| — \| 1985 \| — | — \| — \| — \| — |
| 5 · 11 | 1986 (1) dicho en el ancla) | sí | Wittenoom \| Australia, Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 124 \| 165 \| 130 \| 143 | — \| — \| 1992 \| 1992 | — \| — \| — \| — |
| 5 · 12 | 1993 (1) dicho en el ancla) | sí | Wittenoom \| Australia, Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no | — → no \| no \| no \| no | sí «AREA CLOSED» (en) \| no \| no \| no | — \| — \| — \| — | 137 \| 177 \| 118 \| 135 | — \| — \| — \| — | — \| — \| — \| — |
| 5 · 13 | 1991 (1) dicho en el ancla) | sí | no \| no \| no \| no | sí \| no \| no \| no | Daniel Écija (padre), Daniel Écija padre, Arantxa Écija → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 146 \| 202 \| 140 \| 157 | — \| — \| — \| — | — \| — \| — \| — |
| 5 · 14 | 1991 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| sí \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 137 \| 183 \| 121 \| 140 | — \| — \| — \| — | — \| — \| — \| — |
| 5 · 15 | 1991 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 143 \| 214 \| 146 \| 161 | — \| — \| — \| 2020s | — \| — \| — \| — |
| 5 · 16 | 1991 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 138 \| 203 \| 144 \| 156 | — \| — \| — \| 2020s | — \| — \| — \| — |
| **cap 5 total** (16 fotos) | — | **0 fuera** | **10 \| 10 \| 10 \| 11** | **1 \| 2 \| 1 \| 3** | **1 \| 1 \| 1 \| 2 con nombre** | **2 \| 2 \| 2 \| 1** | **1 \| 0 \| 0 \| 0** | **132 prom. \| 198 prom. \| 144 prom. \| 151 prom.** | **0 \| 0 \| 2 \| 3** | **0 \| 1 \| 0 \| 0** |
| 6 · 1 | 1989 (1) dicho en el ancla) | sí | no \| Australia \| no \| no | no \| no \| no \| no | Subcomité de Wittenoom → no \| no \| Subcomité de Wittenoom \| Subcomité de Wittenoom | no \| no \| no \| no | — \| — \| — \| — | 130 \| 162 \| 151 \| 140 | — \| — \| — \| — | — \| — \| — \| — |
| 6 · 2 | 1989 (2) el de la foto anterior del cap) | sí | no \| no \| no \| Australia | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 122 \| 192 \| 174 \| 140 | 1970s \| 1970s \| 1979 \| — | — \| — \| — \| — |
| 6 · 3 | 1988 (1) dicho en el ancla) | sí | no \| Australia \| no \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 124 \| 190 \| 155 \| 139 | — \| — \| — \| — | — \| — \| — \| — |
| 6 · 4 | 1988 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | John Patrick de Juan, Mercedes de Juan, Ramón de Juan → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 131 \| 163 \| 137 \| 143 | — \| 1989 \| — \| — | — \| — \| — \| — |
| 6 · 5 | 1988 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 118 \| 172 \| 137 \| 134 | — \| 1989 \| — \| — | — \| — \| — \| — |
| 6 · 6 | 1988 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 116 \| 141 \| 117 \| 116 | — \| — \| — \| — | — \| — \| — \| — |
| 6 · 7 | 1988 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | manos/cara: manos en plano detail \| — \| — \| — | 110 \| 163 \| 127 \| 128 | 2000 \| — \| — \| — | — \| — \| — \| — |
| 6 · 8 | 1988 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | Melita Markey → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 122 \| 169 \| 143 \| 124 | — \| — \| — \| — | — \| — \| — \| — |
| 6 · 9 | 1988 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | manos/cara: manos en plano close \| — \| — \| — | 118 \| 165 \| 119 \| 123 | — \| — \| — \| — | — \| — \| — \| — |
| 6 · 10 | 2007 (1) dicho en el ancla) | sí | no \| no \| no \| no | sí \| no \| no \| no | Subcomité de Wittenoom → Subcomité de Wittenoom \| Subcomité de Wittenoom \| no \| Subcomité de Wittenoom | no \| sí «Wittenoom» (en) \| no \| no | — \| — \| — \| — | 135 \| 179 \| 139 \| 133 | — \| — \| — \| — | — \| — \| — \| — |
| 6 · 11 | 2007 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| sí «MEDIA STATEMENT» (en) \| sí «WITTENOOM ABOLISHED» (en) \| sí «DARK CHAPTER ENDS» (en) | — \| — \| — \| — | 136 \| 155 \| 126 \| 145 | — \| — \| — \| — | — \| — \| — \| — |
| 6 · 12 | 1992 (1) dicho en el ancla) | sí | no \| no \| no \| no | no \| no \| no \| no | — → no \| no \| no \| no | sí «REJECTED» (en) \| no \| no \| no | — \| — \| — \| — | 129 \| 148 \| 115 \| 131 | — \| — \| — \| — | — \| — \| — \| — |
| 6 · 13 | 1992 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | Larry Graham → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 135 \| 164 \| 122 \| 128 | — \| — \| — \| — | — \| — \| — \| — |
| 6 · 14 | 1992 (2) el de la foto anterior del cap) | sí | no \| no \| no \| no | no \| no \| no \| no | Mark Nevill → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 139 \| 166 \| 119 \| 122 | — \| — \| — \| — | — \| — \| — \| — |
| 6 · 15 | 2016 (1) dicho en el ancla) | año fuera del canon | no \| no \| no \| no | sí \| sí \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 137 \| 147 \| 117 \| 122 | — \| — \| — \| — | — \| — \| — \| — |
| 6 · 16 | 2023 (1) dicho en el ancla) | año fuera del canon | no \| no \| no \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 152 \| 165 \| 148 \| 147 | — \| — \| — \| — | — \| — \| — \| — |
| **cap 6 total** (16 fotos) | — | **2 fuera** | **0 \| 2 \| 0 \| 1** | **2 \| 1 \| 0 \| 0** | **1 \| 1 \| 1 \| 2 con nombre** | **1 \| 2 \| 1 \| 1** | **2 \| 0 \| 0 \| 0** | **128 prom. \| 165 prom. \| 134 prom. \| 132 prom.** | **2 \| 3 \| 1 \| 0** | **0 \| 0 \| 0 \| 0** |
| 7 · 1 | 2023 (3) el último del cap anterior) | año fuera del canon | Australia, Fortescue \| Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 121 \| 168 \| 146 \| 143 | — \| — \| — \| — | — \| no vehicles; no structures intact \| — \| — |
| 7 · 2 | 2023 (2) el de la foto anterior del cap) | año fuera del canon | no \| Wittenoom \| Wittenoom \| Wittenoom | no \| sí \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| color_palette: faint blue-grey veins of tailings in the gullies; props_detail: a single deep erosion gully linking the dump to the creek bed like an open vein \| color_palette: thin veins of blue-grey tailings | 120 \| 163 \| 114 \| 131 | — \| — \| — \| — | — \| no people \| — \| — |
| 7 · 3 | 2023 (2) el de la foto anterior del cap) | año fuera del canon | Fortescue \| Fortescue, Wittenoom \| Fortescue, Wittenoom \| Fortescue, Wittenoom | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 127 \| 152 \| 131 \| 145 | — \| — \| — \| — | — \| — \| — \| — |
| 7 · 4 | 2023 (2) el de la foto anterior del cap) | año fuera del canon | Wittenoom \| Fortescue \| Wittenoom \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 124 \| 147 \| 131 \| 140 | — \| — \| — \| — | — \| — \| — \| — |
| 7 · 5 | 2021 (1) dicho en el ancla) | año fuera del canon | no \| Wittenoom \| Wittenoom \| no | no \| no \| no \| no | — → no \| no \| no \| no | no \| sí «ASBESTOS RISK AREA» (en) \| no \| no | — \| — \| — \| — | 128 \| 179 \| 134 \| 143 | — \| — \| — \| — | — \| — \| — \| — |
| 7 · 6 | 2021 (2) el de la foto anterior del cap) | año fuera del canon | Fortescue \| Fortescue \| Fortescue \| Fortescue | no \| no \| no \| no | — → no \| no \| no \| no | no \| no \| no \| no | props_detail: like veins across the land. \| — \| — \| — | 117 \| 147 \| 123 \| 136 | — \| — \| — \| — | — \| — \| — \| — |
| 7 · 7 | 2023 (1) dicho en el ancla) | año fuera del canon | no \| Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no | Maitland Parker, Johnnell Parker → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 139 \| 179 \| 141 \| 146 | — \| — \| — \| — | — \| — \| — \| — |
| 7 · 8 | 2023 (2) el de la foto anterior del cap) | año fuera del canon | no \| Wittenoom \| Wittenoom \| no | no \| no \| no \| no | Maitland Parker, Johnnell Parker → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 147 \| 168 \| 145 \| 150 | — \| — \| — \| — | — \| — \| — \| — |
| 7 · 9 | 2024 (1) dicho en el ancla) | año fuera del canon | Wittenoom \| Wittenoom \| Wittenoom \| no | no \| sí \| no \| no | Maitland Parker, Johnnell Parker → no \| no \| no \| no | no \| no \| no \| no | — \| — \| — \| — | 127 \| 139 \| 120 \| 151 | — \| — \| — \| — | — \| no one present \| — \| — |
| 7 · 10 | 2024 (2) el de la foto anterior del cap) | año fuera del canon | Australia, Federal \| Australia, Federal \| Australia, Federal \| Federal | no \| no \| no \| no | — → no \| no \| no \| no | no \| sí «FEDERAL COURT» (en) \| sí «FEDERAL COURT» (en) \| no | — \| — \| — \| — | 120 \| 161 \| 126 \| 131 | — \| — \| — \| — | — \| no vehicles in frame \| — \| — |
| 7 · 11 | 2024 (2) el de la foto anterior del cap) | año fuera del canon | Wittenoom \| Gorge, Wittenoom \| Wittenoom \| Wittenoom | no \| no \| no \| no | — → no \| no \| no \| no | no \| sí «DANGER ASBESTOS» (en) \| sí «ROAD CLOSED» (en) \| sí «ROAD CLOSED» (en) | — \| — \| — \| — | 137 \| 175 \| 137 \| 159 | — \| — \| — \| — | — \| — \| — \| — |
| 7 · 12 | 2024 (2) el de la foto anterior del cap) | año fuera del canon | Wittenoom \| Wittenoom \| Wittenoom \| no | no \| sí \| no \| no | — → no \| no \| no \| no | sí «DANGER ASBESTOS CONTAMINATION» (en) \| no \| no \| no | mood: An open wound, \| — \| — \| — | 130 \| 168 \| 123 \| 163 | — \| — \| — \| — | — \| no vehicles; no people \| — \| — |
| **cap 7 total** (12 fotos) | — | **12 fuera** | **8 \| 12 \| 12 \| 7** | **0 \| 3 \| 0 \| 0** | **0 \| 0 \| 0 \| 0 con nombre** | **1 \| 3 \| 2 \| 1** | **2 \| 0 \| 1 \| 1** | **128 prom. \| 162 prom. \| 131 prom. \| 145 prom.** | **0 \| 0 \| 0 \| 0** | **0 \| 5 \| 0 \| 0** |

Cómo se mide:
- **1–8:** igual que en F47 (`f47.chequeos`).
- **9:** años de 4 cifras y décadas («1980s») del `setting` crudo que no son el año de la foto. Una década cuenta si la foto no cae dentro de ella.
- **10:** los tramos entre comas del `setting` crudo que traen «no + palabra», pegados enteros.

### Totales por variante (los 4 caps, 60 fotos)

| variante | fotos | 3 lugar en la prosa | 4 gente sin grupo | 5 con nombre en la prosa | 6 texto | 7 F8 | 8 palabras prom. | 9 año del setting ≠ | 10 negaciones |
|---|---|---|---|---|---|---|---|---|---|
| C2 | 60 | 22 | 4 | 2 | 4 | 6 | 131 | 3 | 1 |
| D | 60 | 34 | 6 | 2 | 7 | 0 | 178 | 3 | 6 |
| E | 60 | 29 | 1 | 2 | 6 | 1 | 134 | 3 | 0 |
| F | 60 | 29 | 6 | 4 | 3 | 1 | 143 | 3 | 0 |

### Lo que se ve (hechos medidos, sin elegir modelo)
- **Las 4 variantes recibieron el mismo pedido.** El md5 del pedido es igual en D, E y F en cada cap, y el de D en el cap 2 es igual al de Pro en F46b.
- **Lugar del DÓNDE en la prosa (60 fotos):** C2 22 · D 34 · E 29 · F 29.
  - En el cap 7: C2 8 · D 12 · E 12 · F 7.
- **Gente sin grupo:** C2 4 · D 6 · **E 1** · F 6.
- **Nombres reales de personas en la prosa:** 0 en las 4 variantes. Los «con nombre» de la tabla (C2 2 · D 2 · E 2 · F 4) son todos el falso positivo «Subcomité de Wittenoom» (cap 5 fotos 1 y 9; cap 6 fotos 1 y 10).
- **`text_in_image`:** C2 4 · D 7 · E 6 · F 3.
- **Frases sacadas por F8:** C2 6 · D 0 · E 1 · F 1.
- **Palabras (promedio):** C2 131 · D 178 · **E 134** · F 143.
- **Año del setting distinto del de la foto (chequeo 9):** 3 en cada variante.
- **Negaciones en el setting (chequeo 10):** C2 1 · **D 6** · E 0 · F 0.
- **Año de la foto repetido en el setting:** C2 13/60 · **D 47/60** · E 33/60 · F 36/60. El código lo vuelve a agregar en `{setting}, {año}.`; medido como en F47.
- **Banjima y Aboriginal:**
  - «Banjima» en la prosa: C2 2 · D 3 · E 4 · F 3;
  - «Aboriginal / Indigenous»: C2 0 · D 3 · E 4 · F 0.
  - Las 4 variantes ponen a los Parker (cap 7, fotos 7 y 8) en `asbestos_advocates_victims`: el canon no tiene grupo Banjima.
- **Costo por cap (los 4 caps):**
  - **E (Opus) US$ 0,24–0,31**, suma 1,1328;
  - **F (Sonnet) US$ 0,12–0,16**, suma 0,5882;
  - D (Fable) 0,60–1,07, suma 3,3084;
  - C2 (Pro, caps 5–7) 0,085–0,15, suma 0,3749.
  - Los tokens de entrada son los mismos en D, E y F (mismo pedido); la salida varía (E 7,8–11 k, F 7,8–11,6 k, D 8–16,7 k).
- **Tiempo por llamada:** E 77–111 s · F 60–90 s · D 109–233 s · C2 67–121 s.

### Ejemplo: cap 7, foto 8 (E y F; C2 y D están en F47_REPORT.md)
#### Cap 7 · foto 8 · beat 13

- ancla: ««Todavía lloro por mi territorio, pero eso está arraigado en mí; simplemente no puedo alejarme de él», dijo Parker.»
- año: 2023 (2) el de la foto anterior del cap)
- grupos C2 | D | E | F: asbestos_advocates_victims | asbestos_advocates_victims | asbestos_advocates_victims | asbestos_advocates_victims
- palabras C2 | D | E | F: 147 | 168 | 145 | 150

**E** (145 palabras):

> Elderly Aboriginal Banjima man around 70, gaunt frame, hollow cheeks, grey beard, faded work shirt hanging loose on thin shoulders. He sits on his country, one hand pressed flat into the red earth as he speaks. Face toward the camera, weathered and lined, gaze steady and wet-eyed past the lens, shoulders slightly hunched with shallow breath. His palm resting on a patch of red soil. Red ground at the mouth of Wittenoom Gorge, spinifex and rock behind him, 2023. Grainy 35mm documentary photograph, 2023, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Soft late-afternoon light, warm side glow on one side of the face. Red earth, ochre, faded blue cotton, grey beard, warm amber light. Medium shot, eye-level, shallow depth of field, 85mm lens. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

**F** (150 palabras):

> An elderly Banjima man in his seventies, gaunt and frail, wearing a sun-faded cotton shirt and a worn hat. He sits on the red ground facing the country, speaking and then falling silent, one hand resting on his chest. His face in three-quarter profile, eyes toward the far hills, red dust cut by tear tracks on his cheeks. A thin wooden walking stick lying across his lap. Open red earth at the edge of Banjima country, low gorge hills behind him, 2023. Grainy 35mm documentary photograph, 2023, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Soft dawn light, warm on one side of his face. Red earth, ochre, faded cotton, dark weathered skin, pale dawn sky. Medium shot, eye-level, three-quarter from the side, 85mm lens, shallow depth of field. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

### Costos reales de esta tanda (`data/cost_history.json`, `video_id = f47b-lab`; `COSTOS_F47b.md`)
| servicio | descripción | tokens in / out | costo US$ |
|---|---|---|---:|
| Anthropic claude-sonnet-5-5 | f47 F ch07 slots (intento 1) | 20039 / 7759 | 0.1177 |
| Anthropic claude-sonnet-5-5 | f47 F ch06 slots (intento 1) | 22743 / 9685 | 0.1423 |
| Anthropic claude-opus-5-5 | f47 E ch07 slots (intento 1) | 20039 / 7811 | 0.2364 |
| Anthropic claude-opus-5-5 | f47 E ch02 slots (intento 1) | 27354 / 8358 | 0.2766 |
| Anthropic claude-sonnet-5-5 | f47 F ch02 slots (intento 1) | 27354 / 11008 | 0.1648 |
| Anthropic claude-sonnet-5-5 | f47 F ch05 slots (intento 1) | 23807 / 11576 | 0.1634 |
| Anthropic claude-opus-5-5 | f47 E ch05 slots (intento 1) | 23807 / 10640 | 0.3080 |
| Anthropic claude-opus-5-5 | f47 E ch06 slots (intento 1) | 22743 / 11043 | 0.3118 |

**Total**: US$ 1.7210 (tope 4.00)

La estimación del handoff (Opus 0,33–0,45 por cap, Sonnet 0,17–0,25, ≈ 2,8 en total) quedó por encima del real: E 0,24–0,31, F 0,12–0,16, total 1,72.

## Verificación (paso 8 de /tanda)
- **Suite rápida** (`test_module_f25c.py test_module_f24.py test_module_f21.py`, con proxy muerto): **55 verdes, 3 saltados**.
- **Suite amplia** (los patrones `test_module_*` de `lab/hyperframes/f41/verificar.sh`, con `HTTP(S)_PROXY=127.0.0.1:9`, `NO_PROXY=localhost,127.0.0.1` y `-n auto`): **918 verdes, 5 fallas, 30 saltados** (`verif_f47b/suite_amplia.log`).
  - Son las mismas 5 de F47: `m03_merge_timing` ×2 (previas) y `gfx_lab` ×3.
  - Esta tanda no tocó producción ni tests.
- **Candado de ch02: no corrido.** Escribe en `output/`, y la regla de la tanda prohíbe tocarlo.
- **No se corrió** `pytest --collect-only` ni `pytest test_*.py` en bloque.
- **`git status`:**
  - fuera de `lab/hyperframes/f47/`, solo cambia `DECISIONES.md` (paso 0, commiteado) y `lab/ESTADO_SESION.md`;
  - `diag_234_cap4.py`, `lab/TOPE_TANDA.json` (ahora 4,00 desde 03:30) y `f28a.log` ya venían modificados;
  - en `data/`, solo `cost_history.json`; nada en `output/` ni `topics_db`.

## Lo que queda abierto (entero)
- k1. **Elegir modelo:** lo deciden Omar y el analista con esta tabla. Después vienen las fotos solo del ganador contra Pro (DECISIONES 03:19), en otra tanda.
- k2. **Una corrida por modelo y por cap:** las diferencias de 1–3 fotos entre E y F (gente sin grupo, texto, lugar en el cap 7) pueden ser azar.
- k3. **Siguen sin resolver los arreglos de F47**, que ningún modelo corrige porque vienen del pedido y del canon:
  - el canon es uno por video (14 de 60 fotos fuera de `spans`);
  - no hay `people_group` Banjima;
  - el año se repite en la prosa: el setting lo trae (E 33/60, F 36/60) y `f46b.armar` lo vuelve a poner.
  Quedan para la tanda de arreglos (j2–j4 de F47).
- k4. **Falso positivo del chequeo 5** («Subcomité de Wittenoom»): sigue sin corregirse, como en F47 (j7). Nombres reales de personas en la prosa: 0 en las 4 variantes.
- k5. **Chequeo 9:**
  - una década cuenta si la foto no cae dentro de ella;
  - una frase como «decades after 1991» se lee como el año 1991 (≠ el de la foto si difiere);
  - los 3 de cada variante están en la tabla para leerlos a mano.
- k6. **Chequeo 10** solo mira «no + palabra» en el `setting`. Otras negaciones («without», «empty of») o las que caen en otros casilleros no se cuentan.
- k7. **Effort:** E y F van con `high`, el de D, para que cambie una sola variable. Sonnet 5.5 recalibró sus niveles de effort, así que `high` no tiene por qué equivaler entre modelos. No se probó otro effort.
- k8. **El cambio en `f47_corridas.py`** (`MODELOS[var]`) no altera F47: D sigue con `claude-fable-5-1` y effort `high`. No re-corrí D para comprobarlo (costaría US$ 3,31); el código de D pasa por la misma rama con el mismo valor.
- k9. **C2 del cap 2** sigue siendo el de F46b: no tiene tokens ni segundos en la tabla de costos (está en `f46b-lab`, US$ 0,1178).
- k10. **gfx_lab ×3** en la suite amplia: las mismas fallas que en F47; no vienen de esta tanda.
- k11. **El form de Omar** no se tocó.

## Procesos y subagentes
- Shells en segundo plano: la corrida (`bh97iz44q`) y las suites (`binuzlkf3`), terminadas.
- Subagente: el revisor-handoff, terminado.
- No quedó ningún proceso de la tanda vivo; no se cerró nada de Omar.

## Veredicto de revisor-handoff (íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | md5 del handoff = 90bc49e6… | OK | `md5sum` da 90bc49e6554f032885eddbe3c1dbddde |
| 2 | Paso 0: línea de DECISIONES.md tal cual + commit con el handoff | OK | commit fc72ed8 (DECISIONES.md +1 línea, handoff +52). El texto coincide con el handoff §Paso 0. |
| 3 | E = claude-opus-5-5, F = claude-sonnet-5-5, effort high, caps 2, 5, 6, 7 | OK | `f47b_corridas.py:30` (`MODELOS.update`). `guion_v4.py:59` ESFUERZO[claude-fable-5-1]="high", el mismo de D. |
| 4 | D no cambia con el diff de `f47_corridas.py` | OK | El diff agrega `MODELOS={"D":MODELO_D}` y cambia solo `model=MODELOS[var]`. Effort sigue `ESFUERZO[MODELO_D]`. Para D el valor es idéntico. No se re-corrió D, y el reporte lo dice en k8. |
| 5 | 8 llamadas en paralelo, freno, costos con cost_tracker en `f47b-lab` | OK | `corrida_f47b.log`: 8 ok al 1.er intento. Paralelismo y freno por lectura del reporte y del log; el código del freno no lo audité. |
| 6 | Pedido E y F con md5 igual al de D en cada cap | OK | `md5sum` de `pedidos/pedido_{D,E,F}_ch*.txt`: 3 iguales en cada cap (36ba2962, 04636fa2, 09a0e2ea, c2a21d6f). |
| 7 | Tope US$ 4,00; cero fotos; cero fal | OK | `lab/TOPE_TANDA.json` = 4.0. `cost_history` f47b-lab: total 1,720978, 8 entradas. COSTOS_F47b.md suma 1,7210. E 1,1328 y F 0,5882 cuadran con el reporte. |
| 8 | C2 y D leídos de PROMPTS_F47.json, sin re-correr | OK | `cost_history`: f47-lab sigue con 1 registro, 7 entradas, 3,6833. |
| 9 | PROMPTS_F47b.md con tabla de 10 chequeos C2/D/E/F, totales por cap, crudos, costos | OK | Existen `PROMPTS_F47b.md/.json`, 8 `slots_*`, 8 pedidos y `COSTOS_F47b.md`, todos no vacíos. Recalculé a mano los totales de lugar, sin grupo, texto, F8, chequeo 9 y chequeo 10. Cuadran con el reporte (lugar 22/34/29/29; sin grupo 4/6/1/6; chequeo 10: 1/6/0/0). |
| 10 | Ningún archivo de producción editado; nada en data/ salvo cost_history, output/ ni topics_db | OK | `git status`: solo `lab/ESTADO_SESION.md` y `f47_corridas.py` (lab) modificados, más los nuevos de f47. `data/` y `output/` limpios salvo cost_history, que está bajo git ignore o sin cambio rastreado. |
| 11 | F47b_REPORT.md con «lo que queda abierto» entero + veredicto íntegro de revisor-handoff | PARCIAL | Abierto k1–k11 presente (línea 215). El veredicto es el marcador `{{VEREDICTO}}` en la línea 241; es donde se pega este veredicto. |
| 12 | ESTADO_SESION.md actualizado; commit; no pytest en bloque | PARCIAL | ESTADO actualizado (diff visible). El commit de cierre aún no existe, porque HEAD sigue en fc72ed8; es esperable antes de pegar el veredicto. El reporte declara que no hubo `collect-only`; no lo pude verificar. |
| 13 | Parada, sin elegir modelo | OK | El reporte y el ESTADO dicen «elegir es tuyo y del analista» y no recomiendan modelo. |

Observaciones:
- El commit final falta, y el marcador `{{VEREDICTO}}` queda por reemplazar. Son pasos de cierre, no fallas de contenido.
- Dos afirmaciones del reporte no pude verificarlas. «Sonnet 5.5 recalibró sus niveles de effort» (k7) no está en ninguna fuente que yo vea. Las suites (55 verdes; 918 verdes + 5 fallas) las leí del reporte y no las corrí.
- `ESFUERZO` en `guion_v4.py` no tiene entrada para sonnet-5-5. La corrida usa la clave de Fable para todas las variantes. Cumple «mismo effort que D», pero el effort de Sonnet queda fijado por esa vía y no por su propia entrada.
- La estimación de costo del handoff (≈2,8) quedó por encima del real (1,72). El reporte lo dice.

Fuera de alcance: ninguno nuevo. `diag_234_cap4.py` (cambia TOPIC), `lab/TOPE_TANDA.json` y `lab/hyperframes/f28/a/f28a.log` ya venían modificados antes de la tanda.

Riesgos que el contrato no cubre:
- Una sola corrida por modelo y por cap, así que diferencias de 1 a 3 fotos entre E y F pueden ser azar (el reporte lo admite en k2).
- Los chequeos 9 y 10 son heurísticas de texto: falsos positivos como «decades after 1991», y solo se detecta «no + palabra».
- El cambio sin commitear en `f47_corridas.py` toca el lab de F47. Si alguien re-corre F47 sin él, E y F no existirían en `MODELOS`. Es retrocompatible para D.

### Adenda de CC (después del veredicto)
- **#11 / #12:** el veredicto está pegado. El commit va con este reporte e incluye el cambio en `f47_corridas.py`, así que ya no queda sin commitear.
- **k7 (fuente):** que Sonnet 5.5 recalibró los niveles de effort sale de la referencia del skill `claude-api` (sección de Claude Sonnet 5.5): «Effort still defaults to `high`, but the levels are recalibrated». No es del repo.
- **Effort de Sonnet:** viene de `ESFUERZO[MODELO_D]`, de forma deliberada. El handoff pide «effort high como D»: es el mismo valor para las tres variantes Claude, y no depende de una entrada propia de cada modelo.
- **Suites:** los comandos fueron los mismos de F47 (archivos `test_module_*` nombrados, con proxy muerto). Los logs están en `verif_f47b/`.

