
## B — Compuerta del render: sin guion aprobado no hay `--gfx` (`f97c6f1`)
- **Aprobación**: `fase2b <topic> --aprobar-guion "Omar <fecha>"` (`script_engine/aprobacion.py`, solo biblioteca
  estándar) escribe en `output/<topic>/GUION_PANTALLA.json` `aprobado: {por, fecha, md5_planes, planes}`; `md5_planes` =
  md5 conjunto (nombre y bytes, en orden) de los `gfx_plan_chNN.resolved.json` del topic. Falla si no hay guion, si no
  hay planes o si algún plan es más nuevo que el guion. **CC lo corre solo cuando el prompt de Omar dice literalmente
  «aprobado»** (está en `/tanda` y en el skill). Lo invalida cualquier `--plan-edit` o `--plan-only` posterior: el guion
  se reescribe sin `aprobado`, y si los planes cambian el md5 ya no coincide.
- **Hook `guard_render`** (`.claude/hooks/guard_render.py`, en `settings.json`, mismo patrón que `guard_git`): ante un
  comando que corre `fase2b … --gfx` mira el guion del topic; sin guion, sin `aprobado` o con los planes cambiados,
  **bloquea** (exit 2) y dice qué falta. Pasan: `--plan-only`, `--plan-edit`, `--aprobar-guion`, `--only-cap … --gfx-debug`
  y todo fase2b sin `--gfx` (la salida del candado md5 de ch02). `--dry-run` y el modo batch con `--gfx` se bloquean.
- **Tests** (`test_module_f33.py`): sin guion o sin aprobación bloquea; con aprobación pasa; después de un `--plan-edit`
  (un plan cambia) vuelve a bloquear, y también después de regenerar el guion; `--plan-only` y lo que no es render nunca
  se bloquean; `--dry-run` y batch con `--gfx` sí; aprobar falla con un plan más nuevo que el guion; el hook está en
  `settings.json`.

### Prueba del hook (B.3 / E.1)
Por stdin (`lab/hyperframes/f33/b/prueba_guard_render.txt`):
```
$ python fase2b.py f8s3-vajont-f30 --gfx --dry-run                                  → exit 2 (no está aprobado)
$ python fase2b.py f8s3-vajont-f30 --keep-segments --reuse-visuals --gfx --gfx-sparse --gfx-quality looks --rotulista
                                                                                     → exit 2 (no está aprobado)
$ python fase2b.py f8s3-vajont-f30 --plan-only --rotulista                           → exit 0
$ python fase2b.py ba6c3cac-a091-41c0-8dad-afd2f4364747 --only-cap ch02 --reuse-visuals --sw-encode → exit 0
```
**En vivo, en esta sesión** (`lab/hyperframes/f33/e/prueba_en_vivo.txt`): CC escribió el comando de render en seco de
Vajont y Claude Code lo frenó antes de correrlo:
```
PreToolUse:Bash hook error: [python -I "$CLAUDE_PROJECT_DIR/.claude/hooks/guard_render.py"]: guard_render: sin guion
aprobado no hay render — el guion de f8s3-vajont-f30 no está aprobado (Omar lo aprueba; CC corre `fase2b f8s3-vajont-f30
--aprobar-guion "Omar <fecha>"` solo si su prompt dice «aprobado»)
```
**Falso positivo encontrado en E y arreglado:** el hook del commit B frenaba también comandos que solo *mencionaban* el
render (un heredoc que escribía la evidencia, un parche con ese texto). El primer arreglo (contar solo comandos que
empiezan con `python`) abría un hueco que encontró el revisor (`timeout 600 python fase2b.py … --gfx` pasaba); el arreglo
final saca el cuerpo de los heredocs antes de mirar, no cuenta los comandos de texto (`echo`, `grep`, `git`, `cat`…),
mira detrás de cualquier prefijo (`timeout`, `nohup`, `time`, `env`, `cmd /c`, `start`) y dentro de `bash -c "…"`. Tests:
heredoc y echo no se bloquean; los seis prefijos, `bash -c` y un fase2b después de un heredoc sí. En vivo, después del
arreglo final, `timeout 600 python fase2b.py f8s3-vajont-f30 --gfx --dry-run` quedó bloqueado.

## C — `/tanda`, skills y simulador (`2d87032`)
- `.claude/commands/tanda.md` (copia en `~/.claude/commands/tanda.md`); skills `.claude/skills/guion-de-pantalla/` y
  `.claude/skills/simular-reglas/` (solo en el repo: son del pipeline); agente `.claude/agents/simulador.md`;
  `lab/tools/simular_regla.py`. El agente **`revisor-handoff` ya era de usuario** (`~/.claude/agents/revisor-handoff.md`,
  del 18-10): no se copió.
- Ejemplo del simulador contra el guion de F32 (`lab/hyperframes/f33/c/simulacion_sello_repite_voz.md`), con la regla de
  DECISIONES «sello = clima: no repite la voz ni el subtítulo»:
