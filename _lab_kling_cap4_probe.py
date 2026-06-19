# _lab_kling_cap4_probe.py - LAB (HANDOFF_76). Probe Kling o3 cap4 (Vesey) topic 0d63c6d3.
# 16:9 long, 2K. NO toca prod/m03. NO commit/version_stamp. _lab_kling/ gitignored. ASCII prints. Resumable.
import os, sys, json, time, urllib.request
import requests
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from config import APIConfig
# temp 0 deterministico: usamos el client del helper SIN tocar el helper (lab-only)
from gemini_helpers import _client, _cfg, _parse_with_retry
from google.genai import types

BASE = r"C:\CLAUDE_PROJECTS\automatization_videos"
TID  = "0d63c6d3-580c-4f28-b5f8-af258fc54929"
SCRIPT = os.path.join(BASE, "data", "scripts", f"{TID}.json")
OUT  = os.path.join(BASE, "_lab_kling", "0d63c6d3", "cap4", "v6")  # 76f: subfolder aparte (no pisa v5)
os.makedirs(OUT, exist_ok=True)

KEY  = APIConfig().fal_api_key
HEAD = {"Authorization": f"Key {KEY}", "Content-Type": "application/json"}
IMG_EP = "https://fal.run/fal-ai/kling-image/o3/text-to-image"
IMG_RES, ASPECT, IMG_COST = "2K", "16:9", 0.028
PROBE_IDX = 5  # img 6 [05] = "34 a la horca" -> probe de billing ANTES del batch

GEO_FACTS = ("Denmark Vesey was a free African-American man, a carpenter of great influence in 1820s "
             "Charleston; the 34 co-conspirators were enslaved and free Black men of the same era.")
ERA_HINT  = "1820s and 1880s American county jail (red brick + granite + period-correct ironwork)"

