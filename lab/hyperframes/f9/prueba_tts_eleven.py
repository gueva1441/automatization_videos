# -*- coding: utf-8 -*-
"""
Prueba F9 — ElevenLabs: v2 actual · v2 con pausas <break> · v3 con etiquetas de actuación.
Cap 4 de Orleans v3 (F7c-3), voz del perfil activo (Bill, pqHfZKP75CvOlQylNhV4).
Uso: python lab\hyperframes\f9\prueba_tts_eleven.py   (desde la raíz del repo)
Salida: lab/hyperframes/f9/audio/eleven_*.mp3 · Costo: ~3,000 caracteres de tu plan (≈ US$ 0.7).
"""
import sys, time, pathlib, requests
ROOT = pathlib.Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT))
from config import api
from audio_config import AUDIO_STYLE

OUT = pathlib.Path(__file__).parent / "audio"; OUT.mkdir(exist_ok=True)
VOICE = AUDIO_STYLE.get("voice_id") or api.elevenlabs_voice_id
BASE = dict(AUDIO_STYLE["voice_settings"])  # stability 0.45, similarity 0.8, style 0.6, boost

PLANO = """El 30 de agosto, el agua sucia de la inundación irrumpió en las celdas. Olía a una mezcla de aguas residuales y combustible diésel. En varios pabellones, los presos quedaron atrapados en sus celdas cerradas. Vieron cómo el nivel subía sin poder hacer nada. Pronto, el agua les llegaría hasta el pecho. Inició la evacuación de los edificios Templeman uno y dos. Pero para otros, ya no había tiempo. Un preso que logró salir vio dos cadáveres flotando en el pabellón médico del primer piso. La muerte ya estaba dentro de los muros. Algunos prisioneros estuvieron de pie durante días, con el agua contaminada que les llegaba hasta el pecho o el cuello. No podían sentarse. No podían dormir. En Templeman tres, los reclusos de la planta baja no serían evacuados hasta el jueves primero de septiembre. Cuatro días después de que la inundación los alcanzara. Desesperados, intentaron pedir auxilio. La respuesta no fue un rescate. Fue una advertencia. No era el sonido de botes. Eran disparos."""

CON_BREAKS = """El 30 de agosto, el agua sucia de la inundación irrumpió en las celdas. <break time="0.6s" /> Olía a una mezcla de aguas residuales y combustible diésel. En varios pabellones, los presos quedaron atrapados en sus celdas cerradas. Vieron cómo el nivel subía… <break time="0.8s" /> sin poder hacer nada. Pronto, el agua les llegaría hasta el pecho. <break time="1.2s" />
Inició la evacuación de los edificios Templeman uno y dos. Pero para otros… <break time="0.7s" /> ya no había tiempo. Un preso que logró salir vio dos cadáveres flotando en el pabellón médico del primer piso. <break time="1.5s" />
La muerte ya estaba dentro de los muros. <break time="1.5s" />
Algunos prisioneros estuvieron de pie durante días, con el agua contaminada que les llegaba hasta el pecho… <break time="0.6s" /> o el cuello. No podían sentarse. <break time="0.5s" /> No podían dormir. En Templeman tres, los reclusos de la planta baja no serían evacuados hasta el jueves primero de septiembre. Cuatro días después de que la inundación los alcanzara. <break time="1.2s" />
Desesperados, intentaron pedir auxilio. La respuesta no fue un rescate. <break time="0.6s" /> Fue una advertencia. No era el sonido de botes… <break time="1.5s" />
Eran disparos."""

V3_TAGS = """[slowly] El 30 de agosto, el agua sucia de la inundación irrumpió en las celdas. [pause] Olía a una mezcla de aguas residuales y combustible diésel. En varios pabellones, los presos quedaron atrapados en sus celdas cerradas. Vieron cómo el nivel subía… [pause] sin poder hacer nada. Pronto, el agua les llegaría hasta el pecho. [long pause]
Inició la evacuación de los edificios Templeman uno y dos. Pero para otros… [pause] ya no había tiempo. [quietly] Un preso que logró salir vio dos cadáveres flotando en el pabellón médico del primer piso. [long pause]
[whispers] La muerte ya estaba dentro de los muros. [long pause]
[slowly] Algunos prisioneros estuvieron de pie durante días, con el agua contaminada que les llegaba hasta el pecho… [pause] o el cuello. No podían sentarse. No podían dormir. En Templeman tres, los reclusos de la planta baja no serían evacuados hasta el jueves primero de septiembre. Cuatro días después de que la inundación los alcanzara. [long pause]
Desesperados, intentaron pedir auxilio. La respuesta no fue un rescate. [pause] Fue una advertencia. [quietly] No era el sonido de botes… [long pause]
[whispers] Eran disparos."""

V4_TAGS = V3_TAGS.replace("[long pause]", "[long pause]").replace("[pause]", "[short pause]")

import os
SOLO_V4 = os.environ.get("SOLO_V4") == "1"
PRUEBAS = [
    ("eleven_v4_tags",    "eleven_v4",              V4_TAGS,    {"stability": 0.5, "similarity_boost": 0.8}),
    ("eleven_v4_lento",   "eleven_v4",              "[slowly] " + V4_TAGS.replace("\n", "\n[slowly] "), {"stability": 0.6, "similarity_boost": 0.8}),
] + ([] if SOLO_V4 else [
    ("eleven_v2_plano",   "eleven_multilingual_v2", PLANO,      BASE),
    ("eleven_v2_breaks",  "eleven_multilingual_v2", CON_BREAKS, BASE),
    ("eleven_v3_tags",    "eleven_v3",              V3_TAGS,    {"stability": 0.5, "similarity_boost": 0.8, "style": 0.4, "use_speaker_boost": True}),
    ("eleven_v3_creativo","eleven_v3",              V3_TAGS,    {"stability": 0.0, "similarity_boost": 0.8, "style": 0.6, "use_speaker_boost": True}),
])

VOZ_NUEVA = "N9Z5MLTIaHFLflaLtbDi"   # MS Narrador v1 (Voice Design, 2026-10-22)
PRUEBAS = [(n, m, t, v) for n, m, t, v in PRUEBAS] + [
    ("msnarrador_v4_tags",  "eleven_v4", V4_TAGS, {"stability": 0.5, "similarity_boost": 0.8}),
    ("msnarrador_v4_lento", "eleven_v4", "[slowly] " + V4_TAGS.replace("\n", "\n[slowly] "), {"stability": 0.6, "similarity_boost": 0.8}),
    ("msnarrador_v3_tags",  "eleven_v3", V3_TAGS, {"stability": 0.5, "similarity_boost": 0.8, "style": 0.4, "use_speaker_boost": True}),
]
def _voice_for(name): return VOZ_NUEVA if name.startswith("msnarrador_") else VOICE

for name, model, text, vs in PRUEBAS:
    if (OUT / f"{name}.mp3").exists():
        print(f"--  {name:18} ya existe, salto"); continue
    t0 = time.time()
    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{_voice_for(name)}",
                      headers={"xi-api-key": api.elevenlabs_api_key, "accept": "audio/mpeg"},
                      json={"text": text, "model_id": model, "voice_settings": vs, "language_code": "es"},
                      timeout=180)
    if r.status_code == 200:
        p = OUT / f"{name}.mp3"; p.write_bytes(r.content)
        print(f"OK  {name:18} {len(r.content)/1024:.0f} KB  {time.time()-t0:.1f}s")
    else:
        print(f"ERR {name:18} {r.status_code}: {r.text[:300]}")
print(f"\nArchivos en: {OUT}")
