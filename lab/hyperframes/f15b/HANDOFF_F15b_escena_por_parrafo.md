# HANDOFF F15b — v5.1: la escena merece un párrafo · re-correr Ycuá y Orleans

Analista · 2026-10-23 · Para CC. Base: `0055e14` (rama `f11-guion-v4`; seguí en la misma). Solo ficha → escaleta → guion. Sin producción.

## 0. Por qué (leído del disco y del diff de F15)
- El código de F15 está bien: el sistema v5 entra literal (verificado byte a byte contra el .md), el incidente del preámbulo se arregló y se re-corrió.
- La voz llegó: 0 preguntas, 0 frases de analista, 0 tráiler en los dos temas. Orleans 8.5.
- Lo que falló es de prompt: Sol tomó «ni relleno» al pie de la letra y escribe párrafos de una frase. Ycuá quedó telegráfico (755 palabras, 6 min; «Víctor busca la puerta de blíndex.» como párrafo) y perdió el gancho de las cenizas. Nota 7.
- La escaleta de Ycuá no usó ninguna de las 9 escenas de la ficha (`escena_idx` vacío en los 13 beats).
- El chequeo de la ficha sacó 12 cifras respaldadas (el pool las escribe «G. 4.500 millones») y es más estricto con los sentidos de lo que pedía el handoff.

## 1. Cambios
**1.1 Prompt v5.1** — `lab/hyperframes/f15/PROMPT_GUIONISTA_v5_1.md` (reemplaza al v5; md5 en el reporte). Tres cambios, todos en el bloque SISTEMA, **literales**:
- en `<voz>`: una línea nueva, «Una escena merece un párrafo entero…» (cinco a ocho frases; el párrafo de una frase es un golpe, una o dos veces por cap);
- en `<estructura>` 7: «…bien contado significa con su escena: no es más corto el que dice menos, sino el que no repite.»;
- en `<errores>`: dos errores nuevos con su corrección: «Telegrama» y «Gancho abstracto», tomados de Ycuá F15.
`PROMPT_VERSION = "f15b-1"`. El test byte-idéntico pasa a comparar contra el archivo v5_1 (y el v5 queda reproducible con `version="f15-1"`).

**1.2 Escaleta usa las escenas** (`m01a_escaleta`, prompt con ficha): el texto de la sección ESCENAS pasa a decir: «El beat 1 (gancho) y el beat del pico toman su `imagen_sensorial` de una escena de la ficha cuando hay una para ese momento; los demás beats, cuando sirva.» No rechaza nada: si no cita escena, va a `_avisos` «gancho sin escena de la ficha». Sin ficha, byte-idéntico (test).

**1.3 Chequeo de la ficha, dos aflojes** (`ficha_caso.problems`):
- cifras: antes de comparar, normalizar los dos lados quitando separadores de miles, «G.», «$», «US$», «°» y espacios (4.500 = 4500 = 4,500);
- sentidos de una escena: basta **una** palabra de contenido del campo `sentidos` presente en el texto de sus ids (no una por tramo). Lo que siga sin respaldo, a descartados como hoy.
Tests para los dos casos (las 12 cifras de Ycuá y una escena con un solo sentido respaldado).

## 2. Corridas
- **Fichas: no se rehacen.** Se usan las v2 de F15 que están en `_steps` (re-chequeadas con el afloje de 1.3, sin llamada: `--rechequear`). Si el re-chequeo devuelve ítems a la ficha, se dice en el reporte.
- **Escaleta nueva** para Ycuá y Orleans (1.2). Las de F15 quedan como `_f15`.
- **Guion v5.1** con Sol high, los dos temas.
- Salidas en `lab/hyperframes/f15b/`: escaletas, `NARRACION_<tema>_f15b.md`, `guion_<tema>_f15b.json`, prompts con md5.
- **`compara_f15b.html`**: F15 | F15b por cap, con palabras, minutos, párrafos por cap y frases por párrafo (promedio), bloqueantes, escenas usadas por la escaleta, frases marcadas.
- **Tope: US$ 1.50.**

## 3. Frenos
- Cero reglas nuevas para el guion. Los tres cambios del prompt son texto al modelo, no validadores.
- No tocar el pool, `research_v3`, `m05`, `evidence.py`, `guion_v3_reglas.py`, `config.py`, `topics_db`.
- Sin merge; no commitear `.env` ni `lab/_gpt_probe_analista/`.
- Tests: v5.1 byte-idéntico; escaleta sin ficha intacta; los dos aflojes. Suites verdes + las 5 previas; dorado de v3 verde.
- Actualizar `lab/ESTADO_SESION.md`.

## 4. Reporte `lab/hyperframes/f15b/F15b_REPORT.md`
1. md5 del prompt v5.1 contra el archivo.
2. Tabla F15 | F15b por tema: palabras, minutos, párrafos, frases por párrafo, escenas usadas, bloqueantes.
3. Qué devolvió el re-chequeo de las fichas.
4. Costo y tokens.
5. Veredicto íntegro del revisor-handoff.

## 5. PARADA
Commit + reporte → **PARADA**. El analista revisa el diff (prompt literal, escaleta, aflojes) y lee los dos guiones.
