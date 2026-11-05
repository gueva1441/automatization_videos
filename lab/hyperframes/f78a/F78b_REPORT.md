# F78b — Reporte: variantes con «estado visible en el cuerpo» y edad exacta

Rama `f11-guion-v4`, base `b891b75`. Handoff `lab/hyperframes/f78a/HANDOFF_F78b_estado_visible_edad.md` (md5 `bcc4acf89ba26fd3b06eaa5f2e7cfa75`); la ADENDA manda sobre el cuerpo.

- Etapa A: commit `72018f3`.
- Etapa B: solo Colza (`c4934b7d-3f54-448f-ba5f-539dc744f0d8`), **US$ 0,5263**.
- **PARADA.** Omar y el analista miran la hoja. La Etapa C de F78a no corrió.

## Qué se hizo
1. **Etapa A.** Código solo en `foto_madre.py` y tests en los dos archivos, con `_llamar_estados` simulado (estado no vacío en las fixtures autouse). Ningún test sale a la red: corrí `f78a`/`f60_bc`/`f68`/`f71b`/`f73` con un proxy muerto y pasaron los 108.
   - Suite amplia: 1566 passed, 29 skipped y las 3 heredadas.
   - La cuarta falla de esa corrida era `f42_mapa` (sticker de foto_madre sin actualizar). Actualicé el sticker y `mapa_modulos --check` da 0 fallas; `f42_mapa` da 4 passed.
   - Tabla de qué se pediría: `a2/tabla_pedidos.md`. Commit `72018f3`.
2. **Etapa B** (`b2/etapa_b2.py`, venv, 151 s). Orden de la adenda 7:
   - preflight: de 94 fotos y clips no faltaba ninguno;
   - las 8 variantes de F78a se movieron a `foto_madre/_previas_f78b/` con sus 4 archivos (png, _native, .prompt.txt, .llamada.json);
   - `generate_fotos_madre_personas`: los rasgos salieron del cache, sin llamada. Las 7 madres limpias no cambiaron: `rasgos.json` quedó con el mismo md5 (`intacto: True` en el log);
   - 1 llamada de estados con 6 filas → `estados.json`;
   - 8 variantes nuevas;
   - `save_db` y `m06.assemble_final_script`;
   - las 4 fotos de control: sus 4 archivos a `<cap>/_previas_f78b/` y `process_script`, que regeneró exactamente esas 4.
   - Sin Opus de m03 y sin voz ni render.
3. **Hoja:** `lab/hyperframes/f78a/ETAPA_B2.html`. Muestra:
   - `estados.json` junto a la condición del canon;
   - cada variante en tres versiones: madre limpia, F78a y F78b, con sus prompts;
   - las 4 fotos de control, F78a y F78b, con su prompt.

## Diff (commit 72018f3)
- **`foto_madre.py`** (+151 / −45):
  - `ESTADOS_JSON`.
  - `PREVIAS_DIR` pasa a `_previas_f78b`: la carpeta de lo reemplazado es la de la tanda que lo reemplaza.
  - `_guardar_prompt_madre(…, firma)` y `_firma_de(dest)`: la firma es el md5 de (estado_visible + edad) y va en una línea propia del `.prompt.txt`.
  - `_a_previas(path, carpeta)` mueve png, `_native.png`, `.prompt.txt` y `.llamada.json` sin pisar nada (sufijo `_2`…).
  - `PROMPT_ESTADOS`: el prompt del handoff, tal cual.
  - `_llamar_estados(filas)`: `MODELO_CASILLEROS` con su esfuerzo, schema con `name` (enum), `tramo` (enum) y `estado_visible`. Cruza la respuesta por (name, tramo); un par cruzado no entra.
  - `estados_visibles(filas, madre_dir)`: cache `estados.json` por md5 de la entrada; un par que falta vale "".
  - `_prompt_variante(cv, estado_visible)`: el texto nuevo del handoff, con la edad exacta en dígitos y el `estado_visible` con `rstrip('.')`. Se borró la frase «Show only…» y el uso de `descriptor_edad` en la variante; `descriptor_edad` sigue decidiendo la clave.
  - `generate_fotos_madre_personas`, bloque de variantes:
    - claves → filas únicas (name, tramo) sacadas de `por_clave`;
    - si ninguna clave tiene tramo, no hay llamada ni `estados.json`;
    - si la llamada falla, no se mueve ni se genera nada;
    - clave sin estado visible ni edad → «sin variante: sin estado visible»: no entra en `pedidas` y la variante vieja se mueve;
    - firma distinta → la vieja va a `_previas_f78b` y se rehace;
    - firma igual → se reusa.

  Las claves, cuándo hay variante, `_madres_para_item` y m06 no cambiaron.
