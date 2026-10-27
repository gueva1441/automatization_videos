# HANDOFF F40 — gancho, subtítulos documentales y Kyshtym listo para aprobar (analista, 2026-10-27)

**Para qué:** es la última tanda antes de publicar Kyshtym (DECISIONES 18:30). Trae solo tres cosas: **A** el gancho, **B** los subtítulos y **C** Kyshtym. Todo lo demás está en la lista de DECISIONES 18:30 y **no se toca**. Termina con el papel de Kyshtym listo para que Omar lo apruebe. No hay voz, ni imágenes, ni render de Kyshtym.

## 0. Orden re-derivado
- ¿Construye sobre código que se va a reemplazar? No. A **quita** una regla, B cambia el estilo de un archivo de subtítulos, C solo toca datos de Kyshtym.
- ¿Alguna decisión de hoy cambia el orden? Sí: la de 18:30. Se archivan las rondas del gfx y la propuesta F39b del analista: de sus 4 puntos, entra solo el del gancho; el resto va a la lista.

## 1. Constantes
| valor | dónde | origen | quién |
|---|---|---|---|
| tope de la tanda US$ 1,50 | `lab/TOPE_TANDA.json` | derivado: papel ≤ 1,00 (tope existente de m01e) + crítico del render de muestra + margen | analista |
| fuente de los subtítulos: Anton | `fonts.subs` del perfil | existente; es la misma del title card (`fonts.title`) | Omar 03:34 («familia del title card») |
| **60 px** de alto de letra (1080p) | estilo del .ass long-form | **voto del analista**; Omar lo confirma o lo cambia mirando las fotos de B.3 | Omar |
| ≤ 42 caracteres por renglón, ≤ 2 renglones | armado de los subtítulos | estándar: Netflix Timed Text Style Guide | — |
| duración de cada subtítulo: mínimo 0,833 s, máximo 7 s | armado | Netflix Timed Text Style Guide | — |
| blanco con borde negro, sin amarillo, sin resaltar palabra por palabra | estilo | DECISIONES 03:34 | Omar |
| borde 4 y sombra 2 | estilo | derivado: el borde 10 y la sombra 5 del estilo `Viral` (150 px), escalados a 60 px | — |
| `MarginV` 108 | estilo | existente (estilo `Viral`) | — |

## 2. Módulos tocados
| módulo | hoy | después |
|---|---|---|
| `script_engine/pantalla_filtros.py` (A) | `gancho_dicho` corta en seco el dato del gancho si cualquier cifra suya aparece en cualquier parte de la voz | `gancho_dicho` **borrado**: la coincidencia sigue en `no_dicho` (ya suma las cifras de todo el video para el gancho) y se le **pregunta** al autor, como en los otros beats |
| `script_engine/m01e_pantalla.py` + `pantalla_entrada.py` (A) | calculan `dice_voz` para el gancho | `dice_voz` borrado en los dos (queda sin lector). La pregunta al autor cita la oración y el cap donde la voz dice la cifra, no «la oración ancla o una vecina» |
| `fase2b.py` (B) | long-form quema karaoke (`_build_ass_from_words`: Anton 150, 3 palabras, palabra resaltada) | long-form quema subtítulos documentales (constantes de §1); el karaoke queda **solo** para `video_type` short; `_build_ass_from_syllables` se borra si no tiene llamador vivo |
| datos de `f39-kyshtym` (C) | — | voz sin voseo, títulos nuevos, papel regenerado (sin código) |

## 3. Simulación de A (analista, sobre los datos reales)
| tema | dato del gancho | cifras que encuentra en la voz | hoy | con F40 |
|---|---|---|---|---|
| Kyshtym | D03 «nivel 6 de 7» | 6, 7 («seis de octubre», «siete y veinte»…) | corta en seco | pregunta al autor → otro hecho → **queda** |
| Kyshtym | D50 «19 veces más que Chernóbil» | 19 («dieciocho, diecinueve, veinte años») | corta en seco | pregunta → queda |
| Kyshtym | D201 «planta 20, Valia Dronova» | 20 | corta en seco | pregunta → queda |
| Vajont v6 | D195 «1.269 de 1.328» | ninguna | pasa | pasa (sin cambio) |

Antes de borrar el corte, el analista probó una alternativa: «misma cifra y una palabra en común en la misma oración». Se descartó porque D201 seguía cayendo por «trabaj» («vehículos que **trabaj**aron… veinte o treinta»): una regla de palabras sigue fallando. Lo que funciona es quitar el corte y dejar que el autor juzgue, que es lo vigente para los otros beats (F37 §A.4).

## 4. Paralelo
- Paso 0 en serie.
- **A y B a la vez**, un subagente cada una (no comparten archivos).
- **C después de A**: el papel se regenera con la regla nueva.
- Candado en serie al final de A y B, `revisor-handoff` al final.

## 5. Paso 0
Commit tal cual de `DECISIONES.md` (md5 `0f5bcfb445fae06c7a48ea7b001eed48`, línea 18:30) y este handoff, con los md5 en el mensaje. Si un md5 no coincide: PARADA. Push de la rama al final de la tanda (`main` no se toca).

