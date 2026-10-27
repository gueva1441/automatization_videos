# Revisión del guion de pantalla en papel — Vajont (`01e_pantalla`, m01e-1) · analista · 2026-10-26 22:40

Fuente: `data/scripts/_steps/f8s3-vajont/01e_pantalla.json` y `.raw.json` (entrada: 7 caps, 161 oraciones, 400 ítems de archivo), pool `00_pool_v3.json`, guion colocado `lab/hyperframes/f36/d/GUION_PANTALLA.json`. Criterio: retención (¿hace quedarse?), regla a/b/c, cantidad por cap. `[n]` = oración del cap.

## Veredicto
El papel es **bueno en criterio y corto en cantidad**: 9 fichas en 17 min, ch04 sin ninguna y 2 beats pico vacíos (ch02 b3, ch04 b7). De las 9, 6 son buenas tal cual. Fallas del modelo: 3 (T39 descartado con motivo falso, T85 con motivo falso, D128 omitido sin motivo). Fallas de Fase 2: 8 de 18 cortados por razones mecánicas que deberían ser «mover» (F37). Fallas de filtros: 2 falsos positivos por coincidencia de número (D47 «2», D105 «1962»).
Corrección del analista sobre lo dicho a las 22:16: el archivo sin los D sin cifra **no le quitó nada al autor**: los 10 «no existe en el archivo» (D24, D71, D103, D154, D157, D164, D119, D227, D229, D50) son todos cosas que la voz ya dice. Es ruido en los descartes, no pérdida.

