"""qa_form_markers.py — emisor COMPARTIDO de marcadores @@QAFORM@@ del form asistido.

Contrato chat 61 (LOCKEADO):
  - SOLO se emite con la env var QA_FORM seteada (modo form). Sin QA_FORM no se imprime
    nada → corrida por terminal byte-idéntica.
  - El marcador es 1 línea, JSON ASCII puro (ensure_ascii=True), con flush=True (Windows-safe).
  - Se emite SIEMPRE *antes* del input() del gate; el input()/parseo del gate NO se tocan.
  - El seam de respuesta sigue siendo window.qaFormAnswer({menu, action, value}) en el host.

Nota: fase1.py y niche_discoverer.py tienen copias locales HISTÓRICAS de este mismo molde
(no se refactorizan acá para no tocar código ya validado). El código NUEVO (m05_judge.py,
run_pipeline.py) usa ESTE módulo en vez de duplicar el molde.
"""
import json
import os

# Se lee una sola vez al importar (igual que las copias locales). El server lanza el
# subprocess con QA_FORM=1 en el env; la terminal pura no lo tiene → no se emite nada.
QA_FORM = bool(os.environ.get("QA_FORM"))


def emit_choice_marker(menu, prompt, options, *, default=None, body=None, payload=None):
    """Marcador GENÉRICO de choice (botones) — accept='key'.

    El form dibuja un botón por option; el `key` es exactamente lo que el input() del gate
    ya parsea (V/A/R/S, y/n/s, C, …). `payload` es DISPLAY-ONLY (lista de issues, topic_id,
    etc.): no cambia la acción (la respuesta sigue siendo la `key`).

    El caller decide si llamar (debe envolver en `if QA_FORM:`); igual chequeamos acá para
    que sea imposible emitir por accidente en terminal pura.
    """
    if not QA_FORM:
        return
    marker = {
        "menu": menu,
        "accept": "key",
        "prompt": prompt,
        "options": options,   # [{key, label, disabled?}]
        "default": default,
        "body": body,
    }
    if payload is not None:
        marker["payload"] = payload
    print("@@QAFORM@@ " + json.dumps(marker, ensure_ascii=True), flush=True)


# ── Marcador de COSTO (HANDOFF_133 · pedido Omar): línea aparte @@QAFORM_COST@@ que el
# server bucketea por la fase activa (RESEARCH/GUION/…) → el form muestra el $ Gemini
# sumando por etapa mientras corre. NO es un diálogo (no toca el gate). Solo con QA_FORM. ──
def emit_cost_marker(model, usd, tokens_in, tokens_out, tokens_thinking):
    if not QA_FORM:
        return
    marker = {
        "model": model,
        "usd": round(float(usd or 0.0), 6),
        "in": int(tokens_in or 0),
        "out": int(tokens_out or 0),
        "think": int(tokens_thinking or 0),
    }
    print("@@QAFORM_COST@@ " + json.dumps(marker, ensure_ascii=True), flush=True)
