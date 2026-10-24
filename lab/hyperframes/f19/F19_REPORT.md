# F19 — Kyshtym otra vez: cirílico en el research · REPORTE

2026-10-24 · rama `f11-guion-v4` (desde `29da90c`) · topic `f18-kyshtym-mayak` · corrió sin paradas intermedias. Runner: `f19_corridas.py`; página: `compara_f19.html` (sin API, legible en el teléfono).

## 0. En una línea
**El cirílico funcionó, pero la compuerta dio ROJO y la cadena paró en el research (§2: «Compuerta roja: PARADA»).**
- Los documentos rusos pasaron de aportar 0 ítems a aportar 239, y el pool creció de 175 a 302 ítems.
- La compuerta pide al menos un humano elegible y esta vez hay 0. Lev Tumerman (el humano de F18) sigue en el pool, pero perdió una fuente en inglés y ya no llega al umbral.
- No corrieron ficha, columna, escaleta ni guion. Los tres arreglos de §1 quedaron programados y con tests.
- Gasto: **US$ 0.932 de 5.00.**

## 1. Arreglos (§1 y §2 del handoff: correcciones de forma, sin chequeos nuevos)
1. **Cirílico en el research** (`researcher_steps/research_v3.py`).
   - `seed_profile` pide `nombres_locales`: las formas del lugar y del evento en el alfabeto del idioma local.
   - `place_regex()` arma `place_re` con los nombres latinos como antes (`\b…\b`) más los locales, con lookarounds `(?<!\w)…(?!\w)`. `names_event` y `focus_text` no cambian.
   - **Diferencia con el handoff:**
     - El handoff dice que el perfil lo hace Pro; hoy lo hace Flash (`call_flash_json`). Lo dejé en el mismo paso y el mismo modelo («las genera el mismo paso que hoy genera el perfil»).
     - Los latinos conservan `\b` y no pasan a lookarounds, porque el handoff también pide que Orleans e Ycuá den el mismo `place_re` que antes. Los lookarounds van solo en los locales.
   - Formas que generó para Kyshtym: «Кыштымская авария», «Маяк», «ПО «Маяк»», «Производственное объединение «Маяк»», «Озёрск», «Челябинск-40», «Катастрофа на ПО «Маяк»».
2. **Antagonista persona o institución** (`script_engine/m01a_escaleta.py`, solo con ficha).
   - `SCHEMA_FICHA.antagonista` lleva `tipo` (`persona` o `institucion`), `id` y `nombre`.
   - Una institución existe si su nombre está literal en la ficha: como persona (nombre o variante) o en el texto de 2 o más hechos. El mensaje de rechazo cae en el mismo bloqueante de siempre (`^antagonista .* no es una persona del pool`).
   - **Lectura de formato, declarada:** el artículo de adelante no cuenta («el Ministerio…» está en «al Ministerio…»).
   - **No se filtra por rol institucional:** cualquier persona de la ficha cuenta como fuente, porque «rol institucional» no se puede decidir sin LLM. Lo anoto.
   - Sin ficha, `SCHEMA` y `validate` siguen igual.
3. **Rango de beats en el usuario** (`build_prompt_v2(beats=)`).
   - Cuando hay compuerta, antes de `<tarea>` va «Esta escaleta lleva entre {min} y {max} beats»: verde 7–14, amarillo 7–8, tomado de `_profile`. El sistema v2 queda literal.
   - Sin compuerta, el usuario no cambia: siguen verdes los md5 de F16 y F17.
4. **Citas con traducción** (`researcher_steps/ficha_caso.py`).
   - El esquema de `citas` lleva `traduccion` (opcional), y `texto` dice «la cita en el idioma de su documento, sin traducir». Va como `description` del esquema; el prompt literal del analista no se toca.
   - El chequeo sigue comparando `texto` con el pool.
   - `id_texts` (lo que lee `data_line`) usa la traducción cuando existe. La puse en `id_texts` y no en `data_line`, porque `data_line` recibe el texto ya armado.
   - La sección de la ficha en la escaleta y `FICHA_*.md` muestran la traducción solo si existe.
   - **No se probó con datos:** la ficha no corrió.

