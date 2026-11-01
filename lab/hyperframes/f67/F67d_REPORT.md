# F67d_REPORT — compuerta de narración en borrador

Handoff `HANDOFF_F67d_compuerta_borrador.md`, md5 `ee0055656f028c7910e3a1ce899859d7` (la copia es ese mismo archivo) · rama `f11-guion-v4` · base `69cb84b` (F67c) · CC Opus 5.5 medium. **0 llamadas a la API: US$ 0.** La narración y el papel de Wittenoom no se tocaron: las pruebas van sobre una copia en un `steps_dir` temporal.

## Qué cambió

- `m01f_critico.borrador`: pura, sin disco ni juez. Siempre parte de los párrafos del disco; primero las ediciones libres, después cada DEBERÍA una sola vez, entero o nada.
- `m01f_critico.guardar_y_aprobar`: `borrador` → 1 `_aplicar` → `aprobar_narracion`. Con pendientes no escribe.
- **Se borraron** `aceptar_deberia`, `editar_parrafo`, `aplica`, `oraciones_actuales`, las rutas `/narracion/aceptar` y `/narracion/editar`, y sus tests.
- `qa_studio_server`: `POST /narracion/borrador` (no escribe) y `POST /narracion/aprobar` con `{por, decisiones, ediciones}`; aprobar con pendientes → 400. La página nunca manda párrafos.
- `qa_studio.html`: marca por DEBERÍA, deshacer, «Aprobar narración» apagado hasta que todo esté decidido, «guardando…» con los botones apagados, error visible.

## Salidas

## A. `borrador` sobre una copia de la narración actual de Wittenoom y su `01f_critico.json`

| k | cap | oraciones | tramos | partes | sin decidir (`aplica`) | todos aceptados | aceptar sobre el resultado |
|---|---|---|---|---|---|---|---|
| 1 | ch02 | [9, 16, 17] | 2 | 2 | aplica | aplicado | ya_aplicado |
| 2 | ch03 | [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22] | 1 | 1 | ya_aplicado | ya_aplicado | ya_aplicado |
| 3 | ch04 | [1] | 1 | 1 | aplica | aplicado | ya_aplicado |
| 4 | ch05 | [21] | 1 | 1 | ya_aplicado | ya_aplicado | ya_aplicado |
| 5 | ch06 | [10, 11, 13, 14, 15, 16] | 2 | 1 | no_aplica | no_aplica | no_aplica |
| 6 | ch07 | [1, 7] | 2 | 2 | aplica | aplicado | ya_aplicado |

`pendientes` con todos aceptados: [5] (k=5 no aplica: `1 parte(s) en el texto y 2 tramo(s) en la narración: editar a mano`).

- k=1: la parte «Víctor Calvo, el hijo de Milagros, había hecho esa…» aparece 1 vez/veces con todos aceptados
- k=1: la parte «Del barco, a un avión pequeño. Del avión, a la tie…» aparece 1 vez/veces con todos aceptados
- k=2: la parte «Los informes eran anteriores a la boda, al barco y…» aparece 1 vez/veces con todos aceptados
- k=3: la parte «El hijo cuenta que el primer día de trabajo de su …» aparece 1 vez/veces con todos aceptados
- k=4: la parte «Daniel había estado en Wittenoom diez. Y no fue el…» aparece 1 vez/veces con todos aceptados
- k=5: la parte «Melita Markey, que dirige la Sociedad de Enfermeda…» aparece 0 vez/veces con todos aceptados
- k=6: la parte «En 2023, un relator de la ONU visitó Australia y l…» aparece 1 vez/veces con todos aceptados
- k=6: la parte «Quién sabía está escrito desde 1944: lo escribiero…» aparece 1 vez/veces con todos aceptados

## B. La pestaña en Chrome headless (steps_dir temporal)

### Sin decidir

- Botón «Aprobar narración» apagado = **True** · Falta decidir DEBERÍA 1, 2, 3, 4, 5, 6.
- DEBERÍA 1: sin decidir
- DEBERÍA 2: sin decidir · ya está en el texto
- DEBERÍA 3: sin decidir
- DEBERÍA 4: sin decidir · ya está en el texto
- DEBERÍA 5: sin decidir · no aplica
- DEBERÍA 6: sin decidir

