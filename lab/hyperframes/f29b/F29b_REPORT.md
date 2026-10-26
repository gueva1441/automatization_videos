# F29b — Rotulista: el texto de pantalla lo escribe alguien, anclado a la oración · REPORTE

CC · 2026-10-26 · rama `f11-guion-v4`. Handoff `HANDOFF_F29b_rotulista.md`; tanda `../f30/PROMPT_CC_tanda_F29b_F30.md` (etapa 1 = parte A; etapa 3 = parte B).
Commits: **A `5ae6177`** + fix `f6527a1`. **Parte B: NO CORRIÓ** — la tanda frenó al final de F30 porque el SSIM, leído estricto, no dio lo que pide su handoff (ver `../f30/F30_REPORT.md`, «PARADA antes de la etapa 3»).
Costos de la tanda en F29b: Claude **US$ 0.114** de 2 (4 llamadas de Sonnet 5.5 en las crudas de ejemplo) · Gemini ≈ US$ 0.001 de 1 (el humo de integración en el scratchpad: el crítico de siempre sobre el sello y el crítico nuevo sobre 2 bloques) · ElevenLabs 0.

## A — El rotulista (`5ae6177`, fix `f6527a1`)
**`gfx_rules.rotulista = False` por defecto** (como pidió la tanda: se prendía recién en la etapa 3). Con el flag apagado, el camino es el de F29: F30 D lo confirma (los 7 planes resueltos idénticos a v3).

### Archivos (líneas)
| archivo | +/− | qué |
|---|---|---|
| `script_engine/gfx_rotulista.py` (nuevo) | +780 | entrada por cap, prompt literal, llamada con caché y reintentos, A.4 determinista, colocación A.4.6, pico del cap, prefetch de los 7 caps en paralelo |
| `script_engine/gfx_layer.py` | +74/− | con rotulista: llamada (caché del prefetch), `colocar` en lugar de `plan_pool_documents`/`pool_count_up`, el pico de la escaleta en lugar de `plan_peak`, sin zoom del director ni `pick_zoom`, sin `enforce_reserved` ni `drop_repeated_callouts`; el final del plan por `gfx_realizador.cerrar` |
| `script_engine/gfx_critic.py` | +130 | `criticize_rotulista` (A.6), `frame_t`, `excluir_rotulista` en el crítico de siempre |
| `script_engine/gfx_realizador.py` | +33 | `cerrar` (orden del final), `finalizar` no reescribe anclaje/duración/topes de los bloques del rotulista |
| `script_engine/music_intensity.py` | +19 | `beat_pico_de_cap` (A.1.5: una sola fuente del pico) |
| `script_engine/gfx_literal_lock.py` | +8 | excepción explícita para `rotulista: true` (traen su propio candado, A.4.3) |
| `script_engine/gfx_project.py` | +4 | el callout acepta `face`/`anim` (cifra en cara anton sin sello) |
| `gfx_config.py` | +5 | `rotulista`, `rotulista_modelo`, `rotulista_effort`, `rotulista_tope_usd`, `garantizar_pico` |
| `fase2b.py` | +13 | prefetch del rotulista (los 7 caps en paralelo) antes del loop de render; `--rotulista-modelo` (fix `f6527a1`: GfxRules es frozen) |
| `test_module_f29b_rotulista.py` (nuevo) | +295 | 20 tests sin red |

### Prompt
`ROTULISTA_SYSTEM` y `ROTULISTA_USER` copiados literal del handoff; un test los compara contra el .md (anclado en `**SYSTEM:**` / `**USER:**`). **md5 (SYSTEM + "\n\n" + USER) = `50e6ae74fd588861e81fb5d2191ab644`.** Los huecos `{…}` del USER se reemplazan por texto; el formato de salida («Devolvé: {"bloques": …}») queda intacto.

