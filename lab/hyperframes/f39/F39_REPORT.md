# F39 — Fase 1 de la semilla al papel, en producción + Kyshtym en limpio — REPORTE

Handoff `lab/hyperframes/f39/HANDOFF_F39_fase1_de_la_semilla.md` (md5 `d2cfa61b252734007ad54b26e76d116b`). Rama `f11-guion-v4`, base `ccbc303`. Modelo: Opus 5.5 (medium).

Pedido literal de Omar (palabra por palabra):

> Modelo: Opus medium.
>
> Leé ENTERO lab/hyperframes/f39/HANDOFF_F39_fase1_de_la_semilla.md (md5 d2cfa61b252734007ad54b26e76d116b) y ejecutalo con /tanda, en el orden del handoff:
>
> Paso 0 (en serie): buscar secretos en lo no subido (si hay → PARADA sin push) · commit de DECISIONES.md (md5 3ab8559116cb0ff3740eab7dbb1e1b0f) + el handoff · commit aparte del perfil vigente (gfx_profiles/misterio.json + lexico_propuestas.json, tal cual, con resumen) · git push -u origin f11-guion-v4 (main no se toca).
>
> A en paralelo (subagentes): m01a_escaleta (sin ficha = EscaletaSinFicha, rama vieja borrada) · topic_researcher (investigar UNA semilla en un topic_id dado) · simulador (tabla §1 por código). Vos: fase1_5 (--semilla/--topic, ficha si falta después de la compuerta, PARADA del papel y --aprobar-papel con md5). Candado (md5 ch02 38e5ba14… + suite amplia) en serie al final de A. Cada parte termina con su salida en texto.
>
> B después de A: Kyshtym en topic limpio f39-kyshtym, tope lab/TOPE_TANDA.json = US$ 5,00, UNA corrida sin manos:
> python fase1_5.py --semilla lab/hyperframes/f39/b/semilla_kyshtym.json --topic f39-kyshtym --v3 --guion v4 --batch
> Si un paso falla: PARADA con paso, error y gasto; no se reintenta a mano.
>
> Reglas fijas: cero cambios de prompt; nada copiado de f18-kyshtym-mayak; nada de voz, imágenes, fase2, render, fase3, merge; ningún número nuevo en el código; usá todos los subagentes en paralelo que la tanda permita.
>
> Cierre: F39_REPORT.md con A.5, B.4 (01e_pantalla.md ENTERO), B.5, costos por paso, «lo que queda abierto» entero, veredicto íntegro de revisor-handoff, ESTADO actualizado. PARADA.

## Lecturas declaradas
`CLAUDE.md`; `DECISIONES.md` entero (md5 `3ab8559116cb0ff3740eab7dbb1e1b0f`, con la línea 15:23); `lab/ESTADO_SESION.md` (cabecera y bloques F38e/F38e-0); el handoff entero; `.claude/commands/tanda.md`; `lab/MAPA_MODULOS.md`; el código de `fase1_5.py` (`process_topic`, `run_escaleta_v3`, `run_guion_v4`, `run_pantalla`, `_step_cost`, `main`), `topic_researcher.py` (`_research_seed_deep`, `_enrich_with_seed_metadata`, `research_topics`), `script_engine/m01a_escaleta.generate_escaleta`/`pool_gate_profile`, `researcher_steps/ficha_caso.run`, `.claude/hooks/tope_tanda.py`, y cómo llamaban a la ficha `lab/hyperframes/f23/f23_corridas.py` y `f24/f24_corridas.py`.

## Paso 0
1. **Secretos** (`git log --branches --not --remotes -p`, 229 commits no subidos): patrones `api_key`, `sk-…`, `AIza…`, `Bearer …`, `-----BEGIN … PRIVATE`. Primera pasada: 14 aciertos, todos falsos positivos (`chelyabin`**`sk-`**`court-to-examine-mayak-plant` en URLs de Bellona dentro de pools). Segunda pasada con borde de palabra: **0**. Archivos sensibles en los commits no subidos: ninguno (`gfx_config.py` y `music_config.py` aparecieron por el patrón `config.py$`: no tienen claves; `.env` y `config.py` están en `.gitignore`). En los archivos del paso 0: ninguna clave (solo la mención en el texto del handoff). → **sin secretos, se sigue**.
2. `md5sum DECISIONES.md` = `3ab8559116cb0ff3740eab7dbb1e1b0f` ✓ · handoff `d2cfa61b252734007ad54b26e76d116b` ✓ → commit **`d49178d`** (solo esos 2 archivos, tal cual).
3. **Perfil vigente** → commit **`a67ed45`** (solo `gfx_profiles/misterio.json` y `gfx_profiles/lexico_propuestas.json`, tal cual). Resumen (en el mensaje del commit): `git diff --stat` lexico_propuestas.json +534, misterio.json +11/−…; `misterio.json` cambia las claves de primer nivel `moods` y `sellos_clima` (nueva: el vocabulario de sellos de DECISIONES 14:22); `lexico_propuestas.json` suma 60 palabras propuestas al léxico de moods y actualiza `borradas`, sin claves quitadas. Último commit anterior del perfil: `7c0b2e5` (2026-10-21, wip F5e). El hook `guard_git` no frenó. **No entraron** `diag_234_cap4.py` (modificado desde antes de F38; su último commit es de 2026-05-31: no es de ninguna tanda de esta rama reciente) ni `lab/hyperframes/f28/a/f28a.log` (log de la tanda F28, regrabado por una corrida posterior).
4. **Push** (respaldo, no merge; `main` no se tocó: `origin/main` = `3cf2cc7d…` antes y después):
```
remote: Create a pull request for 'f11-guion-v4' on GitHub by visiting:
remote:      https://github.com/gueva1441/automatization_videos/pull/new/f11-guion-v4
To https://github.com/gueva1441/automatization_videos.git
 * [new branch]      f11-guion-v4 -> f11-guion-v4
branch 'f11-guion-v4' set up to track 'origin/f11-guion-v4'.
```

## Módulos tocados (sticker de `lab/MAPA_MODULOS.md`)
| módulo | hoy | después |
|---|---|---|
| `fase1_5.py` (no está en el mapa: el mapa es de la capa gráfica y lo que la alimenta) | m01a = compuerta + escaleta; no arranca desde una semilla; después de m01b sigue a la voz | `--semilla <archivo> --topic <id>` corre primero el research de esa semilla; m01a = compuerta → ficha si falta → escaleta; después de m01b, PARADA del papel salvo `--aprobar-papel` vigente |
| `topic_researcher.py` (no está en el mapa) | topic con `uuid4`, saltea semillas ya investigadas | `investigar_semilla(seed, topic_id)`: una semilla en un topic dado, registrada en `topics_db`; `research_topics` igual por fuera |
| `m01a_escaleta` | «Fase 1: arma la escaleta … desde la ficha del caso» | sticker nuevo en el mapa: «… desde la ficha del caso v2 … F39 §A.2: sin ficha v2 lanza `EscaletaSinFicha` y para sin gastar; el camino viejo sin ficha se borró.» (mapa regenerado: 35 módulos, 115 aristas, 0 muertos) |
| `researcher_steps/ficha_caso.py` | — | no se tocó: se llama `run` tal cual |

Una variable por parte: A.1 la ficha en m01a, A.2 la escaleta sin ficha, A.3 el arranque desde la semilla, A.4 la compuerta del papel; B corre lo de A sin tocarlo.

## Constantes
Ninguna nueva en el código (las del handoff §2 son todas existentes; el tope US$ 5,00 vive en `lab/TOPE_TANDA.json`, no en el código). Los códigos de salida de `fase1_5` (0 PASS o PARADA del papel, 2 otra PARADA, 1 FAIL) son señales del proceso, no perillas. El tope del papel sale de `m01e_pantalla.tope_usd()` = **1,00 «respaldo (el perfil no trae costos.m01e_tope_usd)»**: el handoff dice «`costos.m01e_tope_usd` del perfil», pero el perfil vigente no trae esa clave (abierto f2).

## Cómo se corrió A
- **Paralelo** (DECISIONES 01:23): subagente 1 = `m01a_escaleta` (A.2), subagente 2 = `topic_researcher` (A.3, la función de una semilla), subagente 3 = simulador (A.5 d), los tres a la vez; CC = `fase1_5` (A.1, A.3, A.4) con interfaces fijadas de antemano (`m01a_escaleta.EscaletaSinFicha`, `topic_researcher.investigar_semilla(seed, topic_id)`).
- Commits por parte: **`f930596`** A.2 · **`e664390`** A.3 (topic_researcher) · **`6b2b717`** fase1_5 (A.1/A.3/A.4 + A.5 a/b/d).
- Candado en serie al final de A (`lab/hyperframes/f39/verificar.sh a_candado`).
- Evidencia de la búsqueda de secretos re-corrida sobre los 230 commits de la rama que no están en `origin/main`: `lab/hyperframes/f39/paso0_secretos.txt` (0 aciertos, 0 archivos sensibles).

## A.1 — La ficha en m01a (`6b2b717`, CC)
`run_escaleta_v3`: salvo escaleta congelada, primero `m01a_escaleta.pool_gate_profile` (rojo → `PoolGateRed` → `Parada`, **sin pagar la ficha**), después `asegurar_ficha`: si hay `ficha_caso.json` con `historia` se usa y no se regenera; si no, `ficha_caso.run(topic_id, steps_dir=STEPS_DIR, title=<seed_title>, tag=<topic_id>)` con el modelo y el prompt vigentes (`gpt-6.1-sol` high, `f23-1`), envuelto en `_step_cost(…, "ficha", …)` → paso «ficha» en `01_v3_costos.json`. El título es el `seed_title` que el topic guardó al registrarse (A.3) o, para un topic viejo, el de `seeds_archive.json` por `seed_id`; si no hay ninguno, `Parada` («no se inventa»). Después, la escaleta; `EscaletaSinFicha` → `Parada`. La compuerta corre dos veces (aquí y dentro de `generate_escaleta`): es determinista, no gasta y reescribe el mismo `POOL_GATE.md` (abierto f4).

## A.2 — Escaleta sin ficha = error (`f930596`, subagente 1)
- `class EscaletaSinFicha(Exception)`; `generate_escaleta` sin ficha v2 → `EscaletaSinFicha(f"{topic_id}: sin ficha_caso.json con historia")` sin armar ningún `call`. Orden sin cambio: frozen → pool vacío = ValueError → compuerta (rojo = PoolGateRed) → ficha → v2. Se quitó el parámetro `attempts=` (solo lo usaba la rama vieja).
- **Borrado** (ninguno con otro llamador vivo; `grep -rn` en todo el repo con alias `me.`/`ma.` y `from … import`): `PROMPT_VERSION` ("f6b-4"), `MAX_ATTEMPTS` y `attempts`, `SYSTEM`, `FEWSHOT`, `rules_text`, `RULES`, `build_prompt`, `pool_section` (con el apagador `ESCALETA_DIGEST`), `ficha_section` (la v1), `_fmt_people`, `_fmt_quotes`, `_fmt_canonical`, `_fmt_counts`, `_verif`, `own_ids`, el bucle Pro (`call_pro_json`, `01a_escaleta_rechazada.json` f6b-4) y sus líneas del docstring. `m01a_escaleta.py` 2036 → 1715 líneas (+27 −348), CRLF.
- **Quedan por otro llamador:** `SCHEMA` (base de `SCHEMA_FICHA`; lo miran `test_module_f19.py:118` y `f22.py:261`); `MAX_APOYOS` (default de `validate`, que usa `frozen_escaleta`; y `test_module_f14::test_validate_apoyos_hasta_6_solo_con_ficha`); `count_variants` (`validate`, `writer_instructions`, `guion_v4.py:587`, `m01b_guionista.py:94/295`, `test_module_f23.py:279`); `validate` y sus helpers, `_profile`, `MAX_APOYOS_FICHA`, `ficha_notes`, `pool_gate_profile`, `apply_pool_plan`, `writer_instructions`, `_persist`, `is_v3` (v2, frozen y `fase1_5`); `NUM_WORDS` (`m01c_editor`), `has_figure` (`m01b_guionista`).
- **Prompts v2 byte-idénticos** (md5 antes = después; el revisor recalculó dos): `SYSTEM_V2` `2e67791c…` · `SYSTEM_V2_F25_1` `9325ad38…` · `SYSTEM_V2_F24_1` `006a195f…` · `SYSTEM_V2_F22_2` `22cfd68b…` · `SYSTEM_V2_F22_1` `7ea18a6a…` · `SYSTEM_V2_F16_1` `49ed74d9…` · `TAREA_V2` `5808b41e…` · `TAREA_COLUMNA` `b53c30be…` · `SCHEMA_FICHA` `a389dea8…` · `PROMPT_VERSION_V2` f26-1 · `build_prompt_v2` `5aea0244…` (fixture f16).
- **Tests borrados por nombre (9), todos de la rama vieja:** `test_module_f14.py::test_escaleta_sin_ficha_byte_identica` (md5 de `build_prompt`/`RULES`); `f14::test_escaleta_con_ficha_lee_la_ficha_y_apoyos_0_6` (`build_prompt` con ficha v1); `f15::test_escaleta_sin_ficha_sigue_byte_identica`; `f15::test_escaleta_con_ficha_v2_historia_y_escenas_primero` (el `build_prompt` viejo, forma anterior a F16); `f15b::test_escaleta_sin_ficha_intacta_y_con_ficha_pide_gancho_y_pico_desde_escenas`; `f16::test_sin_ficha_byte_identico`; `f16::test_sin_ficha_sigue_por_el_camino_viejo` (afirmaba lo que F39 prohíbe; lo reemplaza el test nuevo); `f22::test_escaleta_v1_byte_identica`; `f7::test_escaleta_reads_v3_pool`. Con ellos, los fixtures que solo usaban ellos (`ESC_MD5`, imports sin uso; pyflakes limpio).
- **Tests ajustados (6), usaban la rama vieja de paso:** `f14::test_generate_escaleta_auto_lee_la_ficha_del_disco` (sin ficha → `EscaletaSinFicha`; con ficha v2 sintética, una llamada v2); `f6b::test_generate_con_reintento_pool_plan_y_frozen` (ficha v2 mínima; el reintento es un `dato_central` inexistente, bloqueante v2); `f7::test_digest_has_real_ids_and_escaleta_uses_it` → `test_digest_has_real_ids`; `f7d::test_escaleta_gate_red_spends_nothing_yellow_shortens` (mira `me._profile` en vez de `build_prompt`); `f8::test_minimo_dos_beats_por_cap_de_desarrollo` y `f8::test_amarillo_baja_el_minimo_a_uno` (sin la línea de `RULES`/`rules_text`).
- **Tests nuevos** `test_module_f39_escaleta.py` (8): sin ficha en disco para sin llamar (mensaje exacto, sin `01a_escaleta*`); sin ficha con `columna="generar"` para antes de la columna; excepción pública; ficha sin `historia` para; `topic_id` en vez de `id`; con ficha v2 sigue el camino v2 (`SYSTEM_V2`, `SCHEMA_FICHA`, f26-1, persistida); ficha v2 sin `call` va por `call_escaleta`; frozen no mira la ficha.
- Tests de m01a (22 archivos): 372 passed. Rápida 58. Sticker nuevo aplicado y mapa regenerado (mismo commit).

