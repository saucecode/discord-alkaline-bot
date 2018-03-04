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
import discord, random, asyncio

class RawrPlugin(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.dad_feature = True

		self.name = 'RawrPlugin'
		self.version = '1.0'
		self.author = 'Julian'

	async def on_message(self, message : discord.Message):
		if self.dad_feature and random.random() > 0.7:
			if 5 < len(message.content) < 100 and message.content[0] in ('I', 'i'):
				if message.content.lower().split(' ')[0] in ['i\'m', 'im']:
					whoIsHe = ''
					if '.' in message.content:
						whoIsHe = ' '.join(message.content.split('.')[0].split(' ')[1:])
					else:
						whoIsHe = ' '.join(message.content.split(' ')[1:])

					if random.random() > 0.8:
						await asyncio.sleep(3.0)

					await message.channel.send("Hi %s! I'm Dad!" % (whoIsHe,))

	async def on_command(self, message: discord.Message, command : str, args : str):
		pass

plugins = [RawrPlugin]
commands = {}
