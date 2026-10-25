# HANDOFF F23 — Familias D + G + H + I de la auditoría: el evento ya no es «un día», los umbrales de Orleans pasan a métrica, el intent de cada cap sale de la escaleta, el research habla los idiomas del caso

Analista · 2026-10-24 · Para CC (misma sesión). Base: `2dcc428` (rama `f11-guion-v4`). Una corrida al final (Kyshtym completo, research → guion), **tope US$ 6.00**. **PARADA al terminar.** Después de esta tanda no queda ninguna familia abierta de `AUDITORIA_fase1_supuestos.md`; lo que sigue es la prueba con dos temas nuevos (F24).

Referencias de línea: las de la auditoría (anexos 1–3) sobre `08d63d9`; con F21/F22 se movieron algunas, pero los nombres de funciones y constantes son los mismos.

## 0. Por qué
- **D.** Todo asume un evento de un día y un año: `anio_evento` entero único, contaminación ±20 años con excepciones solo en es/en/it, la compuerta y `is_hard` cuentan solo eventos con AAAA-MM-DD, una fecha por cap, «ese domingo», «fecha completa una vez, en el cap 2», `ficha` pide «los eventos del día», años `(19|20)\d\d`. Mayak va de 1949 a 1997 y el guion de F22d lo cuenta así, bien; los chequeos no lo entienden.
- **G.** Umbrales calibrados con el pool de Orleans (ACLU/DOJ): 150 datos / 8 citas / 2 elegibles / 10 eventos-día, documentos < 3.000 caracteres a la basura, conteo solo si ≥ 1.000, 60–80 hechos pedidos a la ficha aunque el pool tenga 120 ítems, chars por rol desacoplados de las palabras. Dan rojo o amarillo por tipo de fuentes, no por calidad.
- **H.** `narrative_intent` por número de cap (`DEFAULT_INTENT_BY_CAP`): si la explosión cae en el cap 2, ese cap es «setup» para la voz y las imágenes. «Un hecho, una cifra» expulsa los rangos («entre 70 y 80 toneladas»), que a veces son lo único honesto.
- **I.** El research busca en inglés siempre, prioriza `.gov`, pide `Accept-Language: en`, detecta solo en/es/fr/it, y recorta notas al pie solo en inglés.

**Decisión de alcance:** esta tanda **no** mete el juez LLM (queda para después de F24, con un guion de referencia). Y no toca imágenes, voz, gfx ni el contrato de 7 caps.

## 1. Cambios

### 1.1 El tiempo del caso (D)
**Perfil del seed** (`seed_profile`, `PROFILE_SCHEMA`): `anio_inicio`, `anio_fin` (enteros; iguales si el caso es de un día), `tipo_evento: "puntual" | "prolongado"` (puntual = el hecho central ocurre en un día o en pocos días; prolongado = meses o años). `anio_evento` se mantiene = `anio_inicio` (compatibilidad). El modelo los llena; sin perfil viejo, `anio_fin = anio_inicio`. Regenerar el perfil de Kyshtym y el de Orleans/Ycuá con el mismo paso (Flash, centavos); respaldar los actuales como `_perfil_f22.json`.

**Research** (`research_v3.py`):
- Contaminación por año (`ITEM_YEARS`, `LATE_OK`, `EARLY_OK`, ~1309-1336): se borran las listas de palabras por idioma. Un ítem se descarta por año **solo** si su año es anterior a `anio_inicio − 20`. Nada posterior se descarta por año: lo que pasa después (juicios, desclasificaciones, reclamos) es parte del caso. Lo de otro lugar lo sigue filtrando `place_re`, como hoy.
- Fallback `year = date.today().year` (~2087): si no hay año en el perfil, error explícito, no año actual.
- `presente_en_evento` y el digest (~1439, ~1875): «el evento» es el rango `[anio_inicio, anio_fin]`.
- R3 (~1008, 1104, 1138): cronología acepta `AAAA` además de `AAAA-MM` y `AAAA-MM-DD`; `fechas_presente` acepta las tres. La validación «el año de la cita = el año de la fecha» solo descarta si difieren en más de 1.
- Años: toda regex `(19|20)\d\d` de la fase 1 (`evidence.py` 72/245/288, `guion_v3_reglas.py` 47, `m05` 469 fallback «2000») pasa a `1[0-9]{3}|20\d\d`; el año por defecto de una fecha sin año es `anio_inicio` del perfil, y si la cronología cruza años, el de la entrada anterior más cercana.

