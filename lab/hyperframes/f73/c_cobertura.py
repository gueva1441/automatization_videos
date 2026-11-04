# Solo lectura: cobertura de `voz` por cap con la función real del server.
import sys
sys.path.insert(0, r"C:\CLAUDE_PROJECTS\automatization_videos")
import qa_studio_server as q

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
st = q.QAState(TID)
print("cap | palabras narración | palabras suma voz | % | segs | anclas no encontradas")
for n in st._cap_nums():
    cid = st._cap_id(n)
    narr = st._script[cid]["narration"]
    c = st.cap(n)
    segs = c["segments"]
    voz = sum(len((s.get("voz") or "").split()) for s in segs)
    nw = len(narr.split())
    norm = " ".join(narr.split())
    nf = [s.get("anchor") for s in segs if s.get("voz") == s.get("anchor")
          and " ".join((s.get("anchor") or "").split()) not in norm]
    print(f"{cid} | {nw} | {voz} | {100*voz/nw:.1f} % | {len(segs)} | {nf}")
    if cid == "ch03" or "--all" in sys.argv:
        for i, s in enumerate(segs):
            a = s.get("anchor") or ""
            v = s.get("voz") or ""
            resto = v[len(a):].strip() if v.startswith(a) else v
            print(f"   [{i}] ANCLA: {a}")
            if resto:
                print(f"       RESTO: {resto}")
