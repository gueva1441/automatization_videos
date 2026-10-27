# HANDOFF F38e — lo que rompe cualquier video, y nada más (analista, 2026-10-27)

**Para qué:** dejar el sistema listo para Kyshtym (el primer tema nuevo con la estructura de F36–F38). Se arregla solo lo que fallaría en **cualquier** tema. **Cero experimentos de prompt**: el único cambio de prompt es el de la prueba 1, ya medido (F38e-0: mejor elección y ningún rótulo peor). Vajont sigue congelado: no se re-renderiza.

## 0. Orden re-derivado (handoff-analista §0)
- ¿Construye sobre código a reemplazar? No: `pantalla_colocar`, `gfx_layer`, `fase2b` y `m01e` son la estructura vigente (F36/F37).
- ¿Cambia el orden alguna decisión de hoy? Sí, y ya está aplicado: Omar 12:32, «una tanda con lo que rompe cualquier video → Kyshtym solo, de la semilla al papel → rótulos y títulos se pulen con dos temas a la vista». Se archivan las rondas 1b/2b (no se corren). Fuera de esta tanda: B5 y d1 (prompt), forma F31b, subtítulos documentales. Entran los dos prompts **ya medidos** en F38e-0 (rótulos m01e-6 y pedido de títulos): adoptarlos es el mismo criterio para los dos; pulirlos más espera a tener dos temas (DECISIONES 03:37 pedía los títulos antes de Kyshtym).

## Constantes (ninguna nueva)
| valor | dónde | origen |
|---|---|---|
| `black_hold_sec` 1,0 s | R8 | perfil `gfx_profiles/misterio.json` (identidad F3, existente) |
| 15 cps | lectura de la pregunta de cierre | `pantalla_entrada.LECTURA_CPS` (estándar de subtitulado, DECISIONES 11:02 del 26) |
| tope US$ 1,00 | C, regenerar papel | `m01e_pantalla.TOPE_USD_RESPALDO` (Omar, F37) |
| md5 `38e5ba14…` | candado de ch02 `--only-cap` sin gfx | ESTADO (existente) |

## Módulos tocados (una línea cada uno)
| módulo | hoy | después |
|---|---|---|
| `script_engine/gfx_layer.py` + `fase2b.py` (A) | `apply_gfx(reuse=True)` reusa `chXX_gfx.mp4` aunque cambie el plan; el negro de cierre se planea fuera del segmento | la capa guarda el md5 de su plan y se rehace si no coincide; el negro de 1 s queda dentro del segmento y se mide en el mp4 |
| `script_engine/pantalla_colocar.py` (B) | la escalera de intentos no prueba un corte antes del ancla; el reloj no mueve su fin; un movido sin motivo | prueba todo inicio de escena dentro de la oración ancla; el fin se mueve con el intento; todo movido declara qué falló |
| `script_engine/gfx_realizador.pregunta_cierre` (B) | texto = `cierre` de la escaleta, literal | texto = lo que dice la voz (regla abajo, simulada) |
| `script_engine/m01e_pantalla.py` (C) | prompt m01e-5 | prompt m01e-6 = el de la prueba 1, letra por letra; campos `respaldo` y `autor`; verificación del respaldo |
| `script_engine/m01d_particion.titles()` (E) | Flash ve solo `imagen_sensorial`: «basate en lo que se ve» | el pedido de la prueba 2, letra por letra (promesa del cap; ve la pregunta que abre cada beat y cómo termina) |
| `voz_datos.tarjeta_de_voz` + `m01e.tarjeta` + su plantilla, chequeo y tests (D) | tarjeta fecha-hora en el segundo 0 | **borrada** (DECISIONES 11:21), no apagada |

## Paralelo (DECISIONES 01:23)
**A, B, C y E a la vez, un subagente cada una** (no se pisan: A = `gfx_layer`/`fase2b`; B = `pantalla_colocar`/`gfx_realizador`; C = `m01e`; E = `m01d`). **D después de A** (la tarjeta se dibuja en la capa gfx). `revisor-handoff` al final. Cada parte termina con su salida en texto y PARADA corta (se anota en el reporte y sigue; la PARADA real es al final).

