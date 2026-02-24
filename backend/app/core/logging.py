from __future__ import annotations

import logging


def configure_logging(*, debug: bool) -> None:
    """Minimal logging config.

    Uvicorn will also configure logging; this ensures consistent formatting when
    running tests or scripts.
    """

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
