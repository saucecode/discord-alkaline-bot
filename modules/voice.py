from .alkalineplugin import AlkalinePlugin
import discord, asyncio, youtube_dl, requests, urllib3, io, subprocess, threading, json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from concurrent.futures import ThreadPoolExecutor

'''

			HERE BE DRAGONS

			https://github.com/Rapptz/discord.py/issues/1065
			https://stackoverflow.com/questions/48727101/python-subprocess-popen-fails-to-correctly-pipe-urllib3-response

			subprocess.Popen HATES blocking stdin streams.
			A threading.Thread hack is used to correctly implement the streaming of audio resources to ffmpeg.

'''

class VoiceManager(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.queue = []
		self.executor = ThreadPoolExecutor(4)
		self.http = urllib3.PoolManager()

		self.audio_format_code = '171'

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
			self.queue.append( {'type':'query', 'query': args} )

		elif command == 'skip':
			self.client.voice.stop()

		elif command == 'stop':
			self.queue.clear()
			self.client.voice.stop()

		elif command == 'queue':
			await message.channel.send('```\n{}\n```'.format(json.dumps(self.queue,indent=4)))


	def get_youtube_info(self, url):
		with youtube_dl.YoutubeDL({'format':'bestaudio/audio', 'default_search':'ytsearch'}) as yt:
			data = yt.extract_info(url, download=False)
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
						self.queue.pop(0)

					elif self.queue[0]['type'] == 'query':
						data = await self.client.loop.run_in_executor(self.executor, self.get_youtube_info, self.queue[0]['query'])

						if 'entries' in data:
							data = data['entries'][0]

						chosen_format = [j for j in data['formats'] if j['format_id'] == '171'][0]

						player = discord.FFmpegPCMAudio(subprocess.PIPE, pipe=True)
						req = self.http.request('GET', chosen_format['url'], preload_content=False)

						def wdiect(r,proc):
							try:
								while True:
									chunk = r.read(8192)
									if not chunk:
										r.close()
										print('STOPPED THREAD - END OF STREAM')
										proc.stdin.close()
										break
									proc.stdin.write(chunk)
							except BrokenPipeError:
								print('STOPPED THREAD - BROKEN PIPE')
								r.close()

						download_thread = threading.Thread(target=wdiect, args=(req,player._process))

						def after():
							req.close()
							#player.stdin.close()

						self.client.voice.play(
							discord.PCMVolumeTransformer(player, volume=0.5), after=after
						)

						download_thread.start()
						self.queue.pop(0)

			await asyncio.sleep(1)

plugins = [VoiceManager]
commands = {
	'voice': {
		'desc': 'Join/leave your voice channel.'
	},
	'play':{},
	'yt':{
		'usage': '[youtube url or search query]',
		'desc':  'Adds a youtube video to the queue.'
	},
	'queue':{
		'desc':  'Lists items in the play queue.'
	},
	'skip':{
		'desc':  'Skips the currently playing song.'
	},
	'stop':{
		'desc':  'Stops playing and clears the queue.'
	}
}
