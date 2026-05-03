import logging
import os
from datetime import datetime

# ─────────────────────────────────────────
# 🔹 FAANG-LEVEL LOGGER
# ─────────────────────────────────────────

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger

app_logger = get_logger("ElectionAI")
