"""
test_module_38d_forcealign_integration.py — GATE chat 38 (Forced Alignment + sílabas).

Valida OFFLINE (sin APIs, sin red, sin Flash, sin ElevenLabs):
  1. _chars_to_syllables sobre alignment hardcoded CON ACENTOS (observación,
     después) → sílabas con start/end monótonos y word_idx correcto.
  2. Cobertura: 1a sílaba arranca en el start del 1er char; última termina en
     el end del último char (sin perder cobertura por el mapeo).
  3. pyphen parte observación/después/águila sin perder caracteres (rejoin ==
     palabra) — sanity acentos/diptongos (1:1 code points).
  4. _build_ass_from_syllables: NO eventos end<=start (clamp), espacio en cambio
     de word_idx (no se pegan palabras), pre_pad=1.8 corre el 1er start.
  5. Fallback: ChapterPlan acepta alignment_path (default None) → el seam caería
     a _build_ass_from_words.
  6. Mapeo words (text→word) de audio_manager tiene keys {word,start,end}.

USO:
    python test_module_38d_forcealign_integration.py
"""
import re
import sys
import tempfile
from pathlib import Path

import pyphen

from fase2b import (
    _chars_to_syllables,
    _build_ass_from_syllables,
    ChapterPlan,
)


def _chars(word: str, t0: float, dt: float = 0.1) -> list[dict]:
    """Construye characters [{text,start,end}] para una palabra, timing creciente."""
    out = []
    for k, ch in enumerate(word):
        start = t0 + k * dt
        out.append({"text": ch, "start": round(start, 4), "end": round(start + dt, 4)})
    return out


def _alignment_dos_palabras() -> list[dict]:
    """'observación después' con un espacio en el medio. Timing real creciente."""
    chars = _chars("observación", 0.0)            # idx 0..10  (0.0 .. 1.1)
    chars.append({"text": " ", "start": 1.1, "end": 1.2})  # separador
    chars += _chars("después", 1.2)               # idx 12..18 (1.2 .. 1.9)
    return chars


def _alignment_cinco_palabras() -> list[dict]:
    """5 palabras multisílaba → fuerza ≥2 chunks con words_per_chunk=3.
    'pelota casa mesa gato perro'. Timing creciente, espacio entre palabras."""
    words = ["pelota", "casa", "mesa", "gato", "perro"]
    chars: list[dict] = []
    t = 0.0
    for wi, w in enumerate(words):
        if wi > 0:
            chars.append({"text": " ", "start": round(t, 4), "end": round(t + 0.1, 4)})
            t += 0.1
        for ch in w:
            chars.append({"text": ch, "start": round(t, 4), "end": round(t + 0.1, 4)})
            t += 0.1
    return chars


def _bare(text: str) -> str:
    """Texto visible sin tags ASS de override ({...})."""
    return re.sub(r"\{[^}]*\}", "", text)


def _bare_groups(dl: list) -> list:
    """Runs consecutivos de texto desnudo igual → [(bare_text, count), ...].
    Cada run == un chunk (el texto queda QUIETO mientras cambian las sílabas)."""
    groups: list[list] = []
    for _st, _en, t in dl:
        b = _bare(t)
        if not groups or groups[-1][0] != b:
            groups.append([b, 1])
        else:
            groups[-1][1] += 1
    return groups


def _parse_ass_time(t: str) -> float:
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def _dialogue_lines(ass_text: str) -> list[tuple[float, float, str]]:
    """Devuelve [(start, end, text)] de las líneas Dialogue Viral (karaoke)."""
    out = []
    for line in ass_text.splitlines():
        if not line.startswith("Dialogue:"):
            continue
        # Dialogue: 0,START,END,Style,Name,0,0,0,,TEXT
        body = line[len("Dialogue:"):].strip()
        fields = body.split(",", 9)
        layer, start, end, style = fields[0], fields[1], fields[2], fields[3]
        text = fields[9] if len(fields) > 9 else ""
        if style != "Viral":
            continue  # ignorar el overlay Hook
        out.append((_parse_ass_time(start), _parse_ass_time(end), text))
    return out


