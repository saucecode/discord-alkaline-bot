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
import discord, json, requests

class Latex(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		with open('data/template.tex','r') as f:
			self.template = f.read()

		self.name = 'LaTeX Render'
		self.version = '0'
		self.author = 'Julian'

	async def on_command(self, message: discord.Message, command : str, args : str):
		if command == 'tex' and len(args) > 0:
			# strip backticks
			if args[0] == '`' and args[-1] == '`':
				args = args[1:-1]

			req = {'code': self.template.replace('#CONTENT', args), 'format':'png'}
			resp = requests.post('http://rtex.probablyaweb.site/api/v2', json=req).json()
			if resp['status'] == 'success':
				imgurl = 'http://rtex.probablyaweb.site/api/v2/%s' % resp['filename']
				image = requests.get(imgurl).content
				await message.channel.send(file=discord.File(image, filename=resp['filename'] ))
			else:
				await message.channel.send( 'Render failed.' )

plugins = [Latex]
commands = {
	'tex': {
		'usage':'',
		'desc': 'Prints out a message.'
	}
}
