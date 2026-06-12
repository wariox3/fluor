import logging

import sentry_sdk

from app.core.config import (
    SENTRY_DSN,
    ENVIRONMENT,
    SENTRY_TRACES_SAMPLE_RATE,
    DEBUG,
)

logger = logging.getLogger("api")


def setup_sentry():
    """Inicializa Sentry para captura de excepciones.

    Si SENTRY_DSN no está configurado, no hace nada (Sentry desactivado).
    Las integraciones de FastAPI/Starlette se auto-activan al estar instaladas,
    así que toda excepción no controlada se reporta automáticamente.
    """
    if not SENTRY_DSN:
        logger.info("Sentry desactivado (SENTRY_DSN no configurado)")
        return

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT,
        # Performance tracing: 0.0 por defecto (solo errores). Subir si se quiere.
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        # No enviar datos personales (cuerpos, cookies, headers de auth) por defecto.
        send_default_pii=False,
        debug=DEBUG,
    )
    logger.info("Sentry inicializado (environment=%s)", ENVIRONMENT)
