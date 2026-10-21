# RESUMEN F5b — arreglos de la validación (N1–N5, S1–S6) · PARADA para el analista

Rama `f5-guion-v2`, desde `1ca7194`. Sin imágenes ni render: Flash solo para guion, prompts de imagen (texto) y director. `main` intacta. Decisiones: `DECISIONES_F5.md` K1–K20.

## En una línea
Las 10 reglas están en el código y la pantalla de v2 las cumple todas (chequeo S1–S5: 0 fallas). La narración quedó con menos datos que la v2 de F5: medida por hecho, 1.12 contra 2.01 (v1: 0.86). Con las reglas nuevas, Flash no logra cumplir todo junto en 3 intentos.

## Narración (v2 regenerada, 3.ª corrida)
| | v1 | v2 F5 | v2 F5b |
|---|---|---|---|
| conteo | regex | regex | **por id declarado** |
| densidad por id (N2) | — | — | 1.26 |
| densidad por hecho (anclas distintas) | 0.86 | 2.01 | 1.12 |
| densidad por regex (medición de F5) | 1.36 | 3.29 | 3.08 |
| adjetivos/100 (N4: 2–4) | 6.22 | 2.93 | 4.19 |
| caps fuera de 2–4 adjetivos | 7 | 5 | 5 |
| caps con un dato repetido dentro del cap (N3) | 2 | 6 | **0** |
| nombres sin acción (N5) | — | Schwarz, Hubert | **ninguno** |
| datos en más de 2 caps | 2 | 0 | 0 |
| 3-gramas repetidos entre caps (< 5 %) | 3.4 % | 4.1 % | 7.0 % |
| cliffhanger con el dato en el cierre | — | 4 de 6 | 4 de 6 |

- **N1.** Salen del pool la cárcel de 1902, el capitán de la guardia, el médium y la «Inn at the Old Jail». Lo marca el propio bloque («no directamente relacionado»). «Nueva Orleans» queda. Ninguno aparece en la narración. Londres queda: su línea no tiene marcador (K2).
- **N2.** El narrador declara `datos_usados` y se cuenta lo declarado que suena literal. Con la medición de F5 los números se inflaban: un «29 de agosto» prendía 5 eventos (K18).
- **N3.** Ningún cap repite un dato. **N4.** Hay piso y techo, pero 5 caps quedan afuera. **N5.** Schwarz y Hubert salen; Hubert solo aparece como demandado (K3, a confirmar). No quedan mayúsculas pegadas.
- **Abierto:**
  - la densidad (K18);
  - los 3-gramas entre caps, que subieron a 7 %: «sheriff Marlin N. Gusman» y «Prisión Parroquial de Orleans» en todos los caps;
  - el cap 7 sin datos declarados;
  - el narrador aceptó violaciones en 6 caps (`06_judge_narrative.json`, `violaciones_narrador`).

## Pantalla (simulación de los 7 caps, sin render)
| | v1 | v2 F5 | v2 F5b |
|---|---|---|---|
| recortes (del pool) | 5 (0) | 7 (7) | 5 (5) |
| crítico suma / repite / estorba | 37 / 8 / 2 | 33 / 4 / 2 | 31 / 6 / 3 |
| caps con reloj / pregunta | 0 / 6 | 3 / 6 | 2 / 6 |

Chequeo F5b sobre v2 (`SIM_v1_v2.md`): **S1 0 · S2 0 · S3 0 · S4 0 · S5 0 fallas**.
- **S1.** Los tres recortes cortados de F5 ya no salen:
  - «piso comienzan…» → «las aguas residuales refluyen»;
  - «federal otorga…» → «Un jurado federal otorga más de $650,000» (no salió en v2: el hecho es del cap 6);
  - «la prisión no finalizó…» → sin opción.
- **S2.** Ningún recorte adelanta la fecha de la voz.
- **S3.** El cap 5 ya no muestra el jurado del cap 6, y no hay dos bloques del mismo hecho.
- **S4.** Íconos solo del mapa literal: penumbra, sofocante, escalofriante y marea ya no llevan ícono.
- **S5.** El nivel de agua muestra «4.6 metros», nunca «15 pies».
- **Abierto:** los caps 6 y 7 siguen sin recorte (P5, K19), y «repite» del crítico subió de 4 a 6. Las fotos siguen siendo las de v1 (P7).

