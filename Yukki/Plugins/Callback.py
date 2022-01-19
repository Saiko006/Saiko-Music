import asyncio
import os
import random
from asyncio import QueueEmpty

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import get_queue
from Yukki.Inline.start import start_pannel
from Yukki import BOT_USERNAME, MUSIC_BOT_NAME, app, db_mem
from Yukki.Core.PyTgCalls import Queues
from Yukki.Core.PyTgCalls.Converter import convert
from Yukki.Core.PyTgCalls.Downloader import download
from Yukki.Core.PyTgCalls.Yukki import (join_stream, pause_stream,
                                        resume_stream, skip_stream,
                                        skip_video_stream, stop_stream)
from Yukki.Database import (_get_playlists, delete_playlist, get_playlist,
                            get_playlist_names, is_active_chat,
                            remove_active_video_chat, save_playlist)
from Yukki.Database.queue import (add_active_chat, is_active_chat,
                                  is_music_playing, music_off, music_on,
                                  remove_active_chat)
from Yukki.Decorators.admins import AdminRightsCheckCB
from Yukki.Decorators.checker import checkerCB
from Yukki.Inline import (audio_markup, audio_markup2, download_markup,
                          fetch_playlist, paste_queue_markup, primary_markup,
                          secondary_markup2)
from Yukki.Utilities.changers import time_to_seconds
from Yukki.Utilities.chat import specialfont_to_normal
from Yukki.Utilities.paste import isPreviewUp, paste_queue
from Yukki.Utilities.theme import check_theme
from Yukki.Utilities.thumbnails import gen_thumb
from Yukki.Utilities.timer import start_timer
from Yukki.Utilities.youtube import get_m3u8, get_yt_info_id

loop = asyncio.get_event_loop()


@app.on_callback_query(filters.regex("forceclose"))
async def forceclose(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    query, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "You're not allowed to close this.", show_alert=True
        )
    await CallbackQuery.message.delete()
    await CallbackQuery.answer()


