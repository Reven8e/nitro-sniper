from os import system
from discord.ext import commands
from colorama import Fore, init

import re, httpx, platform, traceback, time, asyncio, json, cython

init()


with open('token.json', "r") as f:
    data = json.load(f)
    
token = data['main_token']

os_type = platform.system()

client = commands.Bot(command_prefix=".", self_bot=True)

reg = re.compile("(discord.com/gifts/|discordapp.com/gifts/|discord.gift/)([a-zA-Z0-9]+)")


async def claim(ctx, code, start_time):
    async with httpx.AsyncClient() as r:
        result = await r.post(
            'https://discordapp.com/api/v6/entitlements/gift-codes/' + code + '/redeem',
            json={'channel_id': str(ctx.channel.id)},
            headers={'authorization': token, 'user-agent': 'Mozilla/5.0'})
        delay = (time.time() - start_time)

    if 'nitro' in str(result.content):
        return f"You got nitro boi! Code: {code} | Delay: {delay}"
    
    else:
        return f"Invalid nitro nor this nitro has already been claimed! Code: {code} | Delay: {delay}"



def start():
    while True:
        try:
            @client.event
            async def on_message(ctx):
                message = reg.search(ctx.content)
                if message:
                    code = message.group(2)
                    print(code)

                    if len(code) >= 16:
                        start_time = time.time()
                        result = await claim(ctx, code, start_time)
                        print(result)


            client.run(token, bot=False)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    start()