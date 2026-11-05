# F78a — Reporte: madres de persona con identidad propia + variante por tramo (estado / edad)

Rama `f11-guion-v4`. Handoff `lab/hyperframes/f78a/HANDOFF_F78a_madres_identidad_estado.md`. El md5 inicial era 862efdb9…; con la adenda de las 19:36 pasó a `56cb5d359ced6e4fd969a1233b67ce79`.
Etapa A: commit `7d9fe85`. Etapa B: solo Colza (`c4934b7d-3f54-448f-ba5f-539dc744f0d8`), **US$ 0,8869**.
**PARADA.** La Etapa C no corrió y espera el OK de Omar.

## Qué se hizo
1. **PARADA antes de programar.** Con el dict aparte `foto_madre_variantes` del handoff, las variantes no llegaban a asset_manager, QA ni m09:
   - `fase2a._normalize_long` arma una lista blanca de claves y las tiraba;
   - QA y m09 llaman a `_madres_para_item` solo con el registry y `foto_madre_personas`.

   Omar eligió la opción (a): las variantes van dentro de `foto_madre_personas[nombre]["variantes"]`, junto con `age_at_event`, y se quedan los 3 módulos (adenda 19:36, en DECISIONES).
2. **Etapa A.** Código en los 3 módulos y tests.
   - Un subagente hizo asset_manager y sus tests, en paralelo con foto_madre y m06.
   - Se corrió la suite amplia y salió la tabla real de variantes, sin generar nada. Commit `7d9fe85`.
3. **Etapa B** (`lab/hyperframes/f78a/b/etapa_b.py`, venv, 171 s):
   - Preflight: de 94 fotos y clips esperados no faltaba ninguno. Si hubiera faltado alguno, `process_script` lo habría generado; por eso se verificó antes.
   - Las 7 madres viejas se movieron a `foto_madre/_previas_f78a/`.
   - Una llamada de rasgos, después 7 madres nuevas y 8 variantes, `save_db` y `m06.assemble_final_script`.
   - De cada una de las 6 fotos de control se movieron 4 archivos a `<cap>/_previas_f78a/`: `.png`, `_native`, `_graded` y `.llamada.json`.
   - Se corrió `asset_manager.process_script`, que regeneró exactamente esas 6.
   - No hubo Opus de m03, ni `fase1_5 --from m03`, ni voz, ni render.
4. **Hoja de contacto:** `lab/hyperframes/f78a/ETAPA_B.html` (imágenes embebidas). Muestra:
   - las madres antes y ahora, con sus rasgos;
   - las 8 variantes con su madre limpia y su prompt;
   - las 6 fotos de control antes y después, con su llamada.

## Diff por módulo (commit 7d9fe85)
- **`foto_madre.py`** (+262 / −14):
  - Constantes nuevas: `DESCRIPTOR_EDAD`, copia de la tabla de step_4e con 60+ = «elderly»; `EDAD_EN_PALABRAS` (1 a 19); `RASGOS_JSON`; `PREVIAS_DIR`.
  - `descriptor_edad(n)`.
  - `clave_de_foto(canon, anio)`: la regla única que usan foto_madre y asset_manager.
    - El tramo es el de `condition_by_period` que contiene el año; si se pisan, el más corto.
    - La edad es `age_at_event` + (año − primer año de la era), solo si su descriptor difiere del de la madre.
    - La clave es «AAAA-AAAA» o «sin_estado», más «_edad» si corresponde; sin tramo ni edad queda vacía (madre limpia).
    - `anio_estilo` es el primer año del tramo; sin tramo, el año de la foto.
  - `PROMPT_RASGOS`: el prompt del handoff, tal cual.
  - `_llamar_rasgos`: `call_json(MODELO_CASILLEROS, effort=guion_v4.ESFUERZO[…])`. El schema es una lista de {name con enum, rasgos}; `call_json` registra el costo.
  - `rasgos_personas`: cache `rasgos.json` por md5 de la entrada, con un md5 por persona.
  - `_a_previas`: mueve el archivo y su `.prompt.txt`; nunca borra.
  - `_prompt_variante`: el texto del /edit del handoff.
  - `_generate_variante`: `_generar_nb2(…, frase_de_madres=False)`, con la madre limpia como referencia.
  - `_prompt_persona` recibe `rasgos` y los pone después del canon. Cambió en el mismo lugar: no queda camino viejo.
  - `generate_fotos_madre_personas` hace, en orden:
    - una llamada de rasgos;
    - si cambiaron los rasgos de una persona, o su madre es de antes de los rasgos, mueve la madre y sus variantes a `_previas_f78a`;
    - genera las madres;
    - genera las variantes por clave, hasta `FLUX_MAX_WORKERS` a la vez, y deja `foto_madre_variantes` en el topic.
