# VALIDACIÓN F5 — Guion v2 de Orleans y su efecto en pantalla

**Fecha:** 2026-10-21 00:05 · **Analista:** chat proyecto · **Fuentes leídas del disco:** `lab/guion/compara_orleans.html`, `lab/hyperframes/f5/cues/gfx_cues_v1_ch01–07.md` y `gfx_cues_v2_ch01–07.md`, `DECISIONES_F5.md`, commits `66ee44b…e7b661c`.
**Pregunta de Omar:** ¿al mejorar el guion mejora todo lo demás?

## Veredicto en una línea
**La arquitectura funciona y el guion mejora de verdad; la ejecución no es publicable todavía.** Una contaminación grave en el cap 7, una métrica inflada, y en pantalla la tubería lleva el pool pero las reglas de calidad encima no están. Una pasada más (F5b) y se vuelve a medir.

## 1. ¿v2 usa ≥ 3 datos nuevos por cap y nombra a Gusman? — SÍ
41 datos distintos del pool contra 12 en v1. Gusman y su adjunto desde el cap 1, con la cita "donde pertenecen"; en el cap 5 la cita completa "Están en la cárcel, hombre. Mienten…". Entran Strock, Morgan, Hubert, Waganfeald, Kunkel. Pero **Raphael Schwarz** entra solo para cumplir cuota ("Casos como el de Raphael Schwarz, Arrestado por intoxicación pública" — mayúscula pegada del pool, sin acción en la historia).

## 2. ¿Bajó la repetición entre caps? — SÍ entre caps, NO dentro del cap
Ningún dato en más de 2 caps ("6,500" pasó de 4 caps a 2; "500" de 3 a 1). Pero dentro del cap el narrador pega el dato textual dos y tres veces: cap 3 "29 de agosto de 2005" ×3; cap 4 "nivel del pecho" ×3 y "2 de septiembre de 2005" ×2 en frases seguidas; cap 5 "517" ×2. Por eso los 3-gramas repetidos subieron (3.4 % → 4.1 %).

## 3. ¿La prosa cambió de adjetivos a hechos? — SÍ, con sobrecorrección
Adjetivos/100: 6.2 → 2.9. Tres pares:
- v1 "un coloso de hormigón y hierro" → v2 "la House of Detention (HOD) de la prisión fue reabierta el 17 de octubre de 2005".
- v1 "Imaginen el terror" → v2 "A la medianoche del 29 de agosto, el sheriff Gusman solicitó ayuda para la evacuación".
- v1 "¿Cuánto tiempo podrían resistir?" → v2 "Pero, ¿estaban todos los prisioneros fuera?" (y el cap 5 abre con los 517).
Sobrecorrección: cap 4 bajó a 0.66 adjetivos/100 y se lee como acta ("Los reclusos fueron sacados en botes. Se les llevó al paso elevado…"). Hace falta piso, no solo techo.

## 4. ¿Los cierres anticipan algo concreto? — SÍ (6 de 6 con dato; 5 cumplidos)
cap1→"no planeaba evacuarlos" · cap2→"los generadores perecerían" · cap3→"agua al nivel del pecho" (el juez marca ✘: lo anticipa pero sin la frase exacta; es un falso negativo del chequeo) · cap4→"¿estaban todos fuera?" · cap5→"donde un jurado federal…" · cap6→"la ausencia completa de documentación".

## 5. ¿Mejora todo lo demás (pantalla)? — A MEDIAS
**Lo que ya funciona (la tubería):**
- **Reloj** sale de la cronología: "28 AGO" (ch02), "29 AGO" (ch03), "30 AGO" (ch04). Antes no existía.
- **Recortes del pool con fecha:** "prisioneros no serán evacuados de la Prisión de Orleans Parish" (ch02), "…hasta el viernes 2 de septiembre" (ch04). Antes el recorte repetía la voz.
- **Pregunta del cliffhanger:** "¿Quién cortó la energía?", "¿Quiénes quedaron en las celdas?". Concretas.

