# F22e_REPORT — Fable 5.1 por defecto en el guion v4 · una oración nueva en la escaleta v2.1

2026-10-24 · rama `f11-guion-v4` sobre `f56c018` · **cero corridas, US$ 0.00** · sin merge · **PARADA**.

## 1. Fable 5.1 por defecto en el guion v4
- `guion_v4.DEFAULT_MODELO_GUION = "claude-fable-5-1"` (antes, F22d: `claude-opus-5-5`). Lo usan `guion_v4.write` y `reparar` sin `call`, y `fase1_5.run_guion_v4` sin `--modelo`. Esfuerzo `high` (`ESFUERZO["claude-fable-5-1"]`) y `max_tokens` 32,000 (`claude_helpers.MAX_TOKENS`). Precio en PRICES desde F22d: US$ 10 / 50 por millón.
- **Opus 5.5 y Sol siguen disponibles** con `--modelo claude-opus-5-5` / `--modelo gpt-6.1-sol` (test). `call_for(None)`, que usan la escaleta y la columna, sigue siendo Sol: no cambia.

## 2. Escaleta v2.1: la promesa del gancho
- En `<oficio>` §2, después de «La promesa es una frase que dice qué va a entender el espectador si se queda.», se agregó, en la misma línea y separada por un espacio:
  «Es una imagen o una pregunta, nunca un resumen de lo que va a pasar ni una lista de lo que viene.»
- El mismo texto en `lab/hyperframes/f22/PROMPT_ESCALETA_v2_1.md` (bloque `## SISTEMA`) y en `m01a_escaleta.SYSTEM_V2` (byte-idénticos, test). Nada más cambió: el diff entre la v2.1 de F22 y la de ahora es esa sola línea.
- `PROMPT_VERSION_V2 = "f22-2"` y `PROMPT_VERSION_COLUMNA = "f22-2"` (la escaleta con o sin columna usa el mismo sistema). La v2.1 de F22 queda en código como `SYSTEM_V2_F22_1` (`PROMPT_VERSION_V2_F22 = "f22-1"`), byte-idéntica.

| | md5 |
|---|---|
| bloque `## SISTEMA` del archivo = `SYSTEM_V2` (nuevo, f22-2) | `22cfd68b7cee4734e95bb3ee27bb96b2` |
| `SYSTEM_V2_F22_1` (la v2.1 de F22, f22-1) | `7ea18a6aa1ca91c5ad0dfb7cc9b239a8` |
| archivo `PROMPT_ESCALETA_v2_1.md` entero (nuevo) | `dc08061c557951c0daa21d6e81cfa793` |
| archivo `PROMPT_ESCALETA_v2_1.md` entero (el del handoff de F22) | `601aa76a77ce2c1dd9bd861a3bba6a02` |

Los otros tres sistemas no cambian: ficha `7d3599dc…`, columna `f294cf6b…`, guion v5.2 `743e4f0a…`.

## 3. Tests
- Adaptados a las decisiones: `test_module_f12.py` (el guion sin `call` es Fable; `call_for(None)` sigue en Sol), `test_module_f17.py` (`PROMPT_VERSION_COLUMNA` f22-2), `test_module_f22.py` (md5 nuevo del archivo y del sistema de la escaleta; la v2.1 de F22 con su versión; versión de la escaleta generada) y `test_module_f22d.py` (modelo por defecto del guion = Fable; Opus y Sol con `--modelo`; md5 de los cuatro sistemas).
- Suite amplia (`test_module_f[0-9]*`, `gfx_*`, `01a*`, `01b*`, `m03_*`, fase2b reassemble/hwencode, concat, transition): **806 verdes + las 5 previas** (3 `01b_pauses`, 2 `m03_merge_timing`).

## 4. Archivos
`script_engine/guion_v4.py`, `script_engine/m01a_escaleta.py`, `lab/hyperframes/f22/PROMPT_ESCALETA_v2_1.md`, `fase1_5.py` (un comentario), `test_module_f12.py`, `test_module_f17.py`, `test_module_f22.py`, `test_module_f22d.py`, `lab/ESTADO_SESION.md`, este reporte.

