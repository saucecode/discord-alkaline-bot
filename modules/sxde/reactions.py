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
from ..alkalineplugin import AlkalinePlugin
import discord, os, json, random

class Reactions(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.BACKUP_FILES = ['data/reactions.json']
		
		self.existing_commands = []

		self.reactions = {}
		self.load_reactions()

		self.name = 'Reactions'
		self.version = '0.1'
		self.author = 'Julian'

	def load_reactions(self):
		if not os.path.exists('data/reactions.json'):
			self.save_reactions()

		with open('data/reactions.json', 'r') as f:
			self.reactions = json.load(f)

	def save_reactions(self):
		with open('data/reactions.json', 'w') as f:
			json.dump(self.reactions, f, indent=4, separators=(',', ': '))

	async def on_message(self, message):
		# regular reaction usage
		if message.content[0] == self.client.COMMAND_PREFIX:
			if message.content[:2] == self.client.COMMAND_PREFIX * 2 and len(message.content) > 2:
				reaction_name = message.content[2:]
				if reaction_name in self.reactions and len(self.reactions[reaction_name]) > 0:
					idx = random.randint(0, len(self.reactions[reaction_name]) - 1)
					await message.channel.send('{} {}'.format(idx, self.reactions[reaction_name][idx]))
					
			elif len(message.content) > 2: # Yell at the user for using only backslash when trying to trigger a reaction.
				
				# quickly generates a list of all the valid commands
				if len(self.existing_commands) == 0:
					self.existing_commands = [cmd for plugin in self.client.plugins for cmd in plugin.commands]
				
				reaction_name = message.content[1:]
				
				# do NOT yell at the use if they might be using a real command
				if reaction_name in self.reactions and reaction_name not in self.existing_commands:
					await message.channel.send('It\'s two backslashes you fucking moron.')

	async def on_command(self, message, command, args):
		if command == 'reactionadd':
			if len(args.split(' ')) < 2:
				await message.channel.send('Invalid syntax. Usage: %s%s' % (self.client.COMMAND_PREFIX, commands[command]['usage']))

			reaction_name = args.split(' ')[0]
			reaction_data = args[len(reaction_name)+1:]

			if not reaction_name in self.reactions:
				self.reactions[reaction_name] = []

			self.reactions[reaction_name].append(reaction_data)

			for word in reaction_data.split(' '):
				if 'http' in word and 'puu.sh' in word:
					await message.channel.send('Hey <@{}>! puu.sh links expire after 2 weeks of no use. If you really want to keep this reaction, delete it with `{}reactiondel {} {}` and re-upload to <http://imgur.com>'.format(message.author.id, self.client.COMMAND_PREFIX, reaction_name, len(self.reactions[reaction_name]) - 1))

			self.save_reactions()

			await message.channel.send('Added reaction. %s now has %i reactions.' % (reaction_name, len(self.reactions[reaction_name])))

		elif command == 'reactions':
			await message.channel.send(', '.join( [ name for name in self.reactions if len(self.reactions[name]) > 0 ] ))

		elif command == 'reactiondel':
			if not len(args.split(' ')) == 2:
				await message.channel.send('Usage: `{}{} {}`'.format(self.client.COMMAND_PREFIX, command, args))

			name = args.split(' ')[0]

			try:
				num = int(args.split(' ')[1])
			except ValueError:
				await message.channel.send('Usage: `{}{} {} [index]`'.format(self.client.COMMAND_PREFIX, command, args))
				return

			if not name in self.reactions or len(self.reactions[name]) == 0:
				await message.channel.send('Could not find a reaction with that name.')
				return

			r = self.reactions[name].pop(num)
			self.save_reactions()
			await message.channel.send('Popped reaction: `{}`'.format(r))

plugins = [Reactions]
commands = {
	'reactionadd': {
		'usage': '[reaction name] [reaction]',
		'desc':  'Saves the text or link [reaction] under [reaction name]'
	},
	'reactions':{
		'desc': 'List all reactions.'
	},
	'reactiondel':{
		'usage': '[reaction name] [index]',
		'desc': 'Deletes the specified reaction by index.'
	}
}
