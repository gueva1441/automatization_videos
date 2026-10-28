# Notas de auditoría — zona fase2b_gfx, parte fase2b_gfx_d

Los 12 archivos se leyeron enteros. Ninguno cambió de md5 durante el trabajo (no se tocó ninguno). Todas las rutas son de `script_engine/` salvo que se diga otra cosa.

## Código muerto o sin uso (más allá de las 4 funciones confirmadas)
- `gfx_pool.py:79` `literal_icon_map`: solo la llama `content_icon` (muerta); en producción tampoco la nombra nadie. Con ella quedan sin uso `MISSING_ICONS` (45), `_PEOPLE` (49) y `_NEVER_ICON_ALONE` (53).
- `gfx_pool.py:404` `FORMA_CALL`: constante que nadie lee (el «paso de forma de los recortes» se borró).
- `gfx_pool.py:407` `_hits`: nadie la usa; `evidence.py:122` tiene su propia `_hits` con otra firma.
- `gfx_pool.py:411` `_NUM`: regex sin ningún uso en el archivo ni fuera.
- `gfx_pool.py:361-363`: cabecera «S2 — cronología» sin código debajo.
- `gfx_pool.py:376-377` y `clima.py:61`: leen/cuentan `quote_card`, bloque que `pantalla_colocar.py:175` deja siempre en `None` (F36 D lo borró). Ojo: `gfx_project.py:530,802` y `gfx_guion.py:286` también lo leen, o sea que el bloque sigue en el render aunque ya nadie lo llena.
- `gfx_intensity.py:30` `MIN_CARGAS`: no se usa (solo `MAX_CARGAS`). `gfx_intensity.py:56` `_plain`: no se usa.
- `gfx_vision.py:37` `HUMAN`, `:50` `_plain`, `:54` `_tok`: no se usan en el archivo y nadie los importa.
- `gfx_realizador.py:175` `FUENTES_CIERRE`: tupla que nadie lee (las fuentes se devuelven como strings sueltos).
- `gfx_realizador.py:226` `finalizar(plan, real, log)`: el parámetro `real` no se usa. `gfx_realizador.py:250` `cerrar(...)`: `pool` y `side` no se usan (gfx_layer.py:781-783 igual los pasa).
- `gfx_literal_lock.py:44-45` `lock(..., question_sources=…)`: el parámetro no se usa («queda por compatibilidad del lab»); gfx_layer.py:704/725 igual lo pasa.
- `gfx_realizador.py:128` `candidatos` (con `ya_dicho`, `_voz_en`, `ya_mostrados`): lo que calcula solo termina en un log (gfx_layer.py:272) y en `gfx_beats_<cap>.json`; ningún consumidor lee `real["candidatos"]` para decidir nada. Los `ya_mostrados` además los fabrica `gfx_pool.used_ids_before` en gfx_layer.py:267 solo para esto.
- `pantalla_entrada.py:155` `"ya_mostrado": []`: la clave de la entrada siempre va vacía y nadie la lee (el filtro «ya mostrado» está en `pantalla_colocar.py:201` con `used_before`).

## Comentarios y docstrings que contradicen el código
- `pantalla_filtros.py:227`: dice «pantalla_entrada.del_papel»; esa función no existe (la que hace eso es `pantalla_entrada.preparar_cap`).
- `pantalla_filtros.py:251` (comentario sobre `ORDEN`): menciona `escena_final`, que `pantalla_colocar.py:296` dice que `repartir` reemplazó.
- `pantalla_filtros.py:2-3` y `pantalla_colocar.py:3`: «antes pantalla_filtros» / «antes pantalla_colocar» (el nombre nuevo igual al viejo; parece un reemplazo masivo que pisó el nombre anterior).
- `gfx_realizador.py:17` y `gfx_layer.py:254-255,262`: dicen que sin escaleta gfx_layer «sigue por el camino de siempre»; desde F37 el papel es el único camino y sin escaleta (`rot_on` falso, gfx_layer.py:634) el cap sale sin fichas ni sellos.
- `gfx_realizador.py:6-14`: el docstring de módulo sigue describiendo candidatos obligatorios/opcionales y topes como si decidieran algo; hoy solo sirven de log.
- `gfx_pool.py:2` («Todo detrás de `if pool`: un guion sin pool sigue con verified_facts exactamente como antes») y `gfx_pool.py:4-9`: describen funciones que ya no existen (`pool_clause_options` se presenta como de gfx_pool, pero la usa solo `m01a_skeleton` vía `finalize_pool_plan`).
- `gfx_pool.py:120`: «piezas de gfx_fragments (borrado)»; el módulo `gfx_fragments` ya no existe y las piezas viven acá.
- `gfx_critic.py:87-88` (`build_prompt_rot`): el prompt promete «IMAGEN 2: el mismo instante con el bloque ya dibujado», pero `estorba` (gfx_critic.py:159) llama con una sola imagen (`call(Path(img), prompt)`); el prompt dice que hay dos y se manda una (el docstring de estorba dice «foto sola»).
- `gfx_critic.py:83`: el prompt siempre incluye «EL ROTULISTA DICE QUE APORTA: «»» con texto vacío, y pide tres respuestas (`SCHEMA_ROT` las exige todas, :73-77) aunque solo cuenta `estorba`.
- `gfx_critic.py:23` / `pantalla_colocar.py:225-226`, `:189`, `:339`: siguen los nombres `rotulista`, `tipo_rotulista`, `critico_rotulista` de un módulo que se llama ahora `pantalla_*` (`gfx_literal_lock.py:70,74` filtra por `c.get("rotulista")`, o sea que ese nombre viejo es el que decide qué pasa por el candado).
- `gfx_pool.py:137`: línea con un bloque largo de espacios en medio (`and bool(...)` pegado tras 9 espacios), resto de una continuación de línea; funciona pero no se lee.
- `pantalla_colocar.py:173`: comentario «filtros importa este módulo arriba» (import circular: `pantalla_filtros.py:15` importa pantalla_colocar al tope y pantalla_colocar importa pantalla_filtros dentro de `colocar`).

