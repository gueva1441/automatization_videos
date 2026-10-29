# F51b — el canon separa el aspecto fijo del estado (+ chascada: estilo C sin año) · PARADA

Handoff `lab/hyperframes/f51b/HANDOFF_F51b_aspecto_fijo_y_estado.md`, **md5 `f008374d84fe192ddc72a44b568b0762`** (coincide con el del pedido).
- Rama `f11-guion-v4`. Tope US$ 1,00; **gasto real US$ 0,3919**, 1 llamada a Opus y ningún reintento. Sin fal.
- No se escribió `03_visual.json`: su hora sigue siendo 01:35:38, de antes de la tanda. No se tocaron `name_matching`, el corte Veo, `anio_final` ni `cost_tracker`.
- No se agregó ninguna regla al pedido; solo van las 2 líneas del handoff.

## Qué pasó, en llano
- El pedido del canon dice ahora que `appearance` lleva solo los rasgos fijos, y que el estado va en un campo nuevo, `condition_by_period`. Ese campo no se pega en la foto.
- Opus rehízo el canon de Wittenoom en una llamada (US$ 0,39).
- En las 4 fotos de las manchas (2/9, 4/11, 4/12, 5/8), el aspecto de las familias españolas ya no trae el polvo rojo, que pasó a `condition_by_period`. También perdió «slim to medium builds».
- **Opus no separó del todo:** quedan «sun-weathered» en 2 grupos y «tanned» en 1. El handoff dice que eso no se parchea: se reporta y **decide Omar**.
- **Además, Opus cambió los ids de 8 de los 12 grupos.** Hay 20 fotos del `03_visual.json` de hoy que apuntan a ids que ya no existen, y en esas fotos esos grupos no pegarían aspecto hasta que F51d rehaga las fotos.

## Commits
| etapa | commit |
|---|---|
| 0 | `a5842ba` |
| 1 | `d2b443c` |
| 2 | `7f8fea2` |
| reporte, ESTADO y logs de verificación | este commit |

## Etapa 0 — DECISIONES
- md5 del handoff: `f008374d84fe192ddc72a44b568b0762`.
- La línea se agregó al final con CRLF. Antes, el código comprobó que está dentro del handoff y que no estaba ya en DECISIONES.
- `tail -1 DECISIONES.md`:
```
- 2026-10-29 03:52 · **F51b:** en el pedido del canon, `people_groups[].appearance` pasa a ser solo los rasgos fijos según el origen (piel, pelo, ojos, cara, contextura); el estado documentado (polvo, suciedad, bronceado, heridas, enfermedad, desgaste) va a un campo nuevo, `condition_by_period` (years + condition), que el código no pega en la foto; Wittenoom rehace su canon con Opus (tope US$ 1); chascada: el estilo C sin año va sin «taken in» · Omar · F51b
```
- `lab/TOPE_TANDA.json` = 1,00 desde 03:59:18 (fuera de git).

