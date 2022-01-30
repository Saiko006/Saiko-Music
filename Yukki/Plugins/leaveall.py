import asyncio

from pyrogram import filters

from Yukki import BOT_USERNAME, SUDOERS, app
from Yukki.Core.Clients.cli import ASS_CLI_1, ASS_CLI_2, ASS_CLI_3, ASS_CLI_4, ASS_CLI_5

A1 = ASS_CLI_1
A2 = ASS_CLI_2
A3 = ASS_CLI_3
A4 = ASS_CLI_4
A5 = ASS_CLI_5


@app.on_message(
    filters.command(["leaveall", f"leaveall@{BOT_USERNAME}"])
    & filters.user(SUDOERS)
    & ~filters.edited
)
async def bye(client, message):
    assisten = message.text.split(None, 1)[1]
    if message.from_user.id in SUDOERS:
        left = 0
        failed = 0
        lol = await message.reply("Asisten Meninggalkan semua obrolan")
        async for dialog in assisten.iter_dialogs():
            try:
                await assisten.leave_chat(dialog.chat.id)
                left = left + 1
                await lol.edit(
                    f"""
**🔄 Sedang Memproses**

**✅ Keluar: {left}**
**❌ Gagal: {failed}**
"""
                )
            except:
                failed = failed + 1
                await lol.edit(
                    f"""
**🔄 Sedang Memproses**

**✅ Keluar: {left}**
**❌ Gagal: {failed}**
"""
                )
            await asyncio.sleep(10)
        await lol.delete()
        await message.reply(
            f"""
**💡 Assistant Telah Keluar**

**✅ Keluar: {left}**
**❌ Gagal: {failed}**
""",
        )

        
#ass leave
@app.on_message(filters.command(["assleave", f"assleave@{BOT_USERNAME}"]) & filters.group & ~filters.edited & filters.user(SUDOERS))
async def leave_one(client, message):
    try:
        await assisten.send_message(message.chat.id, "✅ Asisstant Berhasil Keluar")
        await assisten.leave_chat(message.chat.id)
    except BaseException:
        await message.reply_text(
            "❌ **userbot couldn't leave your group, may be floodwaits.**\n\n**» or manually kick userbot from your group**"
        )

        return
    
#leavebot
@app.on_message(filters.command("leavebot") & filters.user(SUDOERS))
async def baaaf(_, message):
    if len(message.command) != 2:
        await message.reply_text(
            "**Ketik:**\n/leavebot [Chat Username or Chat ID]"
        )
        return
    chat = message.text.split(None, 2)[1]
    try:
        await app.leave_chat(chat)
    except Exception as e:
        await message.reply_text(f"Failed\n**Possible reason could be**:{e}")
        print(e)
        return
    await message.reply_text("Bot berhasil keluar")
