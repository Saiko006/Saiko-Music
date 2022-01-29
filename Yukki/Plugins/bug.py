import random
import asyncio
import os

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Yukki import BOT_USERNAME, SUDOERS, app
from config import SUP_GROUP


# ganti nama dan username telegram kalian
OWNER_NAME = "ᴢᴀʟ"
OWNER_USERNAME = "rumahakhirat"


@app.on_message(
    filters.user(SUDOERS) & filters.command(["send", f"send@{BOT_USERNAME}"])
)
async def send(client, message):
    rep = message.reply_to_message
    texted = message.reply_to_message.text
    chid = message.text.split(None, 1)[1]
    if texted:
        await message.delete()
        await rep.delete()
        await client.send_message(chid, texted)
        tm = await message.reply(
            f"**✅ Pesan Yang Anda Balas Telah Dikirim Ke** `{chid}`"
        )
        await asyncio.sleep(5)
        await tm.delete()
        return
    media = await client.download_media(rep)
    if rep.photo:
        await message.delete()
        await rep.delete()
        await client.send_photo(chid, photo=media)
        tm = await message.reply(
            f"**✅ Gambar Yang Anda Balas Telah Dikirim Ke** `{chid}`"
        )
        await asyncio.sleep(5)
        await tm.delete()
    elif rep.video:
        await message.delete()
        await rep.delete()
        await client.send_video(chid, video=media)
        tm = await message.reply(
            f"**✅ Video Yang Anda Balas Telah Dikirim Ke** `{chid}`"
        )
        await asyncio.sleep(5)
        await tm.delete()
    elif rep.sticker:
        await message.delete()
        await rep.delete()
        await client.send_sticker(chid, sticker=media)
        tm = await message.reply(
            f"**✅ Sticker Yang Anda Balas Telah Dikirim Ke** `{chid}`"
        )
        await asyncio.sleep(5)
        await tm.delete()
    elif rep.audio:
        await message.delete()
        await rep.delete()
        await client.send_audio(chid, audio=media)
        tm = await message.reply(
            f"**✅ Audio Yang Anda Balas Telah Dikirim Ke** `{chid}`"
        )
        await asyncio.sleep(5)
        await tm.delete()
    elif rep.voice:
        await message.delete()
        await rep.delete()
        await client.send_voice(chid, voice=media)
        tm = await message.reply(
            f"**✅ Voice Note Yang Anda Balas Telah Dikirim Ke** `{chid}`"
        )
        await asyncio.sleep(5)
        await tm.delete()


@app.on_message(filters.command(["echo", f"echo{BOT_USERNAME}"]) & filters.group)
async def echo(client, message):
    replied = message.reply_to_message
    chat_id = message.chat.id
    urlissed = message.text.split(None, 1)[1]
    if replied:
        await message.delete()
        await replied.reply(urlissed)
        return
    await message.delete()
    await client.send_message(chat_id, urlissed)


@app.on_callback_query(filters.regex("cbcls"))
async def cbcls(client, query):
    a = await client.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_delete_messages:
        return await query.answer(
            "💡 Hanya Admin Yang Dapat Menggunakan Tombol Ini",
            show_alert=True,
        )
    await query.message.delete()


@app.on_callback_query(filters.regex("no_cb"))
async def cb_cls(client, query):
    await query.message.delete()
    tm = await client.send_message(
        query.message.chat.id,
        "**👍 Baiklah {} Semoga Harimu Menyenangkan**".format(query.from_user.mention),
    )
    await asyncio.sleep(5)
    await tm.delete()


@app.on_message(filters.command(["bug", f"bug@{BOT_USERNAME}"]) & filters.group)
async def bug(client, message):
    report = get_text(message)
    if message.chat.username:
        chatusername = f"[{message.chat.title}](t.me/{message.chat.username})"
    else:
        chatusername = message.chat.title
    if not report:
        await message.reply(
            f"""
**🙋🏻‍♂️ Halo {message.from_user.mention} Apa kabar?
🤖 Ada Yang Bisa Saya Bantu?

- Jika Iya, Silahkan Kirim Perintah
• Contoh: `/bug musik nya tidak ke putar`

🔻 Klik Tombol Dibawah Jika Tidak Ada Apa-Apa**
""",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(f"• ᴛᴜᴛᴜᴘ •", callback_data="no_cb"),
                    ],
                ]
            ),
        )
        return
    await client.send_message(
        SUP_GROUP,
        f"""
**✅ [{OWNER_NAME}](t.me/{OWNER_USERNAME}) Ada Laporan Baru

🧑‍💼 Pengguna: {user_name}
💡 Group: {chat_name}
🆔 Id: `{chat_id}`

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
                    InlineKeyboardButton(f"• ᴛᴜᴛᴜᴘ •", callback_data="cbcls"),
                ],
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