## Etapa 1 — código y tests (US$ 0)
**El pedido** (`researcher_steps/step_4e_visual_canon.py`, `TEXTO_1_PEOPLE_GROUPS`):
- La línea vieja de `appearance` se reemplazó por las 2 del handoff. Un script las sacó del bloque del handoff y comprobó que la vieja estaba una sola vez.
- El resto del texto quedó igual, incluida la frase final.
- Diff del texto del pedido, viejo → nuevo (`git diff a5842ba d2b443c -- researcher_steps/step_4e_visual_canon.py`):
```diff
diff --git a/researcher_steps/step_4e_visual_canon.py b/researcher_steps/step_4e_visual_canon.py
index d7c7a0a..9ccb3df 100644
--- a/researcher_steps/step_4e_visual_canon.py
+++ b/researcher_steps/step_4e_visual_canon.py
@@ -743,13 +743,15 @@ def extract_visual_canon(
 #  F50 A — CANON DESDE LA FICHA (antes de m03; reemplaza al 4e del research)
 # ═══════════════════════════════════════════════════════════════
 
-# los textos del lab (F46b texto 1; F48 TEXTO_S5); F50d A: where_when con todos los años y clothing_by_period
+# los textos del lab (F46b texto 1; F48 TEXTO_S5); F50d A: where_when con todos los años y clothing_by_period;
+# F51b: appearance = solo los rasgos fijos, y el estado documentado va a condition_by_period (nadie lo pega en la foto)
 TEXTO_1_PEOPLE_GROUPS = """═══ BLOQUE EXTRA: people_groups ═══
 Lista de los grupos de personas que el material documenta en este caso (hechos, cronología, escenas y citas de arriba). Por grupo, un objeto:
 - id: corto, snake_case, en inglés (p. ej. "spanish_migrant_families")
 - who: quiénes son y su origen documentado (EN, una frase)
 - where_when: dónde y en qué años aparecen, todos los años en que el material los muestra, también décadas después (EN, una frase)
-- appearance: cómo se ven físicamente según su origen documentado y su época: tono de piel, color y tipo de pelo, rasgos, contextura típica de su trabajo (EN, una frase)
+- appearance: solo los rasgos físicos fijos de la persona según su origen documentado: tono de piel, color y tipo de pelo, color de ojos, rasgos de la cara y contextura (EN, una frase). Nada que cambie según dónde estén, qué hagan o qué les pase: eso va en condition_by_period
+- condition_by_period: una entrada por cada tramo de años en que el material documenta un estado físico de ese grupo (polvo, suciedad, bronceado, heridas, enfermedad, desgaste); years "AAAA-AAAA" y condition (EN, una frase). Si el material no documenta ningún estado, lista vacía
 - clothing_by_period: una entrada por cada tramo de años en que el material muestra a ese grupo; years "AAAA-AAAA" y clothing: ropa, peinado y accesorios de ESE grupo en ESE tramo, ese clima y esa clase social (EN, una frase)
 Sin nombres propios de personas. Solo grupos que el material documenta; si el material no dice el origen de un grupo, no lo inventes: dejá appearance vacío."""
 TEXTO_S5 = ("Personajes del material (rol · lugar · años; sin nombres). Que ningún grupo que aparezca acá quede fuera de "
```

**`condition_by_period` sobrevive la limpieza:**
- `extract_visual_canon` deja pasar cada grupo entero (`out["people_groups"] = [g for g … if g.get("id")]`).
- `CANON_KEYS` de `fase1_5` ya tenía `people_groups`, y `asegurar_canon` lo guarda entero en topics_db y en `05_visual_canon.json`. No hizo falta tocarlo.
- Lo comprueban un test (`test_f51b_condition_by_period_sobrevive_la_limpieza`) y el canon real: `canon_f51b.json` trae `condition_by_period` en los 12 grupos.
- Nadie lo pega: `armar` usa solo `appearance`, y `m03_expediente.bloque` (l. 203–208) pega `who`, `where_when`, `appearance` y `clothing_by_period`. Hay un test para esto: `test_f51b_el_armado_no_pega_condition_by_period`.

**Chascada:**
- En `armar`, `estilo` = `ESTILO_C.format(anio=anio) if anio else ESTILO_C.replace(" taken in {anio}", "")`.
- Sin año da «A grainy 35mm documentary photograph, with muted colors and slight underexposure, in a dark-history realist style.».
- Con año, el texto es igual que en F51a.

**Contrato F51a:**
- `lab/hyperframes/f51a/contrato.py` leía los grupos del topic vivo. Después de la etapa 2, el aspecto de las familias cambia, y el contrato daría distinto aunque el armado esté bien.
- Por eso ahora toma los grupos del canon con el que se armó F50h, `lab/hyperframes/f50f/canon_f50f.json`. Antes de la etapa 2, CC comprobó que ese canon era idéntico al `people_groups` del topic y al de `05_visual_canon.json`.
- Con eso sigue dando 20/20, antes y después de la etapa 2.