**Tests:**
- `test_module_f19.py`, 15 tests, cubre:
  - texto ruso con «Кыштым» nombra el evento; sin ninguna forma, no;
  - Ycuá, Cromañón y Vajont dan el mismo `place_re` que su perfil guardado;
  - Gusman pasa; una institución en ≥ 2 hechos pasa; «la KGB» no; sin ficha, igual que siempre;
  - el rango de beats según la compuerta, y sin compuerta, sin línea;
  - citas con traducción.
- Suite amplia: **692 verdes + las 5 previas**. Incluye el dorado v3, la escaleta sin ficha byte-idéntica y los md5 de F16 y F17.

## 2. Embudo F18 | F19 (por idioma de fuente)
El idioma sale del texto de cada documento: el `idioma` del manifiesto marcaba «en» o «?» a los rusos.

| | F18 | F19 |
|---|---|---|
| documentos propuestos (R1) | 16 | 20 |
| documentos bajados | 11 | 13 |
| documentos que nombran el evento | 6 | 10 |
| ítems del pool | 175 | **302** |
| citas del pool (verificadas) | 14 (13) | 20 (18) |
| personajes del pool | 9 | 7 |
| **ruso** (propuestos · bajados · nombran · aportan · ítems*) | 6 · 5 · 1 · **0 · 0** | 9 · 8 · 8 · **8 · 239** |
| inglés (propuestos · bajados · nombran · aportan · ítems*) | 8 · 6 · 5 · 5 · 199 | 11 · 5 · 2 · 2 · 88 |
| → ficha · columna · escaleta · guion | 106 · 43 · 0 · 0 | — (PARADA) |

\* Ítems por documento: un ítem que está en dos documentos cuenta en los dos.

**Cuánto aportó el cirílico: 8 documentos rusos y 239 ítems, contra 0 en F18.** R4: datos 174, cronología 55, lugares 46, citas 20, personajes 7.

R1 no salió igual que en F18. La caché de R1 es por prompt, y el perfil regenerado trajo otros nombres latinos («Kyshtym Accident», «Urals Nuclear Waste Accident», «PA Mayak»…). Eso cambió las consultas, y salieron 20 fuentes en lugar de 16. Hay dos efectos más:
- el tope de 10 descargas se llenó con los rusos, y 4 fuentes en inglés quedaron sin intentar («ya hay 10 documentos»);
- 3 descargas dieron HTTP 429: F05 (stanford.edu, «USSR: Nuclear accident near Kyshtym in 1957-58»), F08 (zaryagazeta) y F13 (en inglés).

## 3. Compuerta y PARADA
**🔴 ROJO**: datos 174 ✔, citas verificadas 18 ✔, eventos con fecha 20 ✔, **elegibles humano 0 ✖**. Motivo: «sin humano que seguir (pocos testigos elegibles)». Copia en `POOL_GATE.md`.

**Por qué 0:**
- `elegible_humano` pide testigo, no antagonista y 3 o más citas o 3 o más datos propios.
- **Lev Tumerman** tenía en F18 2 citas y 3 datos (F05 Stanford + F13 en.wikipedia). Ahora tiene 1 cita y 2 datos, porque en.wikipedia no salió en el R1 nuevo.
- Los documentos rusos sumaron datos, pero ningún testigo con nombre: el pool no ganó personajes (9 → 7).

**Decisión:** PARADA, como manda §2. Sin reintento. El handoff de F18 lo permite una vez solo si la causa es de descarga, y acá la causa principal es que una fuente no fue propuesta. Las tres 429 podrían haber traído testigos, pero eso no se puede demostrar, así que tomé la opción conservadora.

