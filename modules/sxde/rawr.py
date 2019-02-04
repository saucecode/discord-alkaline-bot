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
import discord, random, asyncio, re
from collections import defaultdict

class RawrPlugin(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.dad_feature = True
		self.hit_or_miss_feature = True # well, not really a feature. I guess.
		self.lol_feature = True

		self.name = 'RawrPlugin'
		self.version = '1.2'
		self.author = 'Julian'

		self.lol_history = defaultdict(lambda:['', ''])
		self.repeatable_phrases = ['lol', 'lmao', 'haha', 'sup', 'mew', 'gottem']

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


		if self.hit_or_miss_feature and len(message.content) >= len('hit or miss')-2 \
		   and 'miss' in message.content.lower():
			if self.actually_qualifies(message.content):
				if random.random() > 0.8:
					await message.channel.send('I guess they never miss, huh?')
				else:
					print('Could\'ve fired on "{}", but didn\'t'.format(message.content))


		if self.lol_feature and message.author.id != self.client.user.id:
			self.lol_history[message.channel.id].pop(0)
			self.lol_history[message.channel.id].append(message.content.lower())

			if self.lol_history[message.channel.id][0] == self.lol_history[message.channel.id][1] and self.lol_history[message.channel.id][0] in self.repeatable_phrases:
				await message.channel.send(message.content)


	# An algorithm to determine whether or not its actually appropriate to respond
	def actually_qualifies(self, s):
		s = s.lower()
		short_strings = ['miss', 'missed', 'missing', 'misses']

		if  ',' in s and all(short not in s.split(',')[0] for short in short_strings) \
		and len(s.split(',')[0]) > 3:
			s = s[s.index(',')+1:]
			return actually_qualifies(s)

		s = re.sub('[^0-9a-zA-Z\s]', '', s)
		words = [i for i in s.split(' ') if i]

		# Miss me? Miss the train?
		if words[0] in short_strings and len(words) < 12:
			return True

		# He missed you.
		if  words[1] in short_strings and words[0] in ['he', 'she', 'didnt', 'dont', 'you', 'we', 'i'] \
		and len(words) < 16:
		   return True

		# He is missing! Let him miss the bus
		if words[2] in short_strings and len(words) < 16:
			return True

		# good to watch if you missed it
		if  (words[-2] in short_strings or words[-1] in short_strings):
			return True

		return False

	async def on_command(self, message: discord.Message, command : str, args : str):
		pass


plugins = [RawrPlugin]
commands = {
}