# ---- §3 ruleset (system_instruction del transform, tal cual el handoff) ----
SYS = """You rewrite ONE image prompt into a single dense Kling o3 (text-to-image) prompt in ENGLISH for a
faceless documentary YouTube channel about the Old City Jail in Charleston. Goal: MORE retentive and MORE
explicit (fear/mystery) while staying MONETIZABLE. You also emit light_mode. KEEP the beat; the
narration_anchor is the routing key and is NOT touched. Rewrite ONLY the prompt. Max 2500 chars.

FORMAT (decision A): dense descriptive PROSE (no CSV, no keyword soup). Anchor the subject/location EARLY
and clearly. Integrate materials/texture/clothing into the subject, then environment, then LIGHT, then the
STYLE ANCHOR at the END. Denser/longer than a Flux prompt. The aspect ratio does NOT go in the text
(describe "wide horizontal composition", never "16:9").

R1 - FAITHFUL & EXPLICIT + MONETIZATION CEILING (the core change): show literally what the anchor says,
not the washed metaphor. Where the old prompt emptied the event ("a lone object in a vast room"), RESTORE
the literal subject: execution/gallows -> a scaffold / a ROW of nooses at the scale of the anchor (mass =
many). Blood/violence in the anchor -> show it literal (a wall with dark dried blood), not ambiguous "brown
stains". CEILING (hard cap, not optional): show apparatus + scale + SUGGESTED aftermath -- NEVER lifeless
bodies in frame, never visible hanged people, never fresh graphic blood, never mutilation. Terror is built
from scale + light + EMPTY nooses + loaded LIVING faces, not from the body. Reason: YouTube policy + Kling
CAC filter (the 422/shadowban we avoid). Absorb m03 rule 11: illustrate the OUTCOME not the warning;
plurals (Vesey + 34) -> show several, not one.

R2 - RETENTION by rank (16:9): R1 = peak/hero, specific action, eyes/emotion as focus. R2 = the moment of
ACTION (struggle, raid, panic), dynamic not static. R3 = atmosphere/architecture BUT with ONE loaded focal
point -- never an empty plate. Dense texture (materials, weather, grime).
  SHOT SCALE (16:9) -- vary camera DISTANCE across the chapter; this governs framing distance and OVERRIDES
  rank for distance. Begin every prompt by stating the shot scale in words. DEFAULT to WIDE / EXTREME WIDE
  for beats of establishment, architecture, mass event, aftermath and landscape: the subject small inside a
  vast environment, showing SCALE and DEPTH and AIR (the whole jail, the full courtyard, the street, the
  horizon). Only emotional PEAKS that are ONE human emotion go MEDIUM/CLOSE (a single face, eyes/emotion as
  the subject). A deliberate texture detail (e.g. a blood-stained wall) may be a MEDIUM CLOSE-UP as the
  beat's single detail. GOLDEN RULE: place / event / scale -> open WIDE shot with lots of air; ONE human
  emotion -> medium/close. FORBIDDEN for the whole chapter to be medium/close -- WIDE shots must dominate.
  The mass-execution beat (is_execution_beat=true) is shown from a DISTANCE (extreme wide, low angle) so the
  scale of the many reads -- never a close-up of the apparatus. If the input gives a shot_scale_hint, you
  MUST compose at exactly that shot scale. Emit your chosen shot_scale.

R3 - LIGHT/HOUR by EVENT COHERENCE (not per loose anchor): beats narrating the SAME event share ONE
light_mode. Decide by the real event, not just the anchor sentence. Hard historical rule: the 1886
Charleston earthquake struck ~9:50 PM (night) -> the whole earthquake cluster = night. FOR THIS CHAPTER
(cap4) EVERY image = light_mode="night" (no day beats remain: the quake is night; the protagonist goes
night-accused). night = deep gloom; never inherited dusk/day. Always return light_mode="night".

R4 - HARD ERA (anti-medieval): anchor to an 1820s/1880s American county jail (red brick + granite + period
ironwork). Explicit time marker in EVERY prompt. Forbidden to drift to medieval (vaults, pointed arches,
dungeon, castle). Affirm the correct period; do not name the forbidden terms.

R5 - HUMAN + ETHNICITY: ethnicity integrated into the subject up front, period-correct, faithful to facts
(the protagonist is a free African-American carpenter). No whitewashing. Face to the front on R1.

R6 - NO TEXT, NO PROPER NAMES (reinforced): never legible text/signs/inscriptions (Kling tries to render
text). Also forbidden: literal dates ("April 26, 1986") AND any PROPER NAME OF A PERSON, including the
protagonist -- "Denmark Vesey" must NEVER appear written. Describe by role+aspect+era+ethnicity instead:
"an influential free African-American carpenter in his late 50s". Translate dates to era descriptors ("an
1820s scene"). Surfaces = smooth/worn, positive affirmation (Kling has no negative_prompt).

R7 - LOCATION CONTINUITY: the building/cell/courtyard reads as the SAME jail across images (same red brick
+ granite + octagonal tower descriptors).

R8 - DIVERSITY + SIGNATURE-OBJECT DISCIPLINE: vary angle/scale/subject; no N identical shots; ONE hero per
cluster. No undrawable metaphors ("sense of dread", "eerie silence") -> land them in concrete matter
(reddish glow, sunken eyes).
  SIGNATURE OBJECT (the execution apparatus: scaffold, gallows, nooses) appears ONLY in the beat whose
  anchor narrates the execution ACT ITSELF (prisoners being led to / standing at the gallows / hanged).
  CRITICAL: if an anchor only REFERENCES executions in the past tense or by their CONSEQUENCE (blood
  staining the walls, their memory, the aftermath, "the mass executions that...") it is NOT the execution
  beat -- show ONLY the consequence with ZERO scaffold/nooses/gallows anywhere in frame, not even in the
  background. All lead-up (a looming shadow, the heavy air of injustice, cruel repression), aftermath/
  atmosphere, and psychological beats show NO apparatus. Vary the subject instead: shackles bolted into
  stone, hands gripping iron bars, guards dragging a prisoner, a fearful crowd, a WALL WITH DARK DRIED
  BLOOD filling the frame as the sole dominant subject, an empty fog-filled courtyard, a terrified face.
  EXACTLY ONE beat in the whole chapter carries the apparatus; ZERO repetition of the execution motif.
  You are TOLD per item via is_execution_beat. If is_execution_beat=false, drawing ANY gallows, noose,
  scaffold, gibbet or hanging structure is STRICTLY FORBIDDEN -- not in the foreground, not in the
  background, not as a silhouette or distant hint. If is_execution_beat=true, this is the single beat that
  features the full apparatus (massive scaffold, a row of empty nooses, low angle, guards in silhouette,
  no bodies).
  DE-DUP OF ANY SIGNATURE MOTIF (76e FIX2): the one-owner rule applies to EVERY signature image, not only
  the apparatus. The blood-stained wall is one such motif: it is owned ONLY by is_blood_wall_beat=true. If
  is_blood_wall_beat=false, a wall covered in dark dried blood as the dominant subject is FORBIDDEN -- pick
  a different subject (shackles bolted into stone, hands gripping iron bars, an oppressive crowded
  interior). One owner per motif; never repeat the same signature image across two beats.

R9 - DO NOT WRITE A STYLE/LIGHTING/FILM TAIL: end your prompt at the scene + composition. Do NOT append
film-stock, grain, palette, or lighting descriptors -- the harness appends the house style tail. For night
beats keep the mood murky/decayed; for a free-life day beat keep it dignified and naturally lit; for a
calm-before-disaster dusk beat keep the last fading light. Never write a clean dramatic key.

FIX3 SUBJECT_STATE (76e, deterministic flag per person beat):
- subject_state=free -> a DIGNIFIED FREE person shown in DAYLIGHT at their trade/life: e.g. a free
  African-American carpenter in his ~50s, period 1820s workwear (linen shirt, canvas work apron), in or
  beside his carpentry workshop with tools and timber, dignified expression with quiet weight. ABSOLUTELY
  NO iron bars, NO cell, NO prison stripes, NO shackles. This is the protagonist's free life.
- subject_state=accused -> the accused in a tense interior (no prison stripes; 1820s plain clothing).
- subject_state=imprisoned (or unstated for a prisoner beat) -> a prisoner in plain coarse 1820s clothing.
- ANTI-ANACHRONISM (hard): striped prison uniforms are FORBIDDEN -- anachronistic for the 1820s and wrong
  for a free man. Plain period clothing only.

FIX4 BEAT_MOMENT (76e, render the EXACT moment of the anchor; never jump to aftermath or swap the subject):
- beat_moment=calm_before -> the GREEN CALM BEFORE the disaster (76f aesthetic carve-out). A LUSH, GREEN,
  LIVING natural landscape at WARM GOLDEN-HOUR light, trees and vegetation alive, calm and peaceful, mildly
  saturated and warm -- the OPPOSITE of the cold murky decay of the dread beats. Include ONE subtle
  foreboding cue as a small detail WITHIN the living scene (a distant flock of birds fleeing on the
  horizon, an unnatural stillness, a faint hairline crack just beginning in the soil) -- the omen is a
  detail, NOT the subject. NO cold monochrome, NO grime/decay, NO arid dust-plain (that is aftermath), NO
  ruins, NOT the earthquake itself. The green-calm -> disaster contrast is the retention lever.
- beat_moment=street_disaster -> the DEVASTATED STREET itself: period buildings collapsing along a
  cobblestone street with period people fleeing in the open, debris across the street -- NOT just one
  building facade. Show the street and its depth.
- beat_moment=empty_courtyard -> an EMPTY interior jail courtyard pulled back to EXTREME WIDE: tall
  red-brick and granite perimeter walls receding into fog, oppressive emptiness, silence and scale at
  night. NOT a barred gate, NOT a cage, NOT a close-up of bars -- the subject is the void and the scale.

Output JSON only: {"kling_prompt": "...", "light_mode": "night", "shot_scale": "extreme_wide|wide|medium|close|detail"}."""

