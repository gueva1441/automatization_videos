# HANDOFF F67a — Lab: ¿el crítico de retención por API critica como el analista? (solo lab, solo texto, producción intacta)

Modelo → CC: Opus medium (script de lab, copia de `lab/hyperframes/f63/etapa_a_papel.py`). Decisión de Omar 2026-10-31 18:06 (DECISIONES.md): hacer el lab primero, con la entrada completa que ya recibe el papel. Auditado por subagente (12 correcciones aplicadas, v2); v3 repone `humano_en_escena` (§2).

## 0. Orden re-derivado
- ¿Construye sobre código que ya decidimos reemplazar? No: no toca producción; reusa la entrada del papel (`01e_pantalla.raw.json["entrada"]`, md5 `018f9cc1…`, la de F64 aprobada para producción) y `claude_helpers` tal cual.
- ¿Cambia el orden? Sí: la compuerta de narración (F67, pestaña NARRACIÓN) **espera** a este resultado. Voz/fotos de Wittenoom siguen en PARADA.
- Pregunta que responde: con la **misma entrada** que tuvo el analista, ¿Opus/Fable por API detectan por sí solos dónde se pierde al espectador y proponen DEBERÍA concretos sacados del archivo? El SYSTEM **no** nombra ningún hallazgo del analista (ch03, epílogo): si el modelo los encuentra, los encontró.

## 1. Constantes
| valor | origen | quién |
|---|---|---|
| topic `123bbb64-9fca-4395-8bf4-57d60e219ef1` (Wittenoom) | tema en producción | Omar |
| entrada = `data/scripts/_steps/<tid>/01e_pantalla.raw.json["entrada"]` menos `clima`; en `caps[*].oraciones[*]` se quita `caben` | existe (88.647 tokens medidos); es lo que recibe el autor del papel (DECISIONES 14:16) | derivado |
| seg/palabra 0,34 | `_steps/<tid>/01e_pantalla.json["seg_por_palabra"]["valor"]` | existe |
| métricas por cap (código, §3): `palabras = len(re.findall(r"\S+", texto))`; `segundos = round(palabras*0.34)`; `pct = round(100*palabras/total)`; `pct_acumulado = round(100*acum_exacto/total)` (último = 100); `anios_distintos = len(set(re.findall(r"\b(1[89]\d\d\|20\d\d)\b", texto)))`; `total_min = round(total*0.34/60, 1)` | derivado; límite aceptado: «2000» como cantidad cuenta como año | analista |
| referencia de métricas (etapa 1) | conteo del analista sobre el raw el 31-oct; tolerancia 2 % en palabras | analista |
| verificación: tabla de `_steps/<tid>/01b_verificacion.md` tal cual | existe | existe |
| brazos: O = `claude-opus-5-5` · F = `claude-fable-5-1`, esfuerzo `medium` = el mismo parámetro y valor que F63 pasa; temperatura la de F63 (no se toca); «corrida» = una llamada con SYSTEM y USER idénticos; 2 corridas por brazo, las 4 a la vez | ENTRADA 31d; ids en `hx.PRICES` | analista |
| `max_tokens` 100 000, streaming, sin esquema forzado | `claude_helpers` (F25a) | existe |
| escala de nota 1–10 con anclas (§4) | rúbrica del analista; **Omar confirma o cambia** | analista |
| costo esperado ≈ US$ 0,5 (O) · 1,2 (F) por corrida → ≈ 3,4; se informa, sin tope | PRICES × tokens | derivado |
| semilla del barajado ciego 67 | número de tanda | analista |

