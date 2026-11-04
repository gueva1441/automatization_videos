# F75: personaje medido por la narración · segundos entre promesas nuevas · master −14 LUFS (PARADA)
2026-11-04 · rama f11-guion-v4 · base 63ff8af · handoff `HANDOFF_F75.md`, md5 `fecdcf5ba8645c48b889f22f0a6b6bf7` (verificado antes de arrancar)

## En corto
- **A**: hecho. Wittenoom coincide con el contrato A2 en los 4 candidatos y en las 7 filas de rachas. Gana Daniel (P17), con 16 oraciones.
- **B**: hecho. Wittenoom coincide con el contrato B2 en los 7 tramos, el máximo (182 s, de ch04:18 a ch06:20) y la línea ⚠.
- **C0**: hecho. Hay un lugar común a los 3 caminos: `fase2b.py:3656/3657`.
- **C1**: hecho. **No cumple el techo de pico real.** El master llega a −14,0 LUFS, pero el pico real sobre el AAC queda en **−0,9 dBTP**, por encima del techo de −1,5.
- **C2: NO se cableó.** No voy a cablear un master que no cumple el techo del proyecto. Arreglarlo pide un número o un diseño que no está en la tabla §1. Lo explico en la etapa C.
- Gasto: US$ 0, ninguna llamada a API.
- No escribí nada en `output/`. El mp4 publicado de Wittenoom sigue con md5 `1fb47948e43951d4c009e13c0131d184`, el mismo de antes y de después.
- `data/…/01f_critico.md` no se pisó.
- Hubo 3 subagentes en paralelo: A, B (con A3 y QA) y C0+C1.

## Etapa A: el personaje sale de la narración

### Cambios
**`script_engine/m05_narrative.py`**
- Se borró `_persona_de(skeleton, escaleta)`, sin dejarlo apagado por flag.
- Funciones nuevas:
  - `terminos_retencion(persona, people)`. Toma los términos de `nombres.terminos` que tienen nombre y apellido. Suma el nombre de pila solo si nadie más del pool lo comparte. El apellido solo nunca entra. `nombres.py` no cambió.
  - `_nombra_ret`. El nombre de pila cuenta solo si alguna palabra del texto original empieza con mayúscula y su versión normalizada coincide.
  - `elegir_personaje`:
    - Gana quien sale en más oraciones.
    - Si hay empate, gana `escaleta.humano.id` cuando está entre los empatados; si no, el que aparece primero.
    - Si no aparece nadie, devuelve null con el motivo «nadie del pool se nombra en la voz».
- `retencion()`:
  - Ya no usa `skeleton.personajes`; el skeleton queda solo para los títulos.
  - Las rachas y `oraciones_con_personaje` se cuentan con los mismos términos.
  - `personaje` suma `elegido_por: "narracion"`, `oraciones` y `escaleta_id`.
  - La firma no cambió.

**`tests/test_m05_retencion.py`**
- Se sacó el parametrize viejo (skeleton / institución / sin humano).
- Tests nuevos:
  - nadie nombrado → null;
  - empate → escaleta;
  - empate sin escaleta → el primero;
  - nombre de pila compartido no cuenta;
  - «el inspector» con minúscula no cuenta;
  - apellido solo no cuenta;
  - no usa `skeleton.personajes`.
- Se agregó la igualdad exacta del dict `personaje` con los campos nuevos.

**A3: `SYSTEM.txt`, punto 2**
- Una sola sustitución, con el texto exacto del handoff. Un test comprueba que el SYSTEM nuevo es el de F67a §4 con ese reemplazo y nada más.
- `PROMPT_VERSION = "m01f-2"`.
- El candado ahora es `lab/hyperframes/f75/a/md5.json` (system `5fa554cf…`) más `SYSTEM_m01f-2.txt`.
- La línea del crítico pasó a «Personaje según la narración: … · N oraciones». El test de `tests/test_m01f_compuerta.py:152` está al día.

### Salida de A
`retencion()` corrido directo sobre los archivos del disco, sin LLM. Script: `lab/hyperframes/f75/a/a2_retencion_wittenoom.py`.

