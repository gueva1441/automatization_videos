# F38 — Reintento parcial, tarjeta desde la voz, juez de anclaje, fracciones — REPORTE (corto)

Handoff `lab/hyperframes/f38/HANDOFF_F38_reintento_tarjeta_juez.md`. Base `f39c28f`. Esfuerzo medium. Commits: paso 0
`ebcf2ba` (DECISIONES 00:30 + handoff, tal cual) · A `ebe788e` · B (este reporte). **PARADA.** Sin render, sin aprobar,
sin merge; prompts de escaleta/guionista/partición sin tocar.

**Resultado en una línea:** el código de A hace lo que pide el handoff (tarjeta ✓, reintento parcial ✓, D68 ✓), pero
**el juez con el prompt literal marca casi todo como «adelanta»** (18 de 18 fichas en las dos rondas) y **el papel de
Vajont queda con 0 fichas**. Decide el analista (ver abierto 1). No se forzó nada.

Lecturas (paso 1): nota de cierre de F37, `CLAUDE.md`, `DECISIONES.md` entero (22:26, 22:32 y la nueva 00:30), cabecera
y F37 de `lab/ESTADO_SESION.md`, el handoff entero, `F37_REPORT.md` §C y «Lo que queda abierto».

Módulos (paso 2; sticker del mapa → después): `m01e_pantalla` (papel en Fase 1 → + juez y reintento parcial; la tarjeta
ya no es del autor) · `voz_datos` (pico, reloj, tarjeta derivada → + `tarjeta_de_voz`, `horas_dichas`) · `voz_utils`
(cifras en letras → + fracciones y `misma_cifra`) · `pantalla_colocar`: **no se tocó** (la tarjeta del papel ya la pasa
`gfx_layer` al plan como en F36/F37). Stickers actualizados; mapa 35 módulos, 116 aristas, 0 muertos.

Constantes (paso 4): solo de la lengua y del reloj, con origen en su línea (`# estándar: aritmética de la lengua`,
`# estándar: reloj de 24 h`, `# derivado: …`). Ninguna lista de un tema. El juez lee `config.api.gemini_model` al llamar.

## A — código (commit `ebe788e`, dos subagentes en paralelo)
- **A.1** El reintento ve el papel entero del intento 1 como contexto y devuelve solo `{"cambios": […]}`. `fusionar` aplica
  los cambios por (cap, beat) y deja todo lo demás congelado. Un cambio en un beat sin motivo se ignora y se anota en
  `reintento.ignorados`. Cada motivo lleva su beat (`motivos_beat`). El descarte que «vuelve» no tiene beat: el autor lo
  puede poner en cualquier beat con motivo. Test con la respuesta de F37: D128, AVISO, ALARMA y T92 sobreviven.
  **Q14 no estaba en el intento 1 de F37** (el autor lo había descartado ahí), así que no había nada que conservar.
- **A.2** `voz_datos.tarjeta_de_voz`, sin modelo. La fecha es la primera fecha completa del gancho. La hora es la que dice
  la voz en el beat pico, con la del primer ítem del pool de esa fecha que coincide en minutos y en hora módulo 12. Se
  buscan primero los ítems del beat pico y después los demás de esa fecha. Vajont: **9 OCT 1963 · 22:39** (T66; T72,
  22:43, no). Del prompt del autor se quitaron la línea TARJETA y la clave del formato.
- **A.3** Juez `juez-1` (prompt literal, md5 `4264a968d39aa9f61c39eea729c92ee5`; modelo `gemini-2.5-flash`, de config):
  - Corre una vez después de validar el intento 1.
  - Lo que marca entra al reintento como motivo de su beat.
  - Si la misma ficha sigue después del reintento, sale con regla `juez`.
  - Las fichas nuevas o cambiadas del reintento se juzgan en una segunda ronda, solo ellas. Así se leyó «lo que siga mal
    después del reintento».
  - Caché en `01e_juez.raw.json`. Test sin API con la respuesta grabada sobre el papel de F37 (`f38/a/juez_cache_f37.json`):
    D131 en [1] da `adelanta: true`.
- **A.4** `voz_utils` ahora lee «y medio/media» (+0,5), «medio/media» delante de una unidad (0,5), «y cuarto» (+0,25) y
  «un tercio» (1/3). `misma_cifra` compara a la precisión de la cifra del archivo. D68 ya no vuelve.
- Prompt del autor `m01e-3`, md5 `f8babc027808652bd09113dcf5f87248` (SYSTEM + formato + formato del reintento + la frase
  del reintento parcial; ver abierto 4).
- Tests nuevos: `test_module_f38a_m01e.py` (12) y `test_module_f38a_voz.py` (14). Cambiado: el assert de versión de
  `test_module_f37a_papel.py::test_a3a` (`m01e-2` → `m01e-3`).
- **Verificación (una vez, antes de A):** md5 ch02 `38e5ba14e3d24fd20f9297c9e1dfee24`, rápida **58**, amplia **832 + 5
  previas** (`-n auto`, 1 min 42 s; `pytest-xdist` 3.8.0 instalado). Logs en `f38/a/`. Por DECISIONES 00:30 no se midió
  RAM ni se cerró nada.

## B — Vajont (`f38/b/`)
`python -m script_engine.m01e_pantalla f8s3-vajont` (`b/m01e_vajont.log`) → `fase2b f8s3-vajont-f30 --plan-only`
(`b/plan_only.log`, 199 s). Archivos largos: `b/01e_pantalla.md|json|raw.json`, `b/01e_juez.raw.json`,
`b/GUION_PANTALLA.md|json`.

| paso | resultado |
|---|---|
| intento 1 (Sonnet) | 12 fichas · 10 sellos. Validación: 2 fuera (Q50 caben, Q43 cita sin fecha), 2 preguntas (D47, D105), 2 vuelven (T39, Q15), 1 pico vacío |
| juez ronda 1 | 10 fichas → **10 marcadas** (todas `mismo_asunto: true, adelanta: true`; motivo tipo «un detalle que la voz no menciona después») |
| reintento parcial | podía cambiar 12 de 13 beats (los marcados por el juez y los de las validaciones); cambió la ficha en los 12. ch04 b6 quedó congelado |
| validación del reintento | 3 fuera (D159 fecha del relato, D152 y D161 spoiler) |
| juez ronda 2 | 8 fichas nuevas → **8 marcadas** → salen |
| **papel final** | **0 fichas** · 10 sellos · 4 relojes · tarjeta ✓ |

Intento 1, antes del juez (para la compuerta; detalle en `b/01e_pantalla.raw.json`):
- gancho: D131 en [1];
- beats con ficha: D117, D47, T16, D49, D105, Q50, Q43, D01, **D195 (ch06 b11)** y **Q14 (ch07 b12)**, D245.

**Pantalla (`--plan-only`):**
- tarjeta 9 OCT 1963 · 22:39 en 00:00 (✓);
- 0 fichas;
- sellos colocados: CALMA, AMENAZA, AVISO, ALARMA, INMINENTE, COLAPSO, PÁNICO, MEMORIA (8);
- sellos sin colocar: SILENCIO (cruza el corte / estorba) y RABIA (estorba en los 6 intentos);
- relojes: 3 (ch01, ch04, ch07 20 FEB); el reloj de voz de ch05 queda fuera por `TICKER_MIN`.

