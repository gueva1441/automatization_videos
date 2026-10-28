"""F5d+ (producción de Orleans v2): comillas solo para citas, retoque de caps sueltos, G1 crítico sobre el bloque
dibujado, G2 cuerpo del titular. Sin red."""
from __future__ import annotations

from pathlib import Path

from script_engine import gfx_critic as gc
from script_engine import m05_narrative as mn
from script_engine.gfx_project import HEAD_STEPS, archive_head_px

POOL = {"datos": [{"id": "D01", "texto": "517 reclusos no estaban contabilizados", "tipo": "cifra", "valor": "517"}],
        "cronologia": [], "lugares": [], "personajes": [],
        "citas": [{"id": "Q01", "texto": "Están en la cárcel, hombre. Mienten", "autor": "Sheriff Gusman"}]}


def test_comillas_solo_para_citas_del_pool():
    t = ('El sheriff dijo: "Están en la cárcel, hombre. Mienten". Y "El sheriff de la cárcel declaró que ningún '
         'preso murió". En la sección "Templeman III" hubo cadáveres.')
    assert mn.false_quotes(t, POOL) == ["El sheriff de la cárcel declaró que ningún preso murió"]


def test_g2_el_titular_baja_un_cuerpo_y_no_se_corta():
    px, k = archive_head_px("las aguas residuales refluyen", 2560, 1440)
    assert k == 0
    long = "palabra " * 60                                          # no entra al cuerpo normal en un cuadro bajo
    px2, k2 = archive_head_px(long.strip(), 2560, 700)
    assert k2 >= 1 and px2 < px and px2 >= round(px * HEAD_STEPS[-1]) - 1