```
retencion.personaje = {"id": "P17", "nombre": "Daniel Écija (padre)", "terminos": ["daniel ecija", "daniel"], "elegido_por": "narracion", "oraciones": 16, "escaleta_id": "P16"}
  P17 Daniel Écija (padre): 16   P16 María Bernal: 7   P20 Ramón de Juan: 3   P21 Víctor Calvo: 3
  (fuera de la tabla, todos < 3: P19 2, P13 2, P25 1, P07 1, P23 1, P08 1, P22 1, P24 1)
```

| cap | oraciones/con/racha | contrato A2 | |
|---|---|---|---|
| ch01 | 14/1/7 | 14/1/7 | OK |
| ch02 | 18/1/16 | 18/1/16 | OK |
| ch03 | 25/3/10 | 25/3/10 | OK |
| ch04 | 19/2/12 | 19/2/12 | OK |
| ch05 | 23/6/8 | 23/6/8 | OK |
| ch06 | 25/2/12 | 25/2/12 | OK |
| ch07 | 15/1/10 | 15/1/10 | OK |

**Coincide con el contrato.**

**Lectura del archivo de entrada.** El handoff nombra `01b_narration_normalized.json`, pero ese archivo no trae párrafos con `cap`/`beat`/`texto`. `retencion()` recibe párrafos, y `judge_narration` los lee de `01b_narracion_v3.json` → `parrafos`. Ese archivo da las 139 oraciones del contrato (14/18/25/19/23/25/15). El pool es `01_facts_sources.json` → `evidence_pool`, con los mismos 35 personajes que `00_pool_v3.json`. seg = 0,34, de `06_judge_narrative.json`.

## Etapa B: segundos entre promesas nuevas

### Cambios
**`script_engine/m01f_critico.py`**
- `entre_promesas(loops, caps, seg, *, narracion_md5, narracion_md5_critico)`:
  - Usa la posición de `entrada.caps`.
  - El segundo de cada promesa sale de las palabras anteriores × `seg`. Cada tramo se redondea.
  - Dos loops que abren en la misma oración cuentan como una sola apertura.
  - Devuelve los tramos con `desde`/`hasta` (`"fin"` en el último), `max_segundos` y `max_tramo`.
  - Los `abre` que no existen van a `loops_invalidos`.
- `generar()` lo guarda en `validacion.entre_promesas` con `seg = metricas["seg_por_palabra"]`. Nunca llama a `velocidad()`; un test lo comprueba con un monkeypatch que explota si se llama.
- `critica_md(resp, val, metricas, cab)` ahora es pura y agrega la sección «## Promesas nuevas (código)».
- `rerender(...)` re-arma el `.md` desde el JSON, sin API.

**QA**
- `qa_studio_server.py`: `critico.entre_promesas` en `narracion_vista`.
- `qa_studio.html`: «Personaje según la narración · N oraciones», más una línea `nnEntrePromesas` junto a «loops» con los tramos, el máximo, los inválidos y «⚠ de otra narración».

**Tests**
- `tests/test_m01f_entre_promesas.py` y `tests/test_qa_entre_promesas.py`, ambos nuevos.

### Salida de B
Sección del `.md` de Wittenoom, re-armado desde el `01f_critico.json` existente en `lab/hyperframes/f75/b/01f_critico.md`. Script: `lab/hyperframes/f75/b/rerender_wittenoom.py`. Lo corrí de nuevo después de juntar A y B, y la línea de personaje dice «P17 Daniel Écija (padre) · 16 oraciones».
```
## Promesas nuevas (código)

⚠ calculado sobre la narración actual, no la que vio el crítico (actual `cd0fe3bfcc81bf45871f575c3c0077dc`, crítico `3fc4168d8fc270ba0af8122d8c3799d7`)

| desde | hasta | s |
|---|---|---|
| ch01:2 | ch01:5 | 21 |
| ch01:5 | ch01:11 | 24 |
| ch01:11 | ch01:12 | 2 |
| ch01:12 | ch03:11 | 139 |
| ch03:11 | ch04:18 | 150 |
| ch04:18 | ch06:20 | **182 (máx.)** |
| ch06:20 | fin | 81 |

Segundos estimados por palabra (0.34 s/palabra, sin pausas ni title cards); sin umbral.
```
**Coincide con el contrato B2:** los 7 tramos, el máximo y la línea ⚠.

