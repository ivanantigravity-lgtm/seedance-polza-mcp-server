"""Configuration for the Seedance MCP server."""

from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    """Runtime configuration."""

    polza_api_key: str
    polza_base_url: str = "https://polza.ai/api/v1"
    seedance_model: str = "bytedance/seedance-2"
    poll_interval: int = 8
    max_wait: int = 900
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            polza_api_key=os.environ["POLZA_API_KEY"],
            polza_base_url=os.getenv("POLZA_BASE_URL", "https://polza.ai/api/v1").rstrip("/"),
            seedance_model=os.getenv("SEEDANCE_MODEL", "bytedance/seedance-2"),
            poll_interval=int(os.getenv("SEEDANCE_POLL_INTERVAL", "8")),
            max_wait=int(os.getenv("SEEDANCE_MAX_WAIT", "900")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
