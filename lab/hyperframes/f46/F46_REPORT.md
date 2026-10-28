# F46 — Fotos de época: A/B del cap 2 de Wittenoom (REPORTE)

CC · 2026-10-28 · rama `f11-guion-v4` · handoff `lab/hyperframes/f46/HANDOFF_F46_fotos_de_epoca.md` (md5 `b217a820cce265178f93d3dc3c31ce85` ✓). Paso 0 → Parte 1 → Parte 2 sin parada entre partes. Tope de la tanda US$ 3,00; **gasto real US$ 1,3051**, leído de `cost_history`. **PARADA:** no se elige variante ni se toca producción.

## Qué se corrió
- **Paso 0** (`e8ebb67`): la línea del handoff en `DECISIONES.md`, tal cual. `lab/TOPE_TANDA.json` = 3,00 (no commiteado).
- **Parte 1** (`python lab/hyperframes/f46/f46_corridas.py prompts`, 02:09:34 → 02:12:00, US$ 0,1851):
  - Canon B: `extract_visual_canon` con 147 «facts» sacados de la ficha (65 hechos, 71 eventos de la cronología y 11 escenas). Va en `canon_B.json`; nada a `topics_db`.
  - B1: el flujo de producción del cap (`m03_visual._render_prompts_seedream`: 1 llamada de slots a Pro, el tejido en Flash, las reglas F8 y el estilo al principio con el año de la foto). Lleva el canon B y el `beats_block` de producción más las líneas WHEN / WHERE / CASE-FILE SCENES. Anclas y beats salen tal cual de `03_visual.json` (`force_assign`).
  - B2: los slots de B1, sin otra llamada a Pro, tejidos por el mismo `_fluidify_with_leakage_guard`/`_fluidify_item` con la formula del handoff:
    - sin `mood`;
    - el slot `style` = `style_head(<año>)`;
    - el código no antepone el estilo;
    - el mismo candado de cifras y las mismas reglas F8 después.
- **Parte 2** (`… fotos`, 02:12:5x → 02:13:52, US$ 1,12):
  - 32 fotos (16 de B1 y 16 de B2) con `asset_manager._generate_image_raw`: payload de producción, Seedream 5 Lite text-to-image, 2560×1440.
  - En paralelo con `FLUX_MAX_WORKERS` (20), freno antes de cada foto.
  - `image_grade.grade` a `_graded.png`. **0 rechazadas**, 0 con NSFW.
  - Hojas: `python lab/hyperframes/f46/f46_hoja.py` (lo escribió un subagente Sonnet en paralelo).
- **Producción no se editó.** Las funciones se importan; dentro del proceso del lab se reemplazan `v3img.beats_block` (en B1), el año que recibe `_f8_finish_item` (B1, por foto) y `v3img.wrap_style` (B2, no antepone).
  - El freno envuelve `call_flash_json`/`call_pro_json` de m03 y step_4e, y cada foto.
  - **Nada en `data/` salvo `cost_history.json`** (id `f46-lab`), nada en `output/` (las A solo se leen), nada en `topics_db`.

### Ajuste respecto de la primera versión del script (antes de gastar)
El WHEN con `ev.item_date` perdía las fechas incompletas («1958», «1962-08», «1930s»). Pasé a la `fecha` del item tal cual, como dice el handoff. Así coincide exacto con la simulación del analista:
- beat 2 → WHEN 1958, 1961-09-16, 1962-09-20, 1962-09-24 · WHERE Madrid, Australia · escena 8;
- beat 3 → WHEN 1930s, 1962-08 · WHERE Australia · escenas 0 y 1.

## Salida de la parte 1 — `PROMPTS_AB.md` (tablas; los 48 prompts enteros están en el archivo)
## Canon de época: viejo → nuevo

