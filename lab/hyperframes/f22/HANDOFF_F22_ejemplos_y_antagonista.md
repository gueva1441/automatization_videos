# HANDOFF F22 — Familias C + E de la auditoría: ejemplos de un caso inventado en los cuatro prompts, antagonista persona / institución / ninguno de punta a punta, y el nombre como lo escribe el documento

Analista · 2026-10-24 · Para CC (misma sesión). Base: `8be0ea9` (rama `f11-guion-v4`). Dos corridas al final (Ycuá y Kyshtym desde la ficha), **tope total US$ 3.00**. **PARADA al terminar.**

Archivos que vienen con este handoff, en `lab/hyperframes/f22/` (md5 en §6):
`CASO_EJEMPLO_cardal.md` · `PROMPT_FICHA_v2_1.md` · `PROMPT_COLUMNA_v1_1.md` · `PROMPT_ESCALETA_v2_1.md` · `PROMPT_GUIONISTA_v5_2.md`.

## 0. Por qué
- **C.** Los cuatro prompts (ficha, columna, escaleta, guion) tienen ejemplos de Orleans/Ycuá con hechos reales: ids (Q184, D192…), cifras («517», «398 dólares», «trescientos veintisiete muertos»), nombres (Reed, Pearl Bland, los Paiva). El modelo copia lo que ve: en F16 y F18 escribió ids del ejemplo que no existen en el tema (→ «dato_central no existe», regeneración gastada) y una cifra copiada dispara el bloqueante (a). Además el prompt R3 del research dice «un preso de Templeman III» como ejemplo de autor anónimo para **cada** documento de cualquier tema.
- **E.** El antagonista es «una persona con apellido» en toda la cadena: R3 lo pide persona; la columna no lo decide; la escaleta lo exige (F19 aceptó institución solo con nombre literal, sin variantes); `m01d` lo borra de `personajes` si no es P##; `guion_v3_reglas.antagonist_problems`/`_ANON_VOICE` exigen que suene un apellido. Kyshtym (el Ministerio / Mayak) paró ahí en F18; Vajont o un manicomio van a parar igual.
- **Nombre como lo escribe el documento** (resto de F21): Osetrov, Komarov y Serov quedan con cita «parcial» porque el modelo devolvió «V.M. Osetrov» y el documento dice «Осетров». La verificación no puede adivinar la transliteración; el modelo, que leyó el documento, sí puede decir cómo está escrito.

Esta tanda cambia **prompts y esquemas**. Cero chequeos nuevos de estilo; los únicos cambios en chequeos son los que dicen cómo se evalúa el antagonista (§1.2) y el nombre en documento (§1.3).

## 1. Cambios

### 1.1 Los cuatro prompts (C)
Un solo caso inventado, «Puerto Cardal, 1968» (`CASO_EJEMPLO_cardal.md`), en los cuatro. Cada archivo dice arriba **qué cambia y qué no**; CC lo pega literal desde `## SISTEMA` y verifica md5.
- `ficha_caso.system()` ← `PROMPT_FICHA_v2_1.md`. `PROMPT_VERSION = "f22-1"`.
- `m01a_columna` SYSTEM ← `PROMPT_COLUMNA_v1_1.md`. `PROMPT_VERSION = "f22-1"`. El `to_markdown` de la columna agrega la línea `QUIÉN DECIDE: …` entre HUMANO y PICO.
- `m01a_escaleta.SYSTEM_V2` ← `PROMPT_ESCALETA_v2_1.md`. `PROMPT_VERSION` de la escaleta con ficha: `f22-1`. **Sin ficha (v1): byte-idéntica**, no se toca.
- `guion_v4.system()` ← `PROMPT_GUIONISTA_v5_2.md` (versión `v5.2`).
- **Research R3** (`research_v3.py` ~1011): el ejemplo de autor anónimo «un preso de Templeman III» pasa a «la descripción que da el texto (por ejemplo, el rol: «una vecina», «un operario»)». `seed_vocabulario` (~1972-1983): los ejemplos «en una cárcel: preso, guardia, oficial» / «sheriff, el ministerio, el dueño» pasan a ejemplos de **tres** tipos de caso distintos en una línea: «(un incendio: cliente, cajera, bombero · una planta: operario, ingeniero, evacuado · una cárcel: preso, guardia)» y «(el dueño · el ministerio · el sheriff)». Los ejemplos JSON con `"anio": 2006, "idioma": "en"` (123, 198, 331) pasan a `"anio": 0, "idioma": "xx"`. `seed_profile` (2020): «inglés (Nueva Orleans, EE. UU.)» → «el idioma del lugar del caso».
- **Mensajes de feedback al modelo** con nombres de Orleans (`m05_narrative` 555/559/627/633: «Interestatal 10», «la celda», «sheriff Marlin N. Gusman»; `guion_v3_reglas` 449 «Nueva Orleans, agosto de 2005.», 257 «ese domingo»): sin nombres propios; el ancla modelo se arma con el lugar y el año **del seed actual**; «ese domingo» → «ese día».
- Los prompts de la escaleta **v1** (208-240) no se tocan (camino sin ficha).

