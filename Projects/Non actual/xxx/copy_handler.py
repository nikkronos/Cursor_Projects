"""
Copy handler module for Копия иксуюемся.
Copies messages from source channel to target channel using aiogram bot.
"""
import asyncio
import io
import html
import re
from typing import Optional
from pyrogram.types import Message as PyrogramMessage
from pyrogram import Client
from aiogram.types import BufferedInputFile, InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAnimation, InputMediaAudio
from loader import bot, TARGET_CHANNEL_ID, logger
from utils import retry_telegram_api_async
from database import log_copied_message, get_target_message_id, is_message_copied
from config import load_config

# Load configuration
config = load_config()
SOURCE_CHANNEL_ID = config.get('SOURCE_CHANNEL_ID')

# Global variable to store Pyrogram client (set by userbot)
pyrogram_client: Optional[Client] = None

# Track processed media groups to prevent duplicates
# Key: (chat_id, media_group_id), Value: first_message_id
_processed_media_groups: dict[tuple[int, str], int] = {}


def set_pyrogram_client(client: Client) -> None:
    """
    Set Pyrogram client for downloading files.
    
    Args:
        client: Pyrogram Client instance
    """
    global pyrogram_client
    pyrogram_client = client
    logger.info("Pyrogram client set for copy handler.")


def get_sender_name(message: PyrogramMessage) -> str:
    """
    Get display name of the message sender (user or chat).
    
    Args:
        message: Pyrogram Message
    
    Returns:
        Sender name for use in caption/text
    """
    if message.from_user:
        parts = []
        if message.from_user.first_name:
            parts.append(message.from_user.first_name)
        if message.from_user.last_name:
            parts.append(message.from_user.last_name)
        name = " ".join(parts).strip()
        if message.from_user.username:
            name = f"{name} (@{message.from_user.username})" if name else f"@{message.from_user.username}"
        return name or "?"
    if message.sender_chat:
        return message.sender_chat.title or "?"
    return "?"


def add_sender_to_text(text: str, sender: str, use_html: bool = True) -> str:
    """Prepend sender name to text. If use_html, wrap sender in <b> and escape."""
    if not sender or sender == "?":
        return text
    if use_html:
        safe = html.escape(sender)
        return f"<b>{safe}</b>: {text}" if text else f"<b>{safe}</b>"
    return f"{sender}: {text}" if text else sender


def get_forward_origin_prefix(message: PyrogramMessage, use_html: bool = True) -> str:
    """
    If message is forwarded from a channel/chat, return 'Переслано из: <название или ссылка>\\n'. Else ''.
    """
    fo = getattr(message, "forward_origin", None)
    if not fo:
        return ""
    if use_html:
        # MessageForwardOriginChannel: chat with title, username
        chat = getattr(fo, "chat", None)
        if chat:
            title = (getattr(chat, "title", None) or "").strip()
            username = getattr(chat, "username", None)
            if username:
                link_text = html.escape(title or username)
                return f'Переслано из: <a href="https://t.me/{username}">{link_text}</a>\n'
            if title:
                return f"Переслано из: {html.escape(title)}\n"
        # MessageForwardOriginChat / HiddenUser / User: sender_user_name
        name = getattr(fo, "sender_user_name", None)
        if name:
            return f"Переслано от: {html.escape(str(name))}\n"
    return ""


def get_reply_prefix(message: PyrogramMessage, use_html: bool = True) -> str:
    """If message is a reply, return '↳ В ответ на: <цитата>\\n'. Else ''."""
    if not getattr(message, "reply_to_message", None) or not message.reply_to_message:
        return ""
    reply = message.reply_to_message
    part = (reply.text or reply.caption or "").strip() if reply else ""
    if not part:
        part = "[медиа]"
    if use_html:
        part = html.escape(part)
        if len(part) > 100:
            part = part[:97] + "..."
    return f"↳ В ответ на: {part}\n"