## 4. Costo (`costos_f19.json`)
| paso | tope | US$ |
|---|---|---|
| research v3 con cirílico + compuerta (perfil, R1, R2, R3 de 10 documentos, R4, R5) | 3.00 | 0.9315 (16 min) |
| ficha · columna · escaleta · guion | 0.60 · 0.30 · 0.60 · 0.30 | — (PARADA) |
| **total** | **5.00** | **0.9315** |

## 5. Estado en el disco
- `_steps/f18-kyshtym-mayak/`:
  - `00_pool_v3.json`, `_perfil.json`, `fuentes/` y `POOL_GATE.md` son **los de F19 (rojo)**;
  - lo de F18 quedó en `00_pool_v3_f18.json` y `_f18/`: perfil, fuentes/, POOL_GATE, ficha, columna y la caché R3 del documento ruso.
- El topic en `data/topics_db.json` **sigue con el pool de F18**: el rojo cortó antes de cargar el nuevo. Respaldo en `topics_db.pre_f19.json`.
- `lab/hyperframes/f19/`: `POOL_GATE.md`, `perfil.json`, `manifest.json`, `fuentes.json`, `run_research*.log`, `costos_f19.json`, `compara_f19.html`, `resumen_f19.json`. No hay `FICHA`, `COLUMNA`, `ESCALETA` ni `NARRACION`.

## 6. Para el analista
- El cirílico era la raíz del pool chico (175 → 302), pero no la del humano. Los documentos rusos no tienen testigos con nombre y cita, y el único humano posible (Tumerman) depende de dos fuentes en inglés.
- Opciones, ninguna ejecutada:
  - (a) reintentar el research una vez, con las 429 bajadas y en.wikipedia propuesta;
  - (b) aceptar un humano colectivo (los evacuados del Techa), que la columna ya permite pero la compuerta cuenta como 0;
  - (c) cambiar el tope de 10 descargas para temas bilingües.
- Las tres cosas tocan el research o la compuerta: decide Omar.

## 7. Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Los tres arreglos de §1 están programados y testeados. La cadena paró en el research por compuerta ROJA, como manda §2. Los entregables de ficha, columna, escaleta y guion no existen, y eso es consecuencia de la PARADA, no una falta.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1.1a | `nombres_locales` en el perfil | OK | `research_v3.py` PROFILE_SCHEMA y `seed_profile`; `f19/perfil.json` trae 7 formas en cirílico |
| 1.1b | `place_re` con latinos y locales, `re.I`, lookarounds | PARCIAL | `place_regex` usa lookarounds solo en los locales. Los latinos conservan ``. `re.I` no aparece en la función; no verifiqué si `names_event` lo aplica al compilar |
| 1.1c | Orleans y Ycuá dan el mismo `place_re` | PARCIAL | `test_perfiles_guardados_dan_el_mismo_place_re` usa Ycuá, Cromañón y Vajont. Orleans no está en ese test |
| 1.1d | El perfil lo genera Pro | FALLA (declarada) | Sigue en Flash (`call_flash_json`). El handoff se contradice: dice «Pro» y también «el mismo paso que hoy». El reporte lo anota |
| 1.1e | Research rehecho con respaldo del pool de F18 | OK | `00_pool_v3_f18.json` y `_f18/` existen; `data/topics_db.pre_f19.json` existe; costo 0.93 de 3.00 |
| 1.2 | Antagonista persona o institución | OK | `m01a_escaleta.py`: `institucion_de_la_ficha`, `validate(institucion_ok=)`, esquema con `tipo`. Tests Gusman, ≥2 hechos y «la KGB» están en `test_module_f19.py` |
| 1.3 | Línea de rango de beats en el usuario | OK | `build_prompt_v2(beats=)` y `generate_escaleta_v2`: `beats = ... if gate else None`. Sin compuerta no hay línea; hay test |
| 2a | Citas con `traduccion` | PARCIAL | Está en el esquema, en `id_texts`, en `markdown` y en `ficha_section_v2`. «Una línea en `data_line`» no está implementada directamente; va indirecto por `id_texts`. Nunca corrió con datos |
| 2b | Compuerta roja → PARADA | OK | `POOL_GATE.md` dice ROJO con `elegibles_humano` 0; no corrieron ficha, columna, escaleta ni guion |
| 3 | Salidas | PARCIAL | Existen `POOL_GATE.md`, `costos_f19.json`, `compara_f19.html`, `F19_REPORT.md`. Faltan `FICHA`, `COLUMNA`, `ESCALETA` y `NARRACION` por la PARADA. Faltan también los prompts con md5 |
| 3b | `F19_REPORT.md` con el veredicto íntegro del revisor | PENDIENTE | §7 dice «(se pega abajo)». Es esperable, porque este veredicto todavía no existía |
| 4 | Cero chequeos nuevos y archivos prohibidos intactos | OK | No hay diff en `config.py`, `m03*` ni `topics_db` (git status no los lista). `gfx_profiles/*` y `diag_234_cap4.py` ya estaban modificados en el status inicial |
| 4b | Tests verdes | OK | Corrí `pytest f19, f17, f16, f11`: 74 passed. La cifra «692 verdes» del reporte no la verifiqué (NO VERIFICABLE sin la suite completa) |
| 7 | Reporte sostenido por los archivos | OK | `python -I f19_compara.py` reproduce el embudo: pool 175→302, ru 0→239 ítems, en 199→88. Pool F19 con 7 personajes y pool F18 con 9. Tumerman figura `elegible_humano` True en F18 y False en F19. Perfil y costo coinciden |

