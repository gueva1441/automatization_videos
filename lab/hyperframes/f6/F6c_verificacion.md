# F6c — Verificación LITERAL de testimonios (Orleans v3)

Regla del analista: se baja el documento fuente y se busca la cita literal (no el dominio). El documento vale si es de ≤ 2025 y nombra el lugar o el evento. Verificada = literal + el autor a ≤ 400 caracteres; literal sin el autor = se usa sin nombre.

## Documentos

- **bbc_rebelion** — «Los presos de Katrina», Olenka Frenkiel (BBC) — copia en rebelion.org · https://rebelion.org/los-presos-de-katrina/
- **aclu_2006** — ACLU National Prison Project, «Abandoned and Abused» (2006) · https://www.aclu.org/sites/default/files/pdfs/prison/oppreport20060809.pdf
- **thelens_2025** — The Lens, «Reforms resulted from the thousands left to drown in OPP» (2025) · https://thelensnola.org/2025/08/29/reforms-resulted-from-the-thousands-left-to-drown-in-opp/

## Resultado: {'verificada': 2, 'encontrada_sin_autor': 0, 'sin_verificar': 5}

| id | autor | estado | documento | motivo |
|---|---|---|---|---|
| Q03 | Edward “Edgar” Burton | **verificada** | thelens_2025 | literal en thelens_2025 |
| Q04 | Vincent Norman | **verificada** | bbc_rebelion | literal en bbc_rebelion |
| Q06 | Vincent Norman | **sin_verificar** | — | no está literal en ['bbc_rebelion', 'aclu_2006', 'thelens_2025'] |
| Q07 | Rhonda Ducre | **sin_verificar** | — | no está literal en ['bbc_rebelion', 'aclu_2006', 'thelens_2025'] |
| Q11 | una presa anónima, 35 años, del edificio Conchetta | **sin_verificar** | — | no está literal en ['bbc_rebelion', 'aclu_2006', 'thelens_2025'] |
| Q12 | una presa anónima del TCI (Templeman IV) | **sin_verificar** | — | no está literal en ['bbc_rebelion', 'aclu_2006', 'thelens_2025'] |
| Q13 | un preso anónimo, 19 años, del TCI (Templeman IV) | **sin_verificar** | — | no está literal en ['bbc_rebelion', 'aclu_2006', 'thelens_2025'] |
| D95 | (dato) | **verificada** | bbc_rebelion | literal en bbc_rebelion |

## Fuera del pool

- Q08 (citas): contaminación: Lenore Burnley / Chad Joseph salen de una nota de la ACLU de 2026 sobre Trinidad, no de Orleans 2005 (validación del analista)
- P12 (personajes): contaminación: Lenore Burnley / Chad Joseph salen de una nota de la ACLU de 2026 sobre Trinidad, no de Orleans 2005 (validación del analista)
- D78 (datos): contaminación: Lenore Burnley / Chad Joseph salen de una nota de la ACLU de 2026 sobre Trinidad, no de Orleans 2005 (validación del analista)
- D79 (datos): contaminación: Lenore Burnley / Chad Joseph salen de una nota de la ACLU de 2026 sobre Trinidad, no de Orleans 2005 (validación del analista)
- Q05 (citas): atribución errónea: en la ACLU 2006 «It was like a concentration camp» lo dice un preso anónimo sobre la cárcel de Hunt, no Vincent Norman ni la OPP

## Testimonios literales que hay en las fuentes y NO se sumaron (el pedido era solo los 103 días)

- BBC 2006: Andrew Joseph dice haber visto un cuerpo flotando con una rata sentada en el pecho.
- BBC 2006: «Nos abandonaron a nuestra suerte» — Cardell Williams, dos meses preso sin acusación.
- BBC 2006: la ayudante Rhonda Ducre, sola en un ala, con una linterna casi sin pilas: «Agitaban las barras, prendían fuego las cosas, gritaban y trataban de salir de sus celdas. Era peligroso».
- ACLU 2006: «fearing we were left for dead» (preso anónimo); testimonios con número de recluso.

## Log

- [pool] Q08 fuera por contaminación (Burnley / Chad Joseph, ACLU 2026, Trinidad)
- [pool] P12 fuera por contaminación (Burnley / Chad Joseph, ACLU 2026, Trinidad)
- [pool] D78 fuera por contaminación (Burnley / Chad Joseph, ACLU 2026, Trinidad)
- [pool] D79 fuera por contaminación (Burnley / Chad Joseph, ACLU 2026, Trinidad)
- [pool] Q05 fuera: atribución errónea (ACLU 2006: preso anónimo, cárcel de Hunt)
- [pool] Q04 → literal de la BBC «Simplemente abandonaron la cárcel» (antes «Básicamente abandonaron la prisión»)
- [pool] D95 nuevo: Norman, 103 días (literal BBC)
- [literal] Q03 Edward “Edgar” Burton: verificada — literal en thelens_2025
- [literal] Q04 Vincent Norman: verificada — literal en bbc_rebelion
- [literal] Q06 Vincent Norman: sin_verificar — no está literal en ['bbc_rebelion', 'aclu_2006', 'thelens_2025']
- [literal] Q07 Rhonda Ducre: sin_verificar — no está literal en ['bbc_rebelion', 'aclu_2006', 'thelens_2025']
- [literal] Q11 una presa anónima, 35 años, del edificio Conchetta: sin_verificar — no está literal en ['bbc_rebelion', 'aclu_2006', 'thelens_2025']
- [literal] Q12 una presa anónima del TCI (Templeman IV): sin_verificar — no está literal en ['bbc_rebelion', 'aclu_2006', 'thelens_2025']
- [literal] Q13 un preso anónimo, 19 años, del TCI (Templeman IV): sin_verificar — no está literal en ['bbc_rebelion', 'aclu_2006', 'thelens_2025']
- [literal] D95 : verificada — literal en bbc_rebelion
