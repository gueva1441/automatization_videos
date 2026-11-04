"""audio_master.py — F76: master del mp4 final a `master_lufs` integrados con pico real ≤ `master_tp_dbtp`.

Va al final de fase2b, sobre la mezcla terminada (la voz y la música siguen calibradas a −24; esto es un paso aparte).
Una sola receta, que mide y se corrige sola (F75 mostró que suponer el margen del AAC no sirve):

  cada pasada:  volume=<G>dB, aresample=<sr×oversample>, alimiter=level=disabled:latency=1:limit=<10^(techo/20)>,
                aresample=<sr>  →  AAC <aac_bitrate>  →  medir el AAC con ebur128=peak=true (I, LRA, pico real)
  falla = max(0, pico − tp) + max(0, |I − lufs| − tol)
  falla 0 → listo. Si no: techo −= max(0, pico − tp); G += lufs − I; otra pasada.
  Si una pasada no baja la falla frente a la anterior → para y se queda con la de menor falla que cumpla el pico
  (si ninguna cumple, la de menor pico) y deja un ⚠ (no frena el pipeline).

Arranque: G = lufs − I medido del audio original; techo = tp. Sin número de vueltas: el bucle termina por la regla.
`latency=1` (F75): sin él el limitador atrasa el audio ~5 ms frente al video.
El video no se toca: remux `-c:v copy` a un temporal y reemplazo atómico del mismo archivo.
Constantes: audio_profiles.py (master_*, aac_bitrate) con su origen; 44 100 Hz es la frecuencia de la mezcla de fase2b.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Callable

from audio_config import AUDIO_STYLE
from audio_profiles import AUDIO_PROFILES

# frecuencia del audio final: la de la mezcla de fase2b (`aresample=44100`)
SAMPLE_RATE = 44100


def perfil(clave: str):
    """Constante del perfil activo; si el perfil no la trae, la del perfil de producción (MISTERIO_ABISAL)."""
    return AUDIO_STYLE.get(clave, AUDIO_PROFILES["MISTERIO_ABISAL"][clave])


def _ffmpeg() -> str:
    return shutil.which("ffmpeg") or "ffmpeg"


def medir(path: Path, ffmpeg: str | None = None) -> dict:
    """I (LUFS), LRA (LU) y pico real (dBTP) del audio de `path` con ebur128=peak=true (resumen final)."""
    r = subprocess.run([ffmpeg or _ffmpeg(), "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af",
                        "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    resumen = r.stderr[r.stderr.rfind("Summary:"):]
    i = re.search(r"I:\s*(-?[\d.]+|-inf)\s*LUFS", resumen)
    lra = re.search(r"LRA:\s*(-?[\d.]+)\s*LU", resumen)
    tp = re.search(r"True peak:\s*Peak:\s*(-?[\d.]+|-inf)\s*dBFS", resumen)
    if not (i and lra and tp):
        raise RuntimeError(f"ebur128 sin resumen para {path.name}: {r.stderr[-300:]}")
    return {"I": float(i.group(1)), "LRA": float(lra.group(1)), "pico": float(tp.group(1))}


def cadena(g_db: float, techo_dbtp: float, oversample: int | None = None) -> str:
    """El filtro de una pasada (sin números sueltos: todo sale del perfil o de la pasada)."""
    ov = oversample or perfil("master_oversample")
    return (f"volume={g_db:.2f}dB,aresample={SAMPLE_RATE * ov},"
            f"alimiter=level=disabled:latency=1:limit={10 ** (techo_dbtp / 20):.6f},aresample={SAMPLE_RATE}")


def _pasada_ffmpeg(src: Path, out: Path, g_db: float, techo: float, ffmpeg: str | None = None) -> None:
    subprocess.run([ffmpeg or _ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vn",
                    "-af", cadena(g_db, techo), "-c:a", "aac", "-b:a", perfil("aac_bitrate"), str(out)],
                   check=True, capture_output=True)


def falla(m: dict, lufs: float, tp: float, tol: float) -> float:
    return max(0.0, m["pico"] - tp) + max(0.0, abs(m["I"] - lufs) - tol)


def bucle(medida_original: dict, pasada: Callable[[float, float], dict], *,
          lufs: float | None = None, tp: float | None = None, tol: float | None = None) -> tuple[list[dict], dict, str | None]:
    """El bucle de la receta. `pasada(G, techo)` hace la pasada y devuelve la medida del AAC.
    Devuelve (tabla de pasadas, la elegida, aviso ⚠ o None)."""
    lufs = perfil("master_lufs") if lufs is None else lufs
    tp = perfil("master_tp_dbtp") if tp is None else tp
    tol = perfil("master_lufs_tol_lu") if tol is None else tol
    g, techo = lufs - medida_original["I"], tp
    tabla: list[dict] = []
    while True:
        m = pasada(g, techo)
        fila = {"pasada": len(tabla) + 1, "G": round(g, 2), "techo": round(techo, 2), **m,
                "falla": round(falla(m, lufs, tp, tol), 3)}
        tabla.append(fila)
        if fila["falla"] == 0:
            return tabla, fila, None
        if len(tabla) > 1 and fila["falla"] >= tabla[-2]["falla"]:
            cumplen = [f for f in tabla if f["pico"] <= tp]
            elegida = (min(cumplen, key=lambda f: f["falla"]) if cumplen else min(tabla, key=lambda f: f["pico"]))
            aviso = (f"⚠ master sin cerrar: la pasada {fila['pasada']} no bajó la falla; queda la pasada "
                     f"{elegida['pasada']} (I {elegida['I']}, pico real {elegida['pico']} dBTP"
                     f"{'' if cumplen else ', NINGUNA cumple el techo de pico'})")
            return tabla, elegida, aviso
        techo -= max(0.0, m["pico"] - tp)
        g += lufs - m["I"]


def master_mp4(path: Path, *, ffmpeg: str | None = None, log: Callable[[str], None] = print) -> dict:
    """Masteriza el audio de `path` en el lugar (video `-c:v copy`). Devuelve {original, pasadas, elegida, aviso}."""
    path = Path(path)
    ff = ffmpeg or _ffmpeg()
    work = path.with_name(f"_{path.stem}_master")
    work.mkdir(exist_ok=True)
    try:
        original = medir(path, ff)
        archivos: dict[int, Path] = {}

        def pasada(g: float, techo: float) -> dict:
            out = work / f"pasada_{len(archivos) + 1}.m4a"
            _pasada_ffmpeg(path, out, g, techo, ff)
            archivos[len(archivos) + 1] = out
            return medir(out, ff)

        tabla, elegida, aviso = bucle(original, pasada)
        tmp = path.with_name(f"{path.stem}._master_tmp{path.suffix}")
        subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", str(path),
                        "-i", str(archivos[elegida["pasada"]]), "-map", "0:v", "-map", "1:a", "-c", "copy",
                        "-movflags", "+faststart", str(tmp)], check=True, capture_output=True)
        os.replace(tmp, path)
    finally:
        shutil.rmtree(work, ignore_errors=True)
        path.with_name(f"{path.stem}._master_tmp{path.suffix}").unlink(missing_ok=True)   # si falló el remux
    log(f"  🔊 master: original I {original['I']} LUFS · LRA {original['LRA']} · pico real {original['pico']} dBTP")
    log("     | pasada | G | techo | I | LRA | pico real (AAC) |")
    for f in tabla:
        marca = " ← elegida" if f is elegida else ""
        log(f"     | {f['pasada']} | {f['G']:+.2f} | {f['techo']:.2f} | {f['I']} | {f['LRA']} | {f['pico']} |{marca}")
    if aviso:
        log(f"     {aviso}")
    return {"original": original, "pasadas": tabla, "elegida": elegida, "aviso": aviso}