### 1.2 Antagonista persona / institución / ninguno (E)
Un solo contrato, de punta a punta:
`antagonista = {"tipo": "persona"|"institucion"|"ninguno", "id": "P##" (solo persona), "nombre": str, "por_que": str}`
- **Ficha**: `personas` admite instituciones con rol institucional (ya pasaba; ahora el prompt lo dice). El chequeo de la ficha: una persona con rol institucional no pasa por `es_persona`, pero sí tiene que estar nombrada en el texto de sus ids (como cualquier persona).
- **Columna**: esquema con `antagonista` (§ PROMPT_COLUMNA_v1_1 CHEQUEO). Persona → está en la ficha (`persona_de`); institución → `nombre` o una de sus `variantes` en `personas` de la ficha con rol institucional, **o** literal en ≥ 2 hechos (F19 + variantes); ninguno → `por_que` no vacío. Una regeneración si falla, como hoy.
- **Escaleta v2**: mismo esquema y misma evaluación (`institucion_de_la_ficha` acepta variantes; `tipo: ninguno` no se rechaza si trae `por_que`). Con columna, el usuario ya trae el antagonista de la columna; métrica informativa «antagonista escaleta = antagonista columna».
- **`m01d_particion`**: `personajes` conserva al antagonista con su `tipo` (persona con P##; institución con `nombre`); no desaparece. `entra_en_cap` usa `nombres.nombra`.
- **`guion_v3_reglas.antagonist_problems` y `_ANON_VOICE`**: se evalúan **solo** si `tipo == "persona"`. Con institución: métrica informativa «la institución se nombra en N caps» (busca `nombre` y variantes con `nombres.menciona`). Con ninguno: nada.
- **`guion_v4`**: `mark()`/`data_line` no cambian. `_is_human` no cambia.
- **Métricas** (escaleta y guion): `antagonista_tipo`, `antagonista_caps`.

### 1.3 El nombre como lo escribe el documento (cierre de A)
- **Esquema R3**: `personajes[].nombre_en_documento` y `citas[].autor_en_documento`: «el nombre exactamente como aparece en ESTE texto, en su alfabeto; vacío si el texto no lo nombra». Una línea en la regla 6 y en la 7 del prompt R3. El modelo ya devuelve `nombre` en latín; esto agrega cómo lo vio.
- **`verify_pool`** (`autor_cerca`): busca el apellido de `autor` **o** cualquier parte de `autor_en_documento` (con `nombres.menciona`, en el alfabeto que sea). Igual en `validate` de personajes (R3): «el apellido está en el documento» acepta `nombre_en_documento`.
- **`presence_v3`** y `_names_in`: suman `nombre_en_documento` a los términos de búsqueda.
- El pool de Kyshtym en disco no tiene el campo; **esta tanda no rehace el research** (es F23). Test con un documento ruso de Kyshtym ya bajado: una cita de Osetrov con `autor_en_documento: "Осетров"` → verificada.

### 1.4 Nada más
No se tocan umbrales, compuerta, `video_length`, «eventos del día», intents del skeleton (F23). No se agregan reglas de estilo. `m03*`, `gfx_*`, voz: no.

## 2. Corridas (después de tests y md5)
| tema | desde | pasos | tope |
|---|---|---|---|
| **Ycuá** (`f8s1-ycua-bolanos`) | ficha v2 de F15b existente (no se rehace) | columna v1.1 → escaleta v2.1 → guion v5.2 | US$ 1.00 |
| **Kyshtym** (`f18-kyshtym-mayak`) | **ficha nueva** desde el pool actual (el de F21c, con Osetrov, Komarov, Serov, Ladeyshchikova como personas) | ficha v2.1 → columna v1.1 → escaleta v2.1 → guion v5.2 | US$ 2.00 |
- Ycuá es la referencia: F17 dio 8 con los prompts viejos. Lo que importa: que no empeore y que **ningún nombre, cifra ni id del ejemplo de Puerto Cardal aparezca** en columna, escaleta ni guion (test determinista sobre las salidas: lista de palabras del caso inventado → cero coincidencias).
- Kyshtym: la primera vez que llega a guion. Antagonista esperado: institución. Si la escaleta o el guion paran con bloqueantes después de su regeneración: PARADA con el crudo guardado; no se parchea.
- Respaldar lo que se pisa: `01a_columna`, `01a_escaleta`, `01b_*` de Ycuá como `*_f17.json`; la ficha de Kyshtym de F18 como `ficha_caso_f18.json`.
- Salidas en `lab/hyperframes/f22/`: `FICHA_kyshtym.md`, `COLUMNA_{ycua,kyshtym}.md`, `ESCALETA_{…}.md`, `NARRACION_{ycua,kyshtym}_f22.md`, prompts con md5, `costos_f22.json`, `compara_f22.html` (Ycuá F17 | F22 por cap; Kyshtym solo F22, con la columna arriba).

## 3. Tests (sin red)
- md5 de los cuatro bloques `## SISTEMA` contra los archivos del handoff; v1 de la escaleta byte-idéntica.
- Esquemas: columna y escaleta aceptan `antagonista.tipo` en los tres valores; `ninguno` sin `por_que` falla; institución con variante de la ficha pasa; institución que no está en la ficha falla.
- `m01d`: antagonista institución queda en `personajes` con `tipo`.
- `antagonist_problems` y `_ANON_VOICE` no evalúan con institución; sí con persona (Orleans/Gusman como antes).
- `verify_pool` con `autor_en_documento` cirílico → verificada; sin el campo, igual que hoy.
- «Cero Cardal»: función que, dada una salida (columna/escaleta/guion), busca las palabras del caso inventado (Cardal, Soto, Bascuñán, Quiroga, Marín, Alborada, Faros y Balizas, querosén, telegrama) → en Orleans F7c-3 y Ycuá F17 da 0 (control); se usa en §2.
- Suites verdes + las 5 previas; dorado de v3 verde.

## 4. Frenos
- Cero reglas de estilo nuevas. Cero cambios de umbrales.
- Los prompts se pegan **literales**; cualquier desvío se declara con la línea y el motivo.
- Sin merge; no commitear `.env`, `config.py` ni `lab/_gpt_probe_analista/`.
- Tope US$ 3.00; pasado, PARADA donde esté.
- Actualizar `lab/ESTADO_SESION.md`.

## 5. Reporte `lab/hyperframes/f22/F22_REPORT.md`
1. md5 de los cinco archivos del handoff vs lo que quedó en código. Diff línea a línea de cada prompt (viejo → nuevo), para que el analista confirme que solo cambió lo dicho.
2. Ycuá: tabla F17 | F22 (palabras, personas con nombre por cap, bloqueantes, citas, escenas usadas, antagonista). Kyshtym: la columna tal cual, antagonista elegido y por qué, bloqueantes por paso, lo que paró si paró.
3. «Cero Cardal» en todas las salidas.
4. Costo por paso. Veredicto íntegro del revisor-handoff.

## 6. md5 de los archivos de este handoff
| archivo | md5 |
|---|---|
| CASO_EJEMPLO_cardal.md | 7068cef5063db1de5a015c50891204e4 |
| PROMPT_FICHA_v2_1.md | 168358d182f9831dedc1bd21ba910540 |
| PROMPT_COLUMNA_v1_1.md | af1d5f4150b4f4fc54a0c603e7f65cbb |
| PROMPT_ESCALETA_v2_1.md | 601aa76a77ce2c1dd9bd861a3bba6a02 |
| PROMPT_GUIONISTA_v5_2.md | 9d80720a0d6770c7cb4220f2ba0f4217 |
