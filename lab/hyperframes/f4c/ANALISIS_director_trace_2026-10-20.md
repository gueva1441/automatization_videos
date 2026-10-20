# ANÁLISIS — Cómo está pensando el director (traza ch02 y ch05, F4b)

**Fecha:** 2026-10-20 · **Fuente:** `_fase2b_work` de Orleans (`gfx_intensity`, `gfx_fragments`, `gfx_plan.resolved`, `gfx_cues`, `gfx_chNN.log`) · **Analista:** chat proyecto
**Pregunta de Omar:** ¿por qué pone una gota cuando lo fuerte es "putrefacta", y por qué los recortes repiten lo que ya dice la voz?

---

## 1. Lo que la traza muestra (hechos, no opiniones)

### 1.1 Director de intensidad (Flash)
| Hallazgo | Evidencia | Efecto |
|---|---|---|
| **Las cargas se truncan a las 5 primeras por orden de aparición, no por peso.** | ch02: Flash devolvió 11 cargas; el log usa `[catástrofe, furia, agua, agua, caos]`. Se perdieron `encierro`, `oscuridad`, `silencio` (las tres de **peso 3**). | El cap trabaja con las palabras más flojas del LLM. |
| **Flash prefiere sustantivos abstractos.** | ch02: catástrofe, furia, caos, tragedia, desastre (todos `caos_gritos`, peso 2). **No listó "putrefacta" ni "sumergidos"**, que están en la frase pico. | Lo sensorial (lo que Omar quiere) no llega ni a candidato. |
| **Flash infla palabras comunes.** | "agua" → peso 2 (léxico dice 1; frecuencia 14 en el cap). | "agua" compite con palabras raras y gana por mapa de ícono. |
| **Más de la mitad de las cargas buenas caen en categorías apagadas.** | ch05: borradas/desvanecidas/borrados → `silencio`; infierno → `fuego`; abandonados → `frio_abandono`. Todas en reserva (inactivas). | 7 de 17 cargas de ch05 no producen nada. |
| **Cargas ≠ frase pico.** | ch05 pico = frase 10 ("Cuerpos sin vida… agua pútrida"); `pútrida` (peso 3, veneno) sí está en cargas pero **no se usa** (ver 1.2). | El pico se detecta bien y después se vacía. |

### 1.2 Selección de énfasis (sello / mood / ícono)
| Hallazgo | Evidencia | Efecto |
|---|---|---|
| **El ícono lo decide el mapa literal, no el peso.** | ch02: `agua` (peso 2, frecuencia 14) → `icon_callout: gota`. `encierro` → candado. "putrefacta" ni aparece. | Es exactamente lo que Omar vio: gota en vez de putrefacción. |
| **La regla "nada a ±5 s del pico" borra la palabra más fuerte del cap.** | ch05: `pútrida` (peso 3) está en la frase pico → excluida. Quedan `líquida` (peso 2) y `flotando` (ni siquiera estaba en cargas; vino del léxico). ch02: `sumergidos` excluido, queda `oscuro` (peso 1). | El pico tiene bloque grande pero **sin la palabra**; el resto del cap se llena con palabras débiles. |
| **Peso 1 dispara sello.** | ch02: `oscuro` peso 1 → sello + mood. | Ruido. |
| **"Rareza" se calcula dentro del cap, no del video.** | `agua` rarity 14 pasó porque había pocos candidatos. | Sin mínimo de peso, cualquier cosa entra. |