**Tests:**
- `test_module_f51b.py` (nuevo, 5 tests):
  - el pedido trae las 2 líneas nuevas y no la vieja, y la frase final queda igual;
  - `condition_by_period` sobrevive la limpieza;
  - con `anio=""`, el estilo no dice «taken in», y con año queda igual que en F51a;
  - el armado no pega `condition_by_period`;
  - el contrato F51a sigue verde.
- `test_module_f50a.py` no fija el texto viejo (compara contra la constante), así que no se tocó.
- Corrida puntual: `test_module_f51b f51a f50a f50d f50f f50g f50b f50c f8` → `97 passed`.

**Marca en seco** (`s4e.marca_canon` con la ficha de Wittenoom; sin llamar a nadie):
```
marca vieja a08c790ceac3a982d0cdca904424371f
marca nueva 4828d0e69b6edf3d58954849767ec1fd · distinta: True
```

**Stickers:** se actualizaron el de `step_4e_visual_canon.py` (zona `research`) y el de `m03_imagenes_v3.py` (zona `fase2a`). Mapa: `mapa --check: 157 archivos de producción · 0 fallas`.

## Etapa 2 — canon de Wittenoom con Opus
**Corrida:** `python -u lab/hyperframes/f51b/canon_f51b.py`.
- Antes de llamar, guarda el respaldo en `lab/hyperframes/f51b/antes/` (`topic_wittenoom.json` y `05_visual_canon.json`).
- Después llama a `fase1_5.asegurar_canon` y solo reintenta si sale una Parada con un CanonError detrás.
- **Freno del tope:** `claude_helpers._post` va envuelto y no deja salir una tercera respuesta cobrada. Hace falta porque `call_json` vuelve a llamar solo cuando el JSON viene roto (hasta 3 veces, ~0,34 cada una), y eso podría pasar el tope sin que haya CanonError.
- Salida (`corrida_f51b.json`):
```
{
 "marca_antes": "a08c790ceac3a982d0cdca904424371f",
 "marca_despues": "4828d0e69b6edf3d58954849767ec1fd",
 "intentos": [
  "ok"
 ],
 "llamadas": [
  {
   "model": "claude-opus-5-5",
   "usage": {
    "input_tokens": 15105,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0,
    "cache_creation": {
     "ephemeral_5m_input_tokens": 0,
     "ephemeral_1h_input_tokens": 0
    },
    "output_tokens": 16572,
    "service_tier": "standard",
    "inference_geo": "global",
    "speed": "standard",
    "output_tokens_details": {
     "thinking_tokens": 5441
    }
   },
   "stop_reason": "end_turn"
  }
 ],
 "costo_01_v3_costos": [
  {
   "paso": "canon",
   "usd": 0.3919,
   "segundos": 151.1
  }
 ],
 "log": [
  "  [canon] desde la ficha (4828d0e6): 12 people_groups, 22 personas, 0 props"
 ]
}
```
- **Costo real:**
  - US$ 0,3919, registrado en `01_v3_costos` (paso «canon», 151,1 s).
  - En `cost_history` hay una entrada de 2026-10-29T03:59:21: `Anthropic claude-opus-5-5`, 0,39186, 15105 tokens de entrada y 16572 de salida. Incluye 5441 de thinking, según el `usage`.
  - En total, 0,39 de 1,00.
- `asegurar_canon` escribió topics_db y `05_visual_canon.json` (04:01:52), como en producción. `03_visual.json` no se tocó.

