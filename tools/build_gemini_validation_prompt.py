"""
build_gemini_validation_prompt.py — Combina PROMPT + dump de evidencia (READ-ONLY, $0).

Lee data/topic_evidence_dump.md (generado por dump_topic_evidence.py) y escribe
data/gemini_validation_prompt.txt = bloque PROMPT literal + separador + dump íntegro.

NO modifica el .md ni topics_db.json. NO llama APIs. Solo escribe el .txt final.

Uso:
    python tools/build_gemini_validation_prompt.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DUMP_FILE = DATA_DIR / "topic_evidence_dump.md"
OUT_FILE = DATA_DIR / "gemini_validation_prompt.txt"

PROMPT = """\
Sos un analista de estrategia de contenido para un canal faceless de YouTube en
español, nicho historia oscura / desastres / misterio, formato documental de 8-10 min.

Abajo, después de la línea de separación, te paso la evidencia COMPLETA de 8 temas
candidatos, extraída del scraping real de mi pipeline: nombres de los videos virales
en inglés, vistas crudas, ratio de outlier, mediana del canal, antigüedad del viral,
label de saturación en español, títulos en español encontrados, y los hooks generados.

REGLAS DURAS PARA TU ANÁLISIS:
- NO tenés acceso a YouTube en vivo. NO inventes vistas, títulos ni competencia que no
  estén en los datos de abajo. Si un dato falta, decí "dato no disponible". Trabajá
  SOLO con lo que está abajo.
- Razoná tema por tema, mostrando los números reales que justifican tu veredicto.

CRITERIOS DE EVALUACIÓN:

1. DEMANDA REAL vs RATIO INFLADO. Un outlier_ratio altísimo (ej. 185x) sobre una
   channel_median chica (ej. 2.000 vistas) NO es demanda probada — es un video que
   pegó de casualidad en un canal diminuto. En cambio, vistas absolutas altas (1M+)
   sobre un canal de mediana grande = demanda sostenida real. Para cada tema decí cuál
   de los dos casos es, citando views + ratio + channel_median.

2. HUECO ES vs FORMATO SATURADO. Un es_gap VACÍO/HUECO por keyword no garantiza hueco
   real si el TEMA es genérico (ej. "lugares abandonados", "sitios militares América").
   Ese formato genérico suele estar saturado aunque la frase exacta no aparezca.
   Penalizá los temas genéricos. Premiá las historias específicas y nombrables: un
   lugar concreto, un crimen concreto, una fecha concreta, un nombre propio.

3. ÁNGULO NARRATIVO. Mirá el hook/mystery/reveal. ¿Ancla una historia específica y
   fuerte, o es vago / conspiranoico / tipo listicle "top 10"? Un hook de OVNIs o de
   "top 10" es señal de tema débil para un documental serio.

4. KEYWORDS CONTAMINADAS. Si la search_keyword no tiene relación con el tema (ej. un
   anuncio de alquiler vacacional, una excursión turística), marcá el tema como NO
   confiable: el score se calculó sobre data equivocada, no sobre el tema real.

FORMATO DE TU RESPUESTA:
- Por cada uno de los 8 temas: una línea de veredicto tuyo [CONFIRMO ORO / DUDOSO /
  DESCARTAR] + 2-3 frases citando los números reales que lo justifican.
- Al final: ranking de los 3 mejores candidatos REALES para producir primero, con
  justificación corta de por qué cada uno y en ese orden.

═══════════════════════════════════════════════════════════════════════
DATA DE LOS 8 TEMAS (scraping real del pipeline — NO inventar nada fuera de esto):
═══════════════════════════════════════════════════════════════════════
"""


def main() -> None:
    if not DUMP_FILE.exists():
        print(f"[ERROR] no existe {DUMP_FILE}")
        print("        corré primero: python tools/dump_topic_evidence.py")
        return

    dump = DUMP_FILE.read_text(encoding="utf-8")
    content = PROMPT + "\n" + dump
    OUT_FILE.write_text(content, encoding="utf-8")

    print(f"[OK] Archivo : {OUT_FILE}")
    print(f"[OK] Tamaño  : {len(content)} caracteres ({len(dump)} del dump embebido)")


if __name__ == "__main__":
    main()