**Compuerta y evidencia:** `pool_gate.py:44` y `video_length.gate_eventos_fecha`: cuentan eventos con fecha de **mes o día** (y de año solo, si `tipo_evento == "prolongado"`). `evidence.is_hard` y `used_in` (168-175, 208-210): un evento fechado se «usa» si en la oración suena la fecha **con la granularidad que tiene** (día → «14 de marzo»; mes → «marzo de 1957»; año → «1957»).

**Guion:**
- `guion_v3_reglas.replace_repeated_dates` (221-246): **se borra** (la buena es `guion_v4.replace_repeated_dates`). `DATE_MAX_PER_CAP` y `DATE_PARAPHRASE` (214-265): pasan a **métrica** («fechas literales por cap»); la lista de paráfrasis suma «ese año», «ese invierno», «esa primavera», «ese mes». El mensaje 257 «ese domingo» → «ese día».
- `guion_v4.replace_repeated_dates` (725-750): reemplaza solo si el día de la semana se puede calcular con `datetime` a partir de una fecha **completa** y solo dentro del mismo año; con `tipo_evento == "prolongado"` no reemplaza nada (cada fecha se dice).
- `m05._date_paraphrased` (125-133): acepta paráfrasis solo con `tipo_evento == "puntual"`.
- **Prompt del guion v5.3** (`PROMPT_GUIONISTA_v5_2.md` → `v5_3`): en `<oficio>`, la línea «Las fechas: la fecha completa una vez, en el cap 2. Después: «ese día», «esa noche», «al día siguiente», «el miércoles».» pasa a: «Las fechas: cada fecha nueva se dice completa la primera vez. Si todo pasa en un día, después alcanza con «ese día», «esa noche», «al día siguiente», «el miércoles»; si el caso dura años, cada salto de tiempo se dice («En 1960…»).». Nada más cambia; md5 nuevo en el reporte.
- **Prompt de la ficha v2.2** (`PROMPT_FICHA_v2_1.md` → `v2_2`): «cronologia: los eventos del día en orden, con la fecha y la hora tal como están en el pool» pasa a «cronologia: los eventos en orden, con la fecha que el pool tenga (año, mes o día) y la hora si la hay, tal como están en el pool». Y el conteo de hechos (G, abajo). Nada más.

