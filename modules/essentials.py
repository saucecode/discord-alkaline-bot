import discord

class Essentials:

	def __init__(self, client):
		self.client = client

		self.name = 'Essentials'
		self.version = '1.0'
		self.author = 'Julian'

	async def on_message(self, message):
		pass

	async def on_command(self, message, command, args):
		if command == 'ping':
			await message.channel.send('Pingaz')

		if command == 'whoami':
			user = message.author
			await message.channel.send('Name: %s; Display Name: %s; Discriminator: %s; ID: %i; Server ID: %i' % (user.name, user.display_name, user.discriminator, user.id, message.guild.id))

		if command == 'whois':
			target = args
			user = discord.utils.find(lambda m: target.lower() in m.name.lower() or target.lower() in m.display_name.lower(), message.guild.members)
			if user:
				await message.channel.send('Name: %s; Display Name: %s; Discriminator: %s; ID: %i; Server ID: %i' % (user.name, user.display_name, user.discriminator, user.id, message.guild.id))
			else:
				await message.channel.send('Couldn\'t find that user.')

class Essential_Cats:

	def __init__(self, client):
		self.client = client

		self.name = 'Essential Cats'
		self.version = '1.0'
		self.author = 'Julian'

		self.commands = {}

	async def on_message(self, message):
		pass

	async def on_command(self, message, command, args):
		if command == 'cats':
			await message.channel.send('http://i.imgur.com/jg0bGqX.jpg')

plugins = [Essentials, Essential_Cats]
commands = ['ping', 'cats', 'whoami', 'whois']
