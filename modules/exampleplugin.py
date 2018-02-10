import discord

class ExamplePlugin:

	def __init__(self, client):
		self.client = client

		self.name = 'ExamplePlugin'
		self.version = '-0.01'
		self.author = 'Billy Maize'

	async def on_message(self, message : discord.Message):
		pass

	async def on_command(self, message: discord.Message, command : str, args : str):
		if command == 'test':
			await message.channel.send('I\'m trapped in a Google data center send help')

		elif command == 'square':
			try:
				val = int(args)
				await message.channel.send('%i^2 = %i' % ( val, val*val ))
			except ValueError:
				await message.channel.send('Number must be an integer.')

plugins = [ExamplePlugin]
commands = {
	'test': {
		'usage':'',
		'desc': 'Prints out a message.'
	},
	'square': {
		'usage': '[number]',
		'desc':  'Prints out [number] squared.',
		'example': '4'
	}
}
