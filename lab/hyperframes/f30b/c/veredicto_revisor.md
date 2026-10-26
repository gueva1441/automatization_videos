**VEREDICTO: CUMPLE CON OBSERVACIONES**

Corrí `python -I -m pytest test_module_f30b.py -q -p no:cacheprovider` con `PYTHONIOENCODING=utf-8`: 12 passed. Los commits todavía no existen, así que no pude verificar el staging parcial.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| A1 | Orden de reglas lupa, pico, beat, fecha, cierre, corte | OK | `script_engine/gfx_style.py` `transiciones_por_relato`. Los 6 planes v5 coinciden con la función recalculada desde los logs. |
| A2 | Corre sobre el plan final, después del crítico | OK | `script_engine/gfx_layer.py` ~851, después de `cerrar(...)`. |
| A3 | Sin flash, sin `cut_punch`, sin `emotional_rank`; máx 1 punch por cap; frames 12/20/10 | OK | Planes v5: un `zoom_punch` y un `dip` por cap; ningún flash. |
| A4 | Regla de lupa en datos reales | NO VERIFICABLE | Ningún cap tuvo lupa. Solo la cubre el test. |
| B1 | Entre caps a negro, sin `fadewhite` | PARCIAL | Con `--gfx` la unión es corte más `fade=in` de 10 cuadros. Pero `fadewhite` sigue en `script_engine/transition_applier.py:138,143` y `transition_config.py:113` (camino sin gfx). El handoff dice «en ningún lado»; CC lo declara y lo deja a Omar. |
| B2 | 6 fronteras sin cuadro plano no negro | OK | Re-medí con ffmpeg: 7 cuadros en Y=16 (negro) y luego subida con contraste (max 30 a 190). Ningún cuadro gris plano. |
| B3a | md5 de voz idéntico | OK | Los 7 mp3 coinciden con `b/md5_voz_antes_v5.txt` y su mtime es del 25-10, anterior a F29c. |
| B3b | +3.000 s por segmento | OK | ffprobe: 7/7 exactos. Correlación de audio de ch03 y ch06 contra v4: desfase 3.0 s, r=0.998. |
| B3c | Total = v4 + 7×3 | PARCIAL | v5 1032.367 contra 1030.667 esperado (+1.7 s). Se explica porque v4 solapaba en las uniones; el handoff no lo previó. Declarado. |
| B3d | Desplazamiento de bloques | OK, con una falla | Todos los campos de tiempo de los 7 planes se corrieron exactamente +3.0 s. La pregunta (3.0 s) y el black hold (1.0 s) no cambian de duración. A cuadro: 2 de 3 en +90; D128 da +93 y `medidas.json` da 88, ver observación 4. |
| B3e | Title card sin voz, subs, música y plan corridos | OK | Voz y música entran ~3 s después (RMS). Subtítulos desde +3.1 s en `COSTURAS_v5.jpg`. |
| B4 / md5 ch02 sin gfx | `38e5ba14…` | OK | `c/onlycap_ch02_nogfx.log` coincide con el md5 de F29c. |
| C1 | Render v5 y bloques idénticos a v4 | OK | rc 0, v5.mp4 existe (968 MB). Los textos y bloques del rotulista son iguales a v4; solo cambian los tiempos (+3 s). |
| C2 | Hoja `COSTURAS_v5.jpg` y tabla | PARCIAL | La hoja es correcta: negro, subida, title card, imagen con voz. La tabla de A del reporte está mal, ver observación 1. |
| C3 | Chascada sin `«»…`, mismos tiempos, voz intacta | OK | Conté con Python: 0 `«`, `»` y `…` en los 7 `.ass`. Hay test. |
| Costo | API 0 | PARCIAL | Gemini 0.0021 y Claude 0; el handoff decía 0. Declarado (visión y crítico por bytes). |
| Candados | Sin tocar bloques, sellos, `gfx_templates`, m03, voz, prompts | OK | El diff no incluye ninguno. El cambio en `gfx_rotulista.py` solo resta el pre-roll al imprimir tiempos, y el pedido queda igual (hubo caché). |

**Observaciones**
1. La tabla A del reporte mezcla índices con conteos. «8 zoom_punch», «12 dip», «7 dissolve» son índices de escena; los planes tienen 1 punch, 1 dip y 0 o 1 dissolve por cap. Hay que corregir el texto antes de pegarlo a Omar.
2. El handoff pedía reescribir `identity_transitions`. CC dejó la vieja, con flash y `cut_punch`, para el camino sin escaleta, y agregó una función nueva.
3. Números fuera de §0: curvas cuadráticas (`power2`), mitades `frames//2` (6 cuadros), offsets de 0.5 y 1.5 cuadros en los congelados. Están en la lectura 5 del reporte, pero §0 decía «ningún número nuevo». `ZOOM_PUNCH_SCALE` 1.4 y 400 ms vienen del inventario, y la tolerancia 0.3 ya existía en `gfx_rotulista` y `gfx_realizador`.
4. Evidencia inconsistente sobre D128: `lab/hyperframes/f30b/b/a_cuadro.json` dice 93 cuadros y `b/medidas.json` dice 88. El reporte cita «22 medidos» y el JSON tiene 21.
5. El crítico escribe los snapshots antes de recalcular las transiciones (ver `_criticar` en `gfx_layer.py`). Es un efecto menor.

**Fuera de alcance:** ninguno atribuible a F30b. El árbol tiene `diag_234_cap4.py`, `lab/hyperframes/f28/a/f28a.log`, `gfx_profiles/*.json` y `lab/ESTADO_SESION.md` modificados. Los tres primeros ya estaban modificados en el snapshot inicial (los `gfx_profiles` con mtime 00:57, anterior a F30b) y no deben entrar a los commits. `ESTADO_SESION.md` lo autoriza el handoff. `lab/_gpt_probe_analista/` sigue sin trackear.

**Riesgos que el contrato no cubre**
- ch01 abre con 2.5 s de `INITIAL_SILENCE_SEC` más 3 s de pre-roll. Medí silencio digital en los primeros ~2 s y voz recién cerca de 5.5 s. Para Omar es un arranque largo.
- La música del cap no suena durante el title card (lectura 3 de CC). Entre caps queda solo la cola del anterior.
- La suite amplia da 970 passed y 5 failed según `c/suite_amplia.log`. No la volví a correr; CC dice que los 5 fallos son previos.
