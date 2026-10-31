# F67a_REPORT — ¿el crítico de retención por API critica como el analista?

Handoff `HANDOFF_F67a_critico_por_api.md` v3, md5 `d68e9c1741baccc4a48de0785449d41a` · rama `f11-guion-v4` · base `8119681` · CC Opus 5.5 medium. Lab de solo texto: **no se corrió ni se escribió nada de producción.** Costo total **US$ 5.02**. Las 4 corridas devolvieron JSON en el primer intento, sin reintentos.

## Identidad de la corrida

- **SYSTEM** (§4, leído del handoff byte a byte): md5 `fb3e5a9e734ff730a3b5184d88e7f38a`.
- **USER** (§3, `a/user.json`): md5 `8875d342735eacb913132240e2436440`, 202759 caracteres. Las 4 corridas guardan ese mismo md5 en su raw.
- **Entrada:** `entrada_md5` `018f9cc1b939e2afdcfad5eb5ebcc36f`, menos `clima` y `caben`, más `humano_en_escena` repuesto desde `01a_escaleta.json` por `n` (13/13, §2 v3).
- **Brazos:** O = `claude-opus-5-5`, F = `claude-fable-5-1`, esfuerzo medium, `hx.MAX_TOKENS`, streaming, 4 a la vez con `ThreadPoolExecutor`. Pared 222,3 s.
- **Métricas (Etapa 1):** coinciden con la referencia del §6.1 sin diferencias (`a/metricas.md`). La referencia no va al USER.

## Validación (`a/validacion.md`)

| brazo | nota_total | notas por cap | n deberia | ids inválidos | oraciones inválidas | palabras antes→después | cifras sin respaldo | US$ | s |
|---|---|---|---|---|---|---|---|---|---|
| O_1 | 6.5 | ch01: 7.5 · ch02: 7.0 · ch03: 5.0 · ch04: 8.5 · ch05: 8.0 · ch06: 6.0 · ch07: 6.5 | 10 | — | — | ch01 43→65 · ch03 50→36 · ch03 161→133 · ch03 105→83 · ch04 26→42 · ch05 112→77 · ch06 62→79 · ch06 88→84 · ch07 79→47 · ch07 9→16 | — | 0.8285 | 221.0 |
| O_2 | 6.4 | ch01: 8.0 · ch02: 7.5 · ch03: 5.0 · ch04: 8.5 · ch05: 8.0 · ch06: 6.0 · ch07: 6.5 | 8 | — | — | ch01 43→71 · ch02 14→23 · ch03 338→171 · ch05 35→123 · ch06 74→102 · ch06 166→160 · ch07 79→72 · ch07 35→74 | #1 1, #1 9 | 0.7253 | 168.2 |
| F_1 | 6.0 | ch01: 8.0 · ch02: 7.0 · ch03: 4.5 · ch04: 8.5 · ch05: 7.0 · ch06: 6.0 · ch07: 7.5 | 7 | — | — | ch01 69→65 · ch02 62→48 · ch03 523→381 · ch05 114→89 · ch06 47→45 · ch06 156→128 · ch07 79→61 | #3 1949 | 1.7682 | 218.4 |
| F_2 | 6.0 | ch01: 8.5 · ch02: 7.5 · ch03: 5.0 · ch04: 8.5 · ch05: 8.0 · ch06: 6.5 · ch07: 7.0 | 5 | — | — | ch02 62→47 · ch03 338→257 · ch05 122→86 · ch06 156→179 · ch07 114→166 | — | 1.6991 | 202.8 |

## Varianza (`a/varianza.json`)

| brazo | Δ nota_total | Jaccard de `(cap, idx)` | oraciones marcadas por corrida | intersección |
|---|---|---|---|---|
| O | 0.1 | 0.581 | 48 y 50 | 36 |
| F | 0.0 | 0.623 | 64 y 48 | 43 |

Intersección completa:

