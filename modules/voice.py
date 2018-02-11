from .alkalineplugin import AlkalinePlugin
import discord, asyncio, youtube_dl, requests, urllib3, io

from concurrent.futures import ThreadPoolExecutor

class VoiceManager(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.queue = []
		self.executor = ThreadPoolExecutor(4)
		self.http = urllib3.PoolManager()

		self.name = 'VoiceManager'
		self.version = '0.3'
		self.author = 'Julian'

		for task in asyncio.Task.all_tasks():
			if hasattr(task, 'alkaline_identifier') and task.alkaline_identifier == self.name:
				print('STOPPED TASK:', self.name)
				task.cancel()

		task = self.client.loop.create_task(self.background_task())
		task.alkaline_identifier = self.name

	async def on_command(self, message: discord.Message, command : str, args : str):
		if command == 'voice':
			if not message.author.voice:
				await message.channel.send('You need to be in a voice channel.')
				return

			if message.author.voice and message.author.voice.channel:
				if self.client.voice == None or (self.client.voice != None and not self.client.voice.is_connected()):
					self.client.voice = await message.author.voice.channel.connect()

				elif self.client.voice != None and self.client.voice.channel != message.author.voice.channel:
					await self.client.voice.move_to(message.author.voice.channel)

				elif self.client.voice != None and self.client.voice.channel == message.author.voice.channel:
					await self.client.voice.disconnect()

		elif command == 'play':
			self.queue.append( {'type':'file', 'filename': 'original.webm'} )

		elif command == 'yt':
			url = args
			data = await self.client.loop.run_in_executor(self.executor, self.get_youtube_info, url)
			if type(data) == dict:
				fmt = [j for j in data['formats'] if j['format_id'] == '171'][0]
				self.queue.append( {'type':'download', 'url':fmt['url'], 'filename':'downloaded/{}.webm'.format(data['id'])} )
				# await self.client.loop.run_in_executor(self.executor, self.download_url_into, fmt['url'], 'downloaded/' + data['id'] + '.m4a')


	def get_youtube_info(self, url):
		with youtube_dl.YoutubeDL({'format':'bestaudio/audio', 'default_search':'ytsearch'}) as yt:
			data = yt.extract_info(url, download=False, process=False)
			return data

	def download_url_into(self, url, path):
		req = requests.get(url, stream=True)
		with open(path, 'wb') as f:
			for chunk in req.iter_content(chunk_size=1024*40):
				if chunk:
					f.write(chunk)

	async def background_task(self):
		while 1:

			if len(self.queue) > 0:
				if not self.client.voice.is_playing():
					if self.queue[0]['type'] == 'file':

						fi = open(self.queue[0]['filename'], 'rb')

						self.client.voice.play(
							discord.FFmpegPCMAudio(fi, pipe=True), after=fi.close
						)
						self.queue.pop()

					elif self.queue[0]['type'] == 'download':

						r = self.http.request('GET', self.queue[0]['url'], preload_content=False)

						self.client.voice.play(
							discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(r, pipe=True), volume=0.5), after=r.release_conn
						)
						self.queue.pop()

			await asyncio.sleep(1)

plugins = [VoiceManager]
commands = {
	'voice': {
		'usage':'',
		'desc': 'Join/leave your voice channel.'
	},
	'play':{},
	'yt':{}
}