SCHEMA = {"type": "object", "properties": {
    "kling_prompt": {"type": "string"},
    "light_mode": {"type": "string", "enum": ["night", "day"]},
    "shot_scale": {"type": "string", "enum": ["extreme_wide", "wide", "medium", "close", "detail"]}},
    "required": ["kling_prompt", "light_mode", "shot_scale"]}

# 76d/76e R9 ANTI-PLASTICO — tail por (light_mode, dial). Apendizado por el harness.
_AP = ("heavy organic analog film grain, coarse tactile surface texture, degraded emulsion with dust specks "
    "and fine imperfections, rough non-digital finish -- break any smooth plastic AI-rendered look")
# NIGHT STRONG: wides/arquitectura/evento/detalle.
TAIL_NIGHT_STRONG = (_AP + "; cold near-monochrome desaturated palette with a faint sickly cast, murky "
    "underexposed gloom, crushed deep shadows swallowing detail, oppressive claustrophobic decay, faint "
    "dirty haze, low murky light (not a clean dramatic key), period-correct documentary realism, wide "
    "horizontal composition")
# NIGHT MODERATE: rostro R1/R2. FIX1 76e: cara/ojos +15-20% expuestos, grano SOLO en el entorno.
TAIL_NIGHT_MOD = ("organic analog film grain and tactile surface texture on the surroundings (bars, walls, "
    "background) to break any smooth plastic AI-rendered look, BUT the face and eyes are clearly lifted out "
    "of shadow, well exposed (~15-20% brighter than the murky surroundings), sharp, clean and fully legible "
    "-- never bury the face in grain or darkness; cold desaturated palette with a faint sickly cast, murky "
    "underexposed environment, oppressive claustrophobic decay, period-correct documentary realism, "
    "horizontal composition")