## 5. Veredicto del revisor-handoff (íntegro; su observación 3, el comentario de fase1_5.py, quedó corregida después: dice Fable 5.1)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Fable 5.1 por defecto del guion v4 | OK | `script_engine/guion_v4.py:61` `DEFAULT_MODELO_GUION="claude-fable-5-1"`. Lo usan `write` (l.648), `reparar` (l.940) y `fase1_5.py:281` (`run_guion_v4`) |
| 2 | max_tokens 32000 y effort high | OK | `ESFUERZO["claude-fable-5-1"]="high"`. `claude_helpers.MAX_TOKENS=32000`, importado y leído por mí. El test_f22d lo asserta |
| 3 | Escaleta y columna siguen en Sol | OK | `DEFAULT_MODELO="gpt-6.1-sol"` sin tocar. `call_for(None)` lo usa. test_f12 lo asserta |
| 4 | Opus y Sol accesibles con `--modelo` | OK | `fase1_5.py:687` choices incluye `claude-opus-5-5`, `gpt-6.1-sol` y `claude-fable-5-1`. test_f22d prueba `run_guion_v4` con ambos |
| 5 | Texto agregado literal y en el lugar pedido | OK | `<oficio>` §2, mismo renglón, tras «...si se queda.»: «Es una imagen o una pregunta, nunca un resumen de lo que va a pasar ni una lista de lo que viene.» Una sola aparición en `SYSTEM_V2` |
| 6 | Archivo y SYSTEM_V2 idénticos | OK | Bloque extraído con el ancla del test (`"\n## SISTEMA\n\n"` hasta `"\n\n---\n"`): `== SYSTEM_V2` es True. md5 de ambos `22cfd68b7cee4734e95bb3ee27bb96b2` |
| 7 | No cambia nada más del prompt | OK | `git diff` del .md es de 1 línea (`2 +-`). `SYSTEM_V2` vs `SYSTEM_V2_F22_1`: difiere solo el índice de línea 12 |
| 8 | md5 del reporte | OK | Los cuatro coinciden. Bloque nuevo `22cfd68b…`. F22_1 `7ea18a6a…`. Archivo nuevo `dc08061c557951c0daa21d6e81cfa793` (calculado sobre el archivo en disco, sin CRLF). Archivo viejo `601aa76a…` (`git show HEAD:` da el mismo) |
| 9 | PROMPT_VERSION f22-2 | OK | `m01a_escaleta.py` `PROMPT_VERSION_V2="f22-2"`. Además se subió `PROMPT_VERSION_COLUMNA` a "f22-2" (ver obs. 1) |
| 10 | Tests | OK | Corrí f12/f17/f22/f22d/f22b: 102 passed. No reproduje la suite amplia de 806 que cita el reporte (NO VERIFICABLE) |
| 11 | Cero corridas | OK | No hay artefactos de corrida; `lab/hyperframes/f22e/` solo tiene `F22e_REPORT.md`. El reporte declara US$ 0.00. No pude auditar el gasto de API por fuera del repo |
| 12 | Commit y PARADA | PARCIAL | Todo está sin commitear (HEAD sigue en f56c018), como indica el contexto. Un reporte de F22e falta en el árbol de commit: está sin trackear. §5 del reporte dice `REVISOR_PENDIENTE` hasta que se pegue este veredicto |

Fuera de alcance: ninguno de F22e. `diag_234_cap4.py` y `gfx_profiles/*` aparecen modificados, pero el pedido ya los marcó como ajenos. No los toqué.

Observaciones:
1. `PROMPT_VERSION_COLUMNA` pasó a f22-2. No estaba pedido de forma explícita. Es coherente, porque la escaleta con columna usa el mismo SYSTEM_V2, pero es un cambio extra.
2. Se agregó `SYSTEM_V2_F22_1` (copia de ~70 líneas de la v2.1 anterior) y `PROMPT_VERSION_V2_F22`. Tampoco estaba pedido. Conserva la trazabilidad y los tests de md5 lo cubren.
3. `fase1_5.py:281` conserva el comentario «sin --modelo, el guion es Opus 5.5». Ahora es falso (el modelo es Fable). Es solo un comentario; el archivo no fue tocado por F22e.
4. Los tests de md5 se reescribieron para aceptar el valor nuevo (`22cfd68b…`). Eso es esperable en este cambio.

Riesgos que el contrato no cubre: el costo de Fable es US$ 10/50 por millón, más del doble que Opus, y ahora es el default de toda corrida de guion sin `--modelo`. La frase nueva de la promesa no tiene validación empírica porque no hubo corridas.
