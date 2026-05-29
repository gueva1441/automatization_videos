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


@dataclass
class CostEntry:
    """Una entrada individual de costo."""
    timestamp: str
    stage: str
    service: str
    description: str
    units: float          # cantidad (chars, imágenes, clips, etc.)
    unit_label: str       # "images", "characters", "clips", "calls"
    cost_per_unit: float
    total_cost: float


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
                   units: float, unit_label: str, cost_per_unit: float) -> None:
        """
        Acumula un CostEntry en el bucket correcto:
          · Si hay video activo → entry va al video.
          · Si NO hay video activo → entry va a session_overhead (Fase 1,
            research, descubrimiento). Sin warning.
        """
        entry = CostEntry(
            timestamp=datetime.now().isoformat(),
            stage=stage,
            service=service,
            description=description,
            units=units,
            unit_label=unit_label,
            cost_per_unit=cost_per_unit,
            total_cost=round(units * cost_per_unit, 6),
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

    def save_session_report(self, filepath: Path | None = None) -> Path:
        """Guarda el reporte de sesión como JSON."""
        if filepath is None:
            filepath = DATA_DIR / f"session_report_{datetime.now():%Y%m%d_%H%M%S}.json"
        report = {
            "session": self.get_session_summary(),
            "historical": self.get_historical_summary(),
            "videos": [asdict(v) for v in self.session_videos],
            "session_overhead": [asdict(e) for e in self.session_overhead],
        }
        filepath.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        return filepath


# Instancia global
cost_tracker = CostTracker()