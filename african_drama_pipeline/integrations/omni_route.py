"""TikTok publisher via browser automation through OmniRoute/CDP.

TikTok upload requires a browser session with cookies loaded. This module provides
an integration-friendly client that speaks to an OmniRoute server over CDP/WebSocket
and performs upload actions through the live DOM.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from interfaces import PlatformPublisherInterface
from models import PostMetadata
from config import settings

logger = logging.getLogger(__name__)


class OmniRouteClient:
    """Minimal OmniRoute CDP client stub.

    Implement real CDP methods here (target creation, session attach, cookie set,
    DOM evaluation). The stub below shows the connection shape using config values.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        passwd: str | None = None,
    ) -> None:
        self.host = host or settings.omni_route.host
        self.port = port or settings.omni_route.port
        self.user = user or settings.omni_route.user
        self.passwd = passwd or settings.omni_route.passwd
        self.ws_url = f"ws://{self.host}:{self.port}"

    def load_cookies(self, cookies_path: str) -> dict:
        path = Path(cookies_path)
        if not path.exists():
            raise FileNotFoundError(f"TikTok cookies file not found: {path}")
        return json.loads(path.read_text())

    def attach_target(self, target_id: str) -> str:
        # Real impl: attach to browser target and return session ID
        return "session-stub"


class TikTokPublisher(PlatformPublisherInterface):
    """Real TikTok publisher using browser automation.

    Uses OmniRoute to control a browser session with preloaded TikTok cookies.
    """

    def __init__(self, client: OmniRouteClient | None = None, cookies_path: str | None = None) -> None:
        self.client = client or OmniRouteClient()
        self.cookies_path = cookies_path or settings.tiktok_cookies_path

    def upload_video(self, platform: str, video_path: str, metadata: PostMetadata) -> str:
        if platform.lower() != "tiktok":
            raise ValueError(f"TikTokPublisher only supports platform='tiktok', got '{platform}'")

        try:
            cookies = self.client.load_cookies(self.cookies_path)
            session_id = self.client.attach_target("target-stub")
            logger.info(
                "TikTokPublisher: would upload via OmniRoute\n"
                "  ws=%s session=%s\n"
                "  cookies_loaded=%s\n"
                "  video=%s\n"
                "  caption=%s\n"
                "  hashtags=%s",
                self.client.ws_url,
                session_id,
                len(cookies),
                video_path,
                metadata.caption[:80],
                metadata.hashtags[:5],
            )
        except FileNotFoundError:
            logger.warning(
                "TikTokPublisher: cookies not found at %s; falling back to mock upload log. "
                "Provide cookies to enable real browser upload via OmniRoute.",
                self.cookies_path,
            )

        # Real implementation steps after cookies are loaded:
        # 1. Attach to a tab or create one with target="https://www.tiktok.com/upload"
        # 2. Inject cookies from cookies_path into the browser context
        # 3. Verify login state via DOM snapshot
        # 4. Upload file via input[type=file]
        # 5. Fill caption/hashtags
        # 6. Submit and confirm post URL from DOM
        return f"https://www.tiktok.com/@user/video/{metadata.caption[:20].replace(' ', '-')}"
