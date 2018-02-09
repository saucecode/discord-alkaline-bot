import discord

class ExamplePlugin:

	def __init__(self, client):
		self.client = client

		self.name = 'ExamplePlugin'
		self.version = '-0.01'
		self.author = 'Billy Maize'

	async def on_message(self, message):
		pass

	async def on_command(self, message, command, args):
		if command == 'test':
			await message.channel.send('I\'m trapped in a Google data center send help')

plugins = [ExamplePlugin]
commands = ['test']
