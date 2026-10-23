# F11c — Prompt con la estructura oficial + Gemini 4 Argon vs GPT-6.1 Sol (Ycuá) — REPORTE → PARADA

CC · 2026-10-23 · rama `f11-guion-v4` (base `ae7b8dc`). Handoff: `HANDOFF_F11c_estructura_y_modelos.md`. Solo narración.

**En una línea:** con el prompt reestructurado, **Sol high cumple el criterio** (1,425 palabras, 0 bloqueantes, crudo = final porque el m01c ya no corre) y bajó de 20 a 6 preguntas. **Argon no cumple:** el crudo trae 1,220 palabras y 1 cita inventada; la ronda la saca, pero deja el cap 4 corto y el editor m01c lo recorta más, así que el final queda en 1,111 palabras con 1 bloqueante. Costo de la tanda: **US$ 0.196** de 1.50.

Para leer: `compara_f11c.html` (se lee en el teléfono), `NARRACION_ycua_v4c_argon.md` y `NARRACION_ycua_v4c_sol.md` (cada uno con el crudo y el final).

## 0. Qué se hizo

1. **Prompt v4 reestructurado** (`script_engine/guion_v4.py`, `PROMPT_VERSION = "f11c-1"`). Es el mismo para los dos modelos.
   - **Sistema:** `system()` = `<rol>` → `<voz>` → `<oficio>` (las 8 líneas del handoff) → `<ejemplos_de_voz>`. Va como `system_instruction` en Gemini y como mensaje `system` en GPT. Los dos ejemplos son párrafos enteros de `lab/hyperframes/f7/NARRACION_orleans_v3r3.md` (líneas 105 y 122), copiados literal; un test lo comprueba contra el archivo.
   - **Usuario:** `prompt()` = `<caso>` (tema, humano, promesa, pico, cierre humano) → `<escaleta>` → `<tarea>` al final. «queda abierta» pasó a «el espectador se pregunta:». Se sacó el separador «──» de los caps para que haya un solo formato de delimitadores (XML). Las marcas de los datos (VERIFICADA, SIN VERIFICAR (sin nombre), PANTALLA, CIFRA OFICIAL) y la excepción del humano quedan como estaban.
2. **Modelo propio del guionista:**
   - `gemini_helpers.call_model_json(model=)` y `make_call(model)`: igual que `call_pro_json`, pero con el modelo explícito. No pasan temperature, top_p, top_k ni thinking.
   - `guion_v4.call_for("gemini-4-argon")`: toda la cadena v4 (guionista, regeneración, edición de oración, editor) usa ese modelo.
   - `fase1_5 --guion v4 --modelo gemini-4-argon`.
   - No se tocaron `gemini_model_research` ni `config.py`; `call_pro_json` está igual.
   - Precio en `cost_tracker._DEFAULT_GEMINI_RATES_PER_1M`: US$ 2 / 10 por millón (oficial, vigente hasta el 30/11).
3. **Sin el editor m01c con 0 bloqueantes:** en `reparar`, si el crudo no trae bloqueantes se saltea la pasada del editor y queda en el log. Con bloqueantes, la ronda es la misma de F11b. No se agregó ninguna regla.
4. **Tests:**
   - `test_module_f11c.py` (8, sin red): la estructura y el orden del sistema; los ejemplos literales; el usuario con los datos primero y `</tarea>` al final; `write` manda el sistema y el usuario por separado; argon va al modelo del guion, sin temperature ni thinking, y `gemini_model_research` sigue con el suyo; el precio de argon; m01c se saltea con 0 bloqueantes; con bloqueantes, la ronda sigue igual.
   - Se adaptaron dos aserciones viejas que fijaban la estructura anterior: `test_module_f11.py` (el oficio ahora se busca en `system()`) y `test_module_f11b.py` (sin «──» y sin `endswith`).
   - **Suite amplia: 579 verdes + las 5 fallas previas** (3 `01b_pauses`, 2 `m03_merge_timing`). `test_v3_byte_identico` sigue verde.