## 2. Módulos tocados
- **Nuevo:** `lab/hyperframes/f67/etapa_a_critico.py` (copia de `lab/hyperframes/f63/etapa_a_papel.py`: carga, 4 llamadas con `hx._post`, validación, markdown, ciego). Costo: `hx._track` solo si F63 ya lo usa sin escribir `data/cost_history.json`; si escribe, no se llama y el costo se calcula en el script con `hx.PRICES × tokens`.
- Producción: **nada**. mtimes de `data/scripts/_steps/<tid>/` antes y después en el reporte.
- **Corrección v3 (18:30, falla del analista):** `_para_modelo` del papel quita `humano_en_escena` de los beats, así que la entrada no lo trae y el script abortó bien. En la Etapa 1 el script lo **repone** desde `data/scripts/_steps/<tid>/01a_escaleta.json`: por cada `entrada.beats[i]`, `humano_en_escena = escaleta.beats[j].humano_en_escena` donde `escaleta.beats[j].n == entrada.beats[i].n`; asserta 13 beats emparejados. Es un dato más de la misma escaleta, no una regla.
- Al cargar, el script **asserta** que existen `entrada.escaleta_video.promesa_gancho`, `entrada.escaleta_video.pico`, `entrada.beats[*].humano_en_escena` (tras reponerlo), `entrada.archivo[*].id`, `entrada.caps[*].oraciones[*].idx`; si falta alguno aborta y reporta el nombre real. `idx` es por capítulo: toda referencia a oraciones es `(cap, idx)`.
- Todas las rutas relativas a la raíz del repo: `lab/hyperframes/f67/a/user.json`, `.../a/metricas.md`, `.../a/O_1.raw.json` (O_1, O_2, F_1, F_2), `.../a/O_1.md`, `.../a/validacion.md`, `.../a/ciego/critica_01..04.md`, `.../a/clave_ciego.json`, `lab/hyperframes/f67/F67a_REPORT.md`.

## 3. USER
`USER = json.dumps(payload, ensure_ascii=False, indent=None) + "\n\nFormato de salida (devolvé solo este JSON):\n" + FORMATO_SALIDA`, con `payload` en este orden:
```
{"caps": entrada.caps (sin "caben"),
 "beats": entrada.beats,
 "escaleta_video": entrada.escaleta_video,
 "archivo": entrada.archivo,
 "disputas": entrada.disputas,
 "metricas": {"seg_por_palabra": 0.34, "total_palabras": <int>, "total_min": <float>,
              "caps": [{"cap": "<chNN>", "titulo": "<…>", "oraciones": <int>, "palabras": <int>, "segundos": <int>,
                        "pct": <int>, "pct_acumulado": <int>, "anios_distintos": <int>}, …]},
 "verificacion": "<tabla de 01b_verificacion.md tal cual>"}
```

