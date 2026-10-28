# HANDOFF F42b — Las librerías del form y que una falla se vea como falla

Analista · 2026-10-27 23:05 · rama `f11-guion-v4` · misma sesión de CC que F42 (Omar no pidió sesión nueva).

## Por qué
- Omar lanzó «Hospital Waverly Hills embrujado» desde el form a las 22:42. El research de la semilla tronó a las 22:44 con `ModuleNotFoundError: No module named 'bs4'` (`researcher_steps/research_v3.py:687`, adentro de `html_to_text`). Aun así, el form mostró «✓ pipeline terminó OK» y quedó «no hay topics».
- **Causa 1:** el form corre con el Python desde donde se lanzó `qa_studio_server` (`qa_studio_server.py:1522`, `sys.executable`), que no tiene `bs4`. En F39, CC corrió el research con otro Python que sí la tenía. `requirements.txt` no lista `bs4` (y probablemente tampoco `trafilatura` ni `pdfplumber`, del mismo archivo). F41 b7 y F42 k11 ya avisaban que el form nunca se probó de verdad y que hay dos Pythons.
- **Causa 2:** la falla se traga en tres pasos:
  1. `topic_researcher.research_topics` atrapa el error de la semilla y sigue (`topic_researcher.py:1039-1050`, `continue`);
  2. `fase1.py:776-779` ve que no hay topics, imprime «Abortando.» y sale con `return` (exit 0);
  3. `run_pipeline.main` (`--research`) no encuentra el sentinel y lo trata como «soltaste el pick o cancelaste. Stop limpio.», también exit 0.
- La semilla sigue en la bandeja (`selected_seeds.json`, 22 semillas, Waverly incluida): se puede relanzar en cuanto esto esté arreglado.

## Chequeo del analista (skill handoff-analista §0)
- ¿Construye sobre algo que se va a reemplazar? No.
- ¿Cambia el orden de las tandas? Sí: va antes de F43 (auditoría), porque sin esto el form no corre ni un tema. Voto del analista aceptado por Omar (22:58).

## Constantes
| valor | origen | quién |
|---|---|---|
| ninguno nuevo | — | — |

Qué es «de afuera» se decide por código, sin listas a mano:
- No está en `sys.stdlib_module_names`.
- No es un archivo ni un paquete del repo.

Qué es «opcional» también se decide por código: el import está dentro de un `try` cuyo `except` agarra `ImportError`, `ModuleNotFoundError` o `Exception`. Ejemplo: `trafilatura` en `html_to_text`.

## Módulos que toca (hoy → después)
| archivo | hoy | después |
|---|---|---|
| `dependencias.py` (nuevo, raíz) | — | Recorre por AST los imports alcanzables desde los scripts de las etapas del form (los mismos que lee el mapa de F42 de `run_pipeline`) y separa las librerías de afuera en requeridas u opcionales, cada una con archivo:línea. `faltantes()` dice cuáles no encuentra el Python actual (`importlib.util.find_spec`, sin importar nada). |
| `run_pipeline.py` | Arranca la etapa directo. Con `--research`, «sin sentinel» = stop limpio (exit 0). | Primero llama a `dependencias.faltantes()`. Si falta una requerida: PARADA (exit 1) antes de gastar, con la lista, el archivo:línea de cada una y el comando `"<sys.executable>" -m pip install -r requirements.txt`. Las opcionales que falten solo dan aviso. Con `--research`, si `fase1` sale con error, lo reporta como falla con su motivo, no como stop limpio. |
| `fase1.py` + `topic_researcher.py` | Una semilla que falla se loguea y se sigue; sin topics → `return` (exit 0). | `research_topics` devuelve las semillas que fallaron, con el error de cada una. `fase1` imprime cada falla («semilla X: error Y; sigue en la bandeja») y sale con exit 1. Soltar el pick o cancelar sigue siendo exit 0. La compuerta del pool (`PoolGateRed`, la que devuelve la semilla a la bandeja por falta de material) no cambia: no es un error. |
| `requirements.txt` | Le faltan librerías que usa la cadena. | Todas las requeridas, con la versión instalada en el Python del form. |

`lab/mapa/stickers/` se actualiza para estos archivos (sticker nuevo de `dependencias.py`) y `--check` = 0 al final.

