# HANDOFF F38c — El autor distingue «la voz lo cuenta» de «va a la pantalla», la contradicción se le pregunta, y los decimales se leen bien

Analista · 2026-10-27 02:05 · Para CC. Base: `1f365cb` (rama `f11-guion-v4`). Aprobado por Omar a las 01:56 («si dale»).
Reemplaza al borrador `HANDOFF_F38c_a_pantalla_y_decimales.md`, que queda como `ARCHIVADO_HANDOFF_F38c_borrador.md` con la razón.
Tanda chica, esfuerzo medium. Un commit A (código) + una corrida B (Vajont en papel y `--plan-only`). **Sin render, sin `--aprobar-guion`, sin merge.**

## 0. Orden (DECISIONES 16:49, vuelto a derivar)
- ¿Construye sobre código que ya decidimos reemplazar? **No.** `m01e_pantalla`, `pantalla_filtros`, `gfx_guion` y `voz_utils` se quedan.
- ¿Alguna decisión de hoy cambia el orden? **No.** Después de F38c: revisión del papel → compuerta de Omar → render v6.
- El formato de las cifras en pantalla (punto o coma, horas «22.39») **no va acá**: la raíz está en el research de Fase 1 (punto 4 del orden de tandas). F38c solo arregla cómo se *leen*.

## 1. Causas (verificadas con datos por el analista)
1. **No aparece el número de muertos, ni en la voz ni en pantalla.** La voz nunca dice 1.910 (en las 161 oraciones solo está «Entre los muertos está Guglielmo Celso»). La escaleta dejó D128 para la pantalla, con el motivo «va escrito, no en la voz». `entrada()` lo mete en `beats_que_lo_cuentan` (líneas 212–218), la misma marca que llevan los `dato_central`/`datos_apoyo`, y el prompt llama a esa marca «lo que la escaleta cuenta ahí». Medido en F38b: el autor descartó **31 ítems marcados como `voz_lo_dice`** (en esos tenía razón), y D128 le llega igual que ellos. **No lo descartó: lo ignoró.** La validación solo mira lo que el autor declara, así que el silencio no deja rastro. De los 5 `a_pantalla`, 2 quedaron en el papel (D117, Q50).
2. **«Cifra que contradice la voz» la mira solo Fase 2.** `gfx_guion` (chequeo 5) la marca ✗ cuando el papel ya está cerrado, y el autor nunca se entera. Tampoco puede cortar: «COTA MÁXIMA 722,5 m» frente a «la cota autorizada fue de 715» pueden ser dos hechos distintos. Lo juzga el autor con el mecanismo de F37 §A.4, la pregunta «¿es el mismo hecho?», no con un filtro nuevo.
3. **«722.50» se lee 72 250.** `voz_utils._num_tok` primero llama a `num_es.parse_int`, que ya tiene bien la regla de miles (grupos de 3 dígitos). Cuando `parse_int` devuelve `None` porque es un decimal, el respaldo hace `tok.replace(".", "")` y borra el punto decimal. Pasa con 722.50 → 72250 y con 0.0282 → 282.

## 2. Simulación del analista (sobre el papel de F38b: `lab/_gpt_probe_analista/f38c/sim_f38c.py`)
**(a) `_num_tok`: lo de hoy contra el arreglo de §A.3**
| token | hoy | arreglo |
|---|---|---|
| 722.50 | 72250 | 722,5 |
| 0.0282 | 282 | 0,0282 |
| 1.910 · 2.600 · 6,500 · 55.645.758.500 | igual (miles, por `parse_int`) | igual |
| 0,5 · 1,5 | igual | igual |
| 22.39 · 8.30 (horas) | 2239 · 830 | 22,39 · 8,3. Ninguno de los dos los lee como hora; no tienen unidad, así que `contradicciones` no los compara. Sin efecto. |
| 25.10.2005 (fecha) | 25102005 | `None`: no es una cifra |

**(b) `contradicciones` sobre las 12 fichas del papel, con la oración ancla ±1**
- 11 dan «—» hoy y con el arreglo.
- D40 da «72250 m vs 715» hoy y «722,5 m vs 715» con el arreglo.
- El arreglo no agrega ni quita ninguna. La ✗ de D40 **no desaparece por los decimales**: pasa a ser una pregunta al autor (§A.2).

