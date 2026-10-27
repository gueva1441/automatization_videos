# HANDOFF F38b — Quitar la causa, no agregar un juez

Analista · 2026-10-27 01:30 · Para CC. Base: `cde0de6`. Tanda chica (medium, reglas de velocidad de F38). Un commit de código + la corrida. Sin render, sin aprobar.

## Causa raíz (verificada con los datos de las tres corridas)
| prompt | intento 1: ficha del gancho | dónde |
|---|---|---|
| m01e-1 (F36) | D131 «Más de 260 metros» | [15] «Lo que llegó a la cama de Micaela vino por encima de él» → habla del mismo hecho, en su momento |
| m01e-2 (F37), intento 1 | D131 | [15], igual |
| m01e-2 (F37), reintento | D131 | **[1]** «la presa… sigue en pie» → otro asunto y adelanta el salto |
| m01e-3 (F38), intento 1 | D131 | **[1]**, igual |

El único problema de «oración que no corresponde / adelanta un hecho» que vimos lo **causó la línea que agregó el analista en F37 A.3a** («…y que pueda ir en las primeras oraciones del capítulo»): el autor no cambió de dato, **movió el mismo dato** a una oración que no le corresponde. Con m01e-1 lo anclaba bien. El juez de F38 se agregó para tapar ese efecto: es una segunda capa encima de un error propio, no la raíz. Raíz: **sacar la línea y sacar el juez** («quitar reglas, no apilar»).

## A. Código (commit A)
1. **Revertir la línea del gancho** en `PANTALLA_SYSTEM` a la de m01e-1, literal: «…en el gancho (capítulo 1), cualquier dato del archivo que la voz no diga en todo el video y que haga quedarse a quien mira: el gancho nunca queda sin ficha.» `PROMPT_VERSION = "m01e-4"`, md5 antes/después.
2. **Borrar el juez** (no apagar): `JUEZ_SYSTEM`, la llamada, las dos rondas, la caché `01e_juez*`, su regla `juez` en la validación, sus tests y su grabación. El reintento parcial queda solo con los motivos de las validaciones mecánicas (fecha del relato, cita sin fecha, caben, «¿mismo hecho?», «vuelve», pico vacío).
3. **Se quedan** (son raíz, de F38 A): reintento parcial, tarjeta desde la voz, fracciones.
4. Tests: el gancho de m01e-4 no tiene la frase; no existe nada que llame al juez (grep); el reintento parcial sigue verde.

## B. Vajont (commit B)
`m01e_pantalla` suelto → `--plan-only`. **Esperado, con los datos de m01e-1/m01e-2 intento 1 como base:** ~12 fichas, D131 en ch01 [15] (mismo hecho, sin adelantar), tarjeta 9 OCT 1963 · 22:39, ningún beat cambiado sin motivo. **Que el gancho caiga a 1:26 en vez de en los primeros segundos no es un error de sentido: es gusto** (en los primeros 30 s ya están la tarjeta y el sello PÁNICO); va a la compuerta de Omar con las opciones D118/D195. Pegar papel, pantalla, chequeos y costo como sección nueva y corta de `F38_REPORT.md`; abierto entero; veredicto del revisor. **PARADA.**

## Frenos
Único cambio de prompt: revertir esa línea. Nada nuevo. Nada hardcode. Tests desde `lab/…/c/`, nunca desde `data/`.
