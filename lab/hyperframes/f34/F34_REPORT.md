# F34 — Reglas de pantalla corregidas: reporte

Handoff `lab/hyperframes/f34/HANDOFF_F34_reglas_de_pantalla.md` · base `fc889c9` en `f11-guion-v4` · pedido de Omar: «A a B
sin parar entre partes, cada parte pega su salida en texto; los tres cambios del prompt del rotulista exactos como en
A.1; el prompt de sellos de A.4 literal; sin render ni aprobación; comparación línea por línea con el simulador contra
§1; reporte con el veredicto íntegro del revisor; cerrar tareas en segundo plano; PARADA».

**Commits:** A `24d9dad` (reglas) · B `2f04030` (guion de Vajont) · cierre = el commit de este reporte.
**Costos:** Claude US$ 0.4633 (tope del handoff 1; 10 llamadas, ch03 y ch04 con reintento y ch01 con dos de US$ 0.15 por el pool entero del gancho; ch01 y ch02 se cayeron
en el prefetch por el tope con las llamadas en vuelo y se rehicieron en fila) · Gemini US$ 0.2392 (tope 0.5; sellos de clima, crítico y visión) ·
más una llamada real a Gemini (texto, Flash) que hizo por error un test viejo de F32 antes de que le pusiera un falso.
**Sin render, sin `--aprobar-guion`, sin merge, sin publicar, sin borrar.** md5 de ch02 sin `--gfx` `38e5ba14…`.

## En pocas palabras

Las reglas de A están programadas y probadas (18 tests nuevos). En el guion nuevo de Vajont salen bien los **relojes
(4 + tarjeta), las 2 aguas, los 6 punches y la música alineada con cada title card (0 cuadros de desvío, medido)**.
Salen **5 textos de 9** (D117, T39, D192, D245 y D71 en vez de D49) y **7 sellos de 8**, cuatro de ellos AMENAZA.
Los textos que faltan no son del prompt nuevo: D128 lo saca un bug viejo del realizador (borra todo contador), T85 y
D49 los corta la regla «uno por beat / pico solo a_pantalla», Q50 la lectura (el modelo escribió 147 caracteres) y
D118 el modelo no lo eligió para el gancho. Detalle abajo, con la tabla del simulador.

## Parte A — reglas (commit `24d9dad`)

## Lecturas declaradas (/tanda paso 1)

`CLAUDE.md`, `DECISIONES.md` (entero, con las líneas del 26 en disco), `lab/ESTADO_SESION.md` (cabecera, F33 y F32), el
handoff entero, `.claude/commands/tanda.md`, y el código que toca: `gfx_rotulista` (entero), `gfx_layer.apply_gfx`,
`gfx_realizador` (`cerrar`, `finalizar`, `ya_dicho`), `gfx_pool.pool_ticker`, `gfx_critic` (bloques, criterio de
corte), `gfx_guion` (eventos y chequeos), `aprobacion`, `fase2b` (música continua, mezcla de previsualización,
`_solo_plan`, llamada del render a `apply_gfx`).

**Números del handoff que no están en DECISIONES.md:** §0b cita «DECISIONES 14:28» (gancho) y «DECISIONES 14:36»
(tarjeta) y en el archivo no hay líneas de las 14:28 ni de las 14:36. No entró ningún número nuevo por eso: el gancho
0–1 texto está en la línea de las 02:52; «1 reloj, 1 sello, nunca vacío» no lleva número nuevo (se implementó como
«el sello no cuenta contra el reloj del beat» + un chequeo del guion); la tarjeta dura `title_dur` (identidad F3). La
regla «en caps de una sola escena la unidad es la oración» figura en DECISIONES como **propuesta del analista,
pendiente de confirmar**; se implementó porque el handoff la pide (A.3.2) y queda anotada abajo.

## Módulos que toca (/tanda paso 2, stickers de `lab/MAPA_MODULOS.md`)

| módulo | qué hacía | qué hace después de F34 |
|---|---|---|
| `gfx_rotulista` | escribe los textos por beat, los coloca, una cosa por escena, sellos por tema (la palabra de la voz) | prompt con los 3 reemplazos de A.1; gancho con todo el pool del video; candado/no dicho/spoiler corregidos; una cosa por **oración** en caps de una sola escena; el sello no es fijo ni frena al reloj; sellos de **clima** (Gemini, vocabulario del perfil); reloj y agua desde la voz; tarjeta fecha-hora |
| `gfx_layer` | orquesta el cap y renderiza | engancha reloj de voz, agua de voz, tarjeta y sellos de clima; **plan congelado** con guion aprobado (no reescribe el plan) |
| `gfx_critic` | saca lo que repite la voz, no aporta o tapa | al sello de clima y al agua de la voz solo los saca si **estorban** (forma) |
| `gfx_guion` | escribe el guion y los chequeos | tarjeta a 0:00, sellos con su palabra de la voz, chequeo por oración en caps de una escena, gancho no vacío, inicio de música por cap, tarjeta |
| `fase2b` | arma el video; música continua | con `--gfx`: pieza de música = segmento del cap (+ crossfade), después de la intro; la mezcla de previsualización **mide** dónde arranca cada pieza |
| `gfx_config` | perillas + perfil | acepta la clave `sellos_clima` del perfil |
| `.claude/` | — | modelo del repo `claude-opus-5-5`; `/tanda` paso 12 (cerrar tareas en segundo plano). Los agentes `revisor-handoff` y `simulador` ya tenían `model: sonnet`. |

`music_intensity` no cambió: el mapa se corre igual y se aplica a la pieza (que ahora dura lo que el segmento).
Mapa regenerado: 37 módulos, 118 aristas, 14 muertos; cambiaron los stickers de `fase2b`, `gfx_layer`, `gfx_rotulista`,
`gfx_critic`, `gfx_guion` y `gfx_config`.

**Una variable por etapa:** el handoff mezcla reglas (A) y la corrida (B); van en dos commits. Dentro de A todas las
reglas se miden juntas en B (el handoff lo pide así: «B mide contra esto»).