- **O:** ch01:1, ch01:9, ch03:12, ch03:13, ch03:14, ch03:15, ch03:16, ch03:17, ch03:18, ch03:19, ch03:20, ch03:21, ch03:22, ch03:23, ch03:24, ch03:25, ch03:26, ch03:27, ch03:28, ch05:4, ch05:7, ch06:0, ch06:1, ch06:2, ch06:3, ch06:4, ch06:10, ch06:11, ch06:12, ch06:13, ch06:14, ch07:5, ch07:6, ch07:7, ch07:8, ch07:13
- **F:** ch02:7, ch02:8, ch03:11, ch03:12, ch03:13, ch03:14, ch03:15, ch03:16, ch03:17, ch03:18, ch03:19, ch03:20, ch03:21, ch03:22, ch03:23, ch03:24, ch03:25, ch03:26, ch03:27, ch03:28, ch03:29, ch03:30, ch05:4, ch05:5, ch05:6, ch05:7, ch05:8, ch05:9, ch05:10, ch06:10, ch06:11, ch06:12, ch06:13, ch06:14, ch06:15, ch06:16, ch06:17, ch06:18, ch06:19, ch07:5, ch07:6, ch07:7, ch07:8

## Costo

| corrida | modelo | in | out | de out, razonamiento | US$ | s |
|---|---|---|---|---|---|---|
| O_1 | claude-opus-5-5 | 89925 | 23441 | 14872 | 0.8285 | 221.0 |
| O_2 | claude-opus-5-5 | 89925 | 18282 | 10100 | 0.7253 | 168.2 |
| F_1 | claude-fable-5-1 | 89925 | 17378 | 8995 | 1.7682 | 218.4 |
| F_2 | claude-fable-5-1 | 89925 | 15998 | 7946 | 1.6991 | 202.8 |
| **total** | | | | | **5.0212** | |

El §1 esperaba ≈ US$ 3,4 y se informaba sin tope: costó 48 % más. El USER midió lo previsto; la diferencia está en la salida, que incluye 8–15 mil tokens de razonamiento. Costo por corrida: O 0,73–0,83 (esperado 0,5), F 1,70–1,77 (esperado 1,2). `hx._track` se llamó como en F63, sin `start_video`: `data/cost_history.json` no cambió.

## Producción intacta

Snapshot de mtimes (ns) de los 77 archivos de `data/scripts/_steps/<tid>/` y de `data/cost_history.json`, justo antes y justo después de las llamadas: **idénticos**.

- `a/mtimes_antes.json`: md5 del archivo `01c9f662c8456d63694ef4a8fffaf618`.
- `a/mtimes_despues.json`: md5 del archivo `01c9f662c8456d63694ef4a8fffaf618`.
- Último mtime dentro de `_steps/<tid>/`: `01_v3_costos.json`. Las listas completas están en esos dos JSON.

La Etapa 1 solo lee de `_steps` y corrió antes del primer snapshot. `data/cost_history.json` sigue en 17:31, anterior a este lab.

## Salidas

En `lab/hyperframes/f67/a/`: `user.json`, `md5.json`, `metricas.md`, `{O_1,O_2,F_1,F_2}.raw.json`, `{…}.md`, `validacion.md`, `varianza.json`, `llamadas.log`, `run.log`, `ciego/critica_01..04.md`, `clave_ciego.json`. La clave no se transcribe en este reporte.

## Lo que queda abierto

