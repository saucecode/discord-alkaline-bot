from ..alkalineplugin import AlkalinePlugin
import discord, random, asyncio

class RawrPlugin(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.dad_feature = True

		self.name = 'RawrPlugin'
		self.version = '1.0'
		self.author = 'Julian'

	async def on_message(self, message : discord.Message):
		if self.dad_feature and random.random() > 0.7:
			if 5 < len(message.content) < 100 and message.content[0] in ('I', 'i'):
				if message.content.lower().split(' ')[0] in ['i\'m', 'im']:
					whoIsHe = ''
					if '.' in message.content:
						whoIsHe = ' '.join(message.content.split('.')[0].split(' ')[1:])
					else:
						whoIsHe = ' '.join(message.content.split(' ')[1:])

					if random.random() > 0.8:
						await asyncio.sleep(3.0)

					await message.channel.send("Hi %s! I'm Dad!" % (whoIsHe,))

	async def on_command(self, message: discord.Message, command : str, args : str):
		pass

plugins = [RawrPlugin]
commands = {}