5. **Humo de argon** (`f11c_humo.py` → `humo_argon.json`): la llave lo acepta. Respondió `{"texto": "hola"}` en 7.2 s y costó US$ 0.0006.
6. **Corridas** (`f11c_corridas.py`): Ycuá `f8s1-ycua-bolanos`, escaleta `01a_escaleta_v1.json` (md5 e1ba1a48…), sin notas.
   - El sistema y el usuario se guardaron una sola vez en `prompt_ycua_v4c_sistema.txt` (md5 `8edea05e…`) y `prompt_ycua_v4c_usuario.txt` (md5 `e7062b6c…`), con los md5 en `prompt_ycua_v4c.md5`. Esos md5 son del texto que se mandó (con saltos LF); en el disco, los .txt quedaron con CRLF porque Python escribe en modo texto en Windows, así que su md5 crudo es otro. Cada corrida verificó byte a byte que el guionista mandaba exactamente eso.
   - Salidas `_v4c_<argon|sol>` en `data/scripts/_steps/f8s1-ycua-bolanos/` y en esta carpeta. No se pisó nada anterior y no se escribió en `topics_db`.

## 1. Tabla resumen

Todo se re-midió con el código de hoy. El criterio: bloqueantes ≤ 2, 1,350–1,700 palabras y ningún cap vacío. «Preguntas» y «frases de analista» son métricas: no rechazan nada.

| versión | palabras | bloq. | duras v3 | cierre | preguntas | frases de analista | ids/párrafo (antes → después) | US$ | criterio |
|---|---|---|---|---|---|---|---|---|---|
| v3 (v1) | 1,235 | 3 | 23 | resumen | 1 | 0 | 1.54 → 0.96 | 0.88 | no |
| F11b sol (crudo) | 1,501 | 0 | 22 | cita | **20** | 0 | 4.42 → 1.17 | 0.076 | cumple |
| F11b astra (crudo) | 1,489 | 0 | 24 | cita | 14 | 1 («el testimonio») | 4.08 → 1.08 | 0.157 | cumple |
| **v4c argon (crudo)** | 1,220 | 1 | 32 | cita | 10 | 0 | 4.42 → 1.58 | 0.028 | no |
| **v4c argon (final)** | **1,111** | **1** | 31 | cita | 7 | 0 | 4.17 → 1.58 | 0.079 | **no** |
| **v4c sol (crudo)** | 1,425 | 0 | 17 | cita | 6 | 0 | 4.42 → 1.58 | 0.114 | cumple |
| **v4c sol (final)** | **1,425** | **0** | 17 | cita | **6** | 0 | 4.42 → 1.58 | 0.117 | **cumple** |

Palabras por cap (escrito / objetivo):

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| argon crudo | 95/110 | 203/250 | 204/250 | 195/250 | 212/250 | 206/250 | 105/140 |
| argon final | 95/110 | 203/250 | 204/250 | **115/250** | 198/250 | 191/250 | 105/140 |
| sol (crudo = final) | 102/110 | 236/250 | 233/250 | 238/250 | 241/250 | 243/250 | 132/140 |

Otras métricas:
- El humano (Liz Torres) aparece por nombre en los caps 1, 2, 6 y 7 con argon, y en los caps 1, 2, 5, 6 y 7 con Sol.
- Citas: 11 en el final de argon y 11 en Sol.
- Los dos cierran con una cita.

Así arranca cada crudo (beat 1):
- **argon:** «Cenizas calientes caen del cielorraso. Es una lluvia negra y espesa que quema la piel. Liz Torres mira hacia arriba, atrapada entre las góndolas. «El fuego avanzaba por el techo», recordó Liz Torres. El aire desaparece. Respirar duele. …»
- **sol:** «Cenizas calientes caen del cielorraso. Una lluvia negra y espesa. Era el lugar de encuentro del barrio. Hasta el domingo en que alguien ordenó cerrar las puertas. Liz Torres está dentro del Ycuá Bolaños. «El fuego avanzaba por el techo», recuerda Liz. …»

## 2. Tokens del prompt y costo por corrida

**Prompt** (el mismo para los dos modelos):
- Contado por `gemini-4-argon` con `count_tokens`, que no factura: sistema **506** tokens y usuario **3,214**.
- Facturado en la llamada del guionista: argon 3,917 de entrada y Sol 3,537 (cada tokenizador cuenta distinto; con F11b, el prompt de Ycuá era de ≈ 3.4 k tokens).

**Costo por corrida:**

