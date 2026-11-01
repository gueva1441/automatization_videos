# F70 (lab) — fotos sin texto pedido y cola de época sin «taken in»

Handoff: `lab/hyperframes/f70/HANDOFF_F70_lab.md` (md5 d09999a071c2a27f17acd26c8de03462).

## Etapa 0 — dónde se arma cada cosa (solo lectura, sin cambios)

Las dos piezas están en `script_engine/m03_imagenes_v3.py`, no en el perfil del motor.

| Pieza | Dónde | Qué hace |
|---|---|---|
| **A**, frase de texto escrito | `frase_cartel`, línea 590 | Arma la frase F51f en 3 formas: «The word(s) "X" is/are written …» (606), «The <ubicación> reads "X" …» (608) y «A sign reads …» (601) |
| A, cuándo entra | `armar`, líneas 628 y 640 | Con `text_in_image.present` y `text`, va en el casillero `texto` |
| **B**, cola de estilo | `ESTILO_C`, línea 198 | «A grainy 35mm documentary photograph taken in {anio}, …» |
| B, cuándo entra | `armar`, línea 644 | Con año usa `format`; sin año, `ESTILO_C.replace(" taken in {anio}", "")` |
| Frase final | `NO_TEXT`, línea 415; `armar`, línea 645 | «No readable text, no signage, no labels.» **solo si no hay cartel** |

**Dos cosas que importan si esto pasa a producción:**
1. **Las fotos con cartel no traen la frase final.** El handoff da por hecho que queda igual, pero en esas fotos no existe: la línea 645 la omite cuando hay texto. En el lab no la agrego: «quitar, no reemplazar». Con el cambio en `armar`, en cambio, esas fotos sí la recibirían, así que el lab no prueba exactamente lo que daría producción.
2. **El `replace` de la línea 644 depende del texto « taken in {anio}».** Si cambia `ESTILO_C`, hay que cambiarlo también o las fotos sin año quedan con un `{anio}` literal.

## Resultado

**Quitar la frase no alcanza para sacar el texto; cambiar la cola sacó el sello de la foto que lo tenía, con una sola corrida.** Las 13 salieron por Nano Banana 2 Lite, sin respaldos ni fallas, con las mismas madres que producción.

- **A (frase de texto), 5 fotos:** la palabra pedida desaparece en las 5, pero solo `ch03_img_08` queda sin texto legible. En `ch05_img_03` y `ch07_supp_04` sale más texto inventado y mal escrito. Estas fotos son de un papel o un letrero: el modelo los llena igual.
- **B (cola), 13 fotos:** el «2023» de `ch06_img_07` ya no está. Pero `ch07_supp_04` trae ahora «2026» escrito a mano dos veces. El año sigue en la oración del lugar («…, 2026»), y B no toca esa parte.
- **Control, 6 fotos:** ninguna perdió época, color ni persona, y ninguna trae texto legible ni sello. Sí cambian encuadre, ropa y fondo, pero **eso no se puede atribuir al prompt:** producción no fija semilla, así que el mismo texto también cambiaría.

### Tabla

| Foto | Grupo | Frase A existía | Cola cambió | Texto legible en la nueva | Sello de fecha en la nueva | Qué más cambió |
|---|---|---|---|---|---|---|
| `ch03_img_08` | error | sí | sí | **no**: «Asbestesis» ya no está; líneas sin leer en la hoja | no | Encuadre invertido; por la ventana se ve un pueblo en lugar de polvo |
| `ch03_img_15` | error | sí | sí | **sí**: desapareció la tarjeta, pero aparece un almanaque «OCT 1 1962» | no (el almanaque no es sello de cámara) | La caja de luz parece un panel moderno, fuera de época; el médico es otra cara (no tiene madre) |
| `ch05_img_03` | error | sí | sí | **sí, peor**: «Mine CLOSURE: Wittenoom Hit», «5c Rowfer Ilad dn» | no | Sigue «THE NORTHERN TIMES». Perdió el titular del guion |
| `ch06_img_11` | error | sí | sí | **sí**: «NEWMAN 428 km / MARBLE BAR 188 km», inventado y bien escrito | no | **Ya no es el cartel de Wittenoom**, que era el sujeto. «POPULATION 8» desapareció |
| `ch02_img_04` | error | no | sí | **no**: «SEAT 600» ya no se lee | no | El coche pasa a verse de frente; los novios conservan el parecido |
| `ch07_supp_04` | error | sí | sí | **sí, peor**: «FOHMER WITTEROOM TOWNSITE»; logos falsos | **a mano**: «2026» dos veces, en una chapa | La auditoría daba el letrero viejo por correcto: quedó peor |
| `ch06_img_07` | error | no | sí | no | **no**: el «2023» naranja ya no está | Blazer gris en vez de azul; menos retratos en la pared |
| `ch02_img_05` | control | no | sí | no | no | Cara igual. Vestido azul en vez de tweed; el muelle y el agua cambian |
| `ch03_img_12` | control | no | sí | no | no | **Pierde «pause mid-stride»:** 5 hombres posando, sin polvo cayendo. Blanco y negro en las dos |
| `ch04_img_09` | control | no | sí | no | no | Cara igual, más demacrada. Se ve la cama entera y la bandeja tiene instrumental |
| `ch05_img_12` | control | no | sí | no | no | Cara igual. Luz más cálida; un tanque en lugar de la calle |
| `ch06_img_04` | control | no | sí | no: chapa con nombre, sin leer | no | Campera de cuero en vez de denim; el pasaporte queda abierto en el mostrador |
| `ch07_supp_02` | control | no | sí | no | no | Mismo anciano; **el otro hombre cambia** (no tiene madre). Con arroyo y cerco, igual época |