## Constantes nuevas con su origen (/tanda paso 4)

| constante | valor | origen (comentario en la línea) |
|---|---|---|
| vocabulario de sellos | las 10 palabras | DECISIONES 14:22, en `gfx_profiles/misterio.json` → `sellos_clima` (fuera de git; **Omar la commitea si quiere**: `"sellos_clima": ["PÁNICO", "CALMA", "AMENAZA", "AVISO", "ALARMA", "INMINENTE", "COLAPSO", "SILENCIO", "RABIA", "MEMORIA"]`) |
| duración de la tarjeta | `title_dur` | identidad F3 |
| reloj de la voz | hasta `TICKER_HOLD` después de la oración, mínimo `TICKER_MIN` | derivado: las del reloj de la cronología (gfx_pool) |
| agua de la voz | dura la oración, al menos `sum(WATER_DUR)`; altura `meters / WATER_FULL_M` en 0.15–0.85 | derivado: la plantilla y `animacion_de_cifra` de F32 |
| fechas | día 1–31; año ≥ 100; ventanas de 4 y 8 tokens | estándar (calendario) / derivado (largo de «treinta y uno», «mil novecientos sesenta y tres») |
| medida de la música | 11 025 Hz, ventana 4 s, búsqueda ±20 s, paso 0.5 s | derivado (resolución ≪ 1 cuadro; margen > 14.8 s medidos en F32) |
| ±1 cuadro | `1/fps` | handoff A.7.2 |

### Simulación previa (antes del código)
Íntegra en `lab/hyperframes/f34/a/simulacion_previa.md` (agente `simulador`). Lo que cambió el diseño: A.2.2 ya
convertía letras a dígitos (el arreglo es el orden: no dicho y spoiler antes que la lectura); el sello no cuenta contra
el reloj/agua/lupa de su beat (§A.3.1 «se mueve a otra oración del beat»); el agua pide palabra clave y va una por cap
(cota > ola > nivel); la hora de la tarjeta = la de la cronología de la fecha del pico que dice el `por_que` del pico.

### salida_a.txt (datos reales de Vajont, sin API)

## A.1 prompt del rotulista
- versión f34-1 · md5 nuevo (SYSTEM + USER) `d90ae69a2dc8c7928bd410ead421dc6b`
- deshechos los tres reemplazos da el de F32 byte a byte: `c9231e24afbc785d5870b33088ce076e` (F32: c9231e24…)
- reemplazo 1 (SYSTEM):
  - antes: «En cada beat puede ir como máximo UN texto; en el beat marcado como pico no va ninguno; en el gancho, a lo sumo uno.»
  - ahora: «En cada beat puede ir como máximo UN texto (dos si son dos datos marcados a_pantalla y van en oraciones distintas); en el beat marcado como pico solo van los datos a_pantalla; en el gancho va a lo sumo uno, y para el gancho podés usar cualquier dato de la lista que la narración no diga en todo el video, aunque no sea de su beat: el gancho tiene que prometer algo.»
- reemplazo 2 (SYSTEM):
  - antes: «Escritura: una línea de etiqueta y una o dos líneas de dato; oración completa o etiqueta + valor; nunca un fragmento sin sujeto o sin el valor.»
  - ahora: «Escritura: la etiqueta es una línea corta que dice qué es («ANCHO DE LA FISURA», «ACTA DEL CONSEJO SUPERIOR»); el dato es UNA línea corta con el valor o el hecho en pocas palabras («Más de 1 metro», «13 de 34 representantes presentes»). Nunca una oración larga: se tiene que leer en dos segundos. Nunca un fragmento sin sujeto o sin el valor. No pongas el nombre de la fuente ni el año de publicación en el dato.»
- reemplazo 3 (SYSTEM):
  - antes: «`pool_id` y una línea `aporta`»
  - ahora: «`pool_id`, y si es cifra también unidad y valor y una línea `aporta`»
- reemplazo 3 (formato de salida del USER):
  - antes: «"pool_id": str, "aporta": str}»
  - ahora: «"pool_id": str, "unidad": str|null, "valor": number|null, "aporta": str}»
- gancho (ch01): el pedido trae 520 ítems del pool del video; la voz dice 174 → quedan 346 candidatos («la narración lo dice en el video: no»)
  - D118 «El proyecto de la presa se amplió, convirtiéndola en la más alta del mundo con 266 metros de altura y una capacidad de 115 millones de metros cúbicos de agua.» → la voz lo dice: no
  - D128 «En el desastre murieron 1.910 personas.» → la voz lo dice: no
  - D117 «El Consejo Superior de Obras Públicas aprobó el proyecto de la presa mediante un procedimiento irregular, con solo 13 de 34 representantes presentes.» → la voz lo dice: no
  - D49 «En 1960, un pequeño desmoronamiento provocó una fisura de más de 1 metro de ancho y casi 2 kilómetros de largo en la montaña.» → la voz lo dice: sí

## A.2 filtros (los casos reales; tests en test_module_f34.py)
- candado: el número/año/nombre que dice la oración ancla cuenta (D117 «1943»: test_a2_1)
- no dicho: corre antes que la lectura; «cuatrocientos» = 400 por valor (D237: test_a2_2; el conversor ya estaba, la falla era el orden)
- spoiler: un nombre dicho antes en el cap o en un cap anterior no es spoiler (T85 «Vajont»: test_a2_3)
  - «Vajont» en la voz de ch01–ch06: sí

## A.3.3 fechas completas que dice la voz (reloj desde la voz si la cronología no da reloj)
- ch01: 9 octubre 1963 · «Longarone, Italia, nueve de octubre de mil novecientos sesenta y tres.»
- ch04: 4 noviembre 1960 · «El cuatro de noviembre de mil novecientos sesenta el embalse estaba a seiscientos cincuent»
- ch07: 20 febrero 1968 · «Pasaron más de cuatro años hasta que, el veinte de febrero de mil novecientos sesenta y oc»
- ch07: 29 noviembre 1968 · «El juicio empezó el veintinueve de noviembre de mil novecientos sesenta y ocho.»