**`CANON_F51b.md`:** lo generó `lab/hyperframes/f51b/tabla_f51b.py`, que escribió un subagente en paralelo mientras corría Opus. CC lo corrió con el canon nuevo y lo leyó.
- Tiene la tabla grupo por grupo con el estado igual, cambia, nuevo o desaparece. «Cambia» lo agregó el subagente: sin esa marca, un grupo con otro texto salía «igual».
- Tiene el resto del canon, viejo → nuevo: `era_visual_canon`, con sus claves y `periods`, `anachronism_blocklist`, `documented_people`, `documented_props` y `central_subject`.
- Tiene las 4 fotos armadas en memoria al lado del C′ de F50i.
- El subagente lo probó con el canon viejo como «nuevo»: todo dio «igual», y las 4 fotos armadas dieron byte a byte el C de F50i (4/4).

### Lectura de CC (no es la comparación del analista)
**Grupos (12 → 12):**
- Quedaron 4 ids iguales: `mine_and_mill_workers`, `spanish_migrant_families`, `australian_politicians` y `banjima_traditional_owners`.
- Desaparecieron 8: `prospectors_mine_owners`, `company_managers`, `mine_and_health_officials`, `town_children`, `union_and_arbitration`, `victims_advocates_and_lawyers`, `international_un_official` y `airport_police`.
- Hay 8 nuevos: `company_owners_and_managers`, `government_mines_and_health_officials`, `wittenoom_town_residents`, `unions_and_labour_arbitration`, `asbestos_victims_advocates_and_lawyers`, `international_human_rights_observers`, `environmental_assessors` y `australian_airport_police`.
- Varios son el mismo grupo con otro id. Por ejemplo, `union_and_arbitration` pasa a `unions_and_labour_arbitration`, y `airport_police` a `australian_airport_police`.

**Estado que quedó en `appearance`** (leído a mano, sin lista de palabras):

| grupo | appearance nuevo | lo que queda |
|---|---|---|
| `company_owners_and_managers` | «Adult Anglo-Australian men of European descent with fair to sun-weathered skin and short hair.» | «sun-weathered» |
| `government_mines_and_health_officials` | «Adult Australian men of European descent with fair to sun-weathered skin and short hair.» | «sun-weathered» |
| `unions_and_labour_arbitration` | «Adult Australian men of European descent with fair to tanned skin.» | «tanned» |

- Los otros 4 grupos con aspecto no traen estado: `mine_and_mill_workers`, `spanish_migrant_families`, `australian_politicians` y `banjima_traditional_owners`.
- El polvo, la enfermedad y el desgaste están en `condition_by_period`: 7 grupos tienen alguna entrada y 5 tienen la lista vacía (`company_owners_and_managers`, `australian_politicians`, `international_human_rights_observers`, `environmental_assessors` y `australian_airport_police`).

**`appearance` vacío: 5 de 12, antes eran 2 de 12.**
- Los 5: `wittenoom_town_residents`, `asbestos_victims_advocates_and_lawyers`, `international_human_rights_observers`, `environmental_assessors` y `australian_airport_police`.
- En el canon viejo, los niños del pueblo y las víctimas sí tenían aspecto.

**Las 4 fotos de las manchas:**
- En las 4, `spanish_migrant_families` conserva el id, y el aspecto nuevo no trae polvo.
- Contra el C′ de F50i, cambia solo la oración del aspecto: «Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds.» pasa a «Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes.». Se perdió la contextura.
- En la 5/8, `airport_police` ya no está en el canon: esa foto pegaría solo el aspecto de las familias. Es lo mismo que hacía C′, porque el aspecto de `airport_police` estaba vacío.

**Ids viejos en `03_visual.json`:**
- 20 de las 96 fotos tienen en `people_group` algún id que ya no existe: `victims_advocates_and_lawyers` ×6, `town_children` ×3, `mine_and_health_officials` ×3, `company_managers` ×3, `union_and_arbitration` ×3, `airport_police` ×2, `prospectors_mine_owners` ×1 e `international_un_official` ×1.
- Con `armar`, esos grupos no pegan nada: un id desconocido no agrega aspecto.
- Cuando F51d vuelva a correr m03, Opus va a elegir los `people_group` contra el canon nuevo.