| corrida | llamadas | entrada / salida / razonamiento (guionista) | US$ | segundos |
|---|---|---|---|---|
| humo argon | 1 | 204 / 22 / 0 | 0.0006 | 7 |
| argon | guionista 0.0279 · editar frase 0.0021 · editor m01c 0.0451 · títulos (Flash) 0.0036 | 3,917 / 2,011 / 0 | **0.0788** | 158 |
| sol | guionista 0.1140 · títulos (Flash) 0.0029 | 3,537 / 2,281 / 8,412 | **0.1169** | 268 |
| **tanda** | | | **0.196** (tope 1.50) | |

- Argon devolvió `thoughts_token_count` = 0 en todas las llamadas. El thinking quedó en su valor por defecto (no se pasó `thinking_config`); lo anoto porque es lo que informó la API.
- La partición no tuvo que acortar nada y el juez m05 no generó costo en ninguna de las dos corridas.

## 3. Ronda de reparación

- **Sol:** 0 bloqueantes en el crudo, así que **no corrió el editor m01c** («[editor v4] crudo con 0 bloqueantes: sin pasada del editor m01c»). Tampoco hubo fechas repetidas. El final es el crudo, palabra por palabra (1,425 = 1,425). Esto es lo que cambió respecto de F11b, donde el m01c le recortó 272 palabras.
- **Argon:** 1 bloqueante en el crudo.
  1. **(a) Cita inventada**, cap 4, beat 7: «"La gente corría y volvían todos porque el portón que queda hacia Avenida Artigas estaba cerrado, por donde yo entré", relató una sobreviviente.» Va entre comillas, pero no es una cita del pool.
  2. **Edición de la oración:** aceptada; sacó esa frase (23 palabras) y el resto del párrafo quedó igual. Con eso, el beat 7 pasó de 93 a 70 palabras y el cap 4, de 195 a **172** (medido con `mg.wc`), debajo del mínimo de 188, y pasó a tener **(c) cap 4 corto**.
  3. Regeneración: no corrió, porque los caps a regenerar se calculan con los bloqueantes del crudo, cuando el cap 4 todavía no era corto. Es el diseño de F11 y no lo cambié.
  4. Fechas: sin cambios.
  5. **Editor m01c** (corre porque el crudo tenía 1 bloqueante): editó los 12 párrafos. Aceptó 4 (beats 6, 7, 8 y 11) y rechazó 8: 7 porque subían los bloqueantes de 1 a 2, y 1 por la guardia léxica («ante»). Como el cap 4 ya contaba como un bloqueante (c), el editor podía seguir recortándolo sin que subiera el conteo. Los beats 6 y 7 pasaron de 102 a 67 y de 69 a 48 palabras, y **el cap 4 terminó en 115/250**.
  6. Resultado: 1 → 1 bloqueante; 1,220 → 1,111 palabras.
- **Lectura (sin cambios en el código):** la aceptación del editor solo mira la cantidad de bloqueantes. Si un cap ya es corto, puede recortarlo más sin que suba el conteo. En F11b pasaba lo mismo con el total. Deciden Omar y el analista.

## 4. Aparte: Paiva hijo (no se tocó nada)

El pool de Ycuá trae **dos nombres para el hijo condenado**. Solo F05 dice «Emiliano»; las otras cinco fuentes dicen «Víctor (Daniel) Paiva». Además, el dato D20 junta las dos versiones bajo el nombre «Emiliano».

