# HANDOFF F38d — Lo nuevo se pregunta en otra vuelta (no se corta a ciegas) · el prompt mide «caben» como el código

Analista · 2026-10-27 02:50 · Para CC. Base: `cc7058d` (rama `f11-guion-v4`). Aprobado por Omar a las 02:36 («si dale»).
Tanda chica, esfuerzo medium. Un commit A (código) + una corrida B (Vajont en papel y `--plan-only`). **Sin render, sin `--aprobar-guion`, sin merge.**

## 0. Orden (DECISIONES 16:49, vuelto a derivar)
- ¿Construye sobre código que ya decidimos reemplazar? **No.** Solo toca `m01e_pantalla`, que se queda.
- ¿Alguna decisión de hoy cambia el orden? **No.** Después de F38d: revisión del papel → compuerta de Omar → render v6.

## 1. Causas (verificadas con datos de `f38/b3/`)
1. **ch04 b7 (pico) quedó vacío. Falla del analista (F38c §A.2.3).** El intento 1 puso D105, y la validación le preguntó si «1962» era el mismo hecho. En el reintento el autor lo cambió por D241, «COTA DEL PROYECTO · 723 metros», que es otro hecho distinto de la cota autorizada de 715. El chequeo «contradice» no distingue eso, y como la coincidencia salió **después** del reintento, se cortó sin preguntar. Hoy `llamar` hace **una** sola vuelta de reintento: todo lo nuevo que aparece en esa vuelta (preguntas, fichas caídas) corta sin que el autor lo vea. Lo mismo pasa con `no_dicho` y `spoiler` desde F37, y los tres son detectores con falsos positivos conocidos.
2. **ch05 b8 (pico) quedó vacío y sin su `a_pantalla` Q50. Falla del analista (F36 §C.4).** El prompt dice «Etiqueta + dato no pueden pasar de los caracteres que caben», pero `pantalla_colocar.caracteres` cuenta además, en una cita, **el autor + 5** (comillas y raya). Q50: etiqueta 21 + dato 42 + autor «Administración del comune di Erto e Casso» 41 + 5 = **109**. En la oración [3] caben 77, y el máximo del beat es 90. El autor no sabe que el autor de la cita cuenta, y el motivo de hoy le miente: dice «etiqueta + dato = 109». Recortó de 118 a 109 y volvió a caer. En F38b entró de casualidad: eligió una cita corta, 86 caracteres en [2], donde caben 90.

## 2. Simulación del analista
**(a) ¿Q50 puede entrar con el contrato corregido?** Sí. Medido sobre la entrada de F38c (`f38/b3/01e_pantalla.raw.json`):
| ch05 b8, oraciones | caben |
|---|---|
| [0] [2] [5] [13] | 90 |
| [7] | 88 |
| [1] [3] [11] | 77 |
| resto | 31–62 |
- Autor + 5 = 46, así que a etiqueta + dato les quedan ≤ 44 en una oración de 90.
- «CARTA DE ERTO Y CASSO» (21) + «continua aprensión» (18) + 46 = **85 ≤ 90** → entra en [0], [2], [5] o [13].
- La cita entera, «en continua aprensión y en continua alarma» (42), no entra con ninguna etiqueta. El autor tiene que recortar la cita, que el prompt ya permite («recortada pero sin cambiar palabras»).

**(b) ¿Cuántas vueltas paga el tope?** Se calcula con `_peor_usd` de hoy y las tarifas de `claude_helpers.PRICES` (Sonnet 2 / 10 por millón). La salida peor es la mayor vista: 16 961 tokens.
- Peor caso de una vuelta, con un pedido de ~147 k caracteres: ≈ US$ 0,29. Una vuelta real de F38c costó **US$ 0,17**.
| después de | gastado real | + peor de la siguiente | ¿entra en el tope 1,00? |
|---|---|---|---|
| intento 1 | 0,30 | 0,59 | sí → vuelta 1 |
| vuelta 1 | 0,47 | 0,76 | sí → vuelta 2 |
| vuelta 2 | ~0,64 | ~0,93 | sí → vuelta 3 |
| vuelta 3 | ~0,81 | ~1,10 | **no** → cierra |
- Con el tope de hoy son como mucho **3 vueltas**, y el papel queda como mucho en ~US$ 0,81 (hoy 0,47). **Ningún número nuevo:** las vueltas las limita el tope que ya existe (`costos.m01e_tope_usd`; el perfil no trae la clave, así que vale el respaldo 1,00 que pidió Omar en F37).