## A.4 sellos de clima: el prompt literal (con {lista} del perfil)
```
Elegí UNA palabra de esta lista que nombre el clima de este momento del relato, no lo que se dice: PÁNICO, CALMA, AMENAZA, AVISO, ALARMA, INMINENTE, COLAPSO, SILENCIO, RABIA, MEMORIA.
No puede ser una palabra que aparezca en estas oraciones: «{voz_-1}» «{voz_ancla}» «{voz_+1}».
Momento: función del beat «{funcion}»; oración: «{voz_ancla}».
Respondé solo la palabra en mayúsculas, o NINGUNA si ninguna calza.
```

## A.5 agua desde la voz: oraciones candidatas por cap (y la elegida, una por cap)
- ch03 oración [1]: OLA · 20 m · «Ese marzo, una masa de roca entró al agua y levantó una ola de veinte metros.»
- ch03 oración [7]: OLA · 20 m · «Una ola de veinte metros.»
  → ch03 elige [1] OLA · 20 m (antes de la regla de una animación por beat)
- ch04 oración [0]: NIVEL DEL EMBALSE · 650 m · «El cuatro de noviembre de mil novecientos sesenta el embalse estaba a seiscientos cincuent»
- ch04 oración [12]: NIVEL · 700 m · «La recomendación que salió de ahí fue no pasar de los setecientos metros sobre el nivel de»
- ch04 oración [13]: COTA AUTORIZADA · 715 m · «La cota autorizada fue de setecientos quince.»
  → ch04 elige [13] COTA AUTORIZADA · 715 m (antes de la regla de una animación por beat)

## A.6 tarjeta fecha-hora
- {"texto": "9 OCT 1963 · 22:39", "fecha": "1963-10-09", "hora": "22:39", "pool_id": "T57", "hora_de": "T66", "fuente": "escaleta.pico T57 (fecha) + T66 (hora)"}

### Verificación del commit A
- md5 `fase2b ba6c3cac… --only-cap ch02 --reuse-visuals --sw-encode` = `38e5ba14e3d24fd20f9297c9e1dfee24` (`a/onlycap_ch02_nogfx.log`).
- Suite rápida 58 · suite amplia **1021 pasan + las 5 previas** (01b_pauses ×3, m03_merge_timing ×2) (`a/suite_*.log`).
- Tests nuevos `test_module_f34.py` (18): uno por regla, con los casos reales (D117 «1943», D237 «cuatrocientos», T85
  «Vajont», ch01 una escena, fecha en letras, prompt de A.4 literal contra el handoff, plan congelado con md5 de planes
  idéntico tras un render simulado, música: con `segmentos` 0 cuadros de desvío; el camino viejo da −2.5/−4.5/−6.5 s,
  el mismo patrón que F32 midió en Vajont). Dos tests viejos ajustados porque fijaban el prompt y los sellos de F32
  (`test_module_f29c_rotulista.py`, `test_module_f32.py`: ahora contra `ROTULISTA_*_F32` y con un Gemini falso).

## Parte B — guion nuevo de Vajont (commit `2f04030`)

`fase2b f8s3-vajont-f30 --plan-only --rotulista --rotulista-tope 1.50` (el ledger traía US$ 0.50 de tandas anteriores:
tope de la corrida = 0.50 + 1) → `lab/hyperframes/f34/GUION_PANTALLA.md/.json` (copia; el original en
`output/f8s3-vajont-f30/`) y `output/f8s3-vajont-f30/_fase2b_work/mezcla_preview.wav` (fuera de git). 404 s de pared.
Log `b/plan_only.log`. Sin `--gfx`, sin aprobar. Firefox cerrado (cierre normal) y RAM 17.1 GB antes del md5.

### B.1 lo que queda en pantalla (t_mp4)
- ch01: tarjeta «9 OCT 1963 · 22:39» 0:00 · sello PÁNICO 39.9 · reloj 9 OCT · 1963 76.0. Sin texto.
- ch02: recorte D117 «CONSEJO SUPERIOR DE OBRAS PÚBLICAS, 1943 · Aprobó la presa con 13 de 34 representantes presentes» 128.7 · punch 183.7.
- ch03: agua OLA 20 m 250.7 · punch 250.7 · sello AMENAZA 266.7 · ficha D71 «L'UNITÀ · Diario del Partido Comunista Italiano» 316.2.
- ch04: reloj 4 NOV · 1960 390.6 · ficha T39 «ROCA EN RIESGO DE DERRUMBE SOBRE ERTO · 50 millones de m³» 423.5 · sello AMENAZA 447.2 · punch 458.3 · agua COTA AUTORIZADA 715 m 464.1.
- ch05: punch 527.1 · sello AMENAZA 531.9 · reloj 9 OCT · 1963 596.5 · sello INMINENTE 660.1.
- ch06: punch 707.5 · sello SILENCIO 799.0 · ficha D192 «TÉCNICOS MUERTOS EN EL CENTRO DE CONTROL · 20 técnicos en el estribo izquierdo» 822.2.
- ch07: punch 877.1 · sello AMENAZA 897.6 · reloj 20 FEB · 1968 943.6 · ficha D245 «CONDENA A MONTEDISON, 1997 · 55.645.758.500 liras al municipio de Longarone» 994.2.

### B.2 — comparación línea por línea contra §1 (agente `simulador`, íntegra)

Solo lectura, sobre `lab/hyperframes/f34/GUION_PANTALLA.json`, los `rotulista_chNN.raw.json` y los `sellos_clima_chNN.json` de `output/f8s3-vajont-f30/_fase2b_work/`. Los segundos son t_mp4.

**Totales reales contra los esperados**

