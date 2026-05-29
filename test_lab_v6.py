"""
LAB CHAT 26 v6 STRESS TEST — Narracion inventada (Apolo 13, 1970).

3 fixes nuevos vs v5 stress (validados por auditoria Gemini):

1. ANTI-COMMERCIAL-BRANDS en Ancla Global:
   Quitar marcas comerciales de camara (ARRI, RED, SONY, ALEXA) — Flux las
   renderiza como texto en pantalla. Usar descriptores neutros.

2. ANTI-422 MEDICO:
   Prohibir sintomatologia extrema en sujeto_fisico (sweat visible, pallor,
   eyes closed slumped, hyperventilating, fainting). Disparan safety filter.
   Sanitizar a "tired expression, resting".

3. ANTI-ACRONIMO REFORZADO:
   Extender regla para clases militares OTAN/Soviet (Foxtrot-class, MiG-21,
   M4 Sherman, Apollo 13) y nombres de mision. Describir fisicamente.

Tema: Apolo 13. Contexto distinto: USA 1970, NASA, espacio. Trampas:
acronimos (CSM, LM, CO2, EECOM), nombres de mision, vocabulario tecnico.
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
OUTPUT_DIR = pathlib.Path("lab_output_chat26_v6_apollo")
OUTPUT_DIR.mkdir(exist_ok=True)

NICHO = "dark history / mystery documentary"
FORMATO = "vertical Shorts/TikTok 1080x1920, retencion agresiva (3s decision window)"
AUDIENCIA = "18-45, fans de Netflix dark docs, true crime, mystery"

CHARS_PER_IMAGE = 150
MIN_IMAGES_FLUX = 6
MAX_IMAGES_FLUX = 12

# Narracion INVENTADA — Apolo 13, abril 1970
FAKE_NARRATION = """13 de abril de 1970. A 320,000 kilometros de la Tierra, tres hombres dentro del modulo de comando Odyssey enfrentaron lo impensable. James Lovell, Jack Swigert y Fred Haise habian dejado la orbita lunar atras cuando una explosion silenciosa sacudio la nave. El tanque numero dos de oxigeno habia estallado, arrancando todo el panel lateral del modulo de servicio. En Houston, el director de vuelo Gene Kranz pronuncio la frase que paso a la historia: el fracaso no es una opcion. Pero los datos en sus pantallas decian otra cosa. Los niveles de dioxido de carbono trepaban hacia niveles letales. La temperatura interior caia bajo los cinco grados. Sin energia para calentadores, sin agua potable, los astronautas se acurrucaron en el modulo lunar Aquarius, originalmente disenado para dos hombres durante dos dias, ahora improvisado como bote salvavidas para tres durante cuatro. Los ingenieros en Tierra disenaron un filtro de aire con cinta adhesiva, calcetines y bolsas de plastico. Cuatro dias despues, contra toda probabilidad estadistica, el Odyssey amerizo en el Pacifico Sur. Que silencios guardo Lovell durante esas noches mirando una Luna que jamas pisaria?"""

FAKE_DURATION = 90.0
FAKE_INTENT = "shock"

cfg = APIConfig()
client = genai.Client(api_key=cfg.gemini_api_key)

print("=" * 70)
print("LAB v6 STRESS TEST — Apolo 13 (1970)")
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
# ETAPA 1 — DIRECTOR DE ARTE (FIX 1: sin marcas comerciales)
# ============================================================
DIRECTOR_SYSTEM = """Sos Director de Arte para canales verticales de dark history.

Dada una estrategia de retencion, proponé 3 opciones de Ancla Global que la implementan.

Ancla Global = string en INGLES TECNICO fijo que define identidad visual permanente del nicho.
- Define UNICAMENTE: camera + film type + base lighting + palette + grain/texture
- NO incluye sujetos, personajes, acciones, epocas especificas
- Termina con " -- "
- Max 220 caracteres
- 3 opciones distintas entre si

REGLA CRITICA — NO MARCAS COMERCIALES:
PROHIBIDO mencionar marcas de camaras o equipos comerciales en el Ancla:
- NO: "ARRI", "ALEXA", "RED", "V-RAPTOR", "SONY", "VENICE", "Kodak", "Zeiss"
- Flux las renderiza como texto en pantalla (bug critico cazado en stress test anterior).

USAR DESCRIPTORES NEUTROS:
- "large format digital cinema scan" en lugar de "ARRI ALEXA LF"
- "high dynamic range digital sensor" en lugar de "RED V-RAPTOR"
- "color-graded digital noir aesthetic" en lugar de marca especifica
- "anamorphic film emulation" en lugar de "Cooke anamorphic lens"

OUTPUT JSON array de 3 strings. Solo JSON.
"""

director_user = f"""ESTRATEGIA elegida:
{json.dumps(ESTRATEGIA, ensure_ascii=False)}