Otras diferencias en ese `.md`, ninguna de código:
- La cabecera dice `m01f-1`, porque es la versión con la que corrió aquella crítica.
- La tabla de métricas cambia en ch03 (393 → 384 palabras) y ch05 (257 → 267), porque la narración actual es `cd0fe3bf…`.

## Etapa C: master −14 LUFS / −1,5 dBTP

### C0, solo lectura
- Los 3 caminos están en las líneas que dice el handoff:
  - (a) `_mix_music_audio_only` (:2127): AAC 192k en :2169-2171 y remux `-c copy` en :2177-2179.
  - (b) `_mix_music_into_video` (:1946): re-encode en :2039-2042 y :2081-2084.
  - (c) sin `music_map` (:3537): el audio queda como lo dejó `_concat_segments` (:3529).
- Los tres convergen con `final_path` justo antes de `fase2b.py:3657` (`final_dur = _get_duration(final_path)`).
- Todos los `return` anteriores devuelven `None`. El único final sale en :3679.
- Nada posterior re-escribe el audio:
  - `main` solo llama a `mark_as_generated`, que solo escribe en la DB;
  - `fase3` solo resuelve la ruta;
  - m09 no llama a ffmpeg.
- **Lugar común: SÍ.**
- Quedan sin master, a −24 LUFS, y no se publican:
  - el respaldo sin música, que con gfx se llama `{id}_final_gfx_no_music.mp4` (:3543-3546), no `_final_no_music.mp4` como dice el handoff;
  - `mezcla_preview.wav`.

### C1, lab sin render
Script: `lab/hyperframes/f75/c/f75c1_master_lab.py`. Log: `f75c1.log`. JSON: `loudnorm_pass1.json` y `loudnorm_pass2.json`.
- G = −14 − (−24,0) = +10,0 dB.
- Con ffmpeg 8.1, `alimiter limit` es amplitud lineal: 10^(−2/20) = 0,794328.
- 1.ª pasada: `volume=+10.0dB,alimiter=level=disabled:limit=0.794328,loudnorm=print_format=json`. Dio `input_i −14.50`, `input_tp −2.00`, `input_lra 5.90`, `thresh −24.75`, `offset 0.15`.
- 2.ª pasada: `…,loudnorm=I=-14:TP=-1.5:LRA=5.90:linear=true:measured_I=-14.50:measured_TP=-2.00:measured_LRA=5.90:measured_thresh=-24.75:offset=0.15`, con `-ar 48000 -c:a aac -b:a 192k`. Dio **`normalization_type: "linear"`**.

| | I (LUFS) | LRA (LU) | pico real (dBTP) | modo |
|---|---|---|---|---|
| antes: mp4 publicado | −24,0 | 6,6 | −6,6 | — |
| después: master AAC (48 kHz, 192k) | −14,0 | 5,9 | **−0,9** ✗ (techo −1,5) | linear |

**De dónde sale el −0,9.** Medido etapa por etapa con `ebur128 peak=true`:

| etapa | I | pico de muestra | pico real |
|---|---|---|---|
| solo volume | −14,0 | +3,4 | +3,4 |
| + alimiter | −14,5 | −2,0 | −1,4 |
| master antes del AAC (wav 48 kHz) | −14,0 | −0,9 | −0,9 |
| master AAC | −14,0 | −0,9 | −0,9 |

1. El limitador frena los picos de muestra, no los picos reales: deja +0,6 dB entre muestras.
2. Limitar baja la sonoridad 0,5 LU (queda en −14,5), y el loudnorm lineal la sube +0,5 dB.
3. loudnorm toma como `input_tp` el pico de muestra (−2,00), no el pico real (−1,4). Por eso su chequeo lineal pasa y su JSON dice `output_tp −1.50`, cuando lo real es −0,9.
4. El AAC casi no agrega nada.

El supuesto del handoff, que el margen de −2 dBFS cubre el AAC, no se cumple: ese margen se lo comen la subida y los picos entre muestras.