| | esperado §1 | salió | veredicto |
|---|---|---|---|
| textos | 9 | **5**: D117, D71, T39, D192, D245 | no |
| relojes + tarjeta | 4 + tarjeta | 4 (ch01 76.04, ch04 390.63, ch05 596.49, ch07 943.57) + tarjeta 0.0 | sí |
| aguas | 2 | 2 (ch03 250.73 OLA 20 m, ch04 464.06 COTA 715 m) | sí |
| sellos | 8 | **7**: PÁNICO, AMENAZA ×4, INMINENTE, SILENCIO | no |
| punches | 6 | 6 (ch02 183.67, ch03 250.73, ch04 458.27, ch05 527.13, ch06 707.5, ch07 877.07) | sí |

- El F34_REPORT de CC dice «6 textos» y «8 sellos». Ambas cuentas son erróneas.
- El chequeo «texto sin lectura» del propio guion dice «5 con su lectura».
- Cuento solo los eventos con `queda: true` de tipo ficha, recorte, lupa o persona.
- Los de lista de §1 que sí salieron: D117, T39, D192, D245. D71 salió en lugar de D49.

**ch01** (una sola escena, gancho)

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| texto D118 «LA PRESA DEL VAJONT · 266 m de alto», ancla «la presa que todos creyeron caída sigue en pie» (0:10) | sin texto | no | El modelo propuso D195 (idx 2, rank 1) y no D118. Ver caso 1. |
| tarjeta «9 OCT 1963 · 22:39» en 0:00 | 0.0, dur 3.0, fuente escaleta.pico T57+T66 | sí | |
| sello PÁNICO | PÁNICO 39.94 (crítico: suma) | sí | |
| reloj 9 OCT 1963 en «Longarone, Italia, nueve de octubre…» | reloj `9 OCT · 1963` 76.04, dur 8.32 | sí | |
| punches | cuatro punch_in del director cortados por `duplica` (el zoom_punch del pico los reemplaza) | n/a | |

**ch02**

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| D117 «ACTA DEL CONSEJO SUPERIOR · 13 de 34 representantes presentes» | recorte D117 128.7, dur 6.52, lectura 6.2: «CONSEJO SUPERIOR DE OBRAS PÚBLICAS, 1943 · Aprobó la presa con 13 de 34…» | sí (dato y ancla) | La etiqueta no es la esperada, pero el dato es el mismo y el crítico dio sí/sí/no estorba. «1943» queda en la etiqueta, aunque A.1 pedía no poner el año. |
| sellos CALMA, AMENAZA | ninguno | no | CALMA 162.28 cortado por crítico («tinte de muerte contradice la escena de vida»). AVISO 175.84 (beat 3) cortado por crítico («tinte de agua sobre montaña sin relación»). Los candidatos AMENAZA y los demás cayeron por el filtro «un sello por beat» (el beat ya tenía CALMA o AVISO). Ver caso 5. |
| punch | zoom_punch 183.67 | sí | |

**ch03**

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| D49 «ANCHO DE LA FISURA · Más de 1 metro» | ficha D71 «L'UNITÀ · Diario del Partido Comunista Italiano» 316.2 (dur 4.94, lectura 2.93) | no | D49 se propuso, pero se cortó. Ver caso 2. |
| agua `OLA · 20 m` (Pontesei) | nivel de agua OLA 20 m 250.73, dur 4.81, más zoom_punch en el mismo instante | sí | |
| sello AVISO | AMENAZA 266.66 (crítico: suma) | no | Gemini devolvió AMENAZA (`sellos_clima_ch03.json`); AVISO no apareció. |
| (no esperado) | T21 «VOLUMEN DEL DESLIZAMIENTO» cortado por «beat pico (4): solo a_pantalla» (250.56). T16 persona cortado por candado (256.32). | n/a | El pico del cap es el beat 4, donde A.1 solo deja pasar a_pantalla. |

**ch04**

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| T39 «ALERTA DE MERLIN, 1961 · 50 millones de m³» | ficha T39 423.52 «ROCA EN RIESGO DE DERRUMBE SOBRE ERTO · 50 millones de m³» (dur 3.78, lectura 3.6) | sí | |
| reloj 4 NOV 1960 | reloj 390.63, fuente T36, dur 4.43 | sí | |
| agua `COTA AUTORIZADA · 715 m` | 464.06, dur 4.5 | parcial | El bloque cruza el corte de escena 7 (468.03) por 0.5 s. Ver caso 6. |
| (no esperado) | sello AMENAZA 447.24; T33 cortado por lectura (103 caracteres piden 6.9 s y hay 5.0 s); D103, D104 y D68 cortados por «beat pico (7): solo a_pantalla». | n/a | |

**ch05**

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| Q50 recorte «Carta del municipio… continua aprensión y alarma» | ninguno | no | Se propuso y se cortó por lectura. Ver caso 3. |
| reloj 9 OCT 1963 | reloj 596.49, fuente T61, dur 12.0 | sí | |
| sello INMINENTE | INMINENTE 660.15 (crítico: suma); además AMENAZA 531.95 | parcial | El INMINENTE salió; el AMENAZA extra es de otro beat. |

**ch06**

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| D128 «MUERTOS, RECUENTO OFICIAL · 1.910 personas» | ninguno | no | Ver caso 4. |
| D192 «CENTRO DE CONTROL, ESTRIBO IZQ. · 20 técnicos muertos» | ficha D192 822.23 «TÉCNICOS MUERTOS EN EL CENTRO DE CONTROL · 20 técnicos en el estribo izquierdo» (dur 5.87, lectura 5.0) | sí | |
| sello COLAPSO | ninguno | no | Gemini sí devolvió COLAPSO 4 veces (`sellos_clima_ch06.json`). Cayeron por «un sello por beat: el beat 10 ya tiene INMINENTE», pero ese INMINENTE (710.09) fue cortado después por el crítico. Ver caso 5. |
| sello SILENCIO | SILENCIO 799.03 (crítico: suma) | sí | |

