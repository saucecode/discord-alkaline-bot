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
import random, aiohttp, time, re, os, subprocess, discord

from concurrent.futures import ThreadPoolExecutor

LEFT_ARROW = '\u25C0'
TWISTED_ARROWS = '\U0001F500'
EJECT = '\U000023cf'
RIGHT_ARROW = '\u25B6'
RECENTER_ARROW = '\U000021a9'
REDDIT_CACHE = {}
EXPIRY_TIME = 600

REDDIT_VIDEO_FOLDER = 'v.redd.it_downloads'

FFMPEG_THREADS = 4

class RollingMessage:
	def __init__(self, parent, message, url, links, index=0):
		self.client = parent.client
		self.parent = parent
		self._message = message
		self.video_message = None
		self.url = url
		self.links = links
		self.index = index

	@classmethod
	async def from_command(cls, parent, msg, command, subreddit):
		endpoint = 'top/.json?t=all&limit=100' if command == 'rrtop' else '.json?limit=100'
		url = "https://reddit.com/r/{subreddit}/{endpoint}".format(subreddit=subreddit, endpoint=endpoint)
		message = await msg.channel.send('Requesting data...')
		links = await cls.fetch(url)
		links = links['data']['children']
		instance = cls(parent, message, url, links)
		await instance.update_message()
		return instance

	@property
	def item_text(self):
		return '{item[title]} | {item[url]}'.format(item=self.links[self.index].get('data'))

	async def recenter_message(self):
		newmessage = await self._message.channel.send('*Hello there*')
		#self.rolling_messages[rolling_message.id] = rolling_message
		del self.parent.rolling_messages[self._message.id]
		self.parent.rolling_messages[newmessage.id] = self
		await self._message.delete()
		self._message = newmessage
		await self.update_message()

	async def update_message(self):
		print('UPDATE MESSAGE')
		self.links = await self.fetch(self.url)
		self.links = self.links['data']['children']
		await self._message.edit(content='{}/{} {}'.format(self.index + 1, len(self.links), self.item_text))
		await self.set_reactions()

		regexpr = r'https?:\/\/(w{3}\.)?reddit\.com\/r\/[a-zA-Z_0-9-]+\/comments\/[a-zA-Z_0-9-]+\/.+\/'
		if 'v.redd.it' == self.links[self.index]['data']['domain']:
			if re.match(regexpr, 'https://reddit.com' + self.links[self.index]['data']['permalink']):

				print('VIDEO FOUND WHILE ROLLING')

				video_url = self.links[self.index]['data']['secure_media']['reddit_video']['fallback_url']
				audio_url = 'https://v.redd.it/{}/audio'.format(video_url.split('/')[-2])

				if os.path.exists('{}/{}.mp4'.format(REDDIT_VIDEO_FOLDER, video_url.split('/')[-2])):
					with open('{}/{}.mp4'.format(REDDIT_VIDEO_FOLDER, video_url.split('/')[-2]), 'rb') as f:
						msg = await self._message.channel.send(file=discord.File(fp=f, filename=video_url.split('/')[-2]+'.mp4'))
						self.parent.deletable_messages.append(msg)
						await msg.add_reaction(EJECT)
					return

				# download the original sources
				status = await self._message.channel.send('Downloading... ')
				video_source_fname, audio_source_fname = await self.parent.download_reddit_video(video_url, audio_url)
				await status.edit(content=status.content + 'processing...')

				# convert to small 400x224 pixel files
				final_source_fname = await self.parent.process_reddit_video(video_source_fname, audio_source_fname)

				if not '..' in video_source_fname:
					os.remove(REDDIT_VIDEO_FOLDER + '/' + video_source_fname)
				if audio_source_fname and not '..' in audio_source_fname:
					os.remove(REDDIT_VIDEO_FOLDER + '/' + audio_source_fname)

				await status.delete()

				with open(REDDIT_VIDEO_FOLDER + '/' + final_source_fname, 'rb') as f:
					msg = await self._message.channel.send(file=discord.File(fp=f, filename=video_url.split('/')[-2]+'.mp4'))
					self.parent.deletable_messages.append(msg)
					await msg.add_reaction(EJECT)

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
		for emoji in [LEFT_ARROW, TWISTED_ARROWS, RIGHT_ARROW, RECENTER_ARROW]:
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
		self.deletable_messages = []

		self.executor = ThreadPoolExecutor(4)

		self.name = 'Reddit'
		self.version = '0.2'
		self.author = 'Julian'

	async def download_reddit_video(self, video_url, audio_url):
		if not os.path.exists(REDDIT_VIDEO_FOLDER):
			os.mkdir(REDDIT_VIDEO_FOLDER)

		video_code = audio_url.split('/')[-2]
		video_source_fname = video_code + '.' + video_url.split('/')[-1] + '.mp4'
		audio_source_fname = video_code + '.audio'

		async with aiohttp.ClientSession() as sesh, sesh.get(video_url, headers={'User-Agent': 'Discord-Alkaline-Bot'}) as resp:
			with open('{}/{}'.format(REDDIT_VIDEO_FOLDER, video_source_fname), 'wb') as f:

				while True:
					chunk = await resp.content.read(32768)
					if not chunk: break
					f.write(chunk)
				f.close()

		async with aiohttp.ClientSession() as sesh, sesh.get(audio_url, headers={'User-Agent': 'Discord-Alkaline-Bot'}) as resp:
			if resp.status == 200:
				with open('{}/{}'.format(REDDIT_VIDEO_FOLDER, audio_source_fname), 'wb') as f:

					while True:
						chunk = await resp.content.read(32768)
						if not chunk: break
						f.write(chunk)
					f.close()
			else:
				print('Audio did not download.')
				audio_source_fname = None

		return video_source_fname, audio_source_fname

	async def process_reddit_video(self, video_source_fname, audio_source_fname):
		output_fname = video_source_fname.split('.')[0] + '.mp4'
		if audio_source_fname:
			command = 'ffmpeg -loglevel error -i {}/{} -i {}/{} -s 400x224 -acodec copy -threads {} -fs 8M -y {}/{}'.format(REDDIT_VIDEO_FOLDER, video_source_fname, REDDIT_VIDEO_FOLDER, audio_source_fname, FFMPEG_THREADS, REDDIT_VIDEO_FOLDER, output_fname)
		else:
			# no audio for this video
			command = 'ffmpeg -loglevel error -i {}/{} -an -s 400x224 -threads {} -fs 8M -y {}/{}'.format(REDDIT_VIDEO_FOLDER, video_source_fname, FFMPEG_THREADS, REDDIT_VIDEO_FOLDER, output_fname)

		def processor(cmd):
			subprocess.check_output(cmd.split(' '))

		await self.client.loop.run_in_executor(self.executor, processor, command)

		return output_fname

	async def on_message(self, message):
		if message.author.id == self.client.user.id: return
		if not 'reddit.com/' in message.content:
			return

		regexpr = r'https?:\/\/(w{3}\.)?reddit\.com\/r\/[a-zA-Z_0-9-]+\/comments\/[a-zA-Z_0-9-]+\/.+\/'

		url = message.content.strip()
		ma = re.match(regexpr, url)

		if ma:
			print('VIDEO SEEN IN ON_MESSAGE')
			dat = await RollingMessage.fetch(url + '.json')

			post = dat[0]['data']['children'][0]['data']
			if not post['domain'] == 'v.redd.it':
				return

			video_url = post['secure_media']['reddit_video']['fallback_url']
			audio_url = 'https://v.redd.it/{}/audio'.format(video_url.split('/')[-2])

			if os.path.exists('{}/{}.mp4'.format(REDDIT_VIDEO_FOLDER, video_url.split('/')[-2])):
				with open('{}/{}.mp4'.format(REDDIT_VIDEO_FOLDER, video_url.split('/')[-2]), 'rb') as f:
					await message.channel.send(file=discord.File(fp=f, filename=video_url.split('/')[-2]+'.mp4'))

				return

			# download the original sources
			status = await message.channel.send('Downloading... ')
			video_source_fname, audio_source_fname = await self.download_reddit_video(video_url, audio_url)
			await status.edit(content=status.content + 'processing...')

			# convert to small 400x224 pixel files
			final_source_fname = await self.process_reddit_video(video_source_fname, audio_source_fname)

			if not '..' in video_source_fname:
				os.remove(REDDIT_VIDEO_FOLDER + '/' + video_source_fname)
			if audio_source_fname and not '..' in audio_source_fname:
				os.remove(REDDIT_VIDEO_FOLDER + '/' + audio_source_fname)

			await status.delete()

			with open(REDDIT_VIDEO_FOLDER + '/' + final_source_fname, 'rb') as f:
				await message.channel.send(file=discord.File(fp=f, filename=video_url.split('/')[-2]+'.mp4'))



	async def on_command(self, msg, command, args):
			subreddit = args.strip()
			rolling_message = await RollingMessage.from_command(self, msg, command, subreddit)
			self.rolling_messages[rolling_message.id] = rolling_message

	async def on_reaction_add(self, reaction, user):
		if reaction.message.id in [x.id for x in self.deletable_messages]:
			print(reaction.emoji)
			if reaction.emoji == EJECT:
				msg = [x for x in self.deletable_messages if x.id == reaction.message.id][0]
				await msg.delete()
				self.deletable_messages.remove(msg)

		rolling_message = self.rolling_messages.get(reaction.message.id, None)
		if rolling_message:
			options = {
				LEFT_ARROW: rolling_message.roll_previous,
				RIGHT_ARROW: rolling_message.roll_next,
				TWISTED_ARROWS: rolling_message.roll_random,
				RECENTER_ARROW: rolling_message.recenter_message
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