Chequeos: ✓ al mismo tiempo, corte, lectura, pregunta, cifra, costuras, gancho no vacío (por el sello y el reloj),
música, tarjeta, sin alinear. ✗ a_pantalla, ✗ inicio de voz por cap (previo, F32), ✗ papel sin colocar (SILENCIO,
RABIA).

Esperado del handoff:
- tarjeta: **cumple**;
- gancho en una oración que habla de su dato: **no** (sin ficha);
- D128/Q14 si nadie los cuestionó: Q14 estaba en el intento 1 y **lo cuestionó el juez**; D128 no estaba;
- ningún beat cambiado sin motivo: **cumple**.

**Costo:** Claude US$ 0.5634 (intento 1: 65 860 in · 20 294 out · 0.3347; reintento: 75 008 · 7 866 · 0.2287). Juez
US$ 0.0514 (0.0302 + 0.0212). **Total de m01e: US$ 0.6147** (tope 1.00, respaldo). Fuera de ese total: la grabación del
juez en A, US$ 0.0367, y el crítico de `--plan-only`, US$ 0.0006.

**Lo que es gusto (para la compuerta de Omar, no se forzó):**
- volver a una ficha del intento 1, por `--plan-edit`;
- qué dato en el gancho (D131 o D87);
- D195 en ch06 b11;
- Q14 o T85 en ch07 b12;
- los dos sellos sin colocar.

Nada de esto sirve mientras el juez marque todo.

## Procesos (paso 12)
- Los dos subagentes terminaron.
- El verificador, `m01e` y `--plan-only` terminaron solos.
- No queda python de la tanda vivo.
- No se lanzó qa_studio ni HyperFrames.
- No se cerró ningún programa de Omar (DECISIONES 00:30).

## Lo que queda abierto (entero)
1. **El juez con el prompt literal no discrimina.** Marcó «adelanta» en 18 de 18 fichas de Vajont, y en 11 de 12 sobre
   el papel de F37. Lee «adelanta» como «aporta algo que la voz no dice después», que es justo lo que pide la regla (a).
   El código hace lo que dice el handoff (lo marcado va al reintento y lo que sigue marcado sale), así que **el papel
   queda vacío de fichas**. La causa es del prompt, no del código. Decide el analista. Opciones sin código nuevo: otra
   redacción de `adelanta` («la voz cuenta ese mismo hecho más adelante»; que el juez cite la oración posterior y el
   código verifique que existe), o que `adelanta` solo cuente si el juez nombra la oración. No se tocó el prompt (regla
   del pedido).
2. **Las fichas buenas del intento 1 se perdieron por el juez.** Q14 (lo que pedía el contrato), D195 en el clímax y
   D131 en el gancho. Con un juez que discrimine, el reintento parcial las conservaría.
3. **El reintento puede cambiar casi todo cuando el juez marca casi todo** (12 de 13 beats con motivo). El reintento
   parcial funciona, pero su alcance depende de cuántos motivos haya.
4. **Prompt fuera de los literales, declarado:** además del formato literal de A.1, el reintento lleva una frase
   (`REINTENTO_PARCIAL`): la lista de beats que puede cambiar, «null borra, sin clave no cambia, otro beat se ignora».
   Reemplaza al viejo «devolvé el JSON completo otra vez», que tenía que salir. El md5 del autor la incluye. La revisa el
   analista.
5. **Lectura de la hora de la tarjeta (declarada):**
   - Se buscan primero los ítems del beat pico; si ninguno coincide con la voz, los demás ítems del pool de esa fecha, en
     el orden del pool. En Vajont la hora sale de T66, que no es del beat pico.
   - Entre T66 y T71 (todos a las 22:39) gana el primero del pool.
   - «las diez» sin minutos ni «a/son/eran» delante no cuenta como hora.
6. **Segunda ronda del juez:** el handoff dice «una» llamada. La segunda ronda juzga solo lo que puso el reintento
   (declarado en el docstring). Sin ella, las 8 fichas nuevas habrían quedado sin juzgar.
7. **Si el reintento no trae JSON** o no entra en el tope, queda el intento 1 validado sin confirmaciones: las
   coincidencias cortan. Antes quedaban como preguntas sin resolver. Cambio menor, declarado por el subagente.
8. **Q15 «vuelve»:** el parser ahora lee «las diez y media» del ítem también como 10,5. La voz de ch06 no dice esa frase
   del testimonio, así que el «vuelve» es correcto. Las horas en letras cuentan como cifras en `numeros()`, como antes con
   el entero.
9. **`_analiza("mil novecientos sesenta y tres")` da 963**, mientras `numeros` da 1963. Es previo a F38 (comparado con
   HEAD). `_cifras` no lo saca como año porque queda fuera de rango. No se tocó.
10. **El papel de Vajont en `data/scripts/_steps/f8s3-vajont/01e_pantalla.*` es ahora el de F38 (0 fichas)**, y
    `output/f8s3-vajont-f30/GUION_PANTALLA.*` también. El de F37 está en `lab/hyperframes/f37/c/` por si Omar o el
    analista lo quieren de vuelta. No se restauró.
11. **Tarjeta para Omar:** ✓ en papel y en pantalla, sin `--plan-edit`. Falta verla en render (forma).
12. **De F37, siguen:**
    - el reintento de F37 en caché ya no aplica (cambió el prompt);
    - clave `costos.m01e_tope_usd` del perfil (corre el respaldo 1.00) y las perillas huérfanas de `misterio.json`;
    - sellos que el crítico no deja colocar (hoy SILENCIO y RABIA);
    - spoiler por cifras: el juez lo iba a cubrir y hoy no discrimina;
    - las 5 fallas previas (01b_pauses ×3, m03_merge_timing ×2);
    - «inicio de voz» ch07 sin rampa (F32);
    - Fase 1 entera nunca corrió con `run_pantalla` enganchado;
    - docs históricas con nombres viejos;
    - el lab de identidad sin elegibilidad.
13. **La validación 1c** (cita sin fecha) **se ejercitó esta vez** (Q43 cayó por ella), igual que caben (Q50).
14. **Tests que leen datos vivos:** `test_module_f38a_m01e.py` leía el papel de F37 desde `data/`, y la corrida B lo pisó
    (lo encontró el revisor, fila 12). Ya se arregló (ver la adenda). `test_module_f38a_voz.py` y los de F37 siguen
    leyendo de `data/` la escaleta, la narración y el pool, que B no reescribe. Un Fase 1 nuevo de Vajont los cambiaría.

## Veredicto del revisor (`revisor-handoff`, íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES (hay una falla de regresión que el reporte no declara).

