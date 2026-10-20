"""AB lado a lado: A (sin gfx) | B (con gfx), 1920x540, audio de B. Uso: make_ab.py A.mp4 B.mp4 OUT.mp4"""
import subprocess
import sys

a, b, out = sys.argv[1:4]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", b],
                           capture_output=True, text=True).stdout)
graph = ("[0:v]scale=960:540,setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=120[a];[1:v]scale=960:540,setsar=1,fps=30[b];"
         "[a][b]hstack=inputs=2[v]")
cmd = ["ffmpeg", "-v", "error", "-y", "-i", a, "-i", b, "-filter_complex", graph, "-map", "[v]", "-map", "1:a?",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "160k", "-t", f"{dur:.3f}", out]
subprocess.run(cmd, check=True)
print("ok", out)
