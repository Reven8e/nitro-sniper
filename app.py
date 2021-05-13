from os import system
from discord import message
from discord.ext import commands
from colorama import Fore, init

import re, httpx, platform, traceback, time, asyncio, json, cython, discord

"""
CHANGELOG:
    Fixed only listening to your messages.
    Method by me :)
"""


init()
with open('token.json', "r") as f:
    data = json.load(f)
    
token = data['main_token']

os_type = platform.system()

client = discord.Client()

reg = re.compile("(discord.com/gifts/|discordapp.com/gifts/|discord.gift/)([a-zA-Z0-9]+)")


async def claim(ctx, code, start_time):
    async with httpx.AsyncClient() as r:
        result = await r.post(
            'https://discordapp.com/api/v6/entitlements/gift-codes/' + code + '/redeem',
            json={'channel_id': str(ctx.channel.id)},
            headers={'authorization': token, 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'})
        delay = (time.time() - start_time)

    if 'nitro' in str(result.content):
        return f"You got nitro boi! Code: {code} | Delay: {delay}"
    
    else:
        return f"Invalid nitro nor this nitro has already been claimed! Code: {code} | Delay: {delay}"


async def get_content(message_channel):
    async with httpx.AsyncClient() as r:
        result = await r.get(
            f'https://discordapp.com/api/channels/{message_channel}/messages?limit=1',
            headers={'authorization': token, 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'})
        res = result.json()
        return res[0]["content"]


@client.event
async def on_ready():
    print("Ready! Starting to listen.")


@client.event
async def on_message(ctx):
    message = await get_content(ctx.channel.id)
    code = reg.search(message)
    if code is not None:
        code = code.group(2)
        if len(code) >= 16:
            start_time = time.time()
            result = await claim(ctx, code, start_time)
            print(result)

    elif '**giveaway**' in message.lower():
        try:
            await asyncio.sleep(30)
            await ctx.add_reaction("🎉")
            print("joined giveaway", ctx.guild.name)
        except Exception as e:
            print(e)
    
    elif f"<@!{client.user.id}>" in message and ("giveaway" in message.lower() or "won" in message.lower() or "winner" in message.lower()):
        print("You won the giveaway", ctx.guild.name)


if __name__ == "__main__":
    client.run(token, bot=False, reconnect=True)
