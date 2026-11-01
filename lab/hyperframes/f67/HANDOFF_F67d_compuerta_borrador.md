# HANDOFF F67d — Compuerta de narración en borrador: un solo guardado, sin doble aplicación

Modelo → CC: Opus medium. Decisión de Omar 2026-10-31 noche (DECISIONES.md, «Compuerta de narración en borrador»). Sin prompts nuevos. Corre después de F67c en la misma sesión. Sin topes en dólares. No se aprueba ni se cambia la narración de Wittenoom (está aprobada, md5 cd0fe3bf…): las pruebas van sobre copias en un `steps_dir` temporal.

## 0. Orden re-derivado
- ¿Construye sobre algo a reemplazar? Reemplaza las rutas POST `/narracion/aceptar` y `/narracion/editar` (cada clic escribe a disco + reconstruye + juez).
- ¿Cambia el orden? No; no bloquea publicar Wittenoom (su narración ya está aprobada), sirve para el tema 2.

## 1. Bugs que cierra (con evidencia)
1. **Aceptar no es idempotente:** `m01f_critico.aceptar_deberia` vuelve a ubicar `texto_original` en el texto actual; si `deberia_texto` contiene el original (p. ej. agrega una oración después), cada clic lo vuelve a aplicar (Wittenoom ch03, 31-oct: Omar vio el texto repetido varias veces y lo arregló a mano; ENTRADA_ANALISTA_2026-10-31g §0/§1.2).
2. **Lento y sin aviso:** cada clic = `reconstruir` + `judge_narration`; el botón no muestra estado.
3. **DEBERÍA no contiguos dan «ya no aplica»:** `_ubicar` exige oraciones contiguas. Simulado sobre `01f_critico.json` de Wittenoom (22:02):

| k | cap | oraciones | tramos contiguos | partes en `deberia_texto` (separadas por «[…]») | resultado con la regla nueva |
|---|---|---|---|---|---|
| 1 | ch02 | 9, 16, 17 | 2 | 2 | aplica por partes |
| 2 | ch03 | 12–22 | 1 | 1 | aplica (como hoy) |
| 3 | ch04 | 1 | 1 | 1 | aplica |
| 4 | ch05 | 21 | 1 | 1 | aplica |
| 5 | ch06 | 10, 11, 13–16 | 2 | 1 | **no aplica** (partes ≠ tramos): se muestra «editar a mano», no se adivina |
| 6 | ch07 | 1, 7 | 2 | 2 | aplica por partes |

## 2. Constantes
| valor | origen | quién |
|---|---|---|
| separador de partes = el literal «[…]», buscado en `deberia_texto` **crudo, antes de `limpiar`** (que lo borra, m01f_critico.py:166-168); después se limpia cada parte. No usar `validacion.marcas`: caza cualquier corchete (k=6 da `['[idx 1]','[…]','[idx 7]']`, :36) | salida real de m01f-1 (Wittenoom 22:02) | — |
| «Aprobar narración» se habilita cuando **cada** DEBERÍA tiene decisión (aceptar / editar / rechazar); los «no aplica» cuentan como decididos solo si Omar los rechaza o los edita | Omar 31-oct noche | Omar |

## 3. Módulos tocados (hoy → después)
| archivo | hoy | después |
|---|---|---|
| `script_engine/m01f_critico.py` | `aceptar_deberia` y `editar_parrafo` escriben a disco, cada uno con `_aplicar` | función **pura** `borrador(parrafos, critica, decisiones, ediciones) → {parrafos, por_k:{k: aplicado/no_aplica(motivo)}}` (sin disco, sin juez): primero las ediciones libres por párrafo, después cada DEBERÍA aceptado/editado **una sola vez** (por construcción: `decisiones` es un mapa k → acción), por tramos contiguos si las partes coinciden; + `guardar_y_aprobar(topic, decisiones, ediciones, por)` = `borrador` → 1 `_aplicar` → `fase1_5.aprobar_narracion`. Se **borran** `aceptar_deberia` y `editar_parrafo` con sus tests |
| `qa_studio_server.py` | POST `/narracion/aceptar`, `/narracion/editar`, `/narracion/aprobar` | POST `/narracion/borrador` (vista previa, pura, rápida) y `/narracion/aprobar` con `{por, decisiones, ediciones}`; se borran las otras dos rutas |
| `qa_studio.html` (pestaña NARRACIÓN) | cada botón escribe | el borrador vive en la página; cada acción llama a `/narracion/borrador` y repinta; marca por DEBERÍA (aceptado/editado/rechazado/no aplica) y el botón de ese DEBERÍA se apaga tras decidir (se puede «deshacer»); «Aprobar narración» apagado hasta que todo esté decidido; mientras guarda: «guardando…», todos los botones apagados; error visible |
| tests | `tests/test_m01f_compuerta.py` | + idempotencia (aceptar el DEBERÍA que contiene su original = 1 sola vez), partes «[…]», k=5 «no aplica», aprobar con decisiones pendientes → 400 |

## 4. Etapas
A. `borrador` puro + tests. Reglas: (a) `borrador` **siempre parte de los párrafos del disco**; la página nunca devuelve párrafos, solo `decisiones = {k: {accion: aceptar|editar|rechazar, texto?}}` (k = posición en `respuesta.deberia` filtrado, como m01f_critico.py:347) y `ediciones = [{i, texto}]` con `i` indexado sobre los párrafos **del disco** (aceptar elimina párrafos vacíos, :376; nunca indexar sobre la vista previa). (b) Orden: ediciones libres primero, después DEBERÍA; si una edición libre toca el tramo de un k, ese k queda «no aplica (editado a mano)» y se muestra. (c) «Ya aplicado», **por parte y antes de `_ubicar`**: la parte (no vacía) está en el texto del cap **y** no está contenida en el `texto_original` del tramo (k=4: el original sigue ubicable aunque ya esté aplicado). Salida: tabla §1.3 reproducida por código sobre una **copia** de la narración actual de Wittenoom + su `01f_critico.json`: k=2 y k=4 «ya aplicado», nunca doble; k=1, 3, 6 «aplica»; k=5 «no aplica».
B. Rutas + página. Salida: captura a texto (Chrome headless como F66b) de la pestaña con 1 DEBERÍA aceptado, 1 rechazado, 4 sin decidir (botón Aprobar apagado) y después todo decidido (encendido); en `steps_dir` temporal, nunca el real.
C. Reporte `lab/hyperframes/f67/F67d_REPORT.md` (salidas, diff, tests, veredicto íntegro del subagente revisor (`structure-auditor` si no existe `revisor-handoff`; decirlo)), ESTADO_SESION cabecera, commit en `f11-guion-v4`. Copia de este handoff con md5.

## 5. PARADA
Nada de producción. Avisar «CC terminó».