**Tramos de época:**
- Pasaron de 1937-1945 · 1946-1966 · 1967-1992 · 1993-2026 a 1937-1949 · 1950-1966 · 1967-2007 · 2008-2026.
- Las 96 fotos siguen cayendo en algún tramo (96/96, con `m03_visual._tramo`), lo mismo que el criterio de F50f.

**El resto del canon:** Opus reescribió todos los textos de `era_visual_canon`, el `appearance_canon` de las personas y la lista de anacronismos. El diff está entero en `CANON_F51b.md`. `documented_props` sigue vacío (0 → 0).

## Al cerrar — suites, candado ch02 y contrato F51a
- Contrato F51a después de la etapa 2 (`python lab/hyperframes/f51a/contrato.py`, exit 0): **20/20 byte a byte iguales a PROMPTS_F50h.json → C**.
- Salida de `bash lab/hyperframes/f41/verificar.sh f51b` (logs en `lab/hyperframes/f41/f51b/`):
```
md5: f792f3d483a1fa42daed5f7f0e054f46 *output/ba6c3cac-a091-41c0-8dad-afd2f4364747/_fase2b_work/ch02_segment_only.mp4
rapida: 55 passed, 3 skipped in 3.14s
amplia: 5 failed, 998 passed, 30 skipped, 4 warnings in 65.83s (0:01:05)
FAILED test_module_m03_merge_timing.py::test_c_guarda_de_minimo - AssertionEr...
FAILED test_module_m03_merge_timing.py::test_c_veo_path_y_veo_anchor_intacto
FAILED test_module_gfx_lab.py::test_preview_solo_un_objeto_sobre_la_foto_quieta
FAILED test_module_gfx_lab.py::test_cues_sin_escribir_el_proyecto - Assertion...
FAILED test_module_gfx_lab.py::test_preview_usa_las_plantillas_reales - asser...
```
- La amplia da 998 passed + 5 failed. 4 son las previas conocidas de la cadena.
- La quinta, `gfx_lab::test_preview_solo_un_objeto_sobre_la_foto_quieta`, es un `HTTPError 404` del servidor de preview local corriendo con `-n auto`, la misma familia que la intermitente `test_candado_en_el_preview`. Corrida sola, pasó 2 de 2: `1 passed in 2.57s` y `1 passed in 2.50s`. F51b no toca `gfx_lab`.
- La cuenta: 994 de F51a + 5 de `test_module_f51b.py` = 999 = 998 que pasaron + la intermitente.

## Lo que queda abierto
1. **Decide Omar:** quedó estado en el `appearance` de 3 grupos («sun-weathered» ×2, «tanned» ×1). Según el handoff, no se agregaron reglas al pedido.
2. **Ids de grupo nuevos:** 8 de 12 grupos cambiaron de id y 20 fotos del `03_visual.json` de hoy apuntan a ids viejos. Se resuelve cuando F51d vuelva a correr m03 con el canon nuevo; mientras tanto, esas fotos no pegarían aspecto para esos grupos.
3. **`appearance` vacío en 5 de 12 grupos** (antes 2), entre ellos los residentes y niños del pueblo y las víctimas.
4. **El aspecto de las familias españolas perdió la contextura** («slim to medium builds»), que el pedido nuevo pide.
5. **Varianza de Opus:** con una sola corrida no se puede separar el efecto del pedido nuevo de lo que Opus cambia de una corrida a otra (F50e midió esa varianza). Además de `people_groups`, cambió todo el resto del canon.
6. **`documented_people[].appearance_canon`** puede tener el mismo problema. Por ejemplo, Hancock antes era «weathered by outdoor work» y ahora no. Hoy no se pega en la foto (la lista del handoff).
7. **Uso futuro de `condition_by_period`:** otra variable, la decide Omar (la lista del handoff).
8. **El `03_visual.json` de Wittenoom sigue con el armado viejo y los ids viejos:** eso es F51d.
9. **Contrato F51a:** ahora está fijado a `f50f/canon_f50f.json` (el canon de F50h), no al topic vivo. Así mide solo el armado.
10. **Siguen abiertos de antes:** «Court» (F51c), el corte Veo, `anio_final` y `track_gemini_vision` (F51e). Los scripts de lab de f46 y f46b, que usan `style_head`, también siguen rotos.
11. **Fuera de git y sin tocar:** `diag_234_cap4.py`, `lab/TOPE_TANDA.json` (ahora en 1,00), `lab/hyperframes/f28/a/f28a.log`, la llave y las png de f50h, y los `ENTRADA_ANALISTA_*.md`.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