## A.3 — Arrancar desde una semilla (`e664390` subagente 2 + `6b2b717` CC)
- `topic_researcher.investigar_semilla(seed: dict, topic_id: str) -> dict`: la misma cadena del modo `long` (`_research_seed_deep(seed, existing_titles, topic_id=…)` → `run_seed` v3 en `STEPS_DIR/topic_id` + 4a–4e, `_enrich_with_seed_metadata`), con `id == topic_id` y `seed_title`; sin el filtro de semillas investigadas; registra en `topics_db`; no toca `selected_seeds.json` ni `seeds_archive.json`. Antes de gastar: `ValueError` si `topic_id` vacío, si a la semilla le falta `seed_id`/`seed_title`/`discovery_mode` (agregado: `_enrich` hacía `seed["discovery_mode"]` al final, después de pagar) o si el id ya está en `topics_db` (y otra vez al registrar). `PoolGateRed` se propaga y no se registra nada. `research_topics` sin cambios por fuera (sigue con `uuid4`, filtro, inbox y archivo). Tests nuevos `test_module_f39_research.py` (5); los existentes de `topic_researcher` (f10, f5e, f6a, f7d) 28 verdes sin cambios.
- `fase1_5 --semilla <archivo> --topic <id>` (`research_de_semilla`): lee la semilla (con `seed_id` y `seed_title`); si `_steps/<id>/` existe o el id está en `topics_db` → `Parada` (no pisa); respaldo `data/topics_db.pre_<id>.json`; `investigar_semilla` dentro de `_step_cost(…, "research", …)` (el gasto del research va a `01_v3_costos.json` y al ledger); compuerta roja → `Parada` con los motivos; cualquier otra falla del research → PARADA con su error y exit 2. Después sigue `process_topic` desde m01a. `--semilla` sin `--topic`, o con `--from`/`--only`, es error de argumentos.

## A.4 — La compuerta del papel (`6b2b717`, CC)
- En `process_topic`, cadena v3, después de m01b y antes de `normalizer_gate` (y por lo tanto también al reanudar con `--from normalizer_gate|audio|m07|m03`): `estado_papel(topic_id)`. Sin `01e_pantalla.json` → no pasa («no hay nada que aprobar»); sin `aprobado` → no pasa; `aprobado.md5` ≠ md5 del papel sin el campo `aprobado` (JSON con claves ordenadas) → no pasa («cambió después de la aprobación»). Si no pasa: `⏸ PARADA del papel` con la ruta de `01e_pantalla.md` y el comando para aprobar; `status = "PARADA"`, `parada = "papel"`, exit 0 (es el final esperado de Fase 1). `--only m01b` sigue cortando antes, como siempre.
- `python fase1_5.py --topic <id> --aprobar-papel "QUIÉN FECHA"`: escribe `aprobado: {por, fecha, md5}` en `01e_pantalla.json` y no corre nada más (el mismo parseo de «quién fecha» que `--aprobar-guion`).
- Solo en la cadena v3 (la única que hace papel): un topic viejo sin v3 no tiene papel y seguiría a la voz como antes (abierto f3).
- Tests `test_module_f39_fase1.py` (11): la cadena desde la semilla en orden y PARADA del papel; no pisa un topic existente (carpeta o id); compuerta roja en el research = PARADA; compuerta roja en m01a no paga la ficha; ficha v2 existente no se regenera; sin `seed_title` no se inventa; aprobar y md5 (un papel cambiado queda sin aprobar); reanudar con `--from audio` mira el papel; sin papel no hay nada que aprobar; papel aprobado deja seguir; `--help` tiene los flags.

## A.5 — Salida en texto
**(a) Líneas nuevas de `--help`** (`lab/hyperframes/f39/a/help.txt`):
```
  --semilla ARCHIVO.json
                        F39 §A.3: con --topic <id> nuevo, investiga primero
                        esa semilla en ese topic (research v3 + 4a–4e,
                        registro en topics_db con respaldo
                        topics_db.pre_<id>.json) y sigue la cadena: compuerta
                        → ficha si falta → escaleta → guion → caps y títulos →
                        papel → PARADA del papel. Si _steps/<id>/ o el id ya
                        existen, PARADA (no pisa nada)
  --aprobar-papel "QUIÉN FECHA"
                        F39 §A.4: escribe `aprobado: {por, fecha, md5}` en
                        _steps/<id>/01e_pantalla.json (la compuerta antes de
                        la voz: sin eso, nada corre después de m01b) y no
                        corre nada más
```
**(b) El comando de A.3 con llamadas falsas** (`test_module_f39_fase1.py::test_a3_de_la_semilla_al_papel_en_orden_y_para_en_el_papel` con `pytest -s`; `lab/hyperframes/f39/a/cadena_falsa.txt`):
```
── pasos: research → compuerta → ficha «Un desastre de prueba» → escaleta → guion → caps → papel
  [semilla] «Un desastre de prueba» (s-1) → topic t-f39
  [semilla] topic registrado: 'VT'
════════════════════════════════════════════════════════════
  📜 Procesando topic t-f39 desde m01a
════════════════════════════════════════════════════════════
  [v3] guion v3 (escaleta → guionista → editor → partición)
  [01a v3] Compuerta del pool + escaleta...
  [ficha] sin ficha v2 → ficha_caso.run (gpt-6.1-sol high, prompt f23-1) · título «Un desastre de prueba»
  [ficha] {} · sacados 0
  [01b v4] Guionista v4 → reparación (una ronda) → partición → juez...
  ⏸  PARADA del papel: el papel no está aprobado.
     Leer: …\steps\t-f39\01e_pantalla.md
     Aprobar: python fase1_5.py --topic t-f39 --aprobar-papel "Omar <fecha>"
```
**(c) grep de la rama borrada en `m01a_escaleta.py`:** antes 49 líneas (`lab/hyperframes/f39/a/escaleta_grep_antes.txt`), después 12 (`escaleta_grep_despues.txt`):
```
8:ficha v2, `EscaletaSinFicha` (para, sin gastar); el camino viejo (Pro con el pool, sin ficha) se borró. La salida
11:    generate_escaleta(topic)   → escaleta (persistida en _steps/<id>/01a_escaleta.json); sin ficha v2, EscaletaSinFicha
112:class EscaletaSinFicha(Exception):
121:SCHEMA: dict[str, Any] = {
144:# F39 §A.2: SCHEMA ya no se manda solo (era el de la escaleta sin ficha, borrada); queda como base de SCHEMA_FICHA.
148:SCHEMA_FICHA: dict[str, Any] = copy.deepcopy(SCHEMA)
157:MAX_APOYOS = 3                      # datos_apoyo por beat sin ficha: hoy solo el default de `validate` (escaleta_frozen)
239:             solo_apoyo: … max_apoyos: int = MAX_APOYOS,
781:    F39 §A.2: sin ficha v2 (no hay ficha, o no tiene `historia`), EscaletaSinFicha: para sin llamar a ningún modelo. El
799:        raise EscaletaSinFicha(f"{topic_id}: sin ficha_caso.json con historia")
1457:    """F16 §1.1: <caso> … Sin notas, sin FEWSHOT,
```
**(d) Tabla de §1 recalculada por código** (simulador; `lab/hyperframes/f39/a/sim_sin_ficha.py`, solo lee `data/`; `tabla_sin_ficha.md`):

| topic | ficha_caso.json | prompt_version | historia | 01a_escaleta | 01b_* | en topics_db | ¿para? | clasif. (si para) |
|---|---|---|---|---|---|---|---|---|
| 4ac37187-pennhurst | sí | f23-1 | sí | sí | 2 | no | no | - |
| ba6c3cac-f10seco | no | - | no | sí | 5 | no | sí | lab |
| ba6c3cac-f7r3 | sí | f15-1 | sí | sí | 9 | sí | no | - |
| f18-kyshtym-mayak | sí | f23-1 | sí | no | 0 | sí | no | - |
| f8s1-ycua-bolanos | sí | f15-1 | sí | sí | 37 | sí | no | - |
| f8s2-cromanon | no | - | no | no | 0 | no | sí | lab |
| f8s3-vajont | sí | f23-1 | sí | sí | 4 | sí | no | - |
| f8s3-vajont-f28c | sí | f23-1 | sí | sí | 4 | no | no | - |

Total con pool v3: 8; paran: 2, los mismos dos del analista, los dos de lab; coinciden los 8 topics y los `prompt_version`. Matices: `4ac37187-pennhurst` y `f8s3-vajont-f28c` no están en `topics_db` por id (pennhurst no para, así que no cambia nada); `ba6c3cac-f10seco` tiene escaleta y 5 `01b_*` del camino viejo de F10 y se clasifica «lab» porque no está en `topics_db`. **Ningún topic de producción se rompe.**

**(e) Tests y candado:**
- Nuevos: `test_module_f39_escaleta.py` (8), `test_module_f39_research.py` (5), `test_module_f39_fase1.py` (11) = 24. Borrados: 9. Ajustados: 6 (listas en A.2).
- Candado al final de A (sobre `6b2b717`, `lab/hyperframes/f39/a_candado/`): md5 de ch02 de Orleans sin gfx **`38e5ba14e3d24fd20f9297c9e1dfee24`** ✓ · rápida **58 passed** · amplia **913 passed, 5 failed** = exactamente las 5 previas (`01b_pauses` ×3, `m03_merge_timing` ×2). Cuenta: 898 (F38e) − 9 borrados + 24 nuevos = 913 ✓.

PARADA corta de A anotada; se siguió a B.

### Revisión intermedia de A (`revisor-handoff`, mientras corría B; íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