@app.on_callback_query(
    filters.regex(pattern=r"^(pausecb|skipcb|stopcb|resumecb)$")
)
@AdminRightsCheckCB
@checkerCB
async def admin_risghts(_, CallbackQuery):
    global get_queue
    command = CallbackQuery.matches[0].group(1)
    if not await is_active_chat(CallbackQuery.message.chat.id):
        return await CallbackQuery.answer(
            "Nothing is playing on voice chat.", show_alert=True
        )
    chat_id = CallbackQuery.message.chat.id
    if command == "pausecb":
        if not await is_music_playing(chat_id):
            return await CallbackQuery.answer(
                "Music is already Paused", show_alert=True
            )
        await music_off(chat_id)
        await pause_stream(chat_id)
        await CallbackQuery.message.reply_text(
            f"🎧 Voicechat Paused by {CallbackQuery.from_user.mention}!",
            reply_markup=audio_markup2,
        )
        await CallbackQuery.message.delete()
        await CallbackQuery.answer("Paused", show_alert=True)
    if command == "resumecb":
        if await is_music_playing(chat_id):
            return await CallbackQuery.answer(
                "Music is already Resumed.", show_alert=True
            )
        await music_on(chat_id)
        await resume_stream(chat_id)
        await CallbackQuery.message.reply_text(
            f"🎧 Voicechat Resumed by {CallbackQuery.from_user.mention}!",
            reply_markup=audio_markup2,
        )
        await CallbackQuery.message.delete()
        await CallbackQuery.answer("Resumed", show_alert=True)
    if command == "stopcb":
        if CallbackQuery.message.chat.id not in db_mem:
            db_mem[CallbackQuery.message.chat.id] = {}
        wtfbro = db_mem[CallbackQuery.message.chat.id]
        wtfbro["live_check"] = False
        try:
            Queues.clear(chat_id)
        except QueueEmpty:
            pass
        await remove_active_chat(chat_id)
        await remove_active_video_chat(chat_id)
        await stop_stream(chat_id)
        await CallbackQuery.message.reply_text(
            f"🎧 Voicechat End/Stopped by {CallbackQuery.from_user.mention}!",
            reply_markup=audio_markup2,
        )
        await CallbackQuery.message.delete()
        await CallbackQuery.answer("Stopped", show_alert=True)
    if command == "skipcb":
        if CallbackQuery.message.chat.id not in db_mem:
            db_mem[CallbackQuery.message.chat.id] = {}
        wtfbro = db_mem[CallbackQuery.message.chat.id]
        wtfbro["live_check"] = False
        Queues.task_done(chat_id)
        if Queues.is_empty(chat_id):
            await remove_active_chat(chat_id)
            await remove_active_video_chat(chat_id)
            await CallbackQuery.message.reply_text(
                f"No more music in __Queue__ \n\nLeaving Voice Chat..Button Used By :- {CallbackQuery.from_user.mention}"
            )
            await stop_stream(chat_id)
            await CallbackQuery.message.delete()
            await CallbackQuery.answer(
                "Skipped. No more music in Queue", show_alert=True
            )
            return
        else:
            videoid = Queues.get(chat_id)["file"]
            got_queue = get_queue.get(CallbackQuery.message.chat.id)
            if got_queue:
                got_queue.pop(0)
            finxx = f"{videoid[0]}{videoid[1]}{videoid[2]}"
            aud = 0
            if str(finxx) == "raw":
                await CallbackQuery.message.delete()
                await CallbackQuery.answer("Skipped!", show_alert=True)
                await skip_stream(chat_id, videoid)
                afk = videoid
                title = db_mem[videoid]["title"]
                duration_min = db_mem[videoid]["duration"]
                duration_sec = int(time_to_seconds(duration_min))
                mention = db_mem[videoid]["username"]
                videoid = db_mem[videoid]["videoid"]
                if str(videoid) == "smex1":
                    buttons = buttons = audio_markup(
                        videoid,
                        CallbackQuery.from_user.id,
                        duration_min,
                        duration_min,
                    )
                    thumb = "Utils/Telegram.JPEG"
                    aud = 1
                else:
                    _path_ = _path_ = (
                        (str(afk))
                        .replace("_", "", 1)
                        .replace("/", "", 1)
                        .replace(".", "", 1)
                    )
                    thumb = f"cache/{_path_}final.png"
                    buttons = primary_markup(
                        videoid,
                        CallbackQuery.from_user.id,
                        duration_min,
                        duration_min,
                    )
                final_output = await CallbackQuery.message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=f"⏭️<b>__Skipped Voice Chat__</b>\n\n🏷<b>__Judul:__</b> {title} \n⏱️<b>__Duration:__</b> {duration_min} \n🎧<b>__Atas permintaan:__ </b> {mention}",
                )
                await start_timer(
                    videoid,
                    duration_min,
                    duration_sec,
                    final_output,
                    CallbackQuery.message.chat.id,
                    CallbackQuery.message.from_user.id,
                    aud,
                )
            if str(finxx) == "s1s":
                afk = videoid
                await CallbackQuery.answer()
                mystic = await CallbackQuery.message.reply_text(
                    "Skipped! Please Wait Changing Video Stream...."
                )
                read = (str(videoid)).replace("s1s_", "", 1)
                s = read.split("_+_")
                quality = s[0]
                videoid = s[1]
                if int(quality) == 1080:
                    try:
                        await skip_video_stream(chat_id, videoid, 720, mystic)
                    except Exception as e:
                        return await mystic.edit(
                            f"Error while changing video stream.\n\nPossible Reason:- {e}"
                        )
                    buttons = secondary_markup2(
                        "Smex1", CallbackQuery.from_user.id
                    )
                    mention = db_mem[afk]["username"]
                    await mystic.delete()
                    final_output = await CallbackQuery.message.reply_photo(
                        photo="Utils/Telegram.JPEG",
                        reply_markup=InlineKeyboardMarkup(buttons),
                        caption=(
                            f"⏭️<b>__Skipped Video Chat__</b>\n\n🎧**__Atas permintaan:__** {mention}"
                        ),
                    )
                    await mystic.delete()
                else:
                    (
                        title,
                        duration_min,
                        duration_sec,
                        thumbnail,
                    ) = get_yt_info_id(videoid)
                    nrs, ytlink = await get_m3u8(videoid)
                    if nrs == 0:
                        return await mystic.edit(
                            "Failed to fetch Video Formats.",
                        )
                    try:
                        await skip_video_stream(
                            chat_id, ytlink, quality, mystic
                        )
                    except Exception as e:
                        return await mystic.edit(
                            f"Error while changing video stream.\n\nPossible Reason:- {e}"
                        )
                    theme = await check_theme(chat_id)
                    c_title = CallbackQuery.message.chat.title
                    user_id = db_mem[afk]["user_id"]
                    chat_title = await specialfont_to_normal(c_title)
                    thumb = await gen_thumb(
                        thumbnail, title, user_id, theme, chat_title
                    )
                    buttons = primary_markup(
                        videoid, user_id, duration_min, duration_min
                    )
                    mention = db_mem[afk]["username"]
                    await mystic.delete()
                    final_output = await CallbackQuery.message.reply_photo(
                        photo=thumb,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        caption=(
                            f"⏭️<b>__Skipped Video Chat__</b>\n\n🏷<b>__Judul:__ </b>[{title[:25]}](https://www.youtube.com/watch?v={videoid}) \n⏱**__Durasi__**: {duration_min} \n🎧**__Atas permintaan:__** {mention}"
                        ),
                    )
                    os.remove(thumb)
                    await start_timer(
                        videoid,
                        duration_min,
                        duration_sec,
                        final_output,
                        CallbackQuery.message.chat.id,
                        CallbackQuery.message.from_user.id,
                        aud,
                    )
            else:
                await CallbackQuery.message.delete()
                await CallbackQuery.answer(
                    "Skipped! Playlist Playing....", show_alert=True
                )
                mystic = await CallbackQuery.message.reply_text(
                    f"**{MUSIC_BOT_NAME} Playlist Function**\n\n__Downloading Next Music From Playlist....__\n\nButton Used By :- {CallbackQuery.from_user.mention}"
                )
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                ) = get_yt_info_id(videoid)
                await mystic.edit(
                    f"**{MUSIC_BOT_NAME} Downloader**\n\n**Title:** {title[:50]}\n\n0% ▓▓▓▓▓▓▓▓▓▓▓▓ 100%"
                )
                downloaded_file = await loop.run_in_executor(
                    None, download, videoid, mystic, title
                )
                raw_path = await convert(downloaded_file)
                await skip_stream(chat_id, raw_path)
                theme = await check_theme(chat_id)
                chat_title = await specialfont_to_normal(
                    CallbackQuery.message.chat.title
                )
                thumb = await gen_thumb(
                    thumbnail,
                    title,
                    CallbackQuery.from_user.id,
                    theme,
                    chat_title,
                )
                buttons = primary_markup(
                    videoid,
                    CallbackQuery.from_user.id,
                    duration_min,
                    duration_min,
                )
                await mystic.delete()
                mention = db_mem[videoid]["username"]
                final_output = await CallbackQuery.message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=(
                        f"⏭️<b>__Skipped Voice Chat__</b>\n\n🏷<b>__Judul:__ </b>[{title[:25]}](https://www.youtube.com/watch?v={videoid}) \n⏱️<b>__Durasi:__</b> {duration_min} Mins\n🎧**__Atas permintaan:__** {mention}"
                    ),
                )
                os.remove(thumb)
                await start_timer(
                    videoid,
                    duration_min,
                    duration_sec,
                    final_output,
                    CallbackQuery.message.chat.id,
                    CallbackQuery.message.from_user.id,
                    aud,
                )


