# RESUMEN F4e — Marca de esquina apagada, crítico visual, hoja de contactos

Rama `f3-lab-identidad`, sobre F4d (`b23b0ae`). `main` intacta (`43f528a`). Solo `--only-cap ch02` y `ch05`; no hubo render completo.

## Resultado

| Pedido | Resultado |
|---|---|
| 1. Marca | `channel_bug.corner.enabled = false`: no hay marca en la esquina en ningún cap. El cierre del video queda igual. |
| 2. Crítico visual (6b) | `script_engine/gfx_critic.py`. Corre después de las reglas duras y antes de guardar el plan, de los SFX y del render. Para cada bloque, Gemini recibe el cuadro real de la foto, la frase de la voz y el bloque propuesto descripto en texto, y devuelve suma, repite o estorba con motivo. Solo pasan los «suma». Los criterios de Omar van en el prompt, con 5 ejemplos «suma» del plan dorado de ch02. La caché va por (cuadro, bloque, voz) y cada veredicto queda en `gfx_chNN.log`. |
| 3. Hoja de contactos | `hoja_contactos_ch02.jpg` y `hoja_contactos_ch05.jpg`: un cuadro del render por bloque que pasó, con tiempo, bloque, veredicto y motivo. |

**ch02: pasan 6 de 7.** Sale el ícono ENGULLIDA (gota): «repite lo que la imagen ya muestra». Pasan el recorte de Katrina con la fecha, el nivel de agua 4.6 m, PUTREFACTA, el recorte de las celdas, el zoom y ENCIERRO.
**ch05: pasan 6 de 8.** Sale el ícono DISOLVIÓ (gota sobre una foto de agua) y el dato «1 de septiembre», porque la voz dice la fecha en ese instante. Pasan el zoom al niño, el contador de 500, DESVANECIDAS, CADÁVERES, el recorte «cadáveres flotando…» y DESAPARECIDOS.
Tabla completa con la voz y el motivo de cada bloque: `TABLA_critico.md`. Decisiones: `DECISIONES_F4e.md` (I1–I14).

- Candado sin `--gfx`: el md5 de ch02 `--only-cap` es `38e5ba14…` (`corrida/onlycap_ch02_nogfx_f4e.log`). Es el mismo md5 de referencia fijado desde F4, así que ch02 sin gráficos sigue byte-idéntico. Tests: 316 verdes.

## Lo que hay que saber
1. **El crítico juzga el texto del bloque, no el bloque dibujado.** Por eso pasaron como «suma» dos defectos que la hoja de contactos sí muestra:
   - ch02 1:00.7: el recorte de 10 palabras no entra en la tarjeta y se corta en «…AGUA CONTAMINADA CO». «aguas residuales» no se ve (I12).
   - ch02 1:17.9: el recuadro del zoom «Pies del hombre» cae al costado de los pies (I13).
   Ninguno de los dos está arreglado. Los arreglos posibles son que la tarjeta ajuste la letra o baje la cláusula a 8 palabras, y validar la caja del zoom con el recorte, como ya hace `verify_crop`.
2. Agregué al prompt «un sello de UNA palabra que dice la voz es énfasis, no repetición». Sin esa línea todo sello caía en «repite», porque por diseño el sello es una palabra de la voz. Omar no la pidió, y con ella pasan todos los sellos (I5).
3. Si Gemini falla, el bloque queda y no se cachea (I8). En esta corrida no falló ninguno.
4. Leí «un cuadro 1:1 por bloque» como un cuadro por cada bloque. Los cuadros van a 640 px (16:9), no son recortes sin escalar (I11).