### Cómo quedó cada punto
- **A.1 entrada.** Oraciones = `gfx_peak.sentences` (las del `sentence_idx` del pico). Beats = `gfx_beats_chNN.json`. Ítems = `a_pantalla` del cap + `dato_central`/`datos_apoyo` de sus beats, con texto fuente completo, `fuente`, `por_que`.
- **A.1.5 pico único.** `beat_pico_de_cap`: el beat de `escaleta.pico` si es del cap; si no, el más intenso (empate: el primero, la regla que ya usaba music_intensity, así que el audio de Vajont no cambia). La frase es la oración del beat con más raíces en común con su dato; `pico.t` = inicio de esa oración. `gfx_peak` queda de respaldo sin beats.
- **A.2 llamada.** `claude_helpers.make_call(claude-sonnet-5-5, medium)`, JSON sin esquema. Cruda completa (pedido, respuesta de la API, validación de cada intento) en `_fase2b_work/rotulista_chNN.raw.json`, con caché por pedido. Tope chequeado antes de cada llamada (peor caso de 16 000 tokens de salida). Un reintento si no parsea o si A.4 saca algo; otro si faltan `a_pantalla` o salen sin lo que pide su `por_que`. Si no parsea dos veces, el cap sale sin bloques de texto.
- **A.4 determinista.** Anclaje t0 = fin de oración + 0.3 s dentro de la ventana del beat del ítem. Largo ≤ 9 (cifra ≤ 6, lupa ≤ 4). Cifra sin etiqueta → fuera. Candado: cita = subcadena del texto fuente; el resto, cada número (por valor, en dígitos o en letras: «1.910» = «mil novecientas diez») y cada nombre propio en el texto fuente. No dicho ±20 s y spoiler. Topes 5 / gancho 1 / 1 por oración, `a_pantalla` primero.
- **A.4.6 colocación.** cifra → `data_callout` kind figure, cara anton, entrada slide (nunca sello); recorte → `archive_clipping`; cita → `quote_card`; persona → `data_callout` serif; lupa → `evidence_zoom` con la caja de visión del detalle nombrado, confirmada con `verify_crop` (si no aparece, fuera y anotado).
- **A.5.** Con rotulista quedan afuera `garantizar_pico`, los recortes del pool (`gfx_fragments`/`FORMA_CALL`), el contador, el nivel de agua y el zoom del director. Los sellos quedan como hoy.
- **A.6 crítico.** Corre después de todo: `cerrar` hace finalizar → respaldo → crítico. Son los dos sí/no del handoff, con la voz ±20 s y el `aporta`, sobre la foto y el bloque ya dibujado, y el kicker no cuenta. Cualquier «no» saca el bloque. Sin veredicto, el bloque queda. El veredicto se guarda en el bloque. Sin rotulista se mantiene el orden de F29.

### Lecturas y agregados de CC (declarados)
1. **Ya mostrado en paralelo.** Los 7 caps corren a la vez, así que el prompt recibe como «ya mostrado» los `a_pantalla` de los caps anteriores, que salen sí o sí y se conocen de antemano. Lo que salió de verdad en caps anteriores se vuelve a mirar al colocar (`used_ids_before`) y, si se repite, sale.
2. **Persona.** Nombra a alguien que la voz nombra, así que su nombre (los tokens del arranque) no cuenta en «no dicho»; el cargo sí.
3. **Spoiler de nombres.** El test del handoff («Longarone» 75 s después) es un nombre. Un nombre propio cuenta como spoiler si la voz lo dice después de t0 y no lo dijo antes en el cap. Los números cuentan como spoiler siempre que la voz los diga después de t0.
4. **Agregados a A.4.2.** Muñón fuera (empieza en minúscula o termina en preposición/artículo) y lupa ≤ 4 palabras: el prompt los pide y B.5 cuenta muñones. **Texto de la cifra:** si trae «:» o es una frase, se usa tal cual; si es solo el valor, se arma «etiqueta: valor».
5. **«Lo que pide el `por_que`».** Si el `por_que` nombra cifras, esas cifras tienen que estar (los años de contexto como «… de 1943:» no cuentan). Si pide «la cifra», tiene que haber una cifra del texto fuente. Que Q50 salga «como carta del municipio» no se puede medir con reglas: lo mira la hoja.
6. **Reintento.** El error va agregado al final del USER («TU RESPUESTA ANTERIOR TUVO ESTOS PROBLEMAS…»), no como otro turno.
7. **«Título» del cap.** La escaleta no trae títulos: se usan las funciones de los beats («pico · respiro»). En las citas se agrega «(autor: …)» al lado de la fuente: el prompt pide la cita «con el autor» y el formato de la línea no lo traía.
8. **Sin `unidad` en el esquema de salida.** Nivel de agua y contador nunca salen del rotulista; toda cifra es `data_callout`.
9. **Texto del crítico nuevo.** El handoff da las dos preguntas; el SYSTEM y el armado del pedido son de CC (`gfx_critic.SYSTEM_ROT`, `build_prompt_rot`, versión `f29b-1`).
10. **Candado literal.** Los bloques del rotulista pasan con una excepción explícita (`rotulista: true`), como la pregunta generada: su candado es A.4.3.

