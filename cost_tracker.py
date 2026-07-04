"""
Rastreador de costos del pipeline.
- Registra el costo de cada llamada a API
- Acumula costos por video y por corrida
- v2: bucket session_overhead para costos sin video activo
      (descubrimiento Fase 1, research, queries dinámicas)
- Genera reportes en JSON y resumen en consola
- Historial persistente en data/cost_history.json
"""

import json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path

from config import DATA_DIR, pipeline
from error_handler import error_handler, PipelineStage


# Tarifas Gemini POR TOKEN (HANDOFF_133) — USD por 1M tokens, precios lista Google al
# 2026-07-04 (prompt ≤200k). El thinking se COBRA como output. DEFAULTS commiteados acá
# (config.py está gitignored → no viajan); pipeline.costs["gemini_rates_per_1m"] los OVERRIDEA
# por-modelo si existe. "_default" = fallback conservador (tarifa Pro) si el modelo no está.
_DEFAULT_GEMINI_RATES_PER_1M = {
    "gemini-2.5-pro":         {"input": 1.25, "output": 10.00},
    "gemini-2.5-flash":       {"input": 0.30, "output": 2.50},
    "gemini-3-flash-preview": {"input": 0.30, "output": 2.50},
    "_default":               {"input": 1.25, "output": 10.00},
}


def _gemini_rates_for(model: str) -> dict:
    """Tarifa {input,output} del modelo: defaults commiteados + override de config."""
    merged = {**_DEFAULT_GEMINI_RATES_PER_1M, **(pipeline.costs.get("gemini_rates_per_1m") or {})}
    return merged.get(model) or merged.get("_default") or {"input": 1.25, "output": 10.0}


def _gemini_service_name(model: str) -> str:
    """Deriva el nombre de servicio del string del modelo (no hardcodea Pro/Flash —
    mañana cambia la versión). "gemini-2.5-pro" → "Gemini 2.5 Pro"."""
    return (model or "gemini").replace("-", " ").title()


@dataclass
class CostEntry:
    """Una entrada individual de costo."""
    timestamp: str
    stage: str
    service: str
    description: str
    units: float          # cantidad (chars, imágenes, clips, etc.)
    unit_label: str       # "images", "characters", "clips", "calls", "tokens"
    cost_per_unit: float
    total_cost: float
    # ── Telemetría de tokens (HANDOFF_133) — 0 para entries no-Gemini. thinking se
    # factura como output pero se guarda aparte para poder verlo. usage_ok=False marca
    # una llamada cuyo usage_metadata faltó (se cuenta con tokens 0, no se pierde). ──
    tokens_in: int = 0
    tokens_out: int = 0
    tokens_thinking: int = 0
    usage_ok: bool = True


@dataclass
class VideoCostReport:
    """Reporte de costo de un video individual."""
    video_id: str
    created_at: str
    entries: list[CostEntry] = field(default_factory=list)
    total_cost: float = 0.0

    def add(self, entry: CostEntry) -> None:
        self.entries.append(entry)
        self.total_cost += entry.total_cost


