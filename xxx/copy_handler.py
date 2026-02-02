"""
Copy handler module for Копия иксуюемся.
Copies messages from source channel to target channel using aiogram bot.
"""
import asyncio
import io
import html
from typing import Optional
from pyrogram.types import Message as PyrogramMessage
from pyrogram import Client
from aiogram.types import BufferedInputFile
from loader import bot, TARGET_CHANNEL_ID, logger
from utils import retry_telegram_api_async
from database import log_copied_message, get_target_message_id
from config import load_config

# Load configuration
config = load_config()
SOURCE_CHANNEL_ID = config.get('SOURCE_CHANNEL_ID')

# Global variable to store Pyrogram client (set by userbot)
pyrogram_client: Optional[Client] = None


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
    
    try:
        target_chat_id = int(TARGET_CHANNEL_ID)
        message_type = "unknown"
        
        # Determine message type and copy accordingly; capture target_message_id for reply linking
        target_message_id: Optional[int] = None
        if message.media_group_id:
            message_type = "media_group"
            await copy_media_group(message, target_chat_id)
        elif message.photo:
            message_type = "photo"
            target_message_id = await copy_photo(message, target_chat_id)
        elif message.video:
            message_type = "video"
            target_message_id = await copy_video(message, target_chat_id)
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


async def copy_text(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Copy text message with sender name and reply context. Returns target message id for reply linking."""
    try:
        text = message.text or message.caption or ""
        reply_to_id = get_reply_to_message_id(message)
        reply_prefix = "" if reply_to_id else get_reply_prefix(message, use_html=True)
        sender = get_sender_name(message)
        text = reply_prefix + add_sender_to_text(text, sender, use_html=True)
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
    """Copy photo with caption, sender name and reply context. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        caption = message.caption or ""
        reply_prefix = "" if reply_to_id else get_reply_prefix(message, use_html=True)
        sender = get_sender_name(message)
        caption = reply_prefix + add_sender_to_text(caption, sender, use_html=True)

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
    """Copy video with caption, sender name and reply context. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        caption = message.caption or ""
        reply_prefix = "" if reply_to_id else get_reply_prefix(message, use_html=True)
        sender = get_sender_name(message)
        caption = reply_prefix + add_sender_to_text(caption, sender, use_html=True)
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
    """Copy document (file) with sender and reply context in caption. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        caption = message.caption or ""
        reply_prefix = "" if reply_to_id else get_reply_prefix(message, use_html=True)
        sender = get_sender_name(message)
        caption = reply_prefix + add_sender_to_text(caption, sender, use_html=True)
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
    """Copy voice message with sender and reply context in caption. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        caption = message.caption or ""
        reply_prefix = "" if reply_to_id else get_reply_prefix(message, use_html=True)
        sender = get_sender_name(message)
        caption = reply_prefix + add_sender_to_text(caption, sender, use_html=True)
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
    """Copy sticker. Returns target message id."""
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


async def copy_animation(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Copy animation (GIF) with sender and reply context in caption. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        caption = message.caption or ""
        reply_prefix = "" if reply_to_id else get_reply_prefix(message, use_html=True)
        sender = get_sender_name(message)
        caption = reply_prefix + add_sender_to_text(caption, sender, use_html=True)
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
    """Copy audio file with sender and reply context in caption. Returns target message id."""
    try:
        reply_to_id = get_reply_to_message_id(message)
        caption = message.caption or ""
        reply_prefix = "" if reply_to_id else get_reply_prefix(message, use_html=True)
        sender = get_sender_name(message)
        caption = reply_prefix + add_sender_to_text(caption, sender, use_html=True)
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


async def copy_media_group(message: PyrogramMessage, target_chat_id: int) -> None:
    """Copy media group (album)."""
    try:
        # For media groups, we need to get all messages in the group
        # This is a simplified version - in production, you might want to
        # collect all messages in the group first
        
        # Try to forward the message (Telegram will handle the group)
        # Note: Forwarding might not work if bot doesn't have access
        # In that case, we'll copy individual items
        
        # For now, we'll try to copy the current message
        # In a full implementation, you'd want to collect all messages
        # with the same media_group_id and send them as a group
        
        logger.info(f"Media group detected for message {message.id}. Copying individually...")
        
        # Copy as individual message (fallback)
        if message.photo:
            await copy_photo(message, target_chat_id)
        elif message.video:
            await copy_video(message, target_chat_id)
        elif message.document:
            await copy_document(message, target_chat_id)
        else:
            logger.warning(f"Unknown media type in media group for message {message.id}")
            
    except Exception as e:
        logger.error(f"Error copying media group {message.id}: {e}")


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


async def copy_unknown_as_text(message: PyrogramMessage, target_chat_id: int) -> Optional[int]:
    """Send unknown-type message (emoji, dice, etc.) as text with reply and sender. Returns target message id."""
    try:
        content = _get_unknown_content(message)
        reply_to_id = get_reply_to_message_id(message)
        reply_prefix = "" if reply_to_id else get_reply_prefix(message, use_html=True)
        sender = get_sender_name(message)
        text = reply_prefix + add_sender_to_text(content, sender, use_html=True)
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
