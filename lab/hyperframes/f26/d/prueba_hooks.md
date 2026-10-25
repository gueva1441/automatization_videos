| hook | caso | esperado | resultado | s |
|---|---|---|---|---|
| `guard_git.py` | git add .env | bloquea | bloquea (exit 2) ✅ | 0.1 |
| `guard_git.py` | git add config.py (en una cadena con cd &&) | bloquea | bloquea (exit 2) ✅ | 0.1 |
| `guard_git.py` | git add -A (trae lab/_gpt_probe_analista/) | bloquea | bloquea (exit 2) ✅ | 0.1 |
| `guard_git.py` | git add llave.txt (con una llave adentro) | bloquea | bloquea (exit 2) ✅ | 0.1 |
| `guard_git.py` | git add b.py | pasa | pasa ✅ | 0.1 |
| `guard_git.py` | git commit con llave.txt en el índice | bloquea | bloquea (exit 2) ✅ | 0.1 |
| `guard_git.py` | git commit con b.py en el índice | pasa | pasa ✅ | 0.1 |
| `guard_git.py` | git push origin main | bloquea | bloquea (exit 2) ✅ | 0.1 |
| `guard_git.py` | git push origin rama:main | bloquea | bloquea (exit 2) ✅ | 0.1 |
| `guard_git.py` | git push origin rama | pasa | pasa ✅ | 0.1 |
| `guard_git.py` | git checkout main && git merge rama | bloquea | bloquea (exit 2) ✅ | 0.1 |
| `guard_git.py` | git merge main (estando en rama) | pasa | pasa ✅ | 0.1 |
| `suite_rapida.py` | git commit con un test rojo (HOOK_SUITE_RAPIDA) | bloquea | bloquea (exit 2) ✅ | 0.6 |
| `suite_rapida.py` | git commit con la suite rápida de verdad | pasa | pasa ✅ | 3.9 |
| `suite_rapida.py` | git status (no es commit: no corre nada) | pasa | pasa ✅ | 0.1 |
| `tope_tanda.py` | python fase2a.py con 3.50 gastados de 3.00 | bloquea | bloquea (exit 2) ✅ | 0.1 |
| `tope_tanda.py` | python -I fase1_5.py con 3.50 de 3.00 | bloquea | bloquea (exit 2) ✅ | 0.1 |
| `tope_tanda.py` | python fase2a.py con 3.50 gastados de 10.00 | pasa | pasa ✅ | 0.1 |
| `tope_tanda.py` | python fase2b.py (no lo mira) | pasa | pasa ✅ | 0.1 |
| `md5_prompt.py` | Edit PROMPT_ESCALETA_f26_1.md | avisa | avisa ✅ | 0.1 |
| `md5_prompt.py` | Edit m01a_escaleta.py | avisa | avisa ✅ | 0.1 |
| `md5_prompt.py` | Edit video_length.py | nada | pasa ✅ | 0.1 |