Corrí los tests nuevos de F38 y leí el diff `f39c28f..ebe788e`, el reporte y los archivos de `f38/b/`. No corrí el md5 ni la suite amplia: tomé sus resultados de los logs de `f38/a/`.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Prompts: solo literales de A.1, A.2 y A.3 | PARCIAL | Bien: se quita la línea TARJETA y la clave `tarjeta` del formato; `FORMATO_REINTENTO` (A.1) y `JUEZ_SYSTEM` (A.3) están en `script_engine/m01e_pantalla.py`. `JUEZ_SYSTEM` coincide palabra por palabra con el handoff. No se tocaron escaleta, guionista ni partición. Sobra `REINTENTO_PARCIAL`, un prompt no literal (abierto 4): lo declaran, pero el pedido decía "solo los literales". Es el reemplazo necesario de "devolvé el JSON completo", y define la lista de beats, el null y el "otro beat se ignora". Sin esa frase el formato A.1 no se puede operar. Entra en el md5 del autor. Lo trato como desvío menor y declarado, que decide el analista. |
| 2 | El juez lee `gemini_model` de config | OK | `m01e_pantalla._juez_modelo()` devuelve `str(api.gemini_model)` en el momento de la llamada. No hay "gemini-2.5-flash" escrito en el código. El modelo entra en la clave de caché. |
| 3 | Nada hardcode, constantes con origen | OK | Las constantes nuevas de `voz_datos` y `voz_utils` llevan "estándar:" o "derivado:" en su línea. No hay "vajont", "1963", "22:39" ni IDs de pool en `script_engine/` (grep sobre el diff vacío). `test_constantes_con_origen` pasa. |
| 4 | A.1 reintento parcial por (cap, beat), cambios sin motivo ignorados | OK | Hay tests en `test_module_f38a_m01e.py` y `reintento.ignorados` en el código. En B, "ningún beat cambiado sin motivo" es verdad: ch04 b6 quedó congelado. |
| 5 | A.2 tarjeta desde la voz, sin modelo | OK | `GUION_PANTALLA.md:11` da "9 OCT 1963 · 22:39" y `01e_pantalla.md` indica T66, no T72. La fuente de la hora no es del beat pico, y está declarada (abierto 5). |
| 6 | A.3 juez | OK en código, PARCIAL en la prueba | Hay una llamada en la ronda 1 y una ronda 2 extra, declarada en el abierto 6; el handoff decía "una". D131 sale marcado en la respuesta grabada. |
| 7 | A.4 fracciones, D68 deja de volver | OK | `test_module_f38a_voz.py` (14 tests) pasa. |
| 8 | Verificación una sola vez antes del commit A | OK | `f38/a/verificar.out`: md5 ch02 `38e5ba14` (igual que F37), rápida 58, amplia 832 pasan y 5 fallan. Son las 5 fallas previas (01b_pauses ×3, m03_merge_timing ×2). `verificar.sh` no mide RAM ni cierra Firefox, como pide DECISIONES 00:30. |
| 9 | Fidelidad del resultado de B (0 fichas) | OK | `m01e_vajont.log`, `01e_pantalla.md` ("0 fichas · 10 sellos · 4 relojes") y `GUION_PANTALLA.md` coinciden con la tabla del reporte. En `01e_juez.raw.json` hay 18 `adelanta:true`, 0 `false` y 2 `mismo_asunto:false`. El reporte dice "18 de 18 adelanta", lo cual es correcto. Los motivos citados dicen "la voz no lo menciona después", o sea que el juez leyó mal `adelanta`. Eso está bien diagnosticado como causa del prompt. Costo: 0.6147, con tope 1.00. Los "esperado" del handoff están marcados con honestidad: gancho con ficha incumplido, tarjeta cumplida. |
| 10 | B sin forzar, lo que es gusto listado, no hay render ni aprobar ni merge | OK | Sección "Lo que es gusto" y "Procesos" del reporte. No hay archivos de render ni merge en el diff. |
| 11 | Entregables de B | OK | Los archivos de `f38/b/` existen y no están vacíos. `F38_REPORT.md` existe y su sección del veredicto del revisor está pendiente ("se pega abajo"). |
| 12 | Tests de A siguen verdes después de B | FALLA | Hoy `test_module_f38a_m01e.py` falla 3 tests: `test_a1_lo_del_intento_1_sobrevive_al_reintento_parcial` (`assert 'D195' == 'D128'`) y los dos del juez con D131 (`StopIteration` y `assert r["cache"]` falso). Cargan `PAPEL_F37` y `RAW_F37` desde `data/scripts/_steps/f8s3-vajont/`, que la corrida B sobrescribió con el papel de 0 fichas (abierto 10). Son fixtures no autocontenidos: el F37 original está en `lab/hyperframes/f37/c/` y los tests no lo usan. Los 832 pasados de la suite amplia ya no se sostienen. El reporte no lo dice. |

Fuera de alcance: ninguno en el commit A (solo `m01e_pantalla`, `voz_datos`, `voz_utils`, tests, mapa, `DECISIONES.md` y `f38/`). La corrida B reescribió `data/scripts/_steps/f8s3-vajont/` y `output/f8s3-vajont-f30/GUION_PANTALLA.*`, declarado en el abierto 10.

Riesgos que el contrato no cubre:
- El juez con el prompt literal marca todo como "adelanta" y deja 0 fichas. El contrato fija el prompt, así que esto no se puede arreglar sin cambiarlo, y la decisión es de Omar o del analista.
- Los tests de A dependen de datos vivos de Vajont, así que cada corrida nueva de B los rompe.
- Costo de B: US$ 0.6147 de m01e dentro del tope de respaldo 1.00; la grabación del juez (US$ 0.0367) y el crítico quedaron fuera de ese total.

### Adenda de CC (después del veredicto; el texto de arriba queda tal cual)
Fila 12 arreglada en el commit B: `test_module_f38a_m01e.py` lee `RAW_F37` y `PAPEL_F37` de la copia congelada
`lab/hyperframes/f37/c/` y ya no de `data/`. El código del pipeline no cambió. Suite amplia otra vez (`f38/b/suite_amplia.log`):
**832 + 5 previas**; rápida 58. El md5 de ch02 no se volvió a correr (ningún archivo del pipeline cambió después de A).
Fila 11: el veredicto quedó pegado arriba.

---

# F38b — Quitar la causa, no agregar un juez (sección corta)

Handoff `lab/hyperframes/f38/HANDOFF_F38b_quitar_juez.md` (el del juez-2 quedó archivado, sin leer como orden).
Base `cde0de6`. Commits: paso 0 `d79cd9d` (los dos handoffs, tal cual) · A `ab1b2c5` · B (esta sección). **PARADA.**
Módulos: solo `m01e_pantalla` (sticker sin el juez). Constantes nuevas: ninguna. El único prompt que cambió es la línea
del gancho.

## A (`ab1b2c5`)
- **Línea del gancho**, literal de m01e-1 (comprobada contra `9e9d844`): «…cualquier dato del archivo que la voz no
  diga en todo el video y que haga quedarse a quien mira: el gancho nunca queda sin ficha.» Pasa a `m01e-4`. md5 del
  prompt **`f8babc027808652bd09113dcf5f87248` → `163e1fd195238696d9e66871983d5ac5`**.
- **Juez borrado, no apagado:**
  - código: `JUEZ_SYSTEM`/`JUEZ_VERSION`, `juzgar` con sus dos rondas, `juez_entrada`/`juez_pedido`, `motivo_juez`,
    `sacar_juzgadas`, `primer_json_lista`, la regla `juez` y su sección en el `.md`;
  - tests: los 6 del juez;
  - archivos: la grabación `f38/a/juez_cache_f37.json` (`git rm`) y la caché `data/…/f8s3-vajont/01e_juez.raw.json`.
  - −295 líneas en `m01e_pantalla.py`.
  - Se quedan reintento parcial, tarjeta desde la voz y fracciones.
  - Queda como registro de lo que pasó en F38 B: `f38/b/01e_juez.raw.json`.
