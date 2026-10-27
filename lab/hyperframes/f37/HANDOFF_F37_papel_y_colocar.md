# HANDOFF F37 — El papel elige más y mejor; Fase 2 mueve en vez de cortar

Analista · 2026-10-26 22:40 · Para CC. Base: `2067c77` (F36 cierre). **Tres partes A (autor) → B (colocar) → C (corrida de Vajont), un commit cada una.** PARADA solo al final de C, o antes si se da una de las condiciones de §Frenos. Sin render, sin `--aprobar-guion`. Contrato: `lab/hyperframes/f36/REVISION_PAPEL.md` (revisión del analista del papel de F36, con DEBERÍA por línea). Reglas de Omar que mandan esta tanda (DECISIONES 22:26 y 22:32): **casi nada hardcode; todo arreglo es general (sirve para cualquier tema); ante cada falla, la causa se arregla en el sistema, no con ediciones a mano.**

## 0. Antes de tocar nada
1. Commitear `DECISIONES.md` tal cual (22:26, 22:32, orden 3b).
2. **¿Construye sobre código que se reemplaza?** No. ¿Cambia el orden? No.
3. **Módulos que toca** (stickers del mapa): `m01e_pantalla` (Fase 1: el autor) · `rotulista_filtros` (validaciones) · `rotulista_colocar` y `clima` (mover en vez de cortar) · `gfx_critic` (re-juicio tras mover) · `gfx_director` (se borra el borrador) · `gfx_layer`, `fase2b` (papel = único camino) · `voz_utils` (velocidad del narrador) · `gfx_config`/perfil (constantes que salen del código) · renombres de B.5 · `lab/MAPA_MODULOS.*`.
4. **Constantes — ninguna nueva en el código.** Las dos que hoy están fijas en `m01e_pantalla.py` salen del código:
   | constante | hoy | después | origen |
   |---|---|---|---|
   | `SEG_POR_PALABRA` 0.35 | fijo, medido en un cap de Vajont | **derivado** en cada corrida: mediana de s/palabra de todas las voces ya generadas con el mismo narrador (tiempos de palabra de ElevenLabs en `output/*/`); 0.35 solo como respaldo si no hay ninguna, anotado en el papel | medido |
   | `TOPE_USD` 0.50 | fijo en el código | clave del perfil/config de costos (donde viven los otros topes del pipeline; si no hay lugar, `gfx_profiles/misterio.json` → `costos.m01e_tope_usd`) con **valor 1.00** | decisión de Omar (voto del analista: 1.00 = la llamada + un reintento con margen; la primera costó 0.31) |
   Duración de ficha: `callout_dur_min` 2.5 y `callout_dur_max` 6.0 del perfil (identidad F3). Lectura 15 cps (estándar).

## A. El autor (`m01e_pantalla`) — ve lo que el pool sabe y se corrige solo (commit A)
**Causa raíz de cada falla del papel de F36** (`REVISION_PAPEL.md`) y su arreglo general:
1. **Cita pegada a un momento equivocado (Q43).** Causa: el archivo que recibe el autor no trae `fecha` ni `rol` (el pool los tiene) y 41 de 57 citas no tienen fecha desde el research. Arreglo:
   - a) cada ítem del archivo lleva `fecha` (o `"desconocida"`), y las citas `rol` y `testimonio` (sí/no), tal como están en el pool;
   - b) validación en papel (código, sin modelo) **«fecha del relato»**: el momento del relato en una oración = el último **año** que la voz dijo en el video hasta esa oración (arrastra de caps anteriores; con `voz_utils`, años en letras incluidos). Se compara por **año**, no por día (las fechas relativas de la voz, «tres días después», no se parsean). Un ítem con año **posterior** a ese momento se rechaza, salvo que sea `testimonio: true` (los testimonios se cuentan después) o que la oración ancla o su vecina lo sitúe después («años después», «más tarde», un año posterior dicho);
   - c) **cita sin fecha y no testimonio**: solo vale si su autor (nombre o rol) aparece en la oración ancla o en una vecina; si no, se rechaza. (Q43: su autor «ingeniero jefe, sucesor de Semenza» no está en la voz → cae solo.)
   - simulación del analista con el papel de F36 (año): Q14 (1963) en ch07 [1] pasa (último año dicho: 1963); D245 (1997) en ch07 [18] pasa porque la vecina [19] dice «dos mil»; D105 (1962) en ch04 [16] pasa (1963 ya dicho); T39 (1961) en ch04 [6] pasa (lo dice la misma oración); Q43 (sin fecha) cae por 1c. Pegar en el reporte la tabla real de todas las fichas del papel con su año y el momento del relato.
   - d) anotar para Fase 1 (no se toca ahora): el research debería traer fecha y contexto de las citas.
