# F4b_REPORT — Marca del canal + director inteligente

Rama `f3-lab-identidad` (sobre F4 `56085d1`) · `main` = `43f528a` intacta · decisiones en `DECISIONES_F4b.md`.

## §0 Marca del canal — tira para Omar
`tira_marca_canal.jpg` (3 candidatos: esquina 4 % a opacidad 0.55, esquina ampliada, grande). Enviada a Omar; espera su elección. Implementación (§0.3) después de que elija.

---

## §1 Director de intensidad

**Qué hay:** `script_engine/gfx_intensity.py` (token `intensity_director`). Una llamada Flash por cap marca intensidad por frase, frase pico y 3–5 palabras de carga copiadas de la narración. El validador descarta lo que no es literal o no es una categoría del perfil. Esas cargas se suman al léxico del cap (moods, golpes de zoom, pico) y el pico sale de la frase más intensa. Las palabras nuevas van a `gfx_profiles/lexico_propuestas.json` (14 de Orleans).

**Orleans (antes → ahora, palabra del pico):**

| cap | pico F4 (léxico) | pico F4b (intensidad) | frase |
|---|---|---|---|
| ch01 | sin pico | «misterio» | «Pero lo que sucedió después, es un misterio que nadie quiso ver.» |
| ch02 | «sumergidos» | «sumergidos» (cifra de agua a ≤ 0.1, E8) | «…sumergidos bajo 4.6 metros de agua putrefacta.» |
| ch03 | sin pico | «celdas» | «En celdas herméticamente cerradas, sin salida, sin luz, el agua oscura subiendo sin cesar.» |
| ch04 | sin pico | «oscuridad» | «Sus pequeñas vidas se desdibujaron en el caos, en la oscuridad y en el abandono…» |
| ch05 | «cuerpos» | «cuerpos» | «Cuerpos sin vida a la deriva en la misma agua pútrida…» |
| ch06 | sin pico | «desvanecieron» | «¿Y para aquellos quinientos prisioneros, cuyas vidas se desvanecieron sin rastro oficial…» |
| ch07 | sin pico | «borrados» | «Más de quinientos prisioneros jamás figuraron en los registros de evacuación, borrados…» |

Picos: 7 de 7 (antes 2 de 7).

Verificado con `plan_peak` sobre los datos reales (sin escenas: el bloque grande se decide en el render, con visión): ch02 «frase 4 (intensidad 0.85, máx 0.95) por la cifra de agua» → nivel de agua.

