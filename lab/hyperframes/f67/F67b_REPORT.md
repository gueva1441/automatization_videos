# F67b_REPORT — cierre de la compuerta

Handoff `HANDOFF_F67b_cierre_compuerta.md`, md5 `201c9444d920f8358216b54d477532e5` (la copia es ese mismo archivo) · rama `f11-guion-v4` · base `4ca87d4` · CC Opus 5.5 medium. **0 llamadas a la API: US$ 0.** No corrió voz, fotos, papel ni `--criticar`. `_steps/<tid>/` sin cambios.

## Salidas por etapa

## 1. `papel_falta` y `etapa_de`

Wittenoom hoy (narración sin aprobar):

- `papel_falta` → `papel de otra narración: se re-escribe` (el papel tiene `narracion_md5` = None; narración `778d3e1dcd4ca545453f7a29b6a92bb3`)
- `etapa_de` → `('narracion', 'la narración no está aprobada')`

Sobre una copia, con la narración aprobada:

- aprobada: `778d3e1dcd4ca545453f7a29b6a92bb3`
- `papel_falta` → `papel de otra narración: se re-escribe`
- `etapa_de` → `('papel_nuevo', 'papel de otra narración: se re-escribe')`

## 2. `/papel/aprobar` 409 y botón deshabilitado

POST `/papel/aprobar` con Wittenoom hoy: **409** `{"error": "la narración no está aprobada"}`

Pestaña PAPEL en Chrome headless: botón «Aprobar papel» deshabilitado = **True** · 0 errores de página · aviso: «No se puede aprobar el papel: la narración no está aprobada.» · captura `f67b/papel_bloqueado.png`.

Comienzo de la pestaña:

```
Sin aprobar
el papel no está aprobado
claude-opus-5-5 m01e-7 · US$ 0.9797 · cierre: sin motivos · 0 de 13 fichas revisadas
Aprobar papel
No se puede aprobar el papel: la narración no está aprobada.
⚠ La narración sigue contradiciendo el archivo:
ch01 [1] «Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí.»: La herida del pie va a cerrar. (D85)
ch01 [9] «Lo que sobró de la mina, en cambio, sigue donde lo dejaron.»: Los residuos de la mina siguen donde los dejaron. (D04, D149)
ch03 [14] «En 19
```

## 3. Normalizado desfasado

Comprobación de solo lectura sobre Wittenoom: caps distintos [1, 2, 3, 4, 5, 6, 7] (7). El archivo real sigue en disco: se borra al correr la voz.

Sobre la copia, `descartar_normalizado` imprime:

```
[normalizado] desfasado: 7 caps distintos, se borra
```

Caps [1, 2, 3, 4, 5, 6, 7]; el archivo sigue: False.

`audio_manager._resolve_text_for_tts`, hoy con el archivo real: lee el texto viejo = **True**. Sin el archivo: normalize_for_tts de la narración actual = **True** (el `exists()` de `audio_manager.py:519`).

`normalizer_gate` lo regenera sobre la copia, sin LLM (`_apply_spans_to_narration` + `_persist_normalized_narration`, lo que corre siempre el gate): desfasado después = [].

## 4. `--criticar`

`python fase1_5.py --help`:

```
--criticar            F67b: juez m05 + crítico (≈ US$ 0,8), sin verificador,
                        sobre la narración ya escrita de --topic; usa la tabla
                        de 01b_verificacion.md que haya en disco y no toca la
                        narración ni su aprobación
```

Corrida en seco sobre una copia, con `post` falso; el POST real, `verificar_caps`, `run_verificacion` y `run_pantalla` explotan: exit 0, 1 llamada(s) al `post` falso: ['claude-opus-5-5 · system md5 fb3e5a9e734ff730a3b5184d88e7f38a']. La narración no cambió: True.

```
[m01f] intento 1: in 1 · out 1 · US$ 0.0000 · JSON
  [m01f] nota 6.5 · 0 DEBERÍA · US$ 0.0000 → <copia>\123bbb64-9fca-4395-8bf4-57d60e219ef1\01f_critico.md
  [narración] narración aprobada por Prueba (2026-10-31), md5 778d3e1d…
```

## Topic real

Archivos de `_steps/<tid>/` que cambiaron: ninguno

## Tests

