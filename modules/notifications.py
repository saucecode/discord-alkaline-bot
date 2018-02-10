import discord, os, time, json, asyncio

class Notifications:

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
			seconds = int(args.split(' ')[0])
			remind_message = args[len(str(seconds)):]
			await message.channel.send('I\'ll remind you in %i seconds' % seconds)

			self.notifications['remind'].append( {'message': remind_message, 'when':time.time() + seconds, 'chan':message.channel.id, 'target_user': message.author.id, 'from_user': message.author.id} )
			self.save_notifications()

	async def background_task(self):
		while 1:

			curr_time = time.time()

			for reminder in self.notifications['remind']:
				if reminder['when'] < curr_time:
					chan = self.client.get_channel(reminder['chan'])
					await chan.send(reminder['message'])

					self.notifications['remind'].remove(reminder)
					self.save_notifications()
					break

			await asyncio.sleep(1)

plugins = [Notifications]
commands = {'remind':{}}
