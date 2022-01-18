from Yukki import BOT_USERNAME
from Yukki.Core.Clients.cli import app
from config import LOG_GROUP_ID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 


async def LOG_CHAT(message, what):
    if message.chat.username:
        chatusername = f"[{message.chat.title}](t.me/{message.chat.username})"
    else:
        chatusername = f"{message.chat.title}"
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    logger_text = f"""
**💡 {what}**
**🧑‍💼 Pengguna:** {mention}
**💬 Group:** {chatusername}
**🆔 Id:** `{chat_id}`
**✨ Permintaan:** {message.text}
"""
    await app.send_message(
        LOG_GROUP_ID,
        logger_text,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"• {user_name} •",
                        url=f"{message.link}",
                    )
                ]
            ]
        ),
    )



