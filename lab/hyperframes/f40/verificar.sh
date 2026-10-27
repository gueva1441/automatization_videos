#!/usr/bin/env bash
# F40 (copia del de F39; DECISIONES 00:30: en md5 y tests no se mide RAM ni se cierra nada; amplia con -n auto): verificación de cada commit (/tanda paso 8): md5 de ch02 sin --gfx, suite rápida y suite amplia → lab/hyperframes/f38/<parte>/
set -u
cd /c/CLAUDE_PROJECTS/automatization_videos
parte="${1:?parte (a|b)}"
out="lab/hyperframes/f40/$parte"
mkdir -p "$out"
export PYTHONIOENCODING=utf-8
python fase2b.py ba6c3cac-a091-41c0-8dad-afd2f4364747 --only-cap ch02 --reuse-visuals --sw-encode > "$out/onlycap_ch02_nogfx.log" 2>&1
md5sum output/ba6c3cac-a091-41c0-8dad-afd2f4364747/_fase2b_work/ch02_segment_only.mp4 >> "$out/onlycap_ch02_nogfx.log"
python -m pytest -q test_module_f25c.py test_module_f24.py test_module_f21.py > "$out/suite_rapida.log" 2>&1
python -m pytest -q -n auto test_module_f[0-9]*.py test_module_gfx_*.py test_module_01a*.py test_module_01b*.py test_module_m03_*.py \
  test_module_fase2b_reassemble.py test_module_fase2b_hwencode.py test_module_concat_windowed.py \
  test_module_transition_timeout.py test_constantes_con_origen.py > "$out/suite_amplia.log" 2>&1
echo "md5: $(tail -1 "$out/onlycap_ch02_nogfx.log")"
echo "rapida: $(tail -1 "$out/suite_rapida.log")"
echo "amplia: $(tail -1 "$out/suite_amplia.log")"
grep FAILED "$out/suite_amplia.log"