### 1.3 Fragmentos (recorte / dato)
| Hallazgo | Evidencia | Efecto |
|---|---|---|
| **El recorte termina siendo una frase de la narración, no un documento.** | ch02 recorte0: antes "El huracán Katrina tocó tierra" (fact con fecha) → ahora **"Katrina desató su furia implacable"** (narración, sin fecha, kicker "2005"). | Repite lo que dice la voz y el subtítulo. Perdió el dato (29 de agosto). |
| **Cuando el fragmento viene del fact, sí aporta.** | ch02 recorte1: "celdas inundadas con agua contaminada con **aguas residuales**" (fact 5; la voz no dice "aguas residuales"). ch05: "cadáveres flotando en las aguas de la inundación" (fact 8, testimonio HRW). | Eso es lo que debe pasar siempre. |
| **El kicker (fuente) casi nunca sale.** | ch02 recorte1 kicker `""`; ch05 recorte kicker `""` aunque el fact 8 es un informe de Human Rights Watch. | El recorte parece pie de foto, no prueba. |
| **Los candidatos se cortan mal.** | ch02 dato0: "15 pies 4.6" (cruzó paréntesis) → rechazado por el candado → el cap perdió el dato de 4.6 m (lo salvó el nivel de agua). | Ya arreglado (E42), pero muestra que las listas de candidatos están sucias. |
| **Los datos repiten la voz.** | ch05: "Templeman III", "1 de septiembre": la narración los dice en ese mismo tramo. | Tercer texto igual en pantalla (voz + sub + dato). |

### 1.4 Pregunta de cierre
| Hallazgo | Evidencia |
|---|---|
| Automática ch02: "¿Cómo sucumbieron los generadores de respaldo?" (descartada; quedó la manual de Omar). ch05: "¿Cómo obtuvieron Waganfeald y Kunkel su indemnización?" | El contrato "comparte sustantivo con el cap siguiente" empuja a **trivia procesal** con nombres que el espectador no conoce. No es gancho. |

### 1.5 Lo que sí funciona
Zoom foto-primero (rostro del niño en ch05, "nombrado" por "ojos"), pico detectado en frase correcta, transiciones con alternancia, dedupe de cifras, candado literal (rechazó el fragmento roto), movimientos por identidad.

---

## 2. Diagnóstico en una frase
**El director busca "qué se puede poner" (palabra con ícono, fragmento más dramático, sustantivo compartido) en vez de "qué suma".** Las reglas que escribimos para evitar errores (mapa literal, ±5 s, fuera-de-lista) terminaron eligiendo lo mediocre. Y la truncación a 5 por orden es un bug liso.

## 3. Doctrina del director (nueva, va al perfil como texto y al validador como reglas)

**Principio 0 — El subtítulo ya muestra la narración. Todo lo que se agrega en pantalla SUMA o INTENSIFICA; nunca repite.**
- *Suma* = algo que la voz no dice: fuente, fecha, cifra exacta, nombre del informe, frase textual de un testigo.
- *Intensifica* = **una** palabra de la voz, sellada, con su mood e ícono de categoría.

**Regla 1 — Cargas por peso, no por orden.** Flash devuelve hasta 10 cargas; el validador se queda con las **5 de mayor peso** (empate: más rara en el video completo). Peso 1 nunca entra como carga.

**Regla 2 — Sensorial sobre abstracto.** En el prompt de intensidad: "preferí palabras que se puedan oler, tocar o ver (putrefacta, cadáveres, sumergidos, celdas) sobre palabras-resumen (catástrofe, tragedia, caos, desastre, horror); las palabras-resumen solo si no hay sensoriales en la frase". Few-shot con 5 pares.

**Regla 3 — El pico INCLUYE su palabra.** El bloque grande del pico lleva adentro la palabra de mayor peso de esa frase (sello + mood + ícono de categoría). La limpieza ±5 s aplica a **otros** bloques, no a la palabra del pico. ch02: nivel de agua + sello "PUTREFACTA" + mood veneno. ch05: recorte + sello "PÚTRIDA" + calavera.

**Regla 4 — Ícono por categoría y peso, nunca por "se puede dibujar".** Ícono solo si la palabra tiene **peso ≥ 2** y su categoría tiene ícono: veneno → calavera/biohazard, muerte → calavera/cruz, encierro → candado, agua → gota solo con peso ≥ 2 (nunca "agua" sola). El mapa literal queda como preferencia dentro de la categoría, no como condición.