## Números sin origen claro (no figuran en DECISIONES, identidad F3 ni estándar citado en el mismo archivo)
- `pantalla_colocar.py:221` `era_decade: 2000` fijo para todo recorte tipo documento, sea de la época que sea.
- `pantalla_colocar.py:208-210,214-216`: `side: "left"` fijo en fichas/citas (comentado solo como «la del title card»).
- `gfx_pool.py:455` `t < last + 2.0` y `:461` `start + 12.0`, `:458` tope de 2 cambios: constantes sueltas sin nombre (solo `TICKER_HOLD` 4.0 y `TICKER_MIN` 2.0 tienen nombre y comentario F5f).
- `gfx_pool.py:145` `DOC_MAX_WORDS = 10`, `:481` `COUNT_SAME_TOL = 0.15` (comentado «±15 %»), `:494` umbral `n < 100`: origen F5b/F5e, no una decisión citada.
- `gfx_critic.py:147` `dur` por defecto 2.5 s, `:61` «1 s después de que entra / a mitad si dura menos de 2 s», `:45` ancho 1280, `:188-211` medidas de la hoja de contactos (640, 62, 19, 15, 88): sin origen.
- `gfx_vision.py:38` `MIN_CONF = 0.6`, `:63` lados de caja 0.06–0.3 (repetidos también dentro del texto de `SYSTEM`, :41-42), `:85` tope de 3 detalles: sin origen citado.
- `gfx_intensity.py:29-31` `ATTEMPTS = 2`, `MAX_CARGAS = 5`, `ASK_CARGAS = 10`: citados a «F4c R1», no a una decisión de Omar.
- `pantalla_colocar.py:19` `LECTURA_CPS = 15.0` sí cita su origen (§0 estándar de subtitulado); `pantalla_filtros.py` usa `LECTURA_CPS` importado.

## Rutas o nombres de la cadena vieja que siguen
- `gfx_realizador.py:39` lee `01b_narracion_v3.json` (nombre «v3» con el guion v4 vigente); también `fase2b.py:1559`. La partición lo sigue escribiendo con ese nombre (`m01d_particion.py:243`), así que es consistente pero el nombre quedó de F10.
- `gfx_pool.py:12-34`: el docstring conserva la historia de F5b–F5f (recortes, contador, cita) de bloques borrados; el propio texto dice «quedan como referencia».
- `gfx_director.py:47` cita «DOC_MAESTRO §6» para una deuda de `verified_facts` sin id; no se verificó que siga vigente.

## Otras cosas raras
- `estado_a` de A coincide en los 12 archivos (todos «vivo»); la diferencia está en las etapas: A marca casi todos con `research`…`render` porque `fase1.py`, `fase2a.py`, etc. alcanzan estos módulos por import. Leyendo el código: `aprobar_guion` no corre ninguno (fase2b.py:3719-3732 solo llama `script_engine.aprobacion.aprobar`); `fondos` (fase2b sin `--gfx`) no los corre (el import de gfx_layer es perezoso, fase2b.py:1213); `research`, `papel` y `voz` tampoco. En `guion` corren los que importa `m01e_pantalla`/`m01a_escaleta`/`m01a_skeleton` (fase1_5.py:434 `run_pantalla`; gfx_pool, pantalla_filtros, pantalla_colocar, gfx_realizador.beat_de_pantalla, clima.vocabulario_clima, gfx_peak vía voz_utils).
- Cuatro de las capas que usan modelo o crítico están detrás de tokens del perfil con default `False` en el dataclass (`gfx_config.py:268-279`: `peak_blocks`, `intensity_director`, `photo_first_zoom`, `visual_critic`); `gfx_profiles/misterio.json` trae esas claves, pero el valor que realmente rige no se leyó (regla de la tanda). Por eso `gfx_intensity`, `gfx_vision` y `gfx_critic` están marcados «vivo» pero su ejecución real depende de esos valores. `realizador` (default `True`, gfx_config.py:195) no está en el perfil.
- `voz_datos.py:22` importa `gfx_realizador._raices` (función privada) desde otro módulo; `gfx_realizador.py:91` a su vez usa `evidence._FUNC` y `evidence._content` (privados de otro módulo).
- `gfx_pool.py` es importado por `m01a_skeleton.py`/`m01a_escaleta.py` (Fase 1) y por la capa gráfica (Fase 2): sirve a dos etapas distintas; cualquier cambio de este archivo afecta `guion` y `render`.
- `gfx_intensity.py:129,139`: la regla `_stamp_rule()` (token `stamp_nouns_only`, default `False`, gfx_config.py:280) condiciona dos validaciones; si el perfil lo deja en `False`, las cargas verbales y las palabras del tema no se filtran.
- `pantalla_filtros.py:195-222` `lectura`: la variable `antes` se incrementa con `antes += 0 if entran else 1` (cuenta solo los fallos previos al primer éxito); funciona, pero la lógica de `movido_corte` depende de ese contador y no está probada en ningún test que nombre `lectura` (A: `tests` de `lectura` = 0 en la lista de funciones).
