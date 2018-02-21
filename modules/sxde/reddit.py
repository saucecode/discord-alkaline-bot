from ..alkalineplugin import AlkalinePlugin
import random, requests, aiohttp, time, json

from ..sailortalk import sailor_word

class Reddit(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.cached = {}
		self.expiry_time = 10*60 # 10 minutes

		self.left_arrow = '\u25C0'
		self.right_arrow = '\u25B6'

		self.name = 'Reddit'
		self.version = '0.1'
		self.author = 'Julian'

	async def on_command(self, message, command, args):
		if command == 'rr':
			subreddit = args.split(' ')[0]
			url = 'https://reddit.com/r/' + subreddit + '/.json'

			urls = await self.request_reddit_data(url)
			self.rr_message_url = url
			self.rr_message = await message.channel.send('1/{} {}'.format(len(urls), urls[0]))

			await self.rr_message.add_reaction(self.left_arrow)
			await self.rr_message.add_reaction(self.right_arrow)

		if command == 'rrtop':
			subreddit = args.split(' ')[0]
			urls = await self.request_reddit_data('https://reddit.com/r/' + subreddit + '/.json')
			await message.channel.send(urls[0])

		elif command == 'rrdebug':
			await message.channel.send('```\n{}\n```'.format(json.dumps(self.cached, indent=4)))

	async def on_reaction_add(self, reaction, user):
		if reaction.message.id == self.rr_message.id:
			if reaction.emoji in [self.left_arrow, self.right_arrow]:

				index = int(self.rr_message.content.split('/')[0]) - 1
				if reaction.emoji == self.left_arrow:
					index -= 1
				elif reaction.emoji == self.right_arrow:
					index += 1

				index %= len(self.cached[self.rr_message_url]['content'])

				await self.rr_message.edit(content='{}/{} {}'.format(index+1, len(self.cached[self.rr_message_url]['content']), self.cached[self.rr_message_url]['content'][index]))

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
				self.cached[url]['content'] = ['{} | {}'.format(i['data']['title'], i['data']['url']) for i in dat['data']['children']]
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
	},
	'rrdebug':{}
}