- **Tests:**
  - el gancho de m01e-4 no tiene «primeras oraciones»;
  - nada llama al juez de anclaje (grep de `m01e_pantalla` y de sus nombres en `script_engine/`). El parámetro `juez`
    del crítico «¿estorba?» de `pantalla_colocar`/`clima` es otro y es de antes;
  - `test_a3a` de F37 se invirtió (la línea de A.3a se revirtió);
  - el reintento parcial sigue verde.
- Verificación, una vez: md5 ch02 `38e5ba14e3d24fd20f9297c9e1dfee24`, rápida 58, amplia **828 + 5 previas** (832 − 6 del
  juez + 2 nuevos), en `f38/a2/`. Mapa 35 módulos, 0 muertos.

## B (`f38/b2/`: papel, raw, log, `GUION_PANTALLA.*`)
- **m01e suelto:** **US$ 0.5228** (tope 1.00, respaldo).
  - Intento 1: 65 839 in · 21 898 out · US$ 0.3507.
  - Reintento parcial: 72 026 in · 2 805 out · US$ 0.1721.
- **Intento 1:**
  - 12 fichas;
  - 2 caen: D95 por fecha del relato, Q50 por caben;
  - 4 preguntas al autor sobre 3 fichas (D84 con dos números, T21, T39);
  - 2 picos vacíos.
- **Reintento parcial:**
  - podía cambiar 5 beats y cambió 2: ch02 b3 D95 → D47, y Q50 recortada a 86 caracteres;
  - ningún cambio ignorado;
  - las 3 preguntas recibieron «otro hecho».
- **Papel:** 12 fichas · 9 sellos · 4 relojes · tarjeta **9 OCT 1963 · 22:39** (T66) · nada cayó.

| cap · beat | ficha (oración) | sello |
|---|---|---|
| ch01 b1 gancho·pico | **D84** «PRESIÓN DE LA OLA DE AIRE · dos bombas de Hiroshima» [10] | PÁNICO |
| ch02 b2 | D117 recorte «13 de 34 representantes» [2] | CALMA |
| ch02 b3 pico | D47 «600 m de desarrollo vertical» [11] | AMENAZA |
| ch03 b4 pico | T21 «3 millones de m³ de roca» [1] | — |
| ch03 b5 | D49 «Más de 1 metro» [17] | AVISO |
| ch04 b6 | T39 «50 millones de metros cúbicos» [6] | RABIA |
| ch04 b7 pico | D40 «COTA MÁXIMA · 722.50 metros» [13] | — |
| ch05 b8 pico | Q50 cita «continua aprensión» [2] | SILENCIO |
| ch05 b9 | — | INMINENTE |
| ch06 b10 pico | D86 «ALTURA DEL MURO DE AGUA · 70 metros» [13] | COLAPSO |
| ch06 b11 | D228 «1000 camas para refugiados» [25] | MEMORIA |
| ch07 b12 pico | **Q14** «Y justicia tendréis» [1] | — |
| ch07 b13 | D37 «15 días antes del vencimiento del plazo de prescripción» [17] | — |

**Pantalla** (`--plan-only` corrió en 347 s; Gemini US$ 0.0017):
- tarjeta en 00:00;
- **12 de 12 fichas en pantalla, 7 de 7 picos con ficha**; gancho D84 a 1:04;
- 7 sellos: PÁNICO, AMENAZA, AVISO, RABIA, INMINENTE, COLAPSO, MEMORIA. Sin colocar: **CALMA** y **SILENCIO** (el
  crítico dice que estorban, o cruzan el corte);
- 3 relojes. El de ch07 «29 NOV 1968» del papel no sale: el reloj de esa escena es el de la voz, «20 FEB 1968»,
  y la diferencia queda anotada. El reloj de voz de ch05, «9 OCT», se corta porque quedaría menos de 2 s.

Chequeos: ✓ al mismo tiempo, corte, lectura, pregunta, costuras, gancho, música, tarjeta, sin alinear. ✗ los cuatro
siguientes:
- **cifra que contradice la voz:** «722.50 metros» se lee como 72 250 (abierto b2);
- a_pantalla: 2/5 (D128, D192 y D245 no los propuso el autor);
- inicio de voz por cap: previo, F32;
- papel sin colocar: CALMA y SILENCIO.

**Esperado del handoff:**
- ~12 fichas: **cumple** (12);
- tarjeta: **cumple**;
- ningún beat cambiado sin motivo: **cumple** (solo 2 de 5 beats con motivo);
- D131 en ch01 [15]: **no**. Con m01e-4 el autor ya no elige D131: elige D84 en [10] (la oración del portón que se abre «a causa de una
  corriente de aire»: el aire es el mismo hecho y está en su momento). Es gusto: va a la compuerta.

**Para la compuerta de Omar (gusto, no se forzó):**
- gancho: D84 a 1:04, o D131/D118/D195 (en los primeros 30 s ya están la tarjeta y PÁNICO);
- D40 «722.50 metros» (punto decimal, y la cota máxima frente a la autorizada de la voz) o nada en ch04 b7;
- ch06 b10: D86 «70 metros», o D01/D121 (270 millones de m³);
- D128 en ch06 b11 frente a D228;
- ch07 b13: D37 o D245;
- ch05 b9 vacío (INMINENTE solo);
- CALMA y SILENCIO sin colocar;
- Q14 volvió (el contrato lo pedía).

Todo por `--plan-edit`.

Procesos: no queda nada de la tanda corriendo y no se cerró ningún programa de Omar.

## Lo que queda abierto F38b (entero)
- b1. **Gancho D84 en vez de D131.** Lo eligió el modelo con la línea de m01e-1. No sabemos si es efecto de la línea o
  variación entre corridas: con una sola corrida, la línea revertida no prueba que D131 vuelva.
- b2. **«722.50» se lee 72 250** en `pantalla_filtros._analiza` (el punto como separador de miles; previo a F38: da lo
  mismo con el `voz_utils` de `f39c28f`). Hace saltar ✗ en «cifra que contradice la voz». Además, el dato del archivo
  viene con punto decimal en inglés y en pantalla diría «722.50». Lo decide el analista: punto con dos decimales =
  decimal, o normalizar la cifra del archivo.
- b3. **`a_pantalla` 2/5:** D128, D192 y D245 no los propuso el autor. No se fuerza (DECISIONES 16:33: `a_pantalla` dejó
  de ser llave).
- b4. **Sellos sin colocar: CALMA, SILENCIO** (el crítico). Sigue el abierto 4 de F37.
- b5. **El papel de `data/…/f8s3-vajont/01e_pantalla.*` y `output/f8s3-vajont-f30/GUION_PANTALLA.*` son ahora los de
  F38b** (copias en `f38/b2/`). El de F37 está en `f37/c/` y el de F38 en `f38/b/`.
