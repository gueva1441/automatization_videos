# F50i — Aspecto del grupo sin el «estado» (polvo rojo), una variable, en lab · PARADA

Handoff `lab/hyperframes/f50i/HANDOFF_F50i_aspecto_sin_estado.md`, **md5 `61e9bbfbc4222984dc2a02a3e5220d0f`**.
- El primer prompt de Omar traía el md5 con una «c» de menos. Hice PARADA y avisé; Omar confirmó el md5 correcto.
- Rama `f11-guion-v4`.
- Producción no se tocó: ni `script_engine/`, ni el canon, ni topics_db, ni `03_visual.json`.
- Tope US$ 0,50; **gasto real US$ 0,28**. No hubo visión ni otro modelo.

## Qué pasó, en llano
- Las 4 fotos de F50h con manchas rojas (2/9, 4/11, 4/12, 5/8) se generaron de nuevo con C, cambiando una sola cosa: al aspecto de las familias españolas se le sacó «; women and children tanned and dusted red in Wittenoom».
- Hay 8 fotos nuevas, 2 por prompt. Cada hoja pone arriba las 2 de C de F50h y abajo las 2 de C′.
- El analista mira las hojas. Mi propia lectura va al final de la etapa única.

## Commits
| etapa | commit |
|---|---|
| 0 | `e93ea18` |
| única | `7211ff7` |
| reporte y ESTADO | este commit |

## Etapa 0
- md5 del handoff: `61e9bbfbc4222984dc2a02a3e5220d0f`.
- `DECISIONES.md`, al final y tal cual: se comprobó con código que es idéntica al texto del handoff.

  «- 2026-10-29 03:10 · **F50i:** prueba en lab de una variable: las 4 fotos de F50h con manchas rojas (2/9, 4/11, 4/12, 5/8) se regeneran con C y el aspecto de spanish_migrant_families sin «; women and children tanned and dusted red in Wittenoom» (2 fotos por prompt, tope US$ 0,50). Si las manchas desaparecen, F51 lleva C a producción y el canon separa el aspecto fijo del estado (polvo, enfermedad) · Omar · F50i»
- `lab/TOPE_TANDA.json` = 0,50 (fuera de git).

## Etapa única — `lab/hyperframes/f50i/f50i.py`
**Cómo se arma C′:**
- Es `f50h.armar_c` con `ESTILO_C` y el mismo post-proceso (`f50h.post`), sobre los casilleros del 03_visual.json vivo.
- El único cambio es el `appearance` de `spanish_migrant_families`, en una **copia en memoria** de `grupos`.
- Antes de cambiarlo, el script comprueba que el aspecto del canon sea el texto exacto del handoff.

**Verificación antes de gastar:**
```
prompts: C = F50h 4/4 · solo la cláusula 4/4 · diffs [[('replace', 'builds; women and children tanned and dusted red in Wittenoom.', 'builds.')] ×4]
```
- C rearmado es igual byte a byte al C de `f50h/PROMPTS_F50h.json`, en las 4 fotos.
- C′ es exactamente C con la oración del aspecto reemplazada.
- El diff palabra por palabra muestra solo la cláusula quitada: «builds; women and children tanned and dusted red in Wittenoom.» → «builds.».
- `PROMPTS_F50i.md` trae C y C′ enteros de las 4 fotos, con su diff.

**Fotos:**
- `f50h.generar_2` es `generar_1` de F49 con `num_images` 2, el mismo de F50h.
- Las 4 llamadas fueron en paralelo, con un reintento si hay error, en la sesión `f50i-lab`.
- Antes de lanzar, un freno comprueba que lo ya gastado más 4 × 2 × US$ 0,035 entre en el tope.
```
fotos: 2/9 ok · 4/11 ok · 4/12 ok · 5/8 ok (todas al primer intento) · cost_history f50i-lab = US$ 0.2800
```
- Quedan 8 png en `fotos/<cap>_<foto>/Cp_1.png` y `Cp_2.png`, fuera de git (`.git/info/exclude`).

