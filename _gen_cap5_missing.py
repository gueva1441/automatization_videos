# _gen_cap5_missing.py — genera SOLO las 4 imágenes faltantes de cap5 (08,14,15,16)
# que el filtro de contenido de Flux (AP9/422) había rechazado. Usa los prompts ya parchados
# y el mismo seed-por-sujeto del pipeline. Escribe en el asset dir real (rellena los huecos).
import sys, json, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import asset_manager as am

VIDEO_ID = "91bea3b0-eb43-4797-a32d-90a45fccf1c8"
TARGETS = [8, 14, 15, 16]

d = json.load(open(f"data/scripts/{VIDEO_ID}.json", encoding="utf-8"))
ch = [c for c in d["chapters"] if c.get("chapter_number") == 5][0]
ips = ch["image_prompts"]

print(f"Generando {len(TARGETS)} imágenes faltantes de cap5 (ch05) — video {VIDEO_ID[:8]}")
print(f"use_ultra = {am._is_hook_chapter('ch05')} (ch05 no es hook → Flux Pro estándar)\n")

results = []
for n in TARGETS:
    item = ips[n - 1]
    prompt = item["prompt"]
    sref = item.get("subject_ref")
    seed = am._seed_for_subject(VIDEO_ID, sref)
    out = am._chapter_dir(VIDEO_ID, "ch05", "flux") / am._image_filename("ch05", n)
    print(f"[{n:02d}] subject_ref={sref} seed={seed}")
    print(f"     prompt: {prompt[:90]}...")
    t0 = time.time()
    try:
        meta = am._flux_generate_raw(prompt, out, use_ultra=False, seed=seed)
        dt = time.time() - t0
        ok = out.exists() and out.stat().st_size > 0
        print(f"     ✓ OK {meta.get('width')}x{meta.get('height')} nsfw={meta.get('nsfw_flag')} "
              f"({dt:.1f}s, {out.stat().st_size//1024} KB) → {out.name}\n")
        results.append((n, "ok"))
    except am.ContentRejectedError as e:
        print(f"     ✗ AÚN RECHAZADO por filtro (AP9): {str(e)[:120]}\n")
        results.append((n, "content_rejected"))
    except Exception as e:
        print(f"     ✗ ERROR: {type(e).__name__}: {str(e)[:120]}\n")
        results.append((n, "error"))

print("─" * 60)
oks = sum(1 for _, s in results if s == "ok")
print(f"RESULTADO: {oks}/{len(TARGETS)} generadas · " + " ".join(f"{n}:{s}" for n, s in results))