**(c) ¿Qué habría pasado en F38c con F38d?** La vuelta 2 habría recibido:
- la pregunta de D241 («la voz dice 715 para lo mismo… ¿es el mismo hecho?») en lugar del corte;
- el motivo de Q50 con el desglose verdadero;
- el pico vacío de ch05 b8 y su `a_pantalla`.

**No se puede simular** qué contesta Sonnet.

## 3. Constantes
| valor | origen | quién |
|---|---|---|
| tope US$ 1,00 (limita las vueltas) | perfil `costos.m01e_tope_usd`, o el respaldo de F37 | Omar (F37) |
| 5 caracteres de comillas y raya en una cita | ya existe en `pantalla_colocar.caracteres` (F36 §C.4, derivado: lo que se dibuja) | existente |
| «sin progreso» = los motivos de una vuelta son iguales a los de la anterior | derivado: otra vuelta no tiene nada nuevo que decirle al autor | analista |
Ningún número más.

## 4. Módulos tocados (1)
| módulo | hoy | después |
|---|---|---|
| `script_engine/m01e_pantalla.py` (autor del papel, Fase 1) | un reintento; lo nuevo después de él corta; el prompt y el motivo de «caben» no cuentan el autor de la cita | vueltas de reintento parcial mientras haya motivos y entre en el tope; lo nuevo se pregunta; prompt y motivo miden igual que el código |

## A. Código (commit A)
**Paralelo (DECISIONES 01:23):**
- **Subagente 1:** A.1 + A.2. Es un solo archivo; no se parte en dos, porque se pisan.
- **Subagente 2:** escribe los tests del commit A desde este handoff, en archivo aparte, mientras tanto.
- Al cerrar A, `revisor-handoff` revisa el diff de A **en paralelo** con B.

### A.1 Vueltas de reintento parcial (`llamar`, `validar`)
1. Después de cada vuelta, la validación del papel fusionado corre con los `confirmados` acumulados (las preguntas ya hechas: lo que el autor mantuvo es «otro hecho»). **Una coincidencia nueva** (`no_dicho`, `spoiler`, `contradice`) **no corta: es una pregunta** de la vuelta siguiente, igual que en el intento 1.
2. Hay otra vuelta (el mismo `_reintento_parcial`, el mismo `fusionar`, solo los beats con motivo) mientras se cumplan las tres:
   - hay motivos;
   - los motivos no son iguales a los de la vuelta anterior (sin progreso → cierra);
   - la vuelta entra en el tope (`autor()` ya lo calcula).
3. **Al cerrar** (no hay más motivos, no hubo progreso, se acabó el tope o una vuelta no devolvió JSON), se hace la validación final de hoy: lo que sigue sin preguntar corta, como ahora. El `.md` dice por qué cerró y qué cortó sin pregunta.
4. `confirmados` se acumula de vuelta en vuelta con `_confirmar`; nunca se pisa.
5. El raw pasa a guardar `reintento.vueltas`: por vuelta, beats, motivos, aplicados, ignorados, usd y por qué cerró. `armar`/`a_markdown` lo muestran por vuelta. Periférico: el único lector de `reintento` fuera de `llamar` es `armar`/`a_markdown` (grep del analista). Los tests de F37/F38/F38c que miran `reintento` se ajustan **sin aflojar asserts**.
6. El reintento de JSON completo (el primer intento no parsea) queda como está.