**(c) `a_pantalla` faltantes por beat**
| beat | `a_pantalla` | ficha del papel | resultado |
|---|---|---|---|
| ch02 b2 | D117 | D117 | cumple |
| ch05 b8 | Q50 | Q50 | cumple |
| ch06 b11 | D128, D192 | D228 | **motivo** |
| ch07 b13 | D245 | D37 | **motivo**. D245 entra: «CONDENA A MONTEDISON · 55.645.758.500 liras» son 40 caracteres y en las oraciones del beat caben 67–90 (en 9 de 13) |

**No se puede simular:** qué contesta Sonnet en el reintento. Lo esperado de B es «probable», no seguro.

## 3. Constantes
**Ninguna nueva.** La regla de miles es la que ya está en `num_es.parse_int`. «Un separador solo = decimal» se deriva de esa regla: si `parse_int` ya dijo que no son miles, es decimal. El tope del papel sigue saliendo del perfil (`costos.m01e_tope_usd`).

## 4. Módulos tocados (4)
| módulo | hoy | después |
|---|---|---|
| `script_engine/m01e_pantalla.py` (autor del papel, Fase 1) | mezcla `a_pantalla` con `beats_que_lo_cuentan`; valida solo lo que el autor declara | `a_pantalla` va en un campo propio; un beat sin su `a_pantalla` es motivo del reintento; la contradicción es una pregunta al autor |
| `script_engine/pantalla_filtros.py` (filtros del papel y de Fase 2) | `contradicciones` devuelve frases | además devuelve dónde y qué cifra (una sola lógica; las frases salen de ahí); respeta el `juicio_autor` («contradice») como ya lo hacen `no_dicho` y `spoiler` (`_sin_juicio`) |
| `script_engine/gfx_guion.py` (guion de pantalla) | chequeo 5 sin juicio del autor | chequeo 5 respeta el `juicio_autor` de la ficha |
| `script_engine/voz_utils.py` (cifras de la voz) | `_num_tok` borra el punto decimal | `_num_tok` usa la regla de `parse_int` y, si no son miles, decimal |

## A. Código (commit A)
**Paralelo (DECISIONES 01:23):**
- **Subagente 1:** A.1 + A.2. Van juntos porque los dos tocan `validar` de `m01e`.
- **Subagente 2:** A.3 con sus tests.
- La suite amplia corre al final, una vez.

### A.1 Dos marcas distintas (`m01e_pantalla.entrada`, `validar`)
1. Un id de `a_pantalla` ya **no** entra en `cuentan`. Solo entra si además es `dato_central` o `datos_apoyo` de un beat; en ese caso queda en los dos.
2. Cada ítem del archivo que la escaleta marcó lleva `"a_pantalla": {"beat": <n de beat_de_pantalla>, "por_que": "<por_que>"}`. Es data, no regla: **el prompt no cambia**.
3. Validación del papel: por cada beat que tiene `a_pantalla` y cuya ficha no es ninguno de ellos (vacía u otro id), un motivo para el reintento parcial, con ese beat en `motivos_beat`. Texto literal:
   `el beat {n} de {cap} quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: {id} («{por_que}»)[, {id} («{por_que}»)…]`
4. Si el beat ya lleva uno de sus `a_pantalla`, los demás de ese beat no son motivo. Respeta «como máximo una ficha por beat» del prompt.
5. Si después del reintento sigue faltando: no se fuerza ni se corta nada. El `.md` lo marca ⚠, con el descarte del autor si lo hay o «el autor no lo puso».
6. Periférico: la verificación de descartes `voz_lo_dice` (línea ~437) usa `beats_que_lo_cuentan` para elegir qué caps leer. Un `a_pantalla` ahora sin marca se verifica contra todo el video, igual que hoy un ítem sin marca. Probarlo con test.

### A.2 La contradicción se le pregunta al autor (`pantalla_filtros.contradicciones`, `m01e._validar_ficha`, `gfx_guion` chequeo 5)
1. `contradicciones` devuelve también la estructura `(cifra del bloque, cifra de la voz, oración)`, y las frases de hoy salen de ahí. **Una sola lógica**; los tests de F36 (`test_module_f36.py:136–139`) quedan verdes sin tocarlos.
2. En `_validar_ficha`, después de `spoiler`, la ficha corre `contradicciones(etiqueta + texto, voz del video, cerca=oración ancla ±1)`. Lo que encuentra pasa a `preguntas` con `regla: "contradice"` y `token` = la cifra de la voz, como `no_dicho`/`spoiler`. `_pregunta_txt`, para esa regla, usa `que = "para lo mismo, en la oración ancla o en una vecina"`. Así sale:
   `D40 (ch04 beat 7, oración [13]) «COTA MÁXIMA · 722.50 metros»: la voz dice «715» para lo mismo, en la oración ancla o en una vecina en ch04 [13] («La cota autorizada fue de setecientos quince.»); ¿es el mismo hecho? si no, mantenelo`
