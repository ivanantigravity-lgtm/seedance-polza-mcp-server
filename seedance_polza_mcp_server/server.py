"""FastMCP server for Seedance via Polza Media API."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from fastmcp import FastMCP

from .config import Settings
from .polza_client import PolzaClient


LOGGER = logging.getLogger(__name__)
MODEL_GUIDE = """Seedance guide:

- use async mode by default for video generation
- poll every 5-10 seconds for video
- keep prompts concrete
- do not resend the same expensive generation blindly
- prefer one good prompt over many vague retries
"""


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _compact_status(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": data.get("id"),
        "object": data.get("object"),
        "status": data.get("status"),
        "model": data.get("model"),
        "created": data.get("created"),
        "completed_at": data.get("completed_at"),
        "data": data.get("data"),
        "content": data.get("content"),
        "reasoning_summary": data.get("reasoning_summary"),
        "usage": data.get("usage"),
        "warnings": data.get("warnings"),
        "error": data.get("error"),
    }


def _validate_media_files(items: list[dict[str, str]] | None) -> list[dict[str, str]]:
    if not items:
        return []

    cleaned: list[dict[str, str]] = []
    for item in items:
        media_type = item.get("type")
        data = item.get("data")
        if media_type not in {"url", "base64"}:
            raise ValueError("Media file type must be 'url' or 'base64'")
        if not data:
            raise ValueError("Media file data is required")
        cleaned.append({"type": media_type, "data": data})
    return cleaned


class SeedanceEngine:
    """Core engine for media create / status / wait."""

    def __init__(self, settings: Settings, client: PolzaClient) -> None:
        self.settings = settings
        self.client = client

    async def create_video(
        self,
        *,
        prompt: str,
        model: str | None = None,
        aspect_ratio: str | None = None,
        resolution: str | None = None,
        duration: str | None = None,
        images: list[dict[str, str]] | None = None,
        videos: list[dict[str, str]] | None = None,
        seed: int | None = None,
        sound: bool | None = None,
        user: str | None = None,
        async_mode: bool = True,
    ) -> dict[str, Any]:
        input_payload: dict[str, Any] = {
            "prompt": prompt,
        }

        if aspect_ratio:
            input_payload["aspect_ratio"] = aspect_ratio
        if resolution:
            input_payload["resolution"] = resolution
        if duration:
            input_payload["duration"] = duration
        if seed is not None:
            input_payload["seed"] = seed
        if sound is not None:
            input_payload["sound"] = sound

        validated_images = _validate_media_files(images)
        validated_videos = _validate_media_files(videos)
        if validated_images:
            input_payload["images"] = validated_images
        if validated_videos:
            input_payload["videos"] = validated_videos

        payload: dict[str, Any] = {
            "model": model or self.settings.seedance_model,
            "input": input_payload,
            "async": async_mode,
        }
        if user:
            payload["user"] = user

        result = await self.client.create_media(payload)
        return _compact_status(result)

    async def get_status(self, media_id: str) -> dict[str, Any]:
        result = await self.client.get_media_status(media_id)
        return _compact_status(result)

    async def wait_for_completion(
        self,
        *,
        media_id: str,
        interval_seconds: int | None = None,
        max_wait_seconds: int | None = None,
    ) -> dict[str, Any]:
        interval = interval_seconds or self.settings.poll_interval
        max_wait = max_wait_seconds or self.settings.max_wait
        elapsed = 0

        while elapsed <= max_wait:
            status = await self.get_status(media_id)
            if status["status"] in {"completed", "failed", "cancelled"}:
                return status
            await asyncio.sleep(interval)
            elapsed += interval

        raise TimeoutError(f"Seedance generation {media_id} did not finish within {max_wait} seconds")


def create_app() -> FastMCP:
    """Create FastMCP app."""
    settings = Settings.from_env()
    _setup_logging(settings.log_level)
    client = PolzaClient(settings)
    engine = SeedanceEngine(settings, client)

    app = FastMCP(
        name="seedance-polza-mcp-server",
        instructions=(
            "This server creates and tracks Seedance video generations through Polza.ai Media API. "
            "Use it for concrete video jobs, not for brainstorming."
        ),
    )

    @app.tool
    async def seedance_model_guide() -> str:
        """Return a short practical guide for using Seedance through Polza."""
        return MODEL_GUIDE

    @app.tool
    async def seedance_create_video(
        prompt: str,
        model: str | None = None,
        aspect_ratio: str | None = None,
        resolution: str | None = None,
        duration: str | None = None,
        images: list[dict[str, str]] | None = None,
        videos: list[dict[str, str]] | None = None,
        seed: int | None = None,
        sound: bool | None = None,
        user: str | None = None,
        async_mode: bool = True,
    ) -> str:
        """Create a Seedance video generation through Polza Media API."""
        result = await engine.create_video(
            prompt=prompt,
            model=model,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            duration=duration,
            images=images,
            videos=videos,
            seed=seed,
            sound=sound,
            user=user,
            async_mode=async_mode,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)

    @app.tool
    async def seedance_get_status(media_id: str) -> str:
        """Get current status of a media generation by ID."""
        result = await engine.get_status(media_id)
        return json.dumps(result, ensure_ascii=False, indent=2)

    @app.tool
    async def seedance_wait_for_completion(
        media_id: str,
        interval_seconds: int | None = None,
        max_wait_seconds: int | None = None,
    ) -> str:
        """Poll media status until completed, failed, cancelled, or timeout."""
        result = await engine.wait_for_completion(
            media_id=media_id,
            interval_seconds=interval_seconds,
            max_wait_seconds=max_wait_seconds,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)

    return app


def main() -> None:
    """Entrypoint for direct execution."""
    try:
        app = create_app()
        app.run()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as error:
        LOGGER.error("Server failed to start: %s", error, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