**Por qué no hay C2.** Los arreglos posibles necesitan algo que no está en la tabla §1:
- sobremuestrear antes del limitador para que limite el pico real (el factor sería un número nuevo);
- descontar en G la pérdida del limitador (cambia la receta de G);
- dejar que loudnorm vaya dinámico con su propio limitador (cambia el modo; en dinámico sube a 192 kHz).

Decide el analista con Omar.

**Los 4 extractos** (60 s, wav 16 bit). El minuto más fuerte sale de la ventana móvil de 60 s sobre la sonoridad momentánea de `ebur128`: 644–704 s.

| archivo | I | LRA | pico real |
|---|---|---|---|
| `lab/hyperframes/f75/c/extracto_gancho_0000-0100_original.wav` | −23,8 | 6,2 | −6,6 |
| `lab/hyperframes/f75/c/extracto_gancho_0000-0100_master.wav` | −14,3 | 4,5 | −1,2 |
| `lab/hyperframes/f75/c/extracto_fuerte_1044-1144_original.wav` | −21,8 | 3,4 | −6,8 |
| `lab/hyperframes/f75/c/extracto_fuerte_1044-1144_master.wav` | −12,0 | 2,4 | −0,9 |

También quedó `lab/hyperframes/f75/c/master_full.m4a` (20 MB), el master completo. Los audios no van a git: solo van los scripts, el log y los JSON.

Más notas de C1:
- `-ar 48000`, que pide el handoff, cambia la frecuencia del pipeline, que es 44 100 Hz. En lineal no hace falta. Es una decisión a confirmar.
- `alimiter` con `latency=0`, el valor por defecto, atrasa el audio unos 5 ms frente al video. Con `latency=1` no hay atraso.
- En fase2b el 192k del AAC es un literal repetido en 6 lugares, sin constante con nombre.

## Verificación
- Suite rápida del hook (`f25c`, `f24`, `f21`) más `tests/test_m05_retencion.py`, `tests/test_m01f_compuerta.py`, `tests/test_m01f_entre_promesas.py`, `tests/test_qa_entre_promesas.py`, `test_qa_studio.py`, `f5_narrative`, `f66`, `f74` y `f73`: **255 passed, 3 skipped**.
- Suite amplia, como en F73: 140 archivos más los de `tests/` y `test_qa_studio.py`, con `-n auto`. Resultado: **3 failed, 1572 passed, 29 skipped, 2 xfailed** (`lab/hyperframes/f75/suite.log`). Las 3 son las heredadas: `f51c[1-start-paredes de chapa.]`, `m03_merge_timing::test_c_guarda_de_minimo` y `::test_c_veo_path_y_veo_anchor_intacto`.
- `lab/tools/mapa_modulos.py --check`: 0 fallas. Se actualizaron los stickers de m05, m01f_critico, qa_studio.html y qa_studio_server.py.
- `DECISIONES.md`: 3 líneas del 2026-11-04 (A1, B1, C).

## diff --stat (sin los ajenos)
```
 DECISIONES.md                         |   3 +
 lab/mapa/stickers/fase2a.json         |   4 +-
 lab/mapa/stickers/guion.json          |   4 +-
 lab/mapa/stickers/orquestador.json    |   8 +--
 qa_studio.html                        |   3 +-
 qa_studio_server.py                   |   5 +-
 script_engine/m01f_critico.py         | 112 ++++++++++++++++++++++++++++++----
 script_engine/m01f_prompts/SYSTEM.txt |   2 +-
 script_engine/m05_narrative.py        |  70 ++++++++++++++++-----
 tests/test_m01f_compuerta.py          |  20 ++++--
 tests/test_m05_retencion.py           |  66 +++++++++++++++++---
 nuevos: tests/test_m01f_entre_promesas.py, tests/test_qa_entre_promesas.py, lab/hyperframes/f75/{F75_REPORT.md, suite.log, a/*, b/*, c/ (scripts, log, json)}
```

