from ..alkalineplugin import AlkalinePlugin
import random, requests, aiohttp, time

from ..sailortalk import sailor_word

class Reddit(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.cached = {}
		self.expiry_time = 10*60 # 10 minutes

		self.name = 'Reddit'
		self.version = '0.1'
		self.author = 'Julian'

	async def on_command(self, message, command, args):
		if command == 'rr':
			subreddit = args.split(' ')[0]
			#dat = requests.get('https://reddit.com/r/' + subreddit + '/.json', headers={'User-Agent':'Discord-Alkaline-Bot'}).json()
			#urls = [i['data']['url'] for i in dat['data']['children']] # pull urls from reddit post list
			urls = await self.request_reddit_data('https://reddit.com/r/' + subreddit + '/.json')
			self.rr_message = await message.channel.send(random.choice(urls))

		if command == 'rrtop':
			subreddit = args.split(' ')[0]
			#dat = requests.get('https://reddit.com/r/' + subreddit + '/top/.json?t=all', headers={'User-Agent':'Discord-Alkaline-Bot'}).json()
			#urls = [i['data']['url'] for i in dat['data']['children']] # pull urls from reddit post list
			urls = await self.request_reddit_data('https://reddit.com/r/' + subreddit + '/.json')
			await message.channel.send(random.choice(urls))

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
				self.cached[url]['content'] = [i['data']['url'] for i in dat['data']['children']]
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
