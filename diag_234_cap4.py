# diag_234_cap4.py — Diagnóstico #234: por qué cap 4 cae a uniforme.
# NO toca fase2b. NO gasta API. NO renderiza. Solo lee datos reales.
import json, re
from pathlib import Path

TOPIC = "411bb0b4-7236-443e-82d2-44b952103ae2"
CAP = 4

script_path = Path(f"data/scripts/{TOPIC}.json")
ts_path = Path(f"output/audio/{TOPIC}/ch04_timestamps.json")

print("=" * 60)
print(f"DIAGNOSTICO #234 — cap {CAP} — topic {TOPIC[:8]}")
print("=" * 60)

# ---- 1. Cargar anchors del cap 4 desde el script final ----
script = json.loads(script_path.read_text(encoding="utf-8"))
chapters = script.get("chapters", [])
cap = None
for c in chapters:
    if c.get("chapter_number") == CAP or str(c.get("chapter_id")) == str(CAP):
        cap = c
        break
if cap is None:
    print(f"!! No encontre cap {CAP}. Caps disponibles:",
          [c.get("chapter_number") for c in chapters])
    raise SystemExit(1)

image_prompts = cap.get("image_prompts", [])
anchors = [ip.get("narration_anchor", "") for ip in image_prompts]
print(f"\n[A] Cap {CAP}: {len(anchors)} imagenes / anchors")
for i, a in enumerate(anchors):
    preview = a[:70].replace("\n", "\\n")
    print(f"    anchor[{i}]: '{preview}'{'...' if len(a) > 70 else ''}")

# ---- 2. Llamar a la FUNCION REAL de fase2b ----
print("\n[B] Llamando a la funcion REAL fase2b._compute_durations_from_anchors ...")
from fase2b import _compute_durations_from_anchors

# total_duration: lo sacamos del sync_map del cap
sm = json.loads(Path(f"output/audio/{TOPIC}/sync_map.json").read_text(encoding="utf-8"))
cap_meta = None
for cm in sm.get("chapters", []):
    if cm.get("id") in (f"ch{CAP:02d}", f"ch{CAP}", str(CAP)):
        cap_meta = cm
        break
total = float(cap_meta["duration_sec"]) if cap_meta else 0.0
print(f"    total_duration (sync_map): {total:.2f}s")

result = _compute_durations_from_anchors(anchors, ts_path, total)
if result is not None:
    print(f"    >>> RESULTADO: MATCHEA OK. {len(result)} durations.")
    print(f"        durations: {[round(d,2) for d in result]}")
    print(f"        suma: {sum(result):.2f}s vs total {total:.2f}s")
    print("\n    Si esto matchea, el cap 4 NO cae a uniforme con estos datos.")
    print("    => La premisa del backlog puede estar desactualizada. Reportar a Omar.")
    raise SystemExit(0)

print("    >>> RESULTADO: devolvio None => CAE A UNIFORME.")

# ---- 3. Replicar la secuencia de chequeos para ubicar CUAL fallo ----
print("\n[C] Replicando los chequeos del codigo real para ubicar el return None:")

words = json.loads(ts_path.read_text(encoding="utf-8"))
print(f"    words en timestamps: {len(words)}")

def _norm(tok):
    return re.sub(r"[^\w]", "", tok or "", flags=re.UNICODE).lower()

def _first_n_tokens(text, n=3):
    toks = [_norm(t) for t in text.split() if _norm(t)]
    return toks[:n]

word_norm = [_norm(w.get("word", "")) for w in words]

starts = []
cursor = 0
fail_reason = None
for ai, anchor in enumerate(anchors):
    needle = _first_n_tokens(anchor, n=3)
    if not needle:
        fail_reason = f"FALLA 1a: anchor[{ai}] sin tokens normalizables. anchor='{anchor[:50]}'"
        break
    found = -1
    for i in range(cursor, len(words) - len(needle) + 1):
        if word_norm[i:i + len(needle)] == needle:
            found = i
            break
    matched_by = "3-tokens"
    if found < 0:
        for i in range(cursor, len(words)):
            if word_norm[i] == needle[0]:
                found = i
                matched_by = "1-token-laxo"
                break
    if found < 0:
        fail_reason = (f"FALLA 1b: anchor[{ai}] NO matcheo ni 3-tok ni 1-tok.\n"
                       f"        needle={needle}\n"
                       f"        cursor estaba en word #{cursor} ('{word_norm[cursor] if cursor < len(word_norm) else 'EOF'}')")
        break
    starts.append(float(words[found].get("start", 0.0)))
    print(f"    anchor[{ai}] matcheo en word #{found} ({matched_by}) start={starts[-1]:.2f}s  needle={needle}")
    cursor = found + 1

if fail_reason:
    print(f"\n    >>> CAUSA: {fail_reason}")
    raise SystemExit(0)

# Chequeo de orden creciente
for i in range(1, len(starts)):
    if starts[i] <= starts[i - 1]:
        print(f"\n    >>> CAUSA: FALLA 2 (orden): starts[{i}]={starts[i]:.2f} <= starts[{i-1}]={starts[i-1]:.2f}")
        print(f"        starts completos: {[round(s,2) for s in starts]}")
        raise SystemExit(0)

# Chequeo de durations > 0.05
end_of_segment = total
bad = False
durs = []
for i in range(len(starts)):
    end = starts[i + 1] if i + 1 < len(starts) else end_of_segment
    d = end - starts[i]
    durs.append(d)
    if d <= 0.05:
        print(f"\n    >>> CAUSA: FALLA 3 (duracion): img[{i}] dur={d:.3f}s <= 0.05")
        print(f"        starts: {[round(s,2) for s in starts]}")
        bad = True
        break

if not bad:
    print("\n    >>> Los chequeos replicados PASAN, pero la funcion real dio None.")
    print("        Esto sugiere divergencia entre mi replica y el codigo real")
    print("        (o un path/parametro distinto). Pegar la funcion real a Claude.")
    print(f"        durations replicadas: {[round(d,2) for d in durs]}")