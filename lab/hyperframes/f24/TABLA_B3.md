# F24 §B.3 — prueba de modelo en la escaleta (Kyshtym, ficha v2.2 de F23, prompt f24-1)

Prompt de la escaleta f24-1: bloque SISTEMA md5 `006a195f0ce4be014df34d71644aedb1` (la f22-2 `22cfd68b…` con la línea de
`<errores>` de §B.2). Orden de corrida: F1 (Fable), S1 (Sol), S2 (Sol), F2 (Fable), y después un guion con Fable de cada
escaleta mientras entrara en US$ 2.00. **Gasto de B.3: US$ 1.6568.**

| | modelo | 1.ª pasada: beats por cap | caps fuera de 1–3 (1.ª) | bloqueantes 1.ª → 2.ª | final: beats por cap | ids | apoyos/beat | promesa (1.ª pasada → final) | guion |
|---|---|---|---|---|---|---|---|---|---|
| F1 | claude-fable-5-1 high | — (cortada) | — | se cortó en `max_tokens` 16 000 (US$ 1.0549, 25 491 in) sin JSON utilizable; la regeneración no se intentó (una sola facturación por llamada) | — | — | — | — | no |
| S1 | gpt-6.1-sol high | 1·1·2·2·2·3·3 (14) | **0** | 11 → **1** («humano Q17 no es una persona del pool»: puso el id de una cita como humano) → PARADA | — (rechazada) | — | — | «¿Cómo se borra del relato público una explosión que hizo temblar un edificio?» → «¿Cómo se oculta una catástrofe que hizo temblar el edificio donde un electricista miraba una película?» | no |
| S2 | gpt-6.1-sol high | 1·1·2·1·3·3·3 (14) | **0** | 19 → **0** | **1·1·2·2·2·3·3** (14) | 44 | 2.14 | «¿Cómo se consigue ocultar una nube que ya salió de la fábrica?» (pregunta, sin resumen) | no (tope) |
| F2 | claude-fable-5-1 high | — | — | no corrió: el freno (1.657 + peor caso 0.984 > 2.00) | — | — | — | — | no |

Palabras por cap del guion: **ningún guion corrió**. Después de las escaletas quedaban US$ 0.34 de B.3 y el peor caso de
un guion con Fable es US$ 1.14.

Los bloqueantes de la 1.ª pasada son casi todos de forma (`dato_central` con el texto pegado al id, «P22: …», y un id de
`a_pantalla` repetido en un beat). Ninguno es de reparto: en F23 había 6 beats en el cap 6, y acá ninguna 1.ª pasada de
Sol se sale de 1–3.

**Decisión: la escaleta de la parte C queda en Sol.** Criterio del handoff: menos caps fuera de 1–3 en la 1.ª pasada y
una promesa sin resumen. Sol tiene 0 caps fuera en las dos pasadas, y sus tres promesas son preguntas. Fable no llegó a
devolver una escaleta: con 16 000 tokens de salida se cortó. Además, una pasada de Fable (≈ US$ 1.05) no entra en el tope
de escaleta de la parte C (US$ 0.40 por tema).