## Revisor (revisor-handoff), veredicto íntegro

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Esquina apagada, queda el cierre | OK | misterio.json `"corner":{"enabled":false}`; gfx_bug.py:43/193; gfx_layer.py `corner = cfg["corner_enabled"]`. Los logs nuevos de ch02 y ch05 dicen "marca: … esquina apagada". El cierre se conserva. |
| 2 | Crítico en 6b, antes del render y de los SFX | OK | gfx_layer.py:682-684 corre antes de guardar el plan resuelto y antes de `sfx_events` (:693). Token `visual_critic` OFF en el motor y ON en misterio. |
| 3 | Gemini responde suma/repite/estorba y solo pasan los "suma" | OK | gfx_critic.py (250 líneas). `critico` está en `plan` de gfx_plan_ch02/05.resolved.json con 7 y 8 veredictos. Los SFX reflejan solo lo que pasó: ch02 tiene 5 eventos y ch05 tiene 7. |
| 4 | Few-shot de 5 bloques del dorado de ch02 | OK | gfx_profiles/misterio_critico_fewshot.json existe. Va solo en texto (I6, declarado). |
| 5 | Caché por (foto, bloque) | OK | gfx_critic_ch02.json y gfx_critic_ch05.json existen. |
| 6 | Log por veredicto en gfx_chNN.log | OK | Hay líneas "crítico:" en gfx_ch02.log:231-238 y gfx_ch05.log:231-239. |
| 7 | Hoja de contactos por cap | PARCIAL | Las dos jpg existen, con tiempo, bloque y veredicto. Los cuadros son 16:9 a 640 px, no 1:1; está declarado en I11. Los motivos salen cortados a media frase. |
| 8 | Probado en ch02 y ch05 con --only-cap | OK | Logs en f4e/corrida con rc=0. Pasan 6 de 7 en ch02 y 6 de 8 en ch05. |
| 9 | Tabla coincide con los planes y los logs | OK | Los 15 veredictos de TABLA_critico.md coinciden con `plan.critico` y con los logs (tiempos, bloque, veredicto). |
| 10 | Tests | OK | Los 316 tests pasan. |
| 11 | main en 43f528a | OK | `git rev-parse main` da 43f528a. HEAD sigue en b23b0ae. |
| 12 | Sin render completo | OK | Solo hay ch02 y ch05 `_segment_only.f4e_gfx.mp4`. Los `chNN_gfx.mp4` de los otros caps son de las 15:4x, anteriores. |
| 13 | md5 de la corrida sin --gfx | PARCIAL | Hay un solo md5 (ch02, 38e5ba14…) y ningún md5 de referencia para compararlo. No se prueba que el cap quede idéntico. Falta el md5 de F4d, o el de ch05 sin --gfx. |
| 14 | Commit y RESUMEN_F4e.md | NO VERIFICABLE | No hay commit ni RESUMEN_F4e.md todavía. Se espera que vengan después de este veredicto. |

Interpretaciones y defectos de la hoja (miré las dos imágenes):
- I12 está bien reportado. En ch02 1:00.7 la tarjeta se corta en "…AGUA CONTAMINADA CO" y "aguas residuales" no se ve.
- I13 está bien reportado. El recuadro del zoom de ch02 1:17.9 cae sobre la zona vacía, a la izquierda de los pies.
- I14 es correcto: el "2 m" se ve a mitad de subida.
- Las interpretaciones I3, I5, I6, I8 y I11 son razonables y están declaradas. Observación sobre I5: la aclaración "sello de una palabra no es repetir" es un criterio que Omar no pidió, y hace que todos los sellos pasen.

Hallazgos no reportados:
- El crítico dejó pasar ch05 1:17.4 como "suma" aunque su propio motivo admite que el titular repite la voz ("cuerpos sin vida a la deriva" frente a "cadáveres flotando"). Además queda a 6 s del ícono de calavera "cadáveres" (1:11.1).
- En ch02 0:38.9, el ícono de biohazard pasó como "suma". Su motivo es débil.
- El crítico solo ve el texto propuesto, no el bloque dibujado. Por eso I12 e I13 pasaron como "suma".

Fuera de alcance: `diag_234_cap4.py` (solo cambia el TOPIC). Ya figuraba modificado en el git status inicial y no tiene relación con F4e. Si va en el commit F4e, queda como alcance ajeno. Lo demás es F4e: gfx_config.py, misterio.json, gfx_bug.py, gfx_layer.py y test_module_gfx_profiles.py, más los archivos nuevos del crítico.

Riesgos que el contrato no cubre:
- Con temperatura 0 el crítico es estable por caché, pero juzga el texto y no el render, así que no detecta recortes truncados ni cajas de zoom mal puestas.
- Si Gemini falla, el bloque queda (I8), así que el filtro puede no filtrar sin que nadie lo note. Lo único que lo delata es la línea del log.

**Sobre el punto 13:** la referencia sí existe. `38e5ba14…` es el md5 de ch02 `--only-cap` sin `--gfx` fijado en `ESTADO_SESION` desde F4, y se volvió a medir igual en F4b, F4c, F4d y ahora. Que coincida es la prueba de que el cap sin gráficos sigue idéntico.
**`diag_234_cap4.py`:** no va en el commit (no es nuestro).

## Archivos
- Código: `script_engine/gfx_critic.py` (nuevo), `script_engine/gfx_layer.py`, `script_engine/gfx_bug.py`, `gfx_config.py`, `gfx_profiles/misterio.json`, `gfx_profiles/misterio_critico_fewshot.json` (nuevo). Tests: `test_module_gfx_critic.py` (nuevo), `test_module_gfx_profiles.py`.
- Evidencia: `lab/hyperframes/f4e/`. Respaldo del estado F4d de ch02 y ch05: `_fase2b_work/_bak_f4e_pre/`.