**Veredicto revisor-handoff (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

Tests corridos por mí: 264 passed (comando exacto del pedido). No corrí fase2b. No pude ejecutar Flash real; la evidencia de la corrida real es solo el JSON.

| # | Requisito (HANDOFF §1 / §6) | Estado | Evidencia |
|---|---|---|---|
| 1 | Una llamada Flash por cap, con contexto anterior/siguiente | OK | gfx_layer.py:~470-475 pasa prev2 = últimas 2 frases del cap anterior y next2 = primeras 2 del siguiente. gfx_intensity.build_prompt las incluye. El JSON de Orleans trae 7 entradas (ch01–ch07). |
| 2 | JSON pico / cargas / intensidad por frase | OK | SCHEMA y validate() en gfx_intensity.py. Exige una cifra por frase. |
| 3 | Validador: word literal, categoría del perfil (activas o reserva), peso 1–3 | OK | validate(): `w in sents[si].split()` normalizado, `cat in moods_all` (se pasa ACTIVE_PROFILE["moods"] completo), `1<=peso<=3`. Descarta carga por carga. test_validador_literal_categoria_peso. |
| 4 | Fallback al léxico tras 2 fallos | OK | ATTEMPTS=2. Devuelve None, y augmented_moods(active, None) deja el léxico de hoy. test_fallback_tras_dos_fallos_y_cache. |
| 5 | Léxico fijo como piso | OK | augmented_moods copia el léxico activo y solo suma. Conserva el peso mayor. |
| 6 | Propuestas en gfx_profiles/lexico_propuestas.json, promoción con 2 videos | PARCIAL | record_proposals implementa la lógica y tiene test. El archivo no existe en el repo (gfx_profiles/ no lo tiene). El JSON de Orleans muestra 14 palabras nuevas que deberían estar ahí. La promoción edita misterio.json sin commit automático. DECISIONES E10 lo declara: el commit lo hace CC a mano. Eso se aparta del texto del contrato. |
| 7 | Pico garantizado 1 por cap, frase de mayor intensidad, empate por más cargas de peso 3 | PARCIAL | peak_sentence usa clave (intensidad, n_peso3, -i). OK. Pero plan_peak sustituye esa frase por una con cifra de agua si está a ≤0.1 de la máxima (WATER_PEAK_TOL, gfx_peak.py). Es una excepción al contrato, documentada en DECISIONES E8 y pedida por conservar el agua de ch02. Además, si no hay bloque grande, el pico queda con block=None y la frase marcada. "Garantizado" vale solo como marca. |
| 8 | Cache por hash de narración | OK | cache gfx_intensity_<cap>.json con hash sha1 de la narración. Si cambia el hash, re-llama. Probado en el mismo test del fallback. La clave es por cap en work_dir (que es por video), no por tupla explícita. |
| 9 | Límites por cap sin cambios | OK | No se tocaron max_per_cap ni el intervalo de 20 s. place_emphasis solo cambia la fuente del léxico a ctx["moods"]. |
| 10 | Candados §6: lock literal, `main` intacta, tests verdes | OK | El LLM solo copia palabras, que se validan literales. Rama f3-lab-identidad. 264 verdes. |
| 11 | Candado: sin --gfx, byte-idéntico | NO VERIFICABLE | Todo cuelga de gfx_rules.intensity_director en el perfil misterio, con default False. Pero plan_peak ahora fija `plan["pico"]` aunque no haya bloque, también sin intensidad. Es un cambio de plan, no de píxeles. Falta un diff de segmentos para confirmarlo. |
| 12 | "3–5 cargas" | PARCIAL | Se impone el máximo 5 (`cargas[:MAX_CARGAS]`). MIN_CARGAS=3 está definido pero no se hace cumplir; con 1 carga válida se acepta. La corrida real dio 5 en los 7 caps. |

Fuera de alcance: ninguno entre los staged (todo es F4b §1 más sus documentos). diag_234_cap4.py figura como " M" sin stagear, no está en el diff cached, y no lo toqué.

Riesgos que el contrato no cubre:
- record_proposals reescribe misterio.json con inserción de texto durante el render. Una corrida concurrente, o una palabra mal categorizada que llegue a 2 videos, contamina el perfil en silencio.
- En la corrida real, 5 de 7 caps tienen el pico en la última frase (el LLM sube la intensidad hacia el cierre). Con el empate por peso 3 y la tolerancia de agua, el pico puede repetirse siempre al final.
- Hay 14 palabras nuevas de Orleans que no están persistidas en lexico_propuestas.json. Si el segundo video llega antes de generar ese archivo, el conteo de 2 videos arranca de cero.
```

**Respuesta de CC:**
- `lexico_propuestas.json` generado con las 14 palabras de Orleans y commiteado (punto 6 y riesgo 3).
- Mínimo de 3 cargas: se aceptan menos si solo esas son literales (descartar las válidas sería peor); queda anotado (E12).
- `pico` sin bloque: solo existe con `--gfx` (la capa gfx); sin `--gfx` la capa no corre. El md5 sin `--gfx` se re-mide en §5.
- Pico al final del cap: es lo que el LLM marca como más intenso (cierre de suspenso). Se deja así y se mira en el render de §5 (E13).

---

## §2 Fragmento literal más impactante

**Qué hay:** `script_engine/gfx_fragments.py` (token `fragment_director`). Para cada recorte y dato del cap se arman las opciones literales; la 1 es la de hoy. Flash elige números en una sola llamada por cap y el fragmento elegido pone el ícono de su categoría. Decisiones E14–E18.

**Orleans, antes → ahora** (prueba sobre los planes del render F4; `fragmentos_orleans.json`):

| cap | bloque | antes (F4) | ahora (F4b) | ícono |
|---|---|---|---|---|
| ch01 | recorte | El agua dentro de algunos edificios | **agua contaminada subió implacable** | biohazard |
| ch02 | recorte | El huracán Katrina tocó tierra | **Katrina desató su furia implacable** | — |
| ch02 | recorte | Los prisioneros quedaron atrapados durante días en celdas | (igual) | candado |
| ch03 | recorte | El agua dentro de algunos edificios | nivel del pecho | — |
| ch04 | recorte | El agua dentro de algunos edificios | nivel del pecho | — |
| ch06 | recorte | Los prisioneros quedaron atrapados durante días en celdas | **celdas inundadas con agua contaminada con aguas residuales** | candado |
| ch07 | recorte | Aproximadamente 6,500 personas | Prisión de Orleans | — |
| datos | 7 | Katrina, Prisión Parroquial de Orleans, 6,500 personas, Human Rights Watch, Templeman III, 500 prisioneros… | (iguales: con las reglas de E16 el LLM se quedó con el de hoy) | — |

- ch03/ch04 eligen «nivel del pecho»: en esos tramos la narración no dice nada más fuerte sobre ese fact. En el render real se re-arman los planes y el dedupe entre caps evita repetir titulares (acá ch06 repite el de ch02 porque la prueba lee los planes viejos).

**Veredicto revisor-handoff (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

Los tests que pediste dan 268 passed (los corrí yo). No corrí fase2b.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Fragmentos literales ≤ 8 palabras por cláusula, del fact y de la narración del tramo | OK, con matiz | script_engine/gfx_fragments.py `_clauses` y `fragments(max_words=8)`. Los datos topean en 5 palabras. En el recorte, la narración solo entra si comparte una palabra de contenido con el fact (E15, desviación declarada). |
| 2 | Lista numerada | OK | `build_prompt` genera "1. …"; el test lo verifica (test_module_gfx_fragments.py:49). |
| 3 | Flash elige un número y nada más | OK | SCHEMA `{id, n}` con `thinking_budget=0`. |
| 4 | Fuera de lista → el primero (el de hoy) | OK | `n` inválido pasa a 1, y la opción 1 es el texto de hoy. Hay test con n=999 (:53-55). Si Flash falla, quedan los textos de hoy (test :75). |
| 5 | Prompt con los 5 ejemplos | OK | Constante `EXAMPLES` (5 ítems) incluida en `build_prompt`. El test solo comprueba los 2 primeros en el prompt. |
| 6 | Categoría del fragmento → ícono | OK | `category_of` y `category_icon`, con ícono solo si `icon_svg` existe. El test da `calavera` para «agua putrefacta». En Orleans: ch01 biohazard, ch02 y ch06 candado. |
| 7 | Mood de la categoría acompaña | PARCIAL (declarado) | E18: el mood no se agrega aparte, solo el ícono. El sello rojo tampoco pasa por §2, porque es una sola palabra. El handoff pedía «sello»; es desviación documentada, no silenciosa. |
| 8 | Candado literal intacto | OK | gfx_layer.py: `lock()` se vuelve a pasar tras `choose_fragments`, y `literal_in` filtra antes. |
| 9 | Dedupe de titulares entre caps | OK, con matiz | `used_headlines_before` lee los gfx_plan_ch*.resolved.json de caps anteriores, con test. Solo aplica a recorte, no a datos. Si el titular "de hoy" también está repetido, no hay segundo filtro. |
| 10 | 1 llamada por cap | OK | Un solo `call` con todos los bloques, cacheado por prompt en gfx_fragments_{cap}.json. |
| 11 | Candados §6: sin `--gfx` no cambia nada | OK por lectura | El bloque está tras `gfx_rules.fragment_director` dentro de la capa gfx. Sin `--gfx` no corre; el md5 byte-idéntico no lo medí. |
| 12 | Entregables y documentación | OK | DECISIONES E14–E18, sección §2 en F4b_REPORT.md y fragmentos_orleans.json (UTF-8 válido, 120 líneas). |

Observaciones sobre la evidencia en Orleans:
- La tabla de F4b_REPORT.md (sección §2) muestra ch03 y ch04 con el mismo titular «nivel del pecho», y ch06 repite el de ch02. El reporte lo explica porque la prueba lee los planes viejos. Con esa prueba el dedupe no queda demostrado en datos reales; solo lo demuestra el test unitario.
- ch07 pasa de «Aproximadamente 6,500 personas» a «Prisión de Orleans». Es una elección discutible de Flash, no una falla de contrato.
- Los 7 datos reales quedaron iguales, así que esa rama casi no tiene evidencia real.

Fuera de alcance: ninguno en lo staged (9 archivos, todos de F4b §2 o su registro). diag_234_cap4.py figura modificado sin stage y no es nuestro. No lo toqué.

Riesgos que el contrato no cubre:
- El dedupe depende de que los resolved.json de caps previos existan en work_dir. Si se re-corre un solo cap o el orden cambia, el dedupe puede fallar sin aviso.
- La heurística de bordes por regex (`_VERB_EDGE`, `_KEEP_EDGE`) es frágil con palabras en español no previstas. Puede dejar fragmentos colgados o recortar sustantivos terminados en -an/-en.
- Gasto Gemini de §2 sin medir: el tope de $3 es para toda F4b y este reporte no lo contabiliza.
```

**Respuesta de CC:** el dedupe con datos reales se ve en el render de §5 (planes rehechos en orden). Gasto §2: 3 pasadas de prueba × 7 llamadas Flash sin thinking ≈ US$ 0.01; el total de F4b se mide con el cost_tracker en §5.

---

## §4 Íconos gratis automáticos

**Qué hay:**
- `script_engine/gfx_icons/fetch_game_icons.sh` baja game-icons.net (CC BY 3.0), 4.239 SVG, fuera de git.
- `script_engine/gfx_icons/auto_icons.py`:
  - índice inglés → español (`gfx_profiles/icons/icons_index.json`): 4.176 nombres, 3.729 con traducción, 17 llamadas Flash;
  - Flash elige entre los candidatos según la frase;
  - el SVG se restiliza al hueso del canal, con la tinta y el secado del set propio.
- Claves `gi:` en `icon_svg`. Token `auto_icons`.
- Prioridad: los 12 propios → game-icons → sin ícono.
- Crédito fijo en la descripción de m09: «Íconos: game-icons.net (CC BY 3.0) · Lucide (MIT)».

**Orleans:** cargas concretas de §1 = «agua» (propio: gota) · «penumbra» (ninguno) · «líquida» (ninguno). La tira `tira_iconos_auto_orleans.jpg` suma 22 sustantivos de la narración como demo del estilo: 12 con game-icons. Hay aciertos (prisioneros = preso tras barrotes, ojos, personas, ciudad, almas) y elecciones flojas («pecho» → baúl, «seis» → número 6, «justicia» → carta de tarot). Por eso en el pipeline solo entran palabras de carga marcadas concretas.

---

## §3 Zoom foto-primero

**Qué hay:** `script_engine/gfx_vision.py` (token `photo_first_zoom`), decisiones E19–E22 y E36–E37.
- Antes del director, visión mira cada foto: hasta 3 detalles con caja, confianza y tipo, en caché por hash de la imagen.
- El zoom sale de la foto, en este orden: pico → nombrado por la voz → «de editor» (rostro o manos, en la foto de la frase más intensa) → textura nombrada.
- Cada zoom se confirma recortando la caja.
- Las fotos con rostro o manos quedan de riesgo alto y el acercar apunta al detalle.

**Orleans:** detalles en 96 de 97 escenas (1 falló el JSON de visión y quedó anotada). Rostro o manos en 32 escenas. Zoom por cap (`zooms_orleans.jpg`):

| cap | zoom | cómo | antes (F4) |
|---|---|---|---|
| ch01 | rostro del hombre | de editor | sin zoom |
| ch02 | dedos mojados | de editor | caja «ahogaba» (nivel de agua en el pico) |
| ch03 | ojos asustados | de editor | caja sin detalle nombrado |
| ch04 | lágrima | nombrado («ojos») | «piel» |
| ch05 | rostro del niño | nombrado («ojos») | «cuerpos» (pico) |
| ch06 | cicatriz | de editor | (zoom con caja) |
| ch07 | rostro del hombre | de editor | sin zoom |

Ningún zoom a textura (agua, aceite): las dos texturas nombradas que aparecieron («ojo del huracán», «agua estancada») quedaron detrás de un detalle humano. La primera regla de «nombrado» daba «insecto en agua»; después de E36–E37 los 7 recortes muestran el detalle real.

**Veredicto revisor-handoff §3 + §4 + código de la marca (íntegro):**

```
VEREDICTO: CUMPLE CON OBSERVACIONES

Los 282 tests pasan (los que pediste, los corrí yo). No corrí fase2b.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | §3 prioridad rostro/manos > persona > objeto > texto > textura | OK | `script_engine/gfx_vision.py` PRIORITY; `validate` ordena por prioridad y confianza; test `test_validacion_y_prioridad` |
| 2 | §3 textura solo si se nombra literal y la foto no tiene humano | OK | `pick_zoom`: la textura se salta si hay humano en la foto y va última en `order`; test `test_nombrado_gana_y_textura_nunca_con_humano`. Orleans: ningún zoom a textura (F4b_REPORT §3) |
| 3 | §3 1 zoom por cap | OK | `pick_zoom` devuelve uno solo. `gfx_layer.py` pone `evidence_zoom=None` antes de decidir y desactiva el zoom fuera del pico con `off_peak_zoom=not details`. La tabla de Orleans tiene 7 zooms, uno por cap |
| 4 | §3 zoom de editor con conf ≥ 0.8 en la frase más intensa | OK | `EDITOR_CONF=0.8`; se ordena por `scene_intensity`; test `test_zoom_de_editor_en_la_foto_mas_intensa_y_lejos_del_pico` |
| 5 | §3 rostro/manos → riesgo alto y el acercar apunta al box | PARCIAL | `gfx_layer.py:~495` fija `risk:"rostro"` (no `deform_risk=high` literal) con `origin` en el centro de la caja; `gfx_project.py` usa ese origen como `transformOrigin`. Solo se aplica con `is_flux and not s.safe`. En caps Veo/híbridos no se marca riesgo, y una escena que ya tenía `safe` no se toca |
| 6 | §3 zoom_judge viejo como respaldo | OK | Si visión falla (`details` vacío), no se descarta nada y corre el camino de F4 (`apply_zoom_vision` en `_box`, `plan_peak` con zoom fuera del pico) |
| 7 | §3 evidencia Orleans (caché de visión, zooms, tira) | OK | `lab/hyperframes/f4b/vision_orleans.json` cubre ch01–ch07; `zooms_orleans.jpg` de 57 KB; tabla en el reporte. No abrí las imágenes |
| 8 | §4 game-icons fuera de git, con script de descarga | OK | `.gitignore` línea 63; `git check-ignore` confirma la ruta; `script_engine/gfx_icons/fetch_game_icons.sh`. La ruta es `script_engine/gfx_runtime/icons/`, no `gfx_runtime/icons/` como decía el handoff (decisión E23) |
| 9 | §4 índice | OK | `gfx_profiles/icons/icons_index.json` (26k líneas, versionado). La validación a mano de 50 entradas está en E34 |
| 10 | §4 restilizado al look del canal | PARCIAL | `game_icon_svg` en `auto_icons.py`: fondo quitado, relleno hueso `#e8e0cc` y filtro de tinta de `scoped_svg`. Sin rojo semántico (E24). No es el mismo pipeline que Lucide, y el handoff no pedía rojo si no hay detalle |
| 11 | §4 prioridad propios > game-icons, y solo cargas concretas | OK | `gfx_layer.py` solo busca ícono si `not e.get("icon")` y la palabra es `concreta`. El paso a Lucide casi no existe porque solo hay 12 SVG en el repo (E25, admitido) |
| 12 | §4 crédito en la descripción (m09) | OK | `script_engine/m09_packaging.py` `ICON_CREDIT` y `with_icon_credit`, llamado desde `_normalize_metadata`. El texto coincide con el handoff |
| 13 | §4 tira de Orleans | OK | `tira_iconos_auto_orleans.jpg` (189 KB) más `iconos_auto_orleans.json` |
| 14 | §0.3 la marca sale solo del perfil; finanzas sin marca | OK | `gfx_bug.config()` lee `ACTIVE_PROFILE["channel_bug"]` y exige `enabled` y `svg`. Ni `misterio.json` ni `finanzas.json` tienen la clave, así que queda apagada |
| 15 | §0.3 implementación (esquina, opacidad, fades, cierre) | NO VERIFICABLE | `test_module_gfx_bug.py` pasa, pero no hay render con la marca encendida. Falta correr un cap con `channel_bug.enabled` |
| 16 | §6 candados (literal, `main` intacta, sin `--gfx` byte-idéntico) | PARCIAL | `choose_icons` y `pick_zoom` eligen entre opciones, nunca escriben. No hay prueba de que sin `--gfx` el segmento sea byte-idéntico: el cambio en `stitch` solo actúa con `bug`, pero nadie lo comparó |

Fuera de alcance: ninguno. `diag_234_cap4.py` figura como modificado sin stagear (` M`), así que no está en el diff staged. Los archivos staged son los esperados de §0.3, §3 y §4 más sus pruebas y reportes. No toqué `main`.

Riesgos que el contrato no cubre:
- El crédito de game-icons y Lucide se agrega a la descripción de todos los canales, incluido finanzas, aunque ahí no se usen esos íconos.
- El cierre de video agrega 3,5 s al último cap con la pausa de F3, pero solo se activa con la marca encendida y no está probado en un render real. Hay que verificarlo cuando Omar elija candidato.
- Si falla la visión en una escena, esa escena queda sin detalles y la falla queda cacheada (el JSON de Orleans tiene una escena así). El respaldo con zoom_judge solo funciona si falla el cap entero, no escena por escena.
```

**Respuesta de CC:**
- Respaldo por escena: una escena con visión fallida no entra en `details`, así que para esa escena el pico usa el camino viejo (caché de caja + zoom_judge en `_box`). Lo que no hace es el zoom «de editor» en esa escena.
- Crédito en todos los canales: se deja (atribución de más no viola la licencia; de menos sí).
- Byte-idéntico sin `--gfx`: se mide en §5 (md5 de ch02 `--only-cap`).
- La marca encendida y el cierre se prueban en §5 si Omar eligió candidata; si no, quedan apagados (no se elige por él).