- **`script_engine/m06_assembler.py`** (+9 / −2): `foto_madre_personas[nombre]` suma `age_at_event` y `variantes`, solo las que existen en disco. El registry no cambia.
- **`asset_manager.py`** (+50 / −21):
  - `_madres_para_item` mantiene su firma. Para una persona, la ref sigue siendo su nombre y el path es el de su variante (`_variante_de_persona`, que importa foto_madre de forma perezosa); sin variante, la madre limpia. `persona_aporta_madre` no cambió.
  - `_clave_lote(prompts, refs, madre_paths)` suma el md5 del contenido de cada madre.
  - `_pre_paso_secuencia` agrupa por (persona, path elegido) y pasa ese path.
- **Tests:**
  - `test_module_f60_bc.py`: fixture autouse con rasgos y variantes simulados; `PROMPT_DANIEL` con rasgos; `foto_madre_personas ==` con `age_at_event` y `variantes`.
  - `test_module_f78a.py` (19 tests): clave por tramo y edad; desempate; ref = nombre; variante sin archivo → madre limpia; fuera de era; secuencia con 2 variantes de una persona; `_clave_lote` sensible a la madre; texto exacto del /edit; una sola llamada de rasgos con enum; cache; madre de antes de los rasgos va a `_previas`; si los rasgos fallan no se mueve nada; m06.
- **Verificación:** suite amplia 1559 passed, 29 skipped y 3 fallas heredadas (`f51c[paredes de chapa]`, `m03_merge_timing` ×2), en `a/suite.log`. `mapa_modulos --check`: 163 archivos, 0 fallas.

## Tabla de variantes de Colza (Etapa A, real)
`lab/hyperframes/f78a/a/tabla_variantes.md`, calculada con las funciones de producción.

| persona | clave | edad | fotos |
|---|---|---|---|
| Jesús Sancho Rof | — (limpia) | — | 3 |
| Antonio Muro Fernández Cavada | — (limpia) | — | 2 |
| Arcadio Fernandez | 1981-1989 | — | 15 (incluye ch01_img_01, la foto de arranque del clip del gancho) |
| Arcadio Fernandez | — (limpia, año 2000) | — | 1 (ch07_supp_13) |
| Angela Menseger | 1981-1985 | — | 4 |
| Jesús Lozano | 1981-1981 | — (6 = la de la madre) | 3 |
| Carmen Cortés | 1981-1982 | — (14 = la de la madre) | 4 |
| Carmen Cortés | 1981-1982_15 | 15 | 1 (ch04_img_09) |
| Carmen Cortés | 1992-2000_25 | 25 | 1 (ch07_supp_08) |
| Carmen Cortés | 1992-2000_33 | 33 | 2 (ch07_supp_07 y 09) |
| Mercedes García | 1981-1981 | — | 2 |

Total: 38 fotos con madre de persona, 8 variantes y 6 fotos con madre limpia. Es lo mismo que la simulación del analista, salvo los nombres sin sufijo de edad (adenda).

