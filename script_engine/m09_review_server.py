"""
m09_review_server.py — FORM web local de revisión de miniaturas (m09a, F58: 3 paquetes terminados).

`--review` levanta este server local (127.0.0.1, puerto libre), abre el navegador y muestra UNA pantalla con los
paquetes de `metadata.json`: por paquete la miniatura compuesta, el título con su cuenta de caracteres, el texto, los
datos (`id: texto`), `cap_que_paga`, el ancla y los avisos. Se pueden editar el título y el texto (recompone sin red),
elegir otra base (la foto del paquete o cualquier foto `_graded` del video), «rehacer foto» (A3 solo para ese ancla) y
pedir «3 paquetes nuevos» (todo de nuevo, sin pisar números). COMPONER escribe el thumb_final versionado + CHECKLIST.

stdlib http.server (mismo patrón que mixer_server.py). CERO deps nuevas. Solo sirve rutas dentro de `_assets_dir(tid)`,
`thumb_candidates/` y `publish/`. La lógica vive en ReviewState (testeable sin socket); el Handler es una capa fina.
Las funciones de m09_packaging se llaman vía el módulo (monkeypatcheables en tests).
"""
from __future__ import annotations

import hashlib
import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

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

    def snapshot(self) -> dict:
        meta = pkg._leer_meta(self.tid)
        paquetes = []
        for p in meta.get("paquetes", []) or []:
            if not isinstance(p, dict):
                continue
            mini = p.get("miniatura")
            paquetes.append({
                "n": p.get("n"), "estrategia": p.get("estrategia"),
                "titulo": p.get("titulo", ""), "chars": len(p.get("titulo", "") or ""),
                "texto": p.get("texto", ""), "dato_ids": p.get("dato_ids", []), "datos": p.get("datos", {}),
                "cap_que_paga": p.get("cap_que_paga"), "ancla": p.get("ancla", ""),
                "avisos": p.get("avisos", []), "foto": p.get("foto"), "base": p.get("base"),
                "miniatura": mini, "motivo_sin_foto": p.get("motivo_sin_foto"),
                "prompt": p.get("prompt"),
                "img": (f"/img/{mini}" if mini else (f"/img/{p['foto']}" if p.get("foto") else None)),
                "mtime": self._mtime(mini),
            })
        bases = pkg.bases_del_video(self.tid)
        finals = sorted(p.name for p in self.pub.glob("thumb_final*.png"))
        # rev = versión del INVENTARIO (paquetes + sus archivos). El JS solo redibuja cuando cambia → sin flasheo.
        inv = [(p["n"], p["titulo"], p["texto"], p["base"], p["miniatura"], p["mtime"], p["avisos"]) for p in paquetes]
        rev = hashlib.sha1(json.dumps(inv, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]
        with self.lock:
            gen, err = self.generating, self.last_error
        return {"tid": self.tid, "paquetes": paquetes, "descripcion": meta.get("descripcion", ""),
                "tags": meta.get("tags", []), "avisos": meta.get("avisos", []), "bases": bases,
                "generating": gen, "last_error": err, "thumb_final": self.last_thumb, "finals": finals, "rev": rev}

    def _mtime(self, name: str | None) -> int:
        try:
            return int((self.cand / name).stat().st_mtime) if name else 0
        except OSError:
            return 0

    # ── trabajos en background (Opus + fotos) ──
    def _start(self, target, *args) -> bool:
        with self.lock:
            if self.generating:
                return False
            self.generating = True
            self.last_error = None
        threading.Thread(target=self._run, args=(target, *args), daemon=True).start()
        return True

    def _run(self, target, *args) -> None:
        try:
            target(*args)
        except Exception as e:  # noqa: BLE001
            with self.lock:
                self.last_error = f"{type(e).__name__}: {e}"
        finally:
            with self.lock:
                self.generating = False

    def start_first_batch(self) -> bool:
        """HANDOFF_136b / F58: corre run_candidates ENTERO (N_PAQUETES paquetes + fotos) en background. El caller
        (serve) solo lo dispara si falta metadata con `paquetes` → idempotente. «3 paquetes nuevos» usa lo mismo."""
        return self._start(pkg.run_candidates, self.tid, self.video_path)

    def start_rehacer_foto(self, n: int) -> bool:
        return self._start(pkg.rehacer_foto, self.tid, n)

    # ── edición sin red ──
    def editar(self, n: int, titulo: str | None, texto: str | None, base: str | None) -> dict:
        try:
            p = pkg.editar_paquete(self.tid, n, titulo=titulo, texto=texto, base=base)
            return {"ok": True, "n": p["n"], "miniatura": p.get("miniatura"), "avisos": p.get("avisos", [])}
        except Exception as e:  # noqa: BLE001
            return {"error": f"{type(e).__name__}: {e}"}

    # ── composición final (versionada) ──
    def compose(self, n: int, focus: str = "center", fill: str = pkg.THUMB_FILL_DEFAULT,
                size_factor: float = 1.0) -> dict:
        try:
            p = pkg._paquete(pkg._leer_meta(self.tid), n)
            if not p.get("base"):
                return {"error": f"el paquete {n} no tiene foto ni base elegida"}
            out_name = pkg.next_thumb_name(self.tid)
            written = pkg.compose_and_package(self.tid, p["base"], p.get("texto", ""), p.get("titulo", ""),
                                              focus, fill, out_name, self.video_path, size_factor=size_factor)
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
        """Resuelve una imagen por ruta relativa: `assets/<rel>` dentro de `_assets_dir(tid)`, o un basename en
        thumb_candidates/ o publish/. Nada fuera de esas tres carpetas."""
        name = (name or "").replace("\\", "/")
        if not name.lower().endswith((".png", ".jpg")) or ".." in name.split("/"):
            return None
        if name.startswith("assets/"):
            p = pkg._assets_dir(self.tid) / name[len("assets/"):]
            return p if pkg._dentro(p, pkg._assets_dir(self.tid)) and p.exists() else None
        if "/" in name:
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
<title>Review miniaturas</title>
<style>
 :root{color-scheme:dark}
 body{background:#0f0f12;color:#eee;font-family:system-ui,sans-serif;margin:0;padding:20px}
 h1{font-size:18px;margin:0 0 4px} h2{font-size:14px;color:#9ad;margin:14px 0 8px}
 .err{background:#5a1d1d;border:1px solid #a33;color:#fdd;padding:10px 14px;border-radius:8px;margin:10px 0;display:none}
 .top{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:10px 0}
 .paqs{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:18px}
 .paq{background:#17171c;border:1px solid #2a2a30;border-radius:10px;padding:14px 16px}
 .paq img{width:100%;aspect-ratio:16/9;object-fit:cover;background:#000;border-radius:8px;border:1px solid #333;display:block}
 .nofoto{aspect-ratio:16/9;background:#000;border-radius:8px;border:1px dashed #633;color:#fbb;display:flex;align-items:center;justify-content:center;padding:12px;font-size:12px;text-align:center}
 textarea,input[type=text],select{width:100%;box-sizing:border-box;background:#0c0c0f;color:#eee;border:1px solid #333;border-radius:6px;padding:8px;font:inherit}
 button{background:#e0b020;color:#000;border:0;border-radius:6px;padding:9px 13px;font-weight:700;cursor:pointer;margin-top:8px}
 button.sec{background:#2a2a36;color:#ddd}
 button:disabled{opacity:.5;cursor:wait}
 label{font-size:12px;color:#bbb;display:block;margin:8px 0 3px}
 .muted{color:#888;font-size:12px}
 .mono{font-family:ui-monospace,monospace;font-size:12px}
 .aviso{color:#fc6;font-size:12px}
 .datos{font-size:12px;color:#cdd;margin:4px 0 0 0;padding-left:16px}
 .ancla{font-size:12px;color:#8c8;font-style:italic}
 .row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
 .row > *{margin-top:6px}
 .szbtn{width:38px;padding:8px 0;margin:0;text-align:center}
 .szval{font-family:ui-monospace,monospace;font-size:13px;color:#cdd;min-width:44px;text-align:center}
 #preview img{width:100%;max-width:640px;border-radius:8px;border:1px solid #333;margin-top:8px;display:block}
 .desc{white-space:pre-wrap;font-size:13px;color:#cdd;line-height:1.4}
</style></head><body>
<h1>Review de miniaturas — <span id="tid" class="muted"></span></h1>
<div class="top">
  <button id="nuevosbtn" onclick="nuevos()">3 PAQUETES NUEVOS</button>
  <span id="genstate" class="muted"></span>
</div>
<div id="err" class="err"></div>
<div id="paqs" class="paqs"></div>
<h2>Último compuesto</h2>
<div id="preview" class="muted">(todavía nada)</div>
<h2>Descripción</h2>
<div id="desc" class="desc"></div>
<h2>Tags</h2>
<div id="tags" class="mono"></div>
<script>
let lastRev=null, latest=null, sizeFactor=1.0;
function esc(s){const d=document.createElement('div');d.textContent=s==null?'':s;return d.innerHTML;}
function bumpSize(dir){
  sizeFactor=Math.min(1.6, Math.max(0.7, Math.round((sizeFactor+dir*0.15)*100)/100));
  document.querySelectorAll('.szval').forEach(e=>e.textContent=sizeFactor.toFixed(2)+'x');
}
function baseOptions(p, bases){
  let opts=[];
  if(p.foto) opts.push('<option value="'+esc(p.foto)+'"'+(p.base===p.foto?' selected':'')+'>'+esc(p.foto)+' (la foto del paquete)</option>');
  for(const b of bases){ opts.push('<option value="'+esc(b)+'"'+(p.base===b?' selected':'')+'>'+esc(b)+'</option>'); }
  if(p.base && p.base!==p.foto && !bases.includes(p.base)) opts.unshift('<option value="'+esc(p.base)+'" selected>'+esc(p.base)+'</option>');
  return opts.join('');
}
function renderPaqs(st){
  const g=document.getElementById('paqs');
  g.innerHTML = st.paquetes.map(p=>{
    const img = p.img ? '<img src="'+p.img+'?t='+p.mtime+'">' : '<div class="nofoto">sin foto'+(p.motivo_sin_foto?': '+esc(p.motivo_sin_foto):'')+'</div>';
    const datos = Object.keys(p.datos||{}).map(k=>'<li><span class="mono">'+esc(k)+'</span>: '+esc(p.datos[k])+'</li>').join('');
    const avisos = (p.avisos||[]).map(a=>'<div class="aviso">'+esc(a)+'</div>').join('');
    return '<div class="paq" data-n="'+p.n+'">'
      +'<div class="muted">paquete '+String(p.n).padStart(2,'0')+' · estrategia '+esc(p.estrategia)+' · paga el cap '+esc(p.cap_que_paga)+'</div>'
      +img
      +'<label>Título (<span id="cnt'+p.n+'">'+p.chars+'</span> caracteres)</label>'
      +'<input type="text" id="tit'+p.n+'" value="'+esc(p.titulo)+'" oninput="document.getElementById(\'cnt'+p.n+'\').textContent=this.value.length">'
      +'<label>Texto de la miniatura (2-4 palabras)</label>'
      +'<input type="text" id="txt'+p.n+'" value="'+esc(p.texto)+'">'
      +'<div class="ancla">ancla: «'+esc(p.ancla)+'»</div>'
      +'<ul class="datos">'+datos+'</ul>'
      +avisos
      +'<label>Base</label><select id="base'+p.n+'">'+baseOptions(p, st.bases)+'</select>'
      +'<div class="row">'
      +'<button class="sec" onclick="guardar('+p.n+')">GUARDAR (recompone)</button>'
      +'<button class="sec" onclick="rehacer('+p.n+')" '+(st.generating?'disabled':'')+'>REHACER FOTO</button>'
      +'</div>'
      +'<div class="row"><select id="focus'+p.n+'" style="width:auto"><option value="center">center</option><option value="top">top</option><option value="bottom">bottom</option></select>'
      +'<select id="fill'+p.n+'" style="width:auto"><option value="blanco">blanco</option><option value="amarillo">amarillo</option><option value="rojo">rojo</option></select>'
      +'<button class="szbtn sec" onclick="bumpSize(-1)">A−</button><span class="szval">'+sizeFactor.toFixed(2)+'x</span><button class="szbtn sec" onclick="bumpSize(1)">A+</button>'
      +'<button onclick="componer('+p.n+')">COMPONER FINAL</button></div>'
      +'</div>';
  }).join('') || '<div class="muted">(sin paquetes — usá 3 PAQUETES NUEVOS)</div>';
}
async function refresh(){
  let st; try{ st=await (await fetch('/state')).json(); }catch(e){ return; }
  latest=st;
  document.getElementById('tid').textContent=st.tid;
  const err=document.getElementById('err');
  if(st.last_error){err.style.display='block';err.textContent='⚠ '+st.last_error;}else{err.style.display='none';}
  document.getElementById('genstate').textContent=st.generating?'· generando (Opus + fotos)…':'';
  document.getElementById('nuevosbtn').disabled=st.generating;
  if(st.rev!==lastRev || st.generating!==lastGen){ renderPaqs(st); lastRev=st.rev; lastGen=st.generating; }
  document.getElementById('desc').textContent=st.descripcion||'';
  document.getElementById('tags').textContent=(st.tags||[]).join(', ');
}
let lastGen=null;
async function post(url, body){ return await (await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})).json(); }
async function nuevos(){ document.getElementById('nuevosbtn').disabled=true; await post('/nuevos',{}); setTimeout(refresh,400); }
async function rehacer(n){ await post('/rehacer_foto',{n}); setTimeout(refresh,400); }
async function guardar(n){
  const r=await post('/editar',{n, titulo:document.getElementById('tit'+n).value, texto:document.getElementById('txt'+n).value, base:document.getElementById('base'+n).value});
  if(r.error){alert('No se pudo guardar: '+r.error);return;}
  lastRev=null; refresh();
}
async function componer(n){
  await guardar(n);
  const r=await post('/compose',{n, focus:document.getElementById('focus'+n).value, fill:document.getElementById('fill'+n).value, size_factor:sizeFactor});
  const pv=document.getElementById('preview');
  if(r.error){pv.innerHTML='<div class="err" style="display:block">⚠ '+esc(r.error)+'</div>';}
  else{pv.innerHTML='<div class="muted">'+esc(r.thumb)+' · tamaño '+sizeFactor.toFixed(2)+'× · CHECKLIST escrito</div><img src="/img/'+encodeURIComponent(r.thumb)+'?t='+Date.now()+'">';}
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
                p = self.state.resolve_image(unquote(route[len("/img/"):]))
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
            if route == "/nuevos":
                started = self.state.start_first_batch()
                self._json({"started": started, "busy": not started})
            elif route == "/rehacer_foto":
                started = self.state.start_rehacer_foto(int(body.get("n")))
                self._json({"started": started, "busy": not started})
            elif route == "/editar":
                self._json(self.state.editar(int(body.get("n")), body.get("titulo"), body.get("texto"),
                                             body.get("base") or None))
            elif route == "/compose":
                self._json(self.state.compose(int(body.get("n")), body.get("focus", "center"),
                                              body.get("fill", pkg.THUMB_FILL_DEFAULT),
                                              size_factor=float(body.get("size_factor", 1.0) or 1.0)))
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

    auto_generate_if_empty (HANDOFF_136b / F58): si falta metadata con `paquetes` (candidates_ready=False), dispara
    la primera tanda (N_PAQUETES paquetes + fotos) en background al arrancar — así un click en MINIATURAS del QA
    Studio genera solo. Idempotente: con paquetes ya en disco no dispara (fase3 corre run_candidates ANTES → no se
    ve afectado). El puerto se bindea primero, la generación es en thread → el form responde al toque."""
    Handler.state = ReviewState(tid, video_path=video_path, on_compose=on_compose)
    if port is None:
        port = _free_port()
    httpd = ThreadingHTTPServer((HOST, port), Handler)
    url = f"http://{HOST}:{port}/"
    print("─" * 60)
    print(f"  Form de review de miniaturas — {tid}")
    print(f"  ▶ {url}    (Ctrl+C para frenar)")
    print("─" * 60)
    if auto_generate_if_empty and not pkg.candidates_ready(tid):
        if Handler.state.start_first_batch():
            print(f"  🖼 sin paquetes (candidates_ready=False) → generando la primera tanda "
                  f"({pkg.N_PAQUETES} paquetes + fotos) en background…")
    if open_browser:
        pkg._open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  frenado.")
        httpd.shutdown()
