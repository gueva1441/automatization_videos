# HANDOFF F78a — madres de persona: identidad propia + variante por tramo (estado / edad)
Rama `f11-guion-v4`, base `351a3a7`. Analista, 2026-11-04. Aprobado por Omar 19:08 («dale»). Auditado por subagente (14 correcciones aplicadas).

## Por qué (lo que ve el espectador)
Colza: 1) Arcadio (víctima), Sancho Rof (ministro) y Muro (médico) salen con la MISMA cara; 2) la voz dice «un hombre con las
manos deformadas» (gancho) y «dedos que no se cierran» (ch06) y la foto muestra manos sanas; 3) Carmen Cortés sale con 14 años
en 1992 y 2000 (tenía 25 y 33). Las tres frenan.

## Causa raíz (medida en disco)
1. Identidad: `_prompt_persona` (foto_madre.py l.303) arma la madre con `appearance_canon` + appearance del grupo. El canon
   (step_4e_visual_canon.py l.256-262) prohíbe rasgos específicos a propósito (es dato verificable: se queda así). Resultado:
   10 de 15 personas del canon de Colza = «a middle-aged Spanish man» → mismo prompt → misma cara.
2. Estado: la madre es limpia (F60 0b, DECISIONES 2026-10-30 17:48) y el estado viaja como texto; en /edit la referencia le gana
   al texto (40 /edit sin manos deformadas; las t2i sí muestran cicatrices, Omar 19:07). La madre es de cabeza y hombros: las
   manos no existen en la referencia. `persona_aporta_madre` (asset_manager l.1054) solo quita la madre si el estado cae FUERA de la era.
3. Edad: la madre tiene la edad de `age_at_event` para toda la era (estaba en «se arregla si se repite», F60; se repitió).

## Constantes (ninguna inventada)
| valor | origen | quién |
|---|---|---|
| llamada de rasgos: `claude_helpers.call_json(model=MODELO_CASILLEROS, effort=guion_v4.ESFUERZO[MODELO_CASILLEROS])` + registro en cost_tracker, como m03_visual.py l.320 | existente | Omar 2026-10-28 |
| madre limpia = Seedream 4.5 t2i del perfil (`_generate_madre_seedream`) | existente | Omar F60/F68 |
| variante = /edit de producción `_generar_nb2` con `frase_de_madres=False`; su respaldo Seedream (asset_manager l.512) vale igual | existente F68 | Omar |
| `MADRE_PERSONA_MIN_FOTOS` = 2 | existente | analista F60 |
| edad en el año Y = `age_at_event` + (Y − primer año de `era`); solo si `age_at_event` es número | derivado | — |
| descriptor ≥ 20: tabla de step_4e l.270-283 (early/mid/late-20s…) copiada a una constante `DESCRIPTOR_EDAD` en foto_madre.py citando ese origen | existente (hoy solo texto de prompt) | — |
| descriptor < 20: palabra exacta «fifteen-year-old»: lista literal 1-19 `EDAD_EN_PALABRAS` en foto_madre.py | analista F78a (no hay num2words en el repo) | analista |
| año del estilo de la variante = primer año del tramo de estado; sin tramo, el año de la edad | derivado | analista |
| workers = `FLUX_MAX_WORKERS` | existente | — |

## Módulos que toca (3)
1. `foto_madre.py` — hoy: madre limpia por persona con canon+grupo. Después: (a) UNA llamada con todas las personas con madre →
   `rasgos` por persona, que entran en `_prompt_persona`; (b) genera las VARIANTES por clave (edit de la madre limpia).
2. `script_engine/m06_assembler.py` — hoy: registry {nombre → madre}. Después: las variantes van en un dict APARTE
   `foto_madre_variantes` {nombre: [{clave, tramo, edad, path}]} (no en `foto_madre_registry`: `_nombres_en_prompt`, l.1089,
   tomaría las claves como nombres).