# DAY MODERATE (FIX3 a04 carpintero libre): luz diurna natural, digno, cara legible, textura suave.
TAIL_DAY_MOD = ("organic analog film grain and tactile surface texture to break any smooth plastic "
    "AI-rendered look, but the face and eyes stay sharp, well lit and fully legible; natural overcast "
    "period daylight, dignified and naturalistic, cold slightly desaturated palette, documentary realism, "
    "horizontal composition")
TAIL_DAY_STRONG = (_AP + "; natural overcast period daylight, cold desaturated palette, faint dirty haze, "
    "period-correct documentary realism, wide horizontal composition")
# GOLDEN (76f FIX a09 calma-antes): carve-out ESTETICO -> verde/vivo/golden-hour, NO frio/decay/ruina.
TAIL_GOLDEN = ("lush green living landscape, warm golden-hour light, calm peaceful nature, gentle haze, "
    "faint organic film grain, period-correct documentary realism, wide horizontal composition")

def anti_plastic_dial(shot_scale):
    return "moderate" if shot_scale in ("close", "medium") else "strong"

def pick_tail(light_mode, dial):
    if light_mode == "day":    return TAIL_DAY_MOD if dial == "moderate" else TAIL_DAY_STRONG
    if light_mode == "golden": return TAIL_GOLDEN   # 76f: calma-antes verde/vivo
    return TAIL_NIGHT_MOD if dial == "moderate" else TAIL_NIGHT_STRONG

def with_tail(scene, dial, light_mode):
    s = (scene or "").strip().rstrip(".")
    return f"{s}. {pick_tail(light_mode, dial)}"[:2500]

def compute_flags(anchor):
    al = (anchor or "").lower()
    subject_state = ("free" if "libre" in al else
                     ("accused" if ("acusad" in al or "juicio" in al or "testimon" in al) else ""))
    beat_moment = ("calm_before" if ("la tierra" in al and "rebel" in al) else
                   ("street_disaster" if ("terremoto" in al or "tembl" in al) else
                    ("empty_courtyard" if "tragó" in al or "trago" in al else "")))  # 76f a08
    return {"is_execution_beat": "horca" in al, "is_blood_wall_beat": "sangre" in al,
            "subject_state": subject_state, "beat_moment": beat_moment}

def light_for(flags):
    if flags["subject_state"] == "free":      return "day"     # FIX3: a04 vida libre
    if flags["beat_moment"] == "calm_before": return "golden"  # 76f: calma-antes verde/golden-hour
    return "night"