Alcance: paso 0 y A. No corrí `fase1_5`, `fase2b`, la suite amplia ni toqué `data/`. Corrí los 24 tests de `test_module_f39_*.py` (24 passed). Los resultados del candado los leí de los logs.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 0.1 | Buscar secretos en lo no subido antes del push | NO VERIFICABLE | No hay ningún artefacto de esa búsqueda en el repo. Hoy `origin` está en `a67ed45`, así que el rango no subido ya no se puede reconstruir. Por mi cuenta, un grep de patrones de clave sobre las líneas agregadas de los 5 commits de la tanda dio vacío. Faltaría la salida del `git log --branches --not --remotes -p` original. |
| 0.2 | Commit tal cual de DECISIONES y handoff, con md5 | OK | `d49178d` toca solo esos 2 archivos. `md5sum` da DECISIONES `3ab85591…` y handoff `d2cfa61b…`, los dos iguales a los del contrato. Los md5 están en el mensaje. |
| 0.3 | Perfil en commit aparte, por ruta explícita, con resumen | OK, con una observación | `a67ed45` toca solo `gfx_profiles/misterio.json` y `gfx_profiles/lexico_propuestas.json`. El mensaje trae `--stat` y las claves que cambian (`moods`, `sellos_clima`). La línea de `--stat` quedó con un «−…» a medias. |
| 0.4 | `diag_234_cap4.py` y `f28a.log` fuera de los commits | OK | Siguen como ` M` sin commitear y no aparecen en ningún `--stat`. |
| 0.5 | Push de `f11-guion-v4`, sin tocar `main` | OK | El reflog de `origin/f11-guion-v4` marca «update by push» en `a67ed45`. La rama está «ahead 3», que son los commits de A. |
| A.1 | Orden compuerta → ficha → escaleta | OK | `fase1_5.py` `run_escaleta_v3`: `me.pool_gate_profile` (rojo = `Parada`), luego `asegurar_ficha`, luego `generate_escaleta`. |
| A.1b | Ficha: `ficha_caso.run`, costo como paso «ficha», no regenera una v2 | OK | `asegurar_ficha` usa `_step_cost(..., "ficha", ...)`. Si ya hay ficha con `historia`, la usa. Sin `seed_title` levanta `Parada`, no inventa. `cadena_falsa.txt` muestra el orden. |
| A.2 | `EscaletaSinFicha` y rama vieja borrada | OK | `m01a_escaleta.py:112` define la clase y `:799` la lanza. Los greps antes/después de la rama están en `escaleta_grep_*.txt`. `SCHEMA` y `MAX_APOYOS` quedan con razón declarada (base de `SCHEMA_FICHA`, y `escaleta_frozen`). |
| A.2b | Cero cambios de prompt | OK | Recalculé `SYSTEM_V2` = `2e67791c` y `SCHEMA_FICHA` = `a389dea8`; coinciden con el mensaje de `f930596` y con `A2_SALIDA.md`. |
| A.2c | Tests borrados y ajustados por nombre | OK | `A2_SALIDA.md` lista los 9 borrados y los 6 ajustados. Hay 8 nuevos en `test_module_f39_escaleta.py`. |
| A.3 | `--semilla`: no pisa, respalda `topics_db`, compuerta roja = PARADA | OK | `research_de_semilla` hace Parada si `_steps/<id>` o el id ya existen, copia `topics_db.pre_<id>.json` y convierte `PoolGateRed` en `Parada`. En `main` la falla del research sale con exit 2. |
| A.3b | `investigar_semilla` | OK | `topic_researcher.py` (commit `e664390`). Usa el `topic_id` dado, no filtra semillas ya investigadas y no toca inbox ni `seeds_archive`. `research_topics` queda igual por fuera. |
| A.4 | Compuerta del papel después de m01b, y al reanudar; sin papel = para | OK | `process_topic` revisa `estado_papel` antes de `normalizer_gate`, solo en cadena v3. El md5 se calcula sin el campo `aprobado`. «No hay papel» devuelve False. Cambio de contenido invalida la aprobación. |
| A.4b | `--aprobar-papel "QUIÉN FECHA"` escribe `{por, fecha, md5}` y no corre nada más | OK | `fase1_5.py` `aprobar_papel` y `main` (`sys.exit` inmediato). |
| A.5 | Salidas en texto: help, cadena falsa, greps, tabla, tests, candado | OK | `help.txt`, `cadena_falsa.txt`, `tabla_sin_ficha.md` (8 topics, 2 paran, ambos de lab, igual que la tabla de §1). Candado: ch02 `38e5ba14…`, rápida 58, amplia 913 passed + 5 failed. Los 5 son las previas conocidas (`01b_pauses` ×3, `m03_merge_timing` ×2). |
| — | Ningún número nuevo | OK | En el diff de `m01a` no encontré constantes numéricas nuevas. En `fase1_5` y `topic_researcher` los exit 0/1/2 y `topic_id` son códigos, no parámetros. Los modelos y prompts salen de `fc.MODELO`, `ESFUERZO` y `PROMPT_VERSION`. |

Observaciones (no tumban el veredicto):
- **Secretos:** la búsqueda del paso 0 no dejó prueba. Que se hizo depende de lo que diga el reporte.
- **Compuerta duplicada:** la compuerta del pool corre dos veces, una en `fase1_5` y otra dentro de `generate_escaleta`. No cuesta nada, pero está duplicada.
- **Código muerto:** el subagente de A.2 lo declaró en `A2_SALIDA.md` y el reporte debe repetirlo. Son `escaleta_notas` en `fase1_5.py:196–202` y `pool["digest"]`. Además hay 4 scripts históricos de lab que ya no corren.
- **Candado:** `a_candado/` y `verificar.sh` están sin commitear, como se avisó.

Fuera de alcance: ninguno en los 5 commits. Quedan sin commitear `diag_234_cap4.py` y `f28a.log`, que son de otras tandas y no entraron.

Riesgos que el contrato no cubre:
- La compuerta del papel cambia la conducta de todos los topics v3 existentes: sin `aprobado` vigente, ninguno pasa a la voz. Es lo pedido, pero el flujo manual de Omar lo va a notar.
- La ficha se paga antes de la escaleta. Si la escaleta falla después (`EscaletaSinFicha` no, pero sí un bloqueante), la ficha ya está gastada. No hay tope por paso salvo el de `TOPE_TANDA`.
- `aprobar_papel` reescribe `01e_pantalla.json` con `indent=1`. Si otro módulo compara bytes del archivo, hay un riesgo menor. El md5 de la aprobación no lo usa.

**Adenda de CC a la revisión intermedia:** fila 0.1 → la búsqueda se re-corrió y quedó en `lab/hyperframes/f39/paso0_secretos.txt` (230 commits, 0 aciertos fuera de las URLs de Bellona, 0 archivos sensibles); la primera pasada está en «Paso 0» arriba. Fila 0.3 → el «−…» del mensaje de `a67ed45` es una abreviatura: `git diff --stat` dio «2 files changed, 534 insertions(+), 11 deletions(-)». Código muerto → abierto f5. Candado → entra en el commit del reporte.


## B — Kyshtym en limpio, desatendido
**B.0 Semilla:** `seed_id b6b84f96-03b7-40cd-8173-414d60514c76` **no está en `data/seeds_archive.json`** → se usó la de F18, `lab/hyperframes/f18/seed_f18.json` (md5 `499ad52acc5b9d6621fcc93ccf026507`), copiada tal cual a `lab/hyperframes/f39/b/semilla_kyshtym.json` (mismo md5). `seed_title`: **«Desastre nuclear Kyshtym Mayak»**.

**B.1 Topic limpio:** `f39-kyshtym` no existía ni en `_steps/` ni en `topics_db` antes de correr. Nada se copió de `f18-kyshtym-mayak` (ni perfil, ni `fuentes.json`, ni `_r1_cache.json`, ni `_r3_cache/`): todo lo de `_steps/f39-kyshtym/` lo escribió la corrida (fechas 16:17–16:45, ver B.5).

**B.2 Tope:** `lab/TOPE_TANDA.json` = `{"usd": 5.00, "desde": "2026-10-27T16:03:55"}` (escrito al arrancar B).

**B.3 Una sola corrida, sin manos** (16:04:16 → 16:45:42, 41 min 26 s, exit 0; log `lab/hyperframes/f39/b/corrida.log`):
```
python fase1_5.py --semilla lab/hyperframes/f39/b/semilla_kyshtym.json --topic f39-kyshtym --v3 --guion v4 --batch
```
CC no intervino entre pasos. La cadena llegó hasta el papel y paró en la compuerta del papel:
```
  ⏸  PARADA del papel: el papel no está aprobado.
     Leer: C:\CLAUDE_PROJECTS\automatization_videos\data\scripts\_steps\f39-kyshtym\01e_pantalla.md
     Aprobar: python fase1_5.py --topic f39-kyshtym --aprobar-papel "Omar <fecha>"
  Total: 1  |  PASS: 0  |  PARADA: 1  |  FAIL: 0
  ⏸  f39-kyshtym  (PARADA en papel: el papel no está aprobado)
```
Antes de eso, el guion v4 dejó **2 bloqueantes después de la ronda única** («[v4] quedan 2 bloqueante(s) después de la ronda única: PARADA»): `run_guion_v4` lo imprime como PARADA pero, como siempre desde F11, la cadena sigue a la partición y al papel (no es un freno del código; abierto f6).

Prompts que corrieron (ninguno cambiado en la tanda; `lab/hyperframes/f39/b/prompts_md5.txt`):
```
ficha       gpt-6.1-sol high · prompt_version f23-1 · system md5 070b75dff58aecfa407fac3d62020ce4
escaleta    prompt_version f26-1 · SYSTEM_V2 md5 2e67791cedbfa7492f8b6de1268b7b30 · TAREA_V2 md5 5808b41eb57a0949f009213d52076521
guion_v4    PROMPT_VERSION = f25-1
guion_v4    PROMPT_VERSION_ABIERTO = f13-1
guion_v4    PROMPT_VERSION_F11C = f11c-1
guion_v4    PROMPT_VERSION_V5 = f15-1
guion_v4    PROMPT_VERSION_V5_1 = f15b-1
guion_v4    PROMPT_VERSION_V5_2 = f22-1
guion_v4    PROMPT_VERSION_V5_3 = f23-1
guion_v4    SYSTEM_V5 = md5 2ff2a5cd7bc63a2fa9fc0faa2117ac65
guion_v4    SYSTEM_V5_1 = md5 cdce609abea95ee36d0eb4f44d74dda8
guion_v4    SYSTEM_V5_2 = md5 743e4f0a7ff9e58d86762bbd43679952
guion_v4    SYSTEM_V5_3 = md5 8ca9aa494e3a0b9b4a99f60e6006c5f8
guion_v4    SYSTEM_V5_4 = md5 2f66c1e07e4d6c31178091371821c0c9
guion_v4    VERSIONES_V5 = ('f25-1', 'f23-1', 'f22-1', 'f15b-1', 'f15-1')
guion_v4    DEFAULT_MODELO_GUION = claude-fable-5-1
títulos     PEDIDO_TITULOS md5 0c3fe5599f500ce523c77aac0e328597
papel       claude-sonnet-5-5 medium · m01e-6 · SYSTEM md5 7d2ccdd28055d6e621d1d251a0fe8bb7 · prompt_md5 3b98aef1d8595124967ac7a85b75bab7 · tope (1.0, 'respaldo (el perfil no trae costos.m01e_tope_usd)')
```

### Costos y tiempos por paso (`_steps/f39-kyshtym/01_v3_costos.json`)
| paso | US$ | segundos |
|---|---|---|
| research (R1–R5 + 4a–4e + registro) | 1,4829 | 1358,7 |
| ficha (gpt-6.1-sol high) | 0,3956 | 428,1 |
| escaleta (claude-fable-5-1) | 0,8105 | 157,6 |
| guionista_v4 (claude-fable-5-1) | 1,0680 | 201,8 |
| reparacion_v4 | 0,1048 | 33,3 |
| particion (Flash: caps y títulos) | 0,1310 | 120,5 |
| pantalla (claude-sonnet-5-5, 5 llamadas) | 0,7699 | 172,6 |
| **total** | **4,7627** | **2472,6** (41 min 13 s) |
Resumen por modelo al final del log: **US$ 4,7626** (Fable 1,9833 · Sonnet 0,7699 · Flash 0,1993 · Pro 1,4145 · gpt-6.1-sol 0,3956), igual a la suma de los pasos. **Tope US$ 5,00: no se pasó** (queda 0,24). El juez m05 (16:42 → 16:45, último paso) no aparece como paso propio en `_corridas` (abierto f7).

(Armada por un subagente de solo lectura desde los archivos de `_steps/f39-kyshtym/`, el log y `lab/hyperframes/f23/`; `lab/hyperframes/f39/b/B4_SALIDA.md`.)

### B.4 (por paso) — Salida en texto por paso · `f39-kyshtym`

Corrida única 16:04:16 → 16:45:42 (`_inicio.txt` / `_fin.txt`), `exit=0`, termina en **PARADA del papel**. Log:
`lab/hyperframes/f39/b/corrida.log`. Archivos: `data/scripts/_steps/f39-kyshtym/` (leídos, no tocados). Cada número
lleva su archivo/clave; lo que es estimación o deducción lo dice.

---

#### 1. research

**Perfil** (`_perfil.json`):
- años: `anio_evento` 1957 · `anio_inicio` 1957 · `anio_fin` 1957
- `tipo_evento`: **puntual**
- `idiomas_research`: ruso · inglés · español (`idioma_local` Ruso, `cobertura_ingles` true)
- `lugar_principal`: «Asociación de Producción Mayak»; 6 `nombres_lugar` + 7 `nombres_locales`
- el perfil **no trae día ni mes** del evento (solo años).

**Fuentes de R1** (`fuentes_r1.json`, `prompt_version` f7a-1):
- `fuentes`: **7** → en 4 · ru 3 · es 0
- `_descartadas`: 29 → en 18 · ru 9 · es 2 (las 29 con motivo «ninguna URL del grounding se le parece»)
- `_grounding`: 7 URLs · `_focos_grounding` {pro 0, flash 1, sin 3}

**Bajadas y con aporte** (`fuentes.json` `bajada_ok` / `aporte`, `fuentes/manifest.json`):