Texto legible y cambios salen de mirar las hojas y los recortes en `recortes_detalle.jpg`. Es mi lectura; las hojas están para que la confirmes.

### Límites

1. **Las 5 fotos con frase A salieron sin «No readable text…»,** porque producción no la pone cuando hay cartel (Etapa 0) y el handoff pide no reemplazar nada. Puede explicar parte del texto que aparece. Un cambio en `armar` sí la pondría, así que esta prueba no anticipa esas 5 fotos en producción.
2. **Una corrida por foto y sin semilla.** El «2023» que desaparece podría ser azar: no se sabe con qué frecuencia salía. La cola no se probó por separado, porque el handoff pide A y B juntos.
3. **No medí calidad de cara** más allá de mirarla: las caras de las madres se mantienen a simple vista.

### Archivos

Por foto: `<foto>.diff.txt`, `<foto>_hoja.jpg` (vieja | nueva), `<foto>_native.png` (lo que devolvió el motor, 1376×768), `<foto>.llamada.json` (texto y request_id) y `<foto>.png` (2560×1440). Los 13 `<foto>.png` quedan en disco y **no van al commit** (≈ 50 MB; `.gitignore` de esta carpeta): son el nativo escalado. También `run_lab.py` y `resultados.json`.

### Costo

**≈ US$ 0,55:** 13 fotos a US$ 0,042, el valor registrado en F68. Es estimado: fal no devuelve tokens y su API de uso responde 403, así que el real está en el panel. Sin llamadas a Opus.

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Etapa 0: dónde se arman A y B, con archivo:línea, sin tocar código | OK | `lab/hyperframes/f70/F70_REPORT.md` L9-15. Verifiqué las líneas en `script_engine/m03_imagenes_v3.py`: ESTILO_C 198, NO_TEXT 415, frase_cartel 590 (formas 601/606/608), armar 628/640/644/645. Todas coinciden. `git status` de `script_engine`, `asset_manager.py` y `cost_tracker.py` sale limpio. |
| 2 | Texto nuevo = viejo de output/ con solo A y B | OK | Lo recalculé aparte, con otra lógica que el script: cambié «taken in AAAA» y quité la oración que lleva «in clear crisp». Dio idéntico en las 13. Frase A quitada en 5 fotos (ch03_img_08, ch03_img_15, ch05_img_03, ch06_img_11, ch07_supp_04) y en 0 de las otras 8. ch05_img_03 es la variante «The Front page headline reads "COSTS CLOSE MINE"…». |
| 3 | Parámetros, endpoint y referencias_md5 iguales a producción | OK | Los tres campos son idénticos en las 13. Todas con `estado: ok`, endpoint `google/nano-banana-2-lite[/edit]`, tolerancia 6, una imagen por llamada. `resultados.json` no tiene respaldos ni errores. |
| 4 | Fotos nuevas solo en f70/ | OK | `run_lab.py` solo escribe en `AQUI`. Las 26 png están en f70/. |
| 5 | output/ sin cambios por esta tanda | OK | Los 26 originales (13 png y 13 llamada.json) son del 2026-11-01 01:01-01:03, anteriores al lab, que corrió de 14:51 a 14:52. Detalle en observación 1. |
| 6 | No tocar producción, config, QA, guion ni main | OK | `git status` solo muestra modificados `diag_234_cap4.py`, `f28a.log` y `f58/pedido…txt`. Los tres ya estaban modificados antes de empezar (snapshot inicial; el pedido de f58 es del 01:59). El único untracked nuevo es `f70/`. |
| 7 | Hoja vieja \| nueva rotulada por foto y diff por foto | OK | 13 `_hoja.jpg` con rótulos VIEJA/NUEVA, 13 `.diff.txt` y `recortes_detalle.jpg`. |
| 8 | Tabla del handoff | OK, con matices | Contrasté las 13 hojas sin usar la tabla. Coinciden todas las celdas de texto legible y sello. Matices en las observaciones 3 a 5. |
| 9 | Costo real al final | PARCIAL | El reporte da ≈ US$0,55 (13 × 0,042) y dice que es estimado, porque la API de uso de fal responde 403. No es costo real. |
| 10 | Veredicto del revisor pegado en el reporte | NO VERIFICABLE | `F70_REPORT.md` todavía no tiene la sección. Es el paso que sigue a este veredicto. |
| 11 | `.gitignore` deja fuera los 13 `<foto>.png` de 2560 | OK | `git check-ignore` confirma que `ch*.png` se ignora y `ch*_native.png` se conserva. Lo que va al commit es la imagen nativa 1376×768, las hojas, los recortes y los diffs. Es aceptable: los 2560 son el nativo escalado, así que la información está en los `_native`. Las hojas usan los 2560 y sí van commiteadas (~3,7 MB), y dan la evidencia visual. |

