# HANDOFF F13 — Largo abierto: ¿qué escribe Sol cuando no le exigimos 1,500 palabras?

Analista · 2026-10-23 · Para CC. Base: `b204868` (rama `f11-guion-v4`; seguí en la misma). **Solo narración.** Sin escaleta nueva, sin ficha, sin imágenes, voz ni producción.

## 0. Por qué
- Orleans por v4 (prompt `f11c-1`, Sol high, una llamada, sin notas): 1,456 palabras, 1 bloqueante falso (Nagin, descartado por el pool pero usado por la escaleta), 0 inventos. Nota del analista: 7. Está en `lab/_gpt_probe_analista/orleans/` (corrida del analista, fuera del pipeline).
- El defecto que queda, y es el mismo en Ycuá: **relleno para cumplir el largo**. El cap 3 de Orleans repite cuatro veces lo mismo porque tiene 3 datos y 250 palabras obligatorias.
- Omar: el largo de 1,500 palabras es una hipótesis sin medir. Se prueba qué pasa cuando no se exige.

## 1. Cambio (es sacar, no agregar)
- Parámetro `largo` en `guion_v4` con dos valores: `objetivo` (lo de hoy) y `abierto`.
- Con `abierto`:
  - el prompt **no trae** ni «≈ N palabras» en los caps ni la línea de total en `<tarea>`;
  - en su lugar, una sola frase en `<tarea>`: «Cada cap dura lo que su historia necesita: ni relleno ni resumen.»;
  - el bloqueante (c) de largo (cap fuera de ±25 %) **no se evalúa**; quedan beat faltante, cap vacío y el tope `max_words`;
  - lo demás del prompt (sistema con rol, voz, oficio y ejemplos; usuario con datos y tarea al final) queda idéntico.
- `PROMPT_VERSION = "f13-1"` solo cuando `largo=abierto`; con `objetivo`, el prompt es byte-idéntico a `f11c-1` (test).

## 2. Corridas (Sol high, una llamada cada una, sin notas, sin reparación ni editor)
| corrida | tema | escaleta | largo |
|---|---|---|---|
| `_f13_orl_abierto` | Orleans `ba6c3cac-f7r3` | `01a_escaleta.json` (md5 `2f794418…`) | abierto |
| `_f13_ycua_abierto` | Ycuá `f8s1-ycua-bolanos` | `01a_escaleta_v1.json` (md5 `e1ba1a48…`) | abierto |
- Referencias con largo objetivo, **sin volver a correr**: Orleans = `lab/_gpt_probe_analista/orleans/orleans_v4c_sol.json` (el analista lo corrió con el prompt `f11c-1` tal cual); Ycuá = `lab/hyperframes/f11c/guion_ycua_v4c_sol.json` (crudo).
- Salidas en `lab/hyperframes/f13/`: `NARRACION_<tema>_f13_abierto.md`, `guion_<tema>_f13_abierto.json`, `prompt_<tema>_f13.txt`. No se pisa nada; no se escribe en `topics_db`.
- **`compara_f13.html`** (misma forma que `compara_f11c.html`): por tema, dos columnas lado a lado, **objetivo | abierto**, por cap, con palabras, bloqueantes, preguntas y las frases marcadas en color. Arriba, tabla resumen con: palabras totales, **minutos estimados a 2.05 palabras/s**, palabras por cap, bloqueantes, duras v3 re-medidas, citas, cierre, costo.
- Agregá a la tabla una métrica **«repetición interna»**: % de 3-gramas de contenido que se repiten dentro del mismo cap (usá `m05._trigrams` sobre el cap consigo mismo; no rechaza, solo mide). Es la medida del relleno.
- **Tope: US$ 0.50.**

## 3. Frenos
- Cero reglas nuevas. No tocar `m05`, `evidence.py`, `guion_v3_reglas.py`, `config.py`, el pool ni las escaletas.
- Sin merge; no commitear `.env` ni `lab/_gpt_probe_analista/`.
- Tests sin red: `largo=objetivo` byte-idéntico a `f11c-1`; `largo=abierto` sin cifras de largo en el prompt; el bloqueante (c) de largo apagado solo con `abierto`. Suites verdes + las 5 fallas previas.
- Actualizar `lab/ESTADO_SESION.md`.

## 4. Reporte `lab/hyperframes/f13/F13_REPORT.md`
1. Tabla resumen (la del html).
2. Costo y tokens.
3. Veredicto íntegro del revisor-handoff.

## 5. PARADA
Commit + reporte → **PARADA**. El analista lee las dos versiones abiertas y le dice a Omar si el guion gana filo al soltar el largo, y cuántos minutos daría cada video.
