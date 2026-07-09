import json
import logging
import sys
import time
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from logging.handlers import RotatingFileHandler
from threading import Lock
from typing import Any, Generator

import pytz

from docuflow.configs import settings

# Thread-safety lock for configuring logging
_logging_lock = Lock()
_logging_configured = False

# Context variables for tracing
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
document_id_var: ContextVar[str] = ContextVar("document_id", default="")
stage_var: ContextVar[str] = ContextVar("stage", default="")


@contextmanager
def log_context(
    request_id: str | None = None,
    document_id: str | None = None,
    stage: str | None = None,
) -> Generator[None, None, None]:
    """
    Context manager to bind correlation IDs and stage names to contextvars.

    Ensures they are cleaned up after the block exits.
    """
    tokens = []
    if request_id is not None:
        tokens.append((request_id_var, request_id_var.set(request_id)))
    if document_id is not None:
        tokens.append((document_id_var, document_id_var.set(document_id)))
    if stage is not None:
        tokens.append((stage_var, stage_var.set(stage)))

    try:
        yield
    finally:
        for var, token in reversed(tokens):
            var.reset(token)


class ContextFilter(logging.Filter):
    """Filter that injects context variables into each LogRecord."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get("")
        record.document_id = document_id_var.get("")
        record.stage = stage_var.get("")
        return True


class JSONFormatter(logging.Formatter):
    """Formatter that outputs structured logs in JSON format."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", ""),
            "document_id": getattr(record, "document_id", ""),
            "stage": getattr(record, "stage", ""),
        }

        # Include exception trace if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Include custom performance metrics if present on the log record
        for attr in ["latency_ms", "input_tokens", "output_tokens", "cost_usd", "chunk_count"]:
            if hasattr(record, attr):
                log_data[attr] = getattr(record, attr)

        return json.dumps(log_data)


class HumanReadableFormatter(logging.Formatter):
    """Formatter that appends context variables and metrics to console output."""

    def format(self, record: logging.LogRecord) -> str:
        req_id = getattr(record, "request_id", "")
        doc_id = getattr(record, "document_id", "")
        stage = getattr(record, "stage", "")

        ctx_parts = []
        if req_id:
            ctx_parts.append(f"req:{req_id}")
        if doc_id:
            ctx_parts.append(f"doc:{doc_id}")
        if stage:
            ctx_parts.append(f"stage:{stage}")

        ctx_str = f" [{', '.join(ctx_parts)}]" if ctx_parts else ""

        # Save original msg/args to restore later
        orig_msg = record.msg
        orig_args = record.args

        # Format perf metrics if present
        perf_parts = []
        for attr in ["latency_ms", "input_tokens", "output_tokens", "cost_usd", "chunk_count"]:
            if hasattr(record, attr):
                perf_parts.append(f"{attr}={getattr(record, attr)}")
        perf_str = f" | {', '.join(perf_parts)}" if perf_parts else ""

        record.msg = f"{record.msg}{ctx_str}{perf_str}"

        try:
            result = super().format(record)
        finally:
            record.msg = orig_msg
            record.args = orig_args

        return result


def ist_timezone(*args: Any) -> time.struct_time:
    """Return IST time for logging formatter."""
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(tz).timetuple()


def setup_logging(level: str | None = None) -> None:
    """
    Configure the root logger with Console and RotatingFile handlers.

    Ensures that logging handlers are only configured once for the entire application,
    avoiding multiple file handles/write conflicts on the same log file.
    """
    global _logging_configured

    if _logging_configured:
        return

    with _logging_lock:
        if _logging_configured:
            return

        # Ensure parent directory for log file exists
        log_file = settings.log_path
        log_file.parent.mkdir(parents=True, exist_ok=True)

        log_level = level or settings.LOG_LEVEL
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)

        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Add ContextFilter to root logger
        context_filter = ContextFilter()
        root_logger.addFilter(context_filter)

        # Console formatter
        console_formatter = HumanReadableFormatter(
            "%(asctime)s | %(levelname)-8s | %(name)-40s | %(message)s",
            datefmt="%Y-%m-%d %I:%M:%S %p",
        )
        console_formatter.converter = ist_timezone

        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(context_filter)
        root_logger.addHandler(console_handler)

        # File formatter (JSON)
        file_formatter = JSONFormatter(datefmt="%Y-%m-%d %I:%M:%S %p")
        file_formatter.converter = ist_timezone

        # Rotating File handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(context_filter)
        root_logger.addHandler(file_handler)

        _logging_configured = True


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get a named logger instance.

    Automatically configures logging handlers on the root logger upon the first call.
    """
    setup_logging()
    return logging.getLogger(name)