Contraste por foto con mi lectura:
- **Coinciden con la tabla:** ch03_img_08, ch03_img_15 (almanaque «OCT 1 1962»), ch05_img_03 (texto inventado más abundante), ch06_img_11 (cartel NEWMAN/MARBLE BAR), ch02_img_04, ch07_supp_04 («2026» a mano dos veces en una chapa), ch06_img_07 (el «2023» ya no está) y las 6 de control.
- **ch03_img_15:** la tabla solo menciona la caja de luz. Cambió además la cara del médico: más ancha y de otra persona, sin madre que la fije. El reporte no lo dice.
- **ch03_img_12:** hay 5 hombres posando, como dice la tabla. Pierde el movimiento y el polvo, y también la perspectiva de recorrido.
- **ch07_supp_04:** la celda de sello dice «a mano» y no «sí». Es defendible, pero queda ambiguo para la columna «sello de fecha».

Observaciones:
1. En `output/123bbb64-9fca-4395-8bf4-57d60e219ef1/publish/thumb_candidates/` hay archivos nuevos de las 14:51 (`paquete_01*.png`, `paquete_01_base.llamada.json`, `metadata.json`). También hay backups de QA y un `ch01_clip_01.mp4` de las 14:30-14:34. No son del lab: `run_lab.py` no escribe ahí y el prompt de `paquete_01_base` es otro. Pero sí hay actividad en output/ concurrente, de otro proceso. El reporte debería decirlo, o el criterio «nada nuevo en output/» queda a medias.
2. Límite 1 del reporte, bien señalado: las 5 fotos con frase A salieron sin «No readable text…», porque producción no la pone cuando hay cartel. El lab no prueba lo que daría el cambio real, y eso debilita las conclusiones sobre A en esas 5.
3. El `.replace(" taken in {anio}", "")` de la línea 644 depende del texto de ESTILO_C. Está en el reporte.
4. No hay semilla fija, y el reporte lo reconoce. Los cambios en controles no son atribuibles al prompt.

Fuera de alcance: ninguno. Lo nuevo es `lab/hyperframes/f70/` entero. Los commits de ESTADO_SESION y de f70/ quedan pendientes y no se cuentan como falla.

Riesgos que el contrato no cubre: la muestra es una corrida por foto, así que «el 2023 desapareció» puede ser azar. El año sigue en la oración del lugar (aparece «2026» a mano en supp_04). Si se quita A en producción sin reponer la frase final, ch05_03 y supp_04 empeoran.

**Adenda mía, posterior al veredicto:** agregué a la tabla la cara del médico de `ch03_img_15`, y la columna de sello de `ch07_supp_04` queda como está: no es sello de cámara, pero es una fecha que aparece. Sobre la observación 1: esos archivos de `output/` no son de esta tanda. Son de otro proceso, que no identifiqué (por los nombres, QA Studio o el empaquetado); no los toqué. Ningún resultado cambió.
