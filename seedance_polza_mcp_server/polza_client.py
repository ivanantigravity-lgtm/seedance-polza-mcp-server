"""Polza media client for Seedance."""

from __future__ import annotations

from typing import Any

import httpx

from .config import Settings


class PolzaClient:
    """Thin async client around Polza media endpoints."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def create_media(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self._settings.polza_base_url,
            timeout=180.0,
            headers={"Authorization": f"Bearer {self._settings.polza_api_key}"},
        ) as client:
            response = await client.post("/media", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_media_status(self, media_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self._settings.polza_base_url,
            timeout=60.0,
            headers={"Authorization": f"Bearer {self._settings.polza_api_key}"},
        ) as client:
            response = await client.get(f"/media/{media_id}")
        response.raise_for_status()
        return response.json()
