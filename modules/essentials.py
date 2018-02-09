import discord

from . import dictionarycom as dictionary

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
			await message.channel.send('Pong')

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

		if command == 'define':
			word = args.split(' ')[0]
			defs = dictionary.get_definitions(word)[:3]
			if len(defs) == 0:
				await message.channel.send('What even is a %s?' % word)
			else:
				i=1
				out = ''
				for s in defs:
					out += '%i. %s\n' % (i,s)
					i += 1
				await message.channel.send('```%s```' % (out,))

		if command == 'ud':
			word = args
			definition = dictionary.get_urban_definitions(word)[0]
			for i in range(len(definition['definition'])//2000 + 1):
				await message.channel.send('```%s```' % definition['definition'][i*2000:i*2000+2000])
			await message.channel.send('```examples: %s```' % definition['example'])

plugins = [Essentials]
commands = ['ping', 'whoami', 'whois', 'define', 'ud']
