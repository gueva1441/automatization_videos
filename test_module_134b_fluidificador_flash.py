"""
test_module_134b_fluidificador_flash.py — HANDOFF_134b (offline, sin API).

1. El fluidificador rutea a Flash con thinking_budget=0 (mock del caller, assert de kwargs).
2. gemini_helpers: thinking_budget=None NO agrega thinking_config (regresión de los demás
   callers); thinking_budget=0 SÍ lo agrega.
3. Reporter: entries con descriptions mixtas → agregado por módulo correcto.
4. Rótulo: _SEEDREAM_SLOTS_MODEL_LABEL deriva del flag (Pro/Flash), nunca texto fijo.

USO:
    python test_module_134b_fluidificador_flash.py
"""
import sys

import script_engine.m03_visual as m03
import gemini_helpers as gh
from cost_tracker import CostTracker


def _check(cond, msg, fails):
    if not cond:
        fails.append(msg)


class _Profile:
    formula = m03.SEEDREAM_SLOT_KEYS
    aspect_ratio_text = "wide horizontal composition"


def main() -> int:
    fails: list[str] = []

    # ── (1) fluidificador → Flash + thinking_budget=0 + description ──
    orig_flash, orig_pro = m03.call_flash_json, m03.call_pro_json
    cap = {}
    CLEAN = ("a plain worn glass object resting on a bare metal table in dim grey overcast "
             "light inside an abandoned room, its surface unmarked and quiet.")

    def fake_flash(prompt, system_instruction=None, response_schema=None,
                   thinking_budget=None, description=None):
        cap["tb"] = thinking_budget
        cap["desc"] = description
        return {"prose": CLEAN}

    def fake_pro(*a, **k):
        cap["pro_called"] = True
        return {"prose": CLEAN}

    m03.call_flash_json, m03.call_pro_json = fake_flash, fake_pro
    try:
        slots = {k: "worn object" for k in m03.SEEDREAM_SLOT_KEYS}
        slots["text_in_image"] = {"present": False}
        prose = m03._fluidify_item(slots, [], _Profile(), "cap 2 img #1")
        _check(prose == CLEAN, "(1) el fluidificador no devolvió la prosa del caller", fails)
        _check(cap.get("tb") == 0, f"(1) thinking_budget != 0 (fue {cap.get('tb')})", fails)
        _check(cap.get("desc") == "m03:fluidificador", f"(1) description mal: {cap.get('desc')!r}", fails)
        _check("pro_called" not in cap, "(1) el fluidificador TODAVÍA llama a Pro", fails)
    finally:
        m03.call_flash_json, m03.call_pro_json = orig_flash, orig_pro

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
    ct.track_gemini_tokens("m03:fluidificador", "gemini-2.5-flash", 772, 227, 0)
    ct.track_gemini_tokens("m03:fluidificador", "gemini-2.5-flash", 700, 210, 5)
    ct.track_gemini_tokens("m03:slots", "gemini-2.5-pro", 7008, 5855, 8188)
    ct.track_gemini_tokens("dynamic_queries: submarinos", "gemini-2.5-flash", 100, 80, 10)
    ct.track_gemini_tokens("call_flash_json", "gemini-2.5-flash", 50, 40, 5)
    bd = ct.get_gemini_summary()["by_desc"]
    _check(bd.get("m03:fluidificador", {}).get("calls") == 2, "(3) fluidificador no agrupó 2 calls", fails)
    _check(bd.get("m03:fluidificador", {}).get("tokens_thinking") == 5, "(3) thinking del fluidificador mal", fails)
    _check("m03:slots" in bd, "(3) falta m03:slots", fails)
    _check("dynamic_queries" in bd, "(3) 'dynamic_queries: X' no colapsó a 'dynamic_queries'", fails)
    _check("motor (sin tag)" in bd, "(3) 'call_flash_json' no cayó en 'motor (sin tag)'", fails)

    # ── (4) rótulo derivado del flag, nunca fijo ──
    _check(m03._SEEDREAM_SLOTS_MODEL_LABEL == ("Pro" if m03.SEEDREAM_SLOTS_USE_PRO else "Flash"),
           "(4) _SEEDREAM_SLOTS_MODEL_LABEL no deriva de SEEDREAM_SLOTS_USE_PRO", fails)
    _check(("Pro" if True else "Flash") == "Pro" and ("Pro" if False else "Flash") == "Flash",
           "(4) fórmula de derivación rota", fails)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] fluidificador→Flash+tb0, plumbing tb None/0, reporter por módulo, rótulo derivado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