def transform(prompt_actual, anchor, rank, flags, shot_hint=""):
    # 76f: desanclamos del original (viene night+carcel) para que respeten el carve-out del beat.
    if flags.get("beat_moment") == "calm_before":
        prompt_actual = ("(IGNORE any prior night/jail/arid framing -- compose FRESH per beat_moment="
                         "calm_before: a LUSH GREEN LIVING landscape at warm GOLDEN HOUR, trees alive, "
                         "calm peaceful nature; include ONE subtle foreboding cue as a small background "
                         "detail (a distant flock of birds fleeing / a faint hairline crack just beginning "
                         "in the soil). NO jail, NO buildings, NO arid dust-plain, NO ruins, NOT the "
                         "earthquake itself -- the green calm BEFORE.)")
    elif flags.get("beat_moment") == "empty_courtyard":
        prompt_actual = ("(IGNORE any prior close/barred framing -- compose FRESH per beat_moment="
                         "empty_courtyard: an EMPTY interior jail courtyard pulled back to EXTREME WIDE, "
                         "tall red-brick and granite walls receding into fog, oppressive emptiness and "
                         "scale, night. NO barred gate, NO cage, NO close-up of bars as the subject.)")
    hint_line = (f"shot_scale_hint: {shot_hint} (MANDATORY -- compose at exactly this shot scale)\n"
                 if shot_hint else "")
    ss_line = (f"subject_state: {flags['subject_state']}\n" if flags["subject_state"] else "")
    bm_line = (f"beat_moment: {flags['beat_moment']}\n" if flags["beat_moment"] else "")
    user = (f"emotional_rank: {rank}\n"
            f"is_execution_beat: {str(flags['is_execution_beat']).lower()}\n"
            f"is_blood_wall_beat: {str(flags['is_blood_wall_beat']).lower()}\n"
            f"{ss_line}{bm_line}{hint_line}"
            f"narration_anchor (ES, NO la traduzcas, es la llave de ruteo): {anchor}\n"
            f"era_hint: {ERA_HINT}\n"
            f"geo_ethnicity_facts: {GEO_FACTS}\n"
            f"CURRENT PROMPT (Flux, washed):\n{prompt_actual}")
    def _get():
        resp = _client.models.generate_content(
            model=_cfg.gemini_model, contents=user,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", system_instruction=SYS,
                response_schema=SCHEMA, temperature=0.0))
        return resp.text
    return _parse_with_retry(_get)

# ---------- Paso A: leer cap4 vivo ----------
d = json.load(open(SCRIPT, encoding="utf-8"))
cap4 = d["chapters"][3]
assert cap4["chapter_number"] == 4
items = cap4["image_prompts"]
assert len(items) == 16, f"esperaba 16, hay {len(items)}"
print(f"cap4 (Vesey): {len(items)} imagenes, render_engine={cap4.get('render_engine')}")