### Tests (sin red, `test_module_f29b_rotulista.py`, 20)
Prompt literal del handoff · anclaje y ventana (con la cruda de ch06: D192 en la oración 19, que es del beat 10, queda fuera por A.4.1) · duración · candado (cita alterada falla; cifra que no está falla; «266» con etiqueta pasa y sin etiqueta falla; nombre que no está falla) · no dicho («1.910» con la voz diciendo «mil novecientas diez» a ±20 s falla) · spoiler («Longarone» 75 s después falla) · persona · topes (6 → 5; gancho 2 → 1; dos en la misma oración → 1) · `a_pantalla` D245 sin la cifra en liras → un reintento → anotado y no inventado · no parsea dos veces → sin bloques · pico único (con `escaleta.pico`, `pico.t` 19.94 s ≠ el de gfx_peak, oración 19) · orden (el crítico ve el bloque que entra por respaldo; sin rotulista, el orden de F29) · colocación · candado literal · números por valor · `--rotulista-modelo`.
Suite amplia **940 verdes + 5 previas** (01b_pauses ×3, m03_merge_timing ×2); md5 de `--only-cap ch02` sin `--gfx` con `--sw-encode` = **`38e5ba14…`** (`a/onlycap_ch02_nogfx.log`). **Incidente:** el primer `Write` de los tests pisó el `test_module_f29b.py` de F29 B (sfx). Lo detecté por el conteo de la suite y lo restauré desde git antes del commit; los tests nuevos van en `test_module_f29b_rotulista.py`.