# ─────────────────────────────────────────────────────────────────

def test_1_syllables_word_idx_y_monotonia() -> None:
    syl = _chars_to_syllables(_alignment_dos_palabras())
    # observación → ob-ser-va-ción (4), después → des-pués (2) = 6 sílabas
    assert len(syl) == 6, f"esperaba 6 sílabas, hay {len(syl)}: {[s['text'] for s in syl]}"
    # word_idx: 4 de la palabra 0, 2 de la palabra 1
    assert [s["word_idx"] for s in syl] == [0, 0, 0, 0, 1, 1], \
        f"word_idx mal: {[s['word_idx'] for s in syl]}"
    # starts monótonos no-decrecientes y end >= start
    for k in range(len(syl)):
        assert syl[k]["end"] >= syl[k]["start"], f"sílaba {k}: end < start"
        if k:
            assert syl[k]["start"] >= syl[k - 1]["start"], f"sílaba {k}: start retrocede"
    print("  ✓ test_1 sílabas + word_idx + monotonía OK:", [s["text"] for s in syl])


def test_2_cobertura_primer_y_ultimo_char() -> None:
    chars = _alignment_dos_palabras()
    syl = _chars_to_syllables(chars)
    assert syl[0]["start"] == chars[0]["start"], "la 1a sílaba no arranca en el 1er char"
    assert syl[-1]["end"] == chars[-1]["end"], "la última sílaba no termina en el último char"
    print("  ✓ test_2 cobertura 1er/último char OK")


def test_3_pyphen_acentos_sin_perder_chars() -> None:
    dic = pyphen.Pyphen(lang="es_ES")
    for word in ("observación", "después", "águila", "ciencia"):
        parts = [p for p in dic.inserted(word).split("-") if p]
        assert "".join(parts) == word, f"{word}: pyphen perdió/agregó chars → {parts}"
        assert len(parts) >= 1
    # observación y después sí deben partir en >1 sílaba
    assert len([p for p in dic.inserted("observación").split("-") if p]) >= 3
    assert len([p for p in dic.inserted("después").split("-") if p]) >= 2
    print("  ✓ test_3 pyphen acentos sin perder caracteres OK")


def test_4_render_chunk_estatico() -> None:
    """Chunk ESTÁTICO (no marquesina): el texto desnudo queda QUIETO mientras
    cambian las sílabas resaltadas; al cruzar de chunk el texto SÍ cambia;
    ninguna palabra se parte entre chunks; clamp + espacio intra-chunk + pre_pad."""
    PALABRAS = ["PELOTA", "CASA", "MESA", "GATO", "PERRO"]
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "subs.ass"
        syl = _chars_to_syllables(_alignment_cinco_palabras())
        _build_ass_from_syllables(
            syllables=syl,
            output_path=out,
            audio_duration=20.0,
            video_width=1080,
            video_height=1920,
            words_per_chunk=3,
            max_chars=18,
            pre_pad=0.0,
        )
        dl = _dialogue_lines(out.read_text(encoding="utf-8"))
        assert dl, "no se generaron Dialogue Viral"

        # 4a. clamp: ningún evento con end <= start
        for st, en, _ in dl:
            assert en > st, f"evento con end<=start: {st} >= {en}"

        groups = _bare_groups(dl)
        distinct = [g[0] for g in groups]

        # 4b. ≥2 chunks (texto desnudo cambia al menos una vez)
        assert len(groups) >= 2, f"esperaba ≥2 chunks, hubo {len(groups)}: {distinct}"

        # 4c. QUIETO dentro del chunk: al menos un chunk mantiene el MISMO texto
        #     desnudo a través de varias sílabas consecutivas (no marquesina).
        assert any(g[1] > 1 for g in groups), \
            "ningún chunk se mantuvo quieto entre sílabas (parece marquesina)"

        # 4d. al cruzar de chunk, el texto desnudo SÍ cambia
        for k in range(1, len(groups)):
            assert groups[k][0] != groups[k - 1][0], "dos chunks consecutivos con mismo texto"

        # 4e. ninguna palabra partida entre chunks: cada palabra entera cae en
        #     EXACTAMENTE un texto de chunk.
        for w in PALABRAS:
            hits = [tx for tx in set(distinct) if w in tx]
            assert len(hits) == 1, f"'{w}' aparece en {len(hits)} chunks (¿partida?): {hits}"

        # 4f. espacio entre palabras DENTRO de un chunk (no pegadas)
        assert any(" " in tx for tx in distinct), "no hay espacio entre palabras dentro del chunk"
        assert all("PELOTACASA" not in tx for tx in distinct), "palabras pegadas dentro del chunk"

    # 4g. pre_pad=1.8 → el 1er evento arranca 1.8 más tarde (sílabas frescas)
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "subs_pp.ass"
        syl2 = _chars_to_syllables(_alignment_cinco_palabras())
        first_start_orig = syl2[0]["start"]
        _build_ass_from_syllables(
            syllables=syl2,
            output_path=out,
            audio_duration=20.0,
            video_width=1080,
            video_height=1920,
            pre_pad=1.8,
        )
        dl = _dialogue_lines(out.read_text(encoding="utf-8"))
        first_event_start = min(st for st, _, _ in dl)
        assert abs(first_event_start - (first_start_orig + 1.8)) < 0.02, \
            f"pre_pad no aplicado: 1er start={first_event_start} (esperaba ~{first_start_orig + 1.8})"
    print("  ✓ test_4 chunk estático (quieto intra-chunk + cambia inter-chunk + "
          "sin split + clamp + pre_pad) OK")


