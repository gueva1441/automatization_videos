"""
Manejador centralizado de errores del pipeline.
- Logging estructurado a archivo y consola
- Reintentos con exponential backoff + jitter
- 5 intentos para errores de servidor (503, 429)
- 3 intentos para otros errores
- Reporte de errores por etapa
"""

import logging
import random
import time
import traceback
import json
from datetime import datetime
from pathlib import Path
from functools import wraps
from enum import Enum
from dataclasses import dataclass, field, asdict

from config import LOGS_DIR, pipeline


# ─── Setup del logger ───

class PipelineStage(str, Enum):
    SCRIPT = "script_generator"
    IMAGE = "image_generator"
    VIDEO = "video_generator"
    AUDIO = "audio_generator"
    ASSEMBLY = "video_assembler"
    ORCHESTRATOR = "orchestrator"
    COST_TRACKER = "cost_tracker"
    NICHE_DISCOVERER = "niche_discoverer"
    TOPIC_RESEARCHER = "topic_researcher"
    TOPIC_VALIDATOR = "topic_validator"
    CHANNEL_MEMORY = "channel_memory"


@dataclass
class ErrorRecord:
    """Registro individual de un error."""
    timestamp: str
    stage: str
    error_type: str
    message: str
    traceback: str = ""
    attempt: int = 1
    resolved: bool = False
    context: dict = field(default_factory=dict)


class ErrorHandler:
    """Manejador centralizado de errores del pipeline."""

    def __init__(self, log_dir: Path = LOGS_DIR):
        self.log_dir = log_dir
        self.errors: list[ErrorRecord] = []
        self._setup_logger()

    def _setup_logger(self):
        """Configura logging a archivo y consola."""
        self.logger = logging.getLogger("viral_pipeline")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        # Archivo de log (todo)
        log_file = self.log_dir / f"pipeline_{datetime.now():%Y%m%d_%H%M%S}.log"
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)

        # Consola (info+)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        fmt = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def log_error(
        self,
        stage: PipelineStage,
        error: Exception,
        attempt: int = 1,
        context: dict = None,
    ) -> ErrorRecord:
        """Registra un error con contexto completo."""
        record = ErrorRecord(
            timestamp=datetime.now().isoformat(),
            stage=stage.value,
            error_type=type(error).__name__,
            message=str(error),
            traceback=traceback.format_exc(),
            attempt=attempt,
            context=context or {},
        )
        self.errors.append(record)
        self.logger.error(
            f"[{stage.value}] Intento {attempt} — {type(error).__name__}: {error}"
        )
        return record

    def log_success(self, stage: PipelineStage, message: str, **kwargs):
        """Registra una operación exitosa."""
        self.logger.info(f"[{stage.value}] ✓ {message}")

    def log_warning(self, stage: PipelineStage, message: str):
        """Registra una advertencia."""
        self.logger.warning(f"[{stage.value}] ⚠ {message}")

    def log_info(self, stage: PipelineStage, message: str):
        """Registra info general."""
        self.logger.info(f"[{stage.value}] {message}")

    # ─── Decorador de reintentos ───

    def retry(self, stage: PipelineStage, max_retries: int = None,
              delay: int = None, max_server_retries: int = None):
        """
        Decorador que reintenta una función con exponential backoff + jitter.

        - Errores de servidor (503, 429): hasta max_server_retries (default 5)
        - Otros errores: hasta max_retries (default 3)
        - Jitter aleatorio (0-50%) para evitar thundering herd

        Esperas aprox para 503: ~15s, ~23s, ~45s, ~90s, ~180s

        Uso:
            @error_handler.retry(PipelineStage.IMAGE)
            def generate_image(prompt):
                ...

            # Para servicios costosos (fal.ai Flux/Veo): limitar reintentos
            @error_handler.retry(PipelineStage.IMAGE, max_server_retries=2)
            def expensive_api_call(...):
                ...
        """
        _max = max_retries or pipeline.max_retries  # default 3
        _delay = delay or pipeline.retry_delay_seconds  # default 5
        _max_server_retries = max_server_retries if max_server_retries is not None else 5

        def _is_server_error(error: Exception) -> bool:
            """Detecta errores de servidor (503, 429) en cualquier formato."""
            err_str = str(error)
            return any(code in err_str for code in [
                "503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED",
            ])

        def _calculate_wait(attempt: int, is_server: bool) -> float:
            """Calcula espera con exponential backoff + jitter."""
            base = _delay * (2 ** (attempt - 1))
            if is_server:
                base = max(base, 10) * 1.5  # base mínima 15s para servidor
            jitter = random.uniform(0, base * 0.5)  # 0-50% de variación
            return round(base + jitter, 1)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_error = None
                effective_max = _max

                for attempt in range(1, _max_server_retries + 1):
                    try:
                        result = func(*args, **kwargs)
                        if attempt > 1:
                            self.log_success(
                                stage,
                                f"{func.__name__} exitoso en intento {attempt}",
                            )
                        return result
                    except Exception as e:
                        last_error = e
                        is_server = _is_server_error(e)

                        # Ajustar máximo según tipo de error
                        effective_max = _max_server_retries if is_server else _max

                        self.log_error(stage, e, attempt=attempt, context={
                            "function": func.__name__,
                            "args_summary": str(args)[:200],
                            "is_server_error": is_server,
                        })

                        if attempt >= effective_max:
                            break

                        wait = _calculate_wait(attempt, is_server)
                        self.logger.info(
                            f"[{stage.value}] Reintentando en {wait}s..."
                            + (" (servidor saturado)" if is_server else "")
                        )
                        time.sleep(wait)

                # Todos los intentos fallaron
                self.logger.critical(
                    f"[{stage.value}] {func.__name__} FALLÓ tras {effective_max} intentos"
                )
                raise PipelineError(
                    stage=stage,
                    message=f"{func.__name__} falló tras {effective_max} intentos: {last_error}",
                    original_error=last_error,
                )

            return wrapper
        return decorator

    # ─── Reportes ───

    def get_summary(self) -> dict:
        """Resumen de errores por etapa."""
        summary = {}
        for err in self.errors:
            stage = err.stage
            if stage not in summary:
                summary[stage] = {"total": 0, "types": {}}
            summary[stage]["total"] += 1
            etype = err.error_type
            summary[stage]["types"][etype] = summary[stage]["types"].get(etype, 0) + 1
        return summary

    def save_error_report(self, video_id: str = "unknown"):
        """Guarda reporte JSON de todos los errores de la corrida."""
        report_path = self.log_dir / f"errors_{video_id}_{datetime.now():%Y%m%d_%H%M%S}.json"
        report = {
            "video_id": video_id,
            "generated_at": datetime.now().isoformat(),
            "total_errors": len(self.errors),
            "summary": self.get_summary(),
            "errors": [asdict(e) for e in self.errors],
        }
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        self.logger.info(f"Reporte de errores guardado en: {report_path}")
        return report_path

    def has_critical_errors(self) -> bool:
        """¿Hay errores no resueltos que deberían detener el pipeline?"""
        return any(not e.resolved for e in self.errors)


class PipelineError(Exception):
    """Error específico del pipeline con contexto de etapa."""

    def __init__(self, stage: PipelineStage, message: str, original_error: Exception = None):
        self.stage = stage
        self.original_error = original_error
        super().__init__(f"[{stage.value}] {message}")


# Instancia global
error_handler = ErrorHandler()