@app.on_callback_query(filters.regex("play_playlist"))
async def play_playlist(_, CallbackQuery):
    global get_queue
    loop = asyncio.get_event_loop()
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    callback_request = callback_data.split(None, 1)[1]
    user_id, smex, type = callback_request.split("|")
    chat_title = CallbackQuery.message.chat.title
    user_id = int(user_id)
    if chat_id not in db_mem:
        db_mem[chat_id] = {}
    if smex == "third":
        _playlist = await get_playlist_names(user_id, type)
        try:
            user = await app.get_users(user_id)
            third_name = user.first_name
        except:
            third_name = "Deleted Account"
    elif smex == "Personal":
        if CallbackQuery.from_user.id != int(user_id):
            return await CallbackQuery.answer(
                "This is not for you! Play your own playlist", show_alert=True
            )
        _playlist = await get_playlist_names(user_id, type)
        third_name = CallbackQuery.from_user.first_name
    elif smex == "Group":
        _playlist = await get_playlist_names(
            CallbackQuery.message.chat.id, type
        )
        user_id = CallbackQuery.message.chat.id
        third_name = chat_title
    else:
        return await CallbackQuery.answer("Error In Playlist.")
    if CallbackQuery.message.chat.id not in db_mem:
        db_mem[CallbackQuery.message.chat.id] = {}
    try:
        read1 = db_mem[CallbackQuery.message.chat.id]["live_check"]
        if read1:
            return await CallbackQuery.answer(
                "Live Streaming Playing...Stop it to play playlist",
                show_alert=True,
            )
        else:
            pass
    except:
        pass
    if not _playlist:
        return await CallbackQuery.answer(
            f"This User has no playlist on servers.", show_alert=True
        )
    else:
        await CallbackQuery.message.delete()
        mystic = await CallbackQuery.message.reply_text(
            f"Starting Playlist Of {third_name}.\n\nRequested By:- {CallbackQuery.from_user.first_name}"
        )
        msg = f"Queued Playlist:\n\n"
        j = 0
        for_t = 0
        for_p = 0
        for shikhar in _playlist:
            _note = await get_playlist(user_id, shikhar, type)
            title = _note["title"]
            videoid = _note["videoid"]
            url = f"https://www.youtube.com/watch?v={videoid}"
            duration = _note["duration"]
            if await is_active_chat(chat_id):
                position = await Queues.put(chat_id, file=videoid)
                j += 1
                for_p = 1
                msg += f"{j}- {title[:50]}\n"
                msg += f"Queued Position- {position}\n\n"
                if videoid not in db_mem:
                    db_mem[videoid] = {}
                db_mem[videoid]["username"] = CallbackQuery.from_user.mention
                db_mem[videoid]["chat_title"] = chat_title
                db_mem[videoid]["user_id"] = user_id
                got_queue = get_queue.get(CallbackQuery.message.chat.id)
                title = title
                user = CallbackQuery.from_user.first_name
                duration = duration
                to_append = [title, user, duration]
                got_queue.append(to_append)
            else:
                loop = asyncio.get_event_loop()
                send_video = videoid
                for_t = 1
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                ) = get_yt_info_id(videoid)
                mystic = await mystic.edit(
                    f"**{MUSIC_BOT_NAME} Downloader**\n\n**Title:** {title[:50]}\n\n0% ▓▓▓▓▓▓▓▓▓▓▓▓ 100%"
                )
                downloaded_file = await loop.run_in_executor(
                    None, download, videoid, mystic, title
                )
                raw_path = await convert(downloaded_file)
                if not await join_stream(chat_id, raw_path):
                    return await mystic.edit(
                        "Error Joining Voice Chat. Make sure Voice Chat is Enabled."
                    )
                theme = await check_theme(chat_id)
                chat_title = await specialfont_to_normal(chat_title)
                thumb = await gen_thumb(
                    thumbnail,
                    title,
                    CallbackQuery.from_user.id,
                    theme,
                    chat_title,
                )
                buttons = primary_markup(
                    videoid,
                    CallbackQuery.from_user.id,
                    duration_min,
                    duration_min,
                )
                await mystic.delete()
                get_queue[CallbackQuery.message.chat.id] = []
                got_queue = get_queue.get(CallbackQuery.message.chat.id)
                title = title
                user = CallbackQuery.from_user.first_name
                duration = duration_min
                to_append = [title, user, duration]
                got_queue.append(to_append)
                await music_on(chat_id)
                await add_active_chat(chat_id)
                cap = f"🏷<b>__Judul:__ </b>[{title[:25]}](https://www.youtube.com/watch?v={videoid}) \n💡<b>__Info:__</b> [Get Additional Information](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n⏱**__Durasi__**: {duration_min} \n🎧**_Atas permintaan:__** {CallbackQuery.from_user.mention}"
                final_output = await CallbackQuery.message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=cap,
                )
                os.remove(thumb)
        await mystic.delete()
        if for_p == 1:
            m = await CallbackQuery.message.reply_text(
                "Pasting Queued Playlist to Bin"
            )
            link = await paste_queue(msg)
            preview = link + "/preview.png"
            url = link + "/index.txt"
            buttons = paste_queue_markup(url)
            if await isPreviewUp(preview):
                await CallbackQuery.message.reply_photo(
                    photo=preview,
                    caption=f"This is Queued Playlist of {third_name}.\n\nPlayed by :- {CallbackQuery.from_user.mention}",
                    quote=False,
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
                await m.delete()
            else:
                await CallbackQuery.message.reply_text(
                    text=msg, reply_markup=audio_markup2
                )
                await m.delete()
        else:
            await CallbackQuery.message.reply_text(
                "Only 1 Music in Playlist.. No more music to add in queue."
            )
        if for_t == 1:
            await start_timer(
                send_video,
                duration_min,
                duration_sec,
                final_output,
                CallbackQuery.message.chat.id,
                CallbackQuery.message.from_user.id,
                0,
            )


@app.on_callback_query(filters.regex("add_playlist"))
async def group_playlist(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, type, genre = callback_request.split("|")
    if type == "Personal":
        user_id = CallbackQuery.from_user.id
    elif type == "Group":
        a = await app.get_chat_member(
            CallbackQuery.message.chat.id, CallbackQuery.from_user.id
        )
        if not a.can_manage_voice_chats:
            return await CallbackQuery.answer(
                "You don't have the required permission to perform this action.\nPermission: MANAGE VOICE CHATS",
                show_alert=True,
            )
        user_id = CallbackQuery.message.chat.id
    _count = await get_playlist_names(user_id, genre)
    if not _count:
        sex = await CallbackQuery.message.reply_text(
            f"Welcome To {MUSIC_BOT_NAME}'s Playlist Feature.\n\nGenerating Your  Playlist In Database...Please wait.\n\nGenre:- {genre}"
        )
        await asyncio.sleep(2)
        await sex.delete()
        count = len(_count)
    else:
        count = len(_count)
    count = int(count)
    if count == 50:
        return await CallbackQuery.answer(
            "Sorry! You can only have 50 music in a playlist.",
            show_alert=True,
        )
    loop = asyncio.get_event_loop()
    await CallbackQuery.answer()
    title, duration_min, duration_sec, thumbnail = get_yt_info_id(videoid)
    _check = await get_playlist(user_id, videoid, genre)
    title = title[:50]
    if _check:
        return await CallbackQuery.message.reply_text(
            f"{CallbackQuery.from_user.mention}, Its already in the Playlist!"
        )
    assis = {
        "videoid": videoid,
        "title": title,
        "duration": duration_min,
    }
    await save_playlist(user_id, videoid, assis, genre)
    Name = CallbackQuery.from_user.first_name
    return await CallbackQuery.message.reply_text(
        f"Added to {type}'s {genre} Playlist by {CallbackQuery.from_user.mention}"
    )


@app.on_callback_query(filters.regex("check_playlist"))
async def check_playlist(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    type, genre = callback_request.split("|")
    if type == "Personal":
        user_id = CallbackQuery.from_user.id
        user_name = CallbackQuery.from_user.first_name
    elif type == "Group":
        user_id = CallbackQuery.message.chat.id
        user_name = CallbackQuery.message.chat.title
    _playlist = await get_playlist_names(user_id, genre)
    if not _playlist:
        return await CallbackQuery.answer(
            f"No {genre} Playlist on servers. Try adding musics in playlist.",
            show_alert=True,
        )
    else:
        j = 0
        await CallbackQuery.answer()
        await CallbackQuery.message.delete()
        msg = f"Fetched Playlist:\n\n"
        for shikhar in _playlist:
            j += 1
            _note = await get_playlist(user_id, shikhar, genre)
            title = _note["title"]
            duration = _note["duration"]
            msg += f"{j}- {title[:60]}\n"
            msg += f"    Duration- {duration} Min(s)\n\n"
        m = await CallbackQuery.message.reply_text("Pasting Playlist to Bin")
        link = await paste_queue(msg)
        preview = link + "/preview.png"
        url = link + "/index.txt"
        buttons = fetch_playlist(
            user_name, type, genre, CallbackQuery.from_user.id, url
        )
        if await isPreviewUp(preview):
            await CallbackQuery.message.reply_photo(
                photo=preview,
                caption=f"This is Playlist of {user_name}.",
                quote=False,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
            await m.delete()
        else:
            await CallbackQuery.message.reply_text(
                text=msg, reply_markup=audio_markup2
            )
            await m.delete()


@app.on_callback_query(filters.regex("delete_playlist"))
async def del_playlist(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    type, genre = callback_request.split("|")
    if str(type) == "Personal":
        user_id = CallbackQuery.from_user.id
        user_name = CallbackQuery.from_user.first_name
    elif str(type) == "Group":
        a = await app.get_chat_member(
            CallbackQuery.message.chat.id, CallbackQuery.from_user.id
        )
        if not a.can_manage_voice_chats:
            return await CallbackQuery.answer(
                "You don't have the required permission to perform this action.\nPermission: MANAGE VOICE CHATS",
                show_alert=True,
            )
        user_id = CallbackQuery.message.chat.id
        user_name = CallbackQuery.message.chat.title
    _playlist = await get_playlist_names(user_id, genre)
    if not _playlist:
        return await CallbackQuery.answer(
            "Group has no Playlist on Bot's Server", show_alert=True
        )
    else:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
        for shikhar in _playlist:
            await delete_playlist(user_id, shikhar, genre)
    await CallbackQuery.message.reply_text(
        f"Successfully deleted {type}'s {genre} whole playlist\n\nBy :- {CallbackQuery.from_user.mention}"
    )


@app.on_callback_query(filters.regex("audio_video_download"))
async def down_playlisyts(_, CallbackQuery):
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id
    videoid, user_id = callback_request.split("|")
    buttons = download_markup(videoid, user_id)
    await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    
    
@app.on_callback_query(filters.regex(pattern=r"good"))
async def good(_, CallbackQuery):
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id
    videoid, user_id = callback_request.split("|")
    buttons = download_markup(videoid, user_id)
    await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# callback memek
    
@app.on_callback_query(filters.regex("memekpantek"))
async def memekpantek(_, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    user_name = CallbackQuery.from_user.first_name
    await CallbackQuery.edit_message_text(
f"""❓ **Panduan Dasar untuk menggunakan bot ini:**
1.) Pertama, tambahkan saya ke grup Anda.
2.) Kemudian, promosikan saya sebagai administrator dan berikan semua izin kecuali Admin Anonim.
3.) Setelah mempromosikan saya, ketik /reload di grup anda.
4.) Terkadang, memuat ulang bot dengan menggunakan perintah /reload dapat membantu Anda memperbaiki beberapa masalah.
5.) Nyalakan obrolan video terlebih dahulu sebelum mulai memutar musik.
6.) Userbot/Asisten akan auto join ke grup anda saat play musik.
💡 Jika Anda memiliki pertanyaan lanjutan tentang bot ini, Anda dapat menceritakannya di group support: @Kekiniangroup
""",
       reply_markup=InlineKeyboardMarkup(
             [
                [
                    InlineKeyboardButton("🔙 Home", callback_data="kontolanjing")
                ]
             ]
          ),
       )

@app.on_callback_query(filters.regex("kontolanjing"))
async def kontolanjing(_, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    user_name = CallbackQuery.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    await CallbackQuery.edit_message_text(f"""
**👋 Hello {rpk} !
✪ ᴍʏ ɴᴀᴍᴇ ɪs ᴍᴜꜱɪᴄ ᴋᴇᴋɪɴɪᴀɴ [🤖](https://telegra.ph/file/ee46c0aba5c12e0d2bb71.jpg)
✪ ɪ'ᴍ ᴀ ᴋᴇᴋɪɴɪᴀɴ ᴛʜᴇᴍᴇ ʙᴏᴛ ᴀ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ & ᴠɪᴅᴇᴏ sᴛʀᴇᴀᴍɪɴɢ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴜsᴇꜰᴜʟ ꜰᴇᴀᴛᴜʀᴇs!
✪ ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ [ᴢᴀʟ](https://t.me/rumahakhirat)
───────────────────────
✪ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ : /
───────────────────────
✪ Pᴏᴡᴇʀᴇᴅ 🔰 Bʏ: ᴍᴜꜱɪᴄ ᴋᴇᴋɪɴɪᴀɴ!**
""",
       reply_markup=InlineKeyboardMarkup(
           [
              [
                  InlineKeyboardButton(
                     "➕ ᴀᴅᴅ ᴍᴇ ʏᴏᴜʀ ᴛᴏ ɢʀᴏᴜᴘ​ ➕", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
              ],
              [
                  InlineKeyboardButton("❓ʙᴀsɪᴄ ", callback_data="memekpantek"),
              ],
              [
                  InlineKeyboardButton("ᴄᴏᴍᴍᴀɴᴅ📚", callback_data="cbcmds"),
              ],
              [
                  InlineKeyboardButton("📡 ᴏꜰꜰɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟ ", url=f"https://t.me/musickekiniaan"),
                  InlineKeyboardButton(" sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ 📨", url=f"https://t.me/Kekiniangroup"),
              ],
              [
                  InlineKeyboardButton("👑 ᴏᴡɴᴇʀ 👑", url="https://t.me/rumahakhirat")
              ],   
          ]
      ),
  )
    
    
# callback cbcmds

@app.on_callback_query(filters.regex("cbcmds"))
async def cbcmds(_, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    user_name = CallbackQuery.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    await CallbackQuery.edit_message_text(
        f"""✨ **Hello {rpk} !**
» **Tekan tombol di bawah ini untuk membaca penjelasan dan melihat daftar perintah yang tersedia !**
⚡ __Powered by {MUSIC_BOT_NAME}__""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("👷🏻 ᴀᴅᴍɪɴ ᴄᴍᴅ", callback_data="cbadmin"),
                    InlineKeyboardButton("🧙🏻 sᴜᴅᴏ ᴄᴍᴅ", callback_data="cbsudo"),
                ],[
                    InlineKeyboardButton("📚 ʙᴀsɪᴄ ᴄᴍᴅ", callback_data="cbbasic")
                ],[
                    InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="kontolanjing")
                ],
            ]
        ),
    )
        
    
@app.on_callback_query(filters.regex("cbbasic"))
async def cbbasic(_, CallbackQuery):
    await CallbackQuery.edit_message_text(
        f"""🏮 here is the basic commands:
» /play (Judul/link) - untuk memutar lagu/video yang di inginkan
» /queue - untuk melihat daftar putar lagu
» /song (query) - untuk mendownload lagu/video youtube
» /ping - show the bot ping status
» /bug - untuk melaporkan masalah pada bot
» /settings - untuk mengatur volume
⚡️ __Powered by {MUSIC_BOT_NAME}__""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="cbcmds")]]
        ),
    )
    
    
@app.on_callback_query(filters.regex("cbadmin"))
async def cbadmin(_, CallbackQuery):
    await CallbackQuery.edit_message_text(
        f"""🏮 here is the admin commands:
» /pause - untuk menjeda pemutaran streaming
» /resume - untuk melanjutkan pemutaran streaming yang di jeda
» /skip - untuk memutar streaming berikutnya yang ada didalam antrian
» /end - untuk menghentikan pemutaran streaming
» /reload - memuat ulang bot dan data admid
» /music off - untuk mematikan bot Kekinian Music di dalam group
» /music on - untuk menyalakan bot Kekinian Music di dalam group
» /auth - authorized user untuk Menggunakan Command Admin Permission Bot Kekinian Music
» /unauth - unauthorizer user tidak dapat lagi Menggunakan Command Admin Permission
» /settings - untuk mengatur volume dan auththorized/unauthorized
⚡️ __Powered by {MUSIC_BOT_NAME}__""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="cbcmds")]]
        ),
    )
    
    
@app.on_callback_query(filters.regex("cbsudo"))
async def cbsudo(_, CallbackQuery):
    await CallbackQuery.edit_message_text(
        f"""🏮 here is the sudo commands:
» /restart - restart bot
» /reload - memperbarui bot dan daftar admin
» /speedtest - cek speedtest
» /gcast - broadcast obrolan di semua group obrolan music yang di sajikan
» /music on/off - menyalakan/mematikan Bot Kekinian Music di dalam group
» /auth - authorized user untuk Menggunakan Command Admin Permission Bot Kekinian Music
» /unauth - unauthorizer user tidak dapat lagi Menggunakan Command Admin Permission
» /settings - untuk mengatur volume dan auththorized/unauthorized
⚡ __Powered by {MUSIC_BOT_NAME}__""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="cbcmds")]]
        ),
    )  

    
# callback anjeng
   
@app.on_callback_query(filters.regex("anjeng"))
async def anjeng(_, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    user_name = CallbackQuery.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    await CallbackQuery.edit_message_text(
        f"""✨ **Hello {rpk} !**
» **Tekan tombol di bawah ini untuk membaca penjelasan dan melihat daftar perintah yang tersedia !**
⚡ __Powered by {MUSIC_BOT_NAME}__""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("👷🏻 ᴀᴅᴍɪɴ ᴄᴍᴅ", callback_data="ccadmin"),
                    InlineKeyboardButton("🧙🏻 sᴜᴅᴏ ᴄᴍᴅ", callback_data="ccsudo"),
                ],[
                    InlineKeyboardButton("📚 ʙᴀsɪᴄ ᴄᴍᴅ", callback_data="ccbasic")
                ],[
                    InlineKeyboardButton(" 🔙 ʙᴀᴄᴋ ", callback_data="tomi")
                ],
            ]
        ),
    )
    
    
@app.on_callback_query(filters.regex("ccbasic"))
async def ccbasic(_, CallbackQuery):
    await CallbackQuery.edit_message_text(
        f"""🏮 here is the basic commands:
» /play (Judul/link) - untuk memutar lagu/video yang di inginkan
» /queue - untuk melihat daftar putar streaming
» /song (query) - untuk mendownload lagu/video youtube
» /ping - show the bot ping status
» /bug - untuk melaporkan masalah pada bot
» /settings - mengatur volume
⚡️ __Powered by {MUSIC_BOT_NAME}__""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="anjeng")]]
        ),
    )
    
    
