import discord

class AlkalinePlugin:

	async def on_message(self, message : discord.Message):
		pass

	async def on_command(self, message : discord.Message, command : str, args : str):
		pass

	async def on_message_edit(self, before : discord.Message, after : discord.Message):
		pass

	async def on_reaction_add(self, reaction : discord.Reaction, user : discord.User):
		pass
