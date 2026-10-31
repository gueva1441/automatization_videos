# F65a_REPORT — Cerrar el papel: `a_pantalla` deja de obligar y Fase 2 respeta al verificador

Handoff `lab/hyperframes/f65/HANDOFF_F65a_a_pantalla_y_fase2.md` (md5 1d705b7b053d8796d878cdea1613d827) · rama `f11-guion-v4` · base `5225edf` · 2026-10-31 · CC Opus medium · commits `2c00efa` (Etapa A) y `f54d4ba` (Etapa B) · **cero llamadas al modelo** (juez = caché por `pedido_md5`; ninguna corrida) · nada específico de Wittenoom en el código.

## Etapa A — `a_pantalla` no obliga (`2c00efa`)

**Diff** `script_engine/m01e_pantalla.py` (`validar`): se borró el bloque `for a in a_pantalla_vacios` que sumaba un motivo («el beat N de chXX quedó sin ninguno de los datos que la escaleta dejó para la pantalla…»), su `motivos_beat` y la clave `("a_pantalla", cap, beat)`. `a_pantalla_vacios` se sigue calculando igual y se devuelve (va al JSON por `armar`, al `.md` como «⚠ sin su a_pantalla» con `_por_que_falta`). El dato `a_pantalla` del ítem en la entrada no cambia (el autor lo sigue viendo; el USER de Wittenoom sigue en 018f9cc1…). Docstrings de `validar` y `llamar`. DECISIONES 2026-10-31 15:49 (1.ª línea).

**Salida en texto:** `lab/hyperframes/f65/revalida.py` → `REVALIDA.md` (entero abajo). Resumen: papel actual de Wittenoom: motivos 0 → 0, claves 0 → 0, `a_pantalla_vacios` `[]` (la vuelta de F64 ya había puesto los 6); O2_1 de F63: motivos 5 → 0 (los 5 eran `a_pantalla`: ch03 b5 D01, ch05 b9 D51, ch06 b11 D34, ch06 b12 D40, ch07 b13 D61), claves 5 → 0, los demás motivos iguales (no había otros: O2_1 ya pasaba 13/13 con el verificador en caché), `a_pantalla_vacios` igual. El juez de caché encontró los dos `pedido_md5` del raw de producción y el de `f64/sim/O2_1.json`: ninguna llamada.

### F65a Etapa A — REVALIDA: `a_pantalla` ya no es motivo de vuelta (solo lectura, 0 llamadas)

Entrada de producción de hoy (`entrada_md5` 018f9cc1b939e2afdcfad5eb5ebcc36f), `validar` de `m01e-7`; juez = caché por `pedido_md5` (raw de producción / `lab/hyperframes/f64/sim/O2_1.json`). «Antes» = la regla de F38c §A.1 reconstruida sobre el mismo `a_pantalla_vacios` (un motivo y una clave por beat sin su a_pantalla).

#### 1. Papel actual de Wittenoom (`01e_pantalla.raw.json` → `final`, m01e-7, 13 fichas)

| | antes (F38c §A.1) | después (F65a) |
|---|---|---|
| motivos | 0 | 0 |
| claves | 0 | 0 |
| motivos `a_pantalla` | 0 | 0 |
| `a_pantalla_vacios` | [] | igual |
| fichas que quedan | 13/13 | igual |
| cortadas por el verificador (caché) | [] | igual |

Claves antes: ninguna

Claves después: ninguna

Motivos después (los que siguen):
- (ninguno)

#### 2. O2_1 de F63 (`respuesta` del intento 1 de Opus medium con entrada completa)

| | antes (F38c §A.1) | después (F65a) |
|---|---|---|
| motivos | 5 | 0 |
| claves | 5 | 0 |
| motivos `a_pantalla` | 5 | 0 |
| `a_pantalla_vacios` | [('ch03', 5, ['D01']), ('ch05', 9, ['D51']), ('ch06', 11, ['D34']), ('ch06', 12, ['D40']), ('ch07', 13, ['D61'])] | igual |
| fichas que quedan | 13/13 | igual |
| cortadas por el verificador (caché) | [] | igual |

Claves antes: (a_pantalla, ch03, 5); (a_pantalla, ch05, 9); (a_pantalla, ch06, 11); (a_pantalla, ch06, 12); (a_pantalla, ch07, 13)

Claves después: ninguna

Motivos después (los que siguen):
- (ninguno)


## Etapa B — Fase 2 respeta al verificador (`f54d4ba`)