## Abierto
- **C2 sin cablear.** El master del lab da −0,9 dBTP, por encima del techo de −1,5. Falta decidir el arreglo: sobremuestrear el limitador, descontar la pérdida en G, o loudnorm dinámico. Hasta entonces, el render de Palomares saldría a −24 LUFS.
- **Omar escucha los 4 extractos** antes de que el master se use en Palomares. El sonido del master no debería cambiar mucho con el arreglo del pico, pero el pico sí.
- **`-ar 48000` y la latencia de alimiter**, que hay que confirmar al cablear.
- **192k sin constante.** En fase2b el bitrate del AAC es un literal repetido; el master lo tendría que reusar sin inventar un número.
- **Respaldo sin música.** `_final_gfx_no_music.mp4` y `mezcla_preview.wav` quedan a −24 LUFS, sin master. El analista lo acepta.
- **Archivo de la narración.** El handoff nombra `01b_narration_normalized.json`, pero los párrafos se leen de `01b_narracion_v3.json`. Da el mismo número de oraciones.
- **Nombre de pila compartido.** Se chequea contra todo `pool.personajes`, no solo contra los que pasan `es_persona`. En Wittenoom da igual de las dos maneras.
- **Crítica vieja.** El `.md` de `_steps` sigue siendo el de m01f-1. El nuevo, con «Promesas nuevas», sale recién en la próxima corrida del crítico. La métrica no entra como entrada del prompt en esta tanda.
- **Sticker de qa_studio_server.py.** Su texto no describe los cambios de F72–F74; solo se le sumó la frase de F75.
- **Los 4 abiertos del handoff** (se arreglan si se repiten):
  - el pool fusiona homónimos padre/hijo (P17);
  - la escaleta no comprueba que `humano.id` corresponda a su `rol`;
  - las rachas no cuentan «el hombre», «ese hombre» ni los pronombres;
  - un personaje con partícula («Ramón de Juan» → «ramon juan») queda imposible de encontrar si comparte nombre de pila con otro del pool.

## Veredicto del revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

La decisión de CC de no hacer C2 es correcta según el handoff.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Handoff íntegro (md5 fecdcf5b…) | OK | `md5sum` coincide. |
| 2 | A1: personaje elegido desde la narración, camino viejo borrado | OK | El diff de `m05_narrative.py` borra `_persona_de` y agrega `elegir_personaje`. Los tests viejos están reemplazados en `tests/test_m05_retencion.py`. |
| 3 | A2: tabla de candidatos y rachas de Wittenoom | OK | Corrí `a/a2_retencion_wittenoom.py`: candidatos OK, gana P17 con 16, y las 7 rachas coinciden con el contrato (14/1/7 … 15/1/10). |
| 4 | A3: una sola sustitución en SYSTEM.txt:7 | OK | El diff muestra una línea cambiada y el texto «Después» es exacto. El md5 de `SYSTEM.txt` y el de `a/SYSTEM_m01f-2.txt` es el mismo (5fa554cf…) y `a/md5.json` lo registra. `PROMPT_VERSION` pasó a `m01f-2`. |
| 5 | B1/B2: tabla de segundos entre promesas y línea ⚠ | OK | `b/01f_critico.md:56-68` trae los 7 tramos (21/24/2/139/150/182 máx./81) y la línea ⚠ con los md5 correctos. El `.md` de `_steps` no se pisó. |
| 6 | B1: QA con módulo 5 y «según la narración» | OK | Cambios en `qa_studio_server.py` y `qa_studio.html`, con `tests/test_qa_entre_promesas.py` nuevo. |
| 7 | C0: lugar común, solo lectura | OK | El reporte lo ubica en `fase2b.py:3656/3657`. `git diff` sobre `fase2b.py`, `audio_profiles.py` y `audio_manager.py` sale vacío. |
| 8 | C1: lab sin render, medición antes/después, 4 extractos | OK | Los 4 wav existen y no están vacíos, más `master_full.m4a`, `loudnorm_pass1.json` y `loudnorm_pass2.json`. La 2.ª pasada dio `normalization_type: linear`. |
| 9 | C1: pico real ≤ −1,5 dBTP | FALLA | La medición sobre el AAC da −0,9 dBTP (según el reporte). `loudnorm_pass2.json` dice `output_tp −1.50`, pero es el pico de muestra, no el real. |
| 10 | C2 solo si C0 lo confirma | OK, ver abajo | No se cableó. `fase2b.py` no tiene diff. |
| 11 | No tocar el mp4 publicado | OK | md5 actual 1fb47948e43951d4c009e13c0131d184, igual al del pedido. |
| 12 | Nada en `output/` salvo lab | OK | `git status` no muestra nada en `output/`. |
| 13 | US$ 0, sin API | OK | Los scripts de A, B y C no llaman a API. El reporte declara US$ 0. |
| 14 | Tests | OK | Los 4 archivos pedidos dan 98 passed. `mapa_modulos --check` da 0 fallas en 161 archivos. La suite amplia (3 fallas heredadas) está en `suite.log` y no la corrí: NO VERIFICABLE por mí. |
| 15 | DECISIONES.md con A1, B1 y C | OK | Tres líneas del 2026-11-04. |
| 16 | Reporte con «abierto» completo | PARCIAL | `F75_REPORT.md` tiene el «Abierto» completo. Falta el veredicto, que se pega después de este. |