def get_reply_to_message_id(message: PyrogramMessage) -> Optional[int]:
    """
    Resolve target-channel message ID for message.reply_to_message_id (for native clickable reply).
    Returns None if not a reply or the original message was not copied to target.
    """
    reply_to_id = getattr(message, "reply_to_message_id", None) or (
        message.reply_to_message.id if getattr(message, "reply_to_message", None) and message.reply_to_message else None
    )
    if not reply_to_id or not SOURCE_CHANNEL_ID or not TARGET_CHANNEL_ID:
        return None
    return get_target_message_id(str(SOURCE_CHANNEL_ID), str(TARGET_CHANNEL_ID), reply_to_id)


def _as_input_file(buffer, filename: str = "file"):
    """Convert BytesIO or bytes to aiogram BufferedInputFile."""
    if isinstance(buffer, io.BytesIO):
        buffer.seek(0)
        data = buffer.read()
    else:
        data = buffer
    return BufferedInputFile(file=data, filename=filename)


def _document_looks_like_sticker(message: PyrogramMessage) -> bool:
    """True if message.document is a webp (e.g. sticker sent as file)."""
    doc = getattr(message, "document", None)
    if not doc:
        return False
    fn = (getattr(doc, "file_name", None) or "").lower()
    mime = (getattr(doc, "mime_type", None) or "").lower()
    return fn.endswith(".webp") or "webp" in mime


def _is_forwarded_message(message: PyrogramMessage) -> bool:
    """Check if message is forwarded from another channel/chat."""
    return getattr(message, "forward_origin", None) is not None


async def copy_message(message: PyrogramMessage) -> None:
    """
    Copy message from source channel to target channel.
    
    Args:
        message: Pyrogram Message object from source channel
    """
    if not bot:
        logger.error("Bot instance not available. Cannot copy message.")
        return
    
    if not TARGET_CHANNEL_ID:
        logger.error("TARGET_CHANNEL_ID not configured. Cannot copy message.")
        return
    
    # Check if message was already copied (prevent duplicates)
    if SOURCE_CHANNEL_ID:
        if is_message_copied(str(SOURCE_CHANNEL_ID), str(TARGET_CHANNEL_ID), message.id):
            logger.debug(f"Message {message.id} already copied, skipping duplicate.")
            return
    
    # For media groups, process only the first message (lowest ID) to prevent duplicates
    if message.media_group_id:
        group_key = (message.chat.id, str(message.media_group_id))
        if group_key in _processed_media_groups:
            # Check if this is the first message or a later one
            first_id = _processed_media_groups[group_key]
            if message.id != first_id:
                logger.debug(f"Media group message {message.id} skipped (group already processed via {first_id})")
                return
        else:
            # This is the first message of the group we've seen
            _processed_media_groups[group_key] = message.id
            logger.debug(f"Media group {message.media_group_id}: processing first message {message.id}")
    
    try:
        target_chat_id = int(TARGET_CHANNEL_ID)
        message_type = "unknown"
        
        # Determine message type and copy accordingly; capture target_message_id for reply linking
        target_message_id: Optional[int] = None
        if message.media_group_id:
            message_type = "media_group"
            target_message_id = await copy_media_group(message, target_chat_id)
        elif message.photo:
            message_type = "photo"
            target_message_id = await copy_photo(message, target_chat_id)
        elif message.video:
            message_type = "video"
            target_message_id = await copy_video(message, target_chat_id)
        elif message.document and _document_looks_like_sticker(message):
            message_type = "sticker"
            target_message_id = await copy_document_as_sticker(message, target_chat_id)
        elif message.document:
            message_type = "document"
            target_message_id = await copy_document(message, target_chat_id)
        elif message.voice:
            message_type = "voice"
            target_message_id = await copy_voice(message, target_chat_id)
        elif message.video_note:
            message_type = "video_note"
            target_message_id = await copy_video_note(message, target_chat_id)
        elif message.sticker:
            message_type = "sticker"
            target_message_id = await copy_sticker(message, target_chat_id)
        elif message.animation:
            message_type = "animation"
            target_message_id = await copy_animation(message, target_chat_id)
        elif message.audio:
            message_type = "audio"
            target_message_id = await copy_audio(message, target_chat_id)
        elif message.text or message.caption:
            message_type = "text"
            target_message_id = await copy_text(message, target_chat_id)
        elif getattr(message, "poll", None):
            message_type = "poll"
            target_message_id = await copy_poll(message, target_chat_id)
        elif getattr(message, "dice", None):
            message_type = "dice"
            target_message_id = await copy_unknown_as_text(message, target_chat_id)
        else:
            logger.warning(f"Unknown message type for message {message.id}. Sending as text.")
            message_type = "unknown"
            target_message_id = await copy_unknown_as_text(message, target_chat_id)
        
        if SOURCE_CHANNEL_ID:
            log_copied_message(
                message_id=message.id,
                source_channel_id=str(SOURCE_CHANNEL_ID),
                target_channel_id=str(TARGET_CHANNEL_ID),
                message_type=message_type,
                target_message_id=target_message_id,
            )
        
        logger.info(f"Message {message.id} copied successfully (type: {message_type})")
        
    except Exception as e:
        logger.error(f"Error copying message {message.id}: {e}")


