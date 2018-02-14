from .alkalineplugin import AlkalinePlugin
import discord, os, time, json, asyncio, re

def translate_time_string(time_string):
	seconds = -1
	multiplier = 1

	units = {
		'second': 1,
		'minute': 60,
		'hour': 60*60,
		'day': 60*60*24,
		'week': 60*60*24*7,
		'month': 60*60*24*30
	}

	mat = re.match('^an\s|^a\s|[0-9]+\s|[0-9]+\.[0-9]+', time_string)

	if mat:
		try:
			multiplier = float(time_string.split(' ')[0])
		except:
			pass

		word = time_string.split(' ')[1]
		if word in units:
			seconds = units[word]
		elif word[-1] == 's' and word[:-1] in units:
			seconds = units[word[:-1]]

	return seconds * multiplier

def humanreadable_time(t):
	out = []
	t = [t]

	def shortcut(o,t,s,i):
		if t[0] / i >= 1:
			o.append('%i %s' % (int(t[0] / i), s))
			while t[0] >= i:
				t[0] -= i

	shortcut(out, t, 'months', 60*60*24*30)
	shortcut(out, t, 'days', 60*60*24)
	shortcut(out, t, 'hours', 60*60)
	shortcut(out, t, 'minutes', 60)
	shortcut(out, t, 'seconds', 1)

	if len(out) == 1:
		return out[0]

	out[-1] = 'and ' + out[-1]

	return ', '.join(out)

class Notifications(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.name = 'Notifications'
		self.version = '2.0'
		self.author = 'Julian'

		self.notifications_file = os.getcwd() + os.sep + 'data' + os.sep + 'notifications.json'

		self.BACKUP_FILES = ['data' + os.sep + 'notifications.json']

		self.load_resources()

		for task in asyncio.Task.all_tasks():
			if hasattr(task, 'alkaline_identifier') and task.alkaline_identifier == self.name:
				print('STOPPED TASK:', self.name)
				task.cancel()

		task = self.client.loop.create_task(self.background_task())
		task.alkaline_identifier = self.name

	def load_resources(self):
		self.notifications = {'remind':[], 'tell':{}}

		if not os.path.exists(self.notifications_file):
			with open(self.notifications_file, 'w') as f:
				json.dump(self.notifications, f)

		with open(self.notifications_file, 'r') as f:
			self.notifications = json.load(f)

	def save_notifications(self):
		with open(self.notifications_file, 'w') as f:
			json.dump(self.notifications, f)

	async def on_message(self, message):
		pass

	async def on_command(self, message, command, args):
		if command == 'remind':
			'''seconds = int(args.split(' ')[0])
			remind_message = args[len(str(seconds)):]
			await message.channel.send('I\'ll remind you in %i seconds' % seconds)

			self.notifications['remind'].append( {'message': remind_message, 'when':time.time() + seconds, 'chan':message.channel.id, 'target_user': message.author.id, 'from_user': message.author.id} )
			self.save_notifications()'''

			subject = args.split(' ')[0]

			# determine subject:
			if subject.lower() == 'me':
				subject = message.author
			else:
				mat = re.match('<@.[0-9]+>', subject)

				if mat:
					print(subject[2:-1].replace('!',''), 'ONE')
					subject = discord.utils.get(message.guild.members, id=int(subject[2:-1].replace('!','')))
				else:
					print(subject, [m.display_name for m in message.guild.members], 'TWO')
					subject = discord.utils.find(lambda m: subject.lower() in m.name.lower() or subject.lower() in m.display_name.lower(), message.guild.members)

			if type(subject) == str:
				await message.channel.send('I don\'t know who that is...')
				return

			# determine time
			loc = args.rfind(' in ')
			time_string = args[loc+4:]
			time_seconds = translate_time_string(time_string)

			if time_seconds < 0:
				await message.channel.send('Failed to translate time.')
				return

			reminder_content = ' '.join(message.content.split(' ')[2:-3])
			if reminder_content[:3] == 'to ': reminder_content = reminder_content[3:]

			reminder = {'to': subject.id, 'when':time.time() + time_seconds, 'message': reminder_content, 'channel': message.channel.id}
			added = False

			if len(self.notifications['remind']) == 0:
				self.notifications['remind'].append(reminder)
				added = True
			else:
				for key,value in enumerate(self.notifications['remind']):
					if value['when'] >= reminder['when']:
						self.notifications['remind'][key:key] = [reminder]
						added = True
						break

			if not added:
				self.notifications['remind'].append(reminder)
				added = True

			self.save_notifications()

			await message.channel.send('Ok, I\'ll remind %s in %s' % ('you' if subject == message.author else 'them', humanreadable_time(time_seconds)) )

	async def background_task(self):
		while 1:

			curr_time = time.time()

			for reminder in self.notifications['remind']:
				if reminder['when'] < curr_time:
					chan = self.client.get_channel(reminder['channel'])
					await chan.send('<@{}> {}'.format(reminder['to'], reminder['message']))

					self.notifications['remind'].remove(reminder)
					self.save_notifications()
					break

			await asyncio.sleep(1)

plugins = [Notifications]
commands = {'remind':{}}