| idioma | en R1 | bajadas | con aporte | detalle |
|---|---|---|---|---|
| ru | 3 | 3 | 3 | F01 ru.wikipedia (25 datos · 4 citas · 8 personajes), F03 dic.academic.ru (34 · 6 · 9), F07 veteranrosatom.ru PDF «Маяк – наша гордость и боль», 2007 (142 · 19 · 32) |
| en | 4 | 3 | 2 | F05 Cambridge 2021 (8 · 1 · 0), F06 docs-books «Midnight in Chernobyl» (2 · 0 · 0); F04 Grokipedia «Alyoshenka» bajó (3 211 car., `nombra_evento` false) sin aporte; F02 Facebook **no bajó** (original: «texto de 574 caracteres (< 800: ¿paywall o portada?)»; wayback: «sin copia en la Wayback Machine») |
| es | 0 | 0 | 0 | — |
| **total** | **7** | **6** | **5** | |

Pool (`00_pool_v3.json`): `datos` 203 → ru 193 · en 10 (por `idioma`); por documento F07 139 · F03 29 · F01 25 · F05 8 ·
F06 2. `citas` 27 (F07 19 · F01 4 · F03 3 · F05 1), `personajes` 40, `cronologia` 67, `lugares` 17, `_descartados` 61,
`cifras_canonicas` 0.

**`POOL_GATE.md`** (pegado tal cual):

```
# POOL_GATE — `f39-kyshtym`

**🟢 VERDE** · 2026-10-27

| métrica | valor | umbral (verde) | piso (rojo) |
|---|---|---|---|
| datos | 203 ✔ | 150 | 40 |
| citas_verificadas | 22 ✔ | 8 | — |
| elegibles_humano | 11 ✔ | 2 | — |
| eventos_con_fecha | 42 ✔ | 10 | 3 |
| personas_con_nombre | 40 ✔ | — | 2 |

Tubería normal: 12 min (≈ 1,500 palabras).
```

(El log imprime la misma compuerta dos veces, `[escaleta] compuerta del pool: verde {...}`, antes y después de la ficha.)

**Hilos:** `research_v3.WORKERS = 8` (`researcher_steps/research_v3.py:46`; R2 descargas y R3 un documento por hilo).
**Ni el log ni los archivos dicen cuántos hilos se usaron.** Por diseño: R2 ≤ 7 (7 fuentes); R3 = un hilo por texto
distinto → 5 documentos leídos (F01, F03, F05, F06, F07; F04 no tiene `_r3_cache`) → 5 hilos. Los mtimes de `_r3_cache/`
se superponen (F06 16:18:28, F05 16:18:38, F03 16:19:35, F01 16:19:36, F07 16:24:00 con sus 4 partes en fila), lo que
cuadra con R3 en paralelo.

**US$ y tiempo** (`01_v3_costos.json`, paso «research»): **US$ 1.4829 · 1 358.7 s** (≈ 22 min 39 s; log 16:04:18 →
16:26:57). Incluye 4a–4e. Desglose con la tabla «por módulo» de `corrida.log` (suma exacta 1.4829, 37 llamadas):

| módulo | llamadas | US$ |
|---|---|---|
| R1 descubrimiento (Pro) | 16 | 0.4722 |
| R1 descubrimiento (Flash) | 4 | 0.0821 |
| R1 fichas del grounding | 1 | 0.0036 |
| R2 fichas desde el texto | 1 | 0.0124 |
| R3 F07 (4 partes) | 4 | 0.5155 |
| R3 F01 / F03 / F05 / F06 | 4 | 0.1302 / 0.1133 / 0.0356 / 0.0232 |
| research v3 perfil del seed | 1 | 0.0029 |
| research v3 vocabulario del caso | 1 | 0.0088 |
| motor (sin tag) = 4a–4e | 5 | 0.0831 |

Línea de tiempo **estimada por mtimes** (el log no tiene hora por sub-paso): R1 16:04:18 → 16:17:30 (`_r1_cache.json`)
≈ 13 min · R2 descargas 16:17:46–48, `manifest.json` 16:18:11 · R3 16:18:11 → 16:24:00 ≈ 5 min 50 s · R4/R5 +
compuerta → `00_pool_v3.json` 16:24:49 · 4a–4e 16:24:49 → 16:26:57.

#### 2. 4a–4e (Flash)

**No se pueden separar en `01_v3_costos.json`: están dentro de «research».** Estimación:
- US$: la línea `motor (sin tag)  5 calls · in 50,151 · out 4,459 · think 22,757 · $0.0831` del resumen por módulo de
  `corrida.log` (5 llamadas = 4a, 4b, 4c, 4d, 4e) → **≈ US$ 0.0831** (estimación).
- tiempo, por mtimes: `00_pool_v3.json` 16:24:49 → `01_facts_sources.json` 16:25:14 (4a) → `02_canonical.json` 16:25:27
  (4b) → `03_meta.json` 16:25:39 (4c) → `04_summary.json` 16:26:25 (4d) → `05_visual_canon.json` 16:26:57 (4e) →
  **≈ 128 s** (estimación).
- El log dice `✓ f39-kyshtym registrado · ... · fuentes: 5 · datos: 12` (esos 5/12 son de 4a/`research_summary`, no del pool).

#### 3. ficha (`ficha_caso.json`)

`modelo` gpt-6.1-sol · `esfuerzo` high · `prompt_version` f23-1 · `titulo` «Desastre nuclear Kyshtym Mayak» ·
`pool_md5` b846eeb1529bb861877fb128c89d7f78. (`meta` no existe; los conteos están en `conteos` y `conteos_crudo`.)

| clave | crudo (`conteos_crudo`) | final (`conteos`) |
|---|---|---|
| hechos | 70 | **70** |
| citas | 17 | **16** |
| escenas | 10 | **9** |
| personas | 54 | **54** |
| personas_descartadas | 2 | 1 |
| cifras | 34 | 30 |
| cronologia | 62 | 62 |
| contradicciones | 8 | 7 |
| decisiones | 12 | 11 |
| versiones | 4 | 4 |
| descartados | 24 | 33 |
| humanos_candidatos / giros / pico / pregunta_final | 4 / 6 / 1 / 1 | 4 / 6 / 1 / 1 |

**Sacados: 10** (`sacados`; `chequeo.sacados` por sección: cifras 4 · escenas 1 · contradicciones 1 · decisiones 1 ·
personas_descartadas 1 · citas 1 · descartados 1).
**US$ 0.3956 · 428.1 s** (paso «ficha»; log 16:26:57 → 16:34:05; resumen por módulo `ficha_caso 1 call $0.3956`).

#### 4. escaleta (`01a_escaleta.json`)

`prompt_version` f26-1 · modelo claude-fable-5-1 (resumen por modelo: Fable 4 llamadas = escaleta 1 + guionista 1 +
editar frase 2). No hay `01a_escaleta_rechazada*.json`.

- **Intentos: 1** (`_intentos`). Intento 1: **0 bloqueantes**, 9 reparaciones, 13 no bloqueantes (log: «intento 1: 0
  bloqueante(s) [] · 9 reparación(es) · 13 a métricas»).
- `_reparaciones` (9): «beat 9: apoyo L09 no existe en el pool → fuera»; «a_pantalla D18: cap 6 inválido o lleno → fuera»;
  «a_pantalla D43: cap 6 inválido o lleno → fuera»; y 6 recortes de palabras objetivo por cap (cap 1 220→110, cap 2
  500→250, cap 4 520→250, cap 5 550→250, cap 6 560→250, cap 7 500→140).
- `_avisos`: [] (vacío).
- **Humano:** P43 Anatoly Ivanovich Valevich (fuente F07). En la ficha está en `historia.humanos_candidatos` y también en
  `personas_descartadas`. `_metricas.humano_en_escena_caps` [1, 2, 4, 6, 7], `humano_entra_cap` 1.
- **Antagonista:** `institucion`, D01 «Complejo químico Mayak». `_metricas.antagonista_caps` [].
- **Pico:** **beat 5** (cap 4), id T28; `_metricas.pico_es_el_de_la_ficha` true.
- Beats: 12 (por cap 1, 2, 1, 2, 2, 2, 2); curva de intensidad [4, 1, 2, 3, 5, 2, 4, 4, 3, 4, 3, 3].
- **`a_pantalla`: 5** (D03 cap 1, D17 cap 4, D20 cap 6, D90 cap 6, D83 cap 7). En `caps[].pantalla_ids` hay **12** en
  total (1, 1, 2, 2, 2, 2, 2) con lo que suma el plan del pool; `_pantalla_por_fecha` mueve 2 y saca 5 (cap lleno o
  repetido).
- No bloqueantes (13, `_intentos[0].no_bloqueantes`): cap 3 con menos de 2 beats; falta beat de intensidad 1 después del
  pico; beat 5 con Valevich en escena sin dato suyo verificado; imagen del gancho sin cifras; la última frase no nombra
  al humano; la última frase repite textual Q18; falta la pregunta de pantalla en los 7 caps.
- **US$ 0.8105 · 157.6 s** (paso «escaleta»; log 16:34:05 → 16:36:43).

#### 5. guion (`01b_guionista_v4.json`, `01b_narration.json`, `01b_narracion_v3.json`, `06_judge_narrative.json`)

`prompt_version` f25-1 · ficha f23-1 · modelo claude-fable-5-1 · `nota_b` null.

**Bloqueantes:** antes de la reparación **2** → después **2** (`reparacion.bloqueantes_antes` / `bloqueantes_despues`;
`reparacion.parada` true). Pasos: `regenerados` 0, `ediciones` 2 (**las dos rechazadas**, `motivo_rechazo` «tocó otras
frases del párrafo», `despues` == `antes`), `fechas` 0, `editor` 0 (fuera del camino desde F27). Los 2 que quedan, enteros:

```json
{"codigo": "a", "cap": 2, "beat": 2, "frase": "Lo que se decía en esas calles quedó anotado tal cual: «La fábrica es nociva, a los trabajadores los llaman 'chocolateros', mueren como moscas.", "motivo": "entre comillas, pero no es una cita del pool: «La fábrica es nociva, a los trabajadores los llaman 'chocola…»"}
{"codigo": "a", "cap": 5, "beat": 8, "frase": "El Chelyabinsky Rabochy publica que el domingo pasado por la noche «muchos habitantes de Cheliábinsk observaron un resplandor especial en el cielo estrellado…", "motivo": "entre comillas, pero no es una cita del pool: «muchos habitantes de Cheliábinsk observaron un resplandor es…»"}
```

Log: `[v4] quedan 2 bloqueante(s) después de la ronda única: PARADA`. La cadena igual sigue a partición, papel y juez (así
está escrito `fase1_5.run_guion_v4`), y el RESUMEN final solo muestra «PARADA en papel».

**`metricas`** (sobre el texto de la reparación, antes de la partición): `palabras` 1925 · `largo` «1925 palabras ≈ 13.4
min» · **`citas` 11** · `puntaje` 60 · `duras_v3` 39 · `blandas_v3` 38 · `humano_caps` [1, 2, 4, 6, 7] · `cierre`
«pregunta» · `ecos` 1 · `antagonista_tipo` institucion · `antagonista_caps` 0 · `fechas_literales_por_cap` 0 en los 7 ·
`ids_por_parrafo` antes 11.38 / después 1.52.

**Palabras** (`split()` sobre cada texto; el juez cuenta con su tokenizador):

| cap | guion = reparación (`01b_guionista_v4` párrafos) | objetivo (`metricas.palabras_por_cap`) | **final** (`01b_narration.json` = `01b_narracion_v3.json`) | juez m05 |
|---|---|---|---|---|
| 1 | 175 | 110 | **175** | 176 |
| 2 | 323 | 250 | **323** | 324 |
| 3 | 187 | 260 | **187** | 187 |
| 4 | 272 | 250 | **272** | 273 |
| 5 | 333 | 250 | **333** | 333 |
| 6 | 366 | 250 | **356** | 356 |
| 7 | 265 | 140 | **223** | 224 |
| **total** | **1 921** | 1 510 | **1 869** | 1 873 |

La partición (`m01d_particion.rebalance` con `shorten=editor_shorten()`) acortó los caps 6 (−10) y 7 (−42): frases
borradas, p. ej. «Salió por la puerta.» (cap 6) y «Un hombre viejo con carpetas de juicio.» (cap 7).
**≈ minutos a 2,4 palabras/s:** final 1 869 → 778.8 s ≈ **12.98 min**; guion 1 921 → 800.4 s ≈ 13.34 min.
Caps fuera de banda en `duras_v3`: corto el cap 3 (187 < mín. 221); largos los caps 1, 2, 5, 6, 7 (máx. 126 / 288 / 288 /
288 / 161); los caps 6 y 7 siguen por encima del máximo después del acorte.

