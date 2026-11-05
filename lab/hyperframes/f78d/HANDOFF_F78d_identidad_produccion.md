# HANDOFF F78d — terminar la identidad de las personas (texto con rasgos) en producción + Etapa C de F78a en Colza

Rama `f11-guion-v4`, base `af72da1` (F78c B). Topic Colza `c4934b7d-3f54-448f-ba5f-539dc744f0d8`.
Omar aprobó 2026-11-05 08:57 ET («so dale»). Anotar en DECISIONES.md con esa fecha, incluido lo que NO entra (abajo).
Usá tantos subagentes en paralelo como permita el trabajo.

## Por qué (lo que ve el espectador)
La misma persona sale con otra cara entre fotos (Arcadio canoso sin barba en unas, barbudo en otras). F78c midió la causa y el
arreglo: con los rasgos de la madre en el texto, la escena coincide con la referencia. Esta tanda TERMINA ese arreglo; no agrega reglas.

## Lo que NO entra (decisión de Omar, va a DECISIONES como «se queda» / «se arregla si se repite»)
- Manos deformes en la escena: límite del modelo de imagen, en plano medio no se ven, la voz lo dice → se queda. Sin close-up.
- Nombre real colado en la prosa (ch06_img_14 «Arcadio»): se arregla si se repite.
- Nano Banana 2 completo: no mejora en el lab, cuesta el doble → Lite se queda.

## Constantes
Ninguna nueva. Motor Lite (`engine_profiles.py`, F68). `MADRE_PERSONA_MIN_FOTOS`=2 existente. Sin tope de dólares (regla 2026-10-29): costo reportado después.

## Módulos que toca (3)
1. `script_engine/m03_visual.py`
   - l.166 (`DOCTRINE_PEOPLE`): «from a documented person's appearance_canon when it is one» → «from a documented person's
     appearance (or appearance_canon if there is none) when it is one». Es el resto del mismo cambio de F78c, no una regla nueva.
     Pegá antes/después completo de la línea.
   - `_f8_refill` recibe `personas_fijas: list[str] | None = None`. Si viene: el bloque PERSONAS DOCUMENTADAS de ESA llamada
     lleva SOLO esas personas (copia del topic con `documented_people` filtrado; dato, no instrucción). Al volver, si el
     casillero `persona` nuevo ≠ `personas_fijas` → se descarta lo nuevo, queda el ítem viejo con la marca
     `_rasgos_refill: "persona_distinta"`. Sin reintentos.
   - Cada ítem guarda `aspecto_fuente`: `"rasgos"` si su cap se armó con rasgos vigentes para TODAS sus `persona`, si no `"canon"`.
     (Ítems sin persona: no llevan la clave.)
2. `fase1_5.py` + función nueva en m03 (p. ej. `rehacer_aspecto_personas(topic, video_id)`)
   - Paso nuevo DESPUÉS de foto madre y ANTES de assemble: para cada ítem con `persona` no vacía, `aspecto_fuente != "rasgos"`
     y rasgos vigentes para todas sus personas → `_f8_refill(..., note="", personas_fijas=persona)`. En paralelo.
     Idempotente: correrlo dos veces no llama a nadie la segunda.
   - Ítems editados a mano en QA Studio (buscá la marca que deja el editor de foto F59; declarala): NO se tocan, se listan.
   - Nuevo `--only aspecto` (corre el paso + assemble y corta), para Colza.
3. Tests sin red: filtro de personas, persona distinta → queda lo viejo, idempotencia, salto de ítems de QA, `aspecto_fuente`.
   Tests viejos que cambien: actualizarlos, no borrarlos.

## Etapa A — código + tests. Commit.
Salida en texto: diff de l.166 y la lista de ítems de Colza que el paso tocaría (cap, id, persona, `aspecto_fuente`, si está editado en QA) — sin llamar.

## Etapa B — Colza: textos
`fase1_5.py --topic <tid> --only aspecto`. Salida: tabla por foto → persona → subject viejo → subject nuevo → marca.
Cuántas quedaron `persona_distinta` y cuáles de QA se saltaron. md5 de los archivos del papel/narración aprobados antes y después
(no deben cambiar; si assemble los cambia, PARADA y explicá).

## Etapa C — Colza: fotos y clips (la Etapa C de F78a)
Regenerar con Lite las /edit cuyo prompt cambió en B o cuya madre/variante cambió en F78a/F78b, más los clips del gancho y de ch07
(F78a_REPORT l.127). Lo viejo a `_previas_f78d` (no se borra). Hoja `lab/hyperframes/f78d/ETAPA_C.html`: por foto, referencia |
vieja | nueva + subject nuevo. Costo real por servicio.

## Chascada
Los 3 tests que fallan en `lab/hyperframes/f78c/a/suite.log` (f51c, m03_merge_timing ×2): correlos en `a6ff9a9` y decí si ya
fallaban. Solo reportar; no arreglar en esta tanda.

## Reglas fijas
Sin hardcode; sin reglas nuevas en prompts (solo l.166 arriba). Lo viejo se reemplaza, no se apaga con flags. Veredicto íntegro del
`revisor-handoff` en el reporte `lab/hyperframes/f78d/F78d_REPORT.md`; ESTADO_SESION después del veredicto.

## PARADA
Al terminar la Etapa C. Omar revisa las fotos en QA Studio. No render, no subir nada.

## ADENDA 1 (2026-11-05 09:15, respuesta a la PARADA de CC) — manda sobre el cuerpo
1. «Editado a mano en QA» = opción (a): la foto tiene copia en `output/<tid>/assets/_qa_backups/`. Se lee del disco y `qa_studio_server` no se toca. Si una foto se salta por reseed o por el editor de clip sin edición de texto, no pasa nada: se lista en el reporte y se queda con su texto. En un topic nuevo el paso corre antes de que exista cualquier foto, así que ahí nunca hay saltos.
2. Las notas no se pierden: si el ítem tiene una indicación previa de m03 (`_f8_rehecha` o su equivalente), el refill la vuelve a pasar como `note`. `note=""` solo cuando no había ninguna. En el reporte, la lista de las 3 de Colza con su nota.
3. Movimiento del clip: si se rehace la foto de arranque de un clip, se regenera también su texto de movimiento con la misma función de m03 (en Colza, el gancho y ch07 si aplica). El texto viejo y el nuevo van en el reporte.