### A.2 «Caben» igual en el prompt, en el motivo y en el código
1. **Prompt (cambio literal, una línea).** En `PANTALLA_SYSTEM`, la oración
   `Etiqueta + dato no pueden pasar de los caracteres que caben en la oración ancla (`caben`); si no caben, elegí otra oración o un dato más corto.`
   pasa a
   `Etiqueta + dato —y en una cita, también el autor tal como viene en el archivo y 5 caracteres de comillas y raya— no pueden pasar de los caracteres que caben en la oración ancla (`caben`); si no caben, elegí otra oración o un dato más corto.`
   - No es una regla nueva: corrige la que no decía lo que mide el código.
   - `PROMPT_VERSION = "m01e-5"`, md5 antes y después.
   - **Ninguna otra línea del prompt cambia.**
2. **Motivo de «caben»** (`_validar_ficha`, línea ~616), en vez de «etiqueta + dato = {n}»:
   - normal: `etiqueta {e} + dato {d} = {n} caracteres y en la oración [{si}] caben {c}; en este beat caben como máximo {m} (oración [{sm}])`
   - cita: `etiqueta {e} + dato {d} + autor {a} (con comillas y raya) = {n} caracteres y en la oración [{si}] caben {c}; en este beat caben como máximo {m} (oración [{sm}])`
   - `{m}` y `{sm}` son el mayor `caben` de las oraciones del beat y su oración: data de la entrada, no regla.

### Tests del commit A (los escribe el subagente 2; leen de `lab/`, no de `data/`)
1. Con `post` simulado, el papel de F38c: la vuelta 1 cambia ch04 b7 a D241. La validación pregunta por D241 (`contradice`) y **no corta**. En la vuelta 2 el autor la mantiene → queda con `juicio_autor["contradice"]`, y el chequeo 5 de Fase 2 da ✓.
2. Sin progreso: si la vuelta 2 devuelve lo mismo y los motivos son iguales → cierra. Lo que sigue sin preguntar corta, y el `.md` lo dice.
3. Tope: con `tope` chico, cierra antes de la vuelta que no entra, igual que hoy.
4. Q50: el motivo dice `etiqueta 21 + dato 42 + autor 41 (con comillas y raya) = 109 … caben como máximo 90 (oración [0])`. Si hay empate en el máximo, la primera: es solo informativo.
5. El md5 del prompt cambia exactamente por esa línea. El test compara contra el texto literal de §A.2.1.
6. **Verificación, una vez:** `verificar.sh a4` → md5 de ch02 sigue `38e5ba14…`, rápida 58, amplia sin fallas nuevas. Sticker de `m01e_pantalla` actualizado.
7. **Salida de A en texto:** el prompt cambiado, línea literal, con los dos md5; el motivo de Q50 literal; y el raw de la prueba 1, mostrando las 2 vueltas.

## B. Vajont (commit B)
- `m01e_pantalla` suelto (la clave cambia por la versión del prompt, así que es llamada nueva) → `--plan-only`. Salidas en `f38/b4/`.
- **Esperado (probable, no forzado):**
  - 7/7 picos con ficha;
  - `a_pantalla` ≥ 4/5: Q50 entra recortada; D192 sigue fuera por una ficha por beat;
  - D128 y D245 se quedan;
  - chequeo 5 ✓;
  - 1 a 3 vueltas, papel ≤ US$ 1,00.
- Si un pico sigue vacío: no se fuerza. Se pega el motivo y la respuesta del autor de cada vuelta.
- Sección corta en `F38_REPORT.md`: la tabla papel/pantalla como en F38c, por vuelta qué cambió y cuánto costó, lo abierto entero, los dos veredictos de `revisor-handoff` (A y final) íntegros, y ESTADO. **PARADA.**

## Frenos
- Cambio de prompt: **solo** la línea de §A.2.1, literal. Si el md5 cambia por otra cosa, PARADA.
- Ningún número nuevo. Las vueltas las limita el tope del perfil.
- Nada hardcode: ningún id, palabra ni cifra de Vajont en el código.
- Tests desde `lab/`.
- No subir nada de `lab/_gpt_probe_analista/` (va fuera de git).
- No se cierra ningún programa de Omar.