**«Emiliano Paiva»:** solo F05 (ABC Color, 2024, «A 20 años del Ycuá Bolaños…», https://www.abc.com.py/nacionales/2024/07/28/a-20-anos-del-ycua-bolanos-familiares-y-sobrevivientes-claman-por-justicia-y-memoria/).
- **D20** «Emiliano Paiva, hijo del dueño, fue condenado a 10 años de prisión»: doc_id F05, offset 2282. «…y su hijo, Emiliano Paiva, a 10 años de prisión y quien murió en libertad en el 2020, a raíz de complicaciones por el Covid.»
- **T70**: F05, offset 2293, el mismo pasaje.
- **P07** «Emiliano Paiva, hijo del propietario»: F05, offset 1484. «…Juan Pío Paiva (propietario del local) o de su hijo, Emiliano Paiva, ambos condenados por la tragedia.» (P06 trae el mismo pasaje en F05, offset 1472.)
- Ojo: la evidencia de **D20** también lista F10:3282 y F15:1218, pero esos dos pasajes dicen **«Víctor Paiva»**.

**«Víctor Daniel Paiva» / «Víctor Paiva»** (P28 «gerente de salón del supermercado e hijo de Juan Pío Paiva»):
- **D66, acusación:** F09 (Karin Becker, *La tragedia del Ycuá Bolaños*, libro, 2006), offset 17775. «presentamos una formal acusación contra los señores Juan Pío Paiva y Víctor Daniel Paiva, contra el guardia privado Areco…» D65 y T40 traen el mismo pasaje en F09, offset 17691.
- **D215, causa principal:** F15 (ABC Color, 2011, «Caso Ycuá Bolaños: Concluye proceso penal con tres sentencias condenatorias»), offset 524. «…fueron enjuiciados el principal accionista, Juan Pío Paiva; su hijo Víctor Daniel Paiva y el guardia de seguridad Daniel Areco.»
- **Condena a 10 años:**
  - F15, offset 1218: «…la condena de Juan Pío Paiva, Víctor Paiva y Areco, con 12, 10 y 5 años de prisión, respectivamente.»
  - F10 (Última Hora, 2025, «A 21 años, la Corte dice que Paiva debe pagar G. 4.500 millones»), offset 3282: «…a su hijo Víctor Paiva, a 10 años…»
- **F16** (Última Hora, 2014, «La tragedia que marcó la sociedad»):
  - offset 2383: «su hijo Víctor Paiva también fue a prisión»;
  - offset 2434 (T63): «…aunque en agosto del 2007 consiguió la libertad con restricciones».
- **D222, demanda civil:** F15, offset 2772 (T67 trae el mismo pasaje en F15, offset 2762). «…condenó … al empresario Juan Pío Paiva, su hijo Víctor Daniel Paiva y la sociedad Ycuá Bolaños a pagar más de G. 400 millones».

Para decidir antes de producir: ¿«Emiliano» es un error de F05, o es otro hijo? Ninguna otra fuente lo nombra. Además, la muerte en 2020 por Covid (T70) sale solo de F05. **Esto afecta a los dos textos de F11c:** las narraciones de argon y de Sol dicen «Emiliano Paiva» en el cap 6 (beat de la sentencia).

## 5. Lo que no se hizo / frenos

- Ninguna regla nueva: las dos columnas nuevas son conteos que no rechazan nada.
- No se tocaron `gemini_model_research`, `config.py` ni los archivos prohibidos.
- No se corrió `f10_quirurgico_ycua.py`. Sin merge. No se avanzó a producción.
- `.env` y `lab/_gpt_probe_analista/` no se commitean; la fila «GPT Sol medio (prueba del analista)» de F11b no está en la tabla porque el handoff no la pide.
- Un detalle del crudo de argon: «…ahumado por el hollín.Las puertas…» (falta un espacio después del punto, beat 7). Está en el texto tal como lo devolvió el modelo.

## 6. Veredicto del revisor-handoff (íntegro)

Después del veredicto, CC hizo cuatro cosas: actualizó `lab/ESTADO_SESION.md` (#17), midió el cap 4 (172 palabras, ya no ≈ 173), agregó el prefijo `data/scripts/` a la ruta de `_steps`, y sumó dos notas: el CRLF de los .txt (#10) y que las dos narraciones usan «Emiliano Paiva».

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Sistema = rol, voz, oficio (8 líneas) y ejemplos, en XML; usuario con los datos primero y `<tarea>` al final; "queda abierta" pasó a "el espectador se pregunta" | OK | guion_v4.py `system()` y `prompt()`; diff leído |
| 2 | Ejemplos copiados literal de f7/NARRACION_orleans_v3r3.md | OK | Líneas 105 y 122 del archivo, comparadas contra `EJEMPLOS_VOZ`: idénticas |
| 3 | `PROMPT_VERSION = "f11c-1"` | OK | guion_v4.py |
| 4 | Modelo propio `gemini-4-argon` solo para el guion v4; sin temperature/top_p/top_k; thinking por defecto | OK | `call_model_json`/`make_call` en gemini_helpers.py, `call_for`, `--modelo` en fase1_5.py. `call_pro_json` intacto (el diff solo agrega funciones). |
| 5 | `gemini_model_research` y config.py sin tocar | OK | `git diff -- config.py` vacío; no está en `git status` |
| 6 | Precio de argon US$ 2 / 10 por millón | OK | cost_tracker.py, +2 líneas |
| 7 | m01c se saltea con 0 bloqueantes; con bloqueantes la ronda sigue igual | OK | `reparar`: `if bl0: editor_pass(...) else: log`. El log de Sol lo confirma; el de argon muestra que el editor corrió. |
| 8 | Cero reglas nuevas | OK | El diff no agrega ninguna regex, lista ni rechazo. Las dos columnas nuevas solo cuentan. |
| 9 | Humo de argon antes de las corridas | OK | humo_argon.json: ok=true, US$ 0.00063 |
| 10 | Mismo prompt exacto para las dos corridas, guardado una vez con md5 | OK, con una nota | md5 8edea05e… y e7062b6c… coinciden con `system()` y con los archivos solo tras normalizar CRLF a LF. Los .txt están en disco con CRLF (md5 crudo ffca4ffa/6d51d8e2). Es de forma, no de fondo. |
| 11 | Tope US$ 1.50 | OK | costos_f11c.json: humo 0.0006 + argon 0.0788 + sol 0.1169 = 0.1963, igual que corridas.out |
| 12 | Tabla del reporte (palabras, bloqueantes, duras, preguntas, ids, citas, humano, palabras por cap, costos, tokens 3,917/3,537) | OK | Coincide con resumen_f11c.json en todas las filas. Los 4 caps del reporte de argon (final 4: 115/250) también coinciden. |
| 13 | Secuencia de la ronda de argon | OK | resumen_f11c.json: edición del beat 7 aceptada; sin regeneración; editor con 4 aceptados (6, 7, 8, 11) y 8 rechazados (7 por 1→2, 1 por «ante»); bloqueantes 1→1; palabras 1220→1111 |
| 14 | Sección Paiva (doc_id y offset) | OK | Contrasté contra data/topics_db.json: D20 F05:2282, T70 F05:2293, P07 F05:1484, P06 F05:1472, D66 F09:17775, D65/T40 F09:17691, D215 F15:524, D222 F15:2772, T63 F16:2434. Todo coincide. |
| 15 | Tests | OK | Corrí f11, f11b y f11c: 33 pasan, sin red. Las 579 verdes y las 5 fallas previas no las re-corrí (las tomo de tus datos). |
| 16 | Salidas sin pisar nada ni tocar topics_db; v3 byte-idéntico | OK | Los `_v4c_*` están en data/scripts/_steps/f8s1-ycua-bolanos/ (el reporte dice `_steps/…` sin el prefijo `data/scripts/`). `git status` no marca topics_db.json ni data/topics_db.json. Las dos aserciones adaptadas son solo la estructura vieja del prompt. |
| 17 | Actualizar lab/ESTADO_SESION.md | FALLA | El archivo no aparece modificado en `git status`, y `grep F11c` en él no da nada. El handoff §3 y el CLAUDE.md lo exigen. |
| 18 | §5 del reporte: sin merge, sin `.env`, sin `f10_quirurgico` | NO VERIFICABLE | Nada commiteado todavía; lo afirmado es plausible, pero un commit futuro no se puede revisar desde acá. |

Observaciones:
- Falla #17 (ESTADO_SESION sin actualizar) es el único punto que bloquea.
- El reporte dice "cap 4 ≈173 palabras" tras la edición de la oración. Es una estimación; no está medida en ningún archivo. Es menor.
- La sección Paiva sí advierte que D20 mezcla "Emiliano" (F05) con F10/F15, que dicen "Víctor". Dato para Omar: la narración final de Sol usa «Emiliano Paiva» (NARRACION_ycua_v4c_sol.md, líneas 59 y 125), así que la decisión sobre el nombre afecta ese texto.

Fuera de alcance: ninguno propio de F11c. Hay archivos modificados ajenos (diag_234_cap4.py, gfx_profiles/*), que me pediste ignorar. Hay `__pycache__` suelto dentro de lab/hyperframes/f11c/ (no commitear).

Riesgos que el contrato no cubre:
- El editor m01c acepta por conteo de bloqueantes. Si un cap ya es corto, lo puede recortar más sin que suba el conteo; así pasó con argon (cap 4: 195→115). El reporte lo declara y lo deja a decisión de Omar.
- Argon devolvió thinking=0 en todas las llamadas; la comparación con Sol (8,412 tokens de razonamiento) no es de igual a igual.