| clave | viejo (topics_db, 10 verified_facts) | nuevo (ficha) |
|---|---|---|
| primary_decade | 1960s | 1960s |
| spans | 1937-1966 | 1937-2026 |
| clothing | Practical, durable workwear for miners (overalls, flannel shirts, leather boots); simple, often homemade dresses or skirts and blouses for women; shorts, shirts, and sturdy shoes for children. Lack of personal protective equipment for asbestos exposure is a defining visual element. | Miners' work clothes (heavy-duty fabrics, possibly some dust masks early on), casual desert attire for families (light cottons, short sleeves, trousers/skirts). Bureaucrats and officials in more formal mid-century attire (shirts, ties, trousers, dresses) when visiting or in cities. |
| demographics | Primarily Australian and European (notably Spanish) miners and their families, including children. A significant presence of Banjima Aboriginal people as Traditional Owners, affected by the contamination. Clothing reflects a remote, working-class town in a hot climate during the mid-20th century. | Australian, Spanish, and other European immigrant workers and their families in a remote mining town. Miners in work attire, women and children in everyday desert clothing. (Sourced from verified facts and visual references) |

## Tabla por foto

| foto | beat | año | palabras A / B1 / B2 | año en palabra n.º A / B1 / B2 | primer lugar en palabra n.º A / B1 / B2 | sujeto+setting nombran época · lugar: A / B1 |
|---|---|---|---|---|---|---|
| 1 | 2 | 1961 | 200 / 169 / 149 | 5 («1961») / 5 («1961») / 14 («1960s») | 72 («Madrid») / 65 («Madrid») / 47 («Madrid») | sí · sí / sí · sí |
| 2 | 2 | 1961 | 183 / 168 / 144 | 5 («1961») / 5 («1961») / 64 («1962») | 79 («Madrid») / 81 («Madrid») / 62 («Madrid») | sí · sí / sí · sí |
| 3 | 2 | 1961 | 203 / 175 / 156 | 5 («1961») / 5 («1961») / 49 («1960s») | — / — / — | sí · no / sí · no |
| 4 | 2 | 1961 | 182 / 176 / 149 | 5 («1961») / 5 («1961») / 71 («1961») | — / — / — | no · no / no · no |
| 5 | 2 | 1961 | 173 / 152 / 116 | 5 («1961») / 5 («1961») / 63 («1961») | — / — / — | no · no / no · no |
| 6 | 2 | 1961 | 172 / 177 / 148 | 5 («1961») / 5 («1961») / 81 («1961») | — / 76 («Wittenoom») / 36 («Wittenoom») | sí · no / no · sí |
| 7 | 2 | 1961 | 195 / 152 / 136 | 5 («1961») / 5 («1961») / 73 («1961») | — / — / — | no · no / no · no |
| 8 | 3 | 1961 | 197 / 177 / 134 | 5 («1961») / 5 («1961») / 52 («1962») | — / — / — | no · no / sí · no |
| 9 | 3 | 1961 | 190 / 142 / 118 | 5 («1961») / 5 («1961») / 2 («1960s») | — / — / — | sí · no / sí · no |
| 10 | 3 | 1961 | 182 / 179 / 145 | 5 («1961») / 5 («1961») / 80 («1961») | — / — / — | no · no / no · no |
| 11 | 3 | 1961 | 192 / 174 / 157 | 5 («1961») / 5 («1961») / 83 («1961») | — / — / — | no · no / no · no |
| 12 | 3 | 1961 | 169 / 182 / 146 | 5 («1961») / 5 («1961») / 47 («1960s») | — / — / — | sí · no / sí · no |
| 13 | 3 | 1961 | 200 / 180 / 168 | 5 («1961») / 5 («1961») / 86 («1961») | 70 («Pilbara») / 38 («Pilbara») / 52 («Pilbara») | sí · sí / no · sí |
| 14 | 3 | 1961 | 220 / 179 / 151 | 5 («1961») / 5 («1961») / 83 («1961») | 93 («Wittenoom») / 64 («Wittenoom») / 50 («Wittenoom») | sí · sí / no · sí |
| 15 | 3 | 1961 | 194 / 179 / 147 | 5 («1961») / 5 («1961») / 47 («1937») | 72 («Pilbara») / — / — | no · sí / no · no |
| 16 | 3 | 1961 | 217 / 189 / 167 | 5 («1961») / 5 («1961») / 97 («1961») | 73 («Wittenoom») / 78 («Wittenoom») / 63 («Wittenoom») | no · sí / no · sí |

