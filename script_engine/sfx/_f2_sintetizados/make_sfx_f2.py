"""
make_sfx.py — Genera la librería de SFX de la capa gráfica (F2 §0d) con síntesis FFmpeg.

Licencia: CC0. Los sonidos se SINTETIZAN acá (osciladores + ruido filtrado), no se descargan de
ningún lado, así que no hay terceros ni atribución. Re-correr regenera los .wav idénticos
(semillas fijas).

Uso: python script_engine/sfx/make_sfx.py
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

SFX_DIR: Path = Path(__file__).parent
SR: int = 48_000

# nombre → (duración s, filtro lavfi del generador)
_SOUNDS: dict[str, tuple[float, str]] = {
    # tipeo: 6 clics secos de máquina de escribir
    "tipeo": (0.75, "anoisesrc=d=0.75:c=white:seed=11:a=0.9,highpass=f=2500,"
                    "volume='if(lt(mod(t,0.12),0.012),1,0)':eval=frame"),
    # sello: golpe sordo de goma sobre papel
    "sello": (0.35, "sine=f=95:d=0.35,volume='exp(-18*t)':eval=frame,"
                    "aformat=channel_layouts=mono[a];anoisesrc=d=0.35:c=brown:seed=3:a=0.6,lowpass=f=900,"
                    "volume='exp(-30*t)':eval=frame[b];[a][b]amix=inputs=2:normalize=0"),
    # papel: roce de hoja
    "papel": (0.6, "anoisesrc=d=0.6:c=pink:seed=5:a=0.5,bandpass=f=3500:w=2500,"
                   "volume='sin(PI*t/0.6)':eval=frame"),
    # golpe grave: impacto cinematográfico corto
    "golpe_grave": (1.2, "sine=f=48:d=1.2,volume='1.4*exp(-4*t)':eval=frame"),
    # whoosh suave: barrido de ruido
    "whoosh": (0.8, "anoisesrc=d=0.8:c=pink:seed=7:a=0.6,bandpass=f=1200:w=1600,"
                    "volume='pow(sin(PI*t/0.8),2)':eval=frame"),
    # click: interfaz
    "click": (0.08, "sine=f=1800:d=0.08,volume='exp(-90*t)':eval=frame"),
    # tic de callout: nota corta aguda
    "tic": (0.18, "sine=f=1320:d=0.18,volume='0.7*exp(-28*t)':eval=frame"),
    # tic sordo (F2b §2, énfasis de palabra): tono grave con el agudo filtrado, apagado
    "tic_sordo": (0.22, "sine=f=520:d=0.22,lowpass=f=900,volume='0.9*exp(-24*t)':eval=frame"),
    # drone subida (F3, pregunta de cierre): zumbido grave que sube de 55 a 110 Hz en 3 s y crece; sin golpe
    "drone_subida": (3.0, "aevalsrc='0.5*sin(2*PI*(55*t+9.1667*t*t))+0.25*sin(2*PI*(110*t+18.333*t*t))':d=3:s=48000,"
                          "lowpass=f=700,volume='0.15+0.85*pow(t/3,1.6)':eval=frame,afade=t=out:st=2.6:d=0.4"),
    # latido: dos golpes graves (lub-dub)
    "latido": (0.9, "sine=f=55:d=0.9,volume='1.3*(exp(-25*t)+0.8*exp(-25*abs(t-0.28))*gte(t,0.28))':eval=frame"),
    # F4c R5: un SFX propio por categoría de reserva (capa mínima), todos cortos y bajo la voz
    # brasa (fuego): chisporroteo — chasquidos de ruido blanco irregulares sobre un soplo grave
    "brasa": (0.9, "anoisesrc=d=0.9:c=white:seed=21:a=0.8,highpass=f=1800,"
                   "volume='if(lt(mod(t*37+sin(t*91),1),0.07),1,0.04)*exp(-1.5*t)':eval=frame"),
    # rumor (caos_gritos): murmullo de multitud lejano — ruido rosa en banda de voz que crece y se va
    "rumor": (1.2, "anoisesrc=d=1.2:c=pink:seed=9:a=0.7,bandpass=f=700:w=900,"
                   "volume='pow(sin(PI*t/1.2),1.5)*(0.75+0.25*sin(2*PI*6*t))':eval=frame"),
    # zumbido (radiacion_quimico): zumbido eléctrico de 120 Hz con 3 clics de contador
    "zumbido": (0.9, "aevalsrc='0.35*sin(2*PI*120*t)+0.15*sin(2*PI*240*t)+0.9*lt(mod(t,0.29),0.004)':d=0.9:s=48000,"
                     "volume='sin(PI*t/0.9)':eval=frame"),
    # viento (frio_abandono): ráfaga de viento — ruido marrón con filtro que respira
    "viento": (1.4, "anoisesrc=d=1.4:c=brown:seed=13:a=0.9,lowpass=f=600,"
                    "volume='pow(sin(PI*t/1.4),2)':eval=frame"),
    # vacio (silencio): un tono sub que se apaga — el golpe de la ausencia, sin ataque
    "vacio": (1.2, "sine=f=41:d=1.2,volume='0.9*sin(PI*min(t/0.25,1)/2)*exp(-2.2*t)':eval=frame"),
}


def make_all(out_dir: Path = SFX_DIR, only: list[str] | None = None) -> list[Path]:
    """Sintetiza los SFX (todos, o solo `only`) como WAV 48 kHz mono con un fade de 5 ms en cada borde."""
    out: list[Path] = []
    for name, (dur, graph) in _SOUNDS.items():
        if only and name not in only:
            continue
        dst = out_dir / f"{name}.wav"
        fade = f"afade=t=in:d=0.005,afade=t=out:st={dur - 0.005:.3f}:d=0.005,aformat=sample_rates={SR}:channel_layouts=mono"
        filt = f"{graph},{fade}" if "[" not in graph else f"{graph}[m];[m]{fade}"
        raw = out_dir / f"_{name}.raw.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-filter_complex", filt, "-t", f"{dur}",
                        "-c:a", "pcm_s16le", str(raw)], check=True, timeout=60)
        # normalización de pico a −1 dBFS: la mezcla en fase2b aplica la ganancia del perfil sobre esto
        det = subprocess.run(["ffmpeg", "-v", "info", "-i", str(raw), "-af", "volumedetect", "-f", "null", "-"],
                             capture_output=True, text=True, timeout=60).stderr
        peak = float(re.search(r"max_volume: (-?[\d.]+) dB", det).group(1))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={-1.0 - peak:.2f}dB",
                        "-c:a", "pcm_s16le", str(dst)], check=True, timeout=60)
        raw.unlink()
        out.append(dst)
    return out


if __name__ == "__main__":
    import sys
    for p in make_all(only=sys.argv[1:] or None):        # python make_sfx.py tic_sordo → solo ese
        print(p.name, p.stat().st_size)
