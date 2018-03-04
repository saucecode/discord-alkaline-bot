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
import discord

def is_int(i):
	try:
		int(i)
		return True
	except:
		return False

class Helpful(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.name = 'HelpManager'
		self.version = '1.0'
		self.author = 'Julian'

	async def on_command(self, message: discord.Message, command : str, args : str):
		if command == 'help':
			output = []
			for mod in self.client.plugins:
				for command in mod.commands:
					output.append('{}{} {}'.format(self.client.COMMAND_PREFIX, command, mod.commands[command]['usage'] if 'usage' in mod.commands[command] else ''))
				output.append('')

			page = 0

			if len(args) > 0 and is_int(args):
				page = int(args)

			page_count = len(output)//20 + 1

			await message.channel.send('Commands (Page {} of {}):\n```\n{}\n```'.format(page, page_count, '\n'.join(output[page*20:page*20+20])))

plugins = [Helpful]
commands = {
	'help': {
		'usage': '[page number]',
		'desc': 'Displays the help menu, lists every command.'
	}
}