2. **Descarte con motivo falso (T39 «la voz ya lo dice»).** Causa: el código no verifica lo que el modelo afirma. Arreglo: el formato de `descartados` suma `"tipo": "voz_lo_dice" | "spoiler" | "repetido" | "otro"` (cambio de formato, no de estilo). Para `voz_lo_dice`, el código busca las cifras y nombres del ítem en la voz del cap (con `no_dicho`); si la voz **no** los dice, el ítem vuelve como candidato en el reintento con el motivo («T39: dijiste que la voz lo dice; la voz no dice “50 millones”»).
3. **Beats pico vacíos (ch02 b3, ch04 b7) y gancho tarde (1:26).** Causa: la regla del gancho no dice cuándo, y nada exige ficha en el pico. Arreglo:
   - a) prompt: **reemplazar** (no agregar) en `PANTALLA_SYSTEM`, literal: «en el gancho (capítulo 1), cualquier dato del archivo que la voz no diga en todo el video y que haga quedarse a quien mira: el gancho nunca queda sin ficha.» → «en el gancho (capítulo 1), cualquier dato del archivo que la voz no diga en todo el video, que haga quedarse a quien mira y que pueda ir en las primeras oraciones del capítulo: el gancho nunca queda sin ficha.» `PROMPT_VERSION = "m01e-2"`, md5 antes/después en el reporte.
   - b) validación: **beat pico sin ficha** → reintento nombrando esos beats («el beat 3 de ch02 es pico y quedó sin ficha»). Si en el reintento sigue vacío, queda vacío y el `.md` lo marca ⚠.
4. **Falsos positivos por número suelto (D47 «2», D105 «1962»).** Causa: `spoiler` y `no_dicho` comparan números sin saber si es el mismo hecho, y eso no se resuelve con listas de palabras. Arreglo: en el papel, cuando el código encuentra la coincidencia, **no corta: le pregunta al autor en el reintento** («D47: la voz dice “dos kilómetros” en ch03 [17] (“fisura de casi dos kilómetros de largo”); ¿es el mismo hecho? si no, mantenelo») y la respuesta del reintento es final. El código encuentra; el autor, que ve toda la historia, juzga. En Fase 2, `no_dicho`/`spoiler` respetan ese juicio (no re-cortan lo que el autor ya confirmó como distinto).
5. **Reintento:** uno solo, con **todos** los motivos juntos (1b/c, 2, 3b, 4), dentro del tope del perfil. Medir tokens y costo de las dos llamadas.
6. Tests (uno por punto, con el caso real de Vajont): Q43 cae por 1c; un ítem con fecha posterior cae y un testimonio no; T39 vuelve en el reintento; pico vacío dispara reintento; D47 llega al reintento como pregunta, no como corte; `SEG_POR_PALABRA` se deriva de los tiempos existentes; `TOPE_USD` se lee del perfil.