**Sobre C2:** la decisión es correcta.
- El handoff condiciona C2 a «constantes solo las de la tabla §1» y a un techo de −1,5 dBTP.
- La receta del handoff, tal como está escrita, deja el pico real en −0,9. Cablearla rompería el techo del proyecto en el render de Palomares.
- Los arreglos posibles (sobremuestrear, descontar en G, loudnorm dinámico) necesitan un número o un diseño que no está en §1.
- El handoff pide PARADA cuando algo no coincide. La C0 sí confirma el lugar común, pero el handoff no obliga a cablear aunque el lugar exista.
- El −2 dBFS es un supuesto del propio analista, y el reporte muestra por qué no alcanza.

**Fuera de alcance:**
- Los tres ajenos declarados, que no son de la tanda: `diag_234_cap4.py`, `lab/hyperframes/f28/a/f28a.log` y `lab/hyperframes/f58/pedido_paquetes_wittenoom.txt`. No deben entrar al commit.
- Los stickers de `lab/mapa/stickers/*` sí corresponden: los regeneró `mapa_modulos`.
- Los `??` previos al inicio (`_lab_*`, `_probe_*` y demás) tampoco son de la tanda.

**Observaciones:**
- Corrí `b/rerender_wittenoom.py` y falló al imprimir la flecha «→» en la consola cp1252 (`UnicodeEncodeError`). El `.md` en disco ya tenía el contenido correcto, pero el script no es re-ejecutable limpio en esta consola.
- El reporte dice que el respaldo se llama `_final_gfx_no_music.mp4`, y no `_final_no_music.mp4` como dice el handoff. No lo verifiqué, pero está declarado.
- Los wav no van a git, según el reporte. Omar los escucha desde disco.

**Riesgos que el contrato no cubre:**
- El render de Palomares saldría a −24 LUFS hasta que alguien decida el arreglo del pico. Falta además confirmar `-ar 48000` frente a los 44 100 Hz del pipeline.
- Los extractos «master» que va a escuchar Omar tienen pico real −0,9 y −1,2. El arreglo final los cambiará un poco.
- El personaje depende de mayúsculas y de nombre y apellido. «El hombre», los pronombres y los nombres con partícula quedan sin contar (ya anotado en «abierto»).

### Adenda de CC
- **Punto 9 / C2:** de acuerdo. C2 queda para que el analista decida el arreglo del pico real. Hasta entonces, Palomares sale a −24 LUFS.
- **Punto 14:** la suite amplia la corrí yo (`lab/hyperframes/f75/suite.log`): 3 failed (las heredadas), 1572 passed, 29 skipped, 2 xfailed. En el commit, el hook vuelve a correr la suite rápida.
- **Punto 16:** con este pegado queda cerrado. `ESTADO_SESION.md` tiene la línea F75 y entra en el mismo commit.
- **`rerender_wittenoom.py` en cp1252:** arreglado con `sys.stdout.reconfigure(encoding="utf-8")`. Lo re-corrí con `PYTHONIOENCODING=cp1252` y anduvo. El `.md` dio el mismo md5 (`eb36251a…`).
- **Nombre del respaldo:** sale de `final_path.stem + MUSIC_INTERMEDIATE_SUFFIX` (`fase2b.py:3543-3546`, sufijo `"_no_music"` en :142). Con gfx queda `<tid>_final_gfx_no_music.mp4`, que es el que hay en disco para Wittenoom.