### 1.2 Umbrales a métrica (G)
- **Compuerta** (`pool_gate.py`, `video_length.gate_*`): el color deja de depender de 150/8/2/10. **Rojo** solo si no hay con qué contar: `datos < 40` **o** `personas con nombre < 2` **o** `eventos con fecha < 3`. **Amarillo**: alguna de las cuatro medidas de hoy por debajo de su umbral (se muestran todas, con el valor). **Verde**: todas por encima. El amarillo **ya no acorta el video**: `gate_yellow_max_beats` y la línea de rango de beats pasan a informativas (la escaleta sigue diciendo 7–14).
- `research_v3`: `MIN_DOC_CHARS` 3000 → 800; `EVENT_CHECK_CHARS` 5000 → los primeros 20.000 (un informe oficial tiene diez páginas de portada); `MIN_FUENTES`/`MAX_FUENTES` no cambian. Conteo (`_count_re`, `count_value`, ~1235/1499/1743): piso 1.000 → **10** (Ycuá tiene ~400 muertos, un asilo tiene decenas); `POP_BAND`/`CANON_RATIO` se quedan (son relativas). `FOCUS_DENSITY` → métrica (se anota, no descarta).
- `OFFICIAL_TIPOS` (1213): si el pool no tiene ningún documento de esos tipos, el «oficial» puede ser `academico` o `libro` con el rango más alto (`_doc_rank`), y la cifra lleva `oficial_por_defecto: true` para que la voz diga «según <fuente>» (ya existe `sin_oficial`; es la misma línea).
- **Ficha v2.2** (prompt): «hechos (60 a 80)» → «hechos: entre 40 y 80 según lo que el pool dé (nivel 1 entre 10 y 20); con un pool chico, menos hechos buenos valen más que relleno»; «citas: las mejores 15 a 25» → «las mejores 10 a 25»; «escenas (8 a 15)» → «(6 a 15)». Son los mismos conteos con piso más bajo; no es una regla nueva.
- `m01b_narrator` 58-60 / `m01d` 31-39: las bandas de **caracteres** por rol se derivan de `video_length` (palabras × 6); «cap corto» pasa a aviso, no mueve párrafos.
- `m01a_skeleton` 936-950 (caps 6 y 7 con dato en pantalla obligado, «roba» de otro cap): se quita el robo; si no hay dato, no hay pantalla en ese cap.

### 1.3 El intent sale de la escaleta (H)
- `m01a_escaleta.caps_view` (812-822) y `m01a_skeleton.DEFAULT_INTENT_BY_CAP` (99-107): el `narrative_intent` de cada cap se deriva de la **función de sus beats**: gancho → `hook`; planteo → `setup`; escalada/giro → `rising`; pico → `shock`; respiro/consecuencia → `consequences`; revelacion → `resolution`; cierre → `outro`. Si un cap mezcla, manda el beat de mayor intensidad; el cap 1 es siempre `hook` y el 7 siempre `outro`. `DEFAULT_INTENT_BY_CAP` queda como fallback cuando no hay escaleta (camino viejo).
- `tts_tags` (23-26, 54-55, 64) y `render_engine`: leen el intent real del cap. El contrato de 7 caps no cambia en nada más.
- «Un hecho, una cifra» (`m01a_escaleta` 316-334, `m01a_skeleton` 843-875): un valor con rango («entre 70 y 80 toneladas», «200 a 10.000») es un valor válido, no «otra cifra del mismo conteo».

### 1.4 Los idiomas del caso (I)
- **Perfil**: `idiomas_research` (lista; el local siempre; inglés solo si el perfil dice que el caso tiene cobertura internacional en inglés; español siempre al final para el pool). Hoy el prompt R1 dice «Buscá en INGLÉS y en {lugar}» (~112): pasa a «Buscá en {idiomas_research}». `MAX_DESCARGAS_OK` por idioma sigue (F20).
- `_doc_rank` (1350): `.gov` → `(^|\.)(gov|gob|gouv|gc|go)\.` o terminación `.gov`; `Accept-Language` (601) se arma con `idiomas_research`.
- `detect_lang` (450-459): por alfabeto primero (cirílico → ru, griego → el, árabe → ar, hebreo → he, CJK → cjk) y, en latín, stopwords de es/en/fr/it/de/pt (seis listas de 25 palabras; es lo que hay hoy más de/pt). `_TAIL_HEAD` (557): suma «notas», «bibliografía», «referencias», «note», «bibliografia», «anmerkungen», «literatur», «примечания», «литература».
- Prompt R1/R3 (112-131): «FOIA» → «archivos desclasificados o solicitudes de acceso a la información»; «prensa local de los días del evento (la primera semana)» → «prensa local de la época del evento».
- Lo de verify_quotes (35-36, 40) ya está muerto; no se toca.

### 1.5 Nada más
Cero reglas de estilo. Cero juez LLM. Cero cambios en imágenes/voz/gfx/contrato de 7 caps. Los prompts cambian **solo** en las líneas dichas en 1.1 y 1.2 (guion v5.3, ficha v2.2); escaleta y columna no cambian.