**ch07**

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| T85 «REMISIÓN A JUICIO, 1968 · 11 imputados» | ninguno | no | Ver caso 7. |
| D245 «TRIBUNAL DE BELLUNO, 1997 · 55.645.758.500 liras» | ficha D245 994.17 «CONDENA A MONTEDISON, 1997 · 55.645.758.500 liras al municipio de Longarone» (dur 11.76, lectura 4.8) | sí | |
| reloj 20 FEB 1968 | reloj 943.57, fuente T85, dur 12.0 | sí | |
| sello MEMORIA | AMENAZA 897.65 | no | `sellos_clima_ch07.json` trae NINGUNA, AMENAZA, ALARMA, RABIA y SILENCIO. MEMORIA nunca lo devolvió Gemini. |
| (no esperado) | D32 y T102 cortados por «un texto por beat: el beat 13 ya tiene D245» | n/a | |

**Casos a investigar**

1. **ch01 sin texto (D118).**
   - D118 estaba en el pool del gancho (`gancho:true`, `dice_voz:false`, beat 1). Era elegible: la voz no dice 266 m.
   - El modelo no lo propuso ni lo descartó. Descartó P49, P32, D132 y D195, y su único bloque fue D195 (idx 2, palabra 11, 18.82): «LONGARONE, 1963 · 1.269 de 1.328 habitantes murieron».
   - Ese bloque lo cortó el candado (`filtro: candado`): «no están en el texto fuente de D195: ['1963']». El 1963 es del propio rótulo que escribió el modelo.
   - No hubo segundo intento con otro dato. `rotulista_ch01.raw.json` tiene 2 intentos de llamada, y el `final` es el de D195.
   - Hay un dato que sí cabía en el gancho. Coincide con el 1.269 del pool (D195), pero la fecha la inventó el modelo.
   - El gancho tiene `a_pantalla` vacío: ningún ítem de ch01 está marcado a_pantalla. D118 depende solo de la elección del modelo, y esa regla no obliga a ninguno.
2. **ch03 D71 en vez de D49.**
   - El modelo propuso los dos con `rank 1` y `beat 5`: D71 en la oración 13 (palabra 6, 316.2) y D49 en la oración 17 (palabra 22, 348.92).
   - La regla «un texto por beat» cortó el segundo en orden de oración: «un texto por beat: el beat 5 ya tiene D71» (filtro `cantidad`). Ganó el que viene primero, no el de más valor.
   - D49 no es a_pantalla, y el handoff esperaba D49. Con la nueva regla de «dos si son dos datos marcados a_pantalla» tampoco aplica, porque ninguno de los dos está marcado.
   - D71 es un dato débil: solo aclara qué es L'Unità.
   - D49 tenía lectura 2.73 s. Habría cabido, en la escena 11 con corte en 360.44.
3. **Q50 (ch05).**
   - Se propuso en la oración 2, palabra 18 (527.2). `a_pantalla` lo marca como pedido.
   - Lo cortó la lectura: «147 caracteres piden 9.8 s y hay 5.0 s hasta el corte de escena (30.8 s)». El texto es de 147 caracteres porque el modelo reescribió la cita como «El municipio advierte que la población vive en continua alarma y reitera su preocupación por la seguridad».
   - Un recorte más corto de la carta habría cabido. A.1 pide «UNA línea corta», y esta salió de cuatro líneas.
   - La oración ancla (idx 2, «Desde el dos de octubre…», t0 15.24 del cap, 527.2 en mp4) está a 5.0 s del corte de la escena. No es un problema de reparto: la escena de esa oración es corta.
   - El ancla fue la oración equivocada: la carta se lee más adelante, en las oraciones 13 a 15 (T61).
4. **D128 (ch06).**
   - Salió del modelo bien: oración 24, palabra 4, `unidad: personas`, `valor: 1910`, rank 1, más D192 en la misma oración 24 y palabra 4.
   - En el guion se ve con `tipo: contador` y texto «Guglielmo» (812.71, escena 13). Lo cortó `gfx_realizador.finalizar`, no el rotulista: «contador de una cifra que dice la voz (repite el subtítulo)».
   - Confirma el bug de CC: el realizador quita todo `count_up`, también el del rotulista. La cifra 1.910 no la dice la voz en ese cap: el modelo lo anota en el `aporta` («que la narración nunca dice»).
   - El texto «Guglielmo» del evento es sospechoso. El campo `texto` del contador toma la palabra de la oración que ancla y no el valor.
5. **Sellos AMENAZA repetidos entre caps y sellos faltantes.**
   - AMENAZA sale en ch03 (266.66), ch04 (447.24), ch05 (531.95) y ch07 (897.65). La regla A.4 solo impide repetir dentro del mismo cap (`ya salió en el cap`), así que no hay filtro que lo corte.
   - Gemini inclina a AMENAZA. Cuento 1 en ch01, 5 en ch02, 2 en ch03, 3 en ch04, 3 en ch05, 3 en ch06 y 1 en ch07 sobre sus listas. Devolvió AVISO una sola vez y MEMORIA nunca. Con el modelo y el prompt tal cual, cada cap cae a AMENAZA, INMINENTE o ALARMA.
   - Fallan los esperados: ch02 CALMA y AMENAZA, ch03 AVISO, ch06 COLAPSO, ch07 MEMORIA.
   - El filtro «un sello por beat» corre antes que el crítico. Un sello que el crítico después corta igual ocupó el beat: ch02 CALMA (162.28), ch02 AVISO (175.84) y ch06 INMINENTE (710.09). Por eso los demás candidatos del beat quedan cortados y el cap pierde el sello. En ch06, COLAPSO (devuelto 4 veces) cayó por esto.
