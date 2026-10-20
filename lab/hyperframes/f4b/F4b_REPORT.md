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
