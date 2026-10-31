# F65a Etapa B — FASE2_JUICIO: las 13 fichas del papel actual por el camino de Fase 2, con y sin `juicio_verificador`

Papel `m01e-7` (claude-opus-5-5), entrada de hoy; palabras con tiempos sintetizadas de la narración (0.34 s por palabra, sin escenas: `lectura` corre con esos tiempos, no con la voz real). Fase 2 no llama al verificador: solo lee `juicio_verificador.tokens` de la ficha.

| cap | beat | ficha | estilo | juicio_verificador (regla, tokens) | validar_papel SIN juicio | validar_papel CON juicio | chequeo 5 SIN juicio | chequeo 5 CON juicio | cambia |
|---|---|---|---|---|---|---|---|---|---|
| ch01 | 1 | D108 | normal | ['no_dicho'] {'no_dicho': ['Australia']} | **no_dicho**: la voz lo dice en la oración ancla o en una vecina: ['Australia'] | pasa | — | — | **sí** |
| ch02 | 2 | Q25 | cita | ['spoiler'] {'spoiler': ['2']} | **spoiler**: la voz lo dice en una oración posterior del cap: ['2'] | pasa | — | — | **sí** |
| ch02 | 3 | D83 | normal | — | pasa | pasa | — | — | no |
| ch03 | 4 | D02 | normal | — | pasa | pasa | — | — | no |
| ch03 | 5 | D01 | normal | ['spoiler'] {'spoiler': ['3']} | pasa | pasa | — | — | no |
| ch03 | 6 | D115 | normal | — | pasa | pasa | — | — | no |
| ch04 | 7 | Q19 | cita | — | pasa | pasa | — | — | no |
| ch04 | 8 | D102 | normal | — | pasa | pasa | — | — | no |
| ch05 | 9 | D51 | normal | — | pasa | pasa | — | — | no |
| ch05 | 10 | D23 | papel | ['contradice'] {'contradice': ['30', '2024']} | pasa | pasa | 500 personas vs 30 («Nueve meses después del diagnóstico, Daniel Écija murió en  | — | **sí** |
| ch06 | 11 | D34 | normal | — | pasa | pasa | — | — | no |
| ch06 | 12 | D40 | normal | — | pasa | pasa | — | — | no |
| ch07 | 13 | D61 | papel | — | pasa | pasa | — | — | no |

- Fichas con `juicio_verificador`: 4 (D108, Q25, D01, D23); de ellas, sin juicio Fase 2 cortaría 2 y marcaría en el chequeo 5 1; con juicio pasan 4 y el chequeo 5 marca 0.
- Fichas sin juicio: 9; ninguna cambia entre las dos columnas (OK).
- Lo que corta en ambas columnas es independiente del juicio (p. ej. `lectura` con tiempos sintéticos, o candado): []
