> **ARCHIVADO 2026-10-27 01:58 (no se envió).** Reemplazado por `HANDOFF_F38c_marcas_contradice_decimales.md`. Razón: revisando periféricos con Omar salieron tres fallas del borrador: (1) la causa de D128 no es que `a_pantalla` no llegue, sino que llega mezclado con «la voz lo cuenta» (`beats_que_lo_cuentan`); (2) prometía ✗→✓ en «722.50» y la simulación da 722,5 vs 715 igual; (3) A.2 inventaba una segunda regla de miles (ya existe en `num_es.parse_int`) y el formato español en pantalla rompía horas «22.39»/«8.30».

> **BORRADOR NO ENVIADO (01:40).** Se evalúa en el chat nuevo con Omar antes de mandarlo a CC.

# HANDOFF F38c — El autor sabe qué le dejó la escaleta a la pantalla · decimales

Analista · 2026-10-27 01:50 · Para CC. Base: `1f365cb`. Tanda chica, esfuerzo medium, reglas de velocidad de F38; **subagentes en paralelo** (DECISIONES 01:23): A.1 y A.2 tocan módulos distintos → dos subagentes; la suite corre en paralelo mientras tanto. Un commit A + corrida B. Sin render, sin aprobar.

## Causas (verificadas con datos)
1. **El número de muertos no aparece en ningún lado del video.** La voz nunca dice 1.910 ni 1.269 (grep de las 161 oraciones de F38b: la única mención es «Entre los muertos está Guglielmo Celso»). La escaleta lo sabía y marcó D128 y D192 como `a_pantalla` («va escrito, no en la voz»). Pero `_para_modelo` le manda al autor solo `caps`, `beats`, `archivo` y `clima`: **el `a_pantalla` nunca llega al autor**, que no puede saber que la voz lo calla a propósito. Falla del analista (no lo pedí en F36 C.1).
2. **«722.50» se lee 72 250** y en pantalla diría «722.50» (formato inglés).

## A. Código (commit A, dos subagentes)
**A.1 `a_pantalla` llega al autor y es obligación, no sugerencia** (`m01e_pantalla`):
- Cada ítem del archivo que la escaleta marcó lleva `"a_pantalla": "<por_que>"`.
- Prompt: **una línea nueva en `PANTALLA_SYSTEM`, literal** (no reemplaza a ninguna; la justifica que hoy el dato existe en la entrada pero el prompt no lo nombra): «Los datos marcados a_pantalla la voz los calla a propósito para que se lean en pantalla: cada uno va en una ficha de su beat, salvo que no quepa en ninguna oración del beat.»
- Validación en papel: un `a_pantalla` que no está en el papel → motivo para el reintento parcial en su beat («D128: la escaleta lo dejó para la pantalla y no está»). Si después del reintento sigue afuera, el `.md` lo marca ⚠ con el motivo del autor.
- `PROMPT_VERSION = "m01e-5"`, md5 antes/después.
- Test: con la entrada de F38b, D128, D192 y D245 aparecen como `a_pantalla` en la entrada; un papel sin D128 genera el motivo.
**A.2 Cifras con punto o coma** (`voz_utils` y `pantalla_filtros._analiza`), regla general de formato numérico: un punto o una coma seguidos de **exactamente 3 dígitos** son separador de miles; seguidos de 1 o 2 dígitos, son decimal. En pantalla, las cifras se escriben en formato español (coma decimal, punto de miles) y sin ceros finales en el decimal (722,5). El candado compara por valor. Tests: «722.50» = 722,5; «1.910» = 1910; «55.645.758.500» = 55 645 758 500; «0,5» = 0,5.

## B. Vajont (commit B)
`m01e_pantalla` suelto → `--plan-only`. Esperado sin edición a mano: D128 (y D192 si cabe) en ch06 b11, D245 en ch07; «722,5» o «722,5 m» bien escrito y el ✗ de «cifra que contradice la voz» en ✓; tarjeta; 12–14 fichas; ningún beat cambiado sin motivo. Gusto → lista para la compuerta de Omar. Sección corta en `F38_REPORT.md`, abierto entero, veredicto del revisor, ESTADO. **PARADA.**

## Frenos
Cambio de prompt: solo la línea de A.1, literal. Nada hardcode. Tests desde `lab/…`, no desde `data/`.