## Contexto por beat (WHEN / WHERE / CASE-FILE SCENES)

- beat 2 (ids T34, T37, T38, Q12, Q13, D83): WHEN 1958, 1961-09-16, 1962-09-20, 1962-09-24 · WHERE Madrid, Australia · escenas: Lugar de la entrevista de María Bernal, no precisado en el pasaje. · María Bernal. · La entrevista la muestra rodeada de fotografías familiares de tono sepia.
- beat 3 (ids Q14, Q15, T36, D82, D35, D76): WHEN 1930s, 1962-08 · WHERE Australia · escenas: Barco desde Málaga hacia Australia, durante el viaje de la familia De Juan-Barroso. · Víctor Calvo y su familia. · Calor intenso y mareos durante la travesía. | Pista de aterrizaje y acceso a las viviendas de Wittenoom. · Víctor Calvo y su familia recién llegada. · Movimiento del avión, tierra muy roja, polvo por todas partes y viviendas de chapa, madera y uralita.

Lo que dice la tabla:
- **Largo de los prompts** (palabras, mínimo/mediana/máximo): B1 142/177/189 y B2 116/148/168. A está entre 169 y 220.
- **«faceless»:** en los 16 de B1 (viene del estilo de los slots) y en 0 de B2.
- **El año 1961** está en la palabra 5 en A y en B1 (el estilo va primero). En B2 aparece más adelante (palabra 47–97), y en 7 fotos lo primero que aparece es una década o un año del sujeto («1960s», «1962», «1937»).
- **El lugar casi nunca entra en el prompt:** «Madrid», «Wittenoom» o «Pilbara» aparecen en 6 fotos de cada variante. WHERE «Australia» del beat 3 no se tejió en ninguna.
- **El año de la foto es 1961 en las 16:** el beat 2 lo saca de su `dato_central` (T34, 1961-09-16) y el beat 3 no tiene fecha en el suyo (Q14), así que cae a `topic_year` = 1961, como dice el handoff. Los dos beats del cap terminan con el mismo año.

### Avisos del flujo de producción en esta corrida (no son errores del lab)
- **Reglas F8 «menor en daño» DEGRADADAS:** B1 en las fotos 3, 6, 7, 8 y 16; B2 en la 8. La regla saca la frase que dispara. El cap 2 tiene niños en el beat (Víctor Calvo de chico), y el canon nuevo dice «women and children».
- **Guarda 1 DEGRADADA en B2 foto 15:** el hard fact «150.000» pedía unidad de masa en inglés; en 3 intentos el tejido puso «150.000 fibers» (B1: «150.000 tons») y Guarda 1 aceptó la prosa así.

## Salida de la parte 2 — hojas y costos
- Hojas A | B1 | B2 (las `_graded`), 2560 px de ancho: `lab/hyperframes/f46/hoja_01-04.jpg`, `hoja_05-08.jpg`, `hoja_09-12.jpg`, `hoja_13-16.jpg`.
- Fotos: `lab/hyperframes/f46/B1/` y `B2/` (`ch02_img_NN.png` + `_graded.png`). **No están en git** (unos 190 MB): quedan en el disco.
- Rechazadas por el filtro de seguridad: **ninguna** (`fotos_resultado.json`).

### Costos reales (`data/cost_history.json`, `video_id = f46-lab`; detalle por llamada en `COSTOS.md`)
| servicio | llamadas | US$ |
|---|---|---|
| Gemini 2.5 Flash (canon 1 + tejidos y re-tejidos de B1 y B2) | 42 | 0,0489 |
| Gemini 2.5 Pro (slots de B1, una vez) | 1 | 0,1363 |
| fal.ai Seedream 5.0 Lite t2i | 32 | 1,1200 |
| **Total** (2 reportes: parte 1 y parte 2) | | **1,3051** (tope 3,00) |