**Diff** (los 4 módulos donde `7b48ebf` quitó `juicio_autor`):
- `script_engine/pantalla_filtros.py`: `contradicciones_de(…, juicio=None)` y `contradicciones(…, juicio=None)` vuelven a aceptar `juicio` (la versión de `b9979f6`, leyendo ahora los `tokens` de `juicio_verificador` por regla); `_sin_juicio(ctx, regla, toks)` de vuelta; `no_dicho` y `spoiler` descartan los tokens de `ctx["juicio"][regla]`; `ancla_papel` llena `ctx["juicio"]` con `(b.get("juicio_verificador") or {}).get("tokens") or {}`. Una coincidencia cuyo token ya juzgó «pasa» el verificador no corta ni marca en Fase 2. Fase 2 nunca llama al verificador.
- `script_engine/pantalla_entrada.py` l.142: el bloque del papel lleva `juicio_verificador` tal como viene en la ficha.
- `script_engine/pantalla_colocar.py` l.196: el meta del callout lo lleva al plan.
- `script_engine/gfx_guion.py` l.275/283 (eventos de callouts y recortes) y l.493 (chequeo 5: `contradicciones(…, juicio=(e.get("juicio_verificador") or {}).get("tokens"))`).

**Salida en texto:** `lab/hyperframes/f65/fase2_juicio.py` → `FASE2_JUICIO.md` (entero abajo). Resumen: de las 13 fichas, 4 llevan `juicio_verificador` (D108 no_dicho «Australia», Q25 spoiler «2», D01 spoiler «3», D23 contradice «30»/«2024»); sin juicio Fase 2 cortaría D108 (`no_dicho`) y Q25 (`spoiler`) y el chequeo 5 marcaría D23 («500 personas vs 30»); con juicio las 4 pasan y el chequeo 5 no marca nada; las otras 9 no cambian. El handoff decía «las 7 que el verificador salvó (D108, Q25, D23, D01 y las de la vuelta)»: las tres de la vuelta (D34, D40, D61) no tuvieron marcas en el papel, así que no llevan `juicio_verificador` y pasan igual con o sin él; las salvadas son 4. D01 (spoiler «3» por ch04 [14], otro cap) pasa en Fase 2 aun sin juicio porque el `spoiler` de Fase 2 mira solo las oraciones posteriores del mismo cap. Las palabras con tiempos se sintetizaron de la narración (no hay voz para este guion: PARADA): `lectura` corrió con esos tiempos y no cortó ninguna.

### F65a Etapa B — FASE2_JUICIO: las 13 fichas del papel actual por el camino de Fase 2, con y sin `juicio_verificador`

Papel `m01e-7` (claude-opus-5-5), entrada de hoy; palabras con tiempos sintetizadas de la narración (0.34 s por palabra, sin escenas: `lectura` corre con esos tiempos, no con la voz real). Fase 2 no llama al verificador: solo lee `juicio_verificador.tokens` de la ficha.

