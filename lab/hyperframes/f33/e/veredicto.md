
VEREDICTO: CUMPLE CON OBSERVACIONES (A–D cumplen; E está a medio cerrar y el arreglo del hook sin commitear abre un hueco en la compuerta)

| # | requisito | estado | evidencia |
|---|---|---|---|
| A.1 | DECISIONES.md y ENTRADA al repo sin editar | OK, con un NO VERIFICABLE | `git show 651cb25:` da el mismo md5 que el árbol (231c8f15 / cd5edb63), sin CRLF. No existe copia original. El mtime de ENTRADA (13:33) es anterior al commit. El de DECISIONES (14:23) es posterior al commit A (14:18), aunque `git status` lo da limpio. Byte a byte contra el original: NO VERIFICABLE. |
| A.2 | test de constantes en modo inventario y etiquetas | OK | `pytest test_constantes_con_origen.py`: 2 pasan. 101 constantes / 35 con origen / 66 sin origen (coincide con el reporte). Las 33 «identidad F3» coinciden con `misterio.json`, tanto en HEAD como en el árbol. |
| A.2b | Ningún valor cambia | OK | AST de `gfx_config.py` en `cd60c74` contra hoy: idéntico. El diff solo trae comentarios. |
| A.3 | Línea de DECISIONES en CLAUDE.md | OK | `CLAUDE.md:3`. |
| B.1 | `--aprobar-guion` y bloque `aprobado` | OK | `script_engine/aprobacion.py:37-54`; `fase2b.py` +18 líneas. |
| B.2 | Hook bloquea sin guion, sin aprobar o con md5 distinto | OK | Corrí `guard_render.py` por stdin con Vajont (`f8s3-vajont-f30`, `--dry-run` y el render completo): exit 2. Con `--plan-only`, `--plan-edit` y `--only-cap ch02` sin `--gfx`: exit 0. Está en `settings.json`. |
| B.3 | Tests de la compuerta | OK | `test_module_f33.py` + constantes: 11 pasan. |
| C.1–C.5 | `/tanda`, 2 skills, agente `simulador`, simulador, copias | OK | Todo existe. `~/.claude/commands/tanda.md` es idéntico al del repo. Los skills están solo en el repo. `revisor-handoff` ya era de usuario. El simulador reproduce 10 → 10 → 0. Los ids de Vajont del skill (D117, Q50, D192, D128, T85) existen en el guion y los campos de edición coinciden con `CAMPOS_EDITABLES`. |
| D.1–D.2 | Mapa .md y .json | OK | 37 filas, 117 aristas, 14 muertos. «Quién lo llama» coincide con mi grep de imports en 10 módulos. Las fechas de nacimiento y de «muerto» las verifiqué con `git log` (7e704de, 5ae6177, a878836, cc3f079, 2fcd603, e18e656). |
| D.3 | Hook `guard_mapa` | OK | En un repo temporal con un `gfx_*.py` staged, el `git commit` produce el aviso (rc 0). |
| E.1 | Suites, md5 y prueba del hook | OK | Suite amplia: 1003 pasan + las 5 previas esperadas (corrida mía). Rápida 58. md5 `38e5ba14…` en los logs a–e y en el mp4 en disco. |
| E.2 | Reporte y ESTADO | PARCIAL | El reporte tiene todas las secciones y su mapa pegado es idéntico al archivo, pero termina en «## Veredicto» sin contenido. `ESTADO_SESION.md` no cierra E. No hay commit E. |
| Frenos | Sin render, sin tocar `.env`, `config.py`, `lab/_gpt_probe_analista/` ni `gfx_profiles/*`; sin borrar | OK | Ningún commit toca ninguno. `gfx_profiles/*`, `diag_234_cap4.py` y `f28a.log` salen modificados en el árbol, pero con fechas anteriores a la tanda. No hay borrados en `cd60c74..HEAD`. |