**Juez m05** (`06_judge_narrative.json`, 16:45:42; sin llamadas a modelo, no tiene línea en el resumen de costos):
`video.densidad` 1.44 (mín 2.0) · `adj_100` 0.59 (mín 2.0) · `trigramas_repetidos` 0.0309 (máx 0.05) · `datos_distintos`
27 · `palabras` 1873 · `problemas_de_fechas` 4 · `pantalla_dichos` 1 («cap 4: [D17] …») · `caps_con_repetidos_en_cap`
[4, 5, 6] · `caps_fuera_de_adjetivos` [1–7] · `antagonista` «Igor Vasilyevich Kurchatov» (la escaleta dice «Complejo
químico Mayak») · cliffhangers ok 2 de 6 (caps 1, 2) · `umbral`: densidad ✗ · repeticion ✓ · adjetivacion ✗ ·
repeticion_en_cap ✗ · nombres ✓ · antagonista ✓ · cliffhanger ✗ · `violaciones_narrador` {}.

**US$:** guionista_v4 **1.0680** (201.8 s) + reparacion_v4 **0.1048** (33.3 s; 2 llamadas «editar frase», ninguna
aceptada) = **1.1728**.

**Fecha del evento:** el perfil (`_perfil.json`) solo da el año: **1957** (`anio_evento`, puntual); día y mes no están en
el perfil. En el pool, T28 = `fecha` 1957-09-29, `hora` 16:22. **La voz sí la dice**, en letras, en la primera oración
del cap 4: «Domingo veintinueve de septiembre de mil novecientos cincuenta y siete.», y la hora: «Son las cuatro y
veintidós.» (en F23 no decía el día). Otras: cap 1 «Cheliábinsk-40, mil novecientos cincuenta y siete.»; cap 5 «Lunes
treinta de septiembre.» y «Seis de octubre de mil novecientos cincuenta y siete.». `fechas_literales_por_cap` da 0
porque mide dígitos.

#### 6. partición (`01a_skeleton.json`)

1. Un misterio ardiente
2. Un proyecto oculto
3. Temperatura descontrolada
4. El golpe seco
5. La verdad oculta
6. Verdades contradictorias
7. El largo silencio

**US$ 0.1310 · 120.5 s** (paso «particion»; resumen por módulo `m01d_particion 3 calls $0.1310`; por los totales por
modelo, deducido: 2 Pro + 1 Flash).

#### 7. papel (`01e_pantalla.json`; el `.md` lo pega CC)

`prompt_version` m01e-6 · `prompt_md5` 3b98aef1d8595124967ac7a85b75bab7 · `modelo` claude-sonnet-5-5 · `effort` medium ·
`intentos` 5 · resultado: 11 fichas · 8 sellos · 6 relojes · 50 `descartados` (del modelo: 44 voz_lo_dice, 3 otro,
2 spoiler; 1 de validación).

- **Vueltas: 4** (`reintento.vueltas`). Llamadas (`por_intento`): 1) in 48 038 / out 20 545 · US$ 0.3015 · 141.8 s;
  2) 55 105 / 1 312 · 0.1233 · 11.7 s; 3) 54 524 / 218 · 0.1112 · 2.1 s; 4) 54 538 / 1 354 · 0.1226 · 12.0 s;
  5) 54 561 / 209 · 0.1112 · 2.3 s.
- **Cierre: `tope`** (`reintento.cierre`). `tope` = US$ 1.00, «respaldo (el perfil no trae costos.m01e_tope_usd)»;
  `error`: «gastado 0.7699 + esta llamada hasta 0.3032» → sin quinta vuelta.
- **Cortados al cierre: 0** (`cortados_al_cierre`).
- **Picos vacíos: 1** — ch01 beat 1 (`picos_vacios`). (m01e marca 7 beats como pico: ch01 b1, ch02 b3, ch03 b4, ch04 b5,
  ch05 b7, ch06 b10, ch07 b11.)
- **`a_pantalla` vacíos: 1** — ch01 beat 1, D03 (`a_pantalla_vacios`).
- **US$ 0.7699 · 172.6 s** (`usd` 0.76992; paso «pantalla»).

**Motivos por vuelta** (`reintento.vueltas[].motivos`; log: cada vuelta «fichas fuera 1 · preguntas nuevas 0 · picos
vacíos 1»):

| vuelta | beats | motivos que la dispararon | aplicado | US$ |
|---|---|---|---|---|
| 1 | ch01 b1, ch02 b3, ch04 b5, ch06 b10 | **D03** en ch01 b1 fuera (`no_dicho` … «(gancho)»); D31, D09 ×2, D90: preguntas de spoiler/no_dicho (las 3 se mantuvieron: «otro hecho»); D122, T61, D152 «vuelve a ser candidato»; «el beat 1 de ch01 es pico y quedó sin ficha»; «… quedó sin ninguno de los datos que la escaleta dejó para la pantalla …: D03» | ch01 b1: ficha + sello | 0.1233 |
| 2 | ch01 b1 | **D50** en ch01 b1 fuera (`no_dicho` … gancho); D122, T61, D152 (iguales); pico sin ficha; D03 sin pantalla | ch01 b1: ficha | 0.1112 |
| 3 | ch01 b1 | **D03** otra vez («NIVEL OFICIAL DEL ACCIDENTE · 6 en una escala de 7») fuera (`no_dicho` … gancho); D122, T61, D152; pico sin ficha; D03 sin pantalla | ch01 b1: ficha + sello | 0.1226 |
| 4 | ch01 b1 | **D201** en ch01 b1 fuera (`no_dicho` … gancho); D122, T61, D152; pico sin ficha; D03 sin pantalla | ch01 b1: ficha | 0.1112 |

Al cierre, el único `descartado` de validación es D03 en ch01 b1 («NIVEL 6 DE 7», regla `no_dicho`): la salida de la
vuelta 4 volvió a proponer D03.

**c3/g4 de F38e: sí.** Las vueltas 2, 3 y 4 se gastaron solo en ch01 beat 1, con los mismos dos motivos cada vez
(«pico y quedó sin ficha» y «a_pantalla D03 vacío»). Cada propuesta del modelo para ese beat (D03 → D50 → D03 → D201 →
D03) la sacó la misma regla `no_dicho` del gancho. D03 es justo el `a_pantalla` que la escaleta reservó «sin que la voz lo
lea». Además, D122, T61 y D152 («vuelve a ser candidato») salieron iguales en las 4 vueltas y ninguna vuelta los tocó
(`aplicados` siempre ch01 b1; `ignorados` 0). Gasto de las vueltas 2–4: US$ 0.3450.

#### 8. Costos y tiempos por paso (`01_v3_costos.json` `_corridas`)

| paso | modelo (resumen por modelo/módulo de `corrida.log`) | llamadas | US$ | s | ventana en el log |
|---|---|---|---|---|---|
| research (incl. 4a–4e) | Gemini 2.5 Pro + Flash | 37 | 1.4829 | 1 358.7 | 16:04:18 → 16:26:57 |
| ficha | gpt-6.1-sol high | 1 | 0.3956 | 428.1 | 16:26:57 → 16:34:05 |
| escaleta | claude-fable-5-1 | 1 | 0.8105 | 157.6 | 16:34:05 → 16:36:43 |
| guionista_v4 | claude-fable-5-1 | 1 | 1.0680 | 201.8 | 16:36:43 → 16:40:04 |
| reparacion_v4 | claude-fable-5-1 | 2 | 0.1048 | 33.3 | 16:40:04 → 16:40:38 |
| particion | Gemini (2 Pro + 1 Flash, deducido) | 3 | 0.1310 | 120.5 | 16:40:46 → 16:42:47 |
| pantalla | claude-sonnet-5-5 medium | 5 | 0.7699 | 172.6 | 16:42:47 → 16:45:39 |
| **total `_corridas`** | | **50** | **4.7627** | **2 472.6** (41 min 12.6 s) | |

- Resumen por modelo al final de `corrida.log`: **TOTAL 50 calls · US$ 4.7626** (Fable 1.9833 · Sonnet 0.7699 · Flash
  0.1993 · Pro 1.4145 · gpt-6.1-sol 0.3956). Las 21 líneas «por módulo» suman 50 llamadas y US$ 4.7627.
- **Diferencia `_corridas` vs resumen: US$ 0.0001 = redondeo** (cada paso se guarda a 4 decimales). No hay gasto fuera de
  `_step_cost`: cada módulo del resumen cae en algún paso (las llamadas también cuadran, 50 = 50), y el juez m05 no hace
  llamadas (no tiene línea).
- Reloj: 16:04:16 → 16:45:42 = 2 486 s; los pasos suman 2 472.6 s; los ≈ 13 s restantes quedan fuera de los pasos
  (arranque, registro, 16:40:38 → 16:40:46 entre reparación y partición, juez m05 16:45:39 → 16:45:42).
- Tope de la tanda US$ 5.00 (`lab/TOPE_TANDA.json`): no se pasó (4.7627).

#### 9. Lado a lado con F23 (misma semilla; solo números)

Fuentes F23: `lab/hyperframes/f23/F23_REPORT.md`, `resumen_f23.json`, `fuentes_f23.json`, `manifest_f23.json`,
`ficha_kyshtym_f23.json`, `guion_kyshtym_f23.json`, `run_research.log`, `POOL_GATE.md`; y
`data/scripts/_steps/f18-kyshtym-mayak/00_pool_v3.json` (mtime 2026-10-24 23:05; misma compuerta 154/21/16/56/23 que F23).

| | F23 (`f18-kyshtym-mayak`) | F39 (`f39-kyshtym`) |
|---|---|---|
| perfil | 1948–1967, prolongado; ru · en · es | 1957–1957, puntual; ru · en · es |
| fuentes R1 | 10 (ru 9 · en 1 · es 0) | 7 (en 4 · ru 3 · es 0) |
| descartadas R1 | 42 (en 19 · ru 19 · es 4) | 29 (en 18 · ru 9 · es 2) |
| bajadas | 8 (ru 7 · en 1) | 6 (ru 3 · en 3) |
| con aporte al pool | 8 (ru 7 · en 1) | 5 (ru 3 · en 2) |
| datos del pool por idioma | ru 136 · en 18 | ru 193 · en 10 |
| compuerta | verde | verde |
| · datos | 154 | 203 |
| · citas_verificadas | 21 | 22 |
| · elegibles_humano | 16 | 11 |
| · eventos_con_fecha | 56 | 42 |
| · personas_con_nombre | 23 | 40 |
| research US$ / s | 1.2127 / 1 301 (perfil, R1, R2, R3, R5) | 1.4829 / 1 358.7 (incluye 4a–4e ≈ 0.0831) |
| ficha: hechos / citas / escenas / personas / sacados / US$ | 74 / 16 / 12 / 45 / 14 / 0.3343 | 70 / 16 / 9 / 54 / 10 / 0.3956 |
| escaleta: intentos (bloqueantes) / US$ | 2 (26 → 0) / 0.3222 (gpt-6.1-sol) | 1 (0) / 0.8105 (Fable) |
| guion: bloqueantes al final | 0 | 2 |
| palabras (`split`) | 1 446 | 1 921 guion · **1 869** final |
| ≈ min a 2,4 palabras/s | 10.0 (el reporte F23 dice 11.8, con otra tasa) | 13.34 guion · 12.98 final |
| citas (`metricas.citas`) | 8 | 11 |
| palabras por cap | 111 · 76 · 81 · 134 · 122 · 601 · 319 | 175 · 323 · 187 · 272 · 333 · 356 · 223 (final) |
| caps cortos (bajo el mínimo del cap) | 4: caps 2, 3, 4, 5 (76, 81, 134, 122 vs 204–212) | 1: cap 3 (187 vs 221) |
| duras_v3 / puntaje | 34 / 34 | 39 / 60 |
| ¿dice el día del evento? | no | sí (cap 4, «veintinueve de septiembre», y la hora) |
| partición / papel | no corrieron en F23 | US$ 0.1310 / 0.7699 |
| total de la cadena Kyshtym | 2.7437 (research + ficha + escaleta + guion; la tanda F23 fue 2.7471 con perfiles de otros temas) | 4.7627 |

### B.4 — Papel: `01e_pantalla.md` ENTERO (`data/scripts/_steps/f39-kyshtym/01e_pantalla.md`, md5 `763346a690de98109221e1a32d2211c2`; copia en `lab/hyperframes/f39/b/salida/`)

````markdown
# Guion de pantalla en papel — f39-kyshtym

`m01e_pantalla` m01e-6 (md5 del prompt `3b98aef1d8595124967ac7a85b75bab7`) · claude-sonnet-5-5 medium · 5 intento(s) · US$ 0.7699 · tokens de entrada 48038

Segundos por palabra 0.3459 (mediana de 200 oraciones de 9 caps del narrador N9Z5MLTIaHFLflaLtbDi) · tope US$ 1.0 (respaldo (el perfil no trae costos.m01e_tope_usd)) · intento 1: in 48038 · out 20545 · US$ 0.3015 · intento 2: in 55105 · out 1312 · US$ 0.1233 · intento 3: in 54524 · out 218 · US$ 0.1112 · intento 4: in 54538 · out 1354 · US$ 0.1226 · intento 5: in 54561 · out 209 · US$ 0.1112 · **tope US$ 1.00 (respaldo (el perfil no trae costos.m01e_tope_usd)): gastado 0.7699 + esta llamada hasta 0.3032**

Totales: 11 fichas · 8 sellos · 6 relojes · 50 descartados

## ch01 — Un misterio ardiente