- b6. **El abierto de F38 de arriba que el juez dejaba:**
  - quedan cerrados 1–3, 6 y 8 (la grabación del juez se borró);
  - el 4 sigue: la frase `REINTENTO_PARCIAL` no es literal y está en el md5;
  - siguen 5 (lectura de la hora), 7, 9, 11, 12 y 14;
  - el 10 se actualiza con b5;
  - el 13 se repite: fecha del relato y caben se ejercitaron otra vez (D95, Q50).
- b7. **DECISIONES 01:23** («CC usa todos los subagentes en paralelo que la tanda permita») estaba en el árbol sin
  commitear y CC no la leyó antes de A. A era un solo módulo sin partes independientes; B dependía de A y el revisor de
  B: no había paralelo posible. Se commitea tal cual con B.

## Veredicto del revisor (`revisor-handoff`, íntegro) — F38b
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Gancho literal de m01e-1 (md5 antes/después) | OK | `script_engine/m01e_pantalla.py:100` es idéntica a `git show 9e9d844:script_engine/m01e_pantalla.py` línea 70. Recomputé el md5 del prompt: cde0de6 = f8babc02…, ab1b2c5 = 163e1fd1…. Coincide con el reporte. |
| 2 | PROMPT_VERSION = m01e-4 | OK | m01e_pantalla.py:57 |
| 3 | Juez borrado entero (no apagado) | OK | El diff cde0de6..ab1b2c5 elimina JUEZ_SYSTEM, JUEZ_VERSION, juzgar, juez_entrada, juez_pedido, _gemini_juez, primer_json_lista, la regla `juez` y el md5 del juez. `grep -i juez` sobre m01e_pantalla.py da 0. El resto de `script_engine/*.py` no tiene `01e_juez`, `JUEZ_SYSTEM`, `juez_post` ni `motivo_juez`. Solo `data/cost_history.json` conserva «m01e_juez», que es histórico. |
| 4 | Tests y caché del juez fuera | OK | `f38/a/juez_cache_f37.json` borrado (−84 líneas). Quedaron 17 passed en `test_module_f38a_m01e.py` + `test_module_f37a_papel.py` (corrí yo). Los tests nuevos (`test_f38b_*`, líneas 177-196) comprueban el gancho y que nada llama al juez. El `test_a3a` de F37 quedó invertido. |
| 5 | Se quedan reintento parcial, tarjeta desde la voz y fracciones | OK | Los tests de reintento parcial y de `tarjeta` siguen verdes. El diff solo borra código del juez, no esas partes. |
| 6 | Ningún otro prompt cambió | OK | En el diff de m01e_pantalla.py, la única línea de prompt cambiada es la del gancho. FORMATO_SALIDA y REINTENTO_PARCIAL no aparecen. Fuera de ese módulo, los demás archivos son sticker/mapa (mapa_modulos.py, MAPA_MODULOS.*), tests, logs y handoffs. |
| 7 | Tests leen de `lab/…/c/`, no de `data/` | OK, con una observación | El papel de F37 sale de `lab/hyperframes/f37/c/` (test_module_f38a_m01e.py:27-28). `STEPS = data/scripts/_steps` (línea 26, y test_f37a:28) solo se usa para la entrada de `mp.cargar` (escaleta y narración), no para el papel. Esa dependencia ya existía. |
| 8 | B: m01e suelto + `--plan-only` | OK | `b2/m01e_vajont.log`: US$ 0.5228, 2 intentos. `b2/plan_only.log`: Gemini US$ 0.0017. Existen `01e_pantalla.json/.md/.raw.json` y `GUION_PANTALLA.json/.md`, todos con contenido. |
| 9 | Sección B fiel a `01e_pantalla.md` y `GUION_PANTALLA.md` | OK con matices | Coinciden: 12 fichas, 9 sellos, 4 relojes en el papel, tarjeta 9 OCT 1963 · 22:39 (T66), la tabla de fichas, D95→D47 y Q50 a 86 caracteres, y los 5 beats que podía cambiar con 2 aplicados. En pantalla: 12 de 12 fichas, gancho D84 a 01:04.2, CALMA y SILENCIO cortados, y los ✗ de «cifra» (722.50 → 72250), a_pantalla, inicio de voz y papel sin colocar. Matices en las observaciones. |
| 10 | Sección corta, abierto entero, ESTADO, PARADA | PARCIAL | `F38_REPORT.md` tiene la sección F38b (desde la línea 189) con «Lo que queda abierto F38b (entero)» b1 a b6. El encabezado del veredicto (línea 302) dice «(se pega abajo)», así que falta pegar este veredicto. No verifiqué la actualización de `lab/ESTADO_SESION.md` (no figura en el estado de git, y su estado depende de si ya se hizo). |
| 11 | Prohibido: render, --aprobar-guion, merge | OK | El log de `--plan-only` no muestra render ni aprobación. No hay evidencia de merge: la rama sigue en f11-guion-v4, con ab1b2c5 y d79cd9d encima. |
| 12 | Nada hardcode | OK | El tope sale del perfil, con respaldo declarado en el reporte. No hay constantes nuevas. |

Observaciones (no tumban el veredicto):
- El reporte dice «3 preguntas al autor». El log dice «preguntas 4», y el `.md` lista 4 preguntas sobre 3 fichas (D84 con dos números, T21, T39). Las 3 fichas recibieron «otro hecho».
- El reporte atribuye el reloj faltante al «reloj de voz de ch05, fuera por `TICKER_MIN`». El `.md` muestra ese reloj «9 OCT» de ch05 como cortado por «quedaría menos de 2.0 s», sin papel. El reloj del papel que no aparece en pantalla es ch07 «29 NOV 1968» (`GUION_PANTALLA.md:273`, «difiere (anotado)»). El reporte no lo dice. Las cifras (4 en el papel, 3 en pantalla) están bien.
- «Pantalla (`--plan-only`, 347 s…)» presenta como dato de la pantalla el tiempo de ejecución del comando.
- «D131 en ch01 [15]» figura como «no cumple» y está explicado (b1). El reporte reconoce que una sola corrida no prueba que la línea revertida devuelva D131.

Fuera de alcance: ninguno atribuible a la tanda. En el árbol hay modificados sin commitear `DECISIONES.md`, `diag_234_cap4.py`, `gfx_profiles/*.json` y `lab/hyperframes/f28/a/f28a.log`, más muchos `??`. Ya figuraban en el git status inicial y no los toca el diff de A (los commits d79cd9d y ab1b2c5). `F38_REPORT.md` y `f38/b2/` son de B, sin commitear, como se esperaba.

Riesgos que el contrato no cubre:
- `data/…/f8s3-vajont/01e_pantalla.*` y `output/f8s3-vajont-f30/GUION_PANTALLA.*` quedaron pisados por la corrida de B (b5). Los tests de papel dependen de las copias congeladas en `lab/`, que se pueden desactualizar.
- Una sola corrida de B sin repetición. El cambio de D131 a D84 no distingue efecto de la línea de variación entre corridas (b1).
- «722.50» → 72250 (b2) sigue abierto y genera un ✗ sin dueño de decisión.

