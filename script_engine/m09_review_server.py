"""
m09_review_server.py — FORM web local de revisión de thumbnails (m09a v2, chat 56).

Reemplaza el viejo loop de terminal: `--review` levanta este server local (127.0.0.1,
puerto libre), abre el navegador y muestra UNA pantalla:
  - grilla de candidatas (existing + fresh) — click para ELEGIR;
  - panel de iteración: hero prompt + subject (casting) + crítica → GENERAR MÁS;
  - panel de composición: texto overlay + título + focus → COMPONER (preview + checklist).

stdlib http.server (mismo patrón que mixer_server.py). CERO deps nuevas. NO toca producción:
solo lee canonical/assets y escribe en publish/. Las llamadas Gemini/Flux son del lado de
Omar (sus keys). La lógica vive en ReviewState (testeable sin socket); el Handler es una capa
fina. Las funciones de m09_packaging se llaman vía el módulo (monkeypatcheables en tests).
"""
from __future__ import annotations

import hashlib
import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

from script_engine import m09_packaging as pkg

HOST = "127.0.0.1"


# ═══════════════════════════════════════════════════════════════
#  Estado (lógica testeable, sin socket)
# ═══════════════════════════════════════════════════════════════
class ReviewState:
    def __init__(self, tid: str, video_path: str | None = None, on_compose=None):
        self.tid = tid
        self.video_path = video_path        # va al CHECKLIST (fase3 lo resuelve desde topics_db)
        self.on_compose = on_compose        # callback tras COMPONER exitoso (fase3 → PACKAGED)
        self.pub = pkg._publish_dir(tid)
        self.cand = pkg._candidates_dir(tid)
        self.cand.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.generating = False
        self.last_error: str | None = None
        self.last_thumb: str | None = None

    def _subject_by_file(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for it in pkg._load_iterations(self.pub):
            for f in it.get("files", []):
                out[f] = it.get("subject", "") or ""
        return out

    def snapshot(self) -> dict:
        subj = self._subject_by_file()
        cands = []
        for p in pkg._candidate_files(self.cand):
            try:
                w, h = Image.open(p).size
            except Exception:
                w, h = 0, 0
            cands.append({"name": p.name, "w": w, "h": h,
                          "vertical": h > w, "subject": subj.get(p.name, "")})
        hist = pkg._load_iterations(self.pub)
        hero = ({"prompt": hist[-1].get("hero_prompt", ""), "subject": hist[-1].get("subject", "")}
                if hist else None)
        titles, overlays = [], []
        mp = self.pub / "metadata.json"
        if mp.exists():
            try:
                meta = json.loads(mp.read_text(encoding="utf-8"))
                titles = meta.get("titulos", [])
                overlays = meta.get("overlays", [])   # defensivo: metadata vieja no lo trae
            except (json.JSONDecodeError, OSError):
                titles, overlays = [], []
        finals = sorted(p.name for p in self.pub.glob("thumb_final*.png"))
        # rev = versión del INVENTARIO (candidatas). El JS solo redibuja la grilla cuando
        # cambia → sin flasheo ni tiles negros por recarga cada ciclo de polling.
        inv = [(c["name"], c["w"], c["h"], c["subject"]) for c in cands]
        rev = hashlib.sha1(json.dumps(inv, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]
        with self.lock:
            gen, err = self.generating, self.last_error
        return {"tid": self.tid, "candidates": cands, "hero": hero, "titles": titles,
                "overlays": overlays, "generating": gen, "last_error": err,
                "thumb_final": self.last_thumb, "finals": finals, "rev": rev}

    # ── generación (hero iter + frescas) en background ──
    def start_generate(self, critique: str | None) -> bool:
        with self.lock:
            if self.generating:
                return False
            self.generating = True
            self.last_error = None
        threading.Thread(target=self._run_generate, args=(critique,), daemon=True).start()
        return True

    def _run_generate(self, critique: str | None) -> None:
        try:
            hist = pkg._load_iterations(self.pub)
            if critique and hist:
                hero = pkg.generate_hero_prompt_iter(hist[-1]["hero_prompt"], critique)
            else:
                hero = pkg.generate_hero_prompt(pkg._load_canonical(self.tid))
            start = pkg._next_fresh_index(self.cand)
            _lines, files = pkg._render_fresh_from_hero(hero["prompt"], self.cand,
                                                        pkg.FRESH_THUMBS, start)
            pkg._record_iteration(self.pub, hero["prompt"], hero["subject"],
                                  critique or None, files)
            if not files:
                with self.lock:
                    self.last_error = "el render no generó ninguna imagen (ver terminal)."
        except Exception as e:  # noqa: BLE001
            with self.lock:
                self.last_error = f"{type(e).__name__}: {e}"
        finally:
            with self.lock:
                self.generating = False

    # ── primera tanda COMPLETA (metadata + hero + frescas) en background ──
    def start_first_batch(self) -> bool:
        """HANDOFF_136b: corre run_candidates ENTERO (títulos/overlays/desc/tags por Gemini
        + hero + frescas) — el mismo flujo que el --candidates original. Así el form abre y
        se autollena con las sugerencias del LLM sin que Omar apriete nada. En background:
        el puerto ya respondió, el /state va exponiendo metadata y candidatas a medida que
        aparecen. El caller (serve) solo lo dispara si falta metadata → idempotente."""
        with self.lock:
            if self.generating:
                return False
            self.generating = True
            self.last_error = None
        threading.Thread(target=self._run_first_batch, daemon=True).start()
        return True

    def _run_first_batch(self) -> None:
        try:
            pkg.run_candidates(self.tid, video_path=self.video_path)
        except Exception as e:  # noqa: BLE001
            with self.lock:
                self.last_error = f"{type(e).__name__}: {e}"
        finally:
            with self.lock:
                self.generating = False

    # ── composición (versionada) ──
    def compose(self, base: str, text: str, title: str, focus: str,
                fill: str = pkg.THUMB_FILL_DEFAULT) -> dict:
        try:
            out_name = pkg.next_thumb_name(self.tid)
            written = pkg.compose_and_package(self.tid, base, text, title,
                                              focus, fill, out_name, self.video_path)
            self.last_thumb = written.name
            if self.on_compose:
                try:
                    self.on_compose(written.name)   # fase3 → mark_as_packaged (idempotente)
                except Exception:
                    pass  # el callback NO debe romper la composición
            return {"thumb": written.name}
        except Exception as e:  # noqa: BLE001
            return {"error": f"{type(e).__name__}: {e}"}

    def resolve_image(self, name: str) -> Path | None:
        """Resuelve un PNG por nombre (solo basename) dentro de publish/ (candidatas o finals)."""
        if "/" in name or "\\" in name or not name.lower().endswith((".png", ".jpg")):
            return None
        for cand in (self.cand / name, self.pub / name):
            if cand.exists():
                return cand
        return None


# ═══════════════════════════════════════════════════════════════
#  HTML (estático; todo se renderiza desde /state vía fetch)
# ═══════════════════════════════════════════════════════════════
_PAGE = r"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Review thumbnails</title>
<style>
 :root{color-scheme:dark}
 body{background:#0f0f12;color:#eee;font-family:system-ui,sans-serif;margin:0;padding:20px}
 h1{font-size:18px;margin:0 0 4px} h2{font-size:14px;color:#9ad;margin:18px 0 8px}
 .err{background:#5a1d1d;border:1px solid #a33;color:#fdd;padding:10px 14px;border-radius:8px;margin:10px 0;display:none}
 .layout{display:grid;grid-template-columns:1fr 360px;gap:24px;align-items:start}
 .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
 figure{margin:0;background:#000;border:2px solid #333;border-radius:8px;overflow:hidden;cursor:pointer;position:relative}
 figure.sel{border-color:#e0b020;box-shadow:0 0 0 2px #e0b020}
 figure img{width:100%;display:block;aspect-ratio:16/9;object-fit:cover}
 figcaption{padding:6px 9px;font-size:12px;color:#bbb;font-family:ui-monospace,monospace}
 .subj{color:#8c8;font-size:11px}
 .panel{background:#17171c;border:1px solid #2a2a30;border-radius:10px;padding:14px 16px;margin-bottom:18px}
 .hero{white-space:pre-wrap;line-height:1.4;color:#cdd;font-size:13px;max-height:180px;overflow:auto}
 textarea,input[type=text]{width:100%;box-sizing:border-box;background:#0c0c0f;color:#eee;border:1px solid #333;border-radius:6px;padding:8px;font:inherit}
 button{background:#e0b020;color:#000;border:0;border-radius:6px;padding:10px 14px;font-weight:700;cursor:pointer;margin-top:8px}
 button:disabled{opacity:.5;cursor:wait}
 label{font-size:13px;color:#bbb;display:block;margin:8px 0 4px}
 .muted{color:#888;font-size:12px}
 #preview img{width:100%;border-radius:8px;border:1px solid #333;margin-top:8px}
 .badge{position:absolute;top:6px;left:6px;background:#000a;padding:2px 7px;border-radius:10px;font-size:11px}
</style></head><body>
<h1>Review de miniaturas — <span id="tid" class="muted"></span></h1>
<div class="muted">Click en una candidata para elegirla. La grilla se actualiza sola.</div>
<div id="err" class="err"></div>
<div class="layout">
 <div>
  <h2>Candidatas <span id="genstate" class="muted"></span></h2>
  <div id="grid" class="grid"></div>
 </div>
 <div>
  <div class="panel">
   <h2 style="margin-top:0">Iterar (casting + crítica)</h2>
   <div class="muted">sujeto: <b id="subject">—</b></div>
   <div class="hero" id="hero">—</div>
   <label>Crítica del director (qué cambiar)</label>
   <textarea id="critique" rows="4" placeholder="Ej: basta de edificios, quiero a la novia espectral mirando a cámara…"></textarea>
   <button id="genbtn" onclick="generate()">GENERAR MÁS</button>
  </div>
  <div class="panel">
   <h2 style="margin-top:0">Componer la elegida</h2>
   <div class="muted">elegida: <b id="chosen">(ninguna)</b></div>
   <label>Texto del overlay (2-4 palabras) — ya sugerido por la IA; reescribilo si querés (▾ hay más)</label>
   <input list="overlaylist" id="text" type="text" placeholder="MUERTE EN CHARLESTON" autocomplete="off">
   <datalist id="overlaylist"></datalist>
   <label>Título del VIDEO en YouTube (va al checklist, no a la imagen) — ya sugerido; reescribilo si querés (▾ hay más)</label>
   <input list="titlelist" id="titletext" type="text" placeholder="elegí o escribí el título" autocomplete="off">
   <datalist id="titlelist"></datalist>
   <label>Focus del crop (bases verticales)</label>
   <select id="focus"><option value="center">center</option><option value="top">top</option><option value="bottom">bottom</option></select>
   <label>Color del texto (stroke negro siempre)</label>
   <select id="fill"><option value="blanco">blanco</option><option value="amarillo">amarillo</option><option value="rojo">rojo</option></select>
   <button id="composebtn" onclick="compose()">COMPONER</button>
   <div id="preview"></div>
  </div>
 </div>
</div>
<script>
let chosen=null, lastRev=null;
function esc(s){const d=document.createElement('div');d.textContent=s==null?'':s;return d.innerHTML;}
function applySel(){document.querySelectorAll('#grid figure').forEach(f=>{f.classList.toggle('sel',f.dataset.name===chosen);});}
function renderGrid(st){
  const g=document.getElementById('grid');
  g.innerHTML = st.candidates.map(c=>{
    const subj = c.subject?('<div class="subj">'+esc(c.subject)+'</div>'):'';
    return '<figure data-name="'+esc(c.name)+'" onclick="pick(this.dataset.name)">'
      +'<div class="badge">'+c.w+'×'+c.h+(c.vertical?' ↕':'')+'</div>'
      +'<img src="/img/'+encodeURIComponent(c.name)+'" loading="lazy">'
      +'<figcaption>'+esc(c.name)+subj+'</figcaption></figure>';
  }).join('') || '<div class="muted">(sin candidatas — usá GENERAR MÁS)</div>';
  applySel();
}
async function refresh(){
  let st; try{ st=await (await fetch('/state')).json(); }catch(e){ return; }
  document.getElementById('tid').textContent=st.tid;
  const err=document.getElementById('err');
  if(st.last_error){err.style.display='block';err.textContent='⚠ '+st.last_error;}else{err.style.display='none';}
  document.getElementById('genstate').textContent=st.generating?'· generando…':'';
  document.getElementById('genbtn').disabled=st.generating;
  document.getElementById('subject').textContent=st.hero?st.hero.subject||'—':'—';
  document.getElementById('hero').textContent=st.hero?st.hero.prompt||'(sin hero)':'(sin candidatas — generá la primera tanda)';
  // GRILLA: solo redibujar si el inventario cambió (rev) → sin flasheo ni tiles negros
  if(st.rev!==lastRev){ renderGrid(st); lastRev=st.rev; }
  // comboboxes: poblar los datalist de título y overlay con las sugerencias de la IA
  fillDatalist('titlelist', st.titles);
  fillDatalist('overlaylist', st.overlays||[]);
  // pre-llenar las cajas con la 1a sugerencia del LLM (una sola vez, sin pisar lo que Omar escriba)
  prefillOnce('titletext', (st.titles&&st.titles[0])||'');
  prefillOnce('text', (st.overlays&&st.overlays[0])||'');
}
function prefillOnce(id, val){
  const el=document.getElementById(id);
  if(!el || !val) return;
  if(el.dataset.touched==='1' || el.dataset.prefilled==='1') return;  // ya lo tocó / ya lo pre-llenamos
  if(el.value.trim()!=='') return;                                    // el usuario ya escribió algo
  el.value=val; el.dataset.prefilled='1';
}
function bindTouch(id){
  const el=document.getElementById(id);
  if(el && !el.dataset.bound){ el.addEventListener('input',()=>{el.dataset.touched='1';}); el.dataset.bound='1'; }
}
bindTouch('text'); bindTouch('titletext');
function fillDatalist(id, opts){
  const dl=document.getElementById(id);
  const sig=opts.join('');
  if(dl.dataset.sig===sig) return;   // sin cambios → no redibujar (evita pisar mientras se escribe)
  dl.innerHTML=opts.map(o=>'<option value="'+esc(o)+'">').join('');
  dl.dataset.sig=sig;
}
function pick(name){chosen=name;document.getElementById('chosen').textContent=name;applySel();}
async function generate(){
  document.getElementById('genbtn').disabled=true;
  const critique=document.getElementById('critique').value;
  await fetch('/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({critique})});
  setTimeout(refresh,400);
}
async function compose(){
  if(!chosen){alert('Elegí una candidata primero (click).');return;}
  const text=document.getElementById('text').value;
  const title=document.getElementById('titletext').value.trim();
  if(!title){alert('Elegí o escribí un título');return;}
  const focus=document.getElementById('focus').value;
  const fill=document.getElementById('fill').value;
  const btn=document.getElementById('composebtn');btn.disabled=true;
  const res=await (await fetch('/compose',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({base:chosen,text,title,focus,fill})})).json();
  btn.disabled=false;
  const pv=document.getElementById('preview');
  if(res.error){pv.innerHTML='<div class="err" style="display:block">⚠ '+esc(res.error)+'</div>';}
  else{pv.innerHTML='<div class="muted">'+esc(res.thumb)+' · CHECKLIST escrito</div><img src="/img/'+encodeURIComponent(res.thumb)+'">';}
}
refresh(); setInterval(refresh,2000);
</script></body></html>"""


# ═══════════════════════════════════════════════════════════════
#  HTTP Handler (capa fina sobre ReviewState)
# ═══════════════════════════════════════════════════════════════
class Handler(BaseHTTPRequestHandler):
    state: ReviewState = None  # type: ignore[assignment]  (lo setea serve())

    def log_message(self, *a):  # silencio
        pass

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _bytes(self, data: bytes, ctype: str, status=200):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        try:
            route = urlparse(self.path).path
            if route == "/":
                self._bytes(_PAGE.encode("utf-8"), "text/html; charset=utf-8")
            elif route == "/state":
                self._json(self.state.snapshot())
            elif route.startswith("/img/"):
                name = urlparse(self.path).path[len("/img/"):]
                from urllib.parse import unquote
                p = self.state.resolve_image(unquote(name))
                if not p:
                    self._json({"error": "no encontrada"}, 404)
                else:
                    ct = "image/jpeg" if p.suffix.lower() == ".jpg" else "image/png"
                    self._bytes(p.read_bytes(), ct)
            else:
                self._json({"error": "ruta no encontrada"}, 404)
        except Exception as e:  # noqa: BLE001
            self._json({"error": f"{type(e).__name__}: {e}"}, 500)

    def do_POST(self):
        try:
            route = urlparse(self.path).path
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            if route == "/generate":
                crit = (body.get("critique") or "").strip() or None
                started = self.state.start_generate(crit)
                self._json({"started": started, "busy": not started})
            elif route == "/compose":
                self._json(self.state.compose(body.get("base", ""), body.get("text", ""),
                                              body.get("title", ""), body.get("focus", "center"),
                                              body.get("fill", pkg.THUMB_FILL_DEFAULT)))
            else:
                self._json({"error": "ruta no encontrada"}, 404)
        except Exception as e:  # noqa: BLE001
            self._json({"error": f"{type(e).__name__}: {e}"}, 500)


def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, 0))
    port = s.getsockname()[1]
    s.close()
    return port


def serve(tid: str, video_path: str | None = None, on_compose=None,
          port: int | None = None, open_browser: bool = True,
          auto_generate_if_empty: bool = False) -> None:
    """port=None → puerto libre (compat fase3/CLI). open_browser=False → NO abre pestaña
    (HANDOFF_135: el QA Studio lo embebe en iframe; abrir sería una pestaña duplicada).

    auto_generate_if_empty (HANDOFF_136b): si falta metadata (candidates_ready=False), dispara
    la primera tanda COMPLETA (metadata Gemini con títulos/overlays + hero + frescas) en
    background al arrancar — así un click en MINIATURAS del QA Studio genera solo (y el form se
    autollena con las sugerencias del LLM), sin apretar GENERAR MÁS. Idempotente: con metadata ya
    en disco no dispara (fase3 corre run_candidates ANTES → no se ve afectado). El puerto se
    bindea primero, la generación es en thread → el form responde al toque y muestra 'generando'."""
    Handler.state = ReviewState(tid, video_path=video_path, on_compose=on_compose)
    if port is None:
        port = _free_port()
    httpd = ThreadingHTTPServer((HOST, port), Handler)
    url = f"http://{HOST}:{port}/"
    print("─" * 60)
    print(f"  Form de review de thumbnails — {tid}")
    print(f"  ▶ {url}    (Ctrl+C para frenar)")
    print("─" * 60)
    # Guard = candidates_ready (existe metadata.json), el MISMO criterio que fase3.
    # NO alcanza con mirar si hay PNGs: una corrida vieja pudo dejar frescas SIN metadata
    # (títulos/overlays) → los textbox quedarían vacíos. Si falta la metadata, regeneramos.
    if auto_generate_if_empty and not pkg.candidates_ready(tid):
        if Handler.state.start_first_batch():
            print("  🖼 sin metadata (candidates_ready=False) → generando primera tanda "
                  "COMPLETA (metadata + hero + frescas) en background…")
    if open_browser:
        pkg._open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  frenado.")
        httpd.shutdown()