1. **Decisión de Omar:** el analista lee los 4 ciegos y Omar decide si el crítico entra a la compuerta F67. La escala de nota 1–10 también espera su confirmación (§1).
2. **O_1 devolvió 10 DEBERÍA; el máximo del §5 es 8.** El §5 lo declara límite del handoff y no instrucción, así que la validación no lo trunca. Se ve en la columna `n deberia`. Si el crítico entra a producción, hay que decidir si el tope se le pide al modelo o lo aplica el código.
3. **Falso positivo de `cifras sin respaldo` en O_2 #1:** «1» y «9» son las marcas `[idx1]` e `[idx9]` que el modelo escribió dentro de `deberia_texto`. Esas marcas y el `[…]` también cuentan como palabras en ese `43→71`. No se corrigió: el handoff fija el tokenizador y la regex.
4. **Falso positivo de `cifras sin respaldo` en F_1 #3:** «1949» está respaldado. Ese DEBERÍA cita Q53, cuyo campo `fecha` es 1949, pero el §6.3 solo permite números de `texto` y `contexto_fuente`, no de `fecha`. Si el validador pasa a producción, conviene sumar `fecha`. Con esto y el abierto 3, las 3 cifras marcadas en la tabla son falsos positivos: esta medición no encontró cifras inventadas (no detecta números en palabras ni romanos, §6.3).
5. **Pico:** las 4 corridas lo ubican en ch05 y dan 72, 70, 70 y 70 %. Ninguna da 74 (acumulado al final de ch05, la cifra del §8) ni 60. Dan 174–194 s después, contra 174 s medidos desde el final de ch05. Parece una ubicación dentro del capítulo, entre 59 y 74 %, y O_2 lo escribe como «entre el 67% y el 74%». El código no calculó la posición de la oración del pico: si 70 es correcto o estimado lo juzga el analista.
6. **El Jaccard mide oraciones marcadas, no ideas.** Los DEBERÍA de bloque pesan mucho (F_1 #3 marca las 32 oraciones de ch03, 523→381). Dos corridas pueden coincidir en ch03 y proponer cosas distintas.
7. **Ciego:** la palabra «tokens» aparece en `critica_01`, `02` y `03`, dentro de textos `medible_como` escritos por los modelos: no es metadato. La grep de `opus`, `fable`, `claude`, `sonnet`, `US$` y `O_1`… no da más coincidencias. Limitación del §7: con 2 corridas por brazo se puede emparejar por estilo. `clave_ciego.json` y los `{O,F}_N.md` están en la misma carpeta `a/`: quien lea a ciegas debe abrir solo `ciego/`, y esta tabla de validación ya muestra notas por brazo.
8. **Decisiones de CC, ninguna agrega una constante:** (a) validación y markdown corrieron en código, sin subagentes: tardan menos de 1 s y son deterministas. (b) El primer `a/user.json` quedó con `\r\n` de Windows (md5 de archivo `4ff268d9…`), aunque lo enviado llevaba `\n` (`8875d342…`). Se reescribió con `\n` y se comprobó que el md5 del archivo es el enviado. (c) Se agregó `--desde-raw` para rehacer las etapas 3–5 sin llamadas, y se usó una vez para redondear la Δ de nota (0,09999… → 0,1). Mismos raw, mismo orden del ciego.
9. **PARADA:** voz y fotos de Wittenoom siguen sin correr. El papel sigue sin aprobar y la compuerta de narración F67 espera este resultado.

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Recalculé todo desde los raw y los archivos de `_steps` con un script mío (`-I`, sin `claude_helpers`, sin API, sin pytest). Un solo punto del reporte es falso: la afirmación sobre el «1949» de F_1 #3 (fila 11).

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Md5 del handoff d68e9c17… | OK | `md5sum` del handoff coincide. |
| 2 | SYSTEM y FORMATO_SALIDA = §4/§5 byte a byte; md5 del SYSTEM | OK | Los extraje del handoff: md5 SYSTEM `fb3e5a9e…`, igual al de `md5.json` y al `system_md5` de los 4 raw. El final de `user.json` es exactamente el FORMATO del §5. |
| 3 | USER según §3 | OK | `a/user.json` md5 `8875d342…`, 202.759 caracteres, sin `\r\n`. Orden de claves correcto. Sin `clima` ni `caben`. `humano_en_escena` 13/13 emparejado por `n` con `01a_escaleta.json`. `caps`, `beats`, `escaleta_video`, `archivo` y `disputas` son iguales a los de la entrada. `verificacion` es igual a la tabla de `01b_verificacion.md`. |
| 4 | Métricas y referencia §6.1 | OK | `metricas.md` coincide con la referencia en las 7 filas y el total (1941 palabras, 11,0 min). `entrada_md5` es `018f9cc1…`. |
| 5 | Validación por fila (ids, `(cap, idx)`, palabras antes→después, cifras) | OK | Recalculé las 30 filas de `deberia` y las 4 filas de notas: todo coincide con `validacion.md`. Ids y oraciones inválidos: ninguno. Cifras sin respaldo: O_2 #1 `1` y `9`, F_1 #3 `1949`. |
| 6 | Costos contra PRICES × usage | OK | Recalculados: O_1 0,8285, O_2 0,7253, F_1 1,7682, F_2 1,6991, total 5,0212. Los tokens de razonamiento (14872, 10100, 8995, 7946) coinciden con los raw. Las 4 corridas tuvieron 1 intento. Usan `hx._track` como F63 y `cost_history.json` quedó en 17:31. |
| 7 | Ciego | OK | `Random(67).shuffle` da F_1, O_2, F_2, O_1, igual que `clave_ciego.json`. Hay grep limpio de opus, fable, claude, sonnet, US$, O_N, medium e intento. Los 4 usan la misma plantilla. La palabra «tokens» aparece en 01, 02 y 03, dentro de `medible_como` escrito por el modelo, como dice el reporte. `critica_01…04` aparecen en el reporte solo como rango de archivos y como identificadores de los casos de «tokens»; el reporte no los asocia a ninguna corrida. |
| 8 | Varianza §6.5 | OK | O: Δ 0,1, Jaccard 0,581, 48/50 marcadas, intersección 36. F: Δ 0,0, Jaccard 0,623, 64/48, intersección 43. Coincide con `varianza.json` y con el reporte. |
| 9 | mtimes antes = después | OK | `mtimes_antes.json` y `mtimes_despues.json` son iguales: 77 archivos de `_steps` más `cost_history.json`. El último mtime es `01_v3_costos.json`. |
| 10 | Afirmaciones de los abiertos | OK | Verifiqué: O_1 con 10 DEBERÍA; O_2 #1 con `[idx1]`, `[idx9]` y `[…]` dentro del texto; picos 72/70/70/70 en ch05; segundos después 184/174/190/194; F_1 #3 marca las 32 oraciones de ch03 (523→381); ch06+ch07 = 174 s; O_2 escribe «entre el 67% y el 74%». |
| 11 | Abierto 4: «1949 está en D144, T22, T23, P28 pero en ningún id que ese DEBERÍA cite» | FALLA | F_1 #3 sí cita **Q53**, cuyo campo `fecha` es 1949. Otros ids con 1949 que el reporte no menciona: Q53. El validador solo mira `texto` y `contexto_fuente` (§6.3), por eso lo marcó. La conclusión «dato con el respaldo mal citado» es incorrecta: el respaldo está citado. |
| 12 | md5 de mtimes `3254bc6c…` (reporte líneas 50-51) | NO VERIFICABLE | No lo reproduje con 6 serializaciones distintas. Falta saber cómo se calculó. Sí verifiqué la igualdad real de los dos archivos (fila 9). |
| 13 | Reporte: validación, varianza, costo, md5 de SYSTEM, USER y handoff, mtimes, abiertos, veredicto, sin clave | OK | Todos presentes. El veredicto figura como «(pendiente)», que es lo esperado. La clave no está en el reporte. |

Fuera de alcance: ninguno. Todo lo nuevo está bajo `lab/hyperframes/f67/`. Los `M` de `DECISIONES.md`, `diag_234_cap4.py` y `f28a.log` ya estaban en el snapshot inicial. No encontré cambios en `data/`.

Riesgos que el contrato no cubre:
- `clave_ciego.json` y los `{O,F}_N.md` están en la misma carpeta `a/`, y el commit de `lab/hyperframes/f67/` los publica juntos. Si el analista abre `a/` en vez de `a/ciego/`, el ciego se rompe.
- El allowlist de cifras ignora el campo `fecha` del archivo, así que cifras que sí tienen respaldo salen como «sin respaldo». El caso es F_1 #3 con «1949».

## Adenda de CC

El veredicto es sobre la versión anterior del reporte. Después de recibirlo, sin nueva revisión, corregí en este reporte solo sus filas 11 y 12:

- **Fila 11:** comprobé que F_1 #3 cita Q53 y que su `fecha` es 1949; reescribí el abierto 4. Mi versión decía que el respaldo estaba mal citado, y era falso.
- **Fila 12:** el md5 no era reproducible porque salía de una serialización mía. Ahora es el md5 de los dos archivos, reproducible con `md5sum`.
- **Riesgo de la carpeta `a/`:** no moví la clave ni los `{O,F}_N.md`, porque el §2 fija esas rutas. Queda avisado en el abierto 7. `validacion.md` y `allowlist` no cambiaron: el §6.3 define esa lista.