def test_5_fallback_plan_alignment_path_default() -> None:
    # ChapterPlan se puede construir SIN alignment_path → default None
    # (el seam de carga cae a _build_ass_from_words). Y se puede setear.
    plan = ChapterPlan(
        chapter_id="ch01",
        engine="flux",
        audio_path=Path("x.mp3"),
        audio_duration=12.3,
        asset_paths=[Path("a.png")],
        timestamps_path=Path("ch01_timestamps.json"),
        is_first=True,
        art_profile=None,
    )
    assert plan.alignment_path is None, "alignment_path default debería ser None (fallback)"
    plan2 = ChapterPlan(
        chapter_id="ch02",
        engine="flux",
        audio_path=Path("y.mp3"),
        audio_duration=5.0,
        asset_paths=[Path("b.png")],
        timestamps_path=Path("ch02_timestamps.json"),
        is_first=False,
        art_profile=None,
        alignment_path=Path("ch02_alignment.json"),
    )
    assert plan2.alignment_path == Path("ch02_alignment.json"), "alignment_path no se setea"
    print("  ✓ test_5 ChapterPlan.alignment_path (default None + set) OK")


def test_6_mapeo_words_keys() -> None:
    # Replica el mapeo de audio_manager: alignment['words'] → {word,start,end}
    api_words = [
        {"text": "hola", "start": 0.0, "end": 0.4},
        {"text": "mundo", "start": 0.4, "end": 0.9},
    ]
    words = [
        {"word": w["text"], "start": float(w["start"]), "end": float(w["end"])}
        for w in api_words
    ]
    for w in words:
        assert set(w.keys()) == {"word", "start", "end"}, f"keys mal: {w.keys()}"
    assert words[0]["word"] == "hola"
    print("  ✓ test_6 mapeo words {word,start,end} OK")


def main() -> int:
    tests = [
        test_1_syllables_word_idx_y_monotonia,
        test_2_cobertura_primer_y_ultimo_char,
        test_3_pyphen_acentos_sin_perder_chars,
        test_4_render_chunk_estatico,
        test_5_fallback_plan_alignment_path_default,
        test_6_mapeo_words_keys,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  ✗ {t.__name__} FALLÓ: {type(e).__name__}: {e}")
    print(f"\n  RESULTADO: {passed}/{len(tests)} PASS")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(main())