**Lo que está mal (las reglas encima):**
| # | Problema | Evidencia |
|---|---|---|
| P1 | Recortes cortados a media cláusula | "piso comienzan a inundarse y las aguas residuales refluyen" (ch03), "federal otorga más de $650,000 a dos turistas de Ohio" (ch05), "la prisión no finalizó hasta el viernes 2 de septiembre" (ch04). La regla de cláusula completa falla con los textos largos del pool. |
| P2 | Recorte fuera de la cronología | ch02 a 0:07 "Gusman solicita ayuda para la evacuación" (evento del 29 a medianoche) mientras la voz cuenta el 28 de agosto "no serán evacuados"; 7 s después sale el recorte del 28. Contradicción en pantalla. |
| P3 | Mismo hecho, dos ids, dos recortes | ch05 1:22 "650,000 dólares a Waganfeald y Kunkel" y 1:42 "federal otorga más de $650,000 a dos turistas de Ohio" (D50 y D72). Además es el tema del cap 6: la regla ±1 cap **destripa el cliffhanger**. |
| P4 | Íconos por categoría a adjetivos | penumbra, sofocante, escalofriante, inquietante, horrores → candado; marea, inundación → gota. Es el problema de F4b otra vez: el mapa palabra→ícono literal no está implementado; sigue categoría + peso ≥ 2. |
| P5 | Caps 6 y 7 sin recorte | El pool tiene HOD reabierta, carta del DOJ, 6,375 vs 8,000, 14 órdenes; ninguno salió. Dedupe/ubicación los descartó. |
| P6 | Nivel de agua en "15 pies" | La voz v2 dice "15 pies" y el bloque lo copia; para audiencia en español debe ser "4.6 m" (el pool tiene ambos). |
| P7 | Crítico visual sin fotos reales | La simulación usó las fotos de v1 con anclas de v2: el crítico no pudo juzgar "repite". Q5 solo se cierra con imágenes de v2. |

## 6. Riesgos nuevos
- **Contaminación del pool (GRAVE):** cap 7 cierra con "la antigua cárcel de Nueva Orleans, construida en 1902… un médium psíquico ha detectado la energía". Es la posada embrujada del bloque misterio, otro edificio; el research lo marcaba como "no directamente relacionado". El pool lo tomó como dato y el narrador lo usó. Hace falta filtro de relevancia.
- **Métrica inflada por choque de cifras:** "Interestatal **10**" se cuenta como el dato de los niños de **10** años; "**14** de octubre" como las **14** órdenes. El conteo debe ir por id declarado por el narrador, no por regex. La densidad real de v2 es menor que 3.29 (igual > v1).
- **Nombres por cuota** (Schwarz). Un nombre solo entra si hace algo.
- TTS: "98.7 %", "OPP", "HOD" dependen del normalizer nuevo; sin verificar en audio.
- Datos contradictorios del pool (6,375 / 6,500 / 8,000) usados sin regla de cuál es "el oficial" y cuál "la estimación"; en el cap 7 se usan bien, pero no por regla.

## 7. Decisión recomendada
No rehacer el video de Orleans todavía. **F5b** (≈ 4 h de CC): cinco arreglos de narración + cinco de pantalla (abajo), regenerar v2, re-simular, y el analista vuelve a validar. Si pasa: imágenes de v2 para Orleans (costo de un video) o aplicar directo al siguiente video; eso lo decide Omar con la comparación nueva en mano.

### F5b — Narración
N1 Filtro de relevancia en el pool: fuera lo que el bloque marque como no relacionado (1902 / médium). N2 Métricas por id declarado. N3 Cada dato una vez por cap (paráfrasis permitida sin cifra). N4 Piso de adjetivos 2/100, techo 4. N5 Nombres solo con acción; corregir mayúsculas pegadas del pool.

### F5b — Pantalla
S1 Recorte = cláusula completa también para textos del pool (si no hay cláusula ≤ 10 palabras que empiece en sujeto, Flash reescribe **solo eligiendo** entre fragmentos; nunca cortar). S2 Un recorte no puede mostrar un evento posterior a la fecha que narra la voz en ese tramo (cronología del pool). S3 Dedupe por **hecho**, no por id: dos ids con la misma cifra+entidad son uno; y sin recortes de caps siguientes (±1 solo hacia atrás) para no destripar el cliffhanger. S4 Ícono solo por mapa literal palabra→ícono del perfil (cadáveres→calavera, residuales/contaminada→biohazard, celda/encierro→candado, inundación→gota); adjetivos nunca; categoría solo para el mood. S5 Unidades: en pantalla siempre metros/km/°C; el pool guarda ambas.
