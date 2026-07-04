"""
test_module_cost_tracker_gemini.py — HANDOFF_133 (offline, sin llamar a Gemini).

Verifica la telemetría de costo por tokens:
  (a) track_gemini_response extrae los 3 conteos (in/out/thinking) y el modelo correcto.
  (b) el $ calculado == tokens × tarifa de config (thinking cobrado como output).
  (c) usage_metadata ausente NO rompe → tokens 0 + usage_ok=False (la llamada no se pierde).

Usa una instancia FRESCA de CostTracker (no toca el singleton global).

USO:
    python test_module_cost_tracker_gemini.py
"""
import sys

from cost_tracker import CostTracker, _gemini_service_name, _gemini_rates_for


class _UM:
    def __init__(self, pin, out, think):
        self.prompt_token_count = pin
        self.candidates_token_count = out
        self.thoughts_token_count = think


class _Resp:
    def __init__(self, um):
        self.usage_metadata = um


def _check(cond, msg, fails):
    if not cond:
        fails.append(msg)


def main() -> int:
    fails: list[str] = []

    # ── (a)+(b) Pro con usage conocido ──
    ct = CostTracker()
    ct.track_gemini_response(_Resp(_UM(1000, 2000, 8000)), "gemini-2.5-pro", "m03:slots")
    g = ct.get_gemini_summary()
    pro = g["by_model"].get("Gemini 2.5 Pro")
    _check(pro is not None, "(a) no se registró servicio 'Gemini 2.5 Pro'", fails)
    if pro:
        _check(pro["tokens_in"] == 1000, f"(a) tokens_in={pro['tokens_in']} != 1000", fails)
        _check(pro["tokens_out"] == 2000, f"(a) tokens_out={pro['tokens_out']} != 2000", fails)
        _check(pro["tokens_thinking"] == 8000, f"(a) tokens_thinking={pro['tokens_thinking']} != 8000", fails)
        # (b) $ esperado = in*rate_in + (out+think)*rate_out (thinking factura como output)
        r = _gemini_rates_for("gemini-2.5-pro")
        exp = round(1000 / 1e6 * r["input"] + (2000 + 8000) / 1e6 * r["output"], 6)
        _check(abs(pro["cost_usd"] - round(exp, 4)) < 1e-6,
               f"(b) costo {pro['cost_usd']} != esperado {round(exp,4)}", fails)

    # ── modelo distinto → servicio distinto (no hardcode) ──
    ct2 = CostTracker()
    ct2.track_gemini_response(_Resp(_UM(500, 300, 0)), "gemini-2.5-flash", "m01a")
    _check("Gemini 2.5 Flash" in ct2.get_gemini_summary()["by_model"],
           "(a) Flash no derivó a 'Gemini 2.5 Flash'", fails)
    _check(_gemini_service_name("gemini-2.5-flash") == "Gemini 2.5 Flash",
           "(a) _gemini_service_name mal derivado", fails)

    # ── (c) usage_metadata ausente → no rompe, tokens 0, usage_ok False ──
    ct3 = CostTracker()
    class _NoUM:  # respuesta sin usage_metadata
        pass
    ct3.track_gemini_response(_NoUM(), "gemini-2.5-pro", "rara")
    g3 = ct3.get_gemini_summary()
    _check(g3["totals"]["calls"] == 1, "(c) la llamada sin usage se perdió (no contada)", fails)
    _check(g3["totals"]["tokens_in"] == 0 and g3["totals"]["cost_usd"] == 0.0,
           "(c) llamada sin usage no quedó en 0 tokens/costo", fails)
    _check(g3["totals"]["usage_missing"] == 1, "(c) no se marcó usage_missing", fails)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] telemetría Gemini por tokens: conteos+modelo OK, $ == tokens×tarifa, "
          "usage ausente tolerado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