**Hojas:** `hojas/hoja_<cap>_<foto>.jpg`, 4 jpg de 2896×1566, en git.
- Arriba, «C (F50h)»: las 2 fotos de la letra que la llave de F50h da a C. Leí la llave solo para eso, como dice el handoff, y la letra no se nombra acá.
- Abajo, «C′ (sin polvo)».
- Arriba de cada hoja va el ancla en español.
- No va a ciegas: es una comparación de una variable.

**Lectura de CC** (mirando las 4 hojas; no es la evaluación del analista):
| foto | C (F50h): manchas rojas | C′: manchas rojas |
|---|---|---|
| 2/9 (barco) | las 2 (cara, ropa y manos de madre e hijo) | ninguna |
| 4/11 (hospital) | 1 de 2 (cara y cuello de la mujer) | ninguna |
| 4/12 (foto del bautizo) | 1 de 2 (el vestido de la madre, leve) | ninguna |
| 5/8 (aeropuerto 1985) | las 2 (caras y ropa de las familias detrás) | ninguna |

**Ojo con la 5/8:** las 2 C′ no muestran la fila de familias detrás del agente. Queda solo el viajero y el oficial. Puede ser que sin la oración del polvo el modelo no las ponga, o puede ser azar con 2 fotos. No se puede separar con esta prueba.

## Costo real
| | registrado (cost_history `f50i-lab`) | real |
|---|---:|---:|
| 8 fotos × US$ 0,035 | 0,2800 | 0,2800 |

No hubo visión ni otros modelos. Tope 0,50.