## 2. Corrida (después de tests y md5)
**Kyshtym completo, desde la semilla**, con todo F21–F23: perfil nuevo → research v3 (ruso + inglés + español, `nombre_en_documento`) → compuerta → ficha v2.2 (Sol) → escaleta v2.1/f22-2 sin columna (Sol) → guion v5.3 (Fable). Tope **US$ 6.00** (research ≤ 3.50, ficha 0.60, escaleta 0.40, guion 1.20). Respaldos: pool actual como `00_pool_v3_f22.json`, perfil como `_perfil_f22.json`.
Lo que importa:
1. Compuerta: color y las cuatro medidas; cuántos eventos con fecha de mes/año entran ahora.
2. Osetrov, Komarov, Serov con cita **verificada** gracias a `autor_en_documento` (o por qué no).
3. Ítems rescatados por el rango de años (1976, 1997, 2000s) y ninguno descartado por «contaminación» que sea del caso.
4. Intents por cap de la escaleta nueva vs los fijos.
5. El guion: palabras, bloqueantes, citas, personas por cap, fechas literales por cap (métrica), y **ninguna frase de tráiler en el gancho** (f22-2).
Salidas en `lab/hyperframes/f23/`: `POOL_GATE.md`, `FICHA_kyshtym.md`, `ESCALETA_kyshtym.md`, `NARRACION_kyshtym_f23.md`, prompts con md5, `costos_f23.json`, `compara_f23.html` (F22d | F23 por cap).

## 3. Tests (sin red)
- Perfil con `anio_inicio/fin/tipo_evento`; sin ellos, fallback = `anio_evento`.
- Descarte por año: 1930 fuera con inicio 1957; 1997 dentro; «contaminación» no toca nada posterior.
- Compuerta: pool de Orleans y Ycuá siguen verdes; un pool sintético con 45 datos / 2 personas / 3 eventos-mes → amarillo, no rojo; con 30 datos → rojo. Amarillo no cambia el rango de beats.
- `is_hard`/`used_in` con fecha de mes y de año. `gate_eventos_fecha` cuenta AAAA-MM.
- `replace_repeated_dates`: con «puntual» reemplaza con el día de semana correcto calculado (Vajont 9/10/1963 → miércoles); con «prolongado» no toca.
- `narrative_intent` desde beats: 7 caps de la escaleta de Kyshtym F22d → secuencia esperada; sin escaleta → defaults. `tts_tags` pone golpes en un cap 2 `rising`.
- Rango como valor válido en «un hecho, una cifra».
- `detect_lang`: ruso → ru; alemán → de; portugués → pt; español → es.
- md5 de guion v5.3 y ficha v2.2 contra los archivos del handoff; escaleta y columna sin cambio.
- Suite verde + las 5 previas; dorado v3 (si cambia, solo por las líneas de 1.1).

## 4. Frenos
- Cero chequeos nuevos. Todo lo de §1 borra, baja un piso, deriva de datos o mueve a métrica.
- Prompts solo en las líneas dichas; se pegan literales; md5.
- Sin merge; no commitear `.env`, `config.py`, `lab/_gpt_probe_analista/`.
- Tope US$ 6.00; pasado, PARADA donde esté.
- Actualizar `lab/ESTADO_SESION.md`.

## 5. Reporte `lab/hyperframes/f23/F23_REPORT.md`
1. Tabla: cada ítem de §1 → hecho / no hecho / desvío (con motivo).
2. Compuerta antes (F22) | después, con las cuatro medidas.
3. Los cinco puntos de §2 con números y nombres.
4. Diff línea a línea de los dos prompts.
5. Costo por paso. Veredicto íntegro del revisor-handoff.

## 6. PARADA
Commit + reporte → PARADA. El analista lee el guion, revisa el diff y, si Kyshtym da ≥ 8 sin tocar nada, escribe F24: dos temas nuevos del inbox, de la semilla al guion, sin tocar código. Esa es la prueba de que la fase 1 está verde.