- **Tests:**
  - `test_module_f60_bc.py`: `_llamar_estados` simulado en la fixture autouse.
  - `test_module_f78a.py`:
    - `_fakes` con estados simulados no vacíos;
    - reescrito el test del prompt de la variante: edad exacta, `estado_visible`, sin «Show only» ni «early-30s»;
    - 8 tests nuevos: una llamada con pares únicos y el prompt nuevo; sin estado visible ni edad → sin variante (la vieja se mueve con sus 3 archivos); edad sola → variante solo con la edad; cache de estados; firma que cambia → solo esas variantes se rehacen; `rasgos.json` y madre intactos; variante de antes de la firma → se rehace; estados que fallan → nada se mueve; sin tramos → sin llamada; schema, enums y cruce; `_a_previas` con todos los hermanos y sin pisar.

## Tabla de Etapa A (qué se pediría, Colza)
| persona | clave | edad | condición (canon) | qué se pediría |
|---|---|---|---|---|
| Arcadio Fernandez | 1981-1989 | — | Deformed hands and upper body with disabling chronic pain | variante con el estado visible; "" → sin variante |
| Angela Menseger | 1981-1985 | — | Chronically ill … veins exhausted by transfusions, and diagnosed with liver cancer | ídem |
| Jesús Lozano | 1981-1981 | — | Hospitalized in a glass-walled room with ten other children… | ídem |
| Carmen Cortés | 1981-1982 | — | … losing more than twenty kilos and visibly emaciated | ídem |
| Carmen Cortés | 1981-1982_15 | 15 | ídem | «now 15 years old» + estado visible |
| Carmen Cortés | 1992-2000_33 | 33 | Unable to work after a herniated disc, living on a disability pension | «now 33 years old» + estado visible |
| Carmen Cortés | 1992-2000_25 | 25 | ídem | «now 25 years old» + estado visible |
| Mercedes García | 1981-1981 | — | Suffering cramps and insomnia, too weak to press a typewriter key | variante con el estado visible; "" → sin variante |

La llamada de estados lleva 1 pedido con 6 filas (pares persona/tramo únicos).

## estados.json (`output/<tid>/foto_madre/estados.json`, Opus 5.5, 1 llamada, US$ 0,0263)
| persona | tramo | estado_visible |
|---|---|---|
| Arcadio Fernandez | 1981-1989 | Hands with deformed, contracted fingers and a visibly misshapen, rigid upper body |
| Angela Menseger | 1981-1985 | Forearms with bruising and puncture scars over collapsed veins from repeated transfusions |
| Jesús Lozano | 1981-1981 | A child's face streaked with tears, with features contorted in a grimace of pain |
| Carmen Cortés | 1981-1982 | Visibly emaciated body with sunken cheeks, prominent collarbones and thin, wasted arms and hands |
| Carmen Cortés | 1992-2000 | (vacío) → sus variantes llevan solo la edad |
| Mercedes García | 1981-1981 | Tired face with dark circles under the eyes and weak, limp hands |