- `tests/test_m01f_compuerta.py`: 9 tests `test_f67b_*` (11 casos con los parametrizados), incluidos los 3 del §2. Se borró el caso de la excepción (§4).
- Ajustados: `test_module_f39_fase1` (el papel falso dice su `narracion_md5`) y `test_module_f65b` (aprueba la narración antes de `/papel/aprobar`).
- Suite amplia (`f67b/suite_amplia.log`): `4 failed, 1518 passed, 30 skipped, 3 xfailed, 4 warnings in 70.71s (0:01:10)`. Fallas: test_module_gfx_lab.py::test_cues_sin_escribir_el_proyecto, test_module_m03_merge_timing.py::test_c_guarda_de_minimo, test_module_m03_merge_timing.py::test_c_veo_path_y_veo_anchor_intacto, test_module_gfx_lab.py::test_preview_usa_las_plantillas_reales: las 4 previas.
- `mapa --check`: 0 fallas.

## Diff

```
fase1_5.py                    |  79 +++++++++++++++++++++----
 qa_studio.html                |   3 +-
 qa_studio_server.py           |  16 ++++-
 run_pipeline.py               |   2 +-
 script_engine/m01f_critico.py |   2 +-
 test_module_f39_fase1.py      |   6 +-
 test_module_f65b.py           |   1 +
 tests/test_m01f_compuerta.py  | 134 ++++++++++++++++++++++++++++++++++++++++--
 8 files changed, 222 insertions(+), 21 deletions(-)
```

## Nombres reales y desvíos

1. **La «misma comparación que hace `normalizer_gate`» no existe:** el gate no compara, reescribe siempre (`m02_5_normalizer_gate.py`, `_apply_spans_to_narration` y `gate_normalizer_for_topic`, las 3 salidas llaman a `_persist_normalized_narration`). Lo que sí es igual es el dato: `narration_original` = `ch.get("narration")` de lo que recibe. Comparo contra eso, como dice la constante del §1.
2. **`audio_manager.py:493` es la firma de `_resolve_text_for_tts`;** el chequeo está en `:519`. Sin archivo, `normalize_for_tts`.
3. **El normalizado real de Wittenoom no se borró:** el handoff pide comprobarlo y no correr nada, así que sobre el real solo leo (7 caps distintos) y el borrado corre sobre una copia. Se borra solo cuando se corra la voz. El gate lo regenera entero; se probó con `spans` vacíos, sin LLM.
4. **El caso del normalizado ilegible** cuenta como todos los caps distintos: no estaba en el §1, decisión mía, para que no quede un archivo roto antes de la voz. `audio_manager` igual caería al respaldo.
5. **`/papel/aprobar` con la narración cambiada** responde el motivo de `estado_narracion` («la narración cambió después…»), no la frase del §2. Sin papel sigue el 400 de antes.

## Lo que queda abierto

