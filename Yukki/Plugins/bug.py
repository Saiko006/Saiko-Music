import random
import asyncio
import os

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Yukki import BOT_USERNAME, SUDOERS, app
from Yukki.Decorators.admins import AdminRightsCheck as authorized_users_only
from config import SUP_GROUP

__MODULE__ = "ʙᴜɢ"
__HELP__ = """

/bug [To report a problem]
- ex : /bug bot silent
"""



# ganti nama dan username telegram kalian
OWNER_NAME = "ᴢᴀʟ"
OWNER_USERNAME = "rumahakhirat"


@app.on_message(filters.user(SUDOERS) & filters.command(["echos", f"echos@{BOT_USERNAME}"]) & filters.group)
async def s(client, message):
    r = message.reply_to_message
    c = message.chat.id
    if r:
        await message.delete()
        await message.delete()
        await app.send_sticker(c, r.sticker.file_id)


@app.on_message(filters.user(SUDOERS) & filters.command(["echor", f"echor@{BOT_USERNAME}"]) & filters.group)
async def r(client, message):
    r = message.reply_to_message
    c = message.chat.id
    s = message.text.split(None, 1)[1]
    await message.delete()
    await app.send_sticker(c, s)


@app.on_message(filters.user(SUDOERS) & filters.command(["echo", f"echo@{BOT_USERNAME}"]) & filters.group)
async def p(client, message):
    replied = message.reply_to_message
    chat_id = message.chat.id
    urlissed = message.text.split(None, 1)[1]
    if replied:
        await message.delete()
        await replied.reply(f"{urlissed}")
        return
    await message.delete()
    await app.send_message(chat_id, f"{urlissed}")


@app.on_message(filters.user(SUDOERS) & filters.command(["send", f"send@{BOT_USERNAME}"]))
async def send(client, message):
    chat_id = message.text.split(None, 1)[1]
    replied = message.reply_to_message
    if replied.text:
        await message.delete()
        await client.send_message(chat_id, replied.text)
        tm = await message.reply(
            f"**✅ Pesan Yang Anda Balas Telah Dikirim Ke** `{chat_id}`"
        )
        await asyncio.sleep(5)
        await tm.delete()
    elif replied.sticker.file_id:
        await message.delete()
        await client.send_sticker(chat_id, replied.sticker.file_id)
        tm = await message.reply(
            f"**✅ Sticker Yang Anda Balas Telah Dikirim Ke** `{chat_id}`"
        )
        await asyncio.sleep(5)
        await tm.delete()


@app.on_message(filters.command(["bug", f"bug@{BOT_USERNAME}"]) & filters.group)
async def bug(_, message):
    report = message.text.split(None, 1)[1]
    if message.chat.username:
        chatusername = f"[{message.chat.title}](t.me/{message.chat.username})"
    else:
        chatusername = message.chat.title
    if not report:
        await message.reply(
            "Contoh menggunakan fitur ini\n`/bug assisten nggak mau turun`",
        )
        return
    await app.send_message(
        SUP_GROUP,
        f"""
**✅ [{OWNER_NAME}](t.me/{OWNER_USERNAME}) Ada Laporan Baru

🧑‍💼 Pengguna: {message.from_user.mention}
💡 Group: {chatusername}
🆔 Id: `{message.chat.id}`

💬 Pesan: {report}**
""",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"• {message.from_user.first_name} •",
                        url=f"{message.link}",
                    ),
                ],
                [
                    InlineKeyboardButton(text=f" ᴄʟᴏsᴇ ", callback_data="cls"),
                ]
            ]
        ),
    )
    await message.reply(
        f"**🙏🏻 Terimakasih {message.from_user.mention} laporan anda telah terkirim ke admin**"
    )


APAKAH_TEXT = [
    "Mungkin iya",
    "Mungkin",
    "Iya",
    "Tidak",
    "Nggak tau",
    "Benar",
    "Salah",
    "Lu kali bukan dia",
    "Apa iya",
    "Kayaknya",
    "Ah masa",
    "Masa sih",
    "Oh gitu ya",
    "Oh oke",
    "Stres",
    "Apasih",
    "Gak jelas",
    "Keren",
    "Tolol",
    "Anjing",
    "Anjir",
    "Goblok",
    "Ganteng",
    "Jelek",
    "Bapakau",
    "Dadjal",
    "Setan",
    "Iblis",
    "Babi",
    "Kontol",
    "Oh",
    "Oke",
    "Memek",
    "Kepala kau",
    "Bodo amat",
    "B aja sih",
    "Yang bener",
    "Terus",
    "Bohong",
    "Jangan bohong",
    "Emang",
    "Emang gitu",
    "Apa dong",
    "Apa",
    "Gimana",
    "Apanya",
]


@app.on_message(filters.regex("apakah|Apakah|APAKAH"))
async def apakah(_, message):
    await message.reply(random.choice(APAKAH_TEXT))