- beat 1 · gancho · PICO · ficha — ⚠ pico sin ficha · sello **MEMORIA** en [7] · ⚠ sin su a_pantalla: D03 (lo puso y cayó: no_dicho: D03 es del pool del video y la narración lo dice en algún cap (gancho))
- relojes: —

## ch02 — Un proyecto oculto

- beat 2 · planteo · ficha **D194** [normal] «LAS DOS PRIMERAS PROMOCIONES · Murieron casi por completo» en [9] sobre «Mayak» (54/90 car.) · respaldo: «Las dos primeras promociones de trabajadores de la planta murieron casi por completo.» · año — / relato 1957 · aporta: Pone en una consecuencia concreta lo que significaba trabajar en Mayak; la voz no lo dice. · sello **AMENAZA** en [10]
- beat 3 · planteo · PICO · ficha **D31** [normal] «EL CÉSPED ERA CAMUFLAJE · Tierra de 2 metros de espesor» en [15] sobre «césped» (52/90 car.) · respaldo: «Sobre la estructura se colocó una capa de tierra de 2 metros de espesor y césped para camuflaje.» · año — / relato 1957 · juzgado por el autor: otro hecho {'spoiler': ['2']} · aporta: Explica para qué estaba el césped y da el espesor de tierra que lo cubría; la voz solo dice 'tierra y césped'. · sello **CALMA** en [15]
- relojes: —

## ch03 — Temperatura descontrolada

- beat 4 · escalada · PICO · ficha **T14** [normal] «TANQUES DE ALMACENAMIENTO · Construidos en 1950» en [0] sobre «contenedores» (44/57 car.) · respaldo: «Se construyeron los tanques de almacenamiento de residuos radiactivos en el complejo Mayak. (fecha 1950)» · año 1950 / relato 1956 · aporta: Dice cuándo se construyeron los tanques: ya tenían años de uso cuando empezaron las fugas. La voz no da ese año. · sello **INMINENTE** en [11]
- relojes: 9 MAR 1957 en [6], 10 ABR 1957 en [6]

## ch04 — El golpe seco

- beat 5 · pico · PICO · ficha **D09** [normal] «ESTIMACIONES MODERNAS · Entre 8 y 170 toneladas de TNT» en [9] sobre «TNT» (51/90 car.) · respaldo: «estimaciones modernas la sitúan entre 8 y 170 toneladas» · año — / relato 1957 · juzgado por el autor: otro hecho {'no_dicho': ['TNT'], 'spoiler': ['8']} · aporta: Concreta el 'mucho más' de la voz con el rango que dan las estimaciones modernas. · sello **COLAPSO** en [8]
- beat 6 · respiro · ficha **D17** [normal] «LA ZONA CONTAMINADA · 270.000 habitantes, 217 localidades» en [19] sobre «franja» (54/90 car.) · respaldo: «con 270.000 habitantes en 217 localidades» · año — / relato 1957 · aporta: Pone en personas y pueblos el alcance de la franja; la voz solo da su largo. · sello —
- relojes: 29 SEP 1957 en [0]

## ch05 — La verdad oculta

- beat 7 · giro · PICO · ficha **D93** [normal] «HABITANTES DE LA CIUDAD · 86.000 personas siguieron ahí» en [9] sobre «opción» (52/90 car.) · respaldo: «La ciudad de Ozerk, con 86.000 habitantes, no fue evacuada» · año — / relato 1957 · aporta: Da el número de personas que se quedaron en la ciudad; la voz no lo dice. · sello **SILENCIO** en [5]
- beat 8 · escalada · ficha **D138** [normal] «LAS CALLES MÁS CONTAMINADAS · Lenin y Shkolnaya» en [16] sobre «calles» (44/90 car.) · respaldo: «Las calles más contaminadas en Cheliábinsk-40 fueron la calle Lenin y la calle Shkolnaya.» · año — / relato 1957 · aporta: Nombra las calles que las mujeres barrían y lavaban; la voz no las nombra. · sello **ALARMA** en [17]
- relojes: 6 OCT 1957 en [12]

## ch06 — Verdades contradictorias

- beat 9 · consecuencia · ficha **D163** [normal] «LA GRANJA QUE NO TUMBARON · 50 casas, laboratorio médico» en [3] sobre «casas» (53/90 car.) · respaldo: «El sovkhoz de 50 casas no fue liquidado, sino que se dejó como laboratorio para realizar investigaciones médicas.» · año — / relato 1958 · aporta: Muestra una excepción al entierro total: una granja de 50 casas quedó en pie para estudios médicos. · sello **RABIA** en [5]
- beat 10 · revelacion · PICO · ficha **D90** [papel] «LOS QUE LIMPIARON · Unos 30.000 trabajadores y militares, 1957-1959» en [16] sobre «trabajaba» (64/90 car.) · respaldo: «Entre 1957 y 1959, unos 30.000 trabajadores del combinado y militares recibieron dosis de radiación superiores a 0,25 Sv» · año — / relato 1960 · juzgado por el autor: otro hecho {'spoiler': ['1959']} · aporta: Da la escala de gente que hizo la limpieza sobre la que hay versiones enfrentadas. · sello —
- relojes: —

## ch07 — El largo silencio

- beat 11 · revelacion · PICO · ficha **D83** [normal] «ENFERMOS POR RADIACIÓN · Más de 2000 trabajadores, 1948-1958» en [7] sobre «enfermedad» (57/90 car.) · respaldo: «Entre 1948 y 1958, más de 2000 trabajadores fueron diagnosticados con enfermedad profesional por radiación.» · año — / relato 1989 · aporta: Contrasta en silencio con la declaración de Buldakov: más de 2000 casos diagnosticados en Mayak. · sello —
- beat 12 · cierre · ficha **D149** [normal] «LA LEY CAMBIABA · Casi cada año, durante 10 años» en [12] sobre «perdió» (45/46 car.) · respaldo: «se modificó casi anualmente durante 10 años» · año — / relato 1998 · aporta: Explica por qué reclamar era tan difícil: la ley de liquidadores cambiaba casi cada año. · sello —
- relojes: 13 ABR 1958 en [0], 16 JUN 1989 en [4]

## Lo que cayó

- ch01 beat 1 · ficha D03 «NIVEL 6 DE 7 · Escala internacional de accidentes» en [1] → **no_dicho**: D03 es del pool del video y la narración lo dice en algún cap (gancho)

## Reintento: los motivos que se le mandaron al autor

- D03 (ch01 beat 1) «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7»: no_dicho: D03 es del pool del video y la narración lo dice en algún cap (gancho)
- D31 (ch02 beat 3, oración [15]) «EL CÉSPED ERA CAMUFLAJE · Tierra de 2 metros de espesor»: la voz dice «2» en una oración posterior en ch04 [2] («Dos equipos de la ciudad en la cancha, y en las gradas muchachos de la edad de Valevich y de los del comedor.»); ¿es el mismo hecho? si no, mantenelo
- D09 (ch04 beat 5, oración [9]) «ESTIMACIONES MODERNAS · Entre 8 y 170 toneladas de TNT»: la voz dice «TNT» en la oración ancla o en una vecina en ch04 [9] («La fuerza se calculó después en veinticinco a veintinueve toneladas de TNT; otras fuentes hablan de mucho más.»); ¿es el mismo hecho? si no, mantenelo
- D09 (ch04 beat 5, oración [9]) «ESTIMACIONES MODERNAS · Entre 8 y 170 toneladas de TNT»: la voz dice «8» en una oración posterior en ch07 [14] («Ayudó a otras ocho personas.»); ¿es el mismo hecho? si no, mantenelo
- D90 (ch06 beat 10, oración [16]) «LOS QUE LIMPIARON · Unos 30.000 trabajadores y militares, 1957-1959»: la voz dice «1959» en una oración posterior en ch06 [20] («En mil novecientos cincuenta y nueve, Valevich se fue.»); ¿es el mismo hecho? si no, mantenelo
- D122: dijiste que la voz lo dice («La voz dice los 8 metros de profundidad.»); la voz de ch02 no dice «8,2» («El tanque que explotó era de acero inoxidable y estaba en un cañón de hormigón a 8,2 metros de profundidad.»): vuelve a ser candidato
- T61: dijiste que la voz lo dice («La voz dice el 16 de junio de 1989.»); la voz de ch07 no dice «Rabochi» ni «Mayak» («El periódico "Chelyabinski Rabochi" publica el primer informe de prensa sobre el accidente de 1957 en Mayak. (fecha 1989-06-16)»): vuelve a ser candidato
- D152: dijiste que la voz lo dice («La voz dice los dos litigios de Valevich.»); la voz de ch07 no dice «2» («A Anatoly Valevich le llevó dos procesos judiciales, primero contra el Fondo de Seguro Social y luego contra la Dirección de Protección Social, para que se le reconocieran sus derechos.»): vuelve a ser candidato
- el beat 1 de ch01 es pico y quedó sin ficha
- el beat 1 de ch01 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D03 («La clasificación nivel 6 de 7 es un rótulo oficial; se muestra bajo el gancho sin que la voz lo lea.»)

### Preguntas y respuesta del autor

- D31 {'spoiler': ['2']}: la mantuvo en ch02 beat 3 [15]: otro hecho
- D09 {'no_dicho': ['TNT'], 'spoiler': ['8']}: la mantuvo en ch04 beat 5 [9]: otro hecho
- D90 {'spoiler': ['1959']}: la mantuvo en ch06 beat 10 [16]: otro hecho

### Reintento parcial: 4 vuelta(s)

#### Vuelta 1 · US$ 0.1233

- beats que podía cambiar: ch01 beat 1, ch02 beat 3, ch04 beat 5, ch06 beat 10
- motivos:
  - D03 (ch01 beat 1) «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7»: no_dicho: D03 es del pool del video y la narración lo dice en algún cap (gancho)
  - D31 (ch02 beat 3, oración [15]) «EL CÉSPED ERA CAMUFLAJE · Tierra de 2 metros de espesor»: la voz dice «2» en una oración posterior en ch04 [2] («Dos equipos de la ciudad en la cancha, y en las gradas muchachos de la edad de Valevich y de los del comedor.»); ¿es el mismo hecho? si no, mantenelo
  - D09 (ch04 beat 5, oración [9]) «ESTIMACIONES MODERNAS · Entre 8 y 170 toneladas de TNT»: la voz dice «TNT» en la oración ancla o en una vecina en ch04 [9] («La fuerza se calculó después en veinticinco a veintinueve toneladas de TNT; otras fuentes hablan de mucho más.»); ¿es el mismo hecho? si no, mantenelo
  - D09 (ch04 beat 5, oración [9]) «ESTIMACIONES MODERNAS · Entre 8 y 170 toneladas de TNT»: la voz dice «8» en una oración posterior en ch07 [14] («Ayudó a otras ocho personas.»); ¿es el mismo hecho? si no, mantenelo
  - D90 (ch06 beat 10, oración [16]) «LOS QUE LIMPIARON · Unos 30.000 trabajadores y militares, 1957-1959»: la voz dice «1959» en una oración posterior en ch06 [20] («En mil novecientos cincuenta y nueve, Valevich se fue.»); ¿es el mismo hecho? si no, mantenelo
  - D122: dijiste que la voz lo dice («La voz dice los 8 metros de profundidad.»); la voz de ch02 no dice «8,2» («El tanque que explotó era de acero inoxidable y estaba en un cañón de hormigón a 8,2 metros de profundidad.»): vuelve a ser candidato
  - T61: dijiste que la voz lo dice («La voz dice el 16 de junio de 1989.»); la voz de ch07 no dice «Rabochi» ni «Mayak» («El periódico "Chelyabinski Rabochi" publica el primer informe de prensa sobre el accidente de 1957 en Mayak. (fecha 1989-06-16)»): vuelve a ser candidato
  - D152: dijiste que la voz lo dice («La voz dice los dos litigios de Valevich.»); la voz de ch07 no dice «2» («A Anatoly Valevich le llevó dos procesos judiciales, primero contra el Fondo de Seguro Social y luego contra la Dirección de Protección Social, para que se le reconocieran sus derechos.»): vuelve a ser candidato
  - el beat 1 de ch01 es pico y quedó sin ficha
  - el beat 1 de ch01 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D03 («La clasificación nivel 6 de 7 es un rótulo oficial; se muestra bajo el gancho sin que la voz lo lea.»)
- aplicados: ch01 beat 1 (ficha/sello)

#### Vuelta 2 · US$ 0.1112

- beats que podía cambiar: ch01 beat 1
- motivos:
  - D50 (ch01 beat 1) «LA FUGA, COMPARADA · Chernóbil liberó 19 veces más»: no_dicho: D50 es del pool del video y la narración lo dice en algún cap (gancho)
  - D122: dijiste que la voz lo dice («La voz dice los 8 metros de profundidad.»); la voz de ch02 no dice «8,2» («El tanque que explotó era de acero inoxidable y estaba en un cañón de hormigón a 8,2 metros de profundidad.»): vuelve a ser candidato
  - T61: dijiste que la voz lo dice («La voz dice el 16 de junio de 1989.»); la voz de ch07 no dice «Rabochi» ni «Mayak» («El periódico "Chelyabinski Rabochi" publica el primer informe de prensa sobre el accidente de 1957 en Mayak. (fecha 1989-06-16)»): vuelve a ser candidato
  - D152: dijiste que la voz lo dice («La voz dice los dos litigios de Valevich.»); la voz de ch07 no dice «2» («A Anatoly Valevich le llevó dos procesos judiciales, primero contra el Fondo de Seguro Social y luego contra la Dirección de Protección Social, para que se le reconocieran sus derechos.»): vuelve a ser candidato
  - el beat 1 de ch01 es pico y quedó sin ficha
  - el beat 1 de ch01 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D03 («La clasificación nivel 6 de 7 es un rótulo oficial; se muestra bajo el gancho sin que la voz lo lea.»)
