> **ARCHIVADO 2026-10-27 01:30 — no se ejecuta.** Omar: «¿es la solución de raíz?». No: el juez arreglaba un problema que causó una línea del prompt del analista. Reemplazado por `HANDOFF_F38b_quitar_juez.md`.

# HANDOFF F38b — El juez que discrimina (y prueba antes de aplicar)

Analista · 2026-10-27 01:20 · Para CC. Base: `cde0de6`. Tanda chica: A (prompt + verificación en código, con prueba sobre el papel de F37 antes de tocar Vajont) y B (corrida). Esfuerzo medium, reglas de velocidad de F38 iguales. Sin render, sin aprobar.

## Causa (F38 abierto 1)
El juez marcó «adelanta» en 18 de 18. Sus motivos lo dicen: «el dato especifica un detalle que la voz no menciona» → leyó «adelanta» como «aporta lo que la voz no dice», que es justamente la regla (a) que buscamos. **Falla del analista:** el prompt del juez no se probó contra datos antes de mandarlo. Arreglo general: (1) el prompt dice explícitamente que aportar un dato nuevo está bien; (2) «adelanta» solo cuenta si el juez **cita literal** la oración posterior donde la voz cuenta ese mismo hecho, y **el código verifica** que esa oración existe, es posterior al ancla y contiene la cita. Sin cita verificada no hay marca. El juez juzga sentido; el código impide que invente.

## A. Prompt `juez-2` (literal, reemplaza a `juez-1`) + verificación (commit A)
```
Sos el editor de un documental. Cada texto en pantalla tiene que sumar un dato que la voz no dice: eso está bien y no es un problema.
Te doy, por cada texto: la oración de la voz donde aparece, la anterior y la siguiente, el dato completo del archivo, y la lista numerada (cap:idx) de las oraciones que la voz dice después.
Marcá solo estos dos problemas:
- "otro_asunto": la oración donde aparece y sus vecinas hablan de otra cosa que el dato.
- "adelanta": la voz cuenta ESE MISMO HECHO en una oración posterior, y mostrarlo antes le quita la sorpresa a quien mira. Solo vale si copiás, letra por letra, el pedazo de esa oración posterior donde la voz lo cuenta.
Respondé solo JSON, una entrada por texto:
{"id": …, "otro_asunto": true|false, "adelanta": true|false, "oracion_posterior": "cap:idx" | null, "cita": "pedazo literal" | null, "motivo": "una línea"}
```
- Entrada: la lista posterior va numerada `cap:idx` (hoy va como texto corrido).
- Verificación en código: `adelanta` cuenta solo si `oracion_posterior` existe, es posterior al ancla y `cita` está en ella (texto normalizado: sin tildes, mayúsculas ni puntuación). Si no se verifica, la marca se descarta y se anota «marca sin cita verificada». `otro_asunto` cuenta tal cual.
- **Prueba antes de Vajont (sin tocar `data/`):** correr el juez-2 sobre el papel congelado de F37 (`lab/hyperframes/f37/c/`), grabar la respuesta en `f38/b2/juez2_sobre_f37.json` y pegar la tabla `id · otro_asunto · adelanta · cita · ¿verificada? · motivo`. **Lo que espera el analista** (de `REVISION_PAPEL.md`): D131 en [1] marcado (`otro_asunto`: la oración habla de la presa en pie, o `adelanta` con cita de ch01 [15] «vino por encima de él»); el resto sin marca verificada. Si marca otras con cita verificada, se sigue igual y se listan para el analista. **PARADA solo si vuelven a quedar marcadas todas** (el juez sigue sin discriminar: no se gasta en Vajont).
- Tests (sin API, con la respuesta grabada): una marca sin cita no cuenta; una cita que no está en la oración no cuenta; una oración anterior al ancla no cuenta; D131 queda marcado.

## B. Vajont (commit B)
`m01e_pantalla` suelto → `--plan-only`. Pegar: tabla del juez (las dos rondas), qué cambió el reintento parcial, papel final, pantalla, chequeos, costo. Esperado sin edición a mano: ~10–12 fichas, tarjeta 9 OCT 1963 · 22:39, el gancho en una oración que habla de su dato, Q14 y D195 si el intento 1 los trae y nadie los marca con cita verificada. Gusto → lista para la compuerta. `F38b` va como sección nueva de `F38_REPORT.md` (corta), abierto entero, veredicto del revisor. **PARADA.**

## Frenos
Único cambio de prompt: `juez-1` → `juez-2` (literal, md5 antes/después). Nada hardcode. Tests que lean de `lab/…/c/` congelado, nunca de `data/`.
