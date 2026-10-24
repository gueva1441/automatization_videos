"""F22b — llamada de prueba de 10 tokens (claude-opus-5-5) para confirmar que la llave de .env y el dominio
api.anthropic.com funcionan. No imprime la llave ni los headers: solo código HTTP, modelo, stop_reason, usage y costo.
Uso: python -I lab/hyperframes/f22b/prueba_llave.py
"""
import json
import sys
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    import claude_helpers as ch
    body = {"model": "claude-opus-5-5", "max_tokens": 10, "output_config": {"effort": "low"},
            "messages": [{"role": "user", "content": "Respondé solo: ok"}]}
    try:
        r = ch._post(body)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"sin conexión: {type(e).__name__}: {e.reason}")
        sys.exit(1)
    u = r.get("usage") or {}
    out = {"http": 200, "modelo": r.get("model"), "stop_reason": r.get("stop_reason"),
           "texto": "".join(b.get("text") or "" for b in r.get("content") or [] if b.get("type") == "text"),
           "usage": {k: u.get(k) for k in ("input_tokens", "output_tokens")}, "usd": round(ch.cost_of(r.get("model") or "", u), 6)}
    print(json.dumps(out, ensure_ascii=False))
    (Path(__file__).resolve().parent / "prueba_llave.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                                                      encoding="utf-8")


if __name__ == "__main__":
    main()
