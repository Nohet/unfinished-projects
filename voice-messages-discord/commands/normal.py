import asyncio
import datetime
import os
import random
import sys
import time

import humanize
from discord.ext import commands
from discord import Embed, Member

import discord

from bot import start_time

from gtts import gTTS

import aiosqlite


async def is_table_exists():
    con = await aiosqlite.connect("database.db")
    c = await con.cursor()

    await c.execute("CREATE TABLE IF NOT EXISTS voice_messages(id integer, author integer, member integer)")

    await con.commit()
    await con.close()


class NormalCommandsCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        loop = asyncio.get_event_loop()
        loop.run_until_complete(is_table_exists())

    @commands.command()
    async def info(self, ctx: commands.Context):
        current_time = time.time()
        _cache = []

        difference = int(round(current_time - start_time))
        text = humanize.precisedelta(datetime.timedelta(seconds=difference))

        for mesg in os.listdir("./voice_messages"):
            _cache.append(mesg)

        embed = Embed(
            colour=ctx.author.color
        )
        embed.set_author(name="Informations")
        embed.add_field(name="Python version", value=sys.version[:5], inline=False)
        embed.add_field(name="Discord.py version", value=discord.__version__, inline=False)
        embed.add_field(name="Uptime", value=text, inline=False)
        embed.add_field(name="Created voice messages", value=len(_cache), inline=False)
        embed.set_footer(text=f"{ctx.author.name} | {ctx.author.id}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def message(self, ctx: commands.Context):
        embed = Embed(
            colour=ctx.author.color
        )
        embed.add_field(name="Voice messages", value=f"""Welcome {ctx.author.name}! \n
                                                            If you want to create voice message type
                                                            **$message create <użytkownik> <wiadomość>** \n
                                                            Or else if you want to listen to voice message type
                                                            **$message open <id>**""")
        embed.set_footer(text=f"{ctx.author.name} | {ctx.author.id}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @message.command()
    async def create(self, ctx: commands.Context, member: Member, *, message: str):
        voice_message_id = random.randint(1, 999999)
        voice_message = gTTS(text=f"Voice message with id {voice_message_id}. " + message, lang="en", slow=False)

        voice_message.save(f"./voice_messages/{voice_message_id}.mp3")

        con = await aiosqlite.connect("database.db")
        c = await con.cursor()

        await c.execute("INSERT INTO voice_messages VALUES(?, ?, ?)",
                        (voice_message_id, ctx.author.id, member.id))

        await con.commit()
        await con.close()

        embed = Embed(
            colour=ctx.author.color
        )
        embed.add_field(name="Success", value=f"""Successfully created voice message for **{member.name}**
                                                Message id is **{voice_message_id}**
                                                This message will be deleted in **5** seconds!""")
        embed.set_footer(text=f"{ctx.author.name} | {ctx.author.id}", icon_url=ctx.author.avatar.url)
        member_embed = Embed(
            colour=ctx.author.color
        )
        member_embed.add_field(name="New voice message", value=f"""Member **{ctx.message.author.name}** created voice message for you
                                                                        to listen to it type **$message open {voice_message_id}**""")
        serv_mesg = await ctx.send(embed=embed)
        try:
            await member.send(embed=member_embed)

        except Exception as e:
            print(e)
            await ctx.send("Cannot send private message to this member!")

        await asyncio.sleep(5)

        await serv_mesg.delete()
        await ctx.message.delete()

    @message.command()
    async def open(self, ctx: commands.Context, voice_message_id: str):
        _cache = []
        for file in os.listdir("./voice_messages"):
            if file[:-4] == voice_message_id:
                _cache.append(file)
                embed = Embed(
                    colour=ctx.author.color
                )

                con = await aiosqlite.connect("database.db")
                c = await con.cursor()

                query = await c.execute("SELECT * FROM voice_messages WHERE id = ?", (voice_message_id,))
                query = await query.fetchone()

                await con.commit()
                await con.close()

                if query[2] != ctx.author.id:
                    embed.add_field(name="Error", value="You cannot listen to voice message, that was not directed to you!")
                    await ctx.send(embed=embed)
                    return

                if ctx.author.voice.self_deaf or ctx.author.voice.deaf:
                    embed.add_field(name="Error", value="You cannot listen to voice message while deafened!")
                    await ctx.send(embed=embed)
                    return

                if ctx.author.voice:
                    channel = ctx.author.voice.channel
                    await channel.connect()
                else:
                    return

                voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
                audio_source = discord.FFmpegPCMAudio("./voice_messages/" + file)

                if not voice_client.is_playing():
                    voice_client.play(audio_source, after=None)
                    embed.add_field(name="Success", value=f"Voice message with id **{query[0]}** is being played!")
                    await ctx.send(embed=embed)
        if len(_cache) <= 0:
            embed = Embed(
                colour=ctx.author.color
            )
            embed.add_field(name="Error", value="Voice message with that id does not exists!")
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(NormalCommandsCog(client))
