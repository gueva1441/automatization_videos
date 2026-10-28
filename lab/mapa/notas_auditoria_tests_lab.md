# Notas de auditoría — zona tests_lab (F42 §B)

Materia prima para F43: lo raro que vio cada worker leyendo su parte entera, con archivo:línea. Sin propuestas.

<!-- parte tests_lab -->
# Notas de auditoría — zona tests_lab

Base: 480 archivos (210 `test_*.py` de la raíz, 105 sueltos de la raíz, 165 de `lab/`). Salida en `lab/mapa/tests_lab.json`. Todo por lectura y AST; no se ejecutó ni importó nada del repo.

## Roto sin saberlo (10)
- `test_module_02.py:18` — `from script_engine.m02_profiles import ...`: el módulo no existe; error de colecta (`tests_collect.json`). Nadie lo declaró.
- `test_edge_density.py` — error de colecta `No module named 'cv2'` (dependencia que no está en el venv); no importa nada del repo, pero no colecta.
- `lab/hyperframes/f14/f14_orleans.py:172-174`, `lab/hyperframes/f15/f15_corridas.py:189-191`, `lab/hyperframes/f15b/f15b_corridas.py:167-169` — usan `m01a_escaleta.build_prompt` y `.SYSTEM`, que no existen (solo `SYSTEM_V2*`). Están en el rango f13–f26 del a3 pero el a3 nombra `mg.write`/`mc.edit`, no esto; los clasifiqué como no declarados.
- `lab/hyperframes/f20/f20_corridas.py:124,275` y `lab/hyperframes/f21/recheck.py:71` — `research_v3.SUBJECT_RE_DEFAULT` se borró en F21 (`b24c505`). Mismo criterio que el punto anterior.
- `lab/hyperframes/f4c/recorte_marca.py:60` y `lab/hyperframes/f4d/recorte_marca.py:49` — `from script_engine import gfx_bug`; ese módulo se borró en F36 (`9a7522e`). Lo viejo lo saca con `git show`, pero lo nuevo importa el módulo borrado.
- `lab/hyperframes/f5/analizar_sims.py:79-80` — `gfx_pool._default_year` y `narrated_dates`, borrados en F36. El a3 solo nombra `f5/correr_f5_orleans.py` dentro de f5.

## Roto a sabiendas (14)
`lab/_gpt_probe_analista/*` (6 archivos), `_lab_chat66b_m01a_schema.py` (usa `DEVELOPMENT_CAPS`, `MAX_BULLETS_PER_CHAPTER` de `m01a_skeleton`, ya sin ellos), `_lab_chat66b_m01b_schema.py`, `lab/hyperframes/f5/correr_f5_orleans.py:115-183`, `f6/f6c_narracion_orleans.py`, `f7/f7c_orleans.py`, `f10/f10_seco_orleans.py`, `f10/f10_quirurgico_ycua.py:60` (`replace_repeated_dates` de `guion_v3_reglas`, borrada en F23), `f11/f11_convergencia.py:155-157`. Los de `_gpt_probe_analista` y `_lab_chat66b_m01b_schema.py` los metí por el nombre del a3, aunque el detector no vio el símbolo roto en todos.

## Scripts disfrazados de test_*.py (17 con efectos al importar, no colectables)
Hacen `input()`, `APIConfig`, `genai`, `mkdir` o `exit` en el nivel del módulo; un `pytest` sin `--collect-only` los ejecutaría:
- Gastan plata o llaman APIs al importarse: `test_full_pipeline_lab.py:25-27`, `test_lab_v5.py:28-44`, `test_lab_v6.py:35-51`, `test_lab_v7_bhopal.py:47-63` (el incidente de F42 fue con el primero), `test_module_03_smoke.py:22`, `test_module_03_smoke_sync.py:21-31`, `test_music_director_pripyat.py:46`.
- Piden `input()`: `test_3movements_on_4hards.py:57`, `test_3movs_plus_effects.py:93`, `test_explosion_all_movements.py:67`, `test_movements_v12.py:63`, `test_visual_complexity_classifier.py:80`.
- Imprimen o salen al importar: `test_calculate_image_count.py:14`, `test_fase2b_anchor_durations.py:23`, `test_module_03_text_leakage_casing.py:40`, `test_module_05.py:22`, `test_module_flow_director_fallback.py:35-36`.