**Regla 5 — Activar las categorías de reserva.** `silencio`, `fuego`, `frio_abandono`, `caos_gritos`, `radiacion_quimico` pasan a activas con capa mínima (viñeta + desaturación leve + SFX propio) hasta que el lab les dé forma. Una palabra de peso 3 en categoría sin capa ≥ sello solo. Nunca "nada".

**Regla 6 — El recorte es un documento.** Candidatos **solo del fact** (nunca de la narración). Debe contener al menos un elemento que la narración del tramo **no** dice (cifra, fecha, nombre, "informaron", "según"). **Kicker obligatorio** = fuente del fact o año; sin fuente ni año → sin recorte. Flash elige el más fuerte entre esos; si ninguno cumple → sin recorte.

**Regla 7 — El dato no repite.** `data_callout` solo con cifra/nombre que la narración del tramo no pronuncia, o lo pronuncia pero el fact trae precisión extra ("6,500" cuando la voz dice "seis mil quinientas"). Si repite exacto → sin dato (el contador queda para cifras duras, 1 vez por cifra).

**Regla 8 — La pregunta es un gancho, no trivia.** Flash genera 3; un segundo paso elige por rúbrica: (a) nombra algo que el espectador **ya conoce** (persona/grupo/lugar de este cap o anteriores), (b) implica consecuencia o culpa no resuelta, (c) ≤ 8 palabras, (d) sin nombres propios nuevos ni términos administrativos (indemnización, generadores, registros). Modelo: "¿Quién fue el culpable?", "¿Qué pasó con los 500 presos?", "¿Por qué nadie abrió las celdas?".

**Regla 9 — Traza siempre.** Cada cap deja `DIRECTOR_TRACE_chNN.md` (entradas, candidatos, elección, descartes) generado por el pipeline, para auditar sin pedirle nada al LLM.

## 4. Qué cambiaría en ch02 con la doctrina (simulado a mano)
| t | hoy | con doctrina |
|---|---|---|
| 0:09 recorte | "Katrina desató su furia implacable" (voz) | "Katrina tocó tierra el 29 de agosto" · kicker **2005 · NOAA/fuente del fact** |
| 0:20 | gota + sello AGUA (peso 2 inflado) | nada (agua = peso 1) |
| 0:26 | sello OSCURO (peso 1) | nada |
| 0:33 pico | nivel de agua solo | nivel de agua + sello **PUTREFACTA** + mood veneno + calavera |
| 1:00 recorte | "celdas inundadas… aguas residuales" kicker vacío | igual + kicker **Informe, 2005** + candado |
| 1:19 | candado ENCIERRO | igual (peso 3) + mood oscuridad |
| 1:21 | — | sello **SILENCIO** (peso 3, categoría activada) |
| cierre | "¿Quién fue el culpable?" (manual) | igual, ahora automática por rúbrica |

Menos bloques, más fuertes, ninguno repetido.

## 5. Para CC (F4c, ~5 h)
1. Bug: top-5 cargas por peso (Regla 1). Test.
2. Prompt de intensidad: sensorial > abstracto, 10 cargas, peso 1 excluido (Regla 2).
3. Pico incluye su palabra; limpieza ±5 s solo para otros bloques (Regla 3).
4. Ícono por categoría + peso ≥ 2 (Regla 4). Activar reservas con capa mínima (Regla 5).
5. Recorte = documento: candidatos solo del fact, elemento no narrado obligatorio, kicker obligatorio (Regla 6). Dato no repite (Regla 7).
6. Pregunta por rúbrica (Regla 8).
7. `DIRECTOR_TRACE_chNN.md` automático (Regla 9).
8. Re-correr ch02 y ch05 `--only-cap`, tabla antes/después por bloque, revisor, commit. Sin render completo.
