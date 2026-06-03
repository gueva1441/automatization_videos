"""
_lab_vsr_chat41.py — LAB aislado (chat 41). NO toca el pipeline. $0 LLM/$0 API. Solo
scraping. No escribe a disco.

Valida el filtro OUTLIER de Mode A vía VSR = views_del_video / suscriptores_del_canal,
100% scrapetube por la puerta que FUNCIONA (búsqueda). Reemplaza el filtro de vistas
absolutas (≥1M). NO es un modo nuevo.

Hechos confirmados en vivo (chat 41 — NO re-descubrir):
  - get_channel → MUERTO (cuelga/KeyError continuationCommand). get_playlist → sin views.
  - get_search(results_type="channel") → FUNCIONA y trae los subs.
  - channelId del video: vid["longBylineText"]["runs"][0]["navigationEndpoint"]
        ["browseEndpoint"]["browseId"];  nombre: ...["runs"][0]["text"].
  - subs (campos CRUZADOS en scrapetube): chan["channelId"]=UC...,
        chan["subscriberCountText"]["simpleText"]=@handle (NO son subs),
        chan["videoCountText"]["simpleText"]="16.8M subscribers" (ACÁ están los subs,
        abreviado → muerde el bug del decimal),
        chan["videoCountText"]["accessibility"]["accessibilityData"]["label"]
            ="16.8 million subscribers" (más limpio, fallback).

Reusa de youtube_scanner: _proxies_dict, detect_language, _parse_views_scrapetube (buggy,
solo para mostrar el bug lado a lado). El parser CORREGIDO vive acá (solo del lab).

USO:
    python _lab_vsr_chat41.py            # blocks 0/1/2 (scraping real)
    python _lab_vsr_chat41.py --smoke    # solo funciones puras, sin red
"""
from __future__ import annotations

import re
import sys
import time

# Forzar UTF-8 (Windows cp1252).
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────────
TEST_QUERY = "declassified ocean phenomena"
SEARCH_LIMIT = 12
N_CANDIDATES = 5
VSR_MIN = 5.0          # arranque; 10x = joya fuerte. Omar calibra de OJO con la tabla.
ABS_FLOOR = 80_000     # piso absoluto: demanda real, corta micro-canales
CHAN_SEARCH_LIMIT = 5  # cuántos canales pedir al resolver subs (matchear por channelId)
SLEEP_SEC = 2.0        # anti-ban


# ─────────────────────────────────────────────────────────────────
#  FUNCIONES PURAS (las ejerce el smoke — NO reimplementar en el test)
# ─────────────────────────────────────────────────────────────────

def parse_count_fixed(text: str) -> int:
    """
    Parser CORREGIDO (solo del lab). Saca comas y palabras ('subscribers', 'views',
    'million', 'subscriber'), captura [\\d.]+ como float, multiplica por k/m/b. Maneja
    también el label 'X million subscribers'. Así "16.8M"→16_800_000 y
    "1.99 million"→1_990_000. (El buggy de youtube_scanner hace .replace(".","") →
    "168m" = 168M.)
    """
    if not text:
        return 0
    t = text.lower().replace(",", "")
    # "1.99 million subscribers" → tratar 'million/thousand/billion' como sufijo
    word_mult = {"thousand": 1_000, "million": 1_000_000, "billion": 1_000_000_000}
    for word, mult in word_mult.items():
        m = re.search(rf"([\d.]+)\s*{word}", t)
        if m:
            try:
                return int(float(m.group(1)) * mult)
            except ValueError:
                return 0
    # forma abreviada "16.8m" / "250k" / número pelado
    m = re.search(r"([\d.]+)\s*([kmb])?", t)
    if not m:
        return 0
    try:
        number = float(m.group(1))
    except ValueError:
        return 0
    mult = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000, "": 1}
    return int(number * mult.get(m.group(2) or "", 1))


def channel_id_of(vid: dict) -> str | None:
    try:
        cid = (vid["longBylineText"]["runs"][0]["navigationEndpoint"]
               ["browseEndpoint"]["browseId"])
        return cid if isinstance(cid, str) and cid.startswith("UC") else None
    except (KeyError, IndexError, TypeError):
        return None