### 1 aceptado (k=1), 1 rechazado (k=5), 4 sin decidir

- Botón «Aprobar narración» apagado = **True** · Falta decidir DEBERÍA 2, 3, 4, 6.
- DEBERÍA 1: ✓ aceptado
- DEBERÍA 2: sin decidir · ya está en el texto
- DEBERÍA 3: sin decidir
- DEBERÍA 4: sin decidir · ya está en el texto
- DEBERÍA 5: ✗ rechazado
- DEBERÍA 6: sin decidir

Sin escribir nada en disco tras esos clics: True.

### Deshacer k=1

- Botón «Aprobar narración» apagado = **True** · Falta decidir DEBERÍA 1, 2, 3, 4, 6.
- DEBERÍA 1: sin decidir
- DEBERÍA 2: sin decidir · ya está en el texto
- DEBERÍA 3: sin decidir
- DEBERÍA 4: sin decidir · ya está en el texto
- DEBERÍA 5: ✗ rechazado
- DEBERÍA 6: sin decidir

### Todo decidido

- Botón «Aprobar narración» apagado = **False** · Al aprobar se aplica todo junto.
- DEBERÍA 1: ✓ aceptado
- DEBERÍA 2: ✓ ya estaba aplicado
- DEBERÍA 3: ✓ aceptado
- DEBERÍA 4: ✓ ya estaba aplicado
- DEBERÍA 5: ✗ rechazado
- DEBERÍA 6: ✗ rechazado

Aprobado sobre la copia: ✓ Aprobada por Omar (2026-10-31T22:55)

Copia después de aprobar: md5 `3f1be0ed9d5bcdf7f9e470e851c4ba48`, `aprobado.md5` igual = True; «Y no fue el único que se llevó Wittenoom adentro.» aparece 1 vez.

Errores de página: 0 []

## Topic real

Archivos de `_steps/<tid>/` que cambiaron: ninguno

Coincide con lo pedido en el §4 A: k=2 y k=4 «ya aplicado» y nunca doble; k=1, 3, 6 «aplica»; k=5 «no aplica». Capturas en `f67d/*.png`; texto de la pestaña en `f67d/pestana_parcial.txt` y `f67d/pestana_decidida.txt`.

## Tests

- `tests/test_m01f_compuerta.py`: 64 verdes, incluidos idempotencia (`test_el_deberia_que_contiene_su_original_se_aplica_una_sola_vez`), partes «[…]», «no aplica» por partes ≠ tramos, aprobar con pendientes (400 y sin escribir), 1 reconstrucción + 1 juez, edición que toca un tramo, `i` del disco y borrador puro.
- Suite amplia + `test_run_pipeline` + `test_qa_studio` (`f67d/suite_amplia.log`), **sin `test_module_gfx_lab.py` ni `test_module_fase2b_only_cap.py`, que escriben en `output/`**: `2 failed, 1551 passed, 30 skipped, 3 xfailed, 4 warnings in 67.66s (0:01:07)`. Fallas: test_module_m03_merge_timing.py::test_c_guarda_de_minimo, test_module_m03_merge_timing.py::test_c_veo_path_y_veo_anchor_intacto: las previas. Sin archivos nuevos en `data/` ni `output/`.
- `mapa --check`: 0 fallas.

## Diff

```
qa_studio.html                |  76 +++++++----
 qa_studio_server.py           |  74 ++++++-----
 script_engine/m01f_critico.py | 215 ++++++++++++++++++++++++-------
 tests/test_m01f_compuerta.py  | 285 ++++++++++++++++++++++++++++++++----------
 4 files changed, 476 insertions(+), 174 deletions(-)
```

## Decisiones mías, donde el handoff no llegaba