## Lo que queda abierto (entero)
- h1. **Elegir variante:** lo deciden Omar y el analista mirando las hojas. No se tocó producción.
- h2. **El canon B cambió más que la ropa:**
  - `spans` pasó de 1937-1966 a **1937-2026** (la ficha llega hasta hoy);
  - `documented_people` es otra lista (Eric Saint, Daniel Écija…), y entra al prompt de slots y al scrub de nombres;
  - trae una clave nueva, `central_subject`, que B1 no usa.
  En B1 el canon cambió entero, no solo `clothing`/`demographics`/`primary_decade`.
- h3. **El año de la foto es el mismo en todo el cap** (1961) porque el beat 3 no tiene fecha en su `dato_central`. Su WHEN dice 1930s y 1962-08. La regla «año del `dato_central`» deja afuera las fechas de los `datos_apoyo`.
- h4. **«faceless» sigue en los 16 de B1** (viene del slot `style` que escribe Pro) y no está en B2 (el slot se reemplaza). Además B2 no lleva la cola «35mm film grain, muted documentary colors.» (la pone `wrap_style`, que en B2 no antepone ni agrega). Son dos diferencias más entre B1 y B2, además del orden y el `mood`: B1→B2 mide la estructura entera (orden, `mood`, estilo como slot sin «faceless» y sin cola), no un solo cambio.
- h5. **El lugar del WHERE casi no llega a la prosa** (Australia: 0 de 9 en el beat 3). El dato entra al pedido de slots, pero Pro y el tejido lo dejan afuera.
- h6. **Reglas F8 «menor en daño» que sacan frases** (6 fotos entre B1 y B2): hay que mirar en las hojas si a alguna le falta el sujeto.
- h7. **B2 foto 15: la cifra está con la unidad equivocada** («150.000 fibers», cuando eran toneladas: B1 dice «150.000 tons»). Guarda 1 la dejó pasar degradada.
- h8. **La escena 8 (entrevista de María Bernal, fotos sepia)** era el riesgo anotado por el analista: entró al bloque del beat 2 (fotos 1–7). Hay que ver en las hojas si alguna foto mete la entrevista o el sepia.
- h9. **Una corrida por variante:** las diferencias pueden ser varianza del modelo (Pro, Flash y Seedream).
- h10. **Las PNG de B1/B2 no están en git** (unos 190 MB); `lab/TOPE_TANDA.json` (3,00) tampoco.
- h11. **El form de Omar siguió corriendo** con Wittenoom (ahora en `m09_packaging --review`). No se tocó.

## Procesos y subagentes
- Subagentes: el de `f46_hoja.py` y el revisor, terminados.
- Shells en segundo plano: los de la parte 1 y la parte 2, terminados.
- No cerré ningún proceso de Omar. Al cerrar seguían vivos su `qa_studio_server`, su `run_pipeline --research` y su `m09_packaging`.

