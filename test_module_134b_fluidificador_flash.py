"""
test_module_134b_fluidificador_flash.py — HANDOFF_134b (offline, sin API).

2. gemini_helpers: thinking_budget=None NO agrega thinking_config (regresión de los demás
   callers); thinking_budget=0 SÍ lo agrega.
3. Reporter: entries con descriptions mixtas → agregado por módulo correcto.
(1 y 4 —fluidificador a Flash y rótulo Pro/Flash de los slots— se borraron en F50 con el fluidificador.)

USO:
    python test_module_134b_fluidificador_flash.py
"""
import sys

import gemini_helpers as gh
from cost_tracker import CostTracker


def _check(cond, msg, fails):
    if not cond:
        fails.append(msg)


def main() -> int:
    fails: list[str] = []

    # ── (2) gemini_helpers: thinking_budget None vs 0 en el payload ──
    orig_gc = gh._client.models.generate_content
    cfgs = []

    class _FakeResp:
        text = '{"ok": 1}'
        usage_metadata = None

    def fake_gc(model, contents, config):
        cfgs.append(config)
        return _FakeResp()

    gh._client.models.generate_content = fake_gc
    try:
        gh.call_flash_json("p")                       # tb None (default) → sin thinking_config
        _check(getattr(cfgs[-1], "thinking_config", None) is None,
               "(2) tb=None agregó thinking_config (regresión de otros callers)", fails)
        gh.call_flash_json("p", thinking_budget=0)     # tb 0 → con thinking_config
        tc = getattr(cfgs[-1], "thinking_config", None)
        _check(tc is not None and tc.thinking_budget == 0,
               "(2) tb=0 no fijó ThinkingConfig(thinking_budget=0)", fails)
    finally:
        gh._client.models.generate_content = orig_gc

    # ── (3) reporter por módulo ──
    ct = CostTracker()
    ct.track_gemini_tokens("m09 packaging", "gemini-2.5-flash", 772, 227, 0)
    ct.track_gemini_tokens("m09 packaging", "gemini-2.5-flash", 700, 210, 5)
    ct.track_gemini_tokens("ficha_caso", "gemini-2.5-pro", 7008, 5855, 8188)
    ct.track_gemini_tokens("dynamic_queries: submarinos", "gemini-2.5-flash", 100, 80, 10)
    ct.track_gemini_tokens("call_flash_json", "gemini-2.5-flash", 50, 40, 5)
    bd = ct.get_gemini_summary()["by_desc"]
    _check(bd.get("m09 packaging", {}).get("calls") == 2, "(3) m09 packaging no agrupó 2 calls", fails)
    _check(bd.get("m09 packaging", {}).get("tokens_thinking") == 5, "(3) thinking de m09 packaging mal", fails)
    _check("ficha_caso" in bd, "(3) falta ficha_caso", fails)
    _check("dynamic_queries" in bd, "(3) 'dynamic_queries: X' no colapsó a 'dynamic_queries'", fails)
    _check("motor (sin tag)" in bd, "(3) 'call_flash_json' no cayó en 'motor (sin tag)'", fails)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] plumbing tb None/0, reporter por módulo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
