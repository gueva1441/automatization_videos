"""
LAB CHAT 26 v5 STRESS TEST — Narracion inventada (Crisis Misiles Cuba 1962).

Trampas embebidas para validar pipeline v5 con topic distinto a Pripyat:
- Acronimos militares (B-59, T-5, Foxtrot, CO2) → trampa del acronimo
- Texto pronunciado en cirilico ("Nyet") → anti text bleed
- Año 1962 (no 1986) → anti-modernidad debe adaptarse
- Submarino soviético (contexto cultural distinto)
- Metaforas fisicas ("destino pendia de un hilo", "navegaba ciego")
- Datos numericos (48 horas, 50 grados)
- Nombres propios sin descripcion fisica (Savitsky, Maslennikov, Arkhipov)
- Intent shock SIN explosion (decision humana, tension interna)
- Anacronismo (1962 vs documentos desclasificados 2002)
"""

import json
import pathlib
import time
import requests
from google import genai
from google.genai import types
from config import APIConfig

# ============================================================
# CONFIG
# ============================================================
OUTPUT_DIR = pathlib.Path("lab_output_chat26_v5_stress")
OUTPUT_DIR.mkdir(exist_ok=True)

NICHO = "dark history / mystery documentary"
FORMATO = "vertical Shorts/TikTok 1080x1920, retencion agresiva (3s decision window)"
AUDIENCIA = "18-45, fans de Netflix dark docs, true crime, mystery"

CHARS_PER_IMAGE = 150
MIN_IMAGES_FLUX = 6
MAX_IMAGES_FLUX = 12

# Narracion INVENTADA con trampas
FAKE_NARRATION = """La noche del 14 de octubre de 1962, en lo profundo del Mar Caribe, el destino del mundo entero pendía de un solo hilo. El submarino soviético B-59, tipo Foxtrot, navegaba ciego bajo cargas de profundidad lanzadas por destructores estadounidenses. El capitán Valentin Savitsky, agotado tras semanas sin contacto con Moscú, creyó que la Tercera Guerra Mundial había estallado. Su torpedo nuclear T-5, con potencia equivalente a Hiroshima, esperaba la orden. Bastaba con que tres oficiales votaran sí: Savitsky dijo sí. El político Maslennikov dijo sí. Pero el segundo al mando, Vasili Arkhipov, dijo no. Una sola palabra rusa, "Nyet", cambió la historia. Lo que nadie sabía: documentos desclasificados en 2002 revelaron que el sistema de ventilación del submarino llevaba 48 horas roto, las temperaturas superaban los 50 grados, y la mitad de la tripulación había perdido el conocimiento por intoxicación de CO2. ¿Cómo se mide el valor de un hombre que dice no cuando todos gritan sí?"""

FAKE_DURATION = 85.0
FAKE_INTENT = "shock"

cfg = APIConfig()
client = genai.Client(api_key=cfg.gemini_api_key)

print("=" * 70)
print("LAB v5 STRESS TEST — Narracion inventada Crisis Misiles Cuba 1962")
print(f"Caracteres: {len(FAKE_NARRATION)} | Duracion simulada: {FAKE_DURATION}s")
print("=" * 70)

# ============================================================
# ETAPA 0 — ESTRATEGIA DE RETENCION
# ============================================================
ESTRATEGIA_SYSTEM = """Sos consultor de estrategia visual para canales de YouTube/TikTok verticales.

Proponé 3 ESTRATEGIAS de retencion visual distintas para definir identidad del canal en
este nicho. Cada estrategia debe servir para 50+ videos del mismo nicho.

OUTPUT JSON array de 3 objetos:
[
  {
    "nombre": "string corto (2-3 palabras)",
    "descripcion": "1 frase de que sensacion visual produce",
    "audiencia_target": "que tipo de viewer le funciona mejor",
    "que_retiene_el_ojo": "que elementos visuales fuerzan al viewer a seguir mirando",
    "referencias": "canales/peliculas/fotografos que usan esta estrategia",
    "trade_off": "que sacrifica esta estrategia"
  }
]

Las 3 deben ser distintas entre si. Solo JSON.
"""

estrategia_user = f"""NICHO: {NICHO}
FORMATO: {FORMATO}
AUDIENCIA: {AUDIENCIA}

Propone 3 estrategias de retencion visual para definir identidad permanente del canal."""

