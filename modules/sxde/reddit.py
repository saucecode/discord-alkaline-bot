from ..alkalineplugin import AlkalinePlugin
import random, requests, aiohttp, time, json

from ..sailortalk import sailor_word

class RollingMessage:
	def __init__(self, message, data, formatter, index=0):
		self.message = message
		self.data = data
		self.index = index
		self.formatter = formatter

	async def roll_to(self, idx):
		self.index = idx
		await self.message.edit(content='{}/{} {}'.format(self.index+1, len(self.data), self.formatter(self.data[self.index])))

	async def roll_next(self):
		await self.roll_to((self.index + 1) % len(self.data))

	async def roll_previous(self):
		await self.roll_to((self.index - 1) % len(self.data))

class Reddit(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.cached = {}
		self.expiry_time = 10*60 # 10 minutes

		self.rolling_messages = {}

		self.left_arrow = '\u25C0'
		self.twisted_arrows = '\U0001F500'
		self.right_arrow = '\u25B6'

		self.name = 'Reddit'
		self.version = '0.1'
		self.author = 'Julian'

	async def on_command(self, message, command, args):
		if command in ['rr', 'rrtop']:
			subreddit = args.split(' ')[0]
			url = 'https://reddit.com/r/' + subreddit + '/.json?limit=100'

			if command == 'rrtop':
				url = 'https://reddit.com/r/' + subreddit + '/top/.json?t=all&limit=100'

			rolling_message = await message.channel.send('Retrieving data...') # create rolling-message target
			data = await self.request_reddit_data(url)

			# add buttons BEFORE adding to list
			await rolling_message.add_reaction(self.left_arrow)
			await rolling_message.add_reaction(self.twisted_arrows)
			await rolling_message.add_reaction(self.right_arrow)

			# add to list -- the message roll can now be triggered by on_reaction_add
			self.rolling_messages[rolling_message.id] = RollingMessage(rolling_message, data['data']['children'], lambda i:'{} | {}'.format(i['data']['title'], i['data']['url']))
			await self.rolling_messages[rolling_message.id].roll_to(0)

	async def on_reaction_add(self, reaction, user):
		if reaction.message.id in self.rolling_messages:
			if reaction.emoji == self.left_arrow:
				await self.rolling_messages[reaction.message.id].roll_previous()
			elif reaction.emoji == self.right_arrow:
				await self.rolling_messages[reaction.message.id].roll_next()
			elif reaction.emoji == self.twisted_arrows:
				await self.rolling_messages[reaction.message.id].roll_to(random.randint(0, len(self.rolling_messages[reaction.message.id].data)))

	async def request_reddit_data(self, url):
		if url in self.cached:
			now = time.time()
			if not now > self.cached[url]['expiry']:
				print(url,'is in the cache')
				return self.cached[url]['content']
		else:
			self.cached[url] = {}

		print('Downloading', url)

		async with aiohttp.ClientSession() as session:
			async with session.get(url, headers={'User-Agent':'Discord-Alkaline-Bot'}) as resp:
				dat = await resp.json()
				#self.cached[url]['content'] = [i['data'] for i in dat['data']['children']]
				self.cached[url]['content'] = dat
				self.cached[url]['expiry'] = time.time() + self.expiry_time
				return self.cached[url]['content']

plugins = [Reddit]
commands = {
	'rr':{
		'usage': '[subreddit]',
		'desc':  'Retrieve a random reddit post from [subreddit].'
	},
	'rrtop':{
		'usage': '[subreddit]',
		'desc':  'Retrieve a random all-time best reddit post from [subreddit].'
	}
}