3. `asset_manager.py` — `_madres_para_item` (regla única) devuelve `(nombre, path)` con la ref = el NOMBRE de siempre y el path de
   la variante cuya clave corresponde al año de la foto (tramo que lo contiene + edad de ese año); sin variante → madre limpia.
   Desempate entre tramos que se pisan: el más corto. Así manifest (`foto_madre_refs`), report_foto_madre_edits, QA Studio y m09
   no cambian. `persona_aporta_madre` NO cambia (Omar 2026-10-30 20:29). Secuencia (`_pre_paso_secuencia`, l.1331/1349; hoy
   apagada con nb2_lite, engine_profiles l.115): agrupar por (persona, path elegido), pasar ese path, y meter el md5 de la madre en
   `_clave_lote` (l.1213) para que `pedidos.json` no reanude un pedido viejo.
Tests: `test_module_f60_bc.py` l.361-369 (`registry ==` exacto) se actualiza; nuevo `test_module_f78a.py` (clave por tramo+edad,
desempate, ref = nombre, secuencia con 2 variantes de una persona).

## (a) Llamada de rasgos — prompt completo (va tal cual)
Entrada: JSON lista de las personas que van a tener madre: {name, role, sexo/edad tal como dice appearance_canon, era,
appearance_canon, grupo_appearance}. Salida con schema: lista de {name (enum = los name de entrada), rasgos (string)}, una por persona.
```
Estas son personas reales de un documental. No tenemos fotos de ellas: el retrato de referencia de cada una se genera con IA, y
el espectador tiene que poder reconocer en cada foto quién es quién. Tu trabajo es darle a cada persona un aspecto propio.

Para cada persona escribí UNA frase en inglés con: forma de la cara, pelo (corte, color, canas), vello facial, si usa lentes y
contextura. A los niños no les pongas vello facial ni lentes.

Tiene que respetar, sin contradecirlos, su appearance_canon, el aspecto de su grupo y su sexo.
No pongas edad, ropa, heridas, enfermedad, expresión, oficio ni el nombre: eso lo ponen otras partes.
Dos personas del mismo sexo y de edad parecida no pueden compartir la misma combinación de pelo, vello facial y lentes.
```
Revisión del analista (a mano, 7 con madre de Colza): los 3 hombres → p. ej. «long oval face, receding grey hair combed back,
thick grey moustache, no glasses, thin build» / «round face, dark side-parted hair, clean-shaven, thick-framed glasses, heavy
build» / «square jaw, short curly black hair, full dark beard, no glasses, medium build». Sin edad: no choca con la variante por
edad (Carmen). Simulación real = Etapa B (barata, con PARADA).
Cache: `output/<vid>/foto_madre/rasgos.json` con md5 de la entrada. Si el md5 de los rasgos de una persona cambió, su madre vieja
(y sus variantes) se mueven a `foto_madre/_previas_f78a/` y se regeneran (hoy el skip por PNG existente, l.383-393, lo impediría).
Prompt de la madre: `Head-and-shoulders portrait of {canon}, {rasgos}, {ROPA_MADRE}. {grupo} Neutral expression, …` (resto igual).

## (b) Variantes
Para cada persona con madre y cada foto suya donde aporta: clave = tramo de `condition_by_period` que contiene el año (o ninguno)
+ edad de ese año si `age_at_event` es número y su descriptor difiere del de la madre. Clave vacía → madre limpia.
Destino `output/<vid>/foto_madre/<slug>@<AAAA-AAAA o sin_estado>[_<edad>].png` (+ `.prompt.txt`). Texto del /edit (completo):
```
The same person as in the reference image: same face, same features, same identity. {si hay edad: "Now a <descriptor> person."} {condition, si hay}. Show only what of this would be visible on the body; if nothing is visible, keep the person unchanged. Waist-up portrait framed so that the face and both hands are visible, {ROPA_MADRE}, plain mid-grey background, soft even light. {ESTILO_C con el año de la tabla} {NO_TEXT}
```
Cintura para arriba: el estado de Colza está en manos/torso; la madre limpia (cara) queda igual.