## Tests que no prueban nada bajo pytest (61, colecta 0, sin `def test_`)
Todos tienen `main()` bajo `__main__`; pytest los importa y no corre nada. Algunos, al ejecutarse a mano, gastan: ElevenLabs con `requests.post` (`test_elevenlabs_music_hook.py`, `test_module_36_*` ×5, `test_module_38_timestamps_lab.py`, `test_module_38b_*`, `test_module_38c_*`, `test_module_38e_voice_ab.py`, `test_module_39_shock_lab.py`) y Gemini (`test_chat50_seed_enrichment.py`, `test_chat51_*`, `test_module_03.py`, `test_module_05_live.py`, `test_module_05_voting_live.py`, `test_t1_t3_fanout.py`, `test_t4_aggregate.py`, entre otros). `test_module_gfx_f4d.py` (27 líneas, F36) tampoco tiene `__main__` ni tests.

## Tests colectados con cero `assert` (revisar si pasan siempre)
Colectan pero el archivo no tiene `assert` ni `pytest.raises`; las funciones devuelven `ok` (misma enfermedad que F41 encontró en `test_run_pipeline.py`: devuelven bool y pytest las da por verdes): `test_chat52_already_es.py`, `test_chat52_atomic_aliases.py`, `test_chat52_decay_none.py`, `test_chat52_dropped_cap.py`, `test_chat52_m03_response_schema.py`, `test_chat52_pick_gate.py`, `test_chat52_variant_label.py`, `test_fase1_nochain.py`, `test_fase3.py`, `test_m03_guarda1_degrade.py`, `test_m06_autopass.py:99` (devuelve `ok`), `test_m09_packaging.py:47,91`, `test_m09_review_server.py`, `test_module_03_plan_anchors.py`, `test_research_parallel.py:75,100`. `test_module_f38c_decimales.py` colecta 12 con solo 3 `assert`. Clasificados `vivo` porque colectan, pero su verde no prueba nada.

## Otros
- `test_fase1_nochain.py:18` — `from fase1_5 import __name__`: línea válida (falso positivo del detector de imports), pero importar `fase1_5` deja un `logs/pipeline_<fecha>.log` (F41 a7).
- `test_module_f5b.py:8`, `test_module_gfx_pool.py:8`, `test_module_gfx_auto_icons.py:7`: el detector marcó `ICON_WHITELIST`, `icon_svg`, `scoped_svg` como rotos; no lo están (viven en `script_engine/gfx_icons/__init__.py`). `test_module_f22.py:57,95` y `test_module_f23.py:35` tampoco: son `str.index`.
- Sin commitear: `test_module_f42_mapa.py` (F42 en curso), 17 archivos de `lab/` y 38 sueltos de la raíz (los `_lab_grok_*`, `_lab_kling_*`, `_probe_*` de las tandas de motores de imagen y el `diag_234_cap4.py`, que ESTADO dice que "no es nuestro y nunca se commitea", `ESTADO_SESION.md:572,654`).
- Los 15 `_probe_*.py` que empiezan con BOM (`_probe_A.py` … `_probe_vsr_real.py`) no parsean con `ast` leído como utf-8; con `python` corren bien.
- No hay duplicados byte a byte (md5) entre los 480.
- `lab/probe_lock_imageref.py`, `lab/probe_orphan_mothers.py` y `lab/diag_237_pausa_ab.py`/`diag_238_ley1_ab.py` están en `lab/` pero sin carpeta de tanda (duplican el patrón de los `_probe_*`/`diag_*` de la raíz).
- Una sola herramienta de lab con llamador vivo fuera de ESTADO: `lab/tools/mapa_modulos.py` (hook `guard_mapa.py`, comando `tanda.md`) y `lab/tools/simular_regla.py` (agente `simulador`).