## Veredicto de revisor-handoff (íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | md5 del handoff = b217a820… | OK | `md5sum` da b217a820cce265178f93d3dc3c31ce85 |
| 2 | Paso 0: línea en DECISIONES.md | OK | `DECISIONES.md:128` es el texto del handoff; commit e8ebb67 (+1 línea) |
| 3 | Producción intacta; nada en output/ ni topics_db | OK | `git diff --stat` solo muestra `diag_234_cap4.py` y `f28a.log`, que ya estaban modificados en el snapshot inicial, y `lab/TOPE_TANDA.json`, que es del lab. `lab/ESTADO_SESION.md` también aparece modificado (pedido por el handoff). `f46_corridas.py` solo importa y reemplaza funciones dentro de su proceso (`beats_block`, `_f8_finish_item`, `wrap_style`). |
| 4 | B1 difiere de A solo en la entrada | OK | Misma ruta `_render_prompts_seedream`. Anclas y beats salen de 03_visual con `force_assign`. El canon sale de la ficha con 147 facts. El año por beat es 1961 en las 16 fotos, igual que A. |
| 5 | Bloque de beats B1: solo agrega datos | OK | `f46_corridas.py:151-168` agrega tres líneas (WHEN, WHERE, CASE-FILE SCENES) y no escribe ninguna regla. El WHEN coincide con la simulación del analista (beat 2: 1958… 1962-09-24; beat 3: 1930s, 1962-08). |
| 6 | B2 difiere de B1 solo en la estructura | PARCIAL | Los slots son los de B1, la formula es la del handoff sin `mood`, `style = style_head(año)` y `wrap_style` no antepone (`:213-231`). Pero la cola «35mm film grain, muted documentary colors» está en las 16 de B1 y en 0 de B2. El reporte no lo menciona. Además «faceless» sale solo de B1 (el reporte lo declara en h4). |
| 7 | Freno antes de cada llamada paga | OK | `freno()` envuelve Flash, Pro, canon y cada foto, con reserva de costo (`:82-92`, `:327`). No hubo PARADA. |
| 8 | Costos reales contra el tope | OK | `COSTOS.md`: Flash 0,0489 + Pro 0,1363 + fal 1,1200 = 1,3052, contra el total de 1,3051 por redondeo. Tope 3,00. Coincide con el reporte y con `parte2.log`. |
| 9 | PROMPTS_AB.md: 3 prompts enteros por foto, tabla de palabras, año y lugar, diff de canon | OK | 16 secciones «### Foto», 16 A, 16 B1 y 16 B2. Tabla y diff de canon presentes. Faltan las columnas «sujeto+setting nombran época o lugar» para B2; con los mismos slots que B1 no cambian. |
| 10 | 32 fotos con payload de producción, grade y workers = FLUX_MAX_WORKERS | OK | `parte2.log` muestra 32 «ok» y 0 rechazadas. Hay 16 `_graded` en B1 y 16 en B2. |
| 11 | 4 hojas A\|B1\|B2, ≤ 2560 px, rótulo con n.º y 8 palabras | OK | Las 4 hojas miden 2560×1844. Miré `hoja_13-16.jpg`: columnas y rótulos correctos. |
| 12 | Números del reporte = PROMPTS_AB.md y COSTOS.md | PARCIAL | Tablas, costos y conteos coinciden. Falla h7: el reporte dice que B2 foto 15 quedó «sin la cifra 150.000», pero el prompt B2 dice «with 150.000 fibers visible». La cifra sí está, con unidad equivocada (B1 dice «150.000 tons»). |
| 13 | «Lo que queda abierto» entero | OK | h1–h11 presentes. h7 es inexacto (ver #12). |
| 14 | F46_REPORT.md, ESTADO_SESION y commit | PARCIAL | El reporte existe, pero la línea 112 aún tiene `{{VEREDICTO}}`. ESTADO_SESION está actualizado. El commit no está hecho; no corresponde antes del veredicto. |
| 15 | Sin pytest ni acciones sobre procesos de Omar | NO VERIFICABLE | Lo declara el reporte. No hay evidencia en contra. |

Fuera de alcance: ninguno. Los tres archivos modificados que no son de la tanda ya estaban así al inicio.

Riesgos que el contrato no cubre:
- B2 pierde la cola de estilo y «faceless», así que A→B1→B2 mezcla más de una variable. Eso pesa al elegir variante.
- Una sola corrida por variante: las diferencias pueden ser varianza del modelo (h9).
- Falta corregir h7 en el reporte («cifra presente con unidad errónea» en vez de «sin cifra»).

### Adenda de CC (después del veredicto)
- **#6 y riesgo 1:** h4 ahora dice que B2 tampoco lleva la cola de estilo (`wrap_style` en B2 no agrega nada). B1→B2 mide la estructura entera (orden, `mood`, estilo como slot sin «faceless» y sin cola), no un solo cambio.
- **#12 / h7:** corregido, con el aviso de la Guarda 1 incluido: en B2 foto 15 la cifra está, con la unidad equivocada («150.000 fibers»; B1 «150.000 tons»).
- **#9:** la columna «sujeto+setting» va para A y B1 porque B2 usa los mismos slots que B1.
- **#14:** el veredicto ya está pegado; el commit va con este reporte.