## Cap por cap (DEBERÍA)
| cap · beat | papel | veredicto | DEBERÍA |
|---|---|---|---|
| ch01 b1 gancho | D131 «SALTO DE LA MASA DE AGUA · Más de 260 metros» en [15] (1:26) | ✗ tarde para gancho; además las fuentes no coinciden en la altura (D123 250, D215 200, D44 260) | **Opción A (voto):** D118 «LA PRESA DEL VAJONT · 266 m, la más alta del mundo» en [1] («…la presa que todos creyeron caída sigue en pie», ~0:10): no adelanta nada y abre la pregunta. **Opción B:** D195 «LONGARONE · 1.269 de 1.328 habitantes murieron» en [2] (0:18). Con A, D195 va al clímax (ch06). |
| ch01 sello | PÁNICO [4] | ✓ | — |
| ch02 b2 | D117 papel «SESIÓN DEL CONSEJO SUPERIOR · 13 de 34 representantes presentes» [2]; Fase 2 la cortó (crítico: tapa el documento) | ✓ contenido · ✗ colocación | se queda; F37: mover (otra posición/escena), no cortar |
| ch02 b2 sello | CALMA [6], cortado (rostros) | ✓ contenido | F37: mover de posición |
| ch02 b3 PICO | — (D47 cortado por «spoiler» por el «2») | ✗ pico vacío; el spoiler es falso positivo (2 km del desmoronamiento ≠ 2 km de la fisura de ch03) | **D47 «DESMORONAMIENTO DEL TOC · 2 km de frente y 600 m de desarrollo vertical»** en [11] (Müller lo detecta) |
| ch02 b3 sello | AMENAZA [10] | ✓ | — |
| ch03 b4 PICO | T16 «LA VÍCTIMA DE PONTESEI · Arcangelo Tiziani» [3], **dura 12.7 s** | ✓ contenido (humaniza) · ✗ duración | se queda; F37: duración de ficha con `callout_dur_max` 6.0 s (identidad) |
| ch03 b5 | D49 «ANCHO DE LA FISURA · Más de 1 metro» [17] | ✓ | — |
| ch03 b5 sello | INMINENTE [18], cortado (tapa la fisura) | ✓ | F37: mover de posición |
| ch04 b6 | — (T39 descartado: «la voz ya cuenta la advertencia») | ✗ motivo falso: la voz [6] dice «la amenaza sobre Erto seguía ahí», **no** los 50 millones | **T39 «ROCA QUE AMENAZA ERTO · 50 millones de m³»** en [6] |
| ch04 b7 PICO | — | ✗ pico vacío | **D105 «ENEL · creado por ley en diciembre de 1962»** en [16] («En julio se completó el cambio de propiedad…»): quién compraba era el Estado. (D105 cayó por «no dicho» por el «1962» de [14], otro número: falso positivo). T50 (720 m) **no**: contradice el «700 m en junio» que la voz dice en ch05. |
| ch04 b7 sello | AVISO [14], cortado (cruza el corte) | ✓ | F37: mover antes del corte |
| ch05 b8 PICO | Q50 cita, 127 caracteres, cortada por lectura | ✓ dato · ✗ largo | **Q50 «CARTA DEL MUNICIPIO DE ERTO · “en continua aprensión y en continua alarma”»** (literal, ~70 car.) en [7] («…los de arriba, los que tenían las grietas en el patio», caben 89) |
| ch05 b8 sello | SILENCIO [10] «De la ola no hablaba nadie», cortado (corte) | ✓ excelente lugar | F37: mover antes del corte |
| ch05 b9 | — | ✗ beat vacío | **Q43 «INGENIERO JEFE · “Son sacudidas menores, no hace falta informar al ministerio”»** en [15] (Biadene escribe a Pancini). **Ojo:** la fuente no da fecha y el autor es «sucesor de Semenza» (= Biadene): Omar decide si lo pone en esta noche. |
| ch06 b10 PICO | D01 «ROCA DESPRENDIDA · 270 millones de m³ de roca» [3] | ✓ muy bueno | — |
| ch06 b10 | — | (con opción A) | **+ D195 «LONGARONE · 1.269 de 1.328 habitantes»** en [20] («Longarone ya no.»): el golpe del video |
| ch06 b10 sello | COLAPSO [20], cortado (corte) | ✓ | con D195 en [20], COLAPSO pasa a [19] o se mueve; F37 |
| ch06 b11 | D17 «EVACUADOS DE SU ALDEA · 486 personas» [29] | ✗ débil frente a lo que falta | **D128 «MUERTOS, RECUENTO OFICIAL · 1.910 personas»** en [24] («Entre los muertos está Guglielmo Celso…»); D17 fuera |
| ch06 b11 sello | RABIA [31], cortado (rostro) | ✓ | F37: mover de posición |
| ch07 b12 PICO | Q14 cita «RESPUESTA DE GIOVANNI LEONE · “Y justicia tendréis”» [1] | ✓ muy bueno (la ironía del video) | se queda. **T85 fuera**: un texto por beat y Q14 retiene más; el reloj 20 FEB 1968 ya marca la fecha (cambia el «sí» de las 21:55: Omar confirma) |
| ch07 b13 | D245 «CONDENA A MONTEDISON · 55.645.758.500 liras» [18] | ✓ | — |
| ch07 sello | MEMORIA [22] | ✓ | — |
| (opcional) ch06 | — | | D84 «presión del aire = dos bombas de Hiroshima» en [5]: fuerte, pero ch06 ya tendría 3; solo si Omar lo quiere |

**Con las DEBERÍA:** 14 fichas (ch01 1 · ch02 2 · ch03 2 · ch04 2 · ch05 2 · ch06 3 · ch07 2) ≈ una cada 75 s, todos los picos con ficha; 9 sellos (los del papel, recolocados).

## Para F37 (Fase 2: colocar, no autor; sin números nuevos)
1. **Mover en vez de cortar** (corte de escena, lectura, crítico «estorba»): probar dentro de la oración, el inicio de la escena siguiente dentro de la oración, y la otra posición de pantalla; si nada entra, «papel sin colocar».
2. **Duración de la ficha** = lectura (15 cps) entre `callout_dur_min` 2.5 y `callout_dur_max` 6.0 (identidad F3, perfil); hoy T16 12.7 s, D131 11.2 s.
3. **Falsos positivos por número suelto** en `spoiler` y `no_dicho`: comparar número **con su unidad/magnitud** (como B.5 hizo con las cotas). Casos: D47 «2», D105 «1962».
4. Las ediciones de Omar al papel (esta tabla) por `--plan-edit` sobre `01e_pantalla.json`.
5. Prompt de m01e: **no se toca** por 3 errores en 18 decisiones; se anota y se mira en Kyshtym.
