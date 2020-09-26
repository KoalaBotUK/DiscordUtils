import discord
import asyncio
from discord.ext import commands

__all__ = ["AutoEmbedPaginator", "CustomEmbedPaginator"]

class AutoEmbedPaginator(object):
    def __init__(self, ctx, **kwargs):
        self.embeds = None
        self.ctx = ctx
        self.bot = ctx.bot
        self.current_page = 0
        self.auto_footer = kwargs.get("auto_footer", False)
        self.remove_reactions = kwargs.get("remove_reactions", True)
        self.control_emojis = ('⏮️', '⏪', '🔐', '⏩', '⏭️')
        self.timeout = int(kwargs.get("timeout", 60))
    async def run(self, embeds):
        if not self.embeds:
            self.embeds = embeds
        if self.auto_footer:
            self.embeds[0].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
        msg = await self.ctx.send(embed=self.embeds[0])
        for emoji in self.control_emojis:
            await msg.add_reaction(emoji)
        msg = await msg.channel.fetch_message(msg.id)
        def check(reaction, user):
            return user == self.ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in self.control_emojis
        while True:
            if self.timeout > 0:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add",check=check, timeout=self.timeout)
                except asyncio.TimeoutError:
                    self.current_page = 0
                    for reaction in msg.reactions:
                        if reaction.message.author.id == self.bot.user.id:
                            await msg.remove_reaction(str(reaction.emoji), reaction.message.author)
                    return
                    break
            else:
                reaction, user = await self.bot.wait_for("reaction_add",check=check)
            if str(reaction.emoji) == self.control_emojis[0]:
                self.current_page = 0
                if self.remove_reactions:
                    await msg.remove_reaction(str(reaction.emoji), user)
                if self.auto_footer:
                    self.embeds[0].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
                await msg.edit(embed=self.embeds[0])
            elif str(reaction.emoji) == self.control_emojis[1]:
                self.current_page = self.current_page-1
                self.current_page = 0 if self.current_page<0 else self.current_page
                if self.remove_reactions:
                    await msg.remove_reaction(str(reaction.emoji), user)
                if self.auto_footer:
                    self.embeds[self.current_page].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
                await msg.edit(embed=self.embeds[self.current_page])
            elif str(reaction.emoji) == self.control_emojis[2]:
                self.current_page = 0
                for reaction in msg.reactions:
                    if reaction.message.author.id == self.bot.user.id:
                        await msg.remove_reaction(str(reaction.emoji), reaction.message.author)
                return
                break
            elif str(reaction.emoji) == self.control_emojis[3]:
                self.current_page = self.current_page + 1
                self.current_page = len(self.embeds)-1 if self.current_page > len(self.embeds)-1 else self.current_page
                if self.remove_reactions:
                    await msg.remove_reaction(str(reaction.emoji), user)
                if self.auto_footer:
                    self.embeds[self.current_page].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
                await msg.edit(embed=self.embeds[self.current_page])
            elif str(reaction.emoji) == self.control_emojis[4]:
                self.current_page = len(self.embeds)-1
                if self.remove_reactions:
                    await msg.remove_reaction(str(reaction.emoji), user)
                if self.auto_footer:
                    self.embeds[len(self.embeds)-1].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
                await msg.edit(embed=self.embeds[len(self.embeds)-1])
                
