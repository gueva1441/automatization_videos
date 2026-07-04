"""
test_module_135_thumbs.py — HANDOFF_135 (offline, sin socket real donde se pueda).

1. serve(port=1234, open_browser=False): bind al puerto pedido y pkg._open NO llamado;
   open_browser=True → SÍ llama _open.
2. _thumbs_start() doble: 2do call con proc vivo → 'already' (no relanza); proc muerto → relanza.
3. _port_responds(): cerrado → False, listening → True, None → False.

USO:
    python test_module_135_thumbs.py
"""
import socket
import sys

import qa_studio_server as q
import script_engine.m09_review_server as rs
import script_engine.m09_packaging as pkg


def _check(c, m, fails):
    if not c:
        fails.append(m)


class _FakeHTTPD:
    def __init__(self, addr, handler):
        _FakeHTTPD.addr = addr

    def serve_forever(self):
        return  # no bloquea (el test no corre un server real)

    def shutdown(self):
        pass


class _FakeProc:
    def __init__(self):
        self.alive = True
        self.terminated = False
        self.killed = False

    def poll(self):
        return None if self.alive else 0

    def terminate(self):
        self.terminated = True
        self.alive = False

    def kill(self):
        self.killed = True
        self.alive = False

    def wait(self, timeout=None):
        return 0


def main() -> int:
    fails: list[str] = []

    # ── (1) serve() parametrizable ──
    o_httpd, o_state, o_open = rs.ThreadingHTTPServer, rs.ReviewState, pkg._open
    opened: list = []
    rs.ThreadingHTTPServer = _FakeHTTPD
    rs.ReviewState = lambda *a, **k: object()
    pkg._open = lambda url: opened.append(url)
    try:
        rs.serve("tid_test", port=1234, open_browser=False)
        _check(_FakeHTTPD.addr == (rs.HOST, 1234), f"(1) bind != 1234: {_FakeHTTPD.addr}", fails)
        _check(opened == [], "(1) open_browser=False igual llamó a _open", fails)
        rs.serve("tid_test", port=1235, open_browser=True)
        _check(_FakeHTTPD.addr == (rs.HOST, 1235), "(1) 2do serve no bindeó 1235", fails)
        _check(len(opened) == 1, "(1) open_browser=True no llamó a _open exactamente 1 vez", fails)
    finally:
        rs.ThreadingHTTPServer, rs.ReviewState, pkg._open = o_httpd, o_state, o_open

    # ── (2) _thumbs_start() idempotente POR TID (HANDOFF_135b) ──
    o_popen = q.subprocess.Popen
    o_thumbs = dict(q._THUMBS)
    o_tid = q.TOPIC_ID
    procs: list = []

    def _fake_popen(*a, **k):
        p = _FakeProc()
        procs.append(p)
        return p

    q.subprocess.Popen = _fake_popen
    try:
        q.TOPIC_ID = "AAAAAAAA-topic-a"
        q._THUMBS.update(proc=None, port=None, tid=None)
        r1 = q._thumbs_start()
        _check(r1.get("started") and r1.get("port"), f"(2) 1er start sin 'started'/port: {r1}", fails)
        _check(q._THUMBS["tid"] == "AAAAAAAA-topic-a", "(2) no guardó el tid al lanzar", fails)

        # proc vivo + MISMO tid → already, terminate NO llamado (caso feliz, regresión)
        r2 = q._thumbs_start()
        _check(r2.get("already") and r2.get("port") == r1.get("port"),
               f"(2) mismo tid no dio 'already' mismo port: {r2}", fails)
        _check(not procs[0].terminated, "(2) mató el server del caso feliz (mismo tid)", fails)
        _check(len(procs) == 1, f"(2) relanzó con mismo tid (procs={len(procs)})", fails)

        # proc vivo + tid DISTINTO → relaunched, terminate SÍ, tid actualizado
        q.TOPIC_ID = "BBBBBBBB-topic-b"
        r3 = q._thumbs_start()
        _check(r3.get("relaunched") and r3.get("port"), f"(2) tid distinto no dio 'relaunched': {r3}", fails)
        _check(procs[0].terminated, "(2) NO mató el server viejo al cambiar de topic (bug 135b)", fails)
        _check(len(procs) == 2, f"(2) no spawneó uno nuevo al cambiar topic (procs={len(procs)})", fails)
        _check(q._THUMBS["tid"] == "BBBBBBBB-topic-b", "(2) no actualizó _THUMBS['tid']", fails)

        # proc muerto → started (camino sin relaunch)
        procs[1].alive = False
        r4 = q._thumbs_start()
        _check(r4.get("started"), f"(2) proc muerto no relanzó 'started': {r4}", fails)
        _check(len(procs) == 3, f"(2) no spawneó tras muerte (procs={len(procs)})", fails)
    finally:
        q.subprocess.Popen = o_popen
        q._THUMBS.update(o_thumbs)
        q.TOPIC_ID = o_tid

    # ── (3) _port_responds() ──
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0)); srv.listen(1)
    lp = srv.getsockname()[1]
    _check(q._port_responds(lp) is True, "(3) listening → debería True", fails)
    srv.close()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0)); fp = s.getsockname()[1]; s.close()
    _check(q._port_responds(fp) is False, "(3) puerto cerrado → debería False", fails)
    _check(q._port_responds(None) is False, "(3) None → debería False", fails)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] serve() parametrizable, _thumbs_start idempotente, _port_responds correcto")
    return 0


if __name__ == "__main__":
    sys.exit(main())
