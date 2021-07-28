# made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)

import os

from userge import Message, userge


@userge.on_cmd(
    "alb",
    about={
        "header": "Audio name editor",
        "description": "Change audio name, singer name, album art.",
        "flags": {
            "-t": "title",
        },
        "usage": "{tr}alb [title and/or album art file location]\n",
    },
)
async def album_edt(message: Message):
    """Audio name editor"""
    reply_ = message.reply_to_message
    if not reply_ or not reply_.audio:
        await message.edit("Reply to an audio file...")
        return
    chat_ = message.chat.id
    file_ = await userge.download_media(reply_)
    flag_ = message.flags
    input_ = message.filtered_input_str
    if not input_:
        await message.err("No input found...", del_in=5)
        return
    if "-t" in flag_:
        title = input_
        try:
            await userge.send_audio(chat_, file_, title=title)
        except BaseException:
            await message.err(f"Something unexpected happened, try again...", del_in=5)
        return
    if ";" in input_:
        split_input_ = input_.split(";")
        if len(split_input_) > 2:
            await message.edit("Please give no more than two inputs...", del_in=5)
            return
        for single_input_ in split_input_:
            if "/" in single_input_:
                album_art = single_input_
            else:
                performer = single_input_
        try:
            await userge.send_audio(chat_, file_, thumb=album_art, performer=performer)
        except BaseException:
            await message.err(
                f"Album art file location <code>{album_art}</code> might be invalid, check again...",
                del_in=5,
            )
        await message.delete()
        os.remove(file_)
        return
    if "/" in input_:
        album_art = input_
        try:
            await userge.send_audio(chat_, file_, thumb=album_art)
        except BaseException:
            await message.err(
                f"Album art file location <code>{album_art}</code> might be invalid, check again...",
                del_in=5,
            )
    else:
        performer = input_
        try:
            await userge.send_audio(chat_, file_, performer=performer)
        except BaseException:
            await message.err(
                "Something unexpected happened, try again...",
                del_in=5,
            )
    await message.delete()
    os.remove(file_)