6. **Agua de ch04 que cruza el corte.**
   - 464.06 + 4.5 s = 468.56. La escena 7 corta en 468.03 (88.03 s del cap contra 88.56 s del bloque). El chequeo del guion lo marca ✗: «termina en 88.56 s y la escena 7 corta en 88.03 s». Son 0.53 s.
   - El mismo agua tiene además un chequeo ✗ «cifra que contradice la voz»: «715 m vs 650 m» y «715 m vs 700 m». La cota 715 m es la que dice la voz, y el chequeo la compara con otras alturas del relato. Es falso positivo, porque 650 y 700 son niveles anteriores del embalse; 715 es la cota autorizada.
   - El agua de A.5 no pasa por «lectura»: su duración 4.5 se fija sin mirar el siguiente corte.
7. **T85 en ch07.**
   - El modelo sí lo propuso: oración 11, palabra 20, beat 12, rank 1, «REMISIÓN A JUICIO · Contra 11 personas por el desastre del Vajont» (943.57, lectura 4.13).
   - Lo cortó «beat pico (12): solo `a_pantalla`». T85 no está marcado a_pantalla (solo D245 lo está en ch07). El spoiler no fue la causa, así que A.2 punto 3 se arregló pero el pico lo cortó por otro lado.
   - En el mismo instante, 943.57, salió el reloj `20 FEB · 1968` (fuente T85, dur 12.0). La fecha está pero el hecho (11 imputados) no. §1 esperaba ambos.

**Lectura**

- Salen bien los relojes, las dos aguas, los seis punches, la tarjeta, D117, T39, D192 y D245.
- Faltan 4 textos de los 9, y los 5 que salen no son idénticos a los esperados (D71 en lugar de D49).
- De los 4 faltantes, tres son decisiones de filtro (D49, T85 y D128) y uno es del modelo (D118). Ninguno es de reparto, salvo que D49 perdió contra D71 por orden de oración. Q50 es de lectura.
- Faltan sellos en ch02, ch03, ch06 y ch07 porque Gemini devolvió otra palabra o el sello cayó por el orden de filtros, no porque la regla no se cumpla.
- El «un sello por beat» antes del crítico cuesta sellos en ch02 y ch06.

### Chequeos del guion (copia de GUION_PANTALLA.md)

#### ✓ dos bloques en la misma escena
- ✓ ninguna escena con dos bloques (title card, textos y animaciones; en un cap de una sola escena, ninguna oración: nada solapado)

#### ✗ bloque que cruza un corte
- ✗ ch04 07:44.1 nivel de agua «715 m» termina en 88.56 s y la escena 7 corta en 88.03 s

#### ✓ texto sin lectura
- ✓ 5 con su lectura a 15 cps

#### ✓ pregunta de cierre sin lectura
- ✓ 7 con su lectura a 15 cps

#### ✗ cifra que contradice la voz
- ✗ ch04 07:44.1 «715 m»: 715 m vs 650 m («El cuatro de noviembre de mil novecientos sesenta el embalse estaba a »); 715 m vs 700 m («La recomendación que salió de ahí fue no pasar de los setecientos metr»)

#### ✗ a_pantalla
- ✗ 3/5 en pantalla
- ✗ ch05 Q50: cortó rotulista (lectura): sin tiempo de lectura: 147 caracteres piden 9.8 s y hay 5.0 s hasta el corte de escena (30.8 s)
- ✗ ch06 D128: cortó realizador: contador de una cifra que dice la voz (repite el subtítulo)

#### ✓ costuras con cuadro no negro
- ✓ ch01→ch02 (01:44.1): negro 100.60–101.60 s hasta el corte · voz callada (máx -120.0 dB) · el entrante sube desde negro (corte a negro, sin fadewhite)
- ✓ ch02→ch03 (04:04.7): negro 139.57–140.57 s hasta el corte · voz callada (máx -120.0 dB) · el entrante sube desde negro (corte a negro, sin fadewhite)
- ✓ ch03→ch04 (06:20.0): negro 134.27–135.27 s hasta el corte · voz callada (máx -120.0 dB) · el entrante sube desde negro (corte a negro, sin fadewhite)
- ✓ ch04→ch05 (08:29.0): negro 127.97–128.97 s hasta el corte · voz callada (máx -120.0 dB) · el entrante sube desde negro (corte a negro, sin fadewhite)
- ✓ ch05→ch06 (11:24.7): negro 174.67–175.67 s hasta el corte · voz callada (máx -120.0 dB) · el entrante sube desde negro (corte a negro, sin fadewhite)
- ✓ ch06→ch07 (14:18.9): negro 173.20–174.20 s hasta el corte · voz callada (máx -120.0 dB) · el entrante sube desde negro (corte a negro, sin fadewhite)

#### ✗ inicio de voz por cap
- ✓ ch01 · voz esperada 2.62 s · medida 2.62 s · llega a −18 dB en 2.65 s con rampa (100 ms previos: -26.0 dB)
- ✓ ch02 · voz esperada 107.18 s · medida 107.18 s · llega a −18 dB en 107.18 s con rampa (100 ms previos: -28.1 dB)
- ✓ ch03 · voz esperada 247.78 s · medida 247.78 s · llega a −18 dB en 247.78 s con rampa (100 ms previos: -28.4 dB)
- ✓ ch04 · voz esperada 383.06 s · medida 383.06 s · llega a −18 dB en 383.56 s con rampa (100 ms previos: -21.6 dB)
- ✓ ch05 · voz esperada 512.05 s · medida 512.05 s · llega a −18 dB en 512.07 s con rampa (100 ms previos: -24.5 dB)
- ✓ ch06 · voz esperada 687.81 s · medida 687.81 s · llega a −18 dB en 687.83 s con rampa (100 ms previos: -29.5 dB)
- ✗ ch07 · voz esperada 861.95 s · medida 861.95 s · llega a −18 dB en 861.94 s sin rampa (100 ms previos: -32.6 dB, bajo la voz presente -30.5 dB)

#### ✓ gancho no vacío
- ✓ ch01 beat 1 (gancho): sello «PÁNICO»; reloj «9 OCT · 1963»