## Paso 0
Commit tal cual, con md5 en el mensaje: `DECISIONES.md` (md5 `463bd8e513796ef3dd6260f346133cd3`, línea 12:32) y este handoff. Si un md5 no coincide: PARADA. Los M ajenos (`diag_234_cap4.py`, `gfx_profiles/*`, `f28a.log`) no entran. `F38e0_REPORT.md` y `ESTADO_SESION.md` figuran modificados **solo por fin de línea** (`git diff --ignore-cr-at-eol` vacío): no se tocan.

## A — Ensamble (r1, R8)
1. **r1:** `apply_gfx` escribe junto a `chXX_gfx.mp4` el md5 del plan resuelto con que se dibujó. Con `reuse`, reusa solo si ese md5 coincide con el del plan actual; si no, rehace y lo dice en el log («capa de otro plan: se rehace»). Test: plan cambiado + `reuse` → se rehace; plan igual → se reusa.
2. **R8:** encontrar la causa con datos (sospecha del analista: `gfx_layer.py:305` planea el `black_hold` en `clip_dur + pausa`, después del final del segmento, y el armado de segmentos en `fase2b` lo recorta; cada `seg_0N` de v6 mide 1,0 s menos que su cap en el guion). Arreglo general: el segmento dura voz + pausa de la pregunta + negro, y el negro está.
3. El chequeo «costuras» deja de medir solo el plan: después de armar cada segmento, `ffprobe` de su duración contra la del guion (±1 cuadro) y `blackdetect` del último segundo; si falla, ✗ en el log del render.
4. **Salida en texto:** render `--only-cap ch02 --gfx` de Vajont (no es render completo: no se mide RAM): duración del segmento contra el guion y `blackdetect` del cierre, pegados. Y el md5 sin gfx de ch02 sigue en `38e5ba14…`.

## B — Colocación (B1–B4)
Contrato: `lab/hyperframes/f38/REVISION_GUION_F38d.md` §2–§3.
1. **B1:** el intento «inicio de escena» prueba **todo inicio de escena dentro de la oración ancla, antes o después de la palabra ancla**, antes de pasar a la oración siguiente. Simulado por el analista: D47 entra a 79,6–84,3 s de ch02.
2. **B2:** el reloj mueve su fin con el intento (misma duración, recortada en su nuevo corte). Simulado: 9 OCT en ch05 entra desde 89,4 s.
3. **B3:** encontrar por qué Q51 pasó de [17] a [18] con `fallas` vacío. Si es bug, se arregla. En cualquier caso, **todo movido declara qué falló en cada intento anterior**.
4. **B4, pregunta de cierre desde la voz.** Regla, simulada por el analista sobre los 7 caps de Vajont:
   - si la última oración de la voz del cap termina en «?», esa pregunta es el texto;
   - si no, por cada oración del `cierre` del último beat, la oración de la voz de ese beat con más palabras de contenido en común (empate: la más tardía; sin coincidencia: ninguna); el texto son esas oraciones, en orden y sin repetir;
   - si no queda ninguna, el `cierre`, como hoy.
   Sin números nuevos (sin umbral: el máximo). La posición no cambia: la pregunta va en su pausa al final del cap (F32).
   Simulación: ch01 «Pero el dique no cedió esa noche. Lo que llegó a la cama de Micaela vino por encima de él.» · ch02, ch03, ch05 = su última oración · ch04 y ch06 = sus dos últimas · ch07 «¿Quién decidió que Micaela siguiera durmiendo?» (45 caracteres, en vez de 190).
5. **Salida en texto:** antes de correr, copiar `output/f8s3-vajont-f30/GUION_PANTALLA.*` a `lab/hyperframes/f38e/b/antes/`. Después, `fase2b f8s3-vajont-f30 --gfx --plan-only` con el papel congelado de F38d, sin regenerar el papel ni tocar `data/`. Tabla contra la revisión: filas #2, #5, #6, #8 y #9 (lo esperado arriba) y la lista de **todo lo demás que cambió** (debería ser nada). Sin `--aprobar-guion`: nadie aprueba nada.

