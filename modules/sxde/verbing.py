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
import discord, os, json

from modules.sxde.VerbGraph import VerbGraph

class Verbing(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.graph = VerbGraph()
		self.load_verb_graph()

		self.name = 'Verbing'
		self.version = '0.7'
		self.author = 'Julian'

	def load_verb_graph(self):
		if not os.path.exists('data/verbing.json'):
			self.save_verb_graph()

		with open('data/verbing.json', 'r') as f:
			self.graph.graph = json.load(f)

	def save_verb_graph(self):
		with open('data/verbing.json', 'w') as f:
			json.dump(self.graph.graph, f, indent=4, separators=(',', ': '))

	async def unverb(self, message : discord.Message, args : str):
		if not args.isdigit():
			await message.channel.send('Enter the ID of the action you\'re removing!')
			return
		if not str(message.author.id) in self.graph.graph:
			await message.channel.send('You\'re not in the graph.')
			return
		if not args in self.graph.graph[str(message.author.id)]:
			await message.channel.send('You\'re not performing the action: {}.'.format(self.graph.actions[int(args)]))
			return

		del self.graph.graph[str(message.author.id)][args]
		await message.channel.send('Done!')
		self.save_verb_graph()

	async def verb(self, message : discord.Message, args : str):
		if len(args) == 0:
			await message.channel.send('Available verbs: {}'.format( ', '.join( ['({}) {}'.format(k,v) for k,v in enumerate(self.graph.actions)] ) ))
			await message.channel.send('Available appendages: {}'.format( ', '.join( ['({}) {}'.format(k,v) for k,v in enumerate(self.graph.appendages)] ) ))
			await message.channel.send('Usage: `\\verb ' + commands['verb']['usage'] + '`')
			return

		if len(message.mentions) > 1:
			await message.channel.send('Multiple mentions detected?')
			return

		args = args.split(' ')
		if len(args) == 4:
			my_appendage = int(args[0])
			my_action = int(args[1])
			their_appendage = int(args[2])

			# use the mentioned character, or find by name
			if len(message.mentions) == 1:
				target = str(message.mentions[0].id)
			else:
				target = None
				member = discord.utils.get(message.guild.members, name=args[3])
				if member == None:
					await message.channel.send('Could not find a user with that name.')
					return
				target = str(member.id)

			self.graph.modify_node(str(message.author.id), my_appendage, my_action, their_appendage, target)

			self.save_verb_graph()
			await message.channel.send( self.graph.walk(str(message.author.id), depth=1) )

		elif len(args) == 1:
			target = None
			if args[0].lower() == 'me':
				target = str(message.author.id)
			else:
				if len(message.mentions) == 1:
					target = str(message.mentions[0].id)
				else:
					target = discord.utils.get(message.guild.members, name=args[0])
					if target:
						target = str(target.id)
					else:
						await message.channel.send('Could not find a user with that name.')
						return

			await message.channel.send( ', while '.join( self.graph.attach_names(self.graph.walk(target), message) ) )

	async def allverbs(self, message : discord.Message, args : str):
		target = None
		if args.lower() == 'me':
			target = str(message.author.id)
		else:
			if len(message.mentions) == 1:
				target = str(message.mentions[0].id)
			else:
				target = discord.utils.get(message.guild.members, name=args)
				if target:
					target = str(target.id)
				else:
					await message.channel.send('Could not find a user with that name.')
					return

		if not target in self.graph.graph:
			await message.channel.send( 'User not in graph.' )
			return

		strings = self.graph.attach_names(self.graph.all_actions(target), message)
		await message.channel.send('\n'.join(strings))


plugins = [Verbing]
commands = {
	'verb': {
		'usage':'[your appendage] [verb ID] [user\'s appendage ID] @user',
		'desc': 'Prints out a message.',
		'function': Verbing.verb
	},
	'unverb': {
		'function': Verbing.unverb
	},
	'allverbs':{
		'function': Verbing.allverbs
	}
}