#### ✓ inicio de música por cap
- ✓ ch01: title card 2.500 s · música medida 2.500 s · desvío +0.000 s (+0.00 cuadros)
- ✓ ch02: title card 104.100 s · música medida 104.100 s · desvío +0.000 s (+0.00 cuadros)
- ✓ ch03: title card 244.700 s · música medida 244.700 s · desvío -0.000 s (-0.00 cuadros)
- ✓ ch04: title card 380.000 s · música medida 380.000 s · desvío +0.000 s (+0.00 cuadros)
- ✓ ch05: title card 508.967 s · música medida 508.967 s · desvío +0.000 s (+0.00 cuadros)
- ✓ ch06: title card 684.667 s · música medida 684.667 s · desvío +0.000 s (+0.00 cuadros)
- ✓ ch07: title card 858.867 s · música medida 858.867 s · desvío +0.000 s (+0.00 cuadros)

#### ✓ tarjeta fecha-hora
- ✓ 00:00.0 «9 OCT 1963 · 22:39» · escaleta.pico T57 (fecha) + T66 (hora) · pasó

**Inicio de música por cap (A.7.2):** medido en la pista de música de la mezcla por correlación, los 7 caps arrancan
con su title card con desvío 0.000 s (en F32: ch02 4.6 s antes, ch07 14.8 s antes).

## Lo que queda abierto (entero)

1. **Textos: 5 de 9.** Por qué faltan, según la comparación del simulador:
   - **D128 (ch06):** lo saca `gfx_realizador.finalizar`, que borra TODO `count_up` («contador de una cifra que dice la
     voz») — también el del rotulista, que la voz no dice. Bug previo a F34 (desde F29); no lo arreglé porque el handoff
     no lo pide. Además el evento del contador en el guion muestra «Guglielmo» como texto (toma la palabra del ancla).
   - **T85 (ch07) y D49 (ch03):** el modelo los propuso; los cortan «beat pico: solo `a_pantalla`» (T85) y «un texto por
     beat» con D71 primero por orden de oración (D49). D71 es un dato débil. La regla «un texto por beat» elige por
     `a_pantalla` → `rank` → oración; con dos rank 1 gana el primero.
   - **Q50 (ch05):** el modelo escribió 147 caracteres pese al reemplazo 2 de A.1 («UNA línea corta») y lo ancló a una
     oración a 5 s del corte; cae por lectura.
   - **D118 (ch01, gancho):** era elegible (pool del video, la voz no dice 266 m) pero el modelo eligió D195 y le puso
     «1963» en la etiqueta: el candado lo cortó. El gancho queda con tarjeta + sello + reloj y sin texto.
2. **Sellos: 7 de 8, AMENAZA ×4** (ch03, ch04, ch05, ch07). Con el prompt literal de A.4, Gemini casi no devuelve CALMA,
   AVISO ni MEMORIA (MEMORIA nunca). A.4 solo prohíbe repetir dentro del cap, no entre caps. Y «un sello por beat» corre
   antes del crítico: un sello que el crítico después saca ya ocupó el beat (ch02 CALMA y AVISO, ch06 INMINENTE → ch06
   pierde COLAPSO). Para decidir (Omar/analista): ¿no repetir en todo el video? ¿el crítico antes del reparto?
3. **Agua de ch04:** cruza el corte de la escena 7 por 0.53 s (su duración no mira el corte) y el chequeo «cifra que
   contradice la voz» la marca contra 650/700 m (falso positivo: `contradicciones` compara la cota con el nivel del mar).
4. **Etiquetas con año:** D117 sale «…, 1943» y D245 «…, 1997». El reemplazo 2 prohíbe el año de publicación «en el
   dato»; esos años son del hecho y están en la etiqueta, así que no contradicen A.1, pero §1 los esperaba distintos.
5. **Tarjeta fecha-hora:** está en el plan de ch01 (`tarjeta_inicial`) y en el guion a 0:00, pero **no se dibuja**: el
   mp4 arranca con la intro de 2.5 s (primer cuadro congelado) y la tarjeta dura `title_dur` (3 s, sobre negro). Antes
   del render hay que decidir si la intro pasa a ser la tarjeta (y dura 3 s: todo se corre 0.5 s) o si la tarjeta dura
   lo que la intro. No inventé un número.
6. **Prefetch del rotulista:** con 7 llamadas en vuelo y el pool entero del gancho, el tope del peor caso frenó ch01 y
   ch02 en el prefetch; se rehicieron en fila (sin gasto de más), pero la corrida tardó más.
7. **DECISIONES:** el handoff cita líneas de las 14:28 (gancho) y 14:36 (tarjeta) que no existen en `DECISIONES.md`;
   «en caps de una sola escena la unidad es la oración» sigue como «pendiente de confirmar» y se aplicó porque A.3.2 lo
   pide. El gancho «1 reloj, 1 sello» se implementó sin número nuevo (el sello no cuenta contra el reloj del beat).
8. **`sellos_clima`** vive en `gfx_profiles/misterio.json` (fuera de git): para commitearla, Omar agrega al perfil
   `"sellos_clima": ["PÁNICO", "CALMA", "AMENAZA", "AVISO", "ALARMA", "INMINENTE", "COLAPSO", "SILENCIO", "RABIA", "MEMORIA"]`.
   `gfx_config` ahora acepta esa clave (y valida que sea una lista de palabras).
9. **El plan congelado (A.7.1) no está probado en un render real** (esta tanda no renderiza): el test simula un
   `--only-cap` con `--gfx` (director prohibido, HyperFrames falso) y comprueba que el md5 de los planes y la aprobación
   no cambian. El mapa de intensidad de la música ahora se aplica a una pieza que dura el segmento (no escuchado).
10. **Procesos viejos:** quedan vivos tres `grep` de monitores de la madrugada (PID 23064, 31616, 21988) y un bucle de
    espera de la tanda F30 C (`bash` PID 29824/500, desde las 0:36). No son de esta tanda; quise cerrarlos y el
    clasificador de permisos lo bloqueó: hay que cerrarlos a mano. No hay ningún `find` colgado; de esta tanda no quedó
    nada en segundo plano.