## §1.6 / S6 — prompts de imagen de v2 (texto)
- `m03_visual` cambia solo en el canon: bloque «UBICACIONES DOCUMENTADAS» (menores → CYC/YSC; mujeres → Penitenciaría Estatal de Luisiana (Angola); evacuados → paso elevado de Broad Street sobre la Interestatal 10). Los FRENOS se respetaron. Sin pool, el canon es byte-idéntico.
- 97 prompts, 44 con personas: `PROMPTS_PERSONAS_v2.md`.
- **Reemplazo del niño en la celda:** ch04 imagen 9, ancla «En la prisión había niños de hasta 10 años». Es la mano de un chico en una celda de un centro juvenil. Los otros 2 prompts del cap 4 con niños también van al CYC.
- **Abierto:** quedan dos niños solos en celda de adultos (ch01 supp 3, ch07 Veo). ch03 imagen 10 muestra una masa de reclusos en el bloque de celdas cuya ancla incluye «niños». El canon es pasivo; la propuesta de exigirlo en el validador está anotada, no hecha (K20).

## Dónde está
- Código:
  - `researcher_steps/evidence_pool.py` (N1, N5);
  - `script_engine/evidence.py` (N2, N3, S2, S3, mayúsculas);
  - `m05_narrative.py`, `m01b_narrator.py`;
  - `gfx_pool.py` (S1–S5);
  - `gfx_fragments.py`, `gfx_director.py` y `gfx_layer.py` (S4);
  - `gfx_peak.py` (S5);
  - `m03_visual.py` (§1.6);
  - `gfx_config.py` y `gfx_profiles/misterio.json` (`icon_literal_only`, mapa).
- Tests: `test_module_f5b.py` (nuevo). Suites de guion y gfx: **379 verdes**; 3 fallas viejas en `test_module_01b_pauses.py` (J0b).
- Comparación: `lab/guion/compara_orleans.html` (v1 · v2 F5 · v2 F5b). Tablas: `GUION_v1_v2.md`, `SIM_v1_v2.md`. Cues: `cues/`. Copia versionada: `v2/` (F5b) y `v2_f5/` (F5).
- Se reproduce con `lab/hyperframes/f5/correr_f5_orleans.py --etapa todo`.
- md5 de `topics_db.json`, `normalizer_custom_dict.json` y `lexico_propuestas.json` iguales antes y después. `misterio.json` cambió a propósito (S4).

## Veredicto del revisor (revisor-handoff, íntegro; sobre el estado previo a estos dos ajustes: la obs. 2 ya está corregida arriba y la obs. 4, ESTADO_SESION, entra en este commit)

VEREDICTO: CUMPLE CON OBSERVACIONES

Qué corrí: la suite pedida dio 379 verdes y 3 fallas viejas de 01b_pauses, igual que lo esperado. No hay bytes 0x08 en ningún .py tocado ni en test_module_f5b.py ni en prompts_personas.py. No generé imágenes ni render, no hice commits ni edité nada.

