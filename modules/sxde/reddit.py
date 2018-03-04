from ..alkalineplugin import AlkalinePlugin
import random, aiohttp, time, re, os, subprocess, discord

from concurrent.futures import ThreadPoolExecutor

LEFT_ARROW = '\u25C0'
TWISTED_ARROWS = '\U0001F500'
RIGHT_ARROW = '\u25B6'
REDDIT_CACHE = {}
EXPIRY_TIME = 600

FFMPEG_THREADS = 4

class RollingMessage:
	def __init__(self, client, message, url, links, index=0):
		self.client = client
		self._message = message
		self.url = url
		self.links = links
		self.index = index

	@classmethod
	async def from_command(cls, client, msg, command, subreddit):
		endpoint = 'top/.json?t=all&limit=100' if command == 'rrtop' else '.json?limit=100'
		url = "https://reddit.com/r/{subreddit}/{endpoint}".format(subreddit=subreddit, endpoint=endpoint)
		message = await msg.channel.send('Requesting data...')
		links = await cls.fetch(url)
		links = links['data']['children']
		instance = cls(client, message, url, links)
		await instance.update_message()
		return instance

	@property
	def item_text(self):
		return '{item[title]} | {item[url]}'.format(item=self.links[self.index].get('data'))

	async def update_message(self):
		self.links = await self.fetch(self.url)
		self.links = self.links['data']['children']
		await self._message.edit(content='{}/{} {}'.format(self.index + 1, len(self.links), self.item_text))
		await self.set_reactions()

	async def roll_next(self):
		self.index += 1
		await self.update_message()

	async def roll_previous(self):
		self.index -= 1
		await self.update_message()

	async def roll_random(self):
		self.index = random.randrange(len(self.links))
		await self.update_message()

	async def set_reactions(self):
		for emoji in [LEFT_ARROW, TWISTED_ARROWS, RIGHT_ARROW]:
			await self._message.add_reaction(emoji)

	@staticmethod
	async def fetch(url):
		now = time.time()
		cached_item = REDDIT_CACHE.get(url, None)
		if cached_item and now < cached_item['expiration']:
			print('Cache hit: ', url)
			return cached_item['content']
		print('Cache miss: ', url)
		async with aiohttp.ClientSession() as sesh, sesh.get(url, headers={'User-Agent': 'Discord-Alkaline-Bot'}) as resp:
				dat = await resp.json()
				REDDIT_CACHE[url] = dict(expiration=now+EXPIRY_TIME, content=dat)
				return REDDIT_CACHE[url]['content']

	def __getattr__(self, item):
		return getattr(self._message, item)


class Reddit(AlkalinePlugin):
	def __init__(self, client):
		self.client = client
		self.rolling_messages = {}

		self.executor = ThreadPoolExecutor(4)

		self.name = 'Reddit'
		self.version = '0.2'
		self.author = 'Julian'

	async def download_reddit_video(self, video_url, audio_url):
		if not os.path.exists('downloaded/tmp'):
			os.mkdir('downloaded/tmp')

		video_code = audio_url.split('/')[-2]
		video_source_fname = video_code + '.' + video_url.split('/')[-1] + '.mp4'
		audio_source_fname = video_code + '.audio'

		async with aiohttp.ClientSession() as sesh, sesh.get(video_url, headers={'User-Agent': 'Discord-Alkaline-Bot'}) as resp:
			with open('downloaded/tmp/{}'.format(video_source_fname), 'wb') as f:

				while True:
					chunk = await resp.content.read(32768)
					if not chunk: break
					f.write(chunk)
				f.close()

		async with aiohttp.ClientSession() as sesh, sesh.get(audio_url, headers={'User-Agent': 'Discord-Alkaline-Bot'}) as resp:
			with open('downloaded/tmp/{}'.format(audio_source_fname), 'wb') as f:

				while True:
					chunk = await resp.content.read(32768)
					if not chunk: break
					f.write(chunk)
				f.close()

		return video_source_fname, audio_source_fname

	async def process_reddit_video(self, video_source_fname, audio_source_fname):
		output_fname = video_source_fname.split('.')[0] + '.mp4'
		command = 'ffmpeg -i downloaded/tmp/{} -i downloaded/tmp/{} -s 400x224 -acodec copy -threads {} -y downloaded/tmp/{}'.format(video_source_fname, audio_source_fname, FFMPEG_THREADS, output_fname)

		def processor(cmd):
			subprocess.check_output(cmd.split(' '))

		await self.client.loop.run_in_executor(self.executor, processor, command)

		return output_fname

	async def on_message(self, message):
		if not message.author.name == 'saucecode': return
		if not 'reddit.com/' in message.content:
			return

		regexpr = r'https?:\/\/(w{3}\.)?reddit\.com\/r\/[a-zA-Z_0-9-]+\/comments\/[a-zA-Z_0-9-]+\/.+\/'

		url = message.content.strip()
		ma = re.match(regexpr, url)

		if ma:
			dat = await RollingMessage.fetch(url + '.json')

			post = dat[0]['data']['children'][0]['data']
			if not post['domain'] == 'v.redd.it':
				return

			status = await message.channel.send('Downloading... ')

			video_url = post['secure_media']['reddit_video']['fallback_url']
			audio_url = 'https://v.redd.it/{}/audio'.format(video_url.split('/')[-2])

			# download the original sources
			video_source_fname, audio_source_fname = await self.download_reddit_video(video_url, audio_url)
			await status.edit(content=status.content + 'processing...')

			# convert to small 400x224 pixel files
			final_source_fname = await self.process_reddit_video(video_source_fname, audio_source_fname)

			if not '..' in video_source_fname:
				os.remove('downloaded/tmp/' + video_source_fname)
			if not '..' in audio_source_fname:
				os.remove('downloaded/tmp/' + audio_source_fname)

			await status.delete()

			with open('downloaded/tmp/' + final_source_fname, 'rb') as f:
				await message.channel.send(file=discord.File(fp=f, filename=final_source_fname))



	async def on_command(self, msg, command, args):
			subreddit = args.strip()
			rolling_message = await RollingMessage.from_command(self.client, msg, command, subreddit)
			self.rolling_messages[rolling_message.id] = rolling_message

	async def on_reaction_add(self, reaction, user):
		rolling_message = self.rolling_messages.get(reaction.message.id, None)
		if rolling_message is None:
			return
		options = {
			LEFT_ARROW: rolling_message.roll_previous,
			RIGHT_ARROW: rolling_message.roll_next,
			TWISTED_ARROWS: rolling_message.roll_random
		}
		action = options[reaction.emoji]
		return await action()


plugins = [Reddit]
commands = {
	'rr': {
		'usage': '[subreddit]',
		'desc': 'Retrieve a random reddit post from [subreddit].'
	},
	'rrtop': {
		'usage': '[subreddit]',
		'desc': 'Retrieve a random all-time best reddit post from [subreddit].'
	}
}
