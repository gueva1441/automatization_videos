"""
LAB CHAT 26 — Pipeline completo: Etapa 1 (splitter) + Etapa 2 (slots).

Splitter LLM lee narracion + sync_map del cap y decide:
- Cuantas unidades narrativas hay
- Por cada unidad: timestamps + cuantas imgs necesita (basado en densidad visual)

Generator LLM toma cada unidad y produce N prompts estructurados por slots.

Output: imagenes Flux + JSON de splits + JSON de prompts para auditar todo.
"""

import json
import pathlib
import time
import requests
from google import genai
from google.genai import types
from config import APIConfig

TOPIC_ID = "7b52de57-eee6-4018-ac25-8357e9779d92"
TARGET_CAP = 4
INTENT = "shock"  # de m01a
OUTPUT_DIR = pathlib.Path("lab_output_chat26_v2")
OUTPUT_DIR.mkdir(exist_ok=True)

cfg = APIConfig()
sm = json.loads(pathlib.Path(f"output/audio/{TOPIC_ID}/sync_map.json").read_text(encoding="utf-8"))
cap = sm["chapters"][TARGET_CAP - 1]
narration_text = cap["text"]
cap_duration = cap.get("duration_sec", 0)

print(f"=== LAB chat 26 v2 — ch0{TARGET_CAP} ({INTENT}) ===")
print(f"Duracion: {cap_duration:.1f}s | Narracion: {len(narration_text)} chars\n")

# Ritmo por intent (segundos por imagen objetivo)
RITMO_POR_INTENT = {
    "hook": (3, 5),
    "setup": (8, 12),
    "rising_tension": (5, 8),
    "shock": (3, 5),
    "consequences": (6, 10),
    "resolution": (8, 12),
    "outro": (6, 10),
}
ritmo_min, ritmo_max = RITMO_POR_INTENT.get(INTENT, (6, 10))
target_imgs_min = int(cap_duration / ritmo_max)
target_imgs_max = int(cap_duration / ritmo_min)
print(f"Ritmo objetivo intent={INTENT}: {ritmo_min}-{ritmo_max}s/img")
print(f"Cantidad imgs objetivo: {target_imgs_min}-{target_imgs_max}\n")

# ============================================================
# ETAPA 1 — SPLITTER
# ============================================================
SPLITTER_SYSTEM = f"""Sos editor de documentales dark history estilo Netflix.
Tu trabajo es dividir la narracion de un capitulo en UNIDADES NARRATIVAS
visuales, y decidir cuantas imagenes necesita cada unidad para mantener
el ojo del espectador enganchado.

REGLAS:
1. Una "unidad" agrupa frases que comparten foco visual (ej: "Piscinas relucientes,
   cines a la vanguardia, parques exuberantes y escuelas repletas de niños" =
   1 unidad ENUMERATIVA con 4 imgs sub-itemizadas).
2. Conectores como "Sin embargo", "Despues", "Pero" rompen unidades.
3. Decisiones (numero de imgs) basadas en:
   - Densidad visual del contenido (cuantas cosas distintas se pueden mostrar)
   - Duracion temporal de la unidad (mas tiempo = mas imgs para no aburrir)
4. Target de ritmo: el cap entero debe tener entre {target_imgs_min} y {target_imgs_max} imgs.

OUTPUT JSON array. Cada elemento con campos: unit_id (string como u01), text (string),
visual_focus (string corta), num_images (int), rationale (string corta).
"""

splitter_prompt = SPLITTER_SYSTEM
#splitter_prompt = SPLITTER_SYSTEM.format(min_imgs=target_imgs_min, max_imgs=target_imgs_max)
splitter_user = f"""NARRACION cap (duracion {cap_duration:.0f}s):

{narration_text}

Devolve JSON array con las unidades. Solo JSON, sin markdown."""

print("=== ETAPA 1 — Splitter LLM ===")
client = genai.Client(api_key=cfg.gemini_api_key)
resp = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=splitter_prompt,
        response_mime_type="application/json",
    ),
    contents=splitter_user,
)
units = json.loads(resp.text)
total_imgs = sum(u["num_images"] for u in units)
print(f"Unidades generadas: {len(units)}")
print(f"Total imgs propuestas: {total_imgs}")
for u in units:
    print(f"  {u['unit_id']}: {u['num_images']} imgs | {u['visual_focus'][:60]}")
