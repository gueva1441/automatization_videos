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
