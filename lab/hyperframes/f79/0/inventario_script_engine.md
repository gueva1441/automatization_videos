# F79 Etapa 0 — inventario fuera de `fase2b.py` (código de 210873b)

(i) texto de un prompt · (ii) clave de caché · (iii) imagen que ve un modelo · (iv) clave de caché de capas/segmentos.

| archivo:línea | qué hace | i | ii | iii | iv |
|---|---|---|---|---|---|
| `gfx_config.py:197` | `title_pre_roll: bool = True`; solo lo lee fase2b (1167, 3592) | — | — | — | — |
| `script_engine/gfx_layer.py:133,155` | `build_scenes(pre_roll)`; Veo `start`: corte en `veo_dur + pre_roll` | — | — | indirecto (escenas → `_zoom_frame`) | indirecto (escenas → plan resuelto) |
| `gfx_layer.py:431,436` | `escenas_a_disco` escribe `"pre_roll"` en `gfx_escenas_<cap>.json` (lo leen fase2b 2891, 3042) | — | — | — | — (el md5 de aprobación es de `gfx_plan_ch*.resolved.json`) |
| `gfx_layer.py:533,546,606,610,764` | `apply_gfx(pre_roll)` lo pasa a `preparar_cap`, `build_scenes`, `escenas_a_disco` | — | — | — | — |
| `gfx_layer.py:454-465, 664` | `plan_base(ctx)`: title card a todo cap con título (sin tiempos, sin modelo); único llamador 664 | — | — | — | — |
| `pantalla_entrada.py:94,155` | `preparar_cap(pre_roll)` → `ent["pre_roll"]`: **campo muerto** (nadie lo lee; no va a prompt ni a disco) | — | — | — | — |
| `gfx_guion.py:7, 123-124` | docstrings («intro y pre-roll ya sumados») | — | — | — | — |
| `gfx_guion.py:121-155` | `inicio_de_voz` / `_pcm`: medición de audio; ventana `esperado − primera − buscar_s` y `desde = esperado − 2·RAMPA_S` asumen aire antes de la voz | — | — | — | — |
| `gfx_guion.py:253-264` | texto de la costura («intro … sin voz», «sin voz (pre-roll …)»), `tramos.intro_s`, `title_card_s` | solo GUION_PANTALLA (lo leen personas) | — | — | — |
| `gfx_guion.py:521` | chequeo de costuras: `offset − mezcla["intro"]` | — | — | — | — |
| `gfx_guion.py:555-558` | chequeo de música: «title card» con `title_card_s` (de fase2b 3085) | md/json | — | — | — |
| `gfx_guion.py:616-641, 675, 682` | `armar(intro)`, `intro_s`, `pre_roll`, `pre_pad` en el json; «intro X s», «pre-roll X s» en el md | md/json | — | — | — |
| `gfx_critic.py:53-56` | docstring de `clave_identidad` (dice que no usa bytes porque el pre-roll corre el cap) | — | — | — | — |
| `gfx_critic.py:146-152` | `ident = clave_identidad(…, round(t,2), …)`, `t` en tiempo del cap (incluye pre-roll) | — | **sí** (aceptado, §5.4) | — | — |
| `gfx_critic.py:158` | `frame_at(base, tf)`: el cuadro del base (con pre-roll adelante) que mira Gemini | — | — | **sí** (mismo cuadro, otro segundo) | — |
| `gfx_critic.py:172` | fila con `t` al `resolved["critico"]` | — | — | — | indirecto (sidecar `chXX_gfx.plan.md5`) |
| `mixer_server.py:261` | comentario que nombra `INITIAL_SILENCE_SEC` | — | — | — | — |
| `.claude/skills/guion-de-pantalla/SKILL.md:23` | doc «intro de 2.5 s y pre-roll ya sumados» (instrucción a CC, no prompt del pipeline) | — | — | — | — |

El prompt del crítico (`build_prompt_rot`, gfx_critic.py:80-95) lleva `desc`, `voz`, `aporta`, `por_que`: ningún tiempo.
Cero coincidencias en `run_pipeline.py`, `qa_studio_server.py`, `pantalla_colocar.py`, `clima.py`, `voz_datos.py`.
Falsos positivos (otro concepto): `tramos` de época (asset_manager, foto_madre, m03_visual), de intensidad (music_intensity), de DEBERÍA (m01f_critico), `intro_sec: 0.8` del channel_bug en `gfx_profiles/misterio.json:107` (no lo lee ningún .py).

**`chXX_visual_preroll.mp4` viejos en `_fase2b_work/`:** después de F79 nadie los genera ni los lee por nombre, pero el glob `{cap}_*visual*.mp4` de `_segment_hash` (fase2b 2676) los sigue sumando al hash del segmento (tamaño + mtime) si quedan en disco. Eso solo invalida un segmento reusado (lo rehace), no hace que se lea su contenido. Se lista; no se borran (no es de esta tanda tocar `_fase2b_work/` fuera de `--plan-only`).