# ---------- Paso B: transform (cache) ----------
TPATH = os.path.join(OUT, "transforms.json")
tr = json.load(open(TPATH, encoding="utf-8")) if os.path.exists(TPATH) else []
trmap = {r["img_index"]: r for r in tr}
print(f"\nTRANSFORM (temp0): {len(trmap)} cacheados de 16")
for i, ip in enumerate(items):
    if i in trmap and trmap[i].get("kling_prompt"): continue
    anchor = ip.get("narration_anchor", "")
    flags = compute_flags(anchor)
    lm = light_for(flags)  # 76e: free->day, calm_before->dusk, else night
    ss, dial = "wide", "strong"
    shot_hint = "wide" if i in (1, 4) else ""  # 76d: [01][04] -> wide (eran medium en v3)
    if flags["beat_moment"] == "empty_courtyard": shot_hint = "extreme_wide"  # 76f a08: pull-back
    try:
        out = transform(ip["prompt"], anchor, ip.get("emotional_rank", "R2"), flags, shot_hint)
        scene = (out.get("kling_prompt") or "").strip()
        ss = shot_hint or (out.get("shot_scale") if out.get("shot_scale") in ("extreme_wide","wide","medium","close","detail") else "wide")
        dial = anti_plastic_dial(ss)  # moderado en close/medium (rostros), fuerte en wides/detail
        kp = with_tail(scene, dial, lm) if scene else ""
    except Exception as e:
        kp = ""; print(f"  [{i:02d}] transform ERR: {type(e).__name__}: {e}")
    rec = {"img_index": i, "emotional_rank": ip.get("emotional_rank"), "narration_anchor": anchor,
           "light_mode": lm, "shot_scale": ss, "anti_plastic_dial": dial,
           "subject_state": flags["subject_state"], "beat_moment": flags["beat_moment"], "kling_prompt": kp}
    trmap[i] = rec
    tr = [trmap[k] for k in sorted(trmap)]
    json.dump(tr, open(TPATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"  [{i:02d}] rank={rec['emotional_rank']} light={lm} shot={ss} dial={dial} ss={flags['subject_state'] or '-'} bm={flags['beat_moment'] or '-'} -> {len(kp)} chars")
print(f"TRANSFORM listo: {sum(1 for r in trmap.values() if r['kling_prompt'])}/16 -> {TPATH}")
if "transform_only" in sys.argv:
    print("transform_only -> stop."); sys.exit(0)

# ---------- Paso C: generar (probe img[05] primero) ----------
def kling_image(prompt, dst, max_retries=2):
    n422 = 0; raw = None; t0 = time.time()
    for attempt in range(max_retries + 1):
        try:
            r = requests.post(IMG_EP, headers=HEAD, json={
                "prompt": prompt[:2500], "resolution": IMG_RES, "aspect_ratio": ASPECT,
                "output_format": "png", "result_type": "single", "num_images": 1}, timeout=240)
            if raw is None: raw = {"http": r.status_code, "body": r.text[:400]}
            if r.status_code == 200:
                url = (r.json().get("images") or [{}])[0].get("url")
                if url:
                    urllib.request.urlretrieve(url, dst)
                    return ("ok" if n422 == 0 else "422_retry_ok"), n422, int((time.time()-t0)*1000), raw
            elif r.status_code == 422:
                n422 += 1
            time.sleep(1.0)
        except Exception as e:
            if raw is None: raw = {"exc": f"{type(e).__name__}: {e}"[:300]}
            time.sleep(1.0)
    return "FAILED", n422, int((time.time()-t0)*1000), raw

LOG = os.path.join(OUT, "run_log.json")
log = json.load(open(LOG, encoding="utf-8")) if os.path.exists(LOG) else {"images": [], "chapter": {}}
done = {r["img_index"] for r in log["images"] if r.get("http_status") in ("ok", "422_retry_ok")}

def dst_for(i): return os.path.join(OUT, f"cap4_img{i:02d}.png")
def put(rec):
    log["images"] = [r for r in log["images"] if r["img_index"] != rec["img_index"]] + [rec]
    log["images"].sort(key=lambda r: r["img_index"])
    json.dump(log, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def gen_one(i):
    rec0 = trmap[i]; kp = rec0["kling_prompt"]
    meta = {"emotional_rank": rec0["emotional_rank"], "narration_anchor": rec0["narration_anchor"],
            "light_mode": rec0["light_mode"], "shot_scale": rec0.get("shot_scale"),
            "anti_plastic_dial": rec0.get("anti_plastic_dial"), "subject_state": rec0.get("subject_state"),
            "beat_moment": rec0.get("beat_moment")}
    if not kp:
        put({"img_index": i, **meta, "kling_prompt": "", "http_status": "FAILED", "n_422": 0,
             "cost_real": 0, "latency_ms": 0, "note": "transform vacio", "file": None}); return "FAILED", 0
    st, n4, lat, raw = kling_image(kp, dst_for(i))
    put({"img_index": i, **meta, "kling_prompt": kp, "http_status": st, "n_422": n4,
         "cost_real": IMG_COST if st != "FAILED" else 0, "latency_ms": lat,
         "file": os.path.relpath(dst_for(i), BASE) if st != "FAILED" else None,
         "raw_first": raw if i == PROBE_IDX else None})
    return st, n4

if PROBE_IDX not in done or not os.path.exists(dst_for(PROBE_IDX)):
    print(f"\n=== PROBE billing: img[{PROBE_IDX:02d}] '34 a la horca' ===")
    print("prompt:", trmap[PROBE_IDX]["kling_prompt"][:200])
    st, n4 = gen_one(PROBE_IDX)
    pr = [r for r in log["images"] if r["img_index"] == PROBE_IDX][0]
    print(f"-> {st} n_422={n4} latency={pr['latency_ms']}ms")
    print(f"   raw_first: {json.dumps(pr.get('raw_first'), ensure_ascii=False)[:300]}")
    print(f"   billing: claim ${IMG_COST}/img (no hay campo de costo en la respuesta -> confirmar delta dashboard fal)")
    if st == "FAILED":
        print("PROBE FAILED -> STOP, NO batcheo. Dump arriba."); sys.exit(1)
    print("PROBE OK -> batcheo el resto.")
else:
    print(f"\nimg[{PROBE_IDX:02d}] ya hecho, skip probe.")

# ---------- batch resto ----------
print("\n=== BATCH resto de cap4 (2K, 16:9) ===")
for i in range(16):
    if i == PROBE_IDX: continue
    if i in done and os.path.exists(dst_for(i)): continue
    st, n4 = gen_one(i)
    print(f"  [{i:02d}] rank={trmap[i]['emotional_rank']} light={trmap[i]['light_mode']} -> {st} (n422={n4})")
    time.sleep(0.3)

# ---------- agregados ----------
imgs = log["images"]
ok = sum(1 for r in imgs if r["http_status"] in ("ok", "422_retry_ok"))
n422 = sum(r.get("n_422", 0) for r in imgs)
failed = sum(1 for r in imgs if r["http_status"] == "FAILED")
log["chapter"] = {"total": 16, "ok": ok, "failed": failed, "n_422_events": n422,
                  "rate_422": round(n422 / max(1, sum(1 for r in imgs)), 3),
                  "cost_total_claim": round(ok * IMG_COST, 3)}
json.dump(log, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n===== RESUMEN cap4 =====")
print(f"  ok={ok}/16  FAILED={failed}  eventos_422={n422}  rate_422={log['chapter']['rate_422']}")
from collections import Counter
print("  light_mode:", dict(Counter(r["light_mode"] for r in imgs)))
print(f"  billing (claim): ~${ok*IMG_COST:.2f}  (confirmar delta real en dashboard fal)")
print(f"  carpeta: {OUT}")

# ---------- gallery.html ----------
def esc(s): return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
byidx = {r["img_index"]: r for r in log["images"]}
cards = ""
for i in range(16):
    r = byidx.get(i, {})
    f = f"cap4_img{i:02d}.png"
    exists = os.path.exists(os.path.join(OUT, f))
    media = f'<img src="{f}" loading="lazy">' if exists else f'<div class="no">{r.get("http_status","?")}</div>'
    badge = "R1" if r.get("emotional_rank") == "R1" else r.get("emotional_rank", "")
    cards += (f'<div class="card">{media}<div class="meta"><b>[{i:02d}]</b> '
              f'<span class="r r{esc(badge)}">{esc(badge)}</span> '
              f'<span class="sc">{esc(r.get("shot_scale",""))}</span> '
              f'<span class="ap">tex:{esc(r.get("anti_plastic_dial",""))}</span> '
              f'<span class="l">{esc(r.get("light_mode",""))}</span> '
              f'<span class="st">{esc((r.get("subject_state") or "") + ("/"+r.get("beat_moment") if r.get("beat_moment") else ""))}</span> '
              f'<span class="s">{esc(r.get("http_status",""))}</span></div>'
              f'<div class="a">{esc((r.get("narration_anchor") or "")[:160])}</div></div>')
agg = log.get("chapter", {})
html = ('<!doctype html><meta charset=utf-8><title>cap4 Kling v2 (76b)</title><style>'
    'body{background:#0c0c0d;color:#ddd;font:13px system-ui;margin:18px}h1{font-size:16px}'
    '.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px}'
    '.card{background:#161617;border-radius:8px;overflow:hidden}.card img{width:100%;display:block}'
    '.no{height:190px;display:flex;align-items:center;justify-content:center;color:#c66}'
    '.meta{padding:7px 10px 3px}.r{padding:1px 6px;border-radius:4px;font-size:11px;background:#333}'
    '.rR1{background:#a32d2d;color:#fff}.sc{color:#e0b050;margin-left:5px}.ap{color:#c98bdb;margin-left:5px}.l{color:#7fb3ff;margin-left:5px}.st{color:#d98a5a;margin-left:5px}.s{color:#1d9e75;margin-left:5px}'
    '.a{padding:2px 10px 10px;color:#9a9a9a;font-size:11px;line-height:1.4}</style>'
    f'<h1>cap4 (Vesey) Kling o3 v2 — 76b — ok={agg.get("ok")}/16 · rate_422={agg.get("rate_422")} · '
    f'all night · claim ${agg.get("cost_total_claim")}</h1><div class="grid">{cards}</div>')
open(os.path.join(OUT, "gallery.html"), "w", encoding="utf-8").write(html)
print(f"  gallery: {os.path.join(OUT,'gallery.html')}")
