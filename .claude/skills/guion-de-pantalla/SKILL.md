---
name: guion-de-pantalla
description: Generar, leer, editar y aprobar el guion de pantalla de un topic (fase2b --plan-only / --plan-edit / --aprobar-guion) antes de cualquier render. Usar cuando una tanda toca lo que se ve en pantalla, cuando hay que mostrarle a Omar o al analista qué va a salir, o antes de pedir un render.
---
# Guion de pantalla (F32/F33)

**Regla (DECISIONES 2026-10-26 11:13): texto antes que render, siempre.** Nada se renderiza con `--gfx` sin el guion
revisado y aprobado por Omar; el hook `guard_render` lo frena.

## 1. Generarlo
```bash
PYTHONIOENCODING=utf-8 python fase2b.py <topic> --plan-only
```
- Implica `--gfx --reuse-visuals`: los visuales base (`chNN_flux_visual.mp4` / `chNN_hybrid_visual.mp4`) tienen que
  estar cocidos (no cuece DepthFlow). Sin navegador, sin HyperFrames, sin render.
- Corre el papel (F37: sin borrador del director; `--rotulista` ya no existe), reglas, reparto y crítico (el crítico mira la foto sola, en cada intento), -g30 de los caps en paralelo y el plan en
  fila. Vajont: ~2.7 min con el rotulista en caché; ~5 min si el rotulista llama a Claude.
- Escribe `output/<topic>/GUION_PANTALLA.md` y `.json` (la misma información) y
  `output/<topic>/_fase2b_work/mezcla_preview.wav` (voz + música + sfx, con el grafo del render: para **oír** costuras y
  silencios). Regenerar reescribe el guion **sin** aprobación.

## 2. Qué trae
- **Una línea por evento**, en el segundo del mp4 final (intro de 2.5 s y pre-roll ya sumados):
  `mm:ss · chNN · beat n (función) · tipo · «etiqueta | texto» · dura X s (lectura mínima Y s) · escena k (de a) · voz −1 / ancla / +1 · aporta · fuente · filtro`.
  Tipos: costura, title card, ficha, persona, recorte, cita, lupa, sello, reloj, nivel de agua, contador, punch,
  pregunta de cierre, transición, silencio de voz. **`✂`** = propuesto y cortado: «cortó *quién* (*regla*): *motivo*»
  (rotulista por regla, zona, catálogo de sellos, realizador, crítico, candado).
- **Tabla por beat** al final de cada cap: función · ventana (s del cap) · escenas · propuestos (director · rotulista)
  · cortados por regla (con el motivo de cada uno) · quedan. `⚠ BEAT VACÍO` = nada en el beat; `⚠ CAP SIN TEXTO` en la
  cabecera del cap.
  Cómo leerla: si «propuestos · rotulista» es alto y «quedan» es 0, el material estaba y lo mató una regla (mirar qué
  regla en «cortados»); si «propuestos» es 0, el problema está antes (escaleta, pool, el modelo).
- **Chequeos** (✓/✗ con el dato): dos bloques en una escena, bloque que cruza un corte, texto sin lectura (15 cps),
  pregunta sin lectura, cifra que contradice la voz, `a_pantalla` (cuántos salen y por qué falta cada uno), costuras
  (negro hasta el corte, voz callada), inicio de voz por cap (a tiempo ±1 cuadro y con rampa).

## 3. Editarlo sin volver a llamar al modelo (`--plan-edit`)
```bash
PYTHONIOENCODING=utf-8 python fase2b.py <topic> --plan-edit ediciones.json
```
Las ediciones se suman a `_fase2b_work/plan_edits.json` (las nuevas, después: ganan) y se regenera el guion; el rotulista
sale de caché y el crítico solo mira lo editado (caché por identidad del bloque). Cada edición va por `cap` + `pool_id`
sobre la respuesta del rotulista (después pasa **todas** las reglas: candado, lectura, zona, crítico) o, con `escena`,
sobre el plan colocado. Campos: `texto`, `etiqueta`, `word_idx`, `sentence_idx`, `tipo`, `aporta`, `borrar`, `agregar`,
`escena`. Ejemplos reales de Vajont (`f8s3-vajont-f30`, guion de F32):
```json
{"ediciones": [
  {"cap": "ch02", "pool_id": "D117", "etiqueta": "Consejo Superior de Obras Públicas"},
  {"cap": "ch05", "pool_id": "Q50", "texto": "Las poblaciones de Erto y Casso viven en continua aprensión y alarma."},
  {"cap": "ch06", "pool_id": "D192", "texto": "20 técnicos perecieron en el centro de control."},
  {"cap": "ch06", "pool_id": "D128", "escena": 13},
  {"cap": "ch07", "pool_id": "T85", "borrar": true},
  {"cap": "ch03", "agregar": {"pool_id": "T21", "sentence_idx": 1, "word_idx": 5, "tipo": "cifra",
                              "etiqueta": "Deslizamiento de Pontesei", "texto": "3 millones de m³ de roca",
                              "aporta": "el volumen de roca que cayó, que la voz no dice"}}
]}
```
(D117 cayó por candado por el «1943» de su etiqueta; Q50 y D192, por lectura; T85 es una propuesta de ch07; el
`agregar` usa el dato T21 del pool —«3 millones de m³ de roca» en Pontesei— anclado en la palabra «roca» de la oración
[1] de ch03 («Ese marzo, una masa de roca entró al agua…»). Toda edición vuelve a pasar el candado: si un número o un
nombre no está en el texto fuente del dato, sale.)

## 4. Aprobarlo
Solo cuando el prompt de Omar dice literalmente **«aprobado»**:
```bash
PYTHONIOENCODING=utf-8 python fase2b.py <topic> --aprobar-guion "Omar 2026-10-27"
```
Escribe `aprobado: {por, fecha, md5_planes, planes}` en `GUION_PANTALLA.json` (md5 conjunto de los
`gfx_plan_chNN.resolved.json`). Falla si algún plan es más nuevo que el guion. Cualquier `--plan-edit` o `--plan-only`
posterior la invalida (el guion se reescribe sin `aprobado`, y si los planes cambian el md5 ya no coincide).

## 5. El render
`guard_render` deja pasar `fase2b <topic> … --gfx` solo con la aprobación vigente. **Regla: el render usa los planes
aprobados y no re-decide** (el crítico del rotulista reusa su veredicto por identidad del bloque). Ojo, abierto desde
F32: hoy el render vuelve a correr `apply_gfx` y el crítico de los **sellos** mira el bloque dibujado (snapshot), así que
puede cambiar un veredicto; el lock de planes (`gfx_plan_override` con los planes aprobados) está pendiente para la tanda
de correcciones. Hasta entonces, comparar el plan del render con el aprobado (`md5_planes`) después de renderizar.