3. Con `confirmados`, igual que las otras reglas: lo que el autor mantuvo queda en `juicio_autor["contradice"]`, y una contradicción nueva después del reintento corta.
4. `contradicciones` filtra con `_sin_juicio(ctx, "contradice", …)`. Fase 2: verificar que el `juicio_autor` del bloque (`pantalla_entrada.py:145`) llegue al evento que lee `gfx_guion`; si no llega, llevarlo. El chequeo 5 pasa el juicio a `contradicciones`.
5. Periférico: Fase 2 puede mover la ficha a otra oración («mueve en vez de cortar»). El juicio vale por la cifra de la voz, no por la oración, así que sigue valiendo.

### A.3 Decimales (`voz_utils._num_tok`)
- Después de `parse_int`:
  - si el token tiene **un solo** separador (punto o coma), es decimal: `float(tok.replace(",", "."))`;
  - si tiene más de uno y no son miles (25.10.2005), devuelve `None`.
- Se borra el `replace(".", "")` de hoy.
- `_num_tok` solo lo llama `_num_en` → `_analiza_x`, que usan `contradicciones` y `m01e._cifras`. No hay más periféricos (grep del analista).
- Tests: los 11 tokens de la tabla §2(a).

### Tests del commit A
- **A.1:** con la entrada de F38b (desde `lab/hyperframes/f38/b2/`, no desde `data/`):
  - D128, D192 y D245 traen `a_pantalla` con su beat (11, 11, 13) y **no** están en `beats_que_lo_cuentan`;
  - el papel de F38b genera exactamente 2 motivos `a_pantalla` (ch06 b11 y ch07 b13);
  - un papel con D128 en b11 no genera motivo para D192;
  - un `a_pantalla` descartado como `voz_lo_dice` se verifica contra todo el video.
- **A.2:** D40 del papel de F38b genera la pregunta de §A.2.2, literal. Con `confirmados` que la mantienen, `juicio_autor["contradice"] == ["715"]`, y el chequeo 5 de `gfx_guion` no la marca. Las 11 fichas restantes no generan pregunta.
- **A.3:** tabla §2(a).
- **Verificación, una vez:** `verificar.sh` (md5 de ch02, rápida, amplia `-n auto`) en `f38/a3/`. El md5 de ch02 tiene que seguir siendo `38e5ba14…`. Sticker del mapa de módulos actualizado para los 4.
- **Salida de A en texto:** la entrada de D128 tal como la ve el modelo, los 2 motivos y la pregunta de D40 pegados en el reporte.

## B. Vajont (commit B)
- `m01e_pantalla` suelto con la escaleta y el pool de hoy → `--plan-only`. Salidas en `f38/b3/`: papel, raw, log, `GUION_PANTALLA.*`.
- **Esperado (probable, no forzado):**
  - el reintento recibe los 2 motivos `a_pantalla` y la pregunta de D40;
  - D128 en ch06 b11 y D245 en ch07 b13;
  - D40 se mantiene con juicio o se cambia; en los dos casos, chequeo 5 en ✓;
  - `a_pantalla` 4/5 (D192 fuera por una ficha por beat);
  - tarjeta igual; ningún beat cambiado sin motivo.
- Si el autor no pone D128: no se fuerza. Se reporta su respuesta literal.
- Sección corta en `F38_REPORT.md` con lo abierto entero, el veredicto íntegro de `revisor-handoff`, ESTADO y la tabla papel/pantalla como en F38b. **PARADA.**

## Frenos
- **Ningún cambio de prompt:** `PANTALLA_SYSTEM`, `FORMATO_SALIDA`, `FORMATO_REINTENTO` y `REINTENTO_PARCIAL` quedan igual. El md5 del prompt `163e1fd1…` no cambia; si cambia, PARADA.
- Nada hardcode: ningún id, palabra ni cifra de Vajont en el código.
- Tests desde `lab/…`, no desde `data/`.
- No tocar el formato de cifras en pantalla (va al research de Fase 1).
- No se cierra ningún programa de Omar.
