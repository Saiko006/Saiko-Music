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
        await client.send_message(
            message.chat.id,
            f"""
**💡 Assistant Telah Keluar**

**✅ Keluar: {left}**
**❌ Gagal: {failed}**
""",
        )