## Simulación contra Colza (analista + auditor, 03_visual.json + 05_visual_canon.json)
38 fotos /edit con persona de madre: 32 en tramo con estado → variante; 6 limpias (Sancho Rof ×3, Muro ×2, Arcadio ch07_supp_13 año 2000).
8 variantes: Arcadio@1981-1989 (15 fotos) · Mercedes@1981 (2) · Lozano@1981 (3) · Angela@1981-1985 (4) · Carmen@1981-1982_14 (4) ·
Carmen@1981-1982_15 (1, ch04_img_09) · Carmen@1992-2000_25 (1, ch07_supp_08) · Carmen@1992-2000_33 (2, ch07_supp_07/09).
Ninguna foto suma madre por nombre (F71b) ni tiene 2 madres. Estados no visibles (Carmen 1992-2000 «unable to work…») → «if
nothing is visible, keep the person unchanged». CC imprime la tabla real en la Etapa A.

## Etapas
A) Código (3 módulos) + tests + suite rápida. Salida en texto: tabla de variantes de Colza (persona/clave/edad/fotos), sin generar nada.
B) Colza, imágenes de prueba (camino de producción, SIN Opus y SIN `fase1_5 --from m03`, que rehace m03 con Opus, fase1_5 l.918):
   1. mover las 7 madres actuales a `foto_madre/_previas_f78a/`;
   2. `foto_madre.generate_fotos_madre_personas(topic de topics_db, tid)` + `save_db` → rasgos.json, 7 madres, 8 variantes;
   3. `m06_assembler.assemble_final_script(tid)`;
   4. regenerar SOLO 6 fotos de control con fase2a/asset_manager (su prompt actual): ch01_supp_05 (Arcadio, juicio 1989),
      ch06_img_14 (calculadora), ch03_img_11 (Sancho Rof), ch03_img_14 (Muro), ch05_img_12 (Angela), ch07_supp_07 (Carmen 2000).
      Para cada una mover a `_previas_f78a/` `<stem>.png`, `<stem>_native.png` y `<stem>_graded.png` (si queda el graded,
      image_grade l.68 lo reusa).
   5. Hoja de contacto `lab/hyperframes/f78a/ETAPA_B.html`: madres viejas vs nuevas, rasgos, variantes, 6 fotos antes/después con su prompt.
   **PARADA: Omar mira.**
C) Solo con OK de Omar: regenerar todas las /edit cuyo path de madre cambió (mismos 3 archivos por foto a `_previas_f78a/`).
   Las fotos de arranque de clip (ch01_img_01 gancho, ch07_img_01) cambian la cara del CLIP: se rehacen foto + `_final` + clip con
   el camino de producción (Opus escribe el final, Kling/Omni genera; Omar ya dijo que el costo no importa). Mover
   `_fase2b_work/fondos.json` a `_previas_f78a/` (el papel_md5 no cambia y `etapa_de` no vería los fondos desfasados; así fase2b
   archiva sus caches por nombre de foto, fase2b l.3318-3326). Salida: lista de fotos/clips regenerados y costo. Después Omar en QA Studio.

## Lo viejo se borra
`_prompt_persona` cambia en el mismo lugar; no queda camino viejo.

## Abierto (no entra)
- Con variantes, «sin madre si el estado cae fuera de la era» (Omar 2026-10-30 20:29) podría pasar a «variante» (misma cara). Decisión de Omar.
- El texto de cada /edit sigue describiendo pelo/piel del grupo; si choca con los rasgos se ve en B.

## ADENDA 2026-11-04 19:36 (respuesta a la PARADA de CC, Etapa A)
- Opción (a): las variantes van en `foto_madre_personas[nombre]["variantes"]` (+ `age_at_event`), NO en un dict aparte: fase2a
  `_normalize_long` (fase2a.py:159-160), QA Studio (qa_studio_server.py:1008-1010) y m09 ya pasan `foto_madre_personas` a
  `_madres_para_item`; quedan los 3 módulos. Error del analista (y del auditor): el dict aparte no llegaba a esos consumidores.
- Aceptado: claves sin sufijo de edad cuando la edad es la de la madre (Carmen@1981-1982, Lozano@1981); 60+ = «elderly»
  (una de las dos opciones de step_4e l.284); mover también `.llamada.json` de cada foto a `_previas_f78a/`.