def _build_caption_prefix(message: PyrogramMessage, reply_to_id: Optional[int]) -> str:
    """Reply prefix + forward origin prefix (no sender/content)."""
    reply_prefix = "" if reply_to_id else get_reply_prefix(message, use_html=True)
    forward_prefix = get_forward_origin_prefix(message, use_html=True)
    return reply_prefix + forward_prefix


async def copy_text(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Copy text message with sender name, forward/reply context. Returns target message id for reply linking."""
    try:
        text = message.text or message.caption or ""
        reply_to_id = get_reply_to_message_id(message)
        prefix = _build_caption_prefix(message, reply_to_id)
        sender = get_sender_name(message)
        # If no text but message is forwarded, add forward info
        if not text and _is_forwarded_message(message):
            text = prefix + add_sender_to_text("", sender, use_html=True)
        else:
            text = prefix + add_sender_to_text(text, sender, use_html=True)
        parse_mode = "HTML"

        async def send():
            return await bot.send_message(
                chat_id=target_chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_to_message_id=reply_to_id,
            )
        sent = await retry_telegram_api_async(send, max_attempts=3)
        return sent.message_id if sent else None
    except Exception as e:
        logger.error(f"Error copying text message {message.id}: {e}")
        return None


async def copy_photo(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Copy photo with caption, sender name, forward/reply context. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        caption = message.caption or ""
        prefix = _build_caption_prefix(message, reply_to_id)
        sender = get_sender_name(message)
        caption = prefix + add_sender_to_text(caption, sender, use_html=True)

        # Don't use forward_message for forwarded messages to preserve forward origin info
        if not _is_forwarded_message(message):
            try:
                async def forward():
                    return await bot.forward_message(
                        chat_id=target_chat_id,
                        from_chat_id=message.chat.id,
                        message_id=message.id,
                    )
                sent = await retry_telegram_api_async(forward, max_attempts=2)
                if sent:
                    return sent.message_id
            except Exception:
                pass

        if not pyrogram_client:
            logger.error("Pyrogram client not available. Cannot download photo.")
            return None
        photo_path = await pyrogram_client.download_media(message, in_memory=True)
        if not photo_path:
            logger.error(f"Failed to download photo for message {message.id}")
            return None
        async def send():
            photo_file = _as_input_file(photo_path, "photo.jpg")
            return await bot.send_photo(
                chat_id=target_chat_id,
                photo=photo_file,
                caption=caption,
                parse_mode="HTML",
                reply_to_message_id=reply_to_id,
            )
        sent = await retry_telegram_api_async(send, max_attempts=3)
        return sent.message_id if sent else None
    except Exception as e:
        logger.error(f"Error copying photo {message.id}: {e}")
        return None


async def copy_video(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Copy video with caption, sender name, forward/reply context. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        caption = message.caption or ""
        prefix = _build_caption_prefix(message, reply_to_id)
        sender = get_sender_name(message)
        caption = prefix + add_sender_to_text(caption, sender, use_html=True)
        # Don't use forward_message for forwarded messages to preserve forward origin info
        if not _is_forwarded_message(message):
            try:
                async def forward():
                    return await bot.forward_message(
                        chat_id=target_chat_id,
                        from_chat_id=message.chat.id,
                        message_id=message.id,
                    )
                sent = await retry_telegram_api_async(forward, max_attempts=2)
                if sent:
                    return sent.message_id
            except Exception:
                pass
        if not pyrogram_client:
            logger.error("Pyrogram client not available. Cannot download video.")
            return None
        video_path = await pyrogram_client.download_media(message, in_memory=True)
        if not video_path:
            logger.error(f"Failed to download video for message {message.id}")
            return None
        async def send():
            video_file = _as_input_file(video_path, "video.mp4")
            return await bot.send_video(
                chat_id=target_chat_id,
                video=video_file,
                caption=caption,
                parse_mode="HTML",
                reply_to_message_id=reply_to_id,
            )
        sent = await retry_telegram_api_async(send, max_attempts=3)
        return sent.message_id if sent else None
    except Exception as e:
        logger.error(f"Error copying video {message.id}: {e}")
        return None


async def copy_document(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Copy document (file) with sender, forward/reply context in caption. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        caption = message.caption or ""
        prefix = _build_caption_prefix(message, reply_to_id)
        sender = get_sender_name(message)
        caption = prefix + add_sender_to_text(caption, sender, use_html=True)
        # Don't use forward_message for forwarded messages to preserve forward origin info
        if not _is_forwarded_message(message):
            try:
                async def forward():
                    return await bot.forward_message(
                        chat_id=target_chat_id,
                        from_chat_id=message.chat.id,
                        message_id=message.id,
                    )
                sent = await retry_telegram_api_async(forward, max_attempts=2)
                if sent:
                    return sent.message_id
            except Exception:
                pass
        if not pyrogram_client:
            logger.error("Pyrogram client not available. Cannot download document.")
            return None
        doc_path = await pyrogram_client.download_media(message, in_memory=True)
        if not doc_path:
            logger.error(f"Failed to download document for message {message.id}")
            return None
        async def send():
            doc_file = _as_input_file(doc_path, "document")
            return await bot.send_document(
                chat_id=target_chat_id,
                document=doc_file,
                caption=caption,
                parse_mode="HTML",
                reply_to_message_id=reply_to_id,
            )
        sent = await retry_telegram_api_async(send, max_attempts=3)
        return sent.message_id if sent else None
    except Exception as e:
        logger.error(f"Error copying document {message.id}: {e}")
        return None


async def copy_voice(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Copy voice message with sender, forward/reply context in caption. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        caption = message.caption or ""
        prefix = _build_caption_prefix(message, reply_to_id)
        sender = get_sender_name(message)
        caption = prefix + add_sender_to_text(caption, sender, use_html=True)
        # Don't use forward_message for forwarded messages to preserve forward origin info
        if not _is_forwarded_message(message):
            try:
                async def forward():
                    return await bot.forward_message(
                        chat_id=target_chat_id,
                        from_chat_id=message.chat.id,
                        message_id=message.id,
                    )
                sent = await retry_telegram_api_async(forward, max_attempts=2)
                if sent:
                    return sent.message_id
            except Exception:
                pass
        if not pyrogram_client:
            logger.error("Pyrogram client not available. Cannot download voice.")
            return None
        voice_path = await pyrogram_client.download_media(message, in_memory=True)
        if not voice_path:
            logger.error(f"Failed to download voice for message {message.id}")
            return None
        async def send():
            voice_file = _as_input_file(voice_path, "voice.ogg")
            return await bot.send_voice(
                chat_id=target_chat_id,
                voice=voice_file,
                caption=caption,
                parse_mode="HTML",
                reply_to_message_id=reply_to_id,
            )
        sent = await retry_telegram_api_async(send, max_attempts=3)
        return sent.message_id if sent else None
    except Exception as e:
        logger.error(f"Error copying voice {message.id}: {e}")
        return None


async def copy_video_note(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Copy video note (round video). Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        try:
            async def forward():
                return await bot.forward_message(
                    chat_id=target_chat_id,
                    from_chat_id=message.chat.id,
                    message_id=message.id,
                )
            sent = await retry_telegram_api_async(forward, max_attempts=2)
            return sent.message_id if sent else None
        except Exception:
            pass
        if not pyrogram_client:
            logger.error("Pyrogram client not available. Cannot download video_note.")
            return None
        video_note_path = await pyrogram_client.download_media(message, in_memory=True)
        if not video_note_path:
            logger.error(f"Failed to download video_note for message {message.id}")
            return None
        async def send():
            vn_file = _as_input_file(video_note_path, "video_note.mp4")
            return await bot.send_video_note(
                chat_id=target_chat_id,
                video_note=vn_file,
                reply_to_message_id=reply_to_id,
            )
        sent = await retry_telegram_api_async(send, max_attempts=3)
        return sent.message_id if sent else None
    except Exception as e:
        logger.error(f"Error copying video_note {message.id}: {e}")
        return None


async def copy_sticker(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Copy sticker. Always use send_sticker (never forward_message) to ensure sticker is sent as sticker. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        
        # Send forward origin info as text before sticker if message is forwarded
        forward_prefix = get_forward_origin_prefix(message, use_html=True)
        sender = get_sender_name(message)
        if forward_prefix or sender:
            prefix_text = forward_prefix + add_sender_to_text("", sender, use_html=True)
            if prefix_text.strip():
                try:
                    async def send_text():
                        return await bot.send_message(
                            chat_id=target_chat_id,
                            text=prefix_text,
                            parse_mode="HTML",
                            reply_to_message_id=reply_to_id,
                        )
                    text_msg = await retry_telegram_api_async(send_text, max_attempts=3)
                    if text_msg:
                        reply_to_id = text_msg.message_id
                except Exception as e:
                    logger.warning(f"Failed to send forward origin text for sticker {message.id}: {e}")
        
        # Always download and send as sticker (never use forward_message)
        if not pyrogram_client:
            logger.error("Pyrogram client not available. Cannot download sticker.")
            return None
        sticker_path = await pyrogram_client.download_media(message, in_memory=True)
        if not sticker_path:
            logger.error(f"Failed to download sticker for message {message.id}")
            return None
        async def send():
            sticker_file = _as_input_file(sticker_path, "sticker.webp")
            return await bot.send_sticker(
                chat_id=target_chat_id,
                sticker=sticker_file,
                reply_to_message_id=reply_to_id,
            )
        sent = await retry_telegram_api_async(send, max_attempts=3)
        return sent.message_id if sent else None
    except Exception as e:
        logger.error(f"Error copying sticker {message.id}: {e}")
        return None


async def copy_document_as_sticker(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Send document that is webp (e.g. sticker as file) as sticker. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        
        # Send forward origin info as text before sticker if message is forwarded
        forward_prefix = get_forward_origin_prefix(message, use_html=True)
        sender = get_sender_name(message)
        if forward_prefix or sender:
            prefix_text = forward_prefix + add_sender_to_text("", sender, use_html=True)
            if prefix_text.strip():
                try:
                    async def send_text():
                        return await bot.send_message(
                            chat_id=target_chat_id,
                            text=prefix_text,
                            parse_mode="HTML",
                            reply_to_message_id=reply_to_id,
                        )
                    text_msg = await retry_telegram_api_async(send_text, max_attempts=3)
                    if text_msg:
                        reply_to_id = text_msg.message_id
                except Exception as e:
                    logger.warning(f"Failed to send forward origin text for document-sticker {message.id}: {e}")
        
        if not pyrogram_client:
            logger.error("Pyrogram client not available. Cannot download document as sticker.")
            return None
        sticker_path = await pyrogram_client.download_media(message, in_memory=True)
        if not sticker_path:
            logger.error(f"Failed to download document for message {message.id}")
            return None
        async def send():
            sticker_file = _as_input_file(sticker_path, "sticker.webp")
            return await bot.send_sticker(
                chat_id=target_chat_id,
                sticker=sticker_file,
                reply_to_message_id=reply_to_id,
            )
        sent = await retry_telegram_api_async(send, max_attempts=3)
        return sent.message_id if sent else None
    except Exception as e:
        logger.error(f"Error copying document as sticker {message.id}: {e}")
        return None


async def copy_animation(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Copy animation (GIF) with sender, forward/reply context in caption. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        caption = message.caption or ""
        prefix = _build_caption_prefix(message, reply_to_id)
        sender = get_sender_name(message)
        caption = prefix + add_sender_to_text(caption, sender, use_html=True)
        # Don't use forward_message for forwarded messages to preserve forward origin info
        if not _is_forwarded_message(message):
            try:
                async def forward():
                    return await bot.forward_message(
                        chat_id=target_chat_id,
                        from_chat_id=message.chat.id,
                        message_id=message.id,
                    )
                sent = await retry_telegram_api_async(forward, max_attempts=2)
                if sent:
                    return sent.message_id
            except Exception:
                pass
        if not pyrogram_client:
            logger.error("Pyrogram client not available. Cannot download animation.")
            return None
        animation_path = await pyrogram_client.download_media(message, in_memory=True)
        if not animation_path:
            logger.error(f"Failed to download animation for message {message.id}")
            return None
        async def send():
            anim_file = _as_input_file(animation_path, "animation.gif")
            return await bot.send_animation(
                chat_id=target_chat_id,
                animation=anim_file,
                caption=caption,
                parse_mode="HTML",
                reply_to_message_id=reply_to_id,
            )
        sent = await retry_telegram_api_async(send, max_attempts=3)
        return sent.message_id if sent else None
    except Exception as e:
        logger.error(f"Error copying animation {message.id}: {e}")
        return None


async def copy_audio(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Copy audio file with sender, forward/reply context in caption. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        caption = message.caption or ""
        prefix = _build_caption_prefix(message, reply_to_id)
        sender = get_sender_name(message)
        caption = prefix + add_sender_to_text(caption, sender, use_html=True)
        # Don't use forward_message for forwarded messages to preserve forward origin info
        if not _is_forwarded_message(message):
            try:
                async def forward():
                    return await bot.forward_message(
                        chat_id=target_chat_id,
                        from_chat_id=message.chat.id,
                        message_id=message.id,
                    )
                sent = await retry_telegram_api_async(forward, max_attempts=2)
                if sent:
                    return sent.message_id
            except Exception:
                pass
        if not pyrogram_client:
            logger.error("Pyrogram client not available. Cannot download audio.")
            return None
        audio_path = await pyrogram_client.download_media(message, in_memory=True)
        if not audio_path:
            logger.error(f"Failed to download audio for message {message.id}")
            return None
        async def send():
            audio_file = _as_input_file(audio_path, "audio.mp3")
            return await bot.send_audio(
                chat_id=target_chat_id,
                audio=audio_file,
                caption=caption,
                parse_mode="HTML",
                reply_to_message_id=reply_to_id,
            )
        sent = await retry_telegram_api_async(send, max_attempts=3)
        return sent.message_id if sent else None
    except Exception as e:
        logger.error(f"Error copying audio {message.id}: {e}")
        return None


async def copy_media_group(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Copy media group (album) as a single group. Returns target message id of first message."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        media_group_id = message.media_group_id
        
        # Collect all messages in the media group first (needed for logging)
        group_messages = [message]  # Start with current message
        if pyrogram_client:
            try:
                search_range = 10
                start_id = max(1, message.id - search_range)
                end_id = message.id + search_range
                message_ids = list(range(start_id, end_id + 1))
                messages = await pyrogram_client.get_messages(message.chat.id, message_ids)
                if not isinstance(messages, list):
                    messages = [messages] if messages else []
                for msg in messages:
                    if (msg.media_group_id == media_group_id and 
                        msg.id != message.id and 
                        msg.id not in [m.id for m in group_messages]):
                        group_messages.append(msg)
                group_messages.sort(key=lambda m: m.id)
            except Exception as e:
                logger.debug(f"Could not collect all media group messages: {e}")
        
        # For forwarded messages, use forward_message to preserve forward origin info
        # Telegram will automatically forward the entire media group
        if _is_forwarded_message(message):
            try:
                async def forward():
                    return await bot.forward_message(
                        chat_id=target_chat_id,
                        from_chat_id=message.chat.id,
                        message_id=message.id,
                    )
                sent = await retry_telegram_api_async(forward, max_attempts=2)
                if sent:
                    logger.info(f"Forwarded media group {message.id} successfully (preserves forward origin).")
                    # Log all messages in the media group to prevent duplicate processing
                    if SOURCE_CHANNEL_ID:
                        for msg in group_messages:
                            log_copied_message(
                                message_id=msg.id,
                                source_channel_id=str(SOURCE_CHANNEL_ID),
                                target_channel_id=str(TARGET_CHANNEL_ID),
                                message_type="media_group",
                                target_message_id=sent.message_id,
                            )
                    return sent.message_id
            except Exception as e:
                logger.debug(f"Could not forward media group {message.id}: {e}, will download and send")
        
        # Try to forward the entire media group (Telegram will handle it as one group)
        # This works best for non-forwarded messages
        if not _is_forwarded_message(message):
            try:
                async def forward():
                    return await bot.forward_message(
                        chat_id=target_chat_id,
                        from_chat_id=message.chat.id,
                        message_id=message.id,
                    )
                sent = await retry_telegram_api_async(forward, max_attempts=2)
                if sent:
                    logger.info(f"Media group {message.id} forwarded successfully.")
                    # Log all messages in the media group to prevent duplicate processing
                    if SOURCE_CHANNEL_ID:
                        for msg in group_messages:
                            log_copied_message(
                                message_id=msg.id,
                                source_channel_id=str(SOURCE_CHANNEL_ID),
                                target_channel_id=str(TARGET_CHANNEL_ID),
                                message_type="media_group",
                                target_message_id=sent.message_id,
                            )
                    return sent.message_id
            except Exception as e:
                logger.debug(f"Could not forward media group {message.id}: {e}")
        
        # If forwarding failed, collect all messages and send as group
        if not pyrogram_client:
            logger.error("Pyrogram client not available. Cannot download media group.")
            return None
        
        # group_messages already collected above
        logger.info(f"Found {len(group_messages)} messages in media group {media_group_id}")
        
        # Build media group for aiogram
        media_list = []
        caption = ""
        sender = get_sender_name(message)
        prefix = _build_caption_prefix(message, reply_to_id)
        
        # Collect caption from the last message in group (usually where text is)
        for msg in reversed(group_messages):
            if msg.caption:
                caption = msg.caption
                break
        
        # Build caption with forward/reply info
        caption = prefix + add_sender_to_text(caption, sender, use_html=True)
        
        # Download and prepare all media items
        for idx, msg in enumerate(group_messages):
            try:
                media_data = await pyrogram_client.download_media(msg, in_memory=True)
                if not media_data:
                    logger.warning(f"Could not download media for message {msg.id} in group")
                    continue
                
                media_file = _as_input_file(media_data, f"media_{idx}")
                
                # Determine media type and create appropriate InputMedia
                if msg.photo:
                    # Use caption only for first media item
                    media_list.append(InputMediaPhoto(
                        media=media_file,
                        caption=caption if idx == 0 else None,
                        parse_mode="HTML" if idx == 0 else None
                    ))
                elif msg.video:
                    media_list.append(InputMediaVideo(
                        media=media_file,
                        caption=caption if idx == 0 else None,
                        parse_mode="HTML" if idx == 0 else None
                    ))
                elif msg.document:
                    media_list.append(InputMediaDocument(
                        media=media_file,
                        caption=caption if idx == 0 else None,
                        parse_mode="HTML" if idx == 0 else None
                    ))
                elif msg.animation:
                    media_list.append(InputMediaAnimation(
                        media=media_file,
                        caption=caption if idx == 0 else None,
                        parse_mode="HTML" if idx == 0 else None
                    ))
                elif msg.audio:
                    media_list.append(InputMediaAudio(
                        media=media_file,
                        caption=caption if idx == 0 else None,
                        parse_mode="HTML" if idx == 0 else None
                    ))
                else:
                    logger.warning(f"Unknown media type in media group message {msg.id}")
            except Exception as e:
                logger.error(f"Error processing media group message {msg.id}: {e}")
                continue
        
        if not media_list:
            logger.error(f"No media items prepared for media group {message.id}")
            return None
        
        # Send media group
        async def send():
            return await bot.send_media_group(
                chat_id=target_chat_id,
                media=media_list,
                reply_to_message_id=reply_to_id,
            )
        
        sent_messages = await retry_telegram_api_async(send, max_attempts=3)
        if sent_messages and len(sent_messages) > 0:
            logger.info(f"Media group {message.id} sent successfully ({len(sent_messages)} items).")
            
            # Log all messages in the media group to prevent duplicate processing
            if SOURCE_CHANNEL_ID:
                for msg in group_messages:
                    log_copied_message(
                        message_id=msg.id,
                        source_channel_id=str(SOURCE_CHANNEL_ID),
                        target_channel_id=str(TARGET_CHANNEL_ID),
                        message_type="media_group",
                        target_message_id=sent_messages[0].message_id,  # All point to first message
                    )
            
            return sent_messages[0].message_id
        return None
            
    except Exception as e:
        logger.error(f"Error copying media group {message.id}: {e}")
        return None


def _get_unknown_content(message: PyrogramMessage) -> str:
    """Get human-readable content for unknown message types (dice, emoji, etc.)."""
    if message.text:
        return message.text
    if message.caption:
        return message.caption
    dice = getattr(message, "dice", None)
    if dice:
        emo = getattr(dice, "emoji", "") or "🎲"
        val = getattr(dice, "value", 0)
        return f"{emo} {val}"
    if getattr(message, "poll", None):
        return f"📊 Опрос: {getattr(message.poll.question, 'text', message.poll.question) or 'Опрос'}"
    return "[Медиа-сообщение]"


async def copy_poll(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Send poll with same question and options. Returns target message id."""
    try:
        poll = getattr(message, "poll", None)
        if not poll:
            return None
        question = getattr(poll, "question", None)
        question_text = (getattr(question, "text", None) if question else None) or "Опрос"
        options_raw = getattr(poll, "options", None) or []
        options = []
        for o in options_raw:
            t = getattr(o, "text", None)
            if t is not None:
                options.append(str(t))
        if not options:
            return await copy_unknown_as_text(message, target_chat_id)
        reply_to_id = get_reply_to_message_id(message)
        prefix = _build_caption_prefix(message, reply_to_id)
        sender = get_sender_name(message)
        # Poll question is plain text only; optionally prepend forward/sender as plain line
        question_display = question_text
        if prefix or sender:
            head = (prefix + (sender or "")).replace("<a href=\"", "").replace("\">", ": ").replace("</a>", "")
            head = re.sub(r"<[^>]+>", "", head).strip()
            if head:
                question_display = f"{head}\n\n{question_text}"
        async def send():
            return await bot.send_poll(
                chat_id=target_chat_id,
                question=question_display[:300],
                options=[o[:100] for o in options[:10]],
                is_anonymous=getattr(poll, "is_anonymous", True),
                allows_multiple_answers=getattr(poll, "allows_multiple_answers", False),
                reply_to_message_id=reply_to_id,
            )
        sent = await retry_telegram_api_async(send, max_attempts=3)
        return sent.message_id if sent else None
    except Exception as e:
        logger.error(f"Error copying poll {message.id}: {e}")
        return await copy_unknown_as_text(message, target_chat_id)


async def copy_unknown_as_text(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Send unknown-type message (emoji, dice, etc.) as text with forward/reply and sender. Returns target message id."""
    try:
        content = _get_unknown_content(message)
        reply_to_id = get_reply_to_message_id(message)
        prefix = _build_caption_prefix(message, reply_to_id)
        sender = get_sender_name(message)
        text = prefix + add_sender_to_text(content, sender, use_html=True)
        async def send():
            return await bot.send_message(
                chat_id=target_chat_id,
                text=text,
                parse_mode="HTML",
                reply_to_message_id=reply_to_id,
            )
        sent = await retry_telegram_api_async(send, max_attempts=3)
        return sent.message_id if sent else None
    except Exception as e:
        logger.error(f"Error sending unknown as text {message.id}: {e}")
        return None


async def copy_forward(message: PyrogramMessage, target_chat_id: int) -> None:
    """Try to forward message (used only when bot has access to source)."""
    try:
        async def forward():
            return await bot.forward_message(
                chat_id=target_chat_id,
                from_chat_id=message.chat.id,
                message_id=message.id
            )
        await retry_telegram_api_async(forward, max_attempts=3)
    except Exception as e:
        logger.error(f"Error forwarding message {message.id}: {e}")
        await copy_unknown_as_text(message, target_chat_id)