- aplicados: ch01 beat 1 (ficha)

#### Vuelta 3 · US$ 0.1226

- beats que podía cambiar: ch01 beat 1
- motivos:
  - D03 (ch01 beat 1) «NIVEL OFICIAL DEL ACCIDENTE · 6 en una escala de 7»: no_dicho: D03 es del pool del video y la narración lo dice en algún cap (gancho)
  - D122: dijiste que la voz lo dice («La voz dice los 8 metros de profundidad.»); la voz de ch02 no dice «8,2» («El tanque que explotó era de acero inoxidable y estaba en un cañón de hormigón a 8,2 metros de profundidad.»): vuelve a ser candidato
  - T61: dijiste que la voz lo dice («La voz dice el 16 de junio de 1989.»); la voz de ch07 no dice «Rabochi» ni «Mayak» («El periódico "Chelyabinski Rabochi" publica el primer informe de prensa sobre el accidente de 1957 en Mayak. (fecha 1989-06-16)»): vuelve a ser candidato
  - D152: dijiste que la voz lo dice («La voz dice los dos litigios de Valevich.»); la voz de ch07 no dice «2» («A Anatoly Valevich le llevó dos procesos judiciales, primero contra el Fondo de Seguro Social y luego contra la Dirección de Protección Social, para que se le reconocieran sus derechos.»): vuelve a ser candidato
  - el beat 1 de ch01 es pico y quedó sin ficha
  - el beat 1 de ch01 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D03 («La clasificación nivel 6 de 7 es un rótulo oficial; se muestra bajo el gancho sin que la voz lo lea.»)
- aplicados: ch01 beat 1 (ficha/sello)

#### Vuelta 4 · US$ 0.1112

- beats que podía cambiar: ch01 beat 1
- motivos:
  - D201 (ch01 beat 1) «OTRA MUERTE EN LA PLANTA · Valia Dronova, 38 años: pulmones de piedra»: no_dicho: D201 es del pool del video y la narración lo dice en algún cap (gancho)
  - D122: dijiste que la voz lo dice («La voz dice los 8 metros de profundidad.»); la voz de ch02 no dice «8,2» («El tanque que explotó era de acero inoxidable y estaba en un cañón de hormigón a 8,2 metros de profundidad.»): vuelve a ser candidato
  - T61: dijiste que la voz lo dice («La voz dice el 16 de junio de 1989.»); la voz de ch07 no dice «Rabochi» ni «Mayak» («El periódico "Chelyabinski Rabochi" publica el primer informe de prensa sobre el accidente de 1957 en Mayak. (fecha 1989-06-16)»): vuelve a ser candidato
  - D152: dijiste que la voz lo dice («La voz dice los dos litigios de Valevich.»); la voz de ch07 no dice «2» («A Anatoly Valevich le llevó dos procesos judiciales, primero contra el Fondo de Seguro Social y luego contra la Dirección de Protección Social, para que se le reconocieran sus derechos.»): vuelve a ser candidato
  - el beat 1 de ch01 es pico y quedó sin ficha
  - el beat 1 de ch01 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D03 («La clasificación nivel 6 de 7 es un rótulo oficial; se muestra bajo el gancho sin que la voz lo lea.»)
- aplicados: ch01 beat 1 (ficha)

## Cierre del reintento

- cerró por: **tope** (después de 4 vueltas)
- cortado al cerrar, sin preguntarle al autor: (nada)

## Descartados por el modelo

- Q18 [voz_lo_dice]: La voz dice la cita completa en la oración 6 del capítulo 1.
- D54 [voz_lo_dice]: La voz ya describe la columna rojo-anaranjada.
- D153 [voz_lo_dice]: La voz dice los cincuenta estudiantes trasladados y a Valevich entre ellos.
- Q01 [voz_lo_dice]: La voz dice la cita en la oración 20.
- Q05 [voz_lo_dice]: La voz dice la pregunta de Saprykin.
- Q06 [voz_lo_dice]: La voz dice la respuesta de Kazutov.
- D07 [voz_lo_dice]: La voz dice los 300 m³ y las 70-80 toneladas.
- D30 [voz_lo_dice]: La voz dice las 160 toneladas de la cubierta.
- D122 [voz_lo_dice]: La voz dice los 8 metros de profundidad. — **falso: la voz no dice ['8,2']**
- T20 [voz_lo_dice]: La voz dice las tuberías con fugas y desconectadas en 1956.
- T23 [voz_lo_dice]: La voz dice el llenado entre el 9 de marzo y el 10 de abril.
- D101 [voz_lo_dice]: La voz dice las 70-80 toneladas.
- D46 [voz_lo_dice]: La voz dice el autocalentamiento hasta 330-350 grados.
- Q16 [voz_lo_dice]: La voz dice la cita de Ivanov.
- T28 [voz_lo_dice]: La voz dice las 16:22 del 29 de septiembre.
- D10 [voz_lo_dice]: La voz dice el cráter de 10 por 20 metros.
- D35 [voz_lo_dice]: La voz dice la cubierta de 160 toneladas volando.
- D11 [voz_lo_dice]: La voz dice los 20 millones de curios.
- D12 [voz_lo_dice]: La voz dice el 90 % depositado en el combinado.
- D91 [otro]: La dosis en sieverts no se entiende sola; la cifra de más de 5000 personas ya la dice la voz.
- T32 [voz_lo_dice]: La voz dice el cielo rosado y azul claro.
- T35 [voz_lo_dice]: La voz cuenta los vidrios rotos y la falta de información sobre la radiación.
- T37 [voz_lo_dice]: La voz dice la primera medición a las cuatro de la mañana.
- Q14 [voz_lo_dice]: La voz dice la respuesta del director.
- Q02 [voz_lo_dice]: La voz lee la nota de la aurora casi literal.
- Q07 [voz_lo_dice]: La voz dice que las auroras podrían volver a verse.
- D136 [voz_lo_dice]: La voz dice el dosímetro en la panza del chico.
- D104 [voz_lo_dice]: La voz dice las 600 personas.
- T39 [voz_lo_dice]: La voz dice las 1100 personas y las tres aldeas.
- T43 [voz_lo_dice]: La voz dice los destacamentos de 1958 y 1959.
- D19 [voz_lo_dice]: La voz dice las 23 localidades.
- D21 [voz_lo_dice]: La voz dice los 700 km² cerrados.
- D159 [voz_lo_dice]: La voz dice los vehículos que no se limpiaron.
- D158 [voz_lo_dice]: La voz dice los 200 presos hospitalizados.
- D20 [otro]: El total de reasentados tiene tres cifras distintas entre fuentes; no cabe en una línea sin confundir.
- D40 [spoiler]: Adelanta el total de reasentados y las 23 aldeas que el capítulo 6 cuenta después.
- T50 [otro]: La voz dice que Valevich se fue en 1959; el dato del decreto no cabe bien en los 46 caracteres de la oración.
- D145 [voz_lo_dice]: La voz cuenta al jefe de Belenkov y su agonía.
- Q11 [voz_lo_dice]: La voz lee la cita de la mujer.
- Q21 [voz_lo_dice]: La voz lee la pregunta a Gutnikov.
- Q03 [voz_lo_dice]: La voz dice la declaración de Buldakov.
- D44 [voz_lo_dice]: La voz dice el Berlingske Tidende y el 13 de abril de 1958.
- T57 [voz_lo_dice]: La voz dice el informe de Medvedev en 1976.
- T61 [voz_lo_dice]: La voz dice el 16 de junio de 1989. — **falso: la voz no dice ['Rabochi', 'Mayak']**
- T62 [voz_lo_dice]: La voz dice la sesión del Sóviet Supremo.
- D152 [voz_lo_dice]: La voz dice los dos litigios de Valevich. — **falso: la voz no dice ['2']**
- D156 [voz_lo_dice]: La voz dice el riñón perdido en 1998.
- T64 [voz_lo_dice]: La voz dice el estatus de liquidador en 1993.
- D14 [spoiler]: Habla de la emisión radiactiva y adelanta la explosión del capítulo 4.
````

**Lectura del papel (hechos, sin juicio de calidad):** 4 vueltas de reintento parcial y cierre por **tope** (US$ 0,7699 + hasta 0,3032 > 1,00). Las 4 vueltas se gastaron en **un solo beat, el gancho de ch01** (marcado también PICO): en cada vuelta el autor propuso un dato distinto (D03 → D50 → D03 → D201) y cada uno cayó por **no_dicho del gancho** («es del pool del video y la narración lo dice en algún cap»). Resultado: **el gancho quedó sin ficha** (contra DECISIONES 2026-10-26 14:28, «el gancho nunca queda vacío») y el `a_pantalla` D03 sin poner. Es el patrón c3/g4 de F38e (vueltas gastadas en un motivo que no se va), esta vez en el gancho. Los tres «la voz lo dice» falsos (D122, T61, D152) se repitieron en las 4 vueltas sin que el autor los tomara. Los otros 11 beats tienen ficha; 3 fichas «juzgadas por el autor: otro hecho» (D31, D09, D90).

### B.5 — Nada corrió después del papel
- En `corrida.log` no hay ninguna línea de `normalizer_gate`, `audio`, `m07`, `m03`, `assemble` ni fase2a (grep vacío).
- `output/f39-kyshtym/`: **no existe** (nada en `output/` para el topic).
- Archivos nuevos de `data/scripts/_steps/f39-kyshtym/` (todos los del topic; hora · bytes · nombre):
```
16:17:30   31530 _r1_cache.json
16:17:30   28859 fuentes_r1.json
16:17:45    3643 _perfil.json
16:17:51       — fuentes/ (14 archivos)
16:19:43       — _r3_cache/ (10 archivos)
16:24:49   93594 00_pool_etiquetado.json
16:24:49  599530 00_pool_v3.json
16:24:49    9435 fuentes.json
16:25:14  673500 01_facts_sources.json
16:25:27     213 02_canonical.json
16:25:39     729 03_meta.json
16:26:25    3955 04_summary.json
16:26:57    9148 05_visual_canon.json
16:34:05     386 POOL_GATE.md
16:34:05  105087 ficha_caso.json
16:34:05  107289 ficha_respuesta_cruda.json
16:34:05   69930 FICHA_f39-kyshtym.md
16:36:43   31195 01a_escaleta.json
16:40:46   57817 01b_guionista_v4.json
16:42:46   13305 01a_skeleton.json
16:42:46   39093 01b_narracion_v3.json
16:42:46   25968 01b_narration.json
16:45:39   46993 01e_pantalla.json
16:45:39   20013 01e_pantalla.md
16:45:39  716080 01e_pantalla.raw.json
16:45:39     561 01_v3_costos.json
16:45:42    5910 06_judge_narrative.json
```
- Escrituras en `data/` fuera de `_steps/f39-kyshtym/` (todo lo que cambió desde el tope): `data/topics_db.json` (`57c711ad…` → `b7cbcbf2…`, con el topic `f39-kyshtym` «Kyshtym Mayak: La Explosión Nivel 6 Que Rusia Ocultó», `seed_title` guardado, `status researched`), su respaldo **`data/topics_db.pre_f39-kyshtym.json`**, `data/cost_history.json` (`3d422423…` → `3d988013…`) y **`data/geocode_cache.json`** (`6746fede…` → `9e2ce85b…`: el geocodificador del pool, Nominatim; **no estaba en la lista de escrituras declaradas del handoff**, abierto f8). Ninguna otra.


