# F71b — la persona que el prompt nombra trae su foto madre, y QA lo puede arreglar

Handoff: `lab/hyperframes/f71/HANDOFF_F71b.md` (md5 9a49ba5ecc999ed28b13500ed7ca28e5).

## Resultado

**La foto ya trae la cara de Daniel: el retrato sale de su madre.** De las 99 fotos solo cambia esa.

**Para mirar en la foto nueva** ([ch01_supp_02_despues_graded.png](ch01_supp_02_despues_graded.png)):
- **La mujer desapareció: solo se ven sus manos.** Opus pidió «held in both hands of an older Spanish woman», pero el filtro de producción (`manos/cara: manos en plano close`) sacó esa oración del prompt, y el motor nunca la recibió. La voz habla de «la familia que la guarda», así que se sostiene, pero ya no es la escena anterior.
- **La foto impresa quedó rara:** un retrato tipo carnet arriba y el pie vendado abajo, como dos fotos pegadas. Sale del pedido de Opus («in the upper part of the print… bandaged foot visible below»).
- **La cara viene de la madre:** misma camisa y pose de frente que `daniel_cija.png`.

No hice una segunda corrida: la tanda pedía una sola.

## Lecturas mías

1. **«ch01 supp 1» es el archivo `ch01_supp_02.png`.** El handoff cuenta desde 0. Lo confirmé antes de gastar: es el único con `persona: []` y Daniel en el prompt, y es la mujer con la foto. `ch01_supp_01.png` es Daniel caminando y no se tocó.
2. **Orden de las madres:** `persona` primero; después los nombres del prompt, en orden de aparición; al final `foto_madre_ref`. Con `nb2_lite`, `foto_madre_ref` no entra (F68).
3. **`_madres_para_item([p], [], …)` de la secuencia no recibe prompt:** ese lote pregunta por una persona ya elegida, y la secuencia no se usa con Nano Banana.
4. **Dos cambios chicos más en `_fix_core`:**
   - Respalda también `_native` y `.llamada.json`, que el motor pisa. Vale para cualquier «pedir fix».
   - «Foto anclada a la madre de…» ahora nombra las madres que realmente se usaron. Antes salía solo de `persona`, y aquí no habría dicho nada.

## Etapa A

| Qué | Cómo |
|---|---|
| `_nombres_en_prompt` | Nombres del registry enteros en el prompt; gana el más largo; claves `__…` fuera |
| `_madres_para_item(…, prompt="")` | Candidatos = `persona` + nombres + refs; mismo filtro de era, sin repetir, tope 2 |
| Llamadores | Los 3 de `asset_manager` que eligen madres para generar, y QA (`_madres_de_entrada`, con el prompt re-armado en `_fix_core`) |

**Tabla de las 99 fotos:** [TABLA_MADRES.md](TABLA_MADRES.md). Cambia 1: `ch01_supp_02`, `[]` → `Daniel Écija`. Su año es 2026 y Daniel es de 1962-1963, pero 2026 no cae en un tramo fuera de era de `condition_by_period`, así que aporta, como dice el handoff. La tabla se generó antes de la prueba real.

**Tests:** `test_module_f71b.py`, sin red: el caso real (como fixture), «Daniel Écija hijo», nombre entero, claves `__`, filtro de era, tope 2, madre que no existe, QA con el prompt re-armado sin guardar en `persona`, QA sin nombre sigue sin madre, y respaldo de nativo y llamada. `PEDIDO_*` sin cambios (`test_pedidos_byte_a_byte_con_el_handoff`).

**Suite amplia sin red** (los `pytest` de `verificar.sh`, sin fase2b ni `gfx_lab`, como en F71): 1492 verdes, 30 saltados, 3 xfailed y 3 fallas, las mismas de F71: `m03_merge_timing` ×2, previas, y `f51c`, que lee una narración congelada. `pedido_paquetes_wittenoom.txt` quedó con el mismo md5. Mapa: 0 fallas.

## Etapa B: prueba real (una sola)

Pedido: «la foto que sostiene la mujer es de Daniel Écija joven, su cara». Respuesta del sistema:

> foto rehecha; casilleros editados: subject, action. El filtro de producción sacó: manos/cara: manos en plano close. Foto anclada a la madre de Daniel Écija (casillero persona: no cambia con el pedido).