## rasgos.json (`output/<tid>/foto_madre/rasgos.json`, Opus 5.5, 1 llamada, US$ 0,0249)
| persona | rasgos |
|---|---|
| Jesús Sancho Rof | Broad oval face with light olive skin and brown eyes, dark hair neatly combed back and greying at the temples, clean-shaven, thick dark-rimmed glasses, stocky build |
| Antonio Muro Fernández Cavada | Long narrow face with fair skin and brown eyes, dark hair receding at the forehead and cut short, full dark moustache, no glasses, lean wiry build |
| Arcadio Fernandez | Round full face with light olive skin and brown eyes, thick short curly black hair, short full black beard, no glasses, heavyset broad-shouldered build |
| Angela Menseger | Soft heart-shaped face with fair skin and brown eyes, shoulder-length wavy dark brown hair parted to the side, no glasses, medium sturdy build |
| Jesús Lozano | Small round face with light olive skin and brown eyes, short straight black hair with a blunt fringe across the forehead, slight skinny build |
| Carmen Cortés | Oval face with fair skin and large brown eyes, long dark brown hair tied back in a single braid, slender build |
| Mercedes García | Angular face with high cheekbones, light olive skin and brown eyes, long straight black hair worn loose past the shoulders, thin wire-rimmed glasses, slim build |

Los 3 hombres que antes compartían cara ahora se distinguen: Sancho Rof lleva lentes gruesos, Muro tiene bigote y Arcadio barba. Los rasgos no traen edad ni ropa.

## Etapa B: qué salió (mirado en las hojas de contacto)
- **Madres:** las 7 se distinguen entre sí, y los rasgos se ven en todas (lentes, bigote, barba, trenza, flequillo).
  - Mercedes salió con un marco oscuro alrededor, como una foto dentro de la foto.
- **Variantes:** 5 por Nano Banana 2 Lite y 3 por el respaldo Seedream 4.5 /edit (`carmen@1981-1982`, `carmen@1981-1982_15` y `lozano@1981-1981`). En las tres, Nano Banana devolvió `content_policy_violation` (model_moderated): son menores con estado de enfermedad.
  - Arcadio, Angela y Mercedes tienen las manos a la vista. Las de Arcadio se ven algo rígidas, pero la deformación es leve.
  - La de Lozano (respaldo) trae la ESCENA del estado: la sala de vidrio con niños llorando detrás. La `condition` del canon describe un lugar, no el cuerpo, y el modelo la dibujó igual a pesar de «show only what would be visible on the body».
  - `carmen@1992-2000_33` no se ve de 33 años: sigue joven.
- **6 fotos de control:** mismo prompt y madre nueva. Las referencias se verificaron por md5: la llamada coincide con la madre o variante de `_madres_para_item`.
  - `ch01_supp_05` y `ch06_img_14` usan `arcadio@1981-1989`: Arcadio sale con barba en las dos, la misma cara. En la de la calculadora los dedos se ven tiesos.
  - `ch03_img_11` usa la madre limpia de Sancho Rof: aparece con lentes.
  - `ch03_img_14` usa la madre limpia de Muro: aparece con bigote.
  - `ch05_img_12` usa `angela@1981-1985`.
  - `ch07_supp_07` usa `carmen@1992-2000_33`. Carmen sale con pelo corto y cara aniñada, casi de varón joven. El prompt de la escena dice «dark short practical hair» y le gana a la trenza de la madre.

## Costo real de la Etapa B (cost_tracker del tid, `b/costo_etapa_b.json`)
| servicio | llamadas | US$ |
|---|---|---|
| Anthropic Opus 5.5 (rasgos) | 1 | 0,0249 |
| Seedream 4.5 t2i (7 madres) | 7 | 0,2800 |
| Nano Banana 2 Lite /edit (5 variantes + 6 fotos) | 11 | 0,4620 |
| Seedream 4.5 /edit (3 variantes de respaldo) | 3 | 0,1200 |
| **total** | 22 | **0,8869** |

## Declarado (decidí y sigo)
- La edad no lleva sufijo cuando es la de la madre (Carmen@1981-1982, Lozano@1981-1981); 60+ = «elderly». Aceptado en la adenda.
- La clave de un tramo de un solo año queda «1981-1981»: se usa el formato AAAA-AAAA del handoff tal cual.
- Si un tramo se empata en largo con otro, gana el primero del canon.
- Plantilla «Now a <descriptor> person.» tal cual: con «early-30s» queda «Now a early-30s person» (no se cambió el artículo).
- La entrada de rasgos lleva {name, role, era, appearance_canon, grupo_appearance}: el sexo y la edad van dentro de `appearance_canon`, como dice el handoff. El prompt va tal cual, seguido del JSON.
- Si falla la llamada de rasgos, no se mueve ni se genera nada (las madres viejas quedan) y se avisa. Si a una persona no le llegan rasgos, se queda sin madre nueva.
- Una madre adoptada a mano también se mueve a `_previas` si cambian sus rasgos.
- `persona_aporta_madre` no cambió.
- `process_script` reescribió `assets_manifest.json`. La copia del anterior, `data/scripts/<tid>.json` y `documented_people` de antes están en `lab/hyperframes/f78a/b/antes/`.
- **Una llamada real a fal durante los tests de la Etapa A.** El subagente corrió `test_module_f60_bc.py` antes de que yo mockeara el /edit de las variantes. Salió un pedido real a Nano Banana 2 Lite (`daniel_cija@1962-1963`) que volvió 422. Se arregló con la fixture autouse; las corridas siguientes no salen a la red.

