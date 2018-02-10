import discord

class Reactions:

	def __init__(self, client):
		self.client = client

		self.name = 'Reactions'
		self.version = '0.1'
		self.author = 'Julian'

	async def on_message(self, message):
		if message.content[:2] == self.client.COMMAND_PREFIX * 2:
			await message.channel.send('reaction detected: %s' % message.content[2:])

	async def on_command(self, message, command, args):
		if command == 'reactionadd':
			await message.channel.send('I\'m trapped in a Google data center send help')

plugins = [Reactions]
commands = {'reactionadd':{}}