print("\n=== ETAPA 0 — Estrategia de Retencion ===\n")
resp = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=ESTRATEGIA_SYSTEM,
        response_mime_type="application/json",
    ),
    contents=estrategia_user,
)
estrategias = json.loads(resp.text)

for i, e in enumerate(estrategias, 1):
    print(f"[{i}] {e['nombre']}")
    print(f"    {e['descripcion']}")
    print(f"    Audiencia: {e['audiencia_target']}")
    print(f"    Retencion: {e['que_retiene_el_ojo']}")
    print(f"    Refs: {e['referencias']}")
    print(f"    Trade-off: {e['trade_off']}")
    print()

while True:
    choice = input("Elegi estrategia [1/2/3]: ").strip()
    if choice in ("1", "2", "3"):
        break
ESTRATEGIA = estrategias[int(choice) - 1]
print(f"\n✓ Estrategia elegida: {ESTRATEGIA['nombre']}\n")

# ============================================================
# ETAPA 1 — DIRECTOR DE ARTE
# ============================================================
DIRECTOR_SYSTEM = """Sos Director de Arte para canales verticales de dark history.

Dada una estrategia de retencion, proponé 3 opciones de Ancla Global que la implementan.

Ancla Global = string en INGLES TECNICO fijo que define identidad visual permanente del nicho.
- Define UNICAMENTE: camera + film type + base lighting + palette + grain/texture
- NO incluye sujetos, personajes, acciones, epocas especificas
- Termina con " -- "
- Max 220 caracteres
- 3 opciones distintas entre si

OUTPUT JSON array de 3 strings. Solo JSON.
"""

director_user = f"""ESTRATEGIA elegida:
{json.dumps(ESTRATEGIA, ensure_ascii=False)}

NICHO: {NICHO}
FORMATO: {FORMATO}

Proponé 3 opciones de Ancla Global en ingles tecnico."""

print("=== ETAPA 1 — Director de Arte ===\n")
resp = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=DIRECTOR_SYSTEM,
        response_mime_type="application/json",
    ),
    contents=director_user,
)
anchors = json.loads(resp.text)

for i, a in enumerate(anchors, 1):
    print(f"[{i}] {a}\n")

while True:
    choice = input("Elegi ancla [1/2/3]: ").strip()
    if choice in ("1", "2", "3"):
        break
ANCLA_GLOBAL = anchors[int(choice) - 1]
print(f"\n✓ Ancla elegida: {ANCLA_GLOBAL}\n")

(OUTPUT_DIR / "nicho_identity.json").write_text(json.dumps({
    "nicho": NICHO,
    "estrategia_opciones": estrategias,
    "estrategia_elegida": ESTRATEGIA,
    "ancla_opciones": anchors,
    "ancla_elegida": ANCLA_GLOBAL,
}, indent=2, ensure_ascii=False), encoding="utf-8")

