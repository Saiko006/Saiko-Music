from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, InputMediaPhoto, Message)

from Yukki import db_mem


def others_markup(videoid, user_id):
    if videoid not in db_mem:
        db_mem[videoid] = {}
    db_mem[videoid]["check"] = 1
    buttons = [
        [
            InlineKeyboardButton(
                text="🔎 ʟʏʀɪᴄs",
                callback_data=f"lyrics {videoid}|{user_id}",
            )
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"resumecb"),
            InlineKeyboardButton(text="II", callback_data=f"pausecb"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"skipcb"),
            InlineKeyboardButton(text="▢", callback_data=f"stopcb"),
        ],
        [
            InlineKeyboardButton(text="➕ ʏᴏᴜʀ ʟɪsᴛ​", callback_data=f"your_playlist {videoid}|{user_id})",
            ),
            InlineKeyboardButton(text="➕ ɢʀᴏᴜᴘ ʟɪsᴛ​", callback_data=f"group_playlist {videoid}|{user_id})",
            ),                     
        ],
        [
            InlineKeyboardButton(
                text="⇩ ᴜɴᴅᴜʜ ᴀᴜᴅɪᴏ", callback_data=f"gets audio|{videoid}|{user_id}"
            ),
            InlineKeyboardButton(
                text="⇩ ᴜɴᴅᴜʜ ᴠɪᴅᴇᴏ", callback_data=f"gets video|{videoid}|{user_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="⬅️", callback_data=f"pr_go_back_timer {videoid}|{user_id}"
            ),
            InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data=f"close"),
        ],
    ]
    return buttons




def download_markup(videoid, user_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="⇩ ᴜɴᴅᴜʜ ᴀᴜᴅɪᴏ",
                callback_data=f"gets audio|{videoid}|{user_id}",
            ),
            InlineKeyboardButton(
                text="⇩ ᴜɴᴅᴜʜ ᴠɪᴅᴇᴏ",
                callback_data=f"gets video|{videoid}|{user_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⬅️ ʙᴀᴄᴋ", callback_data=f"goback {videoid}|{user_id}"
            ),
            InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data=f"close"),
        ],
    ]
    return buttons