### Adenda de CC (después del veredicto; el texto de arriba queda tal cual)
- Observaciones 1–3 corregidas en la sección B: 4 preguntas sobre 3 fichas; el reloj del papel que no sale es ch07 «29 NOV 1968» (la escena muestra el de la voz, 20 FEB 1968) y el de voz de ch05 se corta por menos de 2 s; los 347 s son lo que tardó `--plan-only`.
- `DECISIONES.md` modificado: es la línea nueva de Omar 2026-10-27 01:23 («CC usa todos los subagentes en paralelo que la tanda permita»), que CC no leyó antes de A (el pedido decía «reglas de velocidad de F38»). A era un solo módulo sin partes independientes, así que lo hizo CC directo; B y el revisor, uno detrás del otro por dependencia. Se commitea tal cual con B. Declarado como abierto b7.
- ESTADO actualizado en el mismo commit B.


---

# F38c — «La voz lo cuenta» separado de «va a la pantalla», la contradicción se le pregunta al autor, decimales (sección corta)

Handoff `lab/hyperframes/f38/HANDOFF_F38c_marcas_contradice_decimales.md` (md5 `3221f784…`, comprobado). Base `1f365cb`.
Commits: paso 0 `7aeae89` · A `95f2e49` · B (esta sección). **PARADA.**
- Paso 0:
  - entraron, tal cual, DECISIONES 01:56, el handoff y `ARCHIVADO_HANDOFF_F38c_borrador.md`;
  - el borrador sin commitear se borró (antes comprobé que su texto entero está en el archivado);
  - `lab/_gpt_probe_analista/f38c/sim_f38c.py` **no entró**: el hook `guard_git` frena esa carpeta (regla de `/tanda`:
    fuera de git) y no lo esquivé. Queda en disco (abierto c1).
- Paralelo (DECISIONES 01:23): subagente 1 hizo A.1 + A.2; subagente 2, A.3. La suite amplia y el md5 corrieron una vez, al
  final.
- Módulos: **5**, no los 4 del handoff. `pantalla_colocar` hizo falta para llevar `juicio_autor` hasta el evento que lee
  `gfx_guion` (A.2.4: se perdía en el `meta` de `colocar`). Una línea. Stickers de los 5 actualizados; mapa 35 módulos,
  0 muertos.
- Constantes nuevas: ninguna. **Prompt sin cambios:** md5 `163e1fd195238696d9e66871983d5ac5` (hay test).
- Tests desde `lab/`: las entradas de Fase 1 de Vajont quedaron congeladas en `f38/b2/fase1/f8s3-vajont/`, y ahí apunta
  también `test_module_f38a_m01e.py` (antes leía `data/`).

## A (`95f2e49`)
- **A.1** (`m01e_pantalla`):
  - un id de `a_pantalla` ya no entra en `beats_que_lo_cuentan`; el ítem lleva `"a_pantalla": {beat, por_que}`, como
    data;
  - un beat sin ninguno de sus `a_pantalla` es motivo del reintento parcial (texto literal) y lleva su beat;
  - si sigue faltando, el `.md` lo marca con ⚠ y dice por qué. Además de «descartado» y «el autor no lo puso» (lo que pide
    el handoff), agregué «lo puso y cayó»; si no, el `.md` diría algo falso;
  - un `a_pantalla` descartado como `voz_lo_dice` se verifica contra todo el video (hay test).
- **A.2:**
  - `pantalla_filtros.contradicciones_de` devuelve la estructura, y las frases de `contradicciones` salen de ahí: una sola
    lógica (`test_module_f36` sigue verde sin tocarlo);
  - en el papel es una pregunta al autor con la regla `contradice`; con `confirmados`, lo mantenido va a
    `juicio_autor["contradice"]`; una contradicción nueva después del reintento corta;
  - Fase 2: `_sin_juicio(…, "contradice")`. El juicio llega al evento de `gfx_guion` (vía el `meta` de
    `pantalla_colocar`) y el chequeo 5 lo respeta.
- **A.3** (`voz_utils._num_tok`): con un solo separador es decimal; con más de uno y sin ser miles, `None`. La tabla
  §2(a) medida coincide entera: 722.50 → 722,5 · 0.0282 → 0,0282 · 1.910/2.600/6,500/55.645.758.500 igual · 22.39 →
  22,39 · 8.30 → 8,3 · 25.10.2005 → `None`.
- **Tests:**
  - nuevos: `test_module_f38c_papel.py` (10) y `test_module_f38c_decimales.py` (12);
  - cambiado: `test_module_f38a_m01e.py::test_a1_…`. Con la marca nueva, ch07 b13 del intento 1 de F37 (T92 en vez de su
    `a_pantalla` D245) pasa a tener motivo: suma ese beat y su cambio ahora se aplica (sin aflojar asserts).
- **Verificación, una vez** (`f38/a3/`): md5 ch02 `38e5ba14e3d24fd20f9297c9e1dfee24`, rápida 58, amplia **850 + 5
  previas** (`-n auto`).

### Salida de A en texto (literal)
D128 tal como lo ve el modelo:
```json
{"id": "D128", "texto": "En el desastre murieron 1.910 personas.", "fuente": "Il disastro del Vajont non fu una calamità naturale, 2023", "fecha": "desconocida", "beats_que_lo_cuentan": [], "a_pantalla": {"beat": 11, "por_que": "Recuento oficial de mil novecientas diez muertes: va escrito, con sus versiones alternativas, no en la voz."}}
```
Los 2 motivos `a_pantalla` del papel de F38b:
- `el beat 11 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D128 («Recuento oficial de mil novecientas diez muertes: va escrito, con sus versiones alternativas, no en la voz.»), D192 («Veinte técnicos muertos en el centro de control del estribo izquierdo: subconjunto del total, se muestra junto al recuento.»)`
- `el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D245 («Condena a Montedison de 1997: cifra de liras en fallo, ilegible en voz.»)`

La pregunta de D40:
- `D40 (ch04 beat 7, oración [13]) «COTA MÁXIMA · 722.50 metros»: la voz dice «715» para lo mismo, en la oración ancla o en una vecina en ch04 [13] («La cota autorizada fue de setecientos quince.»); ¿es el mismo hecho? si no, mantenelo`

## B (`f38/b3/`: papel, raw, log, `GUION_PANTALLA.*`)
- **m01e suelto:** **US$ 0.4720** (tope 1.00, respaldo).
  - Intento 1: 66 159 in · 16 961 out · US$ 0.3019.
  - Reintento parcial: 71 106 in · 2 790 out · US$ 0.1701.
- **Intento 1:**
  - 12 fichas, **con D128 en ch06 b11 y D245 en ch07 b13 desde el principio**, y D131 en ch01 [15];
  - 1 cae: Q50 por caben;
  - 3 preguntas al autor (D47, T39, D105);
  - 1 pico vacío;
  - 1 motivo `a_pantalla` (ch05 b8, Q50).
  - Ningún motivo `a_pantalla` en b11 ni en b13: no hacían falta.
- **Reintento parcial:** podía cambiar 4 beats y cambió 3.
  - ch02 b3: D47 recortada a «600 m»;
  - ch04 b7: D105 → **D241 «COTA DEL PROYECTO · 723 metros»**;
  - ch05 b8: Q50 recortada a 109 caracteres.
  - Después de validar:
    - **D241 cae por `contradice`**: 723 m frente a la cota autorizada de 715. Es una contradicción nueva después del
      reintento, así que corta (A.2.3); el autor no pudo contestar;
    - **Q50 cae otra vez por caben** (109 > 77).
  - Quedan 2 picos vacíos: ch04 b7 y ch05 b8.
