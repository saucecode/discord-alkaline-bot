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
import discord, time, requests, random, asyncio, re, sys, json, datetime

from . import dictionarycom as dictionary
from .sailortalk import sailor_word
from . import postfix

from concurrent.futures import ThreadPoolExecutor
from google_images_download import google_images_download

def is_float(f):
	try:
		float(f)
		return True
	except:
		return False

class Essentials(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.unauthorized_to_kill = [182411730435964928]
		self.executor = ThreadPoolExecutor(2)

		self.name = 'Essentials'
		self.version = '1.0'
		self.author = 'Julian'

	async def ping(self, message, args):
		await message.channel.send('Pong')

	async def flip(self, message, args):
		random_int = random.randint(0,1)
		if random_int == 0:
			await message.channel.send('Tails')
		else:
			await message.channel.send('Heads')

	async def whoami(self, message, args):
		user = message.author
		await message.channel.send('Name: %s; Display Name: %s; Discriminator: %s; ID: %i; Server ID: %i' % (user.name, user.display_name, user.discriminator, user.id, message.guild.id))

	async def whois(self, message, args):
		target = args
		user = discord.utils.find(lambda m: target.lower() in m.name.lower() or target.lower() in m.display_name.lower(), message.guild.members)
		if user:
			await message.channel.send('Name: %s; Display Name: %s; Discriminator: %s; ID: %i; Server ID: %i' % (user.name, user.display_name, user.discriminator, user.id, message.guild.id))
		else:
			await message.channel.send('Couldn\'t find that user.')

	async def whereami(self, message, args):
		await message.channel.send('Channel ID: %i' % message.channel.id)

	async def define(self, message, args):
		'''
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
		'''
		await message.channel.send('This command is not currently implemented.')

	async def urbandictionary(self, message, args):
		word = args
		definition = dictionary.get_urban_definitions(word)[0]
		for i in range(len(definition['definition'])//2000 + 1):
			await message.channel.send('```%s```' % definition['definition'][i*2000:i*2000+2000])
		await message.channel.send('```examples: %s```' % definition['example'])

	async def filth(self, message, args):
		await message.channel.send(sailor_word())

	async def get_perms(self, message, args):
		await message.channel.send('You have permissions: `%s`' % ' '.join(self.client.get_members_permissions(message.author.id)))

	async def get_ctime(self, message, args):
		if args and is_float(args):
			await message.channel.send(time.ctime(float(args)))

	async def chavatar(self, message, args):
		if not args.startswith('http'): return
		avatar_url = args
		await self.client.user.edit(avatar=requests.get(avatar_url).content)

	async def chnick(self, message, args):
		if not args or len(args) < 3: return
		await message.guild.get_member(self.client.user.id).edit(nick = args)

	def roll_dice_raw(self, args):
		if not re.match('^(\\d+)d(\\d+)$', args):
			return 'Please enter a D&D roll, like 1d6 or 2d20'

		count = int(args.split('d')[0])
		sides = int(args.split('d')[1])
		roll_result = [random.randint(1,sides) for i in range(count)]
		return roll_result

	async def roll_dice(self, message, args):
		result = self.roll_dice_raw(args)
		if type(result) == str:
			await message.channel.send(result)
			return
		
		await message.channel.send('{}: {}'.format(args, ', '.join([str(x) for x in result])))
	
	async def roll_dice_and_sum(self, message, args):
		result = self.roll_dice_raw(args)
		if type(result) == str:
			await message.channel.send(result)
			return
			
		await message.channel.send('{}: {}, sums to {}'.format(args, ', '.join([str(x) for x in result]), sum(result)))
	
	async def when_is_christmas(self, message, args):
		today = datetime.date.today()
		year = today.year
		christmas = datetime.date(year, 12, 25)
		delta = christmas - today
		if delta.days < 0:
			christmas = datetime.date(year+1, 12, 25)
			delta = christmas - today

		# Searches for a :christmas_tree: (number of days) :christmas_tree:
		# pattern in the channel topic and updates the number.
		original = message.channel.topic.encode()
		match = re.search(b'(\xf0\x9f\x8e\x84|:christmas_tree:) (\\d+) (\xf0\x9f\x8e\x84|:christmas_tree:)(.*)$', original)
		if match:
			new = list(match.groups())
			new[1] = str(delta.days).encode()
			new = b' '.join(new)
			await message.channel.edit(topic=new.decode())
		
		await message.channel.send('Christmas is in %i days!' % delta.days)

	async def kill_bot(self, message, args):
		if message.author.id not in self.unauthorized_to_kill:
			print('Killed by:', message.author.name)
			sys.exit(0)

	async def image_search(self, message, args):
		if not args:
			await message.channel.send('Please enter a query.')
			return

		args = re.sub('[^a-zA-Z0-9_ ]', '', args)

		response = google_images_download.googleimagesdownload()
		arguments = {"keywords":args,"limit":3,"print_urls":False, 'output_directory':'google_images'}
		results = await self.client.loop.run_in_executor(self.executor, response.download, arguments)
		paths = sorted(results[args])
		paths = [i for i in paths if i]
		with open(paths[0], 'rb') as f:
			await message.channel.send(content=None, file=discord.File(f, paths[0].split('/')[-1]))
		# await message.channel.send('```{}```'.format(json.dumps(paths, indent=4)))


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
				await self.answer_message.edit(content=postfix.quickly( after.content[1 + 4 + len(self.client.COMMAND_PREFIX):].strip() ))

	async def on_command(self, message, command, args):
		pass

	async def calc(self, message, args):
		self.query_message = message
		self.answer_message = await message.channel.send( postfix.quickly( message.content[1 + 4 + len(self.client.COMMAND_PREFIX):].strip() ) )

plugins = [Essentials, EssentialsCalc]
commands = {
	'ping':{
		'function': Essentials.ping
	},
	'flip':{
		'function': Essentials.flip
	},
	'whoami':{
		'function': Essentials.whoami
	},
	'whois':{
		'function': Essentials.whois
	},
	'define':{
		'usage': '[word]',
		'desc':  'Look up the definition of a word.',
		'function': Essentials.define
	},
	'ud':{
		'usage': '[word or phrase]',
		'desc':  'Look up the definition of a word from urban dictionary.',
		'function': Essentials.urbandictionary
	},
	'whereami':{'perms':['op'], 'function': Essentials.whereami},
	'filth':{
		'desc': 'Generate a random filthy/offensive word or phrase.',
		'function': Essentials.filth
	},
	'perms':{
		'desc': 'Prints your permissions.',
		'function': Essentials.get_perms
	},
	'ctime':{
		'desc': 'Converts unix epoch number to a human-readable time string.',
		'example': '1518765410.543',
		'function': Essentials.get_ctime
	},
	'chavatar':{
		'desc': 'Changes the avatar of the bot to the image at url.',
		'usage': '[url]',
		'perms': ['op', 'admin'],
		'function': Essentials.chavatar
	},
	'nick': {
		'function': Essentials.chnick,
		'desc': 'Changes the nickname in this server.',
		'usage': '[nickname]'
	},

	'calc':{
		'usage': '[postfix expr]',
		'desc':  'Does a calculation.',
		'example': '3 3 * 4 4 * + sqrt',
		'function': EssentialsCalc.calc
	},

	'roll':{
		'function': Essentials.roll_dice,
		'usage': 'XdY',
		'desc': 'Rolls an X sided die Y times',
		'example': '4d6'
	},
	'rolls':{
		'function': Essentials.roll_dice_and_sum,
		'usage': 'XdY',
		'desc': 'Rolls an X sided die Y times, and prints the sum.',
		'example': '4d6'
	},
	'christmas':{
		'function': Essentials.when_is_christmas
	},

	'kill':{
		'function': Essentials.kill_bot
	},

	'img': {
		'function': Essentials.image_search,
		'usage': '[query]',
		'example': 'jessica rabbit'
	}
}
