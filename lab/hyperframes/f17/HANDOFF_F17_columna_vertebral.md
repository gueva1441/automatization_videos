# HANDOFF F17 — La columna vertebral: la historia se decide en una página antes de la escaleta

Analista · 2026-10-23 · Para CC, **en sesión nueva** (pedido de Omar). Base: `fceeee3` (rama `f11-guion-v4`; seguí en la misma). Ficha → columna → escaleta → guion. Sin producción.

## 0. Por qué (del disco)
- F16 funcionó en lo técnico (escaleta por Sol, 13 bloqueantes, 8 escenas, 6 giros, guion de 11 min sin bloqueantes), pero Ycuá dio 6.5: gancho abstracto («ese acceso terminará discutido en un juicio»), pico de 46 palabras en un solo beat, 15 personas con nombre, voz de informe en el cap 3.
- El guionista escribió bien lo que le dieron. La escaleta eligió mal qué contar, porque le pedimos decidir todo de una vez (humano, pico, 13 beats, imágenes, cierres, pantalla) a partir de 47 k caracteres.
- Agregar instrucciones a la escaleta es volver a las reglas. En vez de eso, **se divide la decisión**: primero la columna vertebral (una página: humano, pico, qué pasa en cada cap, con qué termina, qué queda afuera), después la escaleta la rellena con beats.
- La columna la puede leer Omar en un minuto antes de gastar en escaleta y guion.

## 1. Cambios
**1.1 Paso nuevo `m01a_columna`** — prompt en `lab/hyperframes/f17/PROMPT_COLUMNA_v1.md` (md5 en el reporte). SISTEMA literal; usuario = caso + ficha completa (misma sección que hoy usa la escaleta) + tarea literal. Sol high. Salida: JSON del esquema del archivo. Se guarda `01a_columna.json` + `COLUMNA_<tema>.md` (la página legible, con la forma del ejemplo). `PROMPT_VERSION = "f17-1"`.
- Chequeo determinista, sin LLM: 7 caps, humano es persona de la ficha, ids existen, personas de cada cap existen en la ficha. Si falla, una regeneración; si vuelve a fallar, PARADA. Nada más rechaza.
- Métrica informativa: cantidad de personas distintas con nombre en toda la columna.

**1.2 Escaleta v2 lee la columna** (`m01a_escaleta`, solo con ficha): la columna va en el usuario **antes** de la ficha, y la tarea cambia al texto literal de la sección «CÓMO SE USA LA COLUMNA» del archivo. Sistema de la escaleta sin cambios. Bloqueantes: los 13 de F16, ninguno más. Métricas nuevas (informativas): humano = columna, personas por cap ⊆ columna, cierre = «termina». `PROMPT_VERSION` de la escaleta: `f17-1` solo cuando hay columna; sin columna, byte-idéntica a F16 (test).

**1.3 Guion v5.1:** sin cambios.

**1.4 `fase1_5`:** con ficha, m01a = columna → escaleta. Flag `--sin-columna` para reproducir F16.

## 2. Corridas (fichas v2 de F15b, sin rehacer)
- **Ycuá primero, en dos tiempos:**
  1. Solo la columna. Guardá `COLUMNA_ycua.md` y **PARADA corta**: el analista y Omar la leen (es una página). Si Omar dice «dale», seguís; si pide cambios, se anotan en `_steps/<topic>/columna_notas.md` y se regenera la columna **una vez** con las notas en la tarea (solo esa vez; no es un canal permanente).
  2. Escaleta v2 con columna → guion v5.1.
- **Orleans después**, completo en una pasada (columna → escaleta → guion), sin parada intermedia.
- Salidas en `lab/hyperframes/f17/`: columnas (.json y .md), escaletas, `NARRACION_<tema>_f17.md`, prompts con md5. No pisar `_f16`.
- **`compara_f17.html`**: por tema, arriba la columna (humano, pico, las 7 filas, afuera); después F16 | F17 por cap, con palabras, personas con nombre por cap, bloqueantes, escenas usadas, frases marcadas.
- **Tope: US$ 2.00** (columnas ~US$ 0.10 cada una).

## 3. Frenos
- **Cero reglas nuevas** en guion ni escaleta. El chequeo de la columna es estructura e ids, nada de estilo.
- No tocar el pool, `research_v3`, `ficha_caso.py`, `m05`, `evidence.py`, `guion_v3_reglas.py`, `config.py`, `topics_db`, `m03*`, `gfx_*`.
- Los tests no escriben en `data/cost_history.json` (hay 59 entradas de prueba `t-f11b` por US$ 100 falsos; sacarlas y que el tracker no registre cuando corre pytest). **Chascada.**
- Sin merge; no commitear `.env` ni `lab/_gpt_probe_analista/`.
- Tests sin red: sistema de la columna byte-idéntico; esquema y chequeo; escaleta sin columna byte-idéntica a F16; `--sin-columna`. Suites verdes + las 5 previas; dorado de v3 verde.
- Actualizar `lab/ESTADO_SESION.md`.

## 4. Reporte `lab/hyperframes/f17/F17_REPORT.md`
1. md5 del prompt contra el archivo.
2. Las dos columnas tal cual (es lo que Omar lee).
3. Por tema: ¿la escaleta respetó la columna? (humano, personas por cap, cierres). Tabla F16 | F17 del guion.
4. Costo y tokens. Nota de la limpieza de `cost_history`.
5. Veredicto íntegro del revisor-handoff.

## 5. PARADAS
- **Parada 1:** después de `COLUMNA_ycua.md`. Avisá y esperá el «dale» de Omar.
- **Parada 2:** commit + reporte al final. El analista revisa el diff y lee columnas, escaletas y guiones. Si Ycuá da ≥ 8, lo que sigue es producción.