| Casillero | Antes | Después |
|---|---|---|
| `subject` | An aged black-and-white print of Daniel Écija as a young man with a bandaged foot, his face clearly visible and recognizable as Daniel Écija's, kept by his family | An aged black-and-white print of Daniel Écija as a young man, his face clearly visible and recognizable as Daniel Écija's in the upper part of the print, his bandaged foot visible below, kept by his family |
| `action` | The worn photograph lying on a lace tablecloth as an older Spanish woman, out of focus behind it, leans over it to tell its story | The worn photograph held in both hands of an older Spanish woman, out of focus behind it, as she leans over the lace tablecloth to tell its story |

- **Motor:** `google/nano-banana-2-lite/edit`, con 1 referencia (`ae577008…`, la madre de Daniel). `persona` sigue `[]`.
- **Backup:** `assets/_qa_backups/*.20261101_165208.*`: foto, `_graded`, nativo, llamada, guion y `03_visual`. Horneado de ch01 invalidado (`ch01_hybrid_visual.mp4` no existe).
- **Evidencia:** `ch01_supp_02_antes.png`, `_antes_graded.png`, `_despues.png`, `_despues_graded.png`, `prueba_f71b.json`.

**El manifest no cambia:** `_fix_core` no lo toca, como en cualquier «pedir fix». Su `prompt` y `foto_madre_refs` de esta foto quedan con lo anterior, y fase2b le pasa ese `prompt` al director de movimiento.

## Costo

**US$ 0,0605:** Opus US$ 0,0185 (casilleros) + Nano Banana US$ 0,042 (estimado). El handoff esperaba ≈ 0,042 y no contaba a Opus. El dato facturado está en el panel de fal.

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | «ch01 supp 1» = ch01_supp_02.png; supp_01 intacto | OK (lectura correcta, ver obs. A) | Guion vivo: supp[0] tiene persona ['Daniel Écija'], 1963, «The same mid-20s Spanish miner…». supp[1] tiene persona [], 2026, «An aged black-and-white print of Daniel Écija…». Es la mujer con la foto: la imagen «antes» lo muestra. ch01_supp_01.png, _graded, _native y .llamada.json tienen fecha Nov 1 01:01, sin tocar. |
| 2a | Conteo de las 99 fotos | OK | Mi script (chk.py en el scratchpad) recorrió image_f8, image_prompts y supp: 99 ítems. Solo ch01_supp_02 nombra a alguien del registry que no está en persona. Con comparación laxa (sin acentos, por apellido o por nombre) no aparece ningún otro caso. TABLA_MADRES.md: 99 filas, cambia 1 (`[]` → Daniel Écija). |
| 2b | Coincidencia parcial | OK | asset_manager.py:1085-1096: regex `(?<!\w)nombre(?!\w)`, ordenado por longitud, y tapa lo ya hallado. Claves `__` fuera. «Daniel Écija hijo» no dispara a «Daniel Écija». «Daniel Écija's» sí cuenta (el apóstrofe no es `\w`); el prompt nuevo lo contiene y sigue dando la madre (llamada con referencias_md5 ae577008…). Mayúsculas y acentos son exactos: «DANIEL ÉCIJA» o «Daniel Ecija» no disparan. No hay un caso así en las 99. |
| 2c | Tests | OK | f71b + f60_bc + f68 + f69 = 78 passed, sin red. No existe un test_module_qa_studio*.py (hay test_module_qa_form_cost.py); lo de QA está en test_module_f71b.py. |
| 3 | Llamadores de `_madres_para_item` | PARCIAL | asset_manager.py:1331 (pre-paso de secuencia, `[p], []`, sin prompt; el reporte lo declara). :1414 (flux) pasa item["prompt"]. :1672 (supp de cap veo) pasa prompt. :1738 (image_f8 del clip) pasa image_prompts[0], que es la foto 1 y la única que usa madres_f8 (:1762 y :1796, `idx == 1`). qa_studio_server.py:846 (`_reseed_core`) pasa por `_uris_madres`, que usa entry["prompt"] por defecto. :1165 (`_fix_core`) pasa prompt_final, el re-armado. `_fotoclip_core` va por `_fix_core`. El único que no pasa el prompt es la secuencia, y no se usa con nb2_lite. |
| 4 | Diff guion vivo y 03_visual contra backup 165208 | OK | Recorrido recursivo de ambos: solo cambia chapters[0].supplemental_image_prompts[1]: subject, action, prompt, raw_llm_prompt y la clave nueva `_f8_problemas`. `persona` igual. PEDIDO_* no aparece en el diff de asset_manager.py ni en el de qa_studio_server.py. El test «byte a byte» pasa. |
| 5 | Imágenes y filtro de `action` | OK (el reporte describe bien) | La cara del retrato «después» es la de la madre: hombre joven de frente, pelo corto oscuro, cejas gruesas, camisa blanca. En «antes» era un chico sonriente de suéter con otra cara. La mujer desapareció: solo se ven manos sosteniendo la foto, y la composición cambió (ya no es la mesa con encaje). La foto impresa es un carnet arriba y el pie vendado abajo, como dos fotos pegadas. prueba_f71b.json: `action` quedó en casilleros_despues («held in both hands of an older Spanish woman…»), pero prompt_despues y llamada.nb2_lite.texto no la contienen. El texto devuelto dice «El filtro de producción sacó: manos/cara: manos en plano close». |
| 6 | Riesgo de «same person» | Ver riesgos | asset_manager.py:358 (FRASE_EDIT_UNA). |
| 7 | Números de suite y costo | OK | suite_b/amplia.log: 3 failed, 1492 passed, 30 skipped, 3 xfailed; las 3 fallas son f51c y m03_merge_timing ×2, como dice el reporte. Costo: prueba_f71b.json usd_total 0.060488 (Opus 0.018488 + NB2 lite 0.042 estimado), igual a US$ 0,0605 del reporte. |
| 8 | Reglas del handoff | OK | Backup 165208 con foto, _graded, _native, .llamada.json, guion y 03_visual. Los de 161301 y 161413 son de QA de Omar y no se tocaron. No existe ningún *hybrid* en assets (horneado invalidado). Línea de Omar 16:31 en DECISIONES.md. Stickers y mapa actualizados. Es una sola corrida. Parada en F71b_REPORT.md. La línea de ESTADO_SESION todavía no está (permitido). |