El código y el alcance cumplen el handoff. El resultado del canon no cumple del todo la intención (separar aspecto fijo de estado), y el propio reporte lo declara como pendiente de decisión de Omar.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | md5 del handoff = f008374d… | OK | `md5sum` da f008374d84fe192ddc72a44b568b0762 |
| 2 | Etapa 0: línea de DECISIONES tal cual, al final | OK | `git diff` de DECISIONES.md: +1 línea 2026-10-29 03:52, texto idéntico al handoff |
| 3 | Etapa 1: las 2 líneas nuevas reemplazan la de `appearance` y el resto queda igual | OK | researcher_steps/step_4e_visual_canon.py: diff de `TEXTO_1_PEOPLE_GROUPS`, textos idénticos al handoff, frase final intacta |
| 4 | `condition_by_period` sobrevive la limpieza y `armar` no lo pega | OK | test_module_f51b.py, dos tests; 13 passed (f51b, f51a, f50a) corridos por mí |
| 5 | Chascada: estilo C sin año va sin «taken in», y con año queda igual | OK | script_engine/m03_imagenes_v3.py:645; test `estilo_sin_anio`; el contrato muestra «taken in 1962» y «1985» sin cambios |
| 6 | Contrato F51a 20/20 sigue verde | OK | `lab/hyperframes/f51a/contrato.py` corrido por mí, exit 0. Se cambió para leer `f50f/canon_f50f.json` en vez del topic vivo: tiene sentido, pero es un archivo extra tocado |
| 7 | Marca nueva distinta de a08c790c | OK | corrida_f51b.json: 4828d0e6… |
| 8 | Etapa 2: respaldo en `antes/`, 1 llamada, tope US$ 1 | OK | `antes/` tiene los 2 archivos; 1 llamada, intentos ["ok"]; 01_v3_costos: US$ 0,3919. El detalle en `cost_history` no lo comprobé a fondo |
| 9 | Escribe topics_db y `05_visual_canon.json` | OK | `05_visual_canon.json` es idéntico a `canon_f51b.json` y trae `people_groups` |
| 10 | CANON_F51b.md con tabla, resto del canon y 4 fotos al lado del C′ | OK | `tabla_f51b.py` regenera el archivo sin diff en git; hay 4 prompts de foto armados |
| 11 | No escribir `03_visual.json` | OK | su fecha sigue en 01:35:38, anterior a la tanda |
| 12 | No tocar name_matching, corte Veo, anio_final ni cost_tracker | OK | `git diff` de la tanda no incluye name_matching ni cost_tracker. No revisé línea por línea si se tocó el corte Veo o `anio_final` dentro de m03 |
| 13 | Ninguna regla nueva y PARADA si Opus no separa bien | OK | solo se agregaron las 2 líneas; el reporte reporta y se detiene |
| 14 | Cierre: suites, candado ch02, ESTADO, REPORT con el veredicto | NO VERIFICABLE | `suite_rapida.log`, `suite_amplia.log` y `onlycap_ch02_nogfx.log` existen en `lab/hyperframes/f41/f51b/`, pero no los corrí. ESTADO se actualiza después de este veredicto. `F51b_REPORT.md` tiene 224 líneas, trae «Lo que queda abierto» y `{{VEREDICTO}}` en la línea 224 |
| 15 | Un commit por etapa con F51b en el mensaje | OK | a5842ba, d2b443c y 7f8fea2 |