NICHO: {NICHO}
FORMATO: {FORMATO}

Proponé 3 opciones de Ancla Global en ingles tecnico SIN MARCAS COMERCIALES."""

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
# ETAPA 2 — TRADUCTOR LITERAL v6 (con 3 fixes nuevos)
# ============================================================
TRADUCTOR_SYSTEM = """You are a Literal Translator. You convert Spanish narrative prose into pure
physical matter prompts for Flux 2 Pro, optimized for vertical TikTok/Shorts retention.

CRITICAL — OUTPUT LANGUAGE:
ALL slots MUST be in ENGLISH TECHNICAL language. Flux thinks in English. If you write
Spanish in any slot, Flux will render Latin script gibberish on surfaces in the image.

OUTPUT: JSON array of N objects, each with 3 slots:

{
  "sujeto_fisico": "WHAT physical matter appears, in English. NO camera angles, NO lighting,
   NO style descriptors. ONLY matter. If human subject: ALWAYS include an explicit action verb.
   Static museum-photo subjects are forbidden.",
  "anclas_temporales_o_tecnicas": "1 to 3 highly specific objects that anchor era/culture/context,
   in English. DESCRIBE objects PHYSICALLY, not by model code or classification.",
  "modificador_de_escena": "OPTIONAL. Max 4 words. Local atmospheric condition only."
}

HARD RULES:

1. ANTI-READABLE-TEXT (BY DEFAULT):
   For ANY surface that could plausibly have text (walls, paper, blueprints, control panels,
   computer screens, billboards, signs, vehicles, doors, lab equipment, books, documents,
   uniforms with patches), append to sujeto_fisico: "no readable text, no visible letters,
   no inscriptions, no signage, no labels".

2. ANTI-ACRONYM (CRITICAL - REINFORCED):
   NEVER use the following in any output:
   a) Letter/number model codes: "IKS-A", "ZIL-131", "B-59", "T-5", "GP-5", "AK-47"
   b) Military/NATO/Soviet classifications: "Foxtrot-class", "Typhoon-class", "MiG-21"
   c) Mission/vehicle proper names: "Apollo 13", "Odyssey", "Aquarius", "Saturn V", "Soyuz"
   d) Agency acronyms: "NASA", "KGB", "CIA", "FBI"
   ALWAYS describe physically by appearance (materials, shape, color, era cues).
   Bad: "Apollo 13 command module Odyssey"
   Good: "conical aluminum spacecraft capsule with three small triangular windows and white thermal blanket panels"
   Bad: "NASA Mission Control Houston"
   Good: "vast 1970s control room with rows of beige consoles, green CRT monitors, men in white short-sleeved shirts and skinny ties smoking cigarettes"

3. ANTI-MODERNITY (CRITICAL):
   Identify the year/era from the narration and anchor every physical detail to that period.
   When in doubt, append: "period-correct [YEAR] equipment only, no modern materials".

4. ANTI-422 SAFETY (REINFORCED):
   a) FORBIDDEN gore/violence: shrapnel, colossal explosion, violent expulsion, blood, corpses, bodies, gore, massacre, decapitation.
   b) FORBIDDEN medical distress symptoms: visible sweat dripping, severe pallor, eyes
      rolling back, hyperventilating, slumped unconscious, foaming at mouth, vomiting,
      fainting, near-death, agonizing, dying.
   USE INSTEAD:
   - Violence → "scattered industrial materials, structural displacement, kinetic impact"
   - Medical → "tired expression, resting head against wall, eyes closed in fatigue,
     hands shaking slightly, slow breathing"

5. ANTI-LITERALITY (physical metaphors → real event):
   Identify the metaphor → identify the underlying physical event → describe THAT event.

6. ANTI-ABSTRACT-ROLES:
   FORBIDDEN: "astronaut", "engineer", "scientist", "officer" without physical description.
   REQUIRED: physical appearance (clothing material, age, expression, action).
   Bad: "Astronaut Lovell looking at Earth"
   Good: "Mid-forties man with crew cut hair, wearing a white cotton flight suit with grey patches, gripping a metal handrail, gazing through small triangular window"

7. ANTI-SPOKEN-TEXT:
   If narration mentions a spoken word, do NOT render the word as visible text.
   Describe the speaker physically saying it.

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
print("ETAPA 2 — Traductor Literal v6 (STRESS TEST Apolo 13)")
print("=" * 70)

all_prompts_meta = []

n_imgs = max(MIN_IMAGES_FLUX, min(MAX_IMAGES_FLUX, round(len(FAKE_NARRATION) / CHARS_PER_IMAGE)))

print(f"\n--- CAP FAKE (Apolo 13, abril 1970) ---")
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
        "cap": "fake_apollo_1970",
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
    label = f"fake_apollo_img_{idx:02d}"
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
print("RESUMEN v6 STRESS TEST")
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