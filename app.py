from os import system
from colorama import Fore, init
from PIL import Image

import re, httpx, platform, time, asyncio, json, discord, multiprocessing, sys, pytesseract, io, os


"""
CHANGELOG:
    Added Close Option.
    Multi Token
"""

init()
with open('token.json', "r") as f:
    data = json.load(f)

main_token = data['main_token']
alts = data["alts_token"]

os_type = platform.system()

nitro = re.compile("(https://discord.gift/|discord.com/gifts/|discordapp.com/gifts/|discord.gift/|https://discord.com/gifts/|https://discordapp.com/gifts/|discordapp.com/gifts|https:/discord.com/gifts/)([a-zA-Z0-9]+)")
code_pattern = r'\b([a-zA-Z0-9]+)\b'
discord_server = re.compile("(https://discord.gg/|discord.gg/invite/|discord.gg/|https://discord.com|discord.com/invite/|discord.com/)([a-zA-Z0-9]+)")

img_formats = ["jpeg", "jpg", "png", "gif"]

if os_type == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR/tesseract.exe" # Remove This Line if you're 


def start(token, type):
    client = discord.Client()

    async def join(server):
        async with httpx.AsyncClient() as r:
            headers = {'authorization': token, "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
            req = await r.post(f"https://discordapp.com/api/invites/{server}", headers=headers)
            data = req.json()
            guild_id = data["guild"]["id"]
            g = await client.fetch_guild(guild_id)
            if len(g.members) < 500:
                await r.delete(f"https://discord.com/api/users/@me/guilds/{guild_id}")
                return


        if "guild" in data.keys():
            try:
                print("Joined New Server! | Name: {0} | Inviter: {1} | Total guilds: {2}".format(data["guild"]["name"], data["inviter"]["username"], len(client.guilds)))
            except:
                print("Joined New Server! | Name: {0} | Total guilds: {1}".format(data["guild"]["name"], len(client.guilds)))


    async def claim(ctx, code, start_time, type):
        async with httpx.AsyncClient() as r:
            req = await r.post(
                'https://discordapp.com/api/v6/entitlements/gift-codes/' + code + '/redeem',
                json={'channel_id': str(ctx.channel.id)},
                headers={'authorization': main_token,
                         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'})
            delay = (time.time() - start_time)

        if 'nitro' in str(req.content):
            return f"FOUND {type}- You got nitro boi! Code: {code} | Delay: {delay}, | Server: {ctx.guild}"

        else:
            return f"FOUND {type}- Invalid nitro nor this nitro has already been claimed! Code: {code} | Delay: {delay} | Server: {ctx.guild}"


    async def get_code(url):
        async with httpx.AsyncClient() as r:
            req = await r.get(url)
            img = Image.open(io.BytesIO(req.content))
        text = pytesseract.image_to_string(img)
        return text


    @client.event
    async def on_ready():
        print(f"{type}: Logged in as- {client.user.name} | Guilds: {len(client.guilds)}")


    @client.event
    async def on_message(ctx):
        try:
            messages = [message for message in ctx.clean_content.split("\n")]
            for message in messages:
                code = nitro.search(message)
                if code is not None:
                    code = code.group(2)
                    if len(code) >=16 and len(code) <= 19:
                        start_time = time.time()
                        result = await claim(ctx, code, start_time, "Message")
                        print(result)

                else:
                    mess = re.sub('[\W_]+', ' ', message)
                    mess = re.findall(code_pattern, mess)
                    for m in mess:
                        if any(i.isdigit() for i in m) is True and (any(i.isalpha() for i in m) is True):
                            if len(m) >=16 and len(m) <= 19:
                                start_time = time.time()
                                result = await claim(ctx, m, start_time, "Message")
                                print(result)

            message = ctx.content
            if '**giveaway**' in message.lower():
                try:
                    await asyncio.sleep(30)
                    await ctx.add_reaction("🎉")
                    print("joined giveaway", ctx.guild.name, client.user.name)
                except Exception as e:
                    print(e)

            elif f"<@{client.user.id}>" in message.lower() and (
                    "giveaway" in message.lower() or "won" in message.lower() or "winner" in message.lower()):
                print("You won the giveaway", ctx.guild.name, client.user.name)

            else:
                if type == "Alt":
                    server = discord_server.search(message)
                    if server is not None:
                        server = server.group(2)
                        await join(server)

            for attachment in ctx.attachments:
                if any(img in str(attachment) for img in img_formats):
                    start_time = time.time()
                    text = await get_code(str(attachment))
                    code = nitro.search(text)
                    if code is not None:
                        code = code.group(2)
                        if len(code) >= 16 and len(code) <= 19:
                            result = await claim(ctx, code, start_time, "Attachment")
                            print(result)
        except Exception as e:
            print(e)

    client.run(token, bot=False)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    print("Made By: Reven8e.sh#9290")
    processes = []

    main = multiprocessing.Process(target=start, args=(main_token, "Main",))
    main.start()
    processes.append(main)

    for alt in alts:
        p = multiprocessing.Process(target=start, args=(alt, "Alt",))
        processes.append(p)
        p.start()