## Etapa B: qué salió (mirado en las hojas de contacto)
- **Variantes:** salieron las 8 claves. 6 por Nano Banana 2 Lite y 2 por el respaldo Seedream 4.5 (`carmen@1981-1982` y `carmen@1981-1982_15`: menor con estado, moderada).
  - **Arcadio:** los dedos ahora se ven contraídos y deformes. Era lo que faltaba.
  - **Angela:** antebrazos con moretones.
  - **Carmen 1981-1982:** emaciada, con clavículas marcadas.
  - **Mercedes:** cara cansada con ojeras. El marco oscuro de su madre sigue.
  - **Lozano:** ya no aparece la sala ni otros niños, pero sale llorando con muecas de dolor. Es una expresión, aunque el prompt pide «ni sentimientos»; el analista lo admitía como «signos en la cara».
  - **Carmen 25 y 33:** algo mayor que en F78a, pero sigue sin leerse de 33.
- **4 fotos de control** (mismo prompt de escena):
  - `ch01_supp_05` (juicio): Arcadio igual de cara, con las manos juntas y algo crispadas. La deformación de la variante se transmite poco a la escena.
  - `ch06_img_14` (calculadora): las manos sobre la calculadora se ven casi normales. El /edit de la escena no conserva los dedos deformes de la referencia.
  - `ch04_img_12` (Lozano): la escena es la sala de vidrio que pide el propio prompt de la foto, con la variante nueva de referencia.
  - `ch07_supp_07` (Carmen 2000): sigue saliendo un muchacho de pelo corto. El «short practical hair» del prompt de escena manda; es el abierto previsto (se arregla en m03).
- **Las otras fotos de cada variante** (Arcadio 13 más, Angela 4, Carmen 7, Mercedes 2, Lozano 2) siguen con la foto de F78a hasta la Etapa C.

## Costo real de la Etapa B (`b2/costo_etapa_b.json`)
| servicio | llamadas | US$ |
|---|---|---|
| Anthropic Opus 5.5 (estados) | 1 | 0,0263 |
| Nano Banana 2 Lite /edit (6 variantes + 4 fotos) | 10 | 0,4200 |
| Seedream 4.5 /edit (2 variantes de respaldo) | 2 | 0,0800 |
| **total** | 13 | **0,5263** |

## Declarado (decidí y sigo)
- **Lozano tiene variante.** La adenda 5 esperaba que Lozano@1981-1981 quedara sin variante (estado vacío) y que `ch04_img_12` saliera con la madre limpia. La llamada devolvió un estado no vacío (lágrimas y mueca), así que hay variante y la foto de control la usa. El código hace lo que pide el handoff; difiere la expectativa.
- `PREVIAS_DIR` cambió a `_previas_f78b`. Lo que F78a ya movió sigue en `_previas_f78a`.
- La firma es el md5 de {estado_visible, edad} y va en el `.prompt.txt`. Una variante sin firma (F78a) cuenta como firma distinta.
- `anio_estilo` sigue siendo el primer año del tramo: Carmen de 33 lleva el estilo de 1992 (adenda 8).
- Los menores con estado caen al respaldo Seedream (2 de 2 variantes de Carmen niña).
- Las variantes que la Etapa B no movió a mano no existen: las 8 se movieron al empezar.

## Abierto
- **Etapa C de F78a sin correr** (OK de Omar). Al correrla, las fotos de las variantes nuevas pasan a usarlas, incluida `ch01_img_01`, que es la de arranque del clip del gancho.
- **La deformación de manos no pasa a la escena:** la variante de Arcadio ya tiene los dedos deformes, pero el /edit de `ch06_img_14` los suaviza. Si Omar lo ve poco, el refuerzo va en el texto de la escena (m03), otra tanda.
- **Lozano llora en la variante:** la expresión de dolor queda fija en la referencia de sus 3 fotos. Opciones: aceptarlo, o prohibir la expresión en el prompt de estados (cambio de texto del analista).
- **Carmen de 33 no se lee de 33**, ni en la variante ni en `ch07_supp_07` (muchacho de pelo corto). Abierto del handoff: se arregla en m03.
- La madre de Mercedes con marco oscuro: «se arregla si se repite».
- `lab/hyperframes/f60/etapa_bc_prueba.py:90` sigue con la firma vieja de `_clave_lote`: estaba en «no entra».
- Nano Banana modera a los menores con estado; en la Etapa C esas /edit pueden caer al respaldo Seedream y cambiar de estilo.

