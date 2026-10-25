# HANDOFF F24 — Fuentes que se acumulan, beats repartidos, y la prueba de la fase 1 con dos temas nuevos

Analista · 2026-10-24 · Para CC (misma sesión). Base: `03370af` (rama `f11-guion-v4`). Tres partes; **tope total US$ 14.00**. **PARADA al final de la parte C** (y PARADA corta al final de la B, ver §B.4).

## 0. Por qué
- **Fuentes.** Kyshtym en F23 rehízo el research y el buscador trajo otras diez fuentes: se perdió el artículo ruso con Osetrov/Komarov/Serov y a Kutepova. Mismo código, otro material, otra historia (8.5 → 7.5). Lo que ya se encontró una vez no puede volver a perderse.
- **Beats.** La escaleta de F23 puso 6 de 14 beats en el cap 6 (601 palabras) y uno en cada uno de los caps 2–4 (76–134). El prompt lo empuja («un cap puede tener dos beats densos y otro uno solo») y el chequeo solo exige ≥ 1 por cap.
- **La prueba.** Todo lo de F21–F23 se validó con Kyshtym (y Ycuá/Orleans de referencia). La fase 1 está verde solo si dos temas que nunca vimos llegan al guion sin tocar código.

## A. Fuentes que se acumulan (research)
1. **Registro de fuentes por tema**: `data/scripts/_steps/<topic>/fuentes.json` = unión de todas las fuentes descubiertas (R1) y bajadas (R2) en todas las corridas del tema: `{url, titulo, tipo, idioma, anio, primera_vez, veces_vista, bajada_ok, chars, aporte: {datos, citas, personajes}}` (`aporte` = cuántos ítems del pool salieron de ese documento la última vez que se extrajo).
2. **R1 une, no reemplaza**: la lista de candidatos de una corrida = lo nuevo que trae el buscador **+** todo lo que ya estaba en `fuentes.json`. El cupo de descargas por idioma (`MAX_DESCARGAS_OK`) se reparte dando **prioridad a las fuentes con `aporte` alto** de corridas anteriores, después `_doc_rank` como hoy.
3. **R2 no vuelve a bajar** lo que ya está en `_docs/` con el mismo URL (ya existe el txt): lo reutiliza. R3 no vuelve a extraer un documento cuyo txt no cambió: reutiliza sus ítems del pool anterior (misma `doc_id`), re-numerando ids si hace falta. Esto baja el costo de un research repetido a casi cero.
4. Kyshtym: construir `fuentes.json` a partir de los pools de F20/F22/F23 que están en disco (`00_pool_v3_f*.json` + `_docs/`), sin llamar a nada. Test: el artículo ruso de Osetrov figura con su aporte.
5. **No se agrega ningún chequeo**; es memoria entre corridas.

## B. Beats repartidos (escaleta)
1. **Chequeo de estructura** (`validate`/`bloqueantes` v2): cada cap entre **1 y 3 beats**; sigue valiendo 7–14 en total. Es estructura, como «≥ 1 por cap»; entra en los bloqueantes (14 en vez de 13). Una regeneración, como siempre.
2. **Prompt v2.1 → f24-1** (`PROMPT_ESCALETA_v2_1.md`): en `<errores>`, la línea «Repartir el material parejo para llenar siete caps. Un cap puede tener dos beats densos y otro uno solo.» pasa a: «Meter seis beats en un cap y uno en los demás. Cada cap lleva entre uno y tres beats; el material que no cabe se deja afuera, no se apila.» Nada más cambia; md5 en el reporte.
3. **Prueba de modelo en la escaleta** (US$ ≤ 2.00): ficha de Kyshtym de F23, escaleta **Sol ×2** y **Fable ×2** (mismo prompt f24-1), guion con Fable de las cuatro. Tabla: beats por cap, ids, apoyos por beat, promesa textual, palabras por cap del guion, bloqueantes. Si Fable reparte y promete mejor, pasa a ser el modelo de la escaleta **para la parte C**; si no, queda Sol. Lo decide CC con la tabla y lo dice en el reporte (criterio: menos caps fuera de 1–3 beats en la primera pasada, y promesa sin resumen).
4. **PARADA corta**: antes de la parte C, commit de A+B y aviso al analista con la tabla de B.3. Si no hay respuesta en 20 minutos, seguir con el modelo que CC decidió.

## C. La prueba: dos temas nuevos, de la semilla al guion, sin tocar código
Temas (del inbox de Omar, `data/selected_seeds.json`):
- **`4ac37187` — Horrores del Asilo Pennhurst** (Pennsylvania, 1908–1987; prolongado, inglés, antagonista institución).
- **`f8s3-vaj` — La represa de Vajont** (Italia, 9 de octubre de 1963; puntual, italiano, ingenieros con nombre).

Para cada uno, por el camino normal (`run_seed` → perfil → research v3 → compuerta → ficha v2.2 → escaleta f24-1 → guion v5.3 con Fable), con los topes: research 3.50 · ficha 0.60 · escaleta 0.40 · guion 1.20 = **US$ 5.70 por tema**.

**Regla de oro: no se toca código durante la parte C.** Si algo se rompe, PARADA de ese tema con el crudo guardado y el error en el reporte; el otro tema sigue. Lo único permitido: reintentar **una** vez un paso que falló por red/timeout.

Salidas por tema en `lab/hyperframes/f24/<tema>/`: `PERFIL.md`, `POOL_GATE.md`, `FICHA.md`, `ESCALETA.md`, `NARRACION_<tema>_f24.md`, prompts con md5, `costos.json`, `compara_f24.html` (los dos temas, cap por cap).

## D. Reporte `lab/hyperframes/f24/F24_REPORT.md`
1. Parte A: fuentes.json de Kyshtym (cuántas, cuántas con aporte), y una corrida en seco de R1 unido (sin API) que muestre que el artículo ruso quedaría en el cupo.
2. Parte B: la tabla de B.3 y la decisión de modelo.
3. Parte C, por tema: perfil (rango, tipo, idiomas), compuerta con las cuatro medidas, personas con nombre y elegibles, humano y antagonista elegidos, beats por cap, guion (palabras, bloqueantes, citas, personas por cap, fechas literales por cap), **qué se rompió y dónde**, costo por paso.
4. **La tabla de la fase 1**: para cada paso (perfil, R1, R2, R3, R4, R5, compuerta, ficha, escaleta, guion, partición) × tema: corrió solo / necesitó reintento / paró, y por qué.
5. Veredicto íntegro del revisor-handoff. Costo total.

## E. Frenos
- Cero reglas de estilo. El único chequeo nuevo es B.1 (estructura).
- Prompts: solo la línea de B.2.
- Sin merge; no commitear `.env`, `config.py`, `lab/_gpt_probe_analista/`.
- Tope total US$ 14.00; pasado, PARADA donde esté.
- Actualizar `lab/ESTADO_SESION.md`.

## F. PARADA
Commit + reporte → PARADA. El analista lee los dos guiones y la tabla de la fase 1 y le da a Omar **la nota de 1 a 10 de la fase 1**, con la lista de lo que falla etiquetada (se queda / a mano / se arregla / frena). Con eso Omar decide si se pasa a imágenes y voz.