## B. Colocar (Fase 2) — mover en vez de cortar (commit B)
**Causa:** Fase 2 tiró 8 de 18 elecciones del papel por razones de colocación (3 sellos por cruzar un corte, 3 sellos + D117 por el crítico, Q50 por lectura). Lo que el autor eligió no se corta por una razón mecánica: se mueve.
1. **Orden de intentos** para ficha, sello y reloj que no entra (corte de escena, lectura, «nunca al mismo tiempo» o crítico «estorba»), sin números nuevos:
   1) otro instante dentro de la misma oración (palabra de más peso, inicio, palabra ancla);
   2) el inicio de la escena siguiente si cae dentro de la misma oración;
   3) la oración siguiente del mismo beat;
   4) solo para el crítico: las otras posiciones de pantalla que la plantilla **ya** soporta (si soporta una sola, este paso no existe; no se agregan posiciones);
   cada intento vuelve a pasar los filtros mecánicos y el crítico (caché por identidad). Si ninguno entra → «papel sin colocar» con la lista de intentos y por qué falló cada uno.
2. **Duración de la ficha** = lectura (15 cps) acotada entre `callout_dur_min` y `callout_dur_max` del perfil, y nunca más allá del corte (hoy T16 12.7 s, D131 11.2 s).
3. **Lectura de una cita:** el autor ya va en el texto de la ficha; no contarlo dos veces (abierto 8 de F36).
4. **Papel = único camino:** se borra el borrador del director (Gemini) y su prompt; el title card sale del título de la partición; `--rotulista` deja de existir como opción (implícito); se borran los restos apagados que listó el revisor (abierto 19 de F36: `gfx_critic.describe`/`KIND_LABEL`, el `pop` de bloques borrados en `gfx_layer`, ramas de contador/íconos en `gfx_realizador.finalizar`, `gfx_literal_lock`, `gfx_guion.eventos_cap`, `gfx_style.golden_fewshot`, docstring de `gfx_pool`) y el código muerto del abierto 13. Mapa con **0 muertos**.
5. **Renombres** (el nombre dice lo que hace hoy; ninguno escribe): `gfx_rotulista` → `pantalla_entrada`, `rotulista_filtros` → `pantalla_filtros`, `rotulista_colocar` → `pantalla_colocar`; imports, tests, mapa y docs; los runners de lab viejos rotos (abierto 15 de F36) se borran.
6. Tests: un sello que cruza el corte se mueve al intento 1 o 2 (AVISO ch04, SILENCIO ch05, COLAPSO ch06); el crítico re-juzga en la otra posición (si existe) y no tira a la primera; Q50 se mueve a la oración siguiente si no cabe; ninguna ficha dura más de `callout_dur_max`.

## C. Corrida de Vajont y comparación (commit C)
1. `m01e_pantalla` suelto para Vajont (tope del perfil) → `01e_pantalla.md` entero en el reporte, con el reintento y sus motivos.
2. `fase2b f8s3-vajont-f30 --plan-only` → guion.
3. **Simulador contra `REVISION_PAPEL.md`**, línea por línea: qué DEBERÍA salió solo por las reglas generales y qué no (y por qué). Se espera, sin edición a mano: gancho anclado en las primeras oraciones de ch01; T39 de vuelta en ch04; ningún pico vacío (o ⚠ explicado); Q43 fuera por 1c; D47 y D105 juzgados por el autor; los 8 cortes de F36 colocados o con su lista de intentos; ninguna ficha > 6 s. **Lo que solo es gusto** (qué dato va en el gancho, D195 en el clímax, D128 vs D17) **no se fuerza**: se lista para la compuerta de Omar.
4. Totales (fichas, sellos, relojes, tarjeta, punches), «papel sin colocar», costo, tokens. `F37_REPORT.md` con lo abierto entero y el veredicto íntegro del revisor; `ESTADO_SESION.md`. **PARADA.**

## Frenos
Sin render, sin aprobar, sin merge, sin tocar prompts de escaleta/guionista/partición. El único cambio de prompt es el reemplazo literal de A.3a (más el campo `tipo` de A.2 en el formato). Ningún número nuevo en el código: si algo pide uno, PARADA y preguntar. PARADA anticipada si: el JSON del papel no parsea en dos intentos; el tope no alcanza para el reintento; alguna narración no alinea; o los renombres rompen la suite. `.env`, `config.py`, `_gpt_probe_analista/`, `gfx_profiles/*` fuera de git (si `TOPE_USD` va al perfil, dejar la clave para que Omar la agregue y leer con respaldo).