class CostTracker:
    """Rastreador de costos por corrida del pipeline."""

    HISTORY_FILE = DATA_DIR / "cost_history.json"

    def __init__(self) -> None:
        self.current_video: VideoCostReport | None = None
        self.session_videos: list[VideoCostReport] = []
        # ── v2: bucket de overhead de sesión (Fase 1, descubrimiento, research) ──
        self.session_overhead: list[CostEntry] = []

    def start_video(self, video_id: str) -> None:
        """Inicia el tracking de un nuevo video."""
        self.current_video = VideoCostReport(
            video_id=video_id,
            created_at=datetime.now().isoformat(),
        )
        error_handler.log_info(
            PipelineStage.COST_TRACKER,
            f"Tracking de costos iniciado para video: {video_id}",
        )

    def end_video(self) -> VideoCostReport | None:
        """Finaliza y guarda el tracking del video actual."""
        if not self.current_video:
            return None
        report = self.current_video
        self.session_videos.append(report)
        self._save_to_history(report)
        error_handler.log_info(
            PipelineStage.COST_TRACKER,
            f"Video {report.video_id} — Costo total: ${report.total_cost:.4f}",
        )
        self.current_video = None
        return report

    # ─── Métodos de registro por servicio ───

    def track_gemini(self, description: str, calls: int = 1) -> None:
        """Registra costo de llamada a Gemini (guiones/research)."""
        cost_per = pipeline.costs["gemini_per_call"]
        self._add_entry(
            stage=PipelineStage.SCRIPT.value,
            service="Gemini",
            description=description,
            units=calls,
            unit_label="calls",
            cost_per_unit=cost_per,
        )

    def track_gemini_tokens(self, description: str, model: str,
                            input_tokens: int, output_tokens: int,
                            thinking_tokens: int = 0, usage_ok: bool = True) -> None:
        """Registra costo de Gemini POR TOKENS (HANDOFF_133). Pro/Flash se distinguen
        por el string del modelo; la tarifa sale de pipeline.costs["gemini_rates_per_1m"].
        El thinking se cobra como output pero se guarda en su propio campo para verlo."""
        rate = _gemini_rates_for(model)
        input_tokens = int(input_tokens or 0)
        output_tokens = int(output_tokens or 0)
        thinking_tokens = int(thinking_tokens or 0)
        billed_out = output_tokens + thinking_tokens   # thinking factura como output
        cost = input_tokens / 1e6 * rate["input"] + billed_out / 1e6 * rate["output"]
        self._add_entry(
            stage=PipelineStage.SCRIPT.value,
            service=_gemini_service_name(model),
            description=description,
            units=input_tokens + billed_out,
            unit_label="tokens",
            cost_per_unit=0.0,          # no aplica (tarifa in/out distinta)
            total_cost=cost,
            tokens_in=input_tokens,
            tokens_out=output_tokens,
            tokens_thinking=thinking_tokens,
            usage_ok=usage_ok,
        )
        # QA form (HANDOFF_133): emitir el costo en vivo → el server lo suma por etapa.
        # No-op fuera del subprocess del form (guardado por QA_FORM adentro del emisor).
        try:
            from qa_form_markers import emit_cost_marker
            emit_cost_marker(model, cost, input_tokens, output_tokens, thinking_tokens)
        except Exception:
            pass   # la telemetría del form nunca rompe el tracking

    def track_gemini_response(self, response, model: str, description: str = "") -> None:
        """Atajo para los productores: extrae usage_metadata de la respuesta Gemini
        (tolerante a ausencia → tokens 0 + usage_ok=False, no se pierde la llamada) y
        delega en track_gemini_tokens. Una sola costura para todos los call sites."""
        um = getattr(response, "usage_metadata", None)
        if um is None:
            self.track_gemini_tokens(description or "gemini", model, 0, 0, 0, usage_ok=False)
            return
        self.track_gemini_tokens(
            description=description or "gemini",
            model=model,
            input_tokens=getattr(um, "prompt_token_count", 0) or 0,
            output_tokens=getattr(um, "candidates_token_count", 0) or 0,
            thinking_tokens=getattr(um, "thoughts_token_count", 0) or 0,
            usage_ok=True,
        )

    def track_gemini_vision(self, description: str, calls: int = 1) -> None:
        """Registra costo de llamada a Gemini 2.5 Flash Vision (validación)."""
        cost_per = pipeline.costs.get("gemini_vision_per_call", 0.0001)
        self._add_entry(
            stage=PipelineStage.IMAGE.value,
            service="Gemini Vision",
            description=description,
            units=calls,
            unit_label="calls",
            cost_per_unit=cost_per,
        )

    def track_flux_pro(self, description: str, images: int = 1) -> None:
        """Registra costo de generación con fal.ai Flux.2 Pro estándar."""
        cost_per = pipeline.costs["flux_pro_per_image"]
        self._add_entry(
            stage=PipelineStage.IMAGE.value,
            service="fal.ai Flux.2 Pro",
            description=description,
            units=images,
            unit_label="images",
            cost_per_unit=cost_per,
        )

    def track_flux_ultra(self, description: str, images: int = 1) -> None:
        """Registra costo de generación con fal.ai Flux.2 Pro (gancho ch01).

        NOTA: tras migración Nov 2025, Ultra y Pro son el MISMO modelo (Flux.2 Pro).
        Se mantiene este método separado por compatibilidad con asset_manager.
        """
        cost_per = pipeline.costs["flux_pro_ultra_per_image"]
        self._add_entry(
            stage=PipelineStage.IMAGE.value,
            service="fal.ai Flux.2 Pro (hook)",
            description=description,
            units=images,
            unit_label="images",
            cost_per_unit=cost_per,
        )

    def track_kling(self, description: str, images: int = 1) -> None:
        """Registra costo de generación con Kling o3 t2i (fal.run, SYNC).

        Costo aprox $0.028/img; el campo de costo NO viene en la respuesta de fal,
        así que el costo real se confirma por delta de dashboard (deuda chat-67).
        """
        cost_per = pipeline.costs.get("kling_per_image", 0.028)
        self._add_entry(
            stage=PipelineStage.IMAGE.value,
            service="fal.ai Kling o3 (t2i)",
            description=description,
            units=images,
            unit_label="images",
            cost_per_unit=cost_per,
        )

    def track_seedream(self, description: str, images: int = 1, mode: str = "t2i") -> None:
        """Registra costo de generación con Seedream 4.5 (fal.run, SYNC).

        mode ∈ {"t2i","edit"} (HANDOFF_133): SOLO cambia la etiqueta del service para que
        el costo del /edit anclado no se disfrace de t2i. La TARIFA queda 0.04 para ambos
        modos — la real del /edit se confirma por delta dashboard (no inventar precio).
        El campo de costo NO viene en la respuesta de fal, igual que Kling.
        """
        cost_per = pipeline.costs.get("seedream_per_image", 0.04)
        self._add_entry(
            stage=PipelineStage.IMAGE.value,
            service=f"fal.ai Seedream 4.5 ({mode})",
            description=description,
            units=images,
            unit_label="images",
            cost_per_unit=cost_per,
        )

    def track_leonardo(self, description: str, images: int = 1) -> None:
        """[DEPRECATED] Leonardo AI fue reemplazado por Flux. Mantener solo para compatibilidad."""
        cost_per = pipeline.costs["leonardo_per_image"]
        error_handler.log_warning(
            PipelineStage.COST_TRACKER,
            "track_leonardo está deprecated. Usar track_flux_pro o track_flux_ultra.",
        )
        self._add_entry(
            stage=PipelineStage.IMAGE.value,
            service="Leonardo AI (DEPRECATED)",
            description=description,
            units=images,
            unit_label="images",
            cost_per_unit=cost_per,
        )

    def track_fal(self, description: str, clips: int = 1) -> None:
        """Registra costo de generación de video con fal.ai (Veo 3.1 Lite)."""
        cost_per = pipeline.costs["fal_per_clip"]
        self._add_entry(
            stage=PipelineStage.VIDEO.value,
            service="fal.ai (Veo 3.1 Lite)",
            description=description,
            units=clips,
            unit_label="clips",
            cost_per_unit=cost_per,
        )

    def track_elevenlabs(self, description: str, characters: int = 0) -> None:
        """Registra costo de generación de audio con ElevenLabs."""
        cost_per = pipeline.costs["elevenlabs_per_char"]
        self._add_entry(
            stage=PipelineStage.AUDIO.value,
            service="ElevenLabs",
            description=description,
            units=characters,
            unit_label="characters",
            cost_per_unit=cost_per,
        )

    def track_custom(self, stage: str, service: str, description: str,
                     units: float, unit_label: str, cost_per_unit: float) -> None:
        """Registra un costo personalizado (para servicios futuros)."""
        self._add_entry(stage, service, description, units, unit_label, cost_per_unit)

    # ─── Internos ───

    def _add_entry(self, stage: str, service: str, description: str,
                   units: float, unit_label: str, cost_per_unit: float,
                   total_cost: float | None = None, tokens_in: int = 0,
                   tokens_out: int = 0, tokens_thinking: int = 0,
                   usage_ok: bool = True) -> None:
        """
        Acumula un CostEntry en el bucket correcto:
          · Si hay video activo → entry va al video.
          · Si NO hay video activo → entry va a session_overhead (Fase 1,
            research, descubrimiento). Sin warning.

        total_cost explícito (HANDOFF_133): cuando la tarifa no es units×cost_per_unit
        (p.ej. Gemini con tarifa input/output distinta), el caller lo pasa ya calculado.
        """
        entry = CostEntry(
            timestamp=datetime.now().isoformat(),
            stage=stage,
            service=service,
            description=description,
            units=units,
            unit_label=unit_label,
            cost_per_unit=cost_per_unit,
            total_cost=round(total_cost if total_cost is not None else units * cost_per_unit, 6),
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            tokens_thinking=tokens_thinking,
            usage_ok=usage_ok,
        )

        if self.current_video:
            self.current_video.add(entry)
        else:
            # v2: en lugar de warnar y descartar, acumular como overhead de sesión.
            # Útil para contabilizar Fase 1 (niche_discoverer, research, etc.)
            # y tests aislados.
            self.session_overhead.append(entry)

    def _save_to_history(self, report: VideoCostReport) -> None:
        """Guarda el reporte al historial persistente."""
        history = self._load_history()
        history.append(asdict(report))
        self.HISTORY_FILE.write_text(
            json.dumps(history, indent=2, ensure_ascii=False)
        )

    def _load_history(self) -> list:
        if self.HISTORY_FILE.exists():
            return json.loads(self.HISTORY_FILE.read_text())
        return []

    # ─── Reportes ───

    def get_session_overhead_total(self) -> float:
        """Costo total acumulado en session_overhead (no asociado a un video)."""
        return round(sum(e.total_cost for e in self.session_overhead), 4)

    def get_session_summary(self) -> dict:
        """Resumen de la sesión actual (videos + overhead de Fase 1/research)."""
        videos_total = sum(v.total_cost for v in self.session_videos)
        overhead_total = self.get_session_overhead_total()
        grand_total = videos_total + overhead_total

        breakdown: dict[str, float] = {}
        for video in self.session_videos:
            for entry in video.entries:
                svc = entry.service
                breakdown[svc] = breakdown.get(svc, 0.0) + entry.total_cost
        for entry in self.session_overhead:
            svc = entry.service
            breakdown[svc] = breakdown.get(svc, 0.0) + entry.total_cost

        return {
            "session_date": datetime.now().isoformat(),
            "videos_generated": len(self.session_videos),
            "videos_cost_usd": round(videos_total, 4),
            "session_overhead_usd": round(overhead_total, 4),
            "session_overhead_entries": len(self.session_overhead),
            "total_cost_usd": round(grand_total, 4),
            "cost_per_video_avg": round(videos_total / max(len(self.session_videos), 1), 4),
            "breakdown_by_service": {k: round(v, 4) for k, v in breakdown.items()},
        }

    def get_historical_summary(self) -> dict:
        """Resumen del historial completo."""
        history = self._load_history()
        total = sum(v.get("total_cost", 0) for v in history)
        return {
            "total_videos": len(history),
            "total_spent_usd": round(total, 4),
            "avg_cost_per_video": round(total / max(len(history), 1), 4),
        }

    def print_session_report(self) -> None:
        """Imprime reporte bonito en consola."""
        summary = self.get_session_summary()
        print("\n" + "=" * 50)
        print("  💰 REPORTE DE COSTOS — SESIÓN")
        print("=" * 50)
        print(f"  Videos generados:    {summary['videos_generated']}")
        print(f"  Costo videos:        ${summary['videos_cost_usd']:.4f} USD")
        if summary["session_overhead_entries"] > 0:
            print(f"  Overhead sesión:     ${summary['session_overhead_usd']:.4f} USD "
                  f"({summary['session_overhead_entries']} entries — Fase 1 / research)")
        print(f"  Costo total:         ${summary['total_cost_usd']:.4f} USD")
        if summary["videos_generated"] > 0:
            print(f"  Promedio por video:  ${summary['cost_per_video_avg']:.4f} USD")
        print("-" * 50)
        print("  Desglose por servicio:")
        for svc, cost in summary["breakdown_by_service"].items():
            print(f"    {svc:<30s} ${cost:.4f}")
        print("=" * 50 + "\n")

    def _all_entries(self):
        """Itera TODAS las entries de la sesión (videos + overhead)."""
        for video in self.session_videos:
            yield from video.entries
        if self.current_video:
            yield from self.current_video.entries
        yield from self.session_overhead

    @staticmethod
    def _gemini_module_of(description: str) -> str:
        """Módulo/paso de una entry Gemini para el desglose (HANDOFF_134b). Usa el `description`
        del call site: 'm03:fluidificador'/'m03:slots'/'m03:motion', 'deep-*'/'niche_*'/
        'dynamic_queries' (discovery), y los genéricos 'call_flash_json'/'call_pro_json' (los
        callers del motor sin tag → agrupan como 'motor (sin tag)')."""
        d = (description or "").strip()
        if d in ("call_flash_json", "call_pro_json", ""):
            return "motor (sin tag)"
        if ": " in d:              # sufijo free-text (p.ej. "dynamic_queries: <niche>")
            return d.split(": ", 1)[0]
        return d                   # "m03:fluidificador", "deep-tecnico", etc.

    def get_gemini_summary(self) -> dict:
        """Agrega las entries de Gemini (unit_label='tokens') por modelo/servicio Y por módulo
        (description): #llamadas, tokens in/out/thinking, $ y llamadas con usage_metadata ausente."""
        by_model: dict[str, dict] = {}
        by_desc: dict[str, dict] = {}
        for e in self._all_entries():
            if e.unit_label != "tokens":
                continue
            m = by_model.setdefault(e.service, {
                "calls": 0, "tokens_in": 0, "tokens_out": 0,
                "tokens_thinking": 0, "cost_usd": 0.0, "usage_missing": 0,
            })
            d = by_desc.setdefault(self._gemini_module_of(e.description), {
                "calls": 0, "tokens_in": 0, "tokens_out": 0,
                "tokens_thinking": 0, "cost_usd": 0.0,
            })
            for bucket in (m, d):
                bucket["calls"] += 1
                bucket["tokens_in"] += e.tokens_in
                bucket["tokens_out"] += e.tokens_out
                bucket["tokens_thinking"] += e.tokens_thinking
                bucket["cost_usd"] += e.total_cost
            if not e.usage_ok:
                m["usage_missing"] += 1
        for m in by_model.values():
            m["cost_usd"] = round(m["cost_usd"], 4)
        for d in by_desc.values():
            d["cost_usd"] = round(d["cost_usd"], 4)
        totals = {
            "calls": sum(m["calls"] for m in by_model.values()),
            "tokens_in": sum(m["tokens_in"] for m in by_model.values()),
            "tokens_out": sum(m["tokens_out"] for m in by_model.values()),
            "tokens_thinking": sum(m["tokens_thinking"] for m in by_model.values()),
            "cost_usd": round(sum(m["cost_usd"] for m in by_model.values()), 4),
            "usage_missing": sum(m["usage_missing"] for m in by_model.values()),
        }
        return {"by_model": by_model, "by_desc": by_desc, "totals": totals}

    def print_gemini_report(self) -> None:
        """Bloque Gemini del resumen — que Omar vea el $ al cerrar la corrida sin abrir
        el dashboard de Google. No imprime nada si no hubo llamadas Gemini trackeadas."""
        g = self.get_gemini_summary()
        if g["totals"]["calls"] == 0:
            return
        t = g["totals"]
        print("\n" + "─" * 50)
        print("  🧠 GEMINI (por tokens — thinking incluido)")
        print("─" * 50)
        for svc, m in sorted(g["by_model"].items()):
            print(f"    {svc:<22} {m['calls']:>4} calls  "
                  f"in {m['tokens_in']:>8,}  out {m['tokens_out']:>8,}  "
                  f"think {m['tokens_thinking']:>8,}  ${m['cost_usd']:.4f}")
            if m["usage_missing"]:
                print(f"      ⚠ {m['usage_missing']} llamada(s) sin usage_metadata (contadas con 0 tokens)")
        # Desglose POR MÓDULO (HANDOFF_134b chascada 2) — para gatear el 🥈 con dato fino.
        if g["by_desc"]:
            print("  · por módulo:")
            for mod, d in sorted(g["by_desc"].items(), key=lambda kv: -kv[1]["cost_usd"]):
                th = d["tokens_thinking"]
                billed = d["tokens_out"] + th
                pct = f"{round(th / billed * 100)}% think" if billed else "—"
                print(f"    {mod:<20} {d['calls']:>4} calls  "
                      f"in {d['tokens_in']:>8,}  out {d['tokens_out']:>8,}  "
                      f"think {th:>8,}  ${d['cost_usd']:.4f}  ({pct})")
        print("─" * 50)
        print(f"    TOTAL Gemini: {t['calls']} calls · in {t['tokens_in']:,} · "
              f"out {t['tokens_out']:,} · think {t['tokens_thinking']:,} · "
              f"${t['cost_usd']:.4f} USD")

    def print_summary(self) -> None:
        """Resumen completo de la corrida: servicios (fal/seedream/...) + bloque Gemini.
        (HANDOFF_133: fase2a ya llamaba a print_summary — antes no existía y el except la
        tragaba; ahora existe e incluye Gemini.)"""
        self.print_session_report()
        self.print_gemini_report()

    def save_session_report(self, filepath: Path | None = None) -> Path:
        """Guarda el reporte de sesión como JSON."""
        if filepath is None:
            filepath = DATA_DIR / f"session_report_{datetime.now():%Y%m%d_%H%M%S}.json"
        report = {
            "session": self.get_session_summary(),
            "gemini": self.get_gemini_summary(),
            "historical": self.get_historical_summary(),
            "videos": [asdict(v) for v in self.session_videos],
            "session_overhead": [asdict(e) for e in self.session_overhead],
        }
        filepath.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        return filepath


# Instancia global
cost_tracker = CostTracker()