1. **`--aprobar-papel` por CLI no se bloqueó:** el §2 pide solo el POST. No salta nada: `process_topic` y `etapa_de` paran antes por narración o por papel desfasado.
2. **`--criticar` no se probó contra la API:** solo con `post` falso, como pide el handoff. Lo corre Omar después de aprobar; deja `01f_critico` vigente sin tocar la aprobación y sin re-pagar el verificador. La tabla del verificador puede quedar de una narración anterior: el crítico la recibe igual y el `.md` no lo avisa.
3. **Omar decide los 7 DEBERÍA en la pestaña NARRACIÓN;** después, `--papel`. El papel se re-escribe pague o no: si la narración no cambió, el caché de m01e lo devuelve sin llamar al autor y le agrega el campo (si a la validación le falta un pedido guardado, llama solo al verificador); si cambió una oración, ≈ US$ 1.
4. **Tras `--from audio` la voz sale sin los spans del gate:** el normalizado desfasado se borra y el gate no corre, así que el audio usa `normalize_for_tts`. El camino normal es `--from normalizer_gate`.
5. **La pestaña PAPEL puede decir «✓ Aprobado» sobre un papel aprobado y desfasado,** con el botón deshabilitado y el aviso al lado. Solo visual: la cadena frena igual.
6. **De F67, sigue:** `humano` de la escaleta en P16, DEBERÍA no contiguos con la etiqueta «ya no aplica» y la escala de nota. Los abiertos 9 y 10 de F67 y el pendiente de «volver a criticar» quedan cerrados aquí.

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Ejecuté yo: `pytest tests` = 63 passed. Los 3 test_*.py nombrados = 100 passed y 1 failed con la consola por defecto (cp1252, `UnicodeEncodeError` en un `print` del propio test, `test_module_f39_fase1.py:110`). Con `PYTHONUTF8=1` dan 101 passed. `mapa_modulos --check` = 0 fallas, 161 archivos. No llamé a la API ni corrí fase1_5/run_pipeline. Solo importé funciones de lectura sobre Wittenoom.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | `papel_falta` sin la excepción | OK | `fase1_5.py:448-458`: `None` solo si `papel.narracion_md5 == md5_narracion(n3)`; aprobado o no. En vivo da «papel de otra narración: se re-escribe». |
| 2 | `etapa_de` → `papel_nuevo` si está desfasado | OK | `run_pipeline.py:205-207` usa `papel_falta`. En vivo Wittenoom da `('narracion','la narración no está aprobada')`, como pide el handoff. El caso aprobado lo cubre el test `test_f67b_papel_aprobado_sin_narracion_md5_es_papel_nuevo` (`tests/test_m01f_compuerta.py:532`), que pasa. |
| 3 | No queda otro camino que respete un papel aprobado desfasado | OK | Quedan tres lectores del papel. `process_topic` (`fase1_5.py:795`) llama `papel_falta` antes de `estado_papel`. `run_papel_aprobado` (`:497`) y `etapa_de` también. El único grep restante que usa `01e_pantalla.json` es de lectura de contenido. |
| 4 | POST `/papel/aprobar` 409 | OK | `qa_studio_server.py:1921-1930, 2018-2020` (`_papel_bloqueo`, tras validar «por»). `SALIDAS.md` muestra 409 «la narración no está aprobada». Hay test. |
| 5 | Botón deshabilitado | OK | `qa_studio.html:1038-1039` (`disabled` + aviso). PNG de 214801 bytes existe; `papel_pestana.txt` trae el aviso. |
| 6 | `normalizado_desfasado` y `descartar_normalizado` | OK | `fase1_5.py:463-488`. Se llama en `process_topic:809-810` para `from_step in (m01a, m01b, normalizer_gate, audio)`, después de las PARADAs de narración y papel y antes del gate y de la voz. Cubre `--only normalizer_gate` y `--only audio`, que se vuelven `from_step`. No cubre `--from m07/m03`, donde la voz ya existe: aceptable. |
| 7 | Comparación con `narration_original` | OK | `m02_5_normalizer_gate.py:625` guarda `narration_original`. Las 3 salidas de `gate_normalizer_for_topic` llaman `_persist_normalized_narration` (`:696, 707, 723`): confirmo «el gate reescribe siempre». Con el real de Wittenoom hoy: 7 caps distintos. |
| 8 | Normalizado real y `_steps/<tid>` intactos | OK | Recalculé los md5 contra `md5/F67b_antes.json`: 79 archivos, 0 cambiados, 0 faltantes. `01b_narration_normalized.json` sigue en disco. `git status` no muestra nada en `data/`. |
| 9 | `audio_manager` sin el archivo | OK | La firma de `_resolve_text_for_tts` está en `:493` y el `exists()` en `:519`; el reporte lo desvía bien. Sin archivo cae a `normalize_for_tts`. |
| 10 | `--criticar` sin verificador | OK | `criticar()` (`fase1_5.py:635-650`) corre `judge_narration` y `run_critico`, no el verificador. El test lo prueba con `verificar_caps`, `run_verificacion` y `run_pantalla` que explotan, y pasa. |
| 11 | `--criticar`: «sin verificación en disco» | OK | `m01f_critico.py:112` y el test `criticar_usa_o_avisa`. |
| 12 | `--criticar` no toca narración ni aprobación | OK | El test compara los bytes de `01b_narracion_v3.json` y `estado_narracion` sigue en True. `judge_narration` solo escribe `06_judge_narrative.json`. |
| 13 | `--criticar` no se corrió contra la API | OK | El reporte lo declara, y el uso real es 0 US$. |
| 14 | Se borra la excepción y su test | OK | Diff de `fase1_5.py` y `run_pipeline.py`; los tests f39 y f65b se ajustaron. |
| 15 | Cada afirmación del reporte | OK | Verificadas las de arriba. Suite amplia: el log termina en «4 failed, 1518 passed»; las 4 fallas son de gfx_lab y m03_merge_timing, fuera de F67b. |
| 16 | Caché de m01e sin llamar si la narración no cambió | OK, con matiz | `m01e_pantalla.llamar:904-940`. La clave es md5 de `PROMPT_VERSION\|MODELO\|EFFORT\|SYSTEM\|user`. Recalculé la clave de Wittenoom hoy y coincide con `01e_pantalla.raw.json` (`final` presente): hoy sería hit. Matiz: si un `pedido_md5` del verificador no está guardado, hay «caché parcial» y SÍ llama al verificador. El reporte dice «sin llamar» sin ese caso. |
| 17 | ESTADO_SESION cabecera y commit (§3.5) | NO VERIFICABLE | Todavía no hay cambios en `lab/ESTADO_SESION.md` ni commit. El reporte tiene el veredicto «(pendiente)». Falta hacerlos después de este veredicto. |

