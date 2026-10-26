# Hooks de Claude Code del repo (F26 §D)

Están en `.claude/settings.json` (commiteado con `git add -f`, porque `.claude/` está en `.gitignore`). Python, solo
biblioteca estándar; cada hook recibe el evento JSON por stdin. `exit 2` = Claude Code frena la herramienta y le
muestra el motivo a Claude.

| hook | evento | qué hace |
|---|---|---|
| `guard_git.py` | PreToolUse Bash/PowerShell | Bloquea `git add`/`git commit` que incluyan `.env`, `config.py`, algo bajo `lab/_gpt_probe_analista/` o un archivo con una llave de Anthropic/OpenAI adentro (prefijo `sk-` + `ant-`/`proj-` seguido de ≥ 20 caracteres de llave; el prefijo solo, como texto de una regla, no bloquea). Lo que entra en un `add` se le pregunta a git (`git add --dry-run` con los mismos argumentos); en un `commit`, el índice más lo que agregan `-a` o las rutas después de `--`. Bloquea `git push` hacia `main` (refspec `main` o `x:main`, o push sin refspec estando en main) y `git merge` estando en main (o después de `git checkout main` en la misma cadena). |
| `suite_rapida.py` | PreToolUse Bash/PowerShell | Antes de `git commit` corre `pytest test_module_f25c.py test_module_f24.py test_module_f21.py -q -x` (tope 170 s). Rojo → bloquea con las últimas 25 líneas. `HOOK_SUITE_RAPIDA="a.py b.py"` cambia la lista (para probar el hook). |
| `md5_prompt.py` | PostToolUse Edit/Write/MultiEdit | Si el archivo es un `PROMPT_*.md` o tiene `## SISTEMA`/`SYSTEM_V2` adentro, avisa el md5 del archivo (LF) ahora y en `HEAD`, y el del bloque `## SISTEMA` (extraído como en los tests). No bloquea. |
| `tope_tanda.py` | PreToolUse Bash/PowerShell | Antes de `python … fase1_5.py` o `python … fase2a.py`, si existe `lab/TOPE_TANDA.json` (`{"usd": N}`, opcional `"desde": "AAAA-MM-DDTHH:MM:SS"`), suma `total_cost` de `data/cost_history.json` desde `desde` (sin `desde`: desde que se escribió el archivo del tope). Si ya llegó al tope, bloquea. Sin archivo de tope, no hace nada. |
| `guard_render.py` | PreToolUse Bash/PowerShell | F33 §B: bloquea `fase2b … --gfx` si `output/<topic>/GUION_PANTALLA.json` no existe, no tiene `aprobado` (lo escribe `fase2b <topic> --aprobar-guion "Omar <fecha>"`, que CC corre solo cuando el prompt de Omar dice «aprobado») o su `md5_planes` no coincide con los `gfx_plan_chNN.resolved.json` de hoy (`script_engine/aprobacion.py`). No pasan por el hook `--plan-only`, `--plan-edit`, `--aprobar-guion`, `--only-cap … --gfx-debug` ni fase2b sin `--gfx` (el candado md5 de ch02). `--dry-run` y el modo batch con `--gfx` se bloquean. |
| `guard_mapa.py` | PreToolUse Bash/PowerShell | F33 §D.3: antes de `git commit`, si lo que entra toca `script_engine/gfx_*.py` o `fase2b.py` y no toca `lab/MAPA_MODULOS.md`/`.json`, avisa (no bloquea): regenerar el mapa (`python lab/tools/mapa_modulos.py`) o explicar en el reporte por qué no cambió. |

Límites conocidos:
- Ven el comando que se escribe en la herramienta, no lo que un script lanza por dentro (un runner de lab que llama a
  `fase2a.py` con `subprocess` no pasa por `tope_tanda`).
- `cost_history.json` se escribe solo al cerrar un video (`cost_tracker.end_video`, que llama fase2b): el gasto de
  fase1_5/fase2a sin fase2b no aparece ahí todavía. Por eso el tope es por tanda, no por llamada.
- `cost_history.json` hoy no es UTF-8 válido (cost_tracker lo escribe sin `encoding`); el hook lo lee y, si falla,
  cae a cp1252.

Prueba: `python -I lab/hyperframes/f26/d/prueba_hooks.py` → un caso que bloquea y uno que pasa por hook
(`lab/hyperframes/f26/d/prueba_hooks.md`).