11. **Chequeo «inicio de voz» ch07 sin rampa:** previo a F34 (igual en F32).
12. **Mi primer resumen de B (en la versión parcial de este reporte) contó mal:** decía 6 textos y 8 sellos; son 5 y 7
    (corregido con la cuenta del simulador).

## Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | A.1 reemplazos 1, 2 y 3 literales (SYSTEM y formato del USER) | OK | `git diff fc889c9..HEAD script_engine/gfx_rotulista.py`: las líneas nuevas coinciden con el handoff. Las tres sustituciones están como pares antes/ahora y el resto del prompt no figura en el diff. |
| 2 | md5 `d90ae69a…` y vuelta al de F32 (`c9231e24…`) | NO VERIFICABLE | No recalculé el md5. Hay un test que deshace los reemplazos, y `test_module_f34.py` pasa 18/18 (lo corrí). El reporte (líneas 79-93) reporta ambos md5. |
| 3 | A.4: prompt de sellos literal | OK | `SELLO_CLIMA_PROMPT` en `gfx_rotulista.py`: las 4 líneas son idénticas al handoff. El reporte (líneas 112-118) lo pega y hay test de literalidad. |
| 4 | A.2: tres filtros con test del caso real (D117, D237, T85) | OK | `test_module_f34.py` pasa 18/18. |
| 5 | Sin números nuevos sin origen | OK con observación | El reporte declara las constantes y su origen (líneas 59-69). El handoff cita DECISIONES 14:28 y 14:36 y esas líneas no existen. El reporte lo dice (33-38 y abierto nº 7). «Una cosa por oración» sigue como propuesta pendiente en DECISIONES y se aplicó porque A.3.2 lo pide. |
| 6 | Sin render ni `--aprobar-guion` | OK | `b/plan_only.log` muestra solo `--plan-only` y el costo del rotulista. Tampoco hay `--gfx` ni procesos de render vivos. |
| 7 | `.env`, `config.py`, `_gpt_probe_analista` y `gfx_profiles/*` sin tocar en los commits | OK | `git ls-files .env config.py` da 0. El diff de los commits no toca `gfx_profiles`. `misterio.json` y `lexico_propuestas.json` figuran modificados pero sin commitear. (`gfx_profiles/` ya tenía archivos trackeados desde antes.) |
| 8 | Costos: Claude ≤ 1, Gemini ≤ 0.5 | OK | Claude 0.4633 y Gemini 0.2392. La suma (0.7025) coincide con `cost_tracker` en el log (0.7024). El reporte además admite una llamada de más a Gemini por un test viejo. |
| 9 | Tabla del simulador contra §1 pegada, línea por línea | OK | Reporte 157-286 y `b/comparacion_simulador.md` (11.8 KB). |
| 10 | F34_REPORT con el veredicto del revisor | PARCIAL | La sección existe (línea 388) pero está vacía. Se llena al pegar este veredicto. |
| 11 | `lab/ESTADO_SESION.md` actualizado | FALLA | El ESTADO commiteado dice «EN CURSO», «6 textos de 9» y «PENDIENTE: simulador, revisor». El reporte ya corrigió ese «6» a 5 textos y 7 sellos. `ESTADO_SESION.md` no figura como modificado en el árbol de trabajo, así que no se actualizó al cierre. |
| 12 | Ningún proceso en segundo plano vivo | PARCIAL | Esta tanda no dejó nada colgado. El reporte (abierto nº 10) admite 3 `grep` y 2 bucles `bash` viejos de otras tandas sin cerrar. Con `ps` no vi esos PID y no pude confirmar si siguen vivos. |
| 13 | A.8: DECISIONES commiteado, modelo `claude-opus-5-5`, `/tanda` paso 12, mapa | OK | `.claude/settings.json` tiene el modelo. DECISIONES, `tanda.md` y `MAPA_MODULOS.*` están en el diff. |
| 14 | A.8.2: `model: sonnet` en `revisor-handoff` y `simulador` | OK | `simulador.md` y `~/.claude/agents/revisor-handoff.md` lo tienen. El revisor vive fuera del repo, por eso no aparece en el diff. |
| 15 | §1 cumplida | FALLA (declarada) | Salieron 5 textos de 9 y 7 sellos de 8. Relojes, tarjeta, aguas y punches cumplen. El reporte lo declara con causas. |
| 16 | Suites verdes y md5 ch02 `38e5ba14` | OK | Suite rápida 58 (lo corrí y los logs coinciden). La amplia da 1021 y 5 fallos previos: 01b_pauses ×3 y m03_merge_timing ×2. El md5 está en `a/onlycap_ch02_nogfx.log`; no lo re-corrí porque implica render. |

Fuera de alcance: ninguno. Los archivos de `gfx_profiles` quedaron modificados sin commitear (`sellos_clima` queda para que Omar la commitee, como pide el handoff). `diag_234_cap4.py` y `f28a.log`, también modificados sin commitear, no son de esta tanda.

Riesgos que el contrato no cubre:
- La tarjeta fecha-hora está en el plan y en el guion pero no se dibuja en el mp4 (reporte abierto nº 5). Hay que decidir su duración antes de renderizar.
- El plan congelado (A.7.1) y la música alineada solo están probados con un render simulado. El único dato medido fue la mezcla de previsualización: 0 cuadros de desvío.
- Gemini inclina los sellos a AMENAZA (×4 entre caps). El orden «un sello por beat» antes del crítico cuesta sellos en ch02 y ch06.

Antes de commitear: actualizar `lab/ESTADO_SESION.md` (punto 11) y pegar este veredicto en el reporte (punto 10).

**Nota de CC después del veredicto:** los puntos 10 y 11 se resolvieron en el commit de cierre (este veredicto pegado y
`ESTADO_SESION.md` actualizado). Punto 12: al cierre los procesos viejos de otras tandas siguen como dice el abierto nº 10.