# ============================================================
# ETAPA 2 — TRADUCTOR LITERAL v5
# ============================================================
TRADUCTOR_SYSTEM = """You are a Literal Translator. You convert Spanish narrative prose into pure
physical matter prompts for Flux 2 Pro, optimized for vertical TikTok/Shorts retention.

CRITICAL — OUTPUT LANGUAGE:
ALL slots MUST be in ENGLISH TECHNICAL language. Flux thinks in English. If you write
Spanish in any slot, Flux will render Latin script gibberish on surfaces in the image.
Read the narration in Spanish for context, but emit JSON strictly in English.

OUTPUT: JSON array of N objects (N is given by the user), each with 3 slots:

{
  "sujeto_fisico": "WHAT physical matter appears, in English. NO camera angles, NO lighting,
   NO style descriptors. ONLY matter. If human subject: ALWAYS include an explicit action verb
   (looking, holding, gripping, turning, writing, kneeling, etc.). Static museum-photo subjects
   are forbidden.",
  "anclas_temporales_o_tecnicas": "1 to 3 highly specific objects that anchor era/culture/context,
   in English. DESCRIBE objects PHYSICALLY, not by model acronym. Bad: 'IKS-A dosimeter'.
   Good: 'olive green metal handheld dosimeter with analog needle dial'. Bad: 'ZIL-131 truck'.
   Good: 'heavy 1960s Soviet military truck with canvas covered bed and round headlights'.",
  "modificador_de_escena": "OPTIONAL. Max 4 words. Local atmospheric condition only
   ('dust floating', 'thick fog', 'wet asphalt'). Empty string if none applies."
}

HARD RULES:

1. ANTI-READABLE-TEXT (BY DEFAULT):
   For ANY surface that could plausibly have text (walls, paper, blueprints, control panels,
   computer screens, billboards, signs, vehicles, doors, lab equipment, books, documents,
   uniforms with patches), append to sujeto_fisico: "no readable text, no visible letters,
   no inscriptions, no signage, no labels".
   EXCEPTION: only include readable text if the narration EXPLICITLY requires a specific
   historical inscription. In that case, specify the language.

2. ANTI-ACRONYM (CRITICAL):
   NEVER use letter/number model codes in any slot output (no "IKS-A", "ZIL-131", "B-59",
   "T-5", "GP-5", "AK-47", "SOMZ-55"). Flux will draw them as text.
   ALWAYS describe the object physically by appearance (materials, shape, color, era cues).
   The narration may mention acronyms — your job is to translate them to physical description.

3. ANTI-MODERNITY (CRITICAL):
   Identify the year/era from the narration and anchor every physical detail to that period.
   Forbidden modern defaults Flux tends to insert (regardless of era):
   - Modern polycarbonate / plastic items where period materials existed
   - Modern synthetic uniforms / N95 masks / contemporary PPE
   - Modern radios, phones, vehicles
   When in doubt, append: "period-correct [YEAR] equipment only, no modern materials,
   no plastic where leather/canvas/metal belongs".

4. ANTI-422 (safety filter avoidance):
   FORBIDDEN: shrapnel, colossal explosion, violent expulsion, destructive force, blood,
   corpses, bodies, gore, massacre.
   USE INSTEAD: scattered industrial materials, structural displacement, kinetic impact,
   concrete debris, displaced metal fragments, immobile figures.

5. ANTI-LITERALITY (physical metaphors → real event):
   - "destino pendia de un hilo" ≠ literal thread. Translate to the real tension scene.
   - "navegaba ciego" ≠ blind navigation. Translate to instruments / dark interior.
   - Identify the metaphor → identify the underlying physical event → describe THAT event.

6. ANTI-ABSTRACT-ROLES:
   FORBIDDEN: "captain", "officer", "soldier", "scientist", "engineer" without physical
   description.
   REQUIRED: physical appearance (clothing material, age, expression, action).
   Bad: "Captain Savitsky in submarine"
   Good: "Mid-forties man in dark wool Soviet naval uniform with brass buttons, sweating,
   gripping a brass periscope handle, jaw clenched"

7. ANTI-SPOKEN-TEXT:
   If narration mentions a spoken word (e.g. "Nyet", "Stop", a name), do NOT render the
   word as visible text. Describe the speaker physically saying it: "older man in Soviet
   naval officer cap, eyes closed, lips parted mid-word, deep furrow on brow".

8. RETENTION FOR VERTICAL FORMAT (TikTok/Shorts, 3s decision window):
   - Sujeto with dense visual texture
   - Clear focal point (one dominant subject)
   - Tension/action visible — human subjects MUST be doing something specific
   - Compositions the eye processes fast

9. DIVERSITY across the N prompts:
   Each must describe DIFFERENT subject matter. No near-identical images.

JSON only. No markdown.
"""

print("=" * 70)
print("ETAPA 2 — Traductor Literal v5 (STRESS TEST)")
print("=" * 70)

all_prompts_meta = []

n_imgs = max(MIN_IMAGES_FLUX, min(MAX_IMAGES_FLUX, round(len(FAKE_NARRATION) / CHARS_PER_IMAGE)))

print(f"\n--- CAP FAKE (Crisis Misiles Cuba 1962) ---")
print(f"  Duracion simulada: {FAKE_DURATION}s | Narracion: {len(FAKE_NARRATION)} chars")
print(f"  n_images: {n_imgs} | Ritmo: {FAKE_DURATION/n_imgs:.1f}s/img")

user_prompt = f"""Narration (Spanish, for context only — emit JSON in English):

{FAKE_NARRATION}

Generate {n_imgs} prompts as JSON array. JSON only, no markdown."""

