from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from instagrapi import Client
from instagrapi.exceptions import LoginRequired, MediaNotFound

from app.config import get_settings


@dataclass
class InstagramMediaPayload:
    url: str
    shortcode: str
    media_type: str
    author_username: str
    caption: str
    likes_count: int
    comments_count: int
    view_count: int
    comments: list[dict[str, Any]]


class InstagramClientService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = Client()
        self._is_logged_in = False

    def _ensure_login(self) -> None:
        if self._is_logged_in:
            return

        session_path = self.settings.instagram_session_path
        # sessionid is the most stable fallback when password login is blocked by Instagram.
        if self.settings.instagram_sessionid:
            try:
                self.client.login_by_sessionid(self.settings.instagram_sessionid)
                self.client.dump_settings(session_path)
                self._is_logged_in = True
                return
            except Exception as exc:
                raise ValueError(
                    "Не удалось войти через INSTAGRAM_SESSIONID. "
                    "Проверьте, что cookie sessionid актуален."
                ) from exc

        if not self.settings.instagram_username or not self.settings.instagram_password:
            raise ValueError(
                "Instagram credentials are not configured. "
                "Set INSTAGRAM_USERNAME/INSTAGRAM_PASSWORD or INSTAGRAM_SESSIONID."
            )

        try:
            self.client.load_settings(session_path)
            self.client.login(
                self.settings.instagram_username,
                self.settings.instagram_password,
            )
        except Exception:
            # If session restore fails, fallback to clean login.
            self.client = Client()
            try:
                self.client.login(
                    self.settings.instagram_username,
                    self.settings.instagram_password,
                )
            except Exception as exc:
                message = str(exc)
                raise ValueError(
                    "Instagram отклонил вход по логину/паролю. "
                    "Частая причина: новый девайс, проверка безопасности или вход через Facebook. "
                    "Решение: войдите в Instagram в браузере, подтвердите безопасность аккаунта, "
                    "затем добавьте INSTAGRAM_SESSIONID в env.txt и перезапустите сервис. "
                    f"Оригинальная ошибка: {message}"
                ) from exc

        self.client.dump_settings(session_path)
        self._is_logged_in = True

    def fetch_media(
        self,
        url: str,
        comments_limit: int = 200,
        include_comment_replies: bool = False,
    ) -> InstagramMediaPayload:
        self._ensure_login()

        try:
            media_pk = self.client.media_pk_from_url(url)
            media = self.client.media_info(media_pk)
        except (MediaNotFound, LoginRequired) as exc:
            raise ValueError(f"Unable to access media by URL: {url}") from exc

        raw_comments = self.client.media_comments(media_pk, amount=comments_limit)
        comments: list[dict[str, Any]] = []
        for item in raw_comments:
            # instagrapi comment model can differ by version, so use safe attribute access.
            replies_count = getattr(item, "replies_count", 0) or 0
            preview_replies = getattr(item, "preview_child_comments", None) or []
            row = {
                "text": item.text or "",
                "likes_count": item.like_count or 0,
                "created_at": str(item.created_at_utc) if item.created_at_utc else "",
                "username": item.user.username if item.user else "",
                "replies_count": replies_count,
            }
            if include_comment_replies:
                row["replies"] = [reply.text for reply in preview_replies if getattr(reply, "text", None)]
            comments.append(row)

        return InstagramMediaPayload(
            url=url,
            shortcode=media.code,
            media_type=str(media.media_type),
            author_username=media.user.username if media.user else "",
            caption=media.caption_text or "",
            likes_count=media.like_count or 0,
            comments_count=media.comment_count or 0,
            view_count=media.view_count or 0,
            comments=comments,
        )
