import logging
import sys

def setup_logging():

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Silenciar el ruido INFO de httpx (llamadas a Turnstile, zinc, etc.);
    # solo se registran sus advertencias o errores.
    logging.getLogger("httpx").setLevel(logging.WARNING)