Fuera de alcance (modificados sin estar en el diff declarado de 8 archivos del reporte):
- `diag_234_cap4.py`: cambia el TOPIC a `933c76c7…`. No tiene relación con F67b.
- `lab/hyperframes/f28/a/f28a.log`: +33 líneas de corridas de F28. No es F67b.
- `lab/MAPA_PROYECTO.json`, `lab/MAPA_PROYECTO.md`, `lab/mapa/stickers/{guion,orquestador}.json`: regeneración del mapa con stickers de F67b. Es esperable y `--check` da 0 fallas.
- `DECISIONES.md`: la línea de las 20:09. El handoff pide incluirla.
- Los 8 archivos del reporte y todo `lab/hyperframes/f67/` son alcance.
- Hay que decidir si `diag_234_cap4.py` y `f28a.log` entran al commit.

Observaciones (bugs menores, ninguno bloquea):
1. `normalizado_desfasado` (`fase1_5.py:472`) abre `01b_narration.json` sin proteger. Si el normalizado existe y ese archivo no, tira `FileNotFoundError`. En `process_topic` no debería pasar, porque `estado_narracion` ya exigió `01b_narracion_v3.json`.
2. `papel_vista` sigue mostrando «✓ Aprobado» en un papel aprobado y desfasado. Solo se deshabilita el botón y sale el aviso.
3. `--aprobar-papel` por CLI sigue aprobando un papel desfasado. El reporte lo declara y la cadena igual frena después en `papel_falta`.
4. En `--from audio` el normalizado se borra y el gate no corre. La voz sale con `normalize_for_tts` sin los spans aprobados del gate. Sale de lo que el reporte dice, pero conviene que Omar lo sepa.
5. `test_a3_de_la_semilla…` falla si la consola es cp1252 y pasa con `PYTHONUTF8=1`. Es del entorno, no de F67b.

Riesgos que el contrato no cubre:
- Tras `--criticar` o tras aprobar, el papel se re-escribe por cache hit sin `aprobado`. Si Omar edita una sola oración, la clave cambia y son ≈US$ 1 de papel, sin tope.
- La tabla del verificador en disco puede ser de una narración anterior y el crítico la recibe sin aviso. El reporte lo reconoce.
- El commit incluye cambios ajenos (`diag_234_cap4.py`, `f28a.log`) si se hace `git add -A`.

## Adenda de CC

Después del veredicto no toqué código. Decisiones sobre sus observaciones:

- **Fila 16:** corregí el abierto 3 del reporte: el caché puede llamar al verificador si le falta un pedido guardado.
- **Observación 4:** queda como abierto 4, para Omar. El camino normal es `--from normalizer_gate`, y es el que corre `_paso_voz`.
- **Observación 2:** queda como abierto 5. Es solo visual y la cadena frena igual.
- **Observación 1:** no se arregla: `process_topic` llega ahí con la narración exigida y `reconstruir` escribe los dos archivos juntos.
- **Observación 5:** es del entorno; mis corridas usan `PYTHONIOENCODING=utf-8`.
- **Commit:** por rutas explícitas; `diag_234_cap4.py` y `f28a.log` no entran. `ENTRADA_ANALISTA_2026-10-31e.md` y `31f.md` tampoco: son del analista y no los leí.