## Veredicto del revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Handoff md5 bcc4acf8… | OK | `md5sum` coincide con el del pedido y con el commit 72018f3 |
| 2 | A: código solo en foto_madre.py + tests | PARCIAL | El código de producción es solo foto_madre.py. El commit 72018f3 también toca DECISIONES.md, lab/MAPA_PROYECTO.json y .md, lab/mapa/stickers/fase2a.json, suite.log, tabla_pedidos.py y .md. Son derivados o el mapa, pero el pedido decía «solo» |
| 3 | `_llamar_estados`: una llamada, MODELO_CASILLEROS con ESFUERZO, schema con enums name/tramo, cruce por (name, tramo), cache `estados.json` aparte de rasgos | OK | foto_madre.py, diff de `_llamar_estados` y `estados_visibles` |
| 4 | Prompt de estados tal cual el handoff | OK | `PROMPT_ESTADOS` es el texto del handoff l.30-35 |
| 5 | Prompt de variante: edad en dígitos, `estado_visible` con `rstrip('.')`, sin «Show only», sin condición cruda | OK | `_prompt_variante`. El `.prompt.txt` de carmen@1992-2000_33 lo confirma |
| 6 | Sin estado ni edad → sin variante, la vieja se mueve | OK | rama «sin variante: sin estado visible» en `generate_fotos_madre_personas` |
| 7 | Firma md5(estado+edad); si cambia, la vieja va a `_previas` y se rehace; una variante sin firma se rehace | OK | `_firma_de`, `_guardar_prompt_madre(firma)`; las `.prompt.txt` nuevas llevan `firma:` |
| 8 | `_a_previas(path, carpeta)` mueve png, _native, .prompt.txt, .llamada.json | OK | `_previas_f78b` tiene los 4 archivos de las 8 variantes |
| 9 | Una fila por par único; Colza = 6 filas; si ninguna clave tiene tramo no hay llamada; si falla la llamada no se mueve ni se genera nada | OK | `estados.json` tiene 6 filas en `entrada`; el código tiene las ramas de «sin tramos» y de fallo |
| 10 | Tests con `_llamar_estados` mockeado y ninguna llamada a la red | OK | Corrí f78a, f60_bc y f42_mapa con proxy muerto: 61 passed |
| 11 | Suite rápida | OK | `a2/suite.log`: 1566 passed, 4 failed (3 heredadas más f42_mapa, que el reporte dice corregida). Corrí f42_mapa y pasa |
| 12 | A: tabla persona/tramo/edad/condición → qué se pediría; commit | OK | `a2/tabla_pedidos.md`; commit 72018f3 |
| 13 | B: solo Colza, preflight, orden estados → variantes → m06 → mover 4 fotos → process_script | OK | `b2/etapa_b2.py` l.1-8 y 76-105; `etapa_b2.log` EXIT 0; no hay llamadas a m03 |
| 14 | Nada de Opus de m03 | OK | `costo_etapa_b.json`: solo 1 llamada Anthropic, «foto madre estados» |
| 15 | Nada se borra: lo viejo va a `_previas_f78b/` | OK | 32 archivos en `foto_madre/_previas_f78b`; los 4 caps de control tienen `_previas_f78b` con png, _native, _graded y .llamada.json |
| 16 | Hoja `ETAPA_B2.html` | OK | Existe, 1,3 MB |
| 17 | Reporte con qué se hizo, diff, estados.json, costo real, abierto | OK | `F78b_REPORT.md`. El costo del reporte coincide con `costo_etapa_b.json` (US$ 0,5263). La sección «Veredicto del revisor» está pendiente de pegar |
| 18 | Ningún número ni lista nueva fuera de la tabla de constantes | OK | No encontré constantes nuevas. Los literales nuevos son nombres de carpeta y archivo, y DECISIONES.md tiene la línea F78b |
| 19 | PARADA después de B; Etapa C de F78a no corre | OK | El log solo regeneró las 4 fotos de control; el resto quedó en «skip». El reporte declara que las otras fotos de las variantes siguen con la foto vieja |
| 20 | Expectativa de la adenda 5: Lozano@1981 sin variante | PARCIAL | La llamada devolvió un estado no vacío («lágrimas… mueca»), así que Lozano sí tiene variante y ch04_img_12 la usa. El código sigue el handoff y el reporte lo declara. El estado contradice el propio prompt, que pide «ni sentimientos» |
| 21 | ESTADO_SESION.md se actualiza después del veredicto | FALLA | `lab/ESTADO_SESION.md` ya tiene cambios sin commitear con el texto F78b, antes de este veredicto (`git diff` lo muestra). Es solo un orden mal puesto |