Observaciones (resultado del canon):
- Opus no separó del todo. Quedan «sun-weathered» en 2 grupos (`company_owners_and_managers`, `government_mines_and_health_officials`) y «tanned» en `unions_and_labour_arbitration`. El handoff pide reportarlo y que decida Omar. El reporte lo hace.
- 5 grupos quedan con `appearance` vacío: `wittenoom_town_residents`, `asbestos_victims_advocates_and_lawyers`, `international_human_rights_observers`, `environmental_assessors` y `australian_airport_police`. El handoff preveía 2 vacíos. Esos grupos quedan sin aspecto en la foto.
- Opus cambió 8 de los 12 ids. 20 fotos del `03_visual.json` apuntan a ids que ya no existen, y el reporte lo dice. Esas fotos no pegan aspecto hasta F51d.
- El aspecto de `spanish_migrant_families` perdió «slim to medium builds» y la contextura. El pedido sí la incluye entre los rasgos fijos.

Fuera de alcance: ninguno dentro de la tanda. Los modificados `diag_234_cap4.py`, `lab/TOPE_TANDA.json` y `lab/hyperframes/f28/a/f28a.log` ya estaban modificados antes y no los tocó la tanda. `lab/hyperframes/f51a/contrato.py` sí fue editado, con justificación en su docstring.

Riesgos que el contrato no cubre: (1) el canon vivo ya apunta a ids nuevos mientras el `03_visual.json` conserva los viejos, así que cualquier uso de producción antes de F51d queda inconsistente. (2) Un LLM sin reglas nuevas deja 5 de 12 grupos con `appearance` vacío y 3 con rasgos de estado, así que quizá haga falta otra iteración del pedido. (3) `documented_people[].appearance_canon` sigue sin revisarse, como dice la lista del handoff.

### Adenda de CC (después del veredicto)
- **#6, `contrato.py` editado:** es un cambio necesario, no un agregado. Sin él, el contrato de F51a dejaba de dar 20/20 cuando la etapa 2 cambiaba el aspecto de las familias, y el cierre pide que el contrato siga verde. Está declarado en la etapa 1 y en el punto 9 de «Lo que queda abierto».
- **#8, `cost_history`:** CC leyó la entrada con fallback cp1252. `created_at` 2026-10-29T03:59:21, `Anthropic claude-opus-5-5`, US$ 0,39186, 15105 tokens de entrada y 16572 de salida. Es la única entrada del tema desde que arrancó el tope (03:59:18).
- **#12, corte Veo y `anio_final`:** `git diff 79ecc74 HEAD --stat -- script_engine/ researcher_steps/ fase1_5.py` toca solo `step_4e_visual_canon.py` (6 líneas) y `m03_imagenes_v3.py` (4 líneas). En `m03_imagenes_v3.py` cambian dos cosas: la línea `"estilo"` de `armar` y su docstring. `anio_final` y el corte Veo, que está en `m03_visual.py`, no se tocaron.
- **#14, suites:** las corrió `verificar.sh f51b`, y su salida está pegada en «Al cerrar». ch02 `f792f3d4…`; rápida 55 passed; amplia 998 passed + 5 failed: las 4 previas y la intermitente de `gfx_lab`, que corrida sola pasó 2 de 2. El commit del reporte trae también ESTADO.
- **Riesgo 1, uso de producción antes de F51d:** la próxima corrida de m03 sobre Wittenoom vuelve a elegir los `people_group` contra el canon nuevo, así que el desfase entre ids dura solo mientras quede el `03_visual.json` de hoy. Nada lo está usando ahora.