## Abierto
- **Etapa C sin correr** (OK de Omar). Regenera todas las /edit cuyo path de madre cambió, y también los clips del gancho y de ch07, porque `ch01_img_01` (Arcadio) cambia de cara.
- **Lozano@1981-1981:** el estado del canon describe una escena («hospitalized in a glass-walled room with ten other children…») y la variante la dibujó detrás del niño. Esa variante va como referencia en 3 fotos. Opciones para el analista:
  - no generar variante cuando la condición es de lugar;
  - pasar solo la parte corporal de la condición;
  - aceptar que el /edit de cada foto pone su propia escena.
- **Carmen adulta (ch07_supp_07):** la edad no se lee y el prompt de la escena («short practical hair») pisa la trenza de la madre. Es el punto del handoff «el texto de cada /edit sigue describiendo pelo/piel del grupo; si choca con los rasgos se ve en B». Se vio: choca.
- **Nano Banana modera** las variantes de menores con enfermedad; las 3 salieron por el respaldo Seedream. En la Etapa C, las /edit de Carmen niña y de Lozano pueden caer igual al respaldo.
- La madre nueva de Mercedes trae un marco oscuro (foto dentro de foto).
- `lab/hyperframes/f60/etapa_bc_prueba.py:90` llama a `am._clave_lote(prompts, refs)` con la firma vieja: es un script de lab fuera de los 3 módulos y daría TypeError si se corre.
- Lo que ya estaba abierto en el handoff: con variantes, la regla «sin madre si el estado cae fuera de la era» podría pasar a «variante». Decisión de Omar.

## Veredicto del revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

No ejecuté nada que llame a APIs. Revisé el contrato, el commit, los logs y los artefactos en disco. No volví a correr la suite.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Handoff con md5 56cb5d35… y adenda 19:36 como regla | OK | `md5sum` coincide; el commit usa `foto_madre_personas[n]["variantes"]` y `age_at_event` |
| 2 | Etapa A: código solo en foto_madre.py, m06_assembler.py y asset_manager.py | OK | `git show --stat 7d9fe85` |
| 3 | Etapa A: tests (`test_module_f60_bc.py` actualizado, `test_module_f78a.py` nuevo) y suite rápida | PARCIAL | Existen (+27 y 327 líneas). `a/suite.log`: 1559 passed, 3 failed. Las 3 fallas se atribuyen a la rama, pero no pude comprobar que ya fallaban antes. |
| 4 | Etapa A: tabla real de variantes de Colza sin generar imágenes | OK | `a/tabla_variantes.md`: 38 fotos, 8 variantes, 3 grupos con madre limpia. Coincide con el handoff. |
| 5 | Etapa A: commit | OK | `7d9fe85`, con atribución |
| 6 | B: 7 madres viejas movidas a `_previas_f78a/`, sin borrar | OK | 7 png y 7 `.prompt.txt` en `foto_madre/_previas_f78a/`; `etapa_b.log` líneas 3-9 |
| 7 | B: 7 madres nuevas, 8 variantes y `rasgos.json` | OK | Los archivos están en disco; `etapa_b.log` líneas 14-34 |
| 8 | B: 6 fotos de control, con sus 3 archivos más `.llamada.json` movidos | OK | `assets/ch0X_flux/_previas_f78a/` tiene 4 archivos por foto; el log dice «a regenerar» exactamente esas 6 |
| 9 | B: nada más regenerado, sin Opus de m03 ni fase1_5 | OK | Solo esas 6 fotos y `assets_manifest.json` tienen mtime nuevo; el log marca todo lo demás como «skip»; no hay clips, voz ni render nuevos |
| 10 | B: hoja `ETAPA_B.html` | OK | Existe, 1,8 MB, con imágenes embebidas |
| 11 | PARADA tras B, sin Etapa C | OK | `etapa_b.log` termina en EXIT 0; no hay `_previas` de las otras /edit ni de `fondos.json` |
| 12 | Reporte con diff por módulo, tabla, rasgos.json, costo real y «abierto» | PARCIAL | Todo está en `F78a_REPORT.md`. La sección del veredicto dice «(pegado abajo)» y sigue vacía. |
| 13 | Costo real de B | OK | `costo_etapa_b.json` suma 0,886876, igual al log y al reporte (US$ 0,8869). Hay una sola llamada de rasgos. |
| 14 | Sin números ni listas nuevas fuera de la tabla del handoff | OK | Las constantes citadas son las del handoff. El reporte declara sus decisiones (clave «1981-1981», «a early-30s», desempate por orden del canon). |
| 15 | `ESTADO_SESION.md` pendiente hasta después del veredicto | OK | No figura entre los archivos tocados |

