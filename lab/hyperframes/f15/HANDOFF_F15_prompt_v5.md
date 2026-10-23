# HANDOFF F15 — Prompt del guionista v5 (escrito completo) + ficha con historia y escenas · Ycuá y Orleans

Analista · 2026-10-23 · Para CC. Base: `1920d40` (rama `f11-guion-v4`; seguí en la misma). **Solo ficha → escaleta → guion.** Sin imágenes, voz ni producción.

## 0. Por qué
- F14 probó que la ficha en vez del digest funciona: Orleans pasó de 6.3 a 11.8 min con los mismos datos, nota 8.
- Lo que falta está en los dos prompts, no en el código:
  - el del guionista tiene 8 líneas de oficio y 2 ejemplos; le faltan la voz, la estructura y los errores que se repiten en todas las corridas (voz de tráiler en el cap 1, explicar lo obvio, preguntas automáticas);
  - el de la ficha pide un archivo (hechos, cifras, citas) pero no una historia (humano con arco, giros, pico, escenas). Lo bueno de F14 (Pearl, la barra contra la pared) salió por suerte, no por diseño.
- Esta vez el analista escribió los dos prompts completos. **Van literales.** No se resumen, no se reordenan, no se les agregan reglas. Si algo no se puede implementar tal cual, se anota en el reporte y se implementa lo que sí; no se reinterpreta.

## 1. Cambios
**1.1 Guionista v5** — `lab/hyperframes/f15/PROMPT_GUIONISTA_v5.md` (md5 en el reporte).
- El bloque SISTEMA (`<rol>`, `<voz>`, `<estructura>`, `<oficio>`, `<ejemplos>`, `<errores>`) reemplaza entero a `guion_v4.system()`. `PROMPT_VERSION = "f15-1"`.
- El mensaje de usuario: `<caso>`, `<escaleta>` (datos con texto de la ficha y marcas; nueva marca `VERSIÓN DE: quién` para los ítems que la ficha dejó en `versiones`), `<tarea>` tal como está en el archivo. Largo abierto siempre; el parámetro `largo` queda pero el default pasa a `abierto`.
- Test: el sistema generado es byte-idéntico al bloque SISTEMA del archivo (leelo del .md en el test, no lo copies a mano).

**1.2 Ficha v2** — `lab/hyperframes/f15/PROMPT_FICHA_v2.md`.
- Se agregan al `<tarea>` y al esquema: `historia` (humanos_candidatos, giros, pico, pregunta_final), `escenas`, y en `hechos` los campos `nivel` y `sirve_para`. `PROMPT_VERSION` de la ficha: `f15-1`.
- El chequeo determinista cubre lo nuevo (ids existentes; cifras/horas/fechas respaldadas; sentidos de una escena presentes en el texto de sus ids, si no → descartados).
- El `.md` para el teléfono muestra `historia` y `escenas` arriba de todo.

**1.3 Escaleta** (`m01a_escaleta`): con ficha, el prompt lleva `historia` y `escenas` antes de `hechos`; el humano se elige entre `humanos_candidatos` (otro → `_avisos`); `imagen_sensorial` cita la escena que usa (`escena_idx`) cuando hay. Sin ficha, byte-idéntico (test, como en F14).

**1.4 Bloqueante (d) mira la ficha.** Una persona que está en `personas_descartadas` de la ficha no es contaminación. Es un cable que F14 dejó cruzado (Burl Cain, Katherine Mattes), no una regla nueva: el chequeo cambia de fuente, no de criterio.

## 2. Corridas (Sol high, sin notas, sin reparación ni editor)
| tema | ficha | escaleta | guion |
|---|---|---|---|
| Ycuá `f8s1-ycua-bolanos` | nueva (v2) | nueva | v5 |
| Orleans `ba6c3cac-f7r3` | nueva (v2) | nueva | v5 |
- Las fichas y escaletas anteriores no se pisan (sufijo `_f14` para las de F14 si todavía no lo tienen).
- Salidas en `lab/hyperframes/f15/`: fichas, escaletas, `NARRACION_<tema>_f15.md`, `guion_<tema>_f15.json`, prompts con md5.
- **`compara_f15.html`**: por tema, **mejor versión anterior | F15** por cap (Ycuá: F13 abierto; Orleans: F14), con palabras, minutos, bloqueantes, preguntas, citas, frases marcadas (tráiler, juicio, eco, analista). Arriba: embudo pool → ficha → escaleta → guion, humano elegido, pico elegido.
- **Tope: US$ 2.50** (dos fichas, dos escaletas, dos guiones).

**Advertencia que va en el reporte:** los ejemplos del prompt v5 salen de Orleans y Ycuá. En estos dos temas Sol tiene una ventaja que no tendrá en un tema nuevo. Es aceptado: son los únicos párrafos probados de 8+. Con el primer tema nuevo se mide de verdad.

## 3. Frenos
- No tocar `00_pool_v3.json`, `research_v3.py`, `m05`, `evidence.py`, `guion_v3_reglas.py`, `config.py`, `topics_db`.
- **Cero reglas nuevas** para el guion. El prompt v5 trae todo lo que se le pide al modelo; nada de eso se convierte en validador.
- Sin merge; no commitear `.env` ni `lab/_gpt_probe_analista/`.
- Tests sin red: sistema v5 byte-idéntico al archivo; ficha v2 (esquema, chequeo de escenas); escaleta sin ficha byte-idéntica; bloqueante (d) con `personas_descartadas`. Suites verdes + las 5 fallas previas; dorado de v3 verde.
- Actualizar `lab/ESTADO_SESION.md`.

## 4. Reporte `lab/hyperframes/f15/F15_REPORT.md`
1. md5 de los dos prompts contra los archivos del analista.
2. Tabla resumen y embudo, por tema.
3. Qué eligió la ficha (humanos candidatos, pico, giros) y qué eligió la escaleta de eso.
4. Qué pasó con Paiva hijo, Nagin, Cain y Mattes.
5. Costo y tokens.
6. Veredicto íntegro del revisor-handoff.

## 5. PARADA
Commit + reporte → **PARADA**. El analista revisa **el diff del código** (prompts byte-idénticos, chequeo de escenas, bloqueante (d), escaleta sin ficha intacta) y después lee fichas, escaletas y guiones, y le da a Omar la nota y la comparación.