1. **`editar` sin texto = «resuelto a mano»:** el §4 pone `texto?` como opcional. Sirve para k=5: Omar corrige en los párrafos y marca ese DEBERÍA como decidido. `editar` con texto sigue la misma regla de partes: si no coincide con los tramos queda pendiente.
2. **`aceptar` o `editar` con texto que termina en «no aplica» sigue pendiente:** cuenta como decidido solo rechazándolo o resuelto a mano, como pide el §2.
3. **Un «ya aplicado» sigue pidiendo decisión:** el §2 dice que **cada** DEBERÍA tiene decisión. Aceptarlo no cambia nada.
4. **Si el borrador deja el texto igual no reconstruye:** el md5 no cambia y el papel sigue vigente. Sin esto, re-aprobar sin cambios correría el juez y borraría el normalizado para nada.
5. **Una edición que deja el texto igual no cuenta como edición.**
6. **`etapa_c_prueba.py` (lab de F67 C) queda como está:** llama a funciones borradas. Es registro de esa etapa; ya no corre.

## Lo que queda abierto

1. **`--aprobar-narracion` y la «A» del form de `run_pipeline` aprueban sin decisiones:** el handoff cambia la pestaña; ese camino aprueba tal cual, sin aplicar nada.
2. **El borrador se pierde al recargar la pestaña:** vive en la página, como pide el §3, y no se guarda en ningún lado.
3. **Wittenoom no se ve afectada:** con su narración aprobada solo hace falta entrar si se quiere re-decidir.

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES
Corrí solo lo permitido: pytest de tests/test_m01f_compuerta.py dio 64 passed, y mapa_modulos --check dio 161 archivos, 0 fallas. No toqué data/ ni output/. El handoff tiene el md5 pedido (ee005565…).

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1a | `borrador` parte siempre del disco; la página no devuelve párrafos; `i` sobre el disco | OK | m01f_critico.py `borrador(parrafos…)` y `_ediciones` validan `i` contra `len(parrafos)` del disco. `_parrafos_de_cap` propaga `indices`. qa_studio.html `nnCuerpo` manda solo `decisiones` y `ediciones`; `nnDisco` lee del GET. |
| 1b | Ediciones primero; k tocado queda «no aplica (editado a mano)» | OK | `tocado_a_mano` se calcula sobre el disco antes de las ediciones y `a_mano` se devuelve con motivo «editado a mano». Test en tests/test_m01f_compuerta.py:462. |
| 1c | «Ya aplicado» por parte y antes de `_ubicar` | OK | `_aplicar_deberia`: la parte está en el cap y no está en el tramo, y recién después llama a `_ubicar`. SALIDAS.md A: k=2 y k=4 `ya_aplicado`, k=1, 3 y 6 `aplicado`, k=5 `no_aplica`. |
| 2 | Separador «[…]» en crudo, sin `validacion.marcas` | OK | `_partes` hace `str(crudo).split(SEPARADOR)` y recién después `limpiar`. No usa `marcas`. |
| 3 | Botón Aprobar habilitado solo si cada DEBERÍA tiene decisión; «no aplica» cuenta solo si se rechaza o se edita | OK | `pendientes` = estados pendiente o no_aplica. `guardar_y_aprobar` lanza ValueError antes de escribir, y el servidor lo devuelve como 400. En la página el botón se apaga con `pend.length` o `nnBusy`. |
| 3b | Las 4 decisiones del reporte frente al texto | PARCIAL | (1) «editar» sin texto = «resuelto a mano» es una lectura razonable del §2, pero no está escrita en el handoff. (2) y (3) son coherentes con el §2. (4) «sin cambio no reconstruye» es agregado de CC y no contradice el handoff. |
| 4 | Doble aplicación | OK, con salvedad | No encontré ningún caso que aplique dos veces. Dos DEBERÍA que se pisan: el segundo pierde su tramo y queda `no_aplica`, que bloquea la aprobación. Reenvío tras aprobar: queda `ya_aplicado` o `no_aplica`. Texto editado: se aplica una sola vez porque `decisiones` es un mapa k → acción. Salvedad: el chequeo «ya aplicado» es una subcadena sobre todo el cap. Una parte corta que ya esté en el cap por otro lado se saltea sin avisar, y se pierde el cambio. Es un fallo por omisión, no una doble aplicación. |
| 5 | Borrado de `aceptar_deberia`, `editar_parrafo`, `aplica`, `oraciones_actuales` y las dos rutas | OK | Test en tests/test_m01f_compuerta.py:530 y :612. Un grep en producción no encuentra referencias vivas. Las únicas son `etapa_c_prueba.py` de lab, que el reporte declara muerta, y el campo `oraciones_actuales` que ahora devuelve `borrador`. |
| 6 | Página: estados, deshacer, «guardando…», error visible | OK | `NN_MARCA` y las marcas por DEBERÍA; `nnDeshacer` y Deshacer por párrafo; el botón dice «guardando…» y todo se apaga con `nnBusy`; `nnError` se pinta en `.err`. Capturas 0 a 4 existen y no están vacías; SALIDAS.md muestra los estados sin decidir, parcial, deshacer, todo decidido y aprobado. |
| 7 | Pruebas solo en temporales; Wittenoom intacta | OK | SALIDAS.md: «Archivos de `_steps/<tid>/` que cambiaron: ninguno». `F67d_antes.json` y `F67d_despues.json` son idénticos. |
| 8 | Entregables: reporte, SALIDAS, capturas, script | OK | F67d_REPORT.md, f67d/SALIDAS.md, 5 PNG, etapa_f67d_salidas.py. |
| 9 | Veredicto del revisor en el reporte, ESTADO_SESION, commit, copia del handoff con md5 | NO VERIFICABLE | El reporte tiene «(pendiente)» en la sección del veredicto, como corresponde. Faltan el commit y ESTADO_SESION, que van después de este veredicto. |

