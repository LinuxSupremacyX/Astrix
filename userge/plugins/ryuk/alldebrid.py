# AllDebrid API plugin By Ryuk

import os
import asyncio

import aiohttp
from userge import Message, userge
from userge.utils import post_to_telegraph as post_tgh

# Your Alldbrid App token
KEY = os.environ.get("DEBRID_TOKEN")


TEMPLATE = """
<b>Name</b>: <i>{name}</i>
Status: <i>{status}</i>
ID: {id}
Size: {size}
{uptobox}"""


# Get response from api and return json or the error
async def get_json(endpoint: str, query: dict):
    if not KEY:
        return "API key not found."
    api = "https://api.alldebrid.com/v4" + endpoint
    params = {"agent": "bot", "apikey": KEY, **query}
    async with aiohttp.ClientSession() as session:
        async with session.get(url=api, params=params) as ses:
            try:
                json = await ses.json()
                return json
            except Exception as e:
                return str(e)


# Unlock Links or magnets
@userge.on_cmd(
    "unrestrict",
    about={
        "header": "Unrestrict Links or Magnets on Alldebrid",
        "flags": "-save to save link in servers",
        "usage": "{tr}unrestrict [www.example.com] or [magnet]",
    },
)
async def debrid(message: Message):
    if not (link_ := message.filtered_input_str):
        return await message.reply("Give a magnet or link to unrestrict.", quote=True)
    for i in link_.split():
        link = i
        if link.startswith("http"):
            if "-save" not in message.flags:
                endpoint = "/link/unlock"
                query = {"link": link}
            else:
                endpoint = "/user/links/save"
                query = {"links[]": link}
        else:
            endpoint = "/magnet/upload"
            query = {"magnets[]": link}
        unrestrict = await get_json(endpoint=endpoint, query=query)
        if not isinstance(unrestrict, dict) or "error" in unrestrict:
            return await message.reply(unrestrict, quote=True)
        if "-save" in message.flags:
            await message.reply("Link Successfully Saved.", quote=True)
        else:
            if not link.startswith("http"):
                data = unrestrict["data"]["magnets"][0]
            else:
                data = unrestrict["data"]
            name_ = data.get("filename", data.get("name",""))
            id_ = data.get("id")
            size_ = round(int(data.get("size", data.get("filesize",0))) / 1000000)
            ready_ = data.get("ready", "True")
            ret_str = f"""Name: **{name_}**\nID: `{id_}`\nSize: **{size_} mb**\nReady: __{ready_}__"""
            await message.reply(ret_str, quote=True)


# Get Status via id or Last 5 torrents
@userge.on_cmd(
    "torrents",
    about={
        "header": "Get singla magnet info or last 5 magnet info using id",
        "flags": {"-s": "-s {id} for status", "-l": "limited number of results you want, defaults to 1"},
        "usage": "{tr}torrents\n{tr}torrents -s 12345\n{tr}torrents -l 10",
    },
)
async def torrents(message: Message):
    endpoint = "/magnet/status"
    query = {}

    if "-s" in message.flags and "-l" in message.flags:
        return await message.reply("can't use two flags at once", quote=True)

    if "-s" in message.flags:
        if not (input_ := message.filtered_input_str):
            return await message.reply("ID required with -s flag", quote=True)

        query = {"id": input_}

    json = await get_json(endpoint=endpoint, query=query)
    if not isinstance(json, dict) or "error" in json:
        return await message.reply(json, quote=True)

    data = json["data"]["magnets"]
    if not isinstance(data, list):
        data = [data]

    ret_str_list = []
    limit = 1
    if "-l" in message.flags:
        limit = int(message.filtered_input_str)

    for i in data[0:limit]:
        status = i.get("status")
        name = i.get("filename")
        id = i.get("id")
        downloaded = ""
        uptobox = ""
        if status == "Downloading":
            downloaded = f"""<i>{round(int(i.get("downloaded",0))/1000000)}</i>/"""
        size = f"""{downloaded}<i>{round(int(i.get("size",0))/1000000)}</i> mb"""
        if link := i.get("links"):
            uptobox = "<i>UptoBox</i>: \n[ " + "\n".join([f"""<a href={z.get("link","")}>{z.get("filename","")}</a>""" for z in link]) + " ]"
        ret_str_list.append(ret_val := TEMPLATE.format(name=name, status=status, id=id, size=size, uptobox=uptobox))

    ret_str = "<br>".join(ret_str_list)
    if len(ret_str) < 4096:
        await message.reply(ret_str, quote=True)
    else:
        await message.reply(post_tgh("Magnets", ret_str.replace("\n","<br>")), disable_web_page_preview=True, quote=True)


# Delete a Magnet
@userge.on_cmd("del_t", about={"header": "Delete the previously unrestricted Torrent", "usage": "{tr}del_t 123456\n{tr}del_t 123456 78806"})
async def delete_torrent(message: Message):
    endpoint = "/magnet/delete"
    if not (id := message.filtered_input_str):
        return await message.reply("Enter an ID to delete")
    for i in id.split():
        json = await get_json(endpoint=endpoint, query={"id": i})
        await message.reply(str(json), quote=True)