## C — Papel (m01e-6)
1. `PANTALLA_SYSTEM` = el bloque «Prompt nuevo (m01e-6-prueba), entero» de `lab/hyperframes/f38/PRUEBA1_prompt_rotulos.md`, letra por letra (md5 del SYSTEM `7d2ccdd28055d6e621d1d251a0fe8bb7`, el que se midió). `PROMPT_VERSION = "m01e-6"`.
2. `FORMATO_SALIDA` y `FORMATO_REINTENTO`: el de la prueba (con `"respaldo": "…"`) más `"autor": "…" | null` después de `respaldo`. El autor va solo en una cita y es la causa de e1/d1: hoy el modelo lo metía dentro del texto porque no tenía dónde escribirlo.
3. **Respaldo, en `validar`:**
   - el `respaldo` tiene que ser subcadena del texto del ítem (`ev.norm`, como el candado). Si no lo es, es un motivo del reintento, regla `respaldo`;
   - con un respaldo válido, el candado mira cifras, nombres y años contra el respaldo, no contra todo el texto; se mantiene la excepción de lo que dice la oración ancla;
   - las citas siguen exigiendo frase literal.
4. **Autor:** se muestra el del modelo si cada nombre propio que **no** abre la frase está en `autor`, `rol` o `texto` del archivo; si no, el del archivo, sin cortar. Casos de test:
   - «Municipio de Erto y Casso» pasa;
   - «Pietro Leone» no pasa;
   - el de Q14 que devuelva el modelo se reporta, pase o no.
   `caracteres` cuenta el autor que se muestra.
5. **Salida en texto:**
   - copiar `data/scripts/_steps/f8s3-vajont/` a `lab/hyperframes/f38e/c/vajont_steps/` y correr m01e ahí, con `steps_dir`; no se escribe en `data/`;
   - tabla de las fichas: v6 | prueba 1 | m01e-6 con vueltas, con las mismas columnas que `prueba1/TABLA.md`, más el `autor` mostrado y de dónde salió;
   - aparte: las 3 citas (¿entran?), US$ y vueltas.
6. Los tests de m01e se actualizan al formato nuevo y ninguno se borra sin decir por qué.

## E — Títulos de cap (m01d, Fase 1)
1. El pedido de `titles()` = el bloque «Pedido nuevo, entero» de `lab/hyperframes/f38/PRUEBA2_prompt_titulos.md`, letra por letra; `lines` como en la prueba 2 (`prueba2/prueba2_titulos.py`), con una corrección: el pico sale de `esc["pico"]["beat"]` (los beats no traen campo `pico`: abierto e7 de F38e-0). La validación de código (≤ 5 palabras, sin dígito, sin «?») y el respaldo no cambian. Mismo modelo (Flash).
2. Tests de `titles()` al pedido nuevo.
3. **Salida en texto:** el pedido entero tal como sale para Vajont (con « · pico» en el beat 10) y una corrida con los 7 títulos. No se escribe en `data/`.

## D — Borrar la tarjeta fecha-hora (después de A)
Fuera del código: `voz_datos.tarjeta_de_voz` y `tarjeta_inicial` si nadie más los usa, `m01e.tarjeta` y `tarjeta_motivo`, su plantilla, su dibujo en la capa gfx, su línea en `gfx_guion` y su chequeo, sus tests y la entrada en `GUION_PANTALLA`. Una lógica menos, no un flag. **Salida en texto:** `grep -rn tarjeta script_engine/ fase2b.py` antes y después, y el `--plan-only` de B rehecho sin tarjeta (el video arranca con la primera imagen).

## Cierre
- Suite rápida y amplia: verdes, más las 5 previas.
- `F38e_REPORT.md` en `lab/hyperframes/f38e/`, con:
  - las salidas de A–D;
  - US$;
  - «lo que queda abierto» entero;
  - el veredicto íntegro de `revisor-handoff`.
- ESTADO.
- Commits por parte, agregando archivos por ruta explícita.

## Frenos
- Render completo de Vajont → no se hace.
- `--aprobar-guion` → no se hace.
- Escribir en `data/` → PARADA.
- Gasto mayor a US$ 1,00 → PARADA.
- Un número nuevo que no esté en la tabla de constantes → PARADA y se pregunta.
- Fase 3, publicar o merge → no se hace.

## PARADA
Al terminar A–D, revisor y commits. Lo siguiente (Kyshtym de la semilla al papel) es otro handoff.