## Verificación
- Suite rápida: 55 passed, 3 skipped.
- Suite amplia: 4 failed, 991 passed (las 4 de siempre). Logs en `f41/f50i`.
- ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46`, igual.
- No se tocó ningún archivo de producción.

## Lo que queda abierto
1. **El analista revisa las hojas.** Si las manchas desaparecen, F51 lleva C a producción y el canon separa el aspecto fijo del estado (polvo, enfermedad), según DECISIONES 03:10.
2. **Con 2 fotos por prompt** y sin `seed`, una foto limpia puede ser azar: en F50h la 5/8 ya tenía una versión limpia con el aspecto viejo. Según la lectura de CC, que no es la del analista, hay 8 de 8 limpias en C′ contra 6 de 8 manchadas en C.
3. **La 5/8 en C′ pierde la gente de fondo.** Para decidir si importa, hace falta mirar la escena que pide el casillero.
4. **El aspecto vive en el canon** (`people_groups[].appearance`, que escribe Opus). Hasta que F51 separe aspecto fijo y estado, el resto de las fotos del grupo sigue llevando «dusted red».
5. **La llave de F50h:** para armar estas hojas se leyó qué letra es C en estas 4 fotos, como manda el handoff. El resto de la llave sigue cerrada y Omar todavía no eligió en F50h.
6. **De antes:**
   - F50h: la elección de Omar por letra, y la visión registrada a tarifa fija;
   - F50g-B: Court, el corte Veo y `anio_final`;
   - la foto madre en F51;
   - Veo 3.1 en fal se apaga el 2026-11-17.

## Procesos
`f50i.py` y `verificar.sh f50i` corrieron en primer plano. No queda nada corriendo. No se cerró ningún programa de Omar.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | md5 del handoff en el reporte y la línea de DECISIONES tal cual, al final | OK | `md5sum` da 61e9bbfb…; la línea está al final de DECISIONES.md (+1 línea en el diff) |
| 2 | C′ cambia solo el appearance de `spanish_migrant_families`, sobre copia en memoria; el resto es `f50h.armar_c` + `ESTILO_C` + `f50h.post` | OK | `f50i.py:55-57` (`grupos_p`, con PARADA si el canon no es el texto del handoff), `:67-68` |
| 3 | C rearmado = C de F50h; el diff muestra solo la cláusula | OK | corrí `--sin-fotos`: "C = F50h 4/4 · solo la cláusula 4/4"; las 4 diffs son 1 `replace` («builds; women… Wittenoom.» → «builds.»). PROMPTS_F50i.md/.json quedaron sin cambios en git |
| 4 | `generar_2` = `generar_1` de F49 con `num_images` 2; 8 fotos en paralelo; costo | OK | `f50h.py:175-186` (payload de producción, `num_images` = 2); `ThreadPoolExecutor` en `f50i.py:102`; 4/4 ok al primer intento; 8 png en `fotos/`; `cost_history` `f50i-lab` = 0,28 (leído con fallback cp1252); tope 0,50 con freno previo |
| 5 | Hojas con C de F50h arriba (letra tomada de la llave) y C′ abajo, rotuladas, una por foto | OK | `f50i.py:109-142`; 4 jpg existen; en las que vi (5/8, 4/12) los rótulos son «C (F50h)» y «C′ (sin polvo)» |
| 6 | Producción intacta; sin `llave.json` ni png en git | OK | `git diff c3fffaf..HEAD --stat` solo toca DECISIONES.md y `lab/hyperframes/f50i/*`; `git ls-files` no devuelve ninguna llave ni png de f50h/f50i |
| 7 | Sin visión ni otros modelos; ningún número fuera de la tabla | OK | `f50i.py` no importa ningún modelo de visión; 0,035 × 8 = 0,28 y 0,50 salen de la tabla del handoff |
| 8 | La «lectura de CC» está marcada como tal, no como evaluación del analista | OK | el reporte la titula «Lectura de CC (…no es la evaluación del analista)». Contrasté 5/8 y 4/12 con las hojas y coincide: 5/8 C con manchas en las 2 y C′ limpias sin la fila de familias; 4/12 C con una sola manchada, leve, y C′ limpias |
| 9 | Suite rápida y candado ch02 | NO VERIFICABLE | las cifras del reporte (55 passed, 991 passed + 4 failed, md5 ch02 f792f3d4…) las tomé del reporte, no las corrí |
| 10 | ESTADO_SESION y veredicto de revisor-handoff en el reporte | PARCIAL | F50i_REPORT.md está sin commitear y su veredicto es todavía el marcador `{{VEREDICTO}}`; ESTADO se hace después, según el pedido |

Observaciones:
- En «Lo que queda abierto» (punto 2), «8 de 8 limpias en C′, contra 6 de 8 manchadas en C» sale de la lectura de CC. No lo dice en ese lugar, aunque la tabla de arriba sí lo marca como lectura.
- 5/8 en C′: se pierde la fila de familias del fondo. El reporte lo declara y dice que la prueba no puede separar causa de azar. No lo veo como falla.
- Aparte de los dos archivos untracked ya declarados (el reporte y `f41/f50i/`), hay un `ENTRADA_ANALISTA_2026-10-29d.md` untracked en la carpeta f50i. El reporte no lo menciona.

Fuera de alcance: ninguno en los commits. Sin commitear solo quedan el reporte, `f41/f50i/` y `ENTRADA_ANALISTA_2026-10-29d.md`.

Riesgos que el contrato no cubre: con 2 fotos por prompt y sin `seed`, 8 de 8 limpias no prueba la causa. El mismo aspecto ya había dado una versión limpia en F50h. Sin el polvo desaparece también parte del contenido de la escena (5/8), y el contrato no define cómo decidir eso.

### Adenda de CC (después del veredicto)
- **#9, suites y candado:** salen de `lab/hyperframes/f41/f50i/`, que va en el commit de este reporte. Rápida 55 passed; amplia 991 passed + las 4 previas; ch02 `f792f3d483a1fa42daed5f7f0e054f46`.
- **Observación 1:** el punto 2 de «Lo que queda abierto» dice ahora que el 8/8 y el 6/8 son lectura de CC.
- **`ENTRADA_ANALISTA_2026-10-29d.md`:** es del analista, no de esta tanda. No se toca ni se commitea.

