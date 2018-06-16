"""
    Alkaline Bot - a modular Discord chat bot
    Copyright (C) 2018    Julian Cahill

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from .alkalineplugin import AlkalinePlugin
import discord, time, requests

from . import dictionarycom as dictionary
from .sailortalk import sailor_word
from . import postfix

def is_float(f):
	try:
		float(f)
		return True
	except:
		return False

class Essentials(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.name = 'Essentials'
		self.version = '0.1'
		self.author = 'Julian'

	async def on_command(self, message, command, args):
		if command == 'ping':
			await message.channel.send('Pong')


		elif command == 'whoami':
			user = message.author
			await message.channel.send('Name: %s; Display Name: %s; Discriminator: %s; ID: %i; Server ID: %i' % (user.name, user.display_name, user.discriminator, user.id, message.guild.id))


		elif command == 'whois':
			target = args
			user = discord.utils.find(lambda m: target.lower() in m.name.lower() or target.lower() in m.display_name.lower(), message.guild.members)
			if user:
				await message.channel.send('Name: %s; Display Name: %s; Discriminator: %s; ID: %i; Server ID: %i' % (user.name, user.display_name, user.discriminator, user.id, message.guild.id))
			else:
				await message.channel.send('Couldn\'t find that user.')


		elif command == 'whereami':
			await message.channel.send('Channel ID: %i' % message.channel.id)


		elif command == 'define':
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


		elif command == 'ud':
			word = args
			definition = dictionary.get_urban_definitions(word)[0]
			for i in range(len(definition['definition'])//2000 + 1):
				await message.channel.send('```%s```' % definition['definition'][i*2000:i*2000+2000])
			await message.channel.send('```examples: %s```' % definition['example'])


		elif command == 'filth':
			await message.channel.send(sailor_word())

		elif command == 'perms':
			await message.channel.send('You have permissions: `%s`' % ' '.join(self.client.get_members_permissions(message.author.id)))

		elif command == 'ctime':
			if args and is_float(args):
				await message.channel.send(time.ctime(float(args)))

		elif command == 'chavatar':
			if not args.startswith('http'): return
			avatar_url = args
			await self.client.user.edit(avatar=requests.get(avatar_url).content)


class EssentialsCalc(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.answer_message = None
		self.query_message = None

		self.name = 'Essentials-Calc'
		self.version = '0.1'
		self.author = 'Julian'

	async def on_message_edit(self, before, after):
		if not self.answer_message == None:
			if before.id == self.query_message.id:
				await self.answer_message.edit(content=postfix.outputResult( postfix.doPostfix(after.content[1 + 4 + len(self.client.COMMAND_PREFIX):].strip()) ))

	async def on_command(self, message, command, args):
		if command == 'calc':
			self.query_message = message
			self.answer_message = await message.channel.send( postfix.outputResult( postfix.doPostfix(message.content[1 + 4 + len(self.client.COMMAND_PREFIX):].strip()) ) )

plugins = [Essentials, EssentialsCalc]
commands = {
	'ping':{},
	'whoami':{},
	'whois':{},
	'define':{
		'usage': '[word]',
		'desc':  'Look up the definition of a word.'
	},
	'ud':{
		'usage': '[word or phrase]',
		'desc':  'Look up the definition of a word from urban dictionary.'
	},
	'whereami':{'perms':['op']},
	'filth':{
		'desc': 'Generate a random filthy/offensive word or phrase.'
	},
	'perms':{
		'desc': 'Prints your permissions.'
	},
	'ctime':{
		'desc': 'Converts unix epoch number to a human-readable time string.',
		'example': '1518765410.543'
	},
	'chavatar':{
		'desc': 'Changes the avatar of the bot to the image at url.',
		'usage': '[url]',
		'perms': ['op', 'admin']
	},

	'calc':{
		'usage': '[postfix expr]',
		'desc':  'Does a calculation.',
		'example': '3 3 * 4 4 * + sqrt',
	}
}