Observaciones (las dos primeras te las dejo para que decidas):
1. **Hueco en la compuerta, hoy sin commitear.** El arreglo de E pide que el comando simple empiece con `python`/`py`/`fase2b.py`. Pasa (exit 0) `timeout 600 python fase2b.py f8s3-vajont-f30 --gfx`, y también `nohup python …`, `time python …` y `cmd /c python …`. El hook de `HEAD` (commit D) sí los frenaba. El reporte (lectura 3 y «Lo que queda abierto») solo admite los runners de lab; no dice nada de estos prefijos. El falso positivo es real: el hook de D también frenaba el heredoc. Pero el arreglo cambió ese falso positivo por una forma de saltarse la compuerta.
2. **El mapa llama «muerto» a lo que sigue corriendo.** La definición es «nadie lo llama». Pero `select_punches`, `identity_transitions` y `place_emphasis` se llaman igual (`gfx_layer.py:783/786`, `gfx_director.py:776`) y su resultado se descarta; la columna «por qué» lo dice, pero la definición no. Además `data_callout.html.tmpl` figura «solo sin rotulista» en la tabla principal y «muerto» en la lista de muertos.
3. **Pendiente de cierre.** Falta el veredicto en el reporte, el estado de E en ESTADO y el commit E. Al commitear: `git add -f` para `.claude/hooks/guard_render.py`, más `test_module_f33.py`, el reporte y `lab/hyperframes/f33/e/`. Esos archivos de E están sin trackear o modificados.

Fuera de alcance: ninguno en `cd60c74..HEAD`. En el árbol hay archivos modificados o sin trackear anteriores a la tanda y no tocados por ella.

Riesgos que el contrato no cubre: el hook solo ve el comando escrito (no `bash -c`, `powershell -Command` ni runners de lab que llamen a fase2b por dentro); la aprobación no impide que el render vuelva a decidir (el reporte lo admite). Las 66 constantes sin origen quedan en inventario sin que nada falle.

**Después del veredicto (CC):**
- Obs. 1 (hueco): arreglado. El hook final saca el cuerpo de los heredocs antes de mirar, no cuenta los comandos de texto (`echo`, `printf`, `grep`, `rg`, `git`, `sed`, `awk`, `cat`, `head`, `tail`, `Write-Output`, `Write-Host`, `Select-String`, `findstr`), busca `fase2b.py`/`-m fase2b` detrás de cualquier prefijo y mira dentro de un argumento que sea un comando entero (`bash -c "…"`, `powershell -Command "…"`). Tests nuevos: `timeout 600`, `nohup`, `time`, `cmd /c`, `env A=1`, `start /b`, `bash -c "…"` y un fase2b después de un heredoc **bloquean**; el heredoc y el echo que solo lo mencionan **no**. En vivo: `timeout 600 python fase2b.py f8s3-vajont-f30 --gfx --dry-run` quedó bloqueado (`e/prueba_en_vivo.txt`, punto 3). El riesgo de `bash -c` / `powershell -Command` queda cubierto; siguen fuera los runners y los scripts `.sh`/`.ps1` (lectura 3, abierto 3).
- Obs. 2 (definición de muerto): el mapa ahora dice «muerto = en el camino con escaleta y rotulista no aporta: nadie lo llama, o se llama y su resultado se descarta», y las tres funciones que se calculan y se tiran llevan «**se llama y se descarta**» en su «por qué». `data_callout.html.tmpl` pasó a «muerto en el camino con rotulista; vive sin rotulista» en la tabla, igual que en la lista.
- Obs. 3: veredicto pegado, ESTADO cerrado y commit E con `git add -f` para lo de `.claude/`.
- A.1 NO VERIFICABLE: los archivos se agregaron con `git add` tal como estaban en disco, sin ninguna edición de CC (no hay `Edit`/`Write` sobre ellos en esta sesión); el mtime de DECISIONES posterior al commit sin diff en `git status` es un toque de mtime sin cambio de contenido.