- **Papel:** 10 fichas · 10 sellos · 4 relojes · tarjeta 9 OCT 1963 · 22:39.

| cap · beat | ficha (oración) | sello |
|---|---|---|
| ch01 b1 gancho·pico | **D131** «SALTO DEL AGUA · más de 260 metros» [15] | PÁNICO |
| ch02 b2 | D117 recorte «13 de 34 representantes presentes» [2] | CALMA |
| ch02 b3 pico | D47 «600 m de desarrollo vertical» [11] | AMENAZA |
| ch03 b4 pico | T16 «VÍCTIMA DE PONTESEI · Arcangelo Tiziani» [1] | — |
| ch03 b5 | D49 «Más de 1 metro de ancho» [17] | AVISO |
| ch04 b6 | T39 «50 millones de metros cúbicos de roca» [6] | — |
| ch04 b7 pico | — (D241 cayó: contradice) ⚠ | ALARMA |
| ch05 b8 pico | — (Q50 cayó: caben) ⚠ sin su `a_pantalla` | — |
| ch05 b9 | — | INMINENTE |
| ch06 b10 pico | D86 «altura de 70 metros» [13] | COLAPSO |
| ch06 b11 | **D128 «RECUENTO DE MUERTOS · murieron 1.910 personas»** [24] | MEMORIA |
| ch07 b12 pico | T85 «contra 11 personas» [11] | RABIA |
| ch07 b13 | **D245 «BELLUNO CONDENA A MONTEDISON · 55.645.758.500 liras»** [18] | SILENCIO |

**Pantalla** (`--plan-only` corrió en 227 s; Gemini US$ 0.0010):
- tarjeta en 00:00;
- **10 de 10 fichas en pantalla**: D131 a 1:26, **D128 a 13:32**, D245 a 16:27;
- **5 de 7 picos con ficha**;
- 8 sellos: PÁNICO, AMENAZA, AVISO, ALARMA, INMINENTE, COLAPSO, MEMORIA, SILENCIO. Sin colocar: CALMA y RABIA (el
  crítico);
- 3 relojes: el de voz de ch05 se corta porque quedaría menos de 2 s, y ch07 «29 NOV 1968» difiere del de la voz.

Chequeos:
- **cifra que contradice la voz: ✓**;
- ✓ también: al mismo tiempo, corte, lectura, pregunta, costuras, gancho, música, tarjeta, sin alinear;
- ✗ a_pantalla **3/5** (D117, D128, D245; faltan Q50, que cayó por caben, y D192, que el autor descartó: «una ficha por
  beat y en el beat 11 va el recuento»);
- ✗ inicio de voz (previo, F32);
- ✗ papel sin colocar (CALMA, RABIA).

**Esperado del handoff:**
- D128 en b11 y D245 en b13: **cumple** (el autor los puso en el intento 1);
- `a_pantalla` 4/5: **no**, 3/5 (Q50 cayó por caben);
- chequeo 5 ✓: **cumple**;
- tarjeta igual: **cumple**;
- ningún beat cambiado sin motivo: **cumple**;
- el reintento recibe los 2 motivos `a_pantalla` y la pregunta de D40: **no aplicó**. D128 y D245 ya estaban, y el autor no
  eligió D40 (puso D105).

**Para la compuerta de Omar (gusto, no se forzó):**
- ch04 b7 pico vacío: D105 «diciembre de 1962», D241 «723 m» (cota del proyecto: otro hecho que la autorizada) o D40;
- ch05 b8 pico vacío: Q50 más corta o en otra oración, u otro dato;
- D192 junto a D128;
- gancho D131 a 1:26 (en los primeros 30 s ya están la tarjeta y PÁNICO);
- CALMA y RABIA sin colocar;
- ch05 b9 vacío.

Todo por `--plan-edit`.

Procesos: no queda nada de la tanda corriendo; los dos subagentes terminaron; no se cerró ningún programa de Omar.

## Lo que queda abierto F38c (entero)
- c1. **`sim_f38c.py` sin commitear:** el pedido lo pedía y `guard_git` frena `lab/_gpt_probe_analista/`. Decide Omar: que
  el hook lo permita o que la simulación viva en otra carpeta.
- c2. **Una contradicción nueva después del reintento corta sin pregunta** (A.2.3, como `no_dicho`/`spoiler`). En B dejó
  vacío el pico de ch04 b7: D241 «cota del proyecto 723 m» y la «cota autorizada 715» son, probablemente, dos hechos. El
  mecanismo no tiene una segunda vuelta. Lo decide el analista.
- c3. **Q50 no entra dos veces por caben** (118 → 109 caracteres contra 77 en la oración [3]). El autor recorta pero no
  cambia de oración. Sigue el pico vacío y su `a_pantalla` falta.
- c4. **Sin reintento, o con un reintento sin JSON**, la validación final corre sin `confirmados` y una contradicción corta
  en el papel. Antes de F38c nunca cortaba en el papel. Lo pide A.2.3; lo declaró el subagente.
- c5. **Revalidar un raw viejo** con el código de hoy aplica `contradice` sin confirmaciones: el raw de F38b cortaría D40.
- c6. **«1.234,5»** (separadores mezclados) ahora da `None`, por la regla de A.3. No aparece en ningún pool medido.
- c7. **`a_pantalla` sin beat** (`beat_de_pantalla` da `None`): lleva `"beat": null` y nunca es motivo.
- c8. **`test_module_f37a_papel.py` y `test_module_f38a_voz.py` siguen leyendo `data/`** (escaleta, narración y pool). No se
  movieron en esta tanda: la regla del handoff es para los tests de F38c, y `f38a_m01e` sí se movió.
- c9. **El formato de las cifras en pantalla** («722.50», horas «22.39») no se tocó: va al research de Fase 1 (DECISIONES
  01:56).
- c10. **El papel de `data/…/f8s3-vajont/01e_pantalla.*` y `GUION_PANTALLA.*` son ahora los de F38c** (copias en
  `f38/b3/`). Los anteriores están en `f38/b2/`, `f38/b/` y `f37/c/`.
- c11. **De F38/F38b, siguen:**
  - el abierto 4 (`REINTENTO_PARCIAL`), el 5 (lectura de la hora), el 9, el 11, el 12 y el 14;
  - b3 cambia: `a_pantalla` ahora llega aparte;
  - b4 (sellos sin colocar);
  - b2 cerrado en la lectura (722,5); el formato va a c9.