| # | requisito | estado | evidencia |
|---|---|---|---|
| N1 | Filtro de relevancia en el pool | OK | `01_facts_sources.json`: 1902, médium, capitán, Old Jail solo están en `_descartados` (motivo «el bloque lo marca como no relacionado»), no en datos, lugares ni personajes. Cero apariciones en `01b_narration.json`. |
| N2 | Métricas por id declarado | OK | `06_judge_narrative.json` trae `conteo: por_id` y `datos_usados`. Densidad por id 1.26 en `GUION_v1_v2.md`, y los tres números por hecho (0.86 / 2.01 / 1.12) en `DECISIONES_F5.md` K18. |
| N3 | Cada dato una vez por cap | OK | `repetidos_en_cap` vacío en los 7 caps de v2; v1 tiene «6,500» ×2 y «500» ×4. |
| N4 | Adjetivos entre 2 y 4 por 100 | PARCIAL | Hay piso y techo en el código (`umbrales` 2.0–4.0). El resultado no cumple: 4.19 en total y 5 caps fuera de rango (cap 1 en 10.59). El RESUMEN lo declara. |
| N5 | Nombres solo si actúan; mayúsculas pegadas | OK | Schwarz y Hubert no están en el pool ni en la narración. No hay mayúsculas pegadas en el pool (regex). Hubert salió por una interpretación del propio trabajo (K3, «a confirmar»). |
| S1 | Recorte con cláusula completa | OK | `SIM_v1_v2.md`: chequeo S1 = 0 fallas, y los tres recortes cortados de F5 ya no salen. No verifiqué el código de `gfx_pool` línea por línea. |
| S2 | Sin evento posterior a la fecha de la voz | OK | Chequeo S2 = 0 fallas. Caso revisado: en ch02 el reloj dice 27 AGO hasta 00:31 y el recorte de T05 sale a 00:37, ya fuera de ese tramo. |
| S3 | Dedupe por hecho; solo cap actual y anteriores | OK | Chequeo S3 = 0 fallas. Los recortes de ch05 son T13 (cap 4) y T12; ya no aparece el jurado del cap 6. |
| S4 | Ícono solo por mapa literal | OK | Chequeo S4 = 0 fallas; `icon_literal_only` y el mapa están en `gfx_config.py` y `misterio.json`. Observación: ch04 anota «falta ícono rayo_tachado» en el recorte de los generadores; es consistente con la regla, pero queda un recorte sin ícono. |
| S5 | Unidades métricas en pantalla | OK | ch02 muestra «4.6 metros». `gfx_peak.py:133` convierte pies a metros. La voz sí dice «15 pies» (correcto). |
| S6 | §1.6 con FRENOS | OK | `git diff m03_visual.py` solo agrega `_LOC_GROUPS` y las funciones de ubicaciones. La única línea eliminada es `{blocklist_block}`, reemplazada por la misma más `{loc_block}`. No se tocaron los validadores, el fluidificador, los rangos, el plan de anclas ni los hard_fact_ids. Sin pool, el canon queda igual. |
| S6b | Prompts v2 y anclas con personas; reemplazo del niño | OK | `PROMPTS_PERSONAS_v2.md`: 97 prompts, 44 con personas, y el reemplazo marcado (ch04 flux 9, «niños de hasta 10 años», mano de un chico en el centro juvenil). |
| E | Entregables | OK | Existen `RESUMEN_F5b.md` (5 KB), `PROMPTS_PERSONAS_v2.md`, `GUION_v1_v2.md`, `SIM_v1_v2.md`, `cues/`, `v2/` y `v2_f5/`. Las cifras del RESUMEN coinciden con los json y md: 5 recortes, crítico 31/6/3, 2 caps con reloj, 6 con pregunta, 3-gramas 7.0 %, violaciones en 6 caps, cliffhanger 4 de 6. Las de v2 F5 y v1 (2.01, 4.1 %) no las pude contrastar contra un archivo propio. |

Observaciones:
1. El RESUMEN admite lo no logrado: densidad baja (1.12 contra 2.01 de F5, y bajo el umbral de 2.0), caps 6 y 7 sin recorte (P5), adjetivos fuera de rango en 5 caps, 3-gramas en 7 % y cap 7 sin datos declarados.
2. Subestima los niños en celda de adultos. El RESUMEN dice «dos» (ch01 supp 3 y ch07 Veo), pero `PROMPTS_PERSONAS_v2.md:32` marca también ch03 flux 10, que menciona niños en una masa de reclusos «NO respeta el canon». Es un grupo, no un niño solo, pero conviene contarlo.
3. «Cliffhanger con el dato en el cierre» pasa de 4 a 6 a 4 de 6, o sea sin mejora. En cap 3 y en otro cap el cierre no lleva el dato.
4. `lab/ESTADO_SESION.md` no figura como modificado, y CLAUDE.md exige actualizarlo en cada hito. Falta hacerlo antes o junto al commit.
5. La sección «Veredicto del revisor» del RESUMEN está vacía; hay que pegar este veredicto ahí.
6. La regla del RESUMEN sobre N5 (Hubert) depende de una confirmación pendiente del analista.

Fuera de alcance: `diag_234_cap4.py` aparece modificado y, según el pedido, no es nuestro; no debe entrar al commit. También hay muchos untracked ajenos (`_lab_*`, `_probe_*`, `QA_*`, `cap4_*`, `lab/hyperframes/{lab_cap,limpio,prueba,renders,snapshots,v2}`, `lab/identidad/plan_ch02_lab*`, `preset_sweep_out`), que tampoco deben incluirse. Los archivos nuevos de F5b que sí hay que agregar son `test_module_f5b.py`, `prompts_personas.py`, `PROMPTS_PERSONAS_v2.md`, `RESUMEN_F5b.md`, `VALIDACION_F5.md`, `v2_f5/`, `v2/03_visual.json`, `v2/06_judge_narrative_v2f5.json` y `pruebas/`.

Riesgos que el contrato no cubre:
- El canon de ubicaciones es solo texto de contexto, sin validador (K20), así que los prompts pueden seguir mezclando niños con adultos al generar imágenes reales.
- Con la narración aceptada con violaciones, el analista y Omar juzgan una v2 más pobre en datos que la de F5.
- Las fotos de la simulación son las de v1 (P7), por lo que la pantalla no está validada con imágenes reales.