Fuera de alcance:
- En el commit A: DECISIONES.md, lab/MAPA_PROYECTO.json y .md, lab/mapa/stickers/fase2a.json (el chequeo del mapa los exige).
- Fuera del commit: `lab/ESTADO_SESION.md` modificado antes de tiempo.
- Archivos modificados desde antes, no de esta tanda: diag_234_cap4.py, f28a.log, pedido_paquetes_wittenoom.txt.
- Extra: `lab/hyperframes/f78a/b/analista_vista.jpg` sin trackear.

Observaciones:
- No pude verificar el contenido visual de las fotos ni de la hoja. Solo comprobé que existen y que no están vacías.
- El log dice «grade de post: 90 imágenes → *_graded.png», es decir que el grade se pasó sobre las 90 imágenes, no solo sobre las 4. Es idempotente, pero no está declarado en el reporte.
- Quedan resultados de producto que el reporte declara y no son fallas del contrato: Carmen 33 no se lee de 33; la deformación de manos de Arcadio no pasa a la escena; Lozano aparece llorando.

Riesgos que el contrato no cubre:
- Lozano llora fijo en la referencia de sus 3 fotos. La Etapa C lo propagaría a todas.
- 2 de las 8 variantes salieron por el respaldo Seedream (cambio de estilo), y esa deriva se amplía en la Etapa C.
- `etapa_bc_prueba.py:90` sigue con la firma vieja de `_clave_lote`; el handoff lo dejó fuera.

### Adenda de CC
- **Punto 2 (archivos extra en el commit A):** son los que exigen las reglas fijas del repo: el sticker y el mapa regenerado (`mapa --check` 0, guard_mapa), la línea fechada de DECISIONES y la salida en texto de la Etapa A. Código de producción tocado: solo `foto_madre.py`.
- **Punto 21 (ESTADO_SESION antes del veredicto):** el texto se escribió antes, pero entra en el mismo commit que la Etapa B, después de este veredicto. No se commiteó nada antes.
- **Grade de las 90 fotos:** `_apply_grade` reusa el `_graded.png` existente. Solo las 4 fotos de control tienen `_graded` nuevo (20:16); el resto conserva la hora de antes (p. ej. `ch02_img_01_graded.png`, 18:42).
- **Punto 20 / Lozano:** de acuerdo, el estado devuelto incluye una expresión, contra el «ni sentimientos» del prompt. Es el primer punto del «abierto».
- **`analista_vista.jpg`:** es del analista; no la toqué ni la commiteo.