class CustomEmbedPaginator(object):
    def __init__(self, ctx, **kwargs):
        self.embeds = None
        self.ctx = ctx
        self.bot = ctx.bot
        self.timeout = int(kwargs.get("timeout",60))
        self.current_page = 0
        self.control_emojis = []
        self.control_commands = []
        self.auto_footer = kwargs.get("auto_footer", False)
        self.remove_reactions = kwargs.get("remove_reactions", False)
    def add_reaction(self, emoji, command):
        self.control_emojis.append(emoji)
        self.control_commands.append(command)
    def insert_reaction(self, index, emoji, command):
        self.control_emojis.insert(index, emoji)
        self.control_commands.insert(index, command)
    def remove_reaction(self, emoji):
        if emoji in self.control_emojis:
            index = self.control_emojis.index(emoji)
            self.control_emojis.remove(emoji)
            self.control_commands.pop(index)
    def remove_reaction_at(self, index):
        if index > len(self.control_emojis)-1:
            index = len(self.control_emojis)-1
        elif index < 0:
            index = 0
        try:
            self.control_emojis.pop(index)
            self.control_commands.pop(index)
        except:
            pass
    def clear_reactions(self):
        self.control_emojis = []
        self.control_commands = []
    async def run(self, embeds):
        self.update_called = False
        self.embeds = embeds
        if self.auto_footer:
            self.embeds[0].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
        msg = await self.ctx.send(embed=self.embeds[0])
        for emoji in self.control_emojis:
            await msg.add_reaction(emoji)
        msg = await msg.channel.fetch_message(msg.id)
        def check(reaction, user):
            return user == self.ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in self.control_emojis
        while True:
            if self.timeout > 0:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add",check=check, timeout=self.timeout)
                except asyncio.TimeoutError:
                    for reaction in msg.reactions:
                        if reaction.message.author.id == self.bot.user.id:
                            await msg.remove_reaction(str(reaction.emoji), reaction.message.author)
                    self.current_page = 0
                    return
                    break
            else:
                reaction, user = await self.bot.wait_for("reaction_add",check=check)
            for emoji in self.control_emojis:
                if emoji == str(reaction.emoji):
                    index = self.control_emojis.index(emoji)
                    cmd = self.control_commands[index]
                    if cmd.lower() == "first":
                        self.current_page = 0
                        if self.remove_reactions:
                            await msg.remove_reaction(str(reaction.emoji), user)
                        if self.auto_footer:
                            self.embeds[0].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
                        await msg.edit(embed=self.embeds[0])
                    elif cmd.lower() == "last":
                        self.current_page = len(self.embeds)-1
                        if self.remove_reactions:
                            await msg.remove_reaction(str(reaction.emoji), user)
                        if self.auto_footer:
                            self.embeds[len(self.embeds)-1].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
                        await msg.edit(embed=self.embeds[len(self.embeds)-1])
                    elif cmd.lower() == "next":
                        self.current_page += 1
                        self.current_page = len(self.embeds)-1 if self.current_page > len(self.embeds)-1 else self.current_page
                        if self.remove_reactions:
                            await msg.remove_reaction(str(reaction.emoji), user)
                        if self.auto_footer:
                            self.embeds[self.current_page].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
                        await msg.edit(embed=self.embeds[self.current_page])
                    elif cmd.lower() == "back":
                        self.current_page = self.current_page-1
                        self.current_page = 0 if self.current_page<0 else self.current_page
                        if self.remove_reactions:
                            await msg.remove_reaction(str(reaction.emoji), user)
                        if self.auto_footer:
                            self.embeds[self.current_page].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
                        await msg.edit(embed=self.embeds[self.current_page])
                    elif cmd.lower() == "delete":
                        self.current_page = 0
                        await msg.delete()
                        return
                        break
                    elif cmd.lower() == "clear" or cmd.lower() == "lock":
                        self.current_page = 0
                        for reaction in msg.reactions:
                            if reaction.message.author.id == self.bot.user.id:
                                await msg.remove_reaction(str(reaction.emoji), reaction.message.author)
                        return
                        break
                    elif cmd.startswith("page"):
                        shit = cmd.split()
                        pg = int(shit[1])
                        self.current_page = pg
                        if pg > len(embeds)-1:
                            pg = len(embeds)-1
                        if pg < 0:
                            pg = 0
                        if self.remove_reactions:
                            await msg.remove_reaction(str(reaction.emoji), user)
                        if self.auto_footer:
                            self.embeds[self.current_page].set_footer(text=f'({pg+1}/{len(self.embeds)})')
                        await msg.edit(embed=self.embeds[pg])
                    elif cmd.startswith("remove"):
                        things = cmd.split()
                        things.pop(0)
                        something = things[0]
                        if something.isdigit():
                            index = int(something)
                            index = len(self.control_emojis)-1 if index > len(self.control_emojis)-1 else index
                            index = 0 if index < 0 else index
                            emoji = self.control_emojis[index]
                            if self.remove_reactions:
                                await msg.remove_reaction(str(reaction.emoji), user)
                            await msg.remove_reaction(emoji, self.bot.user)
                            self.control_emojis.pop(index)
                            self.control_commands.pop(index)
                        else:
                            emoji = something
                            if emoji in self.control_emojis:
                                if self.remove_reactions:
                                    await msg.remove_reaction(str(reaction.emoji), user)
                                await msg.remove_reaction(emoji, self.bot.user)
                                index = self.control_emojis.index(emoji)
                                self.control_emojis.remove(emoji)
                                self.control_commands.pop(index)