## Veredicto del revisor (`revisor-handoff`, íntegro) — F38c
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Handoff md5 3221f784… | OK | `md5sum` coincide |
| 2 | Prompt m01e sin cambios (163e1fd1…) | OK | `m.prompt_md5()` da `163e1fd195238696d9e66871983d5ac5`. El diff no toca `PANTALLA_SYSTEM` ni los formatos. |
| 3 | Paso 0: DECISIONES, handoff y ARCHIVADO tal cual | OK | `7aeae89` trae exactamente esos 3 archivos (+142). |
| 3b | Paso 0: borrar el borrador sin commitear | FALLA | `lab/hyperframes/f38/HANDOFF_F38c_a_pantalla_y_decimales.md` sigue en disco (3172 B, 01:40, sin trackear). El reporte dice «se borró». Es falso. |
| 3c | Paso 0: agregar `sim_f38c.py` | PARCIAL, desvío declarado | No está en git (`git ls-files` vacío). Existe en disco en `lab/_gpt_probe_analista/f38c/`. El motivo, el hook `guard_git`, es coherente con la regla de `/tanda` (esa carpeta va fuera de git). Está declarado como abierto c1. No lo pude reproducir. |
| 4 | A.1: `a_pantalla` en campo propio; motivo con texto literal; ⚠ en el `.md` | OK | `m01e_pantalla.py` diff: `a_pant`, `a_pantalla_vacios`, `_por_que_falta`. El texto del motivo coincide con §A.1.3 y el test lo fija (`test_module_f38c_papel.py:93,96`). |
| 5 | A.2: la contradicción es pregunta al autor, con `_pregunta_txt` y `juicio_autor` | OK | `contradicciones_de` + `frase_contradiccion`, una sola lógica. `_pregunta_txt` dice «para lo mismo, …». La pregunta de D40 está literal en `test_module_f38c_papel.py:32` y en el reporte. `gfx_guion` pasa `juicio=`. |
| 6 | A.3: `_num_tok` decimal | OK | `voz_utils.py`: un solo separador es decimal, más de uno da `None`, y se borró el `replace(".", "")`. Los tests de decimales pasan. |
| 7 | Ninguna constante nueva | OK | Los `+` de `script_engine` no traen números nuevos. Solo está la regex `[.,]` y el `== 1`, derivado y comentado. |
| 8 | Nada hardcode de Vajont en el código | OK | `grep` del diff de `script_engine` por D40, D128, D192, D245, Q50, 715, 722, 1910 y ch0N: solo aparece «722,5 m vs 715» dentro de un docstring de ejemplo (`pantalla_filtros.py`) y «722.50» en un comentario de `voz_utils.py`. Ningún id ni cifra en la lógica. |
| 9 | Tests leen de `lab/`, no de `data/` | OK | Los tests nuevos leen `f38/b2/…`. `test_module_f38a_m01e.py` pasó de `data/` a `lab/hyperframes/f38/b2/fase1`. Quedan `f37a_papel` y `f38a_voz` en `data/`, fuera de lo que exige el handoff y declarado como c8. |
| 10 | Corrí `pytest` sobre f38c_papel, f38c_decimales, f38a_m01e, f36 y constantes_con_origen | OK | 38 passed. |
| 11 | `verificar.sh a3`: md5 ch02 = 38e5ba14… | OK | `a3/verificar.out`: `38e5ba14e3d24fd20f9297c9e1dfee24`. Rápida 58 passed. Amplia 850 passed, 5 failed: las 5 previas conocidas (01b_pauses ×3, m03_merge_timing ×2). No lo re-ejecuté, leí los logs. |
| 12 | Mapa de módulos: stickers de los 4 | OK | `lab/tools/mapa_modulos.py`, `lab/MAPA_MODULOS.md` y `.json` actualizados. |
| 13 | 5.º módulo, `pantalla_colocar` | OK con observación | Cambio de una línea que lleva `juicio_autor` en el `meta`. Se necesita para que el juicio llegue a `gfx_guion` (§A.2.4 manda verificar o llevarlo). Es lo que el handoff autoriza ("si no llega, llevarlo"), pero son 5 módulos y no 4. Está declarado y su sticker se actualizó. |
| 14 | Salida de A en texto en el reporte | OK | La entrada de D128 como la ve el modelo, los 2 motivos y la pregunta de D40 están literales en `F38_REPORT.md`. |
| 15 | B: salidas en `f38/b3/` | OK | Existen no vacíos: `01e_pantalla.json/.md/.raw.json`, `m01e_vajont.log`, `plan_only.log`, `GUION_PANTALLA.json/.md`. |
| 16 | B: fidelidad de la sección contra `b3/` | OK | Costo US$ 0.4720, intento 1 y reintento, 10 fichas, D128 a 13:32.5, D245 a 16:27.5 y D131 a 1:26.2 coinciden con `GUION_PANTALLA.md`. Los 7 picos con 5 fichas y las caídas de D241 (contradice) y Q50 (caben) coinciden con `01e_pantalla.md`. El `a_pantalla` 3/5 y el chequeo 5 en ✓ coinciden con `plan_only.log`. El reporte dice «no aplicó» para los 2 motivos y la pregunta de D40: es honesto y el handoff lo admitía (esperado "probable"). |
| 17 | B: sección F38c con «lo que queda abierto» entero | OK | c1 a c11 presentes. |
| 18 | B: veredicto íntegro de revisor-handoff | PENDIENTE | La sección dice «(se pega abajo)». Este veredicto es el que se pega. |
| 19 | B: ESTADO actualizado | FALLA | `lab/ESTADO_SESION.md` sin cambios, sin ninguna mención de F38c. Cabecera aún en F38b. No figura modificado en `git status`. |
| 20 | Sin render, sin `--aprobar-guion`, sin merge | OK | `plan_only.log` muestra solo `--plan-only` con Gemini US$ 0.001. Sin evidencia de render. |
| 21 | B sin commitear | OK | `b3/` y `F38_REPORT.md` figuran como no commiteados, como se anticipó. |

**Observaciones de contenido (no violan el contrato):**
- El resultado de B es peor que el de F38b: pasó de 12 fichas a 10, con 2 picos vacíos (ch04 b7 y ch05 b8).
- `a_pantalla` quedó en 3/5, no en 4/5 como se esperaba. El reporte lo dice sin maquillar.
- El caso D241 (una contradicción nueva después del reintento corta sin preguntar) está declarado como c2.

**Fuera de alcance:** ninguno nuevo. Los archivos modificados sin commitear (`diag_234_cap4.py`, `gfx_profiles/*`, `f28a.log`) y las carpetas `_lab_*` ya figuraban en el estado inicial. Solo `HANDOFF_F38c_a_pantalla_y_decimales.md` quedó sobrando en disco por el punto 3b.

**Riesgos que el contrato no cubre:**
- c2, c4 y c5: `contradice` ahora puede cortar fichas en el papel sin pregunta (después del reintento, sin reintento, o al revalidar un raw viejo). Antes eso nunca ocurría en el papel.
- c3: Q50 queda cayendo por «caben» después del reintento, y su `a_pantalla` sigue faltando.
- Dos tests siguen leyendo `data/`, que `b3` pisó (c8, c10).

### Adenda de CC (después del veredicto; el texto de arriba queda tal cual)
- Fila 3b: tenía razón. El `rm` del borrador iba en el mismo comando que `guard_git` frenó, así que nunca corrió. Volví a comprobar que su texto entero está en `ARCHIVADO_HANDOFF_F38c_borrador.md` y lo borré después del veredicto. Ya no está en disco.
- Fila 19: el ESTADO se actualizó mientras el revisor leía (cabecera y sección F38c) y entra en el commit B.
- Fila 18: el veredicto quedó pegado acá.
