# -*- coding: utf-8 -*-
"""
Prueba F9 — Gemini TTS (3.1 Flash preview) con el cap 4 de Orleans v3 (F7c-3).
Genera 4 WAV con 4 voces distintas + 1 con el modelo 2.5 Pro TTS para comparar.
Uso (desde la raíz del repo, con el Python del pipeline):
    python lab/hyperframes/f9/prueba_tts_gemini.py
Salida: lab/hyperframes/f9/audio/*.wav  (24 kHz mono)
Costo estimado: < US$ 0.20 en total.
"""
import base64, os, sys, time, wave, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from config import api  # usa tu gemini_api_key
from google import genai
from google.genai import types

OUT = pathlib.Path(__file__).parent / "audio"
OUT.mkdir(exist_ok=True)

# Cap 4 de F7c-3, con pausas marcadas: "…" = respiro corto, línea en blanco = silencio largo.
TEXTO = """El 30 de agosto, el agua sucia de la inundación irrumpió en las celdas. Olía a una mezcla de aguas residuales y combustible diésel. En varios pabellones, los presos quedaron atrapados en sus celdas cerradas. Vieron cómo el nivel subía… sin poder hacer nada. Pronto, el agua les llegaría hasta el pecho.

Inició la evacuación de los edificios Templeman uno y dos. Pero para otros… ya no había tiempo. Un preso que logró salir vio dos cadáveres flotando en el pabellón médico del primer piso.

La muerte ya estaba dentro de los muros.

Algunos prisioneros estuvieron de pie durante días, con el agua contaminada que les llegaba hasta el pecho… o el cuello. No podían sentarse. No podían dormir. En Templeman tres, los reclusos de la planta baja no serían evacuados hasta el jueves primero de septiembre. Cuatro días después de que la inundación los alcanzara.

Desesperados, intentaron pedir auxilio. La respuesta no fue un rescate. Fue una advertencia. No era el sonido de botes…

Eran disparos."""

ESTILO = ("Narrador de documental de historia oscura en español neutro latinoamericano. Voz masculina grave, "
          "cansada, íntima, como contando algo que vio. Ritmo lento. Pausa larga en cada línea en blanco y "
          "en cada puntos suspensivos; silencio de un segundo antes de la última frase. Sin dramatismo de "
          "locutor: contenido, casi susurrado en los momentos duros. Nunca acelerar.")

PRUEBAS = [
    ("gemini-3.1-flash-tts-preview", "Algenib"),   # gravelly
    ("gemini-3.1-flash-tts-preview", "Gacrux"),    # mature
    ("gemini-3.1-flash-tts-preview", "Orus"),      # firm
    ("gemini-3.1-flash-tts-preview", "Charon"),    # informative, grave
    ("gemini-2.5-pro-preview-tts",   "Algenib"),   # referencia 2.5 Pro
]

client = genai.Client(api_key=api.gemini_api_key)

def _save_wav(path, pcm_bytes, rate=24000):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm_bytes)

def tts_generate_content(model, voice):
    """Camino clásico (google-genai >= 1.x): generate_content con AUDIO."""
    resp = client.models.generate_content(
        model=model,
        contents=f"{ESTILO}\n\nTEXTO:\n{TEXTO}",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            safety_settings=[types.SafetySetting(category=c, threshold="BLOCK_NONE") for c in (
                "HARM_CATEGORY_HARASSMENT","HARM_CATEGORY_HATE_SPEECH",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT","HARM_CATEGORY_DANGEROUS_CONTENT")],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice))),
        ),
    )
    if not resp.candidates or resp.candidates[0].content is None:
        fr = getattr(resp.candidates[0], "finish_reason", None) if resp.candidates else None
        raise RuntimeError(f"respuesta vacía · finish_reason={fr} · prompt_feedback={getattr(resp,'prompt_feedback',None)}")
    part = resp.candidates[0].content.parts[0]
    data = part.inline_data.data
    mime = getattr(part.inline_data, "mime_type", "") or ""
    return data, mime

def tts_interactions(model, voice):
    """Camino nuevo (google-genai >= 2.25): client.interactions con speech_metadata."""
    it = client.interactions.create(
        model=model,
        input=[{"type": "user_input", "content": [{"type": "text",
                 "text": f"Instrucciones de lectura (no las leas en voz alta): {ESTILO}\n\n{TEXTO}"}]}],
        response_format={"type": "audio"},
        generation_config={"speech_config": [{"voice": voice}]},
    )
    return base64.b64decode(it.output_audio.data), "audio/wav"

for model, voice in PRUEBAS:
    name = f"{model.replace('-preview','').replace('gemini-','')}_{voice}.wav"
    path = OUT / name
    t0 = time.time()
    try:
        try:
            data, mime = tts_generate_content(model, voice)
        except Exception as e1:
            print(f"  generate_content falló ({type(e1).__name__}: {str(e1)[:120]}); pruebo interactions…")
            data, mime = tts_interactions(model, voice)
        if isinstance(data, str):
            data = base64.b64decode(data)
        if data[:4] == b"RIFF" or "wav" in mime:
            path.write_bytes(data)
        else:
            _save_wav(path, data)  # PCM crudo 24 kHz
        print(f"OK  {name}  {len(data)/1024:.0f} KB  {time.time()-t0:.1f}s")
    except Exception as e:
        print(f"ERR {name}: {type(e).__name__}: {str(e)[:300]}")

print(f"\nListo. Archivos en: {OUT}")
