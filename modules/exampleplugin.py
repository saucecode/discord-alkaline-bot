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

class ExamplePlugin(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.name = 'ExamplePlugin'
		self.version = '-0.01'
		self.author = 'Billy Maize'

	async def test_command(self, message : discord.Message, args : str):
		await message.channel.send('I\'m trapped in a Google data center send help')

	async def square(self, message : discord.Message, args : str):
		try:
			val = int(args)
			await message.channel.send('%i^2 = %i' % ( val, val*val ))
		except ValueError:
			await message.channel.send('Number must be an integer.')

plugins = [ExamplePlugin]
commands = {
	'test': {
		'usage':'',
		'desc': 'Prints out a message.',
		'function': ExamplePlugin.test_command
	},
	'square': {
		'usage': '[number]',
		'desc':  'Prints out [number] squared.',
		'example': '4',
		'function': ExamplePlugin.square
	}
}