Observaciones (no son fallas):
- Si `_aplicar` escribe y después `aprobar_narracion` lanza Parada, la narración queda reescrita pero sin aprobar. No es atómico, aunque `_aplicar` ya invalida la aprobación.
- En `nnPrevia`, si el POST falla, `nnDec` ya quedó mutado pero la vista (`NNB`) es la vieja. Se muestra el error, pero la pantalla y el estado se desfasan.
- «Editar» con texto sobre un k que no aplica sigue pendiente. Esto coincide con la decisión 2 del reporte, pero «los que editan» del §2 solo se cumple vía «Resuelto a mano».
- Una decisión «editar» sin texto cuenta como decidida sin comprobar que haya una edición real.

Fuera de alcance: no atribuible con certeza. `lab/hyperframes/f58/pedido_paquetes_wittenoom.txt` está modificado (mtime 22:57, casi igual al del reporte) y ya figuraba como `M` en el git status inicial, así que no puedo confirmar que sea de F67d. `diag_234_cap4.py`, `f28a.log` y los stickers y MAPA no son de F67d (los stickers y el MAPA derivan del propio mapa_modulos). Los demás `??` son del lab y preexistentes.

Riesgos que el contrato no cubre:
- `--aprobar-narracion` y la «A» del form de `run_pipeline` siguen aprobando sin decisiones (ya figura como abierto en el reporte).
- El borrador se pierde al recargar la pestaña, porque vive solo en la página.

## Adenda de CC

Después del veredicto no toqué código. Decisiones sobre sus observaciones:

- **Salvedad de la fila 4, queda abierta:** una parte corta que ya esté en otro lugar del cap se marca «ya estaba aplicado» y no se aplica. Omar lo ve en la marca del DEBERÍA. Pasa por la regla del §4 A.c, que mira el texto del cap, y no la cambié.
- **`nnPrevia`:** si el POST falla, la decisión queda puesta y la vista es la anterior, con el error a la vista. El siguiente clic o Aprobar lo vuelve a validar en el servidor. Queda sin arreglar.
- **Aprobar no atómico:** `aprobar_narracion` solo para si falta el archivo que `_aplicar` acaba de escribir. Queda sin arreglar.
- **`editar` sin texto sin edición real:** es decisión de Omar marcarlo «resuelto a mano». Queda así.
- **`pedido_paquetes_wittenoom.txt` (fuera de alcance): lo reescribió mi suite amplia.** `test_module_f58.py` lo regenera con la narración actual, y su mtime coincide con mi corrida. Es lab, no `data/` ni `output/`. No entra al commit y no lo revertí: queda modificado en el árbol.
- **Commit:** por rutas explícitas; `diag_234_cap4.py` y `f28a.log` no entran.