Observaciones
A. «ch01 supp 1» del handoff es supp_02.png, contando desde 0 (el handoff mismo dice «ch01 supp 1»). La lectura es correcta y consistente con la causa raíz (persona [] y Daniel en el prompt). Conviene que Omar lo sepa.
B. El reporte afirma que el manifest no cambió y que `_fix_core` no lo toca. No lo verifiqué contra un backup del manifest: NO VERIFICABLE.
C. `_f8_problemas` es una clave nueva en el ítem. No está en el reporte.

Fuera de alcance: ninguno atribuible a F71b. Archivos modificados: asset_manager.py, qa_studio_server.py, DECISIONES.md, MAPA_PROYECTO.*, orquestador.json. diag_234_cap4.py, f28a.log y pedido_paquetes_wittenoom.txt ya figuraban modificados en el git status inicial, y no los relaciono con F71b.

Riesgos que el contrato no cubre
- Frase «same person» (punto 6): con la madre presente, el motor recibe «A photograph of the same person shown in the reference image». En ch01_supp_02 el sujeto real es otra persona que sostiene una foto, y el resultado muestra el efecto. Pasó la identidad de Daniel al retrato (bien), pero el motor tomó la frase como la foto completa: la mujer desapareció y quedaron solo las manos. En producción, la regla se dispara con cualquier nombre del registry en el prompt, aunque solo sea mención, foto, cartel o posesivo. Esa foto pasa a ser «la persona de la referencia» y puede borrar o fusionar a los otros sujetos. Hoy solo afecta 1 de 99 fotos, pero un guion nuevo escrito por Opus con «print of X» o «X's family» lo dispararía más. El contrato no trae ninguna salvaguarda ni verificación visual.
- Manifest y fase2b: tras el fix, el manifest conserva el `prompt` viejo (con la mujer) y fase2b se lo pasa al director de movimiento. El reporte lo declara. El movimiento aprobado del clip puede quedar desfasado de la foto nueva.
- Secuencia (asset_manager.py:1331): no pasa el prompt. Con un motor que use secuencia, una foto de persona única cuyo prompt nombre a una segunda persona seguiría saliendo con una sola madre. Hoy no se usa con nb2_lite.

**Adenda mía, posterior al veredicto:**
- **Observación B:** el manifest tiene fecha 15:45, anterior a la prueba (16:52), así que esta tanda no lo tocó.
- **Observación C:** `_f8_problemas` es donde `armar_item` deja lo que sacó el filtro: «manos/cara: manos en plano close». Es lo que explica que falte la mujer.
- **Sobre el riesgo de «same person»:** para mí, la mujer falta sobre todo porque el filtro sacó su oración del prompt. La frase puede sumar, pero con una sola corrida no se puede separar.