## 4. SYSTEM (completo, byte a byte; md5 en el reporte)
```
Sos el crítico de retención del canal Misterios Sepultados: documentales en español de historia oscura y lugares abandonados, de 10 a 12 minutos, narrados por una voz que cuenta hechos documentados (no investiga, no opina). Tu única medida es si el espectador de YouTube se queda hasta el final. No corregís estilo, ortografía ni hechos: eso lo hacen otros.

Recibís: la narración completa por capítulos con oraciones numeradas (`caps`, `idx` por capítulo); la escaleta (`beats`: función, emoción, dato central, pregunta abierta, cierre y `humano_en_escena` de cada beat; `escaleta_video`: promesa del gancho, loops con dónde se abren y se pagan, pico del video, cierre humano); el archivo del caso (`archivo`: todo lo que encontró la investigación, cada ítem con `id`, texto, fuente, fecha y el fragmento original); las `disputas` entre fuentes; `metricas` por capítulo calculadas por código (palabras, segundos, porcentaje del video, porcentaje acumulado, años distintos): usá esos números, no cuentes vos; y `verificacion`: oraciones que contradicen el archivo. Las contradicciones son un problema de credibilidad, no de retención: no bajan la nota; mencionalas solo si tocan la promesa del gancho, un loop o el pico.

Qué mirás, en este orden:
1. Gancho (primer capítulo): si en los primeros 30 segundos hay una promesa concreta y una pregunta que obliga a quedarse. La promesa está en `escaleta_video.promesa_gancho`; decí si la voz la cumple.
2. Hilo humano: el personaje del video es el de `escaleta_video` y de los beats con `humano_en_escena`. Por capítulo, decí si aparece en la voz (por nombre o por acción) y cuántas oraciones seguidas pasan sin él. Decí vos dónde ves un valle de retención y por qué.
3. Densidad: años, informes, cifras, instituciones y siglas por minuto, capítulo por capítulo. No hay un número mágico: compará los capítulos entre sí y contra el que mejor retiene.
4. Loops: cada pregunta que el video abre, dónde se paga y si el espectador la recuerda cuando llega el pago.
5. Pico: en qué porcentaje acumulado del video cae el pico (`escaleta_video.pico`), qué viene después, cuánto dura y si eso sostiene al espectador o no.
6. Re-ganchos: cómo termina cada capítulo; si el cierre promete algo del siguiente o solo cierra.
7. Cierre: si vuelve al gancho y lo paga.

Cómo escribís el DEBERÍA: por cada tramo que a tu juicio hace perder espectadores, decí qué oraciones salen (por `cap` e `idx`), por qué se va la gente ahí, y qué debería ir en su lugar: el texto que vos pondrías, con la misma voz, usando solo datos del `archivo` (citá sus `id`). Si la solución es sacar, decí qué se saca y qué se conserva para no perder un dato que otro capítulo necesita. Nunca inventes un dato ni una cita. Nunca toques la promesa del gancho, los re-ganchos ni el pico salvo para hacerlos más fuertes, y si los tocás, decilo en `riesgos`.

`reglas_generales_candidatas`: hasta 5 reglas de retención que saldrían de este caso y servirían para cualquier otro video del canal; `medible_como` dice cómo se verificaría en código con los campos de `metricas` o de `caps`.

Nota: 10 = no hay nada que sacar ni agregar; 8,5 = se publica sin tocar; 7 = se publica, pero tiene un valle claro que costaría espectadores; 5 = hay que reescribir capítulos; menos = no se publica. No premies el esfuerzo ni suavices: la nota sale de lo que mirás arriba, no de la rúbrica.

En el formato, los `<…>` son placeholders. `caps` lleva un objeto por capítulo, en orden ch01..ch07. Devolvé solo el JSON del formato pedido.
```

## 5. FORMATO_SALIDA (va al final del USER; límites acá, no como instrucción)
```
{"nota_total": <número 1-10, un decimal>,
 "resumen": ["<máx. 3 líneas: qué retiene, dónde se pierde al espectador, qué harías primero>"],
 "gancho": {"promesa_cumplida": <true|false>, "comentario": "<1 línea>"},
 "caps": [{"cap": "<chNN>", "nota": <número 1-10>, "personaje_en_voz": <true|false>,
           "oraciones_seguidas_sin_personaje": <entero>, "fuerte": "<1 línea>", "debil": "<1 línea>",
           "reengancho": "<1 línea: cómo termina y si promete algo del siguiente>"}],
 "loops": [{"pregunta": "<…>", "abre": "<chNN:idx>", "paga": "<chNN:idx | null>", "se_recuerda": <true|false>}],
 "pico": {"cap": "<chNN>", "pct_acumulado": <entero>, "segundos_despues": <entero>, "comentario": "<1 línea>"},
 "cierre": "<1 línea: si vuelve al gancho y lo paga>",
 "deberia": [{"cap": "<chNN>", "oraciones": [<idx>, …], "que_sale": "<1 línea>", "por_que_se_van": "<1 línea>",
              "deberia_texto": "<el texto nuevo completo del tramo, con la voz del canal>", "ids": ["<id>", …]}],
 "reglas_generales_candidatas": [{"regla": "<1 línea, para cualquier tema>", "medible_como": "<qué cuenta el código>", "por_que": "<1 línea>"}],
 "riesgos": ["<qué no tocar o qué se pierde si se aplica un DEBERÍA>"]}
```
Máximo 8 ítems en `deberia`, 5 en `reglas_generales_candidatas`.

