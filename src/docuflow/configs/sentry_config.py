# src/docuflow/configs/sentry_config.py

import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from docuflow.configs.settings import settings


def init_sentry() -> None:
    """Initialize Sentry using Pydantic settings"""

    if not settings.SENTRY_DSN:
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)],
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        environment=settings.ENV,
        debug=settings.ENV == "development",
    )