Fuera de alcance:
- Ninguno en el código.
- El commit A también tocó `DECISIONES.md` (las dos entradas F78a), `lab/MAPA_PROYECTO.json` y `.md`, y `lab/mapa/stickers/*.json`. Son documentación y mapa regenerado, no código de los 3 módulos.
- Los archivos de Etapa B (`lab/hyperframes/f78a/b/`, `ETAPA_B.html`, `F78a_REPORT.md`) y los artefactos de `output/` siguen sin commit, como corresponde.

Observaciones:
- **Llamada real a fal en tests:** una llamada real a fal (`daniel_cija@1962-1963`, devolvió 422) salió durante los tests de A, porque un subagente corrió `test_module_f60_bc.py` antes de mockear la variante. Está declarada en el reporte. Costó poco o nada, pero rompe la regla de no llamar a APIs en tests.
- **Script de lab roto:** `lab/hyperframes/f60/etapa_bc_prueba.py:90` usa la firma vieja de `_clave_lote` y daría TypeError. Está declarado y queda sin arreglar.
- **Archivos sobrantes:** en `foto_madre/` quedan tres `*.prompt - Copy.txt` (de 18:56, anteriores a F78a). No son de este trabajo.
- **Defectos de Etapa B a decidir con Omar (el reporte los admite):** la variante de Lozano trae la escena del hospital; la Carmen de 33 años no se lee adulta; la Carmen de ch07_supp_07 pierde la trenza por el «short practical hair» del prompt; la madre de Mercedes trae un marco oscuro; 3 variantes de menores cayeron al respaldo Seedream por moderación de Nano Banana.

Riesgos que el contrato no cubre:
- En la Etapa C, las /edit de menores con enfermedad seguirán cayendo a Seedream. Es un cambio silencioso de motor y de estilo.
- Las variantes que describen una escena en vez del cuerpo (Lozano, que va como referencia en 3 fotos) contaminan las fotos que las usan.
- Las fotos de arranque de clip (`ch01_img_01`, `ch07_img_01`) cambian la cara del clip. Eso obliga a rehacer clips con Kling en C.

### Adenda de CC
- **Punto 3 (fallas heredadas):** son las mismas 3 que F77 ya declaraba como heredadas: `f51c[paredes de chapa]` y `m03_merge_timing` ×2 (`lab/hyperframes/f77/F77_REPORT.md`). Ninguna toca foto_madre, m06 ni asset_manager.
- **Punto 12:** este bloque es el veredicto; queda pegado tal cual.
- **Llamada a fal en tests:** el pedido salió una sola vez y volvió 422 (sin imagen ni cobro de imagen). Ahora la fixture autouse de `test_module_f60_bc.py` simula rasgos y variantes; las corridas siguientes (100 + 1559 tests) no salieron a la red.
- **Los `* - Copy.txt`:** no son míos; los dejé donde estaban.
- **ESTADO_SESION.md:** actualizado después de este veredicto, en el mismo commit que la Etapa B.