## 6. Etapas (una variable por corrida: las 4 llamadas usan el mismo SYSTEM y USER; solo cambian modelo y corrida)
1. **Armar el USER** desde disco; guardar `a/user.json` y su md5; tabla de métricas en `a/metricas.md`. Comparar con la referencia del analista: ch01 161 pal/55 s/8 %/1 año · ch02 220/75/11 %/3 · ch03 523/178/27 %/7 · ch04 232/79/12 %/1 · ch05 292/99/15 %/7 · ch06 297/101/15 %/4 · ch07 216/73/11 %/6 · total 1.941 ≈ 11,0 min. Si alguna palabra difiere > 2 % o un conteo de años difiere, se anota en `metricas.md` y se sigue (no bloquea). Esta referencia **no** va al USER. Salida de la etapa: la tabla.
2. **4 llamadas a la vez** (`ThreadPoolExecutor`): O_1, O_2, F_1, F_2. Detección de JSON: quitar fences ```json si las hay, `json.loads`; si falla → 1 reintento idéntico; si falla otra vez → se guarda el raw y en la tabla va «sin JSON». Guardar `a/<brazo>_<n>.raw.json` (respuesta, usage, segundos, US$).
3. **Validar en código** cada salida: todos los `ids` existen en `archivo`; cada `(cap, idx)` de `deberia.oraciones` existe; `palabras_antes = Σ palabras(oración)` de esas oraciones y `palabras_despues = palabras(deberia_texto)` (mismo tokenizador de §1), calculados por el código; `cifras_sin_respaldo`: números en `deberia_texto` (`regex r"\d+(?:[.,]\d+)*"`, normalizados sin `.` ni `,`) que no estén en el conjunto permitido = números en `texto`+`contexto_fuente` de los ids citados ∪ números de las oraciones que reemplaza ∪ números de toda la narración; se reporta como lista, no como fallo (límite: números en palabras y romanos no se detectan). Tabla `a/validacion.md`: brazo · nota_total · notas por cap · n deberia · ids inválidos · oraciones inválidas · palabras antes→después por deberia · cifras sin respaldo · US$ · s.
4. **Markdown**: `a/<brazo>_<n>.md` completo (con modelo, costo, tokens, tiempo). **Ciego**: `a/ciego/critica_01..04.md` renderizados desde el JSON parseado con una plantilla fija (mismo orden de secciones y campos para los 4), **sin** modelo, costo, tokens, tiempo ni número de corrida; `random.Random(67).shuffle(orden)`; `a/clave_ciego.json = {"critica_01": "O_1", …}`; una corrida sin JSON ocupa igual su `critica_0N.md` con «sin JSON válido».
5. **Varianza** por brazo: diferencia de `nota_total` entre corridas y Jaccard entre los conjuntos `{(cap, idx)}` marcados en `deberia` por las 2 corridas; se reporta el valor y la intersección.
6. **Reporte** `F67a_REPORT.md`: tabla de §6.3, varianza, costo total, md5 del SYSTEM y del USER, mtimes antes/después (idénticos), «lo que queda abierto», veredicto íntegro del subagente `revisor-handoff` del repo. La clave del ciego **no** va en el reporte. Commit en `f11-guion-v4`: solo `lab/hyperframes/f67/`.

## 7. PARADA
Nada de producción se corre ni se escribe. Al terminar: pegar la tabla de §6.3 y avisar. El analista lee los 4 ciegos (límite asumido: con 2 corridas por brazo puede emparejar por estilo) y los compara con su revisión del 31-oct (ENTRADA 31d §1, que NO entra al USER ni al ciego); Omar decide si el crítico entra a la compuerta (F67).

## 8. Revisión del analista (simulación sobre Wittenoom, sin sesgar al modelo)
- Con `metricas` el modelo ve que un cap concentra 27 % del video y 7 años; con el criterio 2 y `humano_en_escena` tiene que decir si el personaje aparece ahí. No se le dice cuál.
- Criterio 5: el pico (beat 10, T64) cae en ch05, acumulado 74 % por palabras (el analista del 31-oct dijo 60 %); después vienen ch06+ch07 = 26 % ≈ 2,9 min. Con `pct_acumulado` el modelo debería dar 74; si da 60 está estimando.
- Invención en `deberia_texto`: la medimos (cifras sin respaldo), no se corrige a mano.
- Lo que no se traslada del chat (gusto acumulado) está como criterios de observación, sin nombrar hallazgos ni números fijos.