## 6. A — El gancho (pregunta, no corte)
1. Borrar `pantalla_filtros.gancho_dicho` y su lugar en el orden de filtros, y `dice_voz` en `m01e_pantalla` y `pantalla_entrada`. Sus tests se borran por nombre o se ajustan.
2. La pregunta al autor de una cifra del gancho dice dónde la dice la voz: cap, número de oración y la oración. Es el mismo formato que ya usa el spoiler: «la voz dice «6» en ch05 [12] («…»); ¿es el mismo hecho? si no, mantenelo».
3. Tests:
   - D03 con «seis de octubre» en otro cap → pregunta, y con «otro hecho» → queda;
   - un gancho cuya cifra la voz dice de verdad con el mismo hecho → el autor dice «mismo hecho» → sale;
   - Vajont D195 → sin cambio.
4. **Salida en texto:** la tabla de §3 recalculada por código.

## 7. B — Subtítulos documentales
1. Long-form (`video_type` long): un estilo nuevo con las constantes de §1. Los cortes van por oración o frase, respetando ≤ 42 caracteres y ≤ 2 renglones, con los tiempos de las palabras que ya existen (`remap_words_to_original`). No hay efecto por palabra. Se mantiene «sin comillas» de F30b (Anton dibuja » como >>). Texto como lo escribe la voz, sin pasar a mayúsculas.
2. Short: karaoke como hoy.
3. Hook (`Hook`, amarillo, `apply_hook`): **no se toca**. El reporte dice si corre en long-form y con qué texto.
4. **Salida en texto** sobre Vajont ch02 (tiene voz; no se gasta nada):
   - (a) los eventos del .ass nuevo (inicio, fin, texto, caracteres por renglón), con ✗ en los que violen §1;
   - (b) render `--only-cap ch02 --gfx --reuse-visuals` y **3 fotos PNG**: una con subtítulo de 2 renglones, una con ficha y subtítulo a la vez (que se vea si se pisan) y una con solo subtítulo;
   - (c) candado: el md5 de ch02 sin gfx **cambia** porque cambian los subtítulos, y es esperado. Para probar que no cambió nada más, correr el mismo `--only-cap ch02` **con `--no-subs` antes y después** del cambio: los dos md5 deben ser iguales. Pegar los tres md5. El candado nuevo, con subtítulos, queda anotado en ESTADO.

## 8. C — Kyshtym (`f39-kyshtym`)
1. **Voz sin voseo:** «cenás» → «cenas» (caps 1 y 7) y «acá» → «aquí» (cap 2), en **todos** los archivos de Fase 1 que llevan la narración (`01b_narracion_v3.json`, `01b_narration.json` con `narration` y `narration_tts`, `01b_guionista_v4.json`, y los que aparezcan). Respaldo `_pre_f40` de cada uno. `grep` final: 0 «cenás» y 0 «acá».
2. **Títulos:** los 7 de DECISIONES 18:30, en todos los archivos de Fase 1 que los llevan (`01a_skeleton.json` y los que aparezcan). `grep` final: 0 títulos viejos.
3. **Papel regenerado** con la regla de A: `m01e_pantalla.generar`, la misma llamada que hace `fase1_5.run_pantalla`, sin script nuevo. Tope existente (US$ 1,00). Respaldo del papel de F39 como `01e_pantalla_f39.*`.
4. **Dos correcciones, solo si se repiten** en el papel nuevo, con `fase2b --plan-edit` (`m01e_pantalla.editar`):
   - ch04 beat 5 con D09 «Entre 8 y 170 t de TNT» → **D50** «CHERNÓBIL · Liberó unas 19 veces más», anclada en la oración de los «veinte millones de curios»;
   - una ficha con «2000» → «2.000».

   Si no se repiten, no se toca nada y se dice. Si `editar` rechaza alguna, se pega el motivo; no se fuerza.
5. **Salida en texto:**
   - `01e_pantalla.md` nuevo **entero**;
   - vueltas, motivos por vuelta, preguntas del gancho con la respuesta del autor, US$;
   - diferencias contra el papel de F39, ficha por ficha.

## 9. Frenos
- Nada de voz, imágenes ni render de Kyshtym. No se corre `--aprobar-papel`: eso lo hace Omar.
- Cero cambios de prompt.
- Nada fuera de A, B y C; lo de la lista no se toca aunque aparezca.
- Ningún número nuevo sin la tabla de §1.

## 10. PARADA
`lab/hyperframes/f40/F40_REPORT.md` con:
- paso 0;
- A (salida de §6.4, tests);
- B (§7.4 a–c, con las 3 fotos);
- C (§8.5);
- suite rápida y amplia;
- push;
- «lo que queda abierto» entero;
- veredicto íntegro de `revisor-handoff`.

ESTADO actualizado. **PARADA**: Omar mira las fotos de los subtítulos y el papel, y si está bien, aprueba.