## A — El Python del form y lo que le falta
1. Encontrá el Python con el que corre el form: el `python.exe` del proceso vivo de `qa_studio_server` (`Get-Process` → `Path` y `CommandLine`, **solo lectura; no lo cierres**). Anotá la ruta en el reporte.
2. Con ese Python corré `dependencias.py` y pegá la tabla: librería · requerida u opcional · archivo:línea · la tiene sí/no.
3. Instalá en ese Python las requeridas que faltan (`"<ese python>" -m pip install …`). Si una no está en el índice de pip o choca con otra, PARADA y decilo.
4. Completá `requirements.txt` con lo instalado (con su versión).
5. Corré otra vez el paso 2 y pegá «0 requeridas faltantes».

**Salida de A:** las dos tablas y la ruta del Python.

## B — PARADA antes de gastar si falta una librería
1. `run_pipeline.main` llama a `dependencias.faltantes()` antes de cualquier etapa (`--research`, `--topic` o el menú).
2. Tests nuevos en `test_module_f42b.py`, todos sin red:
   - con `find_spec` simulado devolviendo `None` para `bs4`, `run_pipeline --research` sale con 1, imprime `bs4` con su archivo:línea (el que dé `dependencias`, no un número escrito en el test) y el comando de pip, y **no** llama a `_run` (se comprueba con un stub de `_run` que falla si lo llaman);
   - una opcional faltante (`trafilatura`) solo avisa y sigue;
   - con todo presente, sigue igual que hoy;
   - `dependencias` lista `bs4` como requerida y `trafilatura` como opcional (sobre el código real del repo).

**Salida de B:** la salida de la PARADA simulada, pegada tal cual.

## C — Que una falla del research se vea como falla
1. Hacé los cambios de `topic_researcher.research_topics` y `fase1` de la tabla de módulos.
2. `run_pipeline --research` propaga ese exit 1 con «fase1: el research falló» (ya devuelve `rc` si es ≠ 0; verificá que el form muestre «✗ pipeline terminó (código 1)», `qa_form.html:191`, leyendo el código).
3. Tests en `test_module_f42b.py`, sin red y con `_research_seed_deep` simulado lanzando `ModuleNotFoundError`:
   - `fase1` sale con 1 y la semilla sigue en la bandeja;
   - soltar el pick sale con 0;
   - con `PoolGateRed`, igual que hoy.

**Salida de C:** la salida de `fase1` con la falla simulada.

## Validación (al final, una vez)
- `python lab/tools/mapa_modulos.py --check` = 0.
- Suite rápida, suite amplia (`lab/hyperframes/f41/verificar.sh`) y candado de ch02 (`f792f3d4…` con subs, `98386f86…` sin subs). La corrida de Omar ya terminó, así que esta vez sí se corren, **con el Python de siempre de las suites**. Más `test_module_f42b.py` con ese Python y también con el del form.
- **Prohibido** `pytest` en bloque sobre `test_*.py` y cualquier colecta sin la exclusión de F42 (incidente de F42, k2). Solo los archivos y patrones nombrados aquí.

## Reglas fijas
- US$ 0: ninguna llamada a API. Los tests van con stubs, y el proxy muerto de F42 aplica a cualquier corrida de tests.
- No se relanza el research ni el form. Lo relanza Omar después.
- No se cierra ningún proceso de Omar (sus `qa_studio_server` siguen vivos).
- Nada en `data/` ni en `output/`.
- `config.py` y `.env` no se tocan.
- Un commit por parte (A, B, C), por rutas explícitas; push a `origin/f11-guion-v4`. Sin merge.
- Reporte `lab/hyperframes/f42/F42b_REPORT.md`: salidas de A, B y C pegadas, «lo que queda abierto» entero y el veredicto íntegro de `revisor-handoff`. ESTADO al día. Cerrá los subagentes y shells propios. **PARADA.**

## Abierto que el analista deja anotado (no es de esta tanda)
- **Dos Pythons (k11 de F42):** las suites corren en el Python del sistema y el form en otro. Voto: un solo Python, el del form, también para tests y candado. Se decide con Omar después de F42b, porque cambiar de Python puede mover el candado.
