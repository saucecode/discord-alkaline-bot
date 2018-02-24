from .alkalineplugin import AlkalinePlugin
import discord, asyncio, youtube_dl, requests, urllib3, io, subprocess, threading, json, re, os, random

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

		self.playlists = {}
		self.load_playlists()

		self.audio_format_codes = ['171', '43']

		self.name = 'VoiceManager'
		self.version = '0.3'
		self.author = 'Julian'

		for task in asyncio.Task.all_tasks():
			if hasattr(task, 'alkaline_identifier') and task.alkaline_identifier == self.name:
				print('STOPPED TASK:', self.name)
				task.cancel()

		task = self.client.loop.create_task(self.background_task())
		task.alkaline_identifier = self.name

	def load_playlists(self):
		if not os.path.exists('data/playlists.json'):
			self.save_playlists()

		with open('data/playlists.json', 'r') as f:
			self.playlists = json.load(f)

	def save_playlists(self):
		with open('data/playlists.json', 'w') as f:
			json.dump(self.playlists, f, indent=4, separators=(',', ': '))

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
			if args.startswith('https://') or args.startswith('http://'):
				self.queue.append( {'type':'query', 'query': args} )
			else:
				search = self.search_songs(args)
				if len(search) > 5:
					await message.channel.send('Found more than 5 results - please be more specific.')
				elif len(search) > 1:
					await message.channel.send('Found these results - please be more specific.\n```\n{}\n```'.format( '\n'.join(search) ))
				elif len(search) == 0:
					await message.channel.send('Added {} to the queue (ytsearch).'.format( args ))
					self.queue.append( {'type':'query', 'query': args} )
				else:
					await message.channel.send('Added {} to the queue. (cached)'.format( '-'.join(search[0].split('-')[:-1]) ))
					self.queue.append( {'type':'file', 'filename': 'downloaded/' + search[0]} )


		elif command == 'yt':
			self.queue.append( {'type':'query', 'query': args} )

		elif command == 'skip':
			self.client.voice.stop()

		elif command == 'stop':
			self.queue.clear()
			self.client.voice.stop()

		elif command == 'queue':
			if len(self.queue) > 0:
				await message.channel.send(
				'```\n{}\n```'.format(
					'\n'.join(
						[ '{}. ({}) {}'.format(i, 'ytsearch' if x['type'] == 'query' else 'cache', x['query'] if x['type'] == 'query' else x['filename']) for i,x in enumerate(self.queue) ]
					)
				)
				)
			else:
				await message.channel.send('Queue is empty.')

		elif command == 'pop':
			if len(self.queue) > 0:
				if len(args) > 0:
					try:
						int(args)
						await message.channel.send('Removed {} from queue'.format(self.queue.pop(int(args))))
					except:
						await message.channel.send('Must specify a position.')
				else:
					await message.channel.send('Removed {} from queue'.format(self.queue.pop()))

		elif command == 'shuffle':
			random.shuffle(self.queue)
			await message.channel.send('Queue shuffled.')

		# PLAYLIST COMMANDS
		elif command == 'pladd':
			if len(args.split(' ')) == 1:
				await message.channel.send('Usage: {}{} {}'.format(self.client.COMMAND_PREFIX, command, commands[command]['usage']))
			else:
				playlist_name = args.split(' ')[0]
				query = args[len(playlist_name)+1:]

				if not playlist_name in self.playlists:
					self.playlists[playlist_name] = []

				search = self.search_songs(query)

				if len(search) > 5:
					await message.channel.send('Found more than 5 results - please be more specific.')
				elif len(search) > 1:
					await message.channel.send('Found these results - please be more specific.\n```\n{}\n```'.format( '\n'.join(search) ))
				elif len(search) == 0:
					await message.channel.send('Couldn\'t find a file matching that query.'.format( args ))
				else:
					self.playlists[playlist_name].append( search[0] )
					self.save_playlists()
					await message.channel.send('Added `{}`. Playlist `{}` now has {} elements.'.format( search[0],playlist_name,len(self.playlists[playlist_name]) ))

		elif command == 'playlists':
			actual_playlists = [playlist_name for playlist_name in self.playlists if len(self.playlists[playlist_name]) > 0]
			await message.channel.send('I found {} playlists:\n{}'.format( len(actual_playlists), ' '.join(actual_playlists) ))

		elif command == 'plview':
			if len(args) == 0 or ' ' in args or not args in self.playlists:
				await message.channel.send('Please specify playlist name.')
			else:
				await message.channel.send('```\n{}\n```'.format( '\n'.join( ['{}. {}'.format(index,song) for index,song in enumerate(self.playlists[args])] ) ))

		elif command == 'plpop':
			args = args.split(' ')
			if not len(args) == 2:
				await message.channel.send('Usage: {}{} {}'.format(self.client.COMMAND_PREFIX, command, commands[command]['usage']))
			elif not args[0] in self.playlists:
				await message.channel.send('Specify an existing playlist name.')
			else:
				try:
					int(args[1])
					item = self.playlists[args[0]].pop(int(args[1]))
					await message.channel.send('Removed `{}` from playlist `{}`.'.format(item, args[0]))
					self.save_playlists()
				except (IndexError, ValueError):
					await message.channel.send('Usage: {}{} {}'.format(self.client.COMMAND_PREFIX, command, commands[command]['usage']))
					return

		elif command == 'plplay':
			if not args in self.playlists:
				await message.channel.send('Specify an existing playlist name.')
			else:
				for fname in self.playlists[args]:
					self.queue.append( {'type':'file', 'filename':'downloaded/{}'.format(fname)} )
				await message.channel.send('Added {} new files to the queue.'.format(len(self.playlists[args])))


	def search_songs(self, query):
		files = os.listdir('downloaded/')
		flatten = lambda l: [item for sublist in l for item in sublist]

		if '..' in query or '/' in query:
			return []

		# get all files who contain at least one word in the query string
		# example: query = "rick never" will return all files with "rick" and "never" in their names.
		# cases are ignored
		files = list(set(flatten([[x for x in files if q.lower() in x.lower().replace('-','')] for q in query.split(' ')])))

		files_sorted = []
		for f in files:
			count = 0
			for tag in query.split(' '):
				if tag.lower() in f.lower().replace('-',''):
					count += 1
			files_sorted.append( (count, f) )

		temp_sort = sorted(files_sorted, reverse=True, key=lambda x:x[0])
		if len(temp_sort) > 1 and temp_sort[0][0] > temp_sort[1][0]:
			return [temp_sort[0][1]]
		files_sorted = [x[1] for x in temp_sort if x[0]>1]
		return files_sorted

	def get_youtube_info(self, url):
		with youtube_dl.YoutubeDL({'format':'bestaudio/audio', 'default_search':'ytsearch'}) as yt:
			data = yt.extract_info(url, download=False)
			return data

	def sanitize_video_title(self, title):
		return re.sub('[^a-zA-Z0-9\\._ -]', '', title)

	async def background_task(self):
		while 1:

			if not self.client.voice:
				continue

			if len(self.queue) > 0:
				if not self.client.voice.is_playing():
					if self.queue[0]['type'] == 'file':
						self.client.voice.play(
							discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.queue[0]['filename']), volume=0.5)
						)
						self.queue.pop(0)

					elif self.queue[0]['type'] == 'query':
						try:
							data = await self.client.loop.run_in_executor(self.executor, self.get_youtube_info, self.queue[0]['query'])
						except youtube_dl.utils.DownloadError:
							print('Failed to download', self.queue[0])
							self.queue.pop(0)
							self.queue.insert(0, {'type':'file', 'filename':'data/error2.wav'})
							continue

						if 'entries' in data:
							data = data['entries'][0]

						available_formats = [j for j in data['formats'] if j['format_id'] in self.audio_format_codes]
						if len(available_formats) == 0:
							self.queue.pop(0)
							self.queue.insert(0, {'type':'file', 'filename':'data/error2.wav'})
							continue
						chosen_format = available_formats[0]

						player = discord.FFmpegPCMAudio(subprocess.PIPE, pipe=True)
						req = self.http.request('GET', chosen_format['url'], preload_content=False)
						filename = 'downloaded/{}-{}.webm'.format( self.sanitize_video_title(data['title']), data['id'] )
						already_downloaded = os.path.exists(filename)

						if not already_downloaded:
							def wdiect(r,proc,fname):
								f = open(fname, 'wb')
								try:
									while True:
										chunk = r.read(8192*4)
										if not chunk:
											r.close()
											print('STOPPED THREAD - END OF STREAM')
											proc.stdin.close()
											break
										f.write(chunk) # FILE WRITE MUST GO FIRST!!
										proc.stdin.write(chunk)
								except BrokenPipeError:
									print('STOPPING THREAD - BROKEN PIPE - CONTINUING DOWNLOAD')

									while True:
										chunk = r.read(8192*4)
										if not chunk:
											break
										f.write(chunk)

									r.close()
								finally:
									f.close()

							download_thread = threading.Thread(target=wdiect, args=(req,player._process,filename))

							def after():
								req.close()
								#player.stdin.close()

							self.client.voice.play(
								discord.PCMVolumeTransformer(player, volume=0.5), after=after
							)

							download_thread.start()
						else:
							self.client.voice.play(
								discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename), volume=0.5)
							)

						self.queue.pop(0)

			await asyncio.sleep(1)

plugins = [VoiceManager]
commands = {
	'voice': {
		'desc': 'Join/leave your voice channel.'
	},
	'play':{
		'usage': '[song or file name]',
		'desc':  'Searches for a cached file and adds to the queue. If no cached file found, searches YouTube. Also accepts YouTube URLs.'
	},
	'yt':{
		'usage': '[youtube url or search query]',
		'desc':  'Adds a youtube video to the queue.'
	},
	'queue':{
		'desc':  'Lists items in the play queue.'
	},
	'pop':{
		'usage': '[position]',
		'desc':  'Removes song queued at position [position], or the end of the queue.'
	},
	'skip':{
		'desc':  'Skips the currently playing song.'
	},
	'stop':{
		'desc':  'Stops playing and clears the queue.'
	},

	'pladd': {
		'usage': '[playlist name] [song name]'
	},
	'plpop': {
		'usage': '[playlist name] [song position]'
	},
	'plplay': {},
	'playlists': {},
	'plview':{},
	'shuffle':{}
}