resp = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=TRADUCTOR_SYSTEM,
        response_mime_type="application/json",
    ),
    contents=user_prompt,
)
beats = json.loads(resp.text)
print(f"  Beats generados: {len(beats)}")

for idx, beat in enumerate(beats, 1):
    mod = beat.get("modificador_de_escena", "").strip()
    flux_prompt = (
        ANCLA_GLOBAL
        + beat["sujeto_fisico"]
        + ", " + beat["anclas_temporales_o_tecnicas"]
        + (", " + mod if mod else "")
    )
    all_prompts_meta.append({
        "cap": "fake_cuba_1962",
        "intent": FAKE_INTENT,
        "img_idx": idx,
        "beat": beat,
        "flux_prompt_final": flux_prompt,
    })

(OUTPUT_DIR / "beats_and_prompts.json").write_text(
    json.dumps(all_prompts_meta, indent=2, ensure_ascii=False),
    encoding="utf-8",
)
print(f"\n✓ {OUTPUT_DIR}/beats_and_prompts.json — {len(all_prompts_meta)} prompts")

# ============================================================
# ETAPA 3 — FLUX
# ============================================================
FAL_URL = f"{cfg.fal_base_url}/fal-ai/flux-2-pro"
HEADERS = {"Authorization": f"Key {cfg.fal_api_key}", "Content-Type": "application/json"}
MAX_RETRIES = 2


def flux_poll(status_url, response_url, timeout=180):
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(status_url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        d = r.json()
        status = d.get("status", "").upper()
        if status == "COMPLETED":
            res = requests.get(response_url, headers=HEADERS, timeout=15)
            res.raise_for_status()
            return res.json()
        if status in ("FAILED", "ERROR"):
            raise RuntimeError(f"Flux fallo: {json.dumps(d)[:200]}")
        time.sleep(2)
    raise TimeoutError(f"Flux timeout {timeout}s")


print("\n" + "=" * 70)
print(f"ETAPA 3 — Generando {len(all_prompts_meta)} imagenes Flux")
print("=" * 70)

errors = []
for meta in all_prompts_meta:
    idx = meta["img_idx"]
    prompt = meta["flux_prompt_final"]
    label = f"fake_cuba_img_{idx:02d}"
    print(f"\n  [{label}] generando...")

    payload = {
        "prompt": prompt,
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "png",
        "image_size": {"width": 1080, "height": 1920},
    }

    success = False
    last_err = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            r = requests.post(FAL_URL, headers=HEADERS, json=payload, timeout=30)
            r.raise_for_status()
            result = r.json()
            data = result if "images" in result else flux_poll(result["status_url"], result["response_url"])
            img_url = data["images"][0]["url"]
            img_bytes = requests.get(img_url, timeout=60).content
            out_path = OUTPUT_DIR / f"{label}.png"
            out_path.write_bytes(img_bytes)
            print(f"     -> {out_path.name}" + (f" (intento {attempt})" if attempt > 1 else ""))
            success = True
            break
        except TimeoutError:
            last_err = f"timeout intento {attempt}"
            print(f"     ⚠ timeout, reintentando...")
            time.sleep(3)
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 422:
                last_err = f"422 content rejected: {e.response.text[:120]}"
                print(f"     ✗ 422, no se reintenta")
                break
            last_err = f"HTTP {e.response.status_code if e.response else '?'}"
            print(f"     ⚠ HTTP error, reintentando...")
            time.sleep(3)
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:100]}"
            print(f"     ⚠ {last_err}, reintentando...")
            time.sleep(3)

    if not success:
        errors.append({"label": label, "prompt": prompt, "error": last_err})
    time.sleep(1)

print("\n" + "=" * 70)
print("RESUMEN STRESS TEST")
print("=" * 70)
print(f"OK: {len(all_prompts_meta) - len(errors)}/{len(all_prompts_meta)} imagenes")
print(f"Estrategia: {ESTRATEGIA['nombre']}")
print(f"Ancla: {ANCLA_GLOBAL}")
if errors:
    print(f"\n⚠ {len(errors)} fallaron:")
    (OUTPUT_DIR / "errors.json").write_text(
        json.dumps(errors, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    for e in errors:
        print(f"  - {e['label']}: {e['error']}")
print(f"\nOutputs: {OUTPUT_DIR}/")