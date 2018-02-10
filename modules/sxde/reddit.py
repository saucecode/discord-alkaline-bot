import random, requests

from ..sailortalk import sailor_word

class Reddit:

	def __init__(self, client):
		self.client = client

		self.name = 'Reddit'
		self.version = '0.1'
		self.author = 'Julian'

	async def on_message(self, message):
		pass

	async def on_command(self, message, command, args):
		if command == 'rr':
			subreddit = args.split(' ')[0]
			dat = requests.get('https://reddit.com/r/' + subreddit + '/.json', headers={'User-Agent':'Discord-Alkaline-Bot'}).json()
			urls = [i['data']['url'] for i in dat['data']['children']] # pull urls from reddit post list
			await message.channel.send(random.choice(urls))

		if command == 'rrtop':
			subreddit = args.split(' ')[0]
			dat = requests.get('https://reddit.com/r/' + subreddit + '/top/.json?t=all', headers={'User-Agent':'Discord-Alkaline-Bot'}).json()
			urls = [i['data']['url'] for i in dat['data']['children']] # pull urls from reddit post list
			await message.channel.send(random.choice(urls))

plugins = [Reddit]
commands = {'rr':{}, 'rrtop':{}}
