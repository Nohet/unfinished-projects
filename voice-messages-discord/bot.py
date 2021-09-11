import json
import os
import time
from itertools import cycle

import discord
from discord.ext import commands, tasks

with open("config.json") as f:
    bot_settings = json.load(f)

start_time = time.time()

intents = discord.Intents.all()

client = commands.Bot(command_prefix="$", intents=intents)
client.remove_command("help")


status = cycle(
    ["Voice messages", "Prefix: $"])


@client.event
async def on_ready():
    change_status.start()


@tasks.loop(seconds=5)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


for file in os.listdir("./commands"):
    if file.endswith(".py"):
        try:
            client.load_extension(f"commands.{file[:-3]}")
            print(f"Successfully loaded {file}")
        except Exception as e:
            print(e)
            continue

client.run(bot_settings["bot settings"]["token"])