@app.on_callback_query(filters.regex("ccadmin"))
async def ccadmin(_, CallbackQuery):
    await CallbackQuery.edit_message_text(
        f"""🏮 here is the admin commands:
» /pause - untuk menjeda pemutaran streaming
» /resume - untuk melanjutkan pemutaran streaming yang di jeda
» /skip - untuk memutar streaming berikutnya yang ada didalam antrian
» /end - untuk menghentikan pemutaran streaming
» /reload - memuat ulang bot dan data admid
» /music off - untuk mematikan bot Kekinian Music di dalam group
» /music on - untuk menyalakan bot Kekinian Music di dalam group
» /auth - authorized user untuk Menggunakan Command Admin Permission Bot Kekinian Music
» /unauth - unauthorizer user tidak dapat lagi Menggunakan Command Admin Permission
» /settings - untuk mengatur volume dan auththorized/unauthorized
⚡️ __Powered by {MUSIC_BOT_NAME}__""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="anjeng")]]
        ),
    )
    
    
@app.on_callback_query(filters.regex("ccsudo"))
async def ccsudo(_, CallbackQuery):
    await CallbackQuery.edit_message_text(
        f"""🏮 here is the sudo commands:
» /restart - restart bot
» /reload - memperbarui bot dan daftar admin
» /speedtest - cek speedtest
» /gcast - broadcast obrolan di semua group obrolan music yang di sajikan
» /music on/off - menyalakan/mematikan Bot Kekinian Music di dalam group
» /auth - authorized user untuk Menggunakan Command Admin Permission Bot Kekinian Music
» /unauth - unauthorizer user tidak dapat lagi Menggunakan Command Admin Permission
» /settings - untuk mengatur volume dan auththorized/unauthorized
⚡ __Powered by {MUSIC_BOT_NAME}__""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="anjeng")]]
        ),
    )  
    
    

@app.on_callback_query(filters.regex("tomi"))
async def cuseradd(_, CallbackQuery):
    out = start_pannel()
    await CallbackQuery.edit_message_text(f"**Thanks for having me in {CallbackQuery.message.chat.title}**.\n\n{MUSIC_BOT_NAME}✅\n\n**Untuk bantuan silahkan klik tombol COMMAND dibawah!**",
        reply_markup=InlineKeyboardMarkup(out[1]),
        disable_web_page_preview=True
    )
    
    
    
    
    
    
    
    
    
    
   