| cap | beat | ficha | estilo | juicio_verificador (regla, tokens) | validar_papel SIN juicio | validar_papel CON juicio | chequeo 5 SIN juicio | chequeo 5 CON juicio | cambia |
|---|---|---|---|---|---|---|---|---|---|
| ch01 | 1 | D108 | normal | ['no_dicho'] {'no_dicho': ['Australia']} | **no_dicho**: la voz lo dice en la oración ancla o en una vecina: ['Australia'] | pasa | — | — | **sí** |
| ch02 | 2 | Q25 | cita | ['spoiler'] {'spoiler': ['2']} | **spoiler**: la voz lo dice en una oración posterior del cap: ['2'] | pasa | — | — | **sí** |
| ch02 | 3 | D83 | normal | — | pasa | pasa | — | — | no |
| ch03 | 4 | D02 | normal | — | pasa | pasa | — | — | no |
| ch03 | 5 | D01 | normal | ['spoiler'] {'spoiler': ['3']} | pasa | pasa | — | — | no |
| ch03 | 6 | D115 | normal | — | pasa | pasa | — | — | no |
| ch04 | 7 | Q19 | cita | — | pasa | pasa | — | — | no |
| ch04 | 8 | D102 | normal | — | pasa | pasa | — | — | no |
| ch05 | 9 | D51 | normal | — | pasa | pasa | — | — | no |
| ch05 | 10 | D23 | papel | ['contradice'] {'contradice': ['30', '2024']} | pasa | pasa | 500 personas vs 30 («Nueve meses después del diagnóstico, Daniel Écija murió en  | — | **sí** |
| ch06 | 11 | D34 | normal | — | pasa | pasa | — | — | no |
| ch06 | 12 | D40 | normal | — | pasa | pasa | — | — | no |
| ch07 | 13 | D61 | papel | — | pasa | pasa | — | — | no |

- Fichas con `juicio_verificador`: 4 (D108, Q25, D01, D23); de ellas, sin juicio Fase 2 cortaría 2 y marcaría en el chequeo 5 1; con juicio pasan 4 y el chequeo 5 marca 0.
- Fichas sin juicio: 9; ninguna cambia entre las dos columnas (OK).
- Lo que corta en ambas columnas es independiente del juicio (p. ej. `lectura` con tiempos sintéticos, o candado): []


## Tests

Adaptación por subagente (paralelo), sin tocar producción ni lab, sin API. Suite del papel (f64, f36c, f37a, f38a_m01e, f38a_voz, f38c, f38d, f38e_c, f38e_d, f38e_e, f40, f37b, f39): **106 verdes + 6 saltados** (los saltados: sin Vajont en `data/`, previos). Rápida (hook) verde en los dos commits.

- `test_module_f64.py` (+1, 18): `test_b_fase2_respeta_juicio_verificador` (§2.3): la ficha D1 «LO QUE PASÓ · El peor desastre industrial de Australia» anclada a la oración vecina de «Wittenoom, Australia Occidental…» cae en `validar_papel` por `no_dicho` («la voz lo dice en la oración ancla o en una vecina: ['Australia']») sin juicio y pasa con `juicio_verificador = {regla: [no_dicho], tokens: {no_dicho: [Australia]}}`; con el token bajo otra regla vuelve a caer. Chequeo 5: `contradicciones("COTA 720 metros", voz «setecientos quince metros»)` marca sin juicio y da `[]` con `juicio={"contradice": ["715"]}`; con otra regla sigue marcando.
- `test_module_f38c_papel.py`: **borrado** `test_a1_papel_f38b_da_dos_motivos` (exigía el motivo de `a_pantalla`) y el helper `_a_pantalla_motivos`; **nuevo** `test_a1_a_pantalla_vacios_sigue_en_la_salida_sin_ser_motivo` (`a_pantalla_vacios == [("ch06", 11), ("ch07", 13)]`, ningún motivo ni clave de a_pantalla); adaptados `test_a1_d128_en_b11_no_da_motivo_por_d192` y `test_a2_contradicciones_estructura_y_frases` (`_sin_juicio` existe otra vez; `juicio={"contradice": ["715"]}` → `[]`).
- `test_module_f38a_m01e.py::test_a1_lo_del_intento_1_sobrevive_al_reintento_parcial`: con el intento 1 de F37 el único motivo que queda es Q15 (vuelve, sin beat) → `beats_m == []` → `llamar` cierra «sin beat» con 1 POST; la fusión parcial se mide con `fusionar` + `validar` directos sobre `[("ch05", 8), ("ch07", 13)]`. **Cobertura perdida (declarado):** el camino de `llamar` con dos vueltas sobre estos datos; sigue cubierto por `f38d::test_2` y `f64::test_f`.
- `test_module_f38d_vueltas.py::test_2_sin_progreso_cierra`: claves esperadas `{("caben", "Q50", "ch05", 8, None), ("pico", "ch05", 8)}` + `a_pantalla_vacios == [("ch05", 8)]`; 1 vuelta, 2 POST, «sin progreso», igual.
- `test_module_f40_gancho.py`: `test_4_no_dicho_en_el_gancho_deja_la_coincidencia_en_dichos` → `test_4_no_dicho_en_el_gancho_respeta_el_juicio_del_verificador` (con `ctx["juicio"] = {"no_dicho": ["6"]}` devuelve None; con juicio de otra regla sigue cortando).
- Sin tocar: `test_module_f37b_colocar.py` (10 verdes).

Observación del subagente, previa a F65a (no se tocó): `pantalla_filtros.contradicciones("Más de 500 muertos", ["Murieron durante casi treinta años."])` devuelve «500 personas vs 30»: «Murieron» activa la magnitud personas y «treinta» (años no es unidad) cae en la rama «cifra sin unidad después de la magnitud». Es el mismo falso positivo que marcó D23 en el papel («500 vs 30»), que ahora el juicio del verificador tapa en Fase 2; el filtro en sí sigue igual.


## Lo que queda abierto

1. **El `.md` y el JSON siguen avisando ⚠ «sin su a_pantalla»**, pero ya nadie lo convierte en acción: queda para la QA del papel (DECISIONES 15:49, 3.ª línea: Omar revisa con una interfaz y puede pedir «sugerir» otra ficha por beat).
2. **El papel actual de Wittenoom (m01e-7, 13/13) se escribió con la regla vieja**: la vuelta puso D01, D51, D34, D40 y D61 porque `a_pantalla` era motivo. Con F65a una corrida nueva no los obligaría. No se re-corrió (cero llamadas): la versión que Omar lee y aprueba es la de F64, con esas 5 fichas técnicas; si las quiere fuera, hay que re-correr el papel (≈ US$ 1,3) o editarlas con `fase2b --plan-edit`.
3. **Fase 2 respeta solo los tokens que el verificador vio en el papel.** Si Fase 2 mueve la ficha a otra oración (`lectura`) y aparece una coincidencia con un token nuevo, esa sí corta (como antes con `juicio_autor`). Y `spoiler` en Fase 2 sigue mirando solo el cap (D01 pasa por eso, no por el juicio).
4. **`FASE2_JUICIO.md` corre con tiempos sintéticos** (no hay voz): `lectura` y las escenas reales pueden cortar otra cosa cuando se genere la voz; lo que mide la tabla es solo el efecto del juicio.
5. **La PARÁ sigue:** el papel no está aprobado; voz, fotos y `fase1_5` no corrieron.

## Veredicto de revisor-handoff (íntegro)

**VEREDICTO: CUMPLE CON OBSERVACIONES**

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | `validar` no genera motivo, `motivos_beat` ni clave de a_pantalla | OK | `git diff 5225edf 2c00efa -- script_engine/m01e_pantalla.py`: se borra el bloque `for a in a_pantalla_vacios` en motivos, motivos_beat y claves. |
| 2 | `a_pantalla_vacios` se sigue calculando y devolviendo; va al JSON y al .md como ⚠ | OK | El cálculo y el return quedan intactos. El test `f38c::test_a1_a_pantalla_vacios_sigue_en_la_salida_sin_ser_motivo` pasa. REVALIDA.md muestra `a_pantalla_vacios` de O2_1 con 5 beats. No leí el render ⚠ del .md; no se tocó. |
| 3 | La entrada del autor no cambió (md5 018f9cc1…) | OK, con una salvedad | El diff de A no toca `entrada` ni `pedido`. Mi propio intento con vocabulario `[]` dio otro md5 (d1555dc3…), porque no usé `vocabulario_clima()`. Al re-correr `revalida.py`, su cabecera de REVALIDA.md sigue diciendo `entrada_md5` 018f9cc1b939e2afdcfad5eb5ebcc36f, con el archivo sin cambios. |
| 4 | `revalida.py` y `fase2_juicio.py` sin llamadas al modelo; el juez es de caché y PARA si falta el `pedido_md5` | OK | `revalida.py:30-45` (juez_cache con `SystemExit("PARÁ…")`). Ningún `_post` ni `verificar` real. Los re-corrí y los .md salieron idénticos (`git status` sin cambios en esos archivos). |
| 5 | Tablas coinciden con el reporte (Wittenoom 0→0; O2_1 5→0 motivos y claves; 13/13) | OK | REVALIDA.md y FASE2_JUICIO.md reproducidos. |
| 6 | `pantalla_filtros` lee `juicio` como `b9979f6`, pero desde `juicio_verificador.tokens` | OK | Diff de B: `contradicciones_de/contradicciones` con `juicio=`, `_sin_juicio` de vuelta, `no_dicho` y `spoiler` filtran con `ctx["juicio"]`. `ancla_papel` llena `ctx["juicio"]` con `(b.get("juicio_verificador") or {}).get("tokens") or {}`. Equivale a lo que 7b48ebf^ quitó. |
| 7 | `pantalla_entrada`, `pantalla_colocar` y `gfx_guion` pasan `juicio_verificador` donde 7b48ebf quitó `juicio_autor` | OK | Los 5 puntos coinciden con los que 7b48ebf quitó: entrada l.142, colocar l.196, gfx_guion l.275/283 y el chequeo 5 (l.493). El chequeo 5 pasa `.get("tokens")`. `grep` no encuentra `juicio_autor` en los .py de `script_engine` (solo en `__pycache__` viejos). |
| 8 | Fase 2 no llama al verificador | OK | El diff de B no importa `pantalla_verificador`. Solo lee tokens. |
| 9 | Nada de Wittenoom en el código | OK | `grep` en `script_engine`: solo menciones previas en docstrings (`m01e_pantalla.py:171`, `name_matching.py:8`). El diff de A y B no agrega ninguna. |
| 10 | Dos commits con prefijo `feat(m01e): F65a …`; `main` intacta | OK | `2c00efa` Etapa A y `f54d4ba` Etapa B sobre `5225edf`. `main` = 43f528a. |
| 11 | Suite verde | OK | Corrí f64, f37a, f37b, f38a_m01e, f38c_papel, f38d, f38e_c y f40_gancho: 69 passed, 3 skipped. El reporte dice 106 verdes y 6 saltados en la suite completa del papel; no la corrí entera. |
| 12 | Lo viejo se borra con sus tests | OK | Se borra `test_a1_papel_f38b_da_dos_motivos`, con su helper `_a_pantalla_motivos`, y queda dicho en el docstring de f38c. Se adaptan f38a, f38d y f40. Se agrega `test_b_fase2_respeta_juicio_verificador` en f64. |
| 13 | Papel sin aprobar y PARADA | OK | No hay voz ni fotos nuevas. El reporte lo declara en «abierto» 5. No encontré flag de aprobación en `01e_pantalla.json`. |
| 14 | `F65a_REPORT.md` con «lo que queda abierto» | OK | Existe, sin trackear. «Abierto» está en las líneas 101-107. La sección «Veredicto» es esta. |
| 15 | `ESTADO_SESION.md` actualizado | NO VERIFICABLE | Sin cambios en el working tree. El pedido lo deja para después de este veredicto. |
| 16 | Subagentes en paralelo; CERO llamadas | NO VERIFICABLE | No hay rastro en el repo de los subagentes. La ausencia de llamadas solo se ve en el código y no en el gasto. |

Fuera de alcance: ninguno en los commits. Los 16 archivos tocados son los declarados: 5 de `script_engine`, 4 tests, 2 stickers y 4 de lab. En el working tree siguen `DECISIONES.md`, `diag_234_cap4.py` y `f28a.log` modificados, pero ya estaban así antes de la tanda y no están en los commits.

Observaciones:
1. «7 salvadas» del handoff son 4 con `juicio_verificador` (D108, Q25, D01, D23). Las tres de la vuelta (D34, D40, D61) no tuvieron marcas, así que pasan con o sin juicio. Aceptable: lo respaldan FASE2_JUICIO.md y los datos de F64.
2. D01 pasa en Fase 2 aun sin juicio porque el `spoiler` de Fase 2 mira solo el cap. La fila de D01 no prueba el juicio. Aceptable y declarado. Los casos que sí lo prueban son D108, Q25 y D23.
3. Los tiempos de `fase2_juicio.py` son sintéticos (0,34 s por palabra, sin escenas). Mide solo el efecto del juicio, no la `lectura` real. Aceptable y declarado en «abierto» 4.
4. `test_module_f38c_papel` con cambios de A y B fue todo al commit B. Esto rompe «suite verde en cada commit» solo si ese test falla en A. No lo verifiqué commit por commit. Es un desvío menor de proceso y no afecta el estado final.
5. Hay un efecto que conviene que Omar tenga presente. El papel de Wittenoom que va a revisar se escribió con la regla vieja y trae 5 fichas técnicas forzadas (D01, D51, D34, D40, D61). El reporte lo declara en «abierto» 2.

Riesgos que el contrato no cubre:
- Un token nuevo que aparezca tras mover la ficha en Fase 2 sí corta, porque el juicio solo cubre lo que el verificador vio en el papel.
- La validación de Fase 2 con voz y escenas reales no se probó, porque no hay voz.
- La regla ya no obliga a cubrir `a_pantalla`. El único aviso es el ⚠ del .md, y nadie lo lee automáticamente.

### Adenda de CC
- **Req. 11:** los 106 + 6 son los 13 archivos de la suite del papel (los 8 del revisor + f36c, f38a_voz, f38e_d, f38e_e, f39_fase1), corridos juntos antes de los dos commits.
- **Req. 16:** las llamadas al modelo pasan todas por `claude_helpers._post`; los dos scripts de lab no lo importan y el juez de caché para con `SystemExit` si falta un `pedido_md5`. `data/cost_history.json` sigue con fecha del 30-oct.
- **Obs. 4:** cierto: en el estado `2c00efa` el test viejo `f38c::test_a1_papel_f38b_da_dos_motivos` fallaría (exigía el motivo que A borró) y `test_a2_contradicciones…` también (aseveraba que `_sin_juicio` no existía, hasta B). La suite que corre el hook (f25c, f24, f21) estuvo verde en ambos commits. Declarado como desvío de proceso.
- **Obs. 5 / riesgo 3:** compartidos; están en «lo que queda abierto» 1 y 2 y en el mensaje a Omar en ESTADO.