Respuestas a tus puntos:
1) Es una reinterpretación razonable. Los dos requisitos del handoff chocan, y quedó una lectura defendible y anotada. El «Pro» es una desviación declarada. La reconciliación de `place_re` es sensata, pero queda sin test de Orleans y con `re.I` sin verificar.
2) Es la misma forma, no un chequeo nuevo: un «existe en la ficha» con dos fuentes. Ignorar el artículo inicial es una lectura leve. No filtrar por «rol institucional» es más permisivo que el handoff, y el reporte lo declara.
3) Correcto. El único uso del rango es `if gate`.
4) Cumple en espíritu, vía `id_texts`, que alimenta `data_line`. No se probó con datos.
5) OK. Respaldos presentes y `topics_db` sin tocar.
6) No reintentar es conservador y está bien justificado y anotado. El reporte deja a Omar tres opciones (a, b, c).
7) Sin afirmaciones sin respaldo. La nota al pie sobre ítems por documento explica la diferencia 199 frente a 175.

Fuera de alcance: ninguno detectado (untracked en f19/ y `test_module_f19.py`, ambos dentro de lo declarado).

Riesgos que el contrato no cubre: la compuerta exige un humano elegible, y los documentos en ruso no aportan testigos con nombre. El cirílico agranda el pool sin resolver ese cuello. El tope de 10 descargas se llenó con rusos y dejó 4 fuentes en inglés sin intentar. Las 3 HTTP 429 hacen que el research no sea reproducible entre corridas.

**Notas de CC después del veredicto** (verificadas, sin cambios de código):
- `re.I`: lo aplica `names_event` en las dos búsquedas (`research_v3.py:583`).
- Orleans no tiene `_perfil.json`: su `place_re` está escrito a mano en `lab/hyperframes/f7/f7a_fuentes_orleans.py:24` y no pasa por `seed_profile`, así que el cambio no lo toca. Los perfiles guardados son los de Ycuá, Cromañón y Vajont, y los tres dan el mismo `place_re` (test).
- Prompts con md5: el research no tiene un prompt de Sol (son las llamadas Gemini de `run_seed`). Los prompts de ficha, columna, escaleta y guion no existen porque no corrieron.
- 692 verdes + 5 previas: suite amplia corrida en esta sesión, después de los cambios de §1.