(OUTPUT_DIR / "splits.json").write_text(json.dumps(units, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nGuardado: {OUTPUT_DIR}/splits.json\n")

# ============================================================
# ETAPA 2 — GENERATOR (slots por unidad)
# ============================================================
GENERATOR_SYSTEM = """Sos director de fotografia para documentales dark history estilo Netflix.
Generas prompts para Flux 2 Pro con anclaje historico-cultural fuerte,
resistentes a sesgos de dataset moderno.

Para CADA imagen pedida en una unidad narrativa, devolves UN prompt en
formato JSON con 7 slots obligatorios:

{
  "scene_type": "close-up | medium shot | wide shot | detail shot | aerial",
  "subject": "descripcion fisica concreta (ropa con materiales especificos, edad, expresion). NUNCA roles abstractos.",
  "period_anchors": "minimo 3 objetos/materiales/tecnologias concretas que anclan epoca",
  "location_context": "geografia y cultura concretas (ej: Soviet Ukraine 1986)",
  "lighting": "fuente luminica + mood",
  "camera_style": "referencia fotografica concreta de la epoca-region (Mosfilm, TASS, Magnum, Pravda...)",
  "palette_mood": "saturacion + atmosfera"
}

REGLAS DURAS:
- Si la unidad pide N imgs, devolves N prompts dentro del mismo array.
- DIVERSIDAD entre los N prompts: cada uno con scene_type distinto si es posible
  (no 3 wide shots seguidos). Alterna escalas y angulos.
- NO uses "modern", "contemporary", "rudimentary".
- NO menciones lo que NO debe aparecer (refuerza lo prohibido).
- Subject describe APARIENCIA, NUNCA rol abstracto ("liquidator", "scientist") sin descripcion fisica.
- Para enumeraciones: si la unidad enumera cosas (piscinas, cines, parques, niños),
  cada imagen cubre UNA cosa distinta del set.
"""

generator_user = f"""CONTEXTO general del capitulo:
{narration_text}

UNIDADES a ilustrar:
{json.dumps(units, indent=2, ensure_ascii=False)}

Para cada unit, generame sus num_images prompts estructurados.

Devuelve JSON con esta forma:
[
  {{"unit_id": "u01", "prompts": [{{...slot1}}, {{...slot2}}, ...]}},
  {{"unit_id": "u02", "prompts": [...]}},
  ...
]

Solo JSON, sin markdown."""

print("=== ETAPA 2 — Generator LLM ===")
resp = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=GENERATOR_SYSTEM,
        response_mime_type="application/json",
    ),
    contents=generator_user,
)
generated = json.loads(resp.text)
(OUTPUT_DIR / "prompts_structured.json").write_text(
    json.dumps(generated, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"Guardado: {OUTPUT_DIR}/prompts_structured.json\n")

# Flatten para Flux
def struct_to_flux(s):
    return (
        f"{s['scene_type']}: {s['subject']}. "
        f"Period: {s['period_anchors']}. "
        f"Location: {s['location_context']}. "
        f"Lighting: {s['lighting']}. "
        f"Style: {s['camera_style']}. "
        f"Mood: {s['palette_mood']}."
    )

flat = []
for unit_block in generated:
    for prompt_struct in unit_block["prompts"]:
        flat.append({
            "unit_id": unit_block["unit_id"],
            "prompt": struct_to_flux(prompt_struct),
        })
print(f"Total prompts flat: {len(flat)}")

# ============================================================
# ETAPA 3 — FLUX
# ============================================================
FAL_URL = f"{cfg.fal_base_url}/fal-ai/flux-2-pro"
HEADERS = {"Authorization": f"Key {cfg.fal_api_key}", "Content-Type": "application/json"}

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
            raise RuntimeError(f"Flux fallo: {json.dumps(d)[:300]}")
        time.sleep(2)
    raise TimeoutError(f"Flux timeout")

print(f"\n=== ETAPA 3 — Generando {len(flat)} imagenes Flux ===")
errors = []
MAX_RETRIES = 2

for i, item in enumerate(flat, 1):
    print(f"  [{i}/{len(flat)}] {item['unit_id']} generando...")
    payload = {
        "prompt": item["prompt"],
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "png",
        "image_size": {"width": 1080, "height": 1920},
    }

    success = False
    last_err = None
    for attempt in range(1, MAX_RETRIES + 2):  # 1 intento + MAX_RETRIES reintentos
        try:
            r = requests.post(FAL_URL, headers=HEADERS, json=payload, timeout=30)
            r.raise_for_status()
            result = r.json()
            data = result if "images" in result else flux_poll(result["status_url"], result["response_url"])
            img_url = data["images"][0]["url"]
            img_bytes = requests.get(img_url, timeout=60).content
            out_path = OUTPUT_DIR / f"ch04_{item['unit_id']}_img_{i:02d}.png"
            out_path.write_bytes(img_bytes)
            print(f"      -> {out_path.name}" + (f" (intento {attempt})" if attempt > 1 else ""))
            success = True
            break
        except TimeoutError as e:
            last_err = f"timeout intento {attempt}"
            print(f"      ⚠ timeout intento {attempt}/{MAX_RETRIES + 1}, reintentando...")
            time.sleep(3)
        except requests.HTTPError as e:
            # 422 = content rejection, NO reintentar (es decisión del safety filter)
            if e.response is not None and e.response.status_code == 422:
                last_err = f"422 content rejected: {e.response.text[:150]}"
                print(f"      ✗ FALLO content filter (422), no se reintenta")
                break
            last_err = f"HTTP {e.response.status_code if e.response else '?'} intento {attempt}"
            print(f"      ⚠ HTTP error intento {attempt}, reintentando...")
            time.sleep(3)
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:150]}"
            print(f"      ⚠ {last_err}, reintentando...")
            time.sleep(3)

    if not success:
        errors.append({"idx": i, "unit_id": item["unit_id"], "prompt": item["prompt"], "error": last_err})

    time.sleep(1)

print(f"\nOK: {len(flat) - len(errors)}/{len(flat)} imagenes en {OUTPUT_DIR}/")
if errors:
    print(f"\n⚠️  {len(errors)} fallaron definitivamente:")
    (OUTPUT_DIR / "errors.json").write_text(json.dumps(errors, indent=2, ensure_ascii=False), encoding="utf-8")
    for e in errors:
        print(f"  - img {e['idx']} ({e['unit_id']}): {e['error']}")
print(f"Splits: {OUTPUT_DIR}/splits.json")
print(f"Prompts: {OUTPUT_DIR}/prompts_structured.json")