## Lo que queda abierto (entero)
**De B (hallazgos de la corrida; para la nota 1–10 del analista, cada uno «se queda / se arregla a mano / frena» lo decide él):**
- f1. **El gancho de ch01 quedó sin ficha** (contra DECISIONES 2026-10-26 14:28): las 4 vueltas del papel se gastaron en ch01 beat 1 (D03 → D50 → D03 → D201), cada propuesta cortada por `no_dicho` del gancho; cierre por **tope**. Es c3/g4 de F38e: la vuelta sigue mientras «los motivos cambian», aunque cambian solo de candidato en el mismo beat con la misma regla. D03 es el `a_pantalla` que la escaleta reservó «sin que la voz lo lea» y m01e lo corta porque la narración sí lo dice: escaleta y validación chocan en ese punto. US$ 0,3450 en las vueltas 2–4.
- f2. **El tope del papel es el de respaldo** (1,00): el handoff dice `costos.m01e_tope_usd` del perfil, pero el perfil vigente (`a67ed45`) no trae esa clave. Agregarla es de Omar (perfil).
- f3. **La compuerta del papel es solo para la cadena v3** (la única que produce papel). Un topic viejo sin v3 sigue a la voz como antes. Además, todo topic v3 existente sin `aprobado` vigente ya no pasa a la voz: el flujo manual de Omar lo va a notar (riesgo del revisor).
- f4. **La compuerta del pool corre dos veces** (en `fase1_5` antes de la ficha y dentro de `generate_escaleta`): no cuesta, reescribe el mismo `POOL_GATE.md`; el log la imprime dos veces.
- f5. **Código que quedó sin lector por A.2:** `escaleta_notas` (lo carga `fase1_5._topic_v3`; solo lo leía `build_prompt`, borrado) y `pool["digest"]` (lo arma `research_v3.build_digest`; solo lo leía `pool_section`, borrado). No se tocaron: borrar `digest` cambia el pool y el `pool_md5` de las fichas. Y 4 scripts históricos de lab ya no corren (`f7/f7c_orleans.py`, `f14/f14_orleans.py`, `f15/f15_corridas.py`, `f15b/f15b_corridas.py`); son registro, no llamadores vivos.
- f6. **El guion terminó con 2 bloqueantes** (código «a», comillas que no son cita del pool, caps 2 y 5) y la reparación de una ronda no cambió nada (las 2 ediciones rechazadas: «tocó otras frases del párrafo»). `run_guion_v4` imprime «PARADA» pero la cadena sigue a la partición y al papel (así desde F11); el resumen final solo muestra la PARADA del papel. Si el guion con bloqueantes debe frenar la cadena antes del papel, es una regla nueva del analista.
- f7. **El juez m05 no tiene paso propio en `01_v3_costos.json`** (no llama a modelos; corre 16:45:39 → 16:45:42).
- f8. **`data/geocode_cache.json` cambió** (Nominatim, del pool): no estaba en la lista de escrituras declaradas (§8). Además `data/topics_db.pre_f39-kyshtym.json` (el respaldo, previsto).
- f9. **El research no muestra su progreso en consola** (`investigar_semilla` llama `run_seed` sin `log=`; F23/F24 lo guardaban en `run_research.log`). Los datos de B.4 del research salen de los archivos de `_steps/`; los hilos usados no quedan registrados (por diseño, 5 en R3).
- f10. **El research no trajo ninguna fuente en español** aunque el perfil la pide; el 68 % de los datos (139 de 203) sale de un documento (F07, veteranrosatom); F02 (Facebook) no bajó y F04 (Grokipedia «Alyoshenka») bajó sin aporte. El perfil quedó «puntual 1957» (F23: 1948–1967, prolongado).
- f11. **La partición acortó los caps 6 (−10 palabras) y 7 (−42)** con `rebalance`/`shorten`: la narración final (1 869) no es la del guion reparado (1 921); los caps 6 y 7 siguen por encima del máximo y el cap 3 está corto (187 < 221).
- f12. **El juez m05 nombra otro antagonista** («Igor Vasilyevich Kurchatov» contra «Complejo químico Mayak» de la escaleta; `antagonista_caps` 0) y falla 4 de 7 umbrales (densidad, adjetivación, repetición en cap, cliffhanger).
- f13. **Valevich (el humano) está dos veces en la ficha**: en `historia.humanos_candidatos` y en `personas_descartadas`.
- f14. **Tres «la voz lo dice» falsos** (D122, T61, D152) volvieron como candidatos en las 4 vueltas y el autor nunca los tomó.
- f15. **La escaleta (Fable) cuesta 2,5 veces la de F23 (gpt-6.1-sol)**: US$ 0,8105 contra 0,3222. Con papel y partición, Kyshtym semilla → papel = US$ 4,76 (F23 semilla → guion: 2,74).
- f16. **La voz ahora dice la fecha del evento** («Domingo veintinueve de septiembre de mil novecientos cincuenta y siete», cap 4, y la hora); en F23 no la decía. El perfil no trae día ni mes (solo el año).

**De A:**
- f17. `aprobar_papel` reescribe `01e_pantalla.json` con `indent=1` (el md5 de la aprobación no depende del formato; riesgo menor si algo compara bytes).
- f18. La ficha se paga antes de la escaleta: si la escaleta falla por un bloqueante, la ficha ya está gastada (solo la frena el tope de la tanda).
- f19. Un `--semilla` que paró en la compuerta roja deja `_steps/<id>/` escrito (perfil, fuentes, pool, `POOL_GATE.md`): reintentar con el mismo id da PARADA «ya existe» (coherente con «no pisa nada»; hay que usar otro id o borrar a mano).
- f20. `investigar_semilla` exige `discovery_mode` en la semilla (lo usaba `_enrich` después de pagar): una semilla sin esa clave para antes de gastar.
- f21. Con `RESEARCH_V3=0`, `investigar_semilla` corre el camino viejo de 4 ángulos (no fuerza v3), como `research_topics`.
- f22. `seed_title` solo lo guarda este camino; `research_topics` sigue sin guardarlo (topics viejos: la ficha lo busca en `seeds_archive.json` por `seed_id`, y si no está, PARADA).

**Lo de siempre, fuera de la tanda:** B5 y d1 (prompt), forma F31b, subtítulos documentales, formato de cifras del research (c9 de F38c), c1 de F38e (regla del autor), y los abiertos de F38e (a1–a9, b1–b10, c1–c11, d1–d5, e-E1–e-E8, g1–g14).

## Procesos (paso 12 de `/tanda`)
Subagentes: escaleta, research, simulador, revisor intermedio, B.4 y revisor final: todos terminaron; ninguno vivo. Shells en segundo plano: el candado de A y la corrida de B (terminados). Ningún proceso de la tanda vivo; no se cerró nada de Omar.

## Veredicto del revisor (`revisor-handoff`, íntegro) — final, sobre paso 0, A y B
VEREDICTO: CUMPLE CON OBSERVACIONES

Alcance: paso 0, A y B contra el handoff (md5 d2cfa61b… verificado) y el pedido literal. No corrí fase1_5, fase2b, modelos ni la suite amplia, y no escribí en data/. Corrí `pytest test_module_f39_*.py`: 24 passed.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 0 | Paso 0: secretos, commit DECISIONES+handoff, perfil aparte, push | OK | md5 DECISIONES 3ab85591… y handoff d2cfa61b… coinciden. Commits d49178d y a67ed45. Búsqueda de secretos en `f39/paso0_secretos.txt`. Push pegado en el reporte, main intacta. |
| A | A.1–A.5, 3 commits por parte, 24 tests, candado | OK | `git diff ccbc303 HEAD --stat` cuadra con el reporte (m01a −375, fase1_5 +201, topic_researcher +45, 3 tests f39 nuevos). Candado: ch02 38e5ba14, rápida 58, amplia 913+5 previas. Esos números los tomé del reporte y de `a_candado/`, no los recorrí. |
| B.0 | Semilla usada y por qué | OK | `semilla_kyshtym.json` y `f18/seed_f18.json` dan md5 499ad52a… (idénticos). El reporte dice que el seed_id no está en `seeds_archive` y pega el seed_title. |
| B.1 | Topic limpio, nada de f18-kyshtym-mayak | OK | `_perfil.json`, `fuentes.json` y `_r1_cache.json` tienen md5 distintos a los de f18. Los 49 archivos de f39-kyshtym tienen mtime 16:17–16:45, posterior al arranque de la corrida, y `_r3_cache` es de 16:19. Un solo md5 coincide: `fuentes/wikipedia_2023-F01.txt`. Es la misma página de Wikipedia bajada de nuevo (mtime de esta corrida), no una copia. |
| B.2 | Tope US$ 5,00 | OK | `lab/TOPE_TANDA.json` = {"usd": 5.00, "desde": "2026-10-27T16:03:55"}, anterior al arranque 16:04:16. |
| B.3 | Una sola corrida, sin manos | OK | `_inicio.txt` 16:04:16 y `_fin.txt` 16:45:42. El log no tiene Traceback y los mtimes de los pasos son continuos. El reporte declara exit 0 y que la cadena paró en la compuerta del papel. |
| B.4 | Salida por paso, `01e_pantalla.md` entero | OK | El `.md` en disco y su copia en `b/salida/` tienen md5 763346a6…. Diff del bloque pegado contra el archivo (sin su primera línea): sin diferencias, 181 líneas en ambos. Están todos los ítems del handoff, incluido el lado a lado con F23 y la fecha del evento. |
| B.4b | Costos por paso y total vs tope | OK | `01_v3_costos.json` suma 4,7627 (1,4829+0,3956+0,8105+1,0680+0,1048+0,1310+0,7699). Es menor que 5,00 y coincide con la tabla del reporte. El resumen del log (4,7626) lo explica como redondeo. |
| B.5 | Nada después del papel, `output/` vacío para el topic | OK | grep de `normalizer_gate`, `assemble` y `fase2a` en el log da 0. No existe `output/f39-kyshtym`. La lista de archivos del reporte coincide con el `ls` de `_steps/f39-kyshtym`. |
| Frenos | Escrituras en data/ declaradas | PARCIAL | Se escribieron `topics_db.json`, `topics_db.pre_f39-kyshtym.json` y `cost_history.json`, previstos. También `geocode_cache.json`, que no estaba previsto. El reporte lo declara como f8. `data_antes_md5.txt` lo respalda, pero ese cambio queda sin respaldo propio. |
| Frenos | Cero cambios de prompt | OK | En el diff de A solo cambia código de m01a (se borraron funciones y prompts de la rama vieja), sin tocar prompts vigentes. `prompts_md5.txt` y el reporte dan los md5 de los prompts vigentes y los de SYSTEM_V2 y SCHEMA_FICHA coinciden con los de f930596. |
| Abierto | «Lo que queda abierto» entero | OK | f1–f22 más «lo de siempre». Cubre el gancho sin ficha, el tope de respaldo, el guion con 2 bloqueantes, la compuerta duplicada y el geocode. |
| Cierre | Veredicto íntegro de revisor-handoff y ESTADO | NO VERIFICABLE | Hoy el reporte tiene solo la revisión intermedia de A. Este veredicto falta pegarlo. `lab/ESTADO_SESION.md` figura modificado pero sin commit. |

Observaciones:
1. En el B.3 del reporte, la ruta de «Leer:» aparece con las barras invertidas comidas (`C:\CLAUDE_PROJECTSutomatization_videos…`). El log real la tiene bien (línea 55), así que el error es de copia y no de la corrida.
2. El hallazgo f1 es grave para la nota: el gancho de ch01 quedó sin ficha porque las vueltas 2–4 se gastaron en el mismo beat (US$ 0,3450). El reporte lo dice sin suavizar, así que no es incumplimiento del contrato.
3. El guion terminó con 2 bloqueantes y la cadena siguió al papel. El reporte lo declara como f6.
4. No cuadran dos cosas del reporte. El costo del research (1,4829, incluye 4a–4e) y los hilos usados son estimaciones por mtime, no datos medidos. Y el tope del papel usa el valor de respaldo de 1,00, porque el perfil no trae `costos.m01e_tope_usd`.

Fuera de alcance: ninguno en los commits de la tanda. Quedan sin commitear `diag_234_cap4.py` y `lab/hyperframes/f28/a/f28a.log`, que son de otras tandas. También quedan sin commitear `lab/ESTADO_SESION.md` y `f39/{F39_REPORT.md,a_candado,b,verificar.sh,paso0_secretos.txt}`, como se anunció.

Riesgos que el contrato no cubre:
- Todo topic v3 existente sin `aprobado` vigente ya no pasa a la voz; Omar lo va a notar en el flujo manual.
- Un `--semilla` que para en la compuerta roja deja `_steps/<id>/` escrito, y reintentar con el mismo id da PARADA. Hay que usar otro id o borrar a mano.
- La ficha se paga antes de la escaleta, y solo el tope de la tanda frena un gasto repetido si la escaleta falla después.

### Adenda de CC (después del veredicto; el texto de arriba queda tal cual)
- Observación 1: la ruta de «Leer:» de B.3 se reemplazó por la línea literal del log (`corrida.log` línea 55). El error era de copia (las barras invertidas se tomaron como escapes al armar el reporte).
- Fila «Cierre»: este veredicto quedó pegado acá; el reporte, `lab/ESTADO_SESION.md` (cabecera, «Para Omar (F39)», bloque F39), `lab/hyperframes/f39/{a_candado,b,verificar.sh,paso0_secretos.txt}` entran en el commit final.
- Fila «Frenos / data/»: `geocode_cache.json` queda declarado (f8) con sus md5 antes (`6746fede…`, en `lab/hyperframes/f39/b/data_antes_md5.txt`) y después (`9e2ce85b…`); no tiene respaldo propio porque es una caché de Nominatim que la corrida solo amplía.
- Observación 4: correcto; en B.4 el desglose 4a–4e (≈ US$ 0,0831, ≈ 128 s) y los hilos (5 en R3) están marcados como estimación, y el tope de respaldo es f2.
- En `b/` no entran `_data_*`, `data_antes_md5.txt` sí (evidencia), ni `_inicio.txt`/`_fin.txt` sí (la hora de la corrida).