### Las dos crudas de ejemplo (`a/rotulista_ch03.raw.json`, `a/rotulista_ch06.raw.json`; fixtures en `fixtures/`)
Sin render: la entrada se armó con el mismo código que apply_gfx, sobre el topic de v3 (`a/f29b_crudas.py`). Cada cap tuvo 2 intentos.
| cap | intento | tokens in/out | US$ | s | lo que dejó A.4 (código final) |
|---|---|---|---|---|---|
| ch03 | 1 | 4251/982 | 0.018 | 8.7 | T21 cifra «Roca desprendida: 3 millones de m³», D71 recorte. Fuera: Q37 (cita de 13 palabras), T18 persona («L'Unità» lo dice la voz), D49 (8 palabras) |
| ch03 | 2 | 4502/2881 | 0.038 | 21.7 | 5 bloques: T21 cifra, T16 recorte «La víctima fue Arcangelo Tiziani.», T27 persona «Giorgio Dal Piaz, geólogo», D71 recorte, D49 cifra «Ancho fisura: Más de 1 m» |
| ch06 | 1 | 5275/1859 | 0.029 | 14.6 | D128 «Muertos en el desastre: 1.910», Q06 «Evacuados de su aldea: 486». Fuera: D192 (oración del beat 10; D192 es del beat 11) → reintento |
| ch06 | 2 | 5572/1780 | 0.029 | 13.9 | D128 «Murieron 1.910 personas en el desastre» (oración 21), D192 «Técnicos muertos en el estribo: 20» (oración 24): los dos `a_pantalla` del cap |
Humo de integración (scratchpad, `apply_gfx(plan_only=True)` de ch06 con el rotulista prendido y la cruda en caché): D128 y D192 quedaron colocados como `data_callout` anton. El pico salió de la escaleta (beat 10, oración 3, palabra «fisura»: un solo sello). El crítico nuevo pasó los dos, con sí/sí.

## B — Vajont v4 con el rotulista: NO CORRIÓ
La etapa 3 dependía de que F30 diera lo que pide su handoff. No dio: SSIM leído estricto. Quedó preparado, sin correr ni commitear el flag:
- `b/hoja_bloques.py`: la hoja de B.3. Por cada bloque, el cuadro en t0 + 1 s (1280 en la hoja y el jpg de 2560 al lado), la miniatura de 360 px, la voz −6 s / durante / +6 s, el `aporta`, el crítico, pool_id, tipo, oración y t0. Es reusable.
- `b/f29b_vajont.py`: copia del topic `f8s3-vajont-f29b`; el rotulista de los 7 caps en paralelo con un tope de 2 − 0.114; los planes en orden con `plan_only`; después el render `--only-cap ch03/ch06` en fila.
- `b/f29b_tabla.py`: la tabla por cap y lo medible de B.5 (muñones, cifras sin etiqueta, números a ±20 s y después, `a_pantalla` 5/5).
- La bandera `fase2b --rotulista` (prende el rotulista y apaga `garantizar_pico`) está guardada como `b/fase2b_rotulista_flag.patch`, no en el código.

## Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Verifiqué la parte A contra el código y los commits. Corrí `python -I -m pytest test_module_f29b_rotulista.py test_module_f29b.py -q`: 23 pasan (20 nuevos + 3 de sfx). `test_module_f29b.py` no cambió desde 6eb6fda (F29 B). No corrí renders ni llamadas a API.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Prompt literal; md5 `50e6ae74…` | OK | Comparé SYSTEM y USER con el .md del handoff: iguales, 0 diffs. md5 recalculado `50e6ae74fd588861e81fb5d2191ab644`. Las crudas guardan el mismo md5, y el USER guardado coincide con `prompt_user(entrada)`. |
| 2 | A.1 entrada, A.2 llamada (Sonnet 5.5 medium, JSON sin esquema, cruda en `rotulista_chNN.raw.json`, tope antes de cada llamada, reintentos) | OK | `gfx_rotulista.py:214-308, 547-619`. Los reintentos son hasta 2 (forma/candado y `a_pantalla` por separado), declarado. |
| 3 | A.1.5 pico único | OK, con lectura propia declarada | `escaleta.pico` real es `{beat:10, id:T57, por_que}`, sin «cap» ni «frase». CC elige la oración por raíces comunes con el dato. Para los caps sin pico de escaleta usa el beat más intenso. Verifiqué que el audio de Vajont no cambia: ch06 beat 10 es el de mayor intensidad (5). |
| 4 | A.4 determinista (anclaje, largo, candado, no dicho, spoiler, topes, `a_pantalla`) | OK / PARCIAL (ver obs. 1) | `gfx_rotulista.py:352-478`. Re-validé las 4 respuestas crudas con el código final: coinciden con la tabla del reporte (ch03: 2 y 5 bloques; ch06: 2 y 2). |
| 5 | A.4.6 colocación | PARCIAL | Cifra, recorte, cita y lupa están. Persona sale como el modelo la escribió («Giorgio Dal Piaz, geólogo»), no «Nombre · cargo». El lado es `quiet_side` de la escena, no «según el sujeto». Ninguna de las dos está declarada. Sin `unidad`, nunca salen agua ni contador: sí declarado (lectura 8). |
| 6 | A.5 fuera del camino | OK | `gfx_layer.py` con `rot_on`: sin `plan_pool_documents`/`FORMA_CALL`, `garantizar_pico`, zoom del director ni `enforce_reserved`. Los sellos quedan como hoy. |
| 7 | A.6 crítico después, dos sí/no, voz ±20 s, `aporta`, el kicker no cuenta, veredicto guardado | OK | `gfx_critic.py` (`criticize_rotulista`), `gfx_realizador.cerrar`. Sin rotulista conserva el orden de F29. |
| 8 | A.7 tests sin red con fixtures ch03/ch06 y cruda guardada | OK / PARCIAL | Cubre los 9 casos del handoff. Van en `test_module_f29b_rotulista.py` porque `test_module_f29b.py` ya existía; el incidente está declarado. Ver obs. 4. |
| 9 | Flag en False; B no corre | OK | `gfx_config.py:220` `rotulista = False`. En `fase2b.py` del HEAD no hay `--rotulista`, solo `--rotulista-modelo`. El patch está en `b/` sin commitear. |
| 10 | Candados de la tanda | OK | Los commits 5ae6177 y f6527a1 no tocan prompts de guion/escaleta/ficha, `.env`, `config.py`, `gfx_profiles` ni `_gpt_probe_analista`. |
| 11 | Costos | OK | `rotulista_costos.json`: 4 llamadas, US$ 0.11421 (0.114 en el reporte), con topes de US$ 2 y US$ 1. El Gemini de ~US$ 0.001 del humo es **NO VERIFICABLE**: el humo vive en el scratchpad. |
| 12 | md5 `--only-cap ch02` sin `--gfx` y suite amplia | OK | `onlycap_ch02_nogfx.log` da `38e5ba14…`, el mismo valor que en los reportes F2, F2b, F3 y F28. `suite_amplia_a.log`: 940 pasan + 5 previas, justo las 5 nombradas. |
| 13 | B no corrida: justificada y declarada | OK | El tope de la tanda manda frenar si el SSIM no da lo que pide el handoff de F30. El handoff de F30 pide ≥ 0.95 por escena. El F30_REPORT documenta 0.9485, 0.940 y 0.947. El F29b_REPORT lo declara en el encabezado y en la sección B. |

Observaciones:
1. **Candado de nombres con un agujero.** `nombres()` ignora el token que abre el texto, como dice el handoff, pero en `persona` ese token ES el nombre. Probé en `validar`: «Mario Bianchi, ingeniero» y «Pedro, ingeniero» pasan aunque «Mario» y «Pedro» no estén en la fuente. Además la persona queda exenta de «no dicho» y de spoiler: un nombre que la voz dice 60 s después pasa. Está declarado el «no dicho» (lectura 2), pero no el agujero del primer token ni la exención de spoiler.
2. **Ventana del beat más laxa que el handoff.** Admite `t0` entre −0.3 s y +0.35 s del beat (`gfx_rotulista.py:383`), y la duración no se recorta a la ventana. Es chico y no está declarado.
3. **El respaldo `garantizar_pico` nunca corre con rotulista.** `garantizar=gfx_rules.garantizar_pico and not rot_on`. El test «el crítico juzga lo del respaldo» solo prueba `cerrar` aislado, no el cableado real. El `rot_on` completo de `apply_gfx` no tiene test de integración. Solo hubo un humo de `plan_only` en ch06 en el scratchpad, que no queda en el repo. La rama de lupa de `colocar` nunca se ejercitó con visión real.
4. **Tests débiles en dos puntos.** `test_rotulista_modelo_por_cli` solo busca texto en el fuente de `fase2b.py`. `test_cruda_de_ch03` apenas afirma algo. El test de pico único compara contra `gfx_intensity.peak_sentence`, no contra `gfx_peak`.
5. **Inconsistencias menores en el reporte y las crudas.**
   - «20 tests / 940 verdes» mezcla el estado antes y después del fix: el log de la suite es de 5ae6177 (19 tests) y el fix agregó 1.
   - No hay log de la suite rápida de A.
   - El campo `validacion` guardado dentro de las `.raw.json` es de una versión anterior del código. Por ejemplo, el intento 1 de ch03 muestra solo D71, y el código final da T21 y D71. Se revalida al leer de caché, así que no afecta, pero el artefacto no coincide con la tabla.
6. **Atribución de commits.** Los dos commits llevan «Co-Authored-By: Claude Opus 5.5», no la línea vigente de Sonnet 5.5. Es cosmético.
7. `F29b_REPORT.md` sigue sin commitear y la sección del veredicto dice «(pendiente)». Hay que pegar este texto íntegro y commitear.

Fuera de alcance: ninguno en 5ae6177 ni f6527a1. En el árbol sin commitear, ajenos a F29b: `gfx_profiles/*`, `diag_234_cap4.py` y `f28a.log`. `lab/hyperframes/f29b/b/` y `F29b_REPORT.md` son lo esperado.

Riesgos que el contrato no cubre:
- Con la parte B sin correr, el cableado completo del rotulista en `apply_gfx` (render, lupa, crítico con snapshots) no se ejercitó nunca fuera de un humo.
- El tope de costo del prefetch se mide por directorio de trabajo, y 7 llamadas en paralelo ven todas el mismo gasto inicial. El tope de la tanda (US$ 2 menos US$ 0.114) solo se aplica si el script `b/f29b_vajont.py` lo fija. Con el flag de `fase2b` solo, valdría 2.0.

**Después del veredicto (CC):** no toqué código: la tanda está en PARADA. Obs. 1 (el primer token de «persona» no pasa por el candado de nombres, y la persona queda exenta de spoiler), obs. 2 (tolerancia de la ventana de −0.3/+0.35 s y duración sin recortar) y obs. 3 (sin test de integración de `apply_gfx` con el rotulista; la lupa sin probar con visión real) quedan **abiertas para antes de correr B**, junto con los dos riesgos (el tope del prefetch en paralelo ve el mismo gasto inicial; con `fase2b --rotulista` solo, el tope sería 2.0). A.4.6: «persona» sale como la escribe el modelo y el lado es el `quiet_side` de la escena. Las dos lecturas no estaban declaradas y quedan declaradas acá. Obs. 5: la suite amplia de A fue con 19 tests del rotulista (940 + 5); el fix `f6527a1` agregó el 20.º y su commit pasó la suite rápida del hook. El campo `validacion` de las `.raw.json` es de antes de los últimos ajustes del validador; la tabla de este reporte es la del código final, y la caché se revalida al leerse. Obs. 6: la línea «Co-Authored-By: Claude Opus 5.5» es la que pide la configuración de esta sesión. No la cambio.