def channel_name_of(vid: dict) -> str:
    try:
        return vid["longBylineText"]["runs"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return ""


def title_of(vid: dict) -> str:
    try:
        return vid["title"]["runs"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return "<sin título>"


def video_views_text(vid: dict) -> str:
    t = (vid.get("viewCountText") or {}).get("simpleText", "")
    if not t:
        t = (vid.get("shortViewCountText") or {}).get("simpleText", "")
    return t or ""


def subs_text_of(chan: dict) -> tuple[str, str]:
    """Devuelve (simpleText, accessibility_label) de videoCountText — donde viven los
    subs (campo cruzado, ver §1-B). NO subscriberCountText (= @handle)."""
    vct = chan.get("videoCountText") or {}
    simple = vct.get("simpleText", "") or ""
    label = ((vct.get("accessibility") or {}).get("accessibilityData") or {}).get("label", "") or ""
    return simple, label


def parse_subs(chan: dict) -> int:
    """Subs del canal (parser corregido). Prioriza simpleText; si falla, el label."""
    simple, label = subs_text_of(chan)
    n = parse_count_fixed(simple)
    if n <= 0 and label:
        n = parse_count_fixed(label)
    return n


def compute_vsr(views: int, subs: int | None) -> float | None:
    if not subs or subs <= 0:
        return None
    return views / subs


def verdict_new(views: int, vsr: float | None,
                vsr_min: float = VSR_MIN, abs_floor: int = ABS_FLOOR) -> bool:
    """Filtro NUEVO: VSR alto AND piso absoluto. subs no resueltos (vsr None) → no pasa."""
    return vsr is not None and vsr >= vsr_min and views >= abs_floor


def verdict_old(views: int) -> bool:
    return views >= 1_000_000


# ─────────────────────────────────────────────────────────────────
#  SMOKE (sin red)
# ─────────────────────────────────────────────────────────────────

def run_smoke() -> int:
    print("  SMOKE (funciones puras, sin red)")
    fails: list[str] = []

    cases = [
        ("16.8M subscribers", 16_800_000), ("2,005,957 views", 2_005_957),
        ("2.53M subscribers", 2_530_000), ("1.99 million subscribers", 1_990_000),
        ("250K subscribers", 250_000), ("812 subscribers", 812),
    ]
    for text, exp in cases:
        got = parse_count_fixed(text)
        ok = got == exp
        print(f"    parse_count_fixed({text!r}) = {got:,}  esperado {exp:,}  "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"parse {text!r} → {got} != {exp}")

    # VSR + veredictos
    vsr = compute_vsr(500_000, 50_000)
    print(f"    vsr(500k/50k) = {vsr}  esperado 10.0  {'OK' if vsr == 10.0 else 'FAIL'}")
    if vsr != 10.0:
        fails.append(f"vsr = {vsr} != 10.0")
    v1 = verdict_new(500_000, 10.0)
    print(f"    verdict_new(500k, vsr=10) = {v1} (esperado True)  {'OK' if v1 else 'FAIL'}")
    if not v1:
        fails.append("verdict_new(500k,10) debería True")
    # 12k views / 2k subs → vsr 6 pero views<80k → piso corta
    vsr2 = compute_vsr(12_000, 2_000)
    v2 = verdict_new(12_000, vsr2)
    print(f"    verdict_new(12k, vsr={vsr2}) = {v2} (esperado False: ABS_FLOOR corta)  "
          f"{'OK' if v2 is False else 'FAIL'}")
    if v2 is not False:
        fails.append("verdict_new(12k,6) debería False por piso")
    # joya: 200k views / 20k subs → vsr 10 → nuevo True, viejo (≥1M) False
    vsr3 = compute_vsr(200_000, 20_000)
    v3, v3old = verdict_new(200_000, vsr3), verdict_old(200_000)
    print(f"    joya 200k/20k: vsr={vsr3} nuevo={v3} viejo={v3old} "
          f"(nuevo caza lo que el viejo tira)  {'OK' if (v3 and not v3old) else 'FAIL'}")
    if not (v3 and not v3old):
        fails.append("joya 200k: nuevo True / viejo False")
    # subs None → no computa, no pasa
    vsr_none = compute_vsr(5_000_000, None)
    v_none = verdict_new(5_000_000, vsr_none)
    print(f"    subs None → vsr={vsr_none} verdict_new={v_none} (esperado None/False)  "
          f"{'OK' if (vsr_none is None and v_none is False) else 'FAIL'}")
    if not (vsr_none is None and v_none is False):
        fails.append("subs None debería vsr None y verdict False")

    print("  " + "─" * 52)
    if fails:
        print(f"  [SMOKE FAIL] {len(fails)}:")
        for f in fails:
            print(f"    - {f}")
        return 1
    print("  [SMOKE OK] funciones puras del lab VSR validadas.")
    return 0


# ─────────────────────────────────────────────────────────────────
#  BLOQUES CON RED
# ─────────────────────────────────────────────────────────────────

def run_live() -> int:
    import scrapetube
    from script_engine.youtube_scanner import (
        _proxies_dict, _parse_views_scrapetube, detect_language,
    )
    proxies = _proxies_dict()

    # ===== BLOQUE 0 =====
    print("\n" + "=" * 64)
    print("  BLOQUE 0 — sanity de las 2 llamadas que funcionan")
    print("=" * 64)
    try:
        search_vids = list(scrapetube.get_search(
            TEST_QUERY, limit=SEARCH_LIMIT, proxies=proxies))
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ get_search(videos) falló: {type(e).__name__}: {e}")
        return 1
    print(f"  get_search(videos) → {len(search_vids)} videos")
    time.sleep(SLEEP_SEC)
    try:
        chan_test = list(scrapetube.get_search(
            "Linus Tech Tips", limit=3, results_type="channel", proxies=proxies))
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ get_search(channel) falló: {type(e).__name__}: {e}")
        return 1
    print(f"  get_search(channel) → {len(chan_test)} canales")
    if not search_vids or not chan_test:
        print("  ❌ GATE 0 FALLÓ — alguna llamada vacía. FRENO.")
        return 1
    # mostrar el campo cruzado en vivo
    c0 = chan_test[0]
    simple, label = subs_text_of(c0)
    print(f"  ✅ GATE 0 OK. Ejemplo canal: channelId={c0.get('channelId')} "
          f"handle={(c0.get('subscriberCountText') or {}).get('simpleText','')!r}")
    print(f"     subs (videoCountText): simpleText={simple!r} | label={label!r} "
          f"→ parseado={parse_subs(c0):,}")

    # ===== BLOQUE 1 + 2 =====
    print("\n" + "=" * 64)
    print("  BLOQUE 1+2 — resolver subs (VSR) + tabla")
    print("=" * 64)
    candidates = [v for v in search_vids if detect_language(title_of(v)) == "en"][:N_CANDIDATES]
    print(f"  candidatos EN: {len(candidates)} (de {len(search_vids)})")

    subs_cache: dict[str, int | None] = {}
    resolved = 0
    rows: list[dict] = []
    for v in candidates:
        title = title_of(v)
        views = parse_count_fixed(video_views_text(v))
        cid = channel_id_of(v)
        cname = channel_name_of(v)
        subs = None
        if cid:
            if cid not in subs_cache:
                time.sleep(SLEEP_SEC)
                subs_cache[cid] = _resolver_subs(scrapetube, proxies, cid, cname)
            subs = subs_cache[cid]
        if subs:
            resolved += 1
        vsr = compute_vsr(views, subs)
        rows.append({
            "title": title, "channel": cname, "views": views, "subs": subs, "vsr": vsr,
            "old": verdict_old(views), "new": verdict_new(views, vsr),
        })

    print(f"\n  GATE 1: canales que resolvieron subs = {resolved}/{len(candidates)} "
          f"({'OK' if resolved >= 1 else 'FALLÓ'})")
    _print_table(rows)
    # bug del decimal sobre los subs (donde muerde)
    print("\n  Bug del decimal sobre SUBS (abreviados):")
    for r in rows:
        if r["subs"]:
            # re-derivar el texto crudo no lo tenemos acá; mostramos buggy vs fixed conceptual
            pass
    print("  (ver smoke: '16.8M' buggy=168.000.000 vs corregido=16.800.000)")
    print("\n  GATE 2 = de OJO (Omar): ¿VSR alto con views<1M (joyas que el viejo tira)? "
          "¿VSR bajo en gigantes que el viejo dejaba pasar?")
    if resolved == 0:
        print("\n  ⚠ NINGÚN canal resolvió subs → talón del VSR-vía-búsqueda (ver reporte).")
        return 1
    return 0


def _resolver_subs(scrapetube, proxies: dict, channel_id: str, channel_name: str) -> int | None:
    """Busca el canal por NOMBRE (results_type=channel), matchea por channelId EXACTO,
    parsea subs de videoCountText. None si el search del nombre no devuelve ese canal."""
    if not channel_name:
        return None
    try:
        chans = list(scrapetube.get_search(
            channel_name, limit=CHAN_SEARCH_LIMIT, results_type="channel", proxies=proxies))
    except Exception as e:  # noqa: BLE001
        print(f"     ⚠ get_search(channel) falló para {channel_name!r}: {type(e).__name__}")
        return None
    for ch in chans:
        if ch.get("channelId") == channel_id:
            subs = parse_subs(ch)
            return subs if subs > 0 else None
    print(f"     ⚠ subs no resueltos: '{channel_name}' no devolvió {channel_id} "
          f"en {len(chans)} canales")
    return None


def _print_table(rows: list[dict]) -> None:
    print(f"\n  {'título':<40} {'views':>11} {'subs':>12} {'VSR':>7} "
          f"{'viejo':>6} {'nuevo':>6}")
    print("  " + "─" * 88)
    for r in rows:
        title = (r["title"][:38] + "…") if len(r["title"]) > 39 else r["title"]
        subs = f"{r['subs']:,}" if r["subs"] else "—(N/R)"
        vsr = f"{r['vsr']:.1f}x" if r["vsr"] is not None else "—"
        old = "✅" if r["old"] else "·"
        new = "✅" if r["new"] else "·"
        print(f"  {title:<40} {r['views']:>11,} {subs:>12} {vsr:>7} {old:>6} {new:>6}")


def main() -> int:
    if "--smoke" in sys.argv:
        return run_smoke()
    rc = run_smoke()
    if rc != 0:
        print("  smoke falló → no sigo a la red.")
        return rc
    return run_live()


if __name__ == "__main__":
    sys.exit(main())
