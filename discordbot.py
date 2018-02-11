import discord
import asyncio
import importlib
import traceback
import json
import os

discord.opus.load_opus('libopus.so.0')
COMMAND_PREFIX = ']'

class AlkalineClient(discord.Client):

	async def on_ready(self):
		print('Logged in as')
		print(self.user.name)
		print(self.user.id)
		print('------')

		self.COMMAND_PREFIX = COMMAND_PREFIX

		self.voice = None

		self.plugins = {}
		self.settings = {}
		self.permissions = {}

		self.load_settings()
		self.load_permissions()

		with open('default_modules','r') as f:
			for line in f:
				line = line.strip()
				if len(line) < 3 or line[0] == '#': continue

				self.load_chatbot_module(line)

		print(
			'Alkaline has loaded', len(self.plugins),
			'modules, containing', len( [item for mod in self.plugins for item in self.plugins[mod]] ),
			'plugins, and found', sum( [len(mod.commands) for mod in self.plugins] ),
			'commands.'
		)

	def load_settings(self):
		if not os.path.exists('data/settings.json'):
			self.save_settings()

		with open('data/settings.json', 'r') as f:
			self.settings = json.load(f)

			if 'command_prefix' in self.settings:
				self.COMMAND_PREFIX = self.settings['command_prefix']
				COMMAND_PREFIX = self.settings['command_prefix']

	def save_settings(self):
		with open('data/settings.json', 'w') as f:
			json.dump(self.settings, f, indent=4, separators=(',', ': '))

	def load_permissions(self):
		if not os.path.exists('data/permissions.json'):
			self.save_permissions()

		with open('data/permissions.json', 'r') as f:
			self.permissions = json.load(f)

	def save_permissions(self):
		with open('data/permissions.json', 'w') as f:
			json.dump(self.permissions, f, indent=4, separators=(',', ': '))

	# returns a list of strings denoting the user's permissions
	def get_members_permissions(self, userid : int):
		return [perm for perm in self.permissions if int(userid) in self.permissions[perm]]

	# returns the set of permissions that a user has out of the list of permissions given
	def get_member_has_any_permissions(self, perms : list, userid : int):
		return set(perms).intersection(self.get_members_permissions(userid))

	def load_chatbot_module(self, module_identifier : str):
		print('Loading module:',module_identifier, end=' ...')

		try:
			loaded_module = importlib.import_module('modules.%s' % (module_identifier,))
		except Exception as err:
			print(' failed:', err.msg)
			traceback.print_exc()
			print()
			return err.msg

		for klass in loaded_module.plugins:
			if not loaded_module in self.plugins:
				self.plugins[loaded_module] = []

			self.plugins[loaded_module].append( klass(self) )

		print(' done.')
		return True

	async def on_message_edit(self, before, after):
		# ignore messages from myself and from other bots
		if before.author.id == self.user.id or before.author.bot:
			return

		# triggers plugin on_message_edit plugin functions
		for mod in self.plugins:
			for plugin in self.plugins[mod]:
				await plugin.on_message_edit(before, after)

	async def on_message(self, message):

		# ignore messages from myself and from other bots
		if message.author.id == self.user.id or message.author.bot:
			return

		# triggers plugin on_message plugin functions
		for mod in self.plugins:
			for plugin in self.plugins[mod]:
				await plugin.on_message(message)

		# detects command attempts and triggers on_command plugin functions
		if message.content.startswith(COMMAND_PREFIX) and len(message.content) > 1 and message.author.id != self.user.id:
			command = message.content.split(' ')[0][1:]
			for mod in self.plugins:
				if command in mod.commands:

					# execute command only if user has permission or if command requires no permissions
					if not 'perms' in mod.commands[command] or self.get_member_has_any_permissions(mod.commands[command]['perms'], message.author.id):
						for plugin in self.plugins[mod]:
							await plugin.on_command(message, command, message.content[1 + len(self.COMMAND_PREFIX) + len(command):])
					else:
						await message.channel.send('Permission denied.')


		# HARD CODED FUNCTIONS

		if message.content.startswith(self.COMMAND_PREFIX):
			can_core_commands = self.get_member_has_any_permissions(['admin'], message.author.id)
			if message.content == COMMAND_PREFIX + 'modules' and can_core_commands:
				await message.channel.send( "```%s```" % '\n'.join([k.__name__ + '\n\t' + ' '.join([a.__class__.__name__ for a in self.plugins[k]]) for k in self.plugins]) )

			if message.content == COMMAND_PREFIX + 'reloadall' and can_core_commands:
				await self.reload_all_plugin_modules(message)

			if message.content.startswith(COMMAND_PREFIX + 'loadmodule') and can_core_commands:
				module_name = message.content.split(' ')[1]
				flag = self.load_chatbot_module(module_name)
				await message.channel.send('Successful.' if flag == True else flag)

			if message.content.startswith(COMMAND_PREFIX + 'reloadmodule') and can_core_commands:
				await self.reload_plugin_module(message)

			if message.content.startswith(COMMAND_PREFIX + 'unloadmodule') and can_core_commands:
				await self.unload_plugin_module(message)


	async def unload_plugin_module(self, message):
		module_name = message.content.split(' ')[1]
		candidates = [mod for mod in self.plugins if module_name in mod.__name__]

		if len(candidates) > 1:
			await message.channel.send('Please be more specific. Found candidates: %s' % ' '.join([x.__name__ for x in candidates]))
			return

		elif len(candidates) == 0:
			await message.channel.send('Could not find a module with that name.')
			return

		mod = candidates[0]
		success_message = await message.channel.send('Unloading module %s (has %i plugins) ...' % (mod.__name__, len(self.plugins[mod])))

		try:
			plugin_tasks = [ task for task in asyncio.Task.all_tasks() if hasattr(task, 'alkaline_identifier') and task.alkaline_identifier in [plugin.name for plugin in self.plugins[mod]] ]
			if len(plugin_tasks) > 0:
				# await message.channel.send('Stopping %i tasks belonging to %s\'s plugins' % (len(plugin_tasks), mod.__name__))
				await success_message.edit(content=success_message.content + ' stopping %i tasks...' % len(plugin_tasks))

				for task in plugin_tasks:
					task.cancel()


			del self.plugins[mod]
			await success_message.edit(content=success_message.content + ' success.')
		except Exception as ex:
			await success_message.edit(content=success_message.content + ' failed: %s' % ex.msg)
			traceback.print_exc()
			print()


	async def reload_all_plugin_modules(self, message):
		output = []

		for key in self.plugins:
			new_module = importlib.reload(key)
			del self.plugins[key]
			self.plugins[new_module] = []

			for klass in new_module.plugins:
				self.plugins[new_module].append( klass(self) )
				output.append( new_module.__name__ + '.' + klass.__name__ )

		await message.channel.send('Reloaded the following plugins: {}'.format( ' '.join(output) ))

	async def reload_plugin_module(self, message):
		module_name = 'modules.' + message.content.split(' ')[1]
		module_to_reload = None

		for mod in self.plugins:
			if mod.__name__ == module_name:
				module_to_reload = mod
				break

		if module_to_reload:
			output = []
			reloaded_module = importlib.reload(module_to_reload)
			del self.plugins[module_to_reload]
			self.plugins[reloaded_module] = []

			for klass in reloaded_module.plugins:
				self.plugins[reloaded_module].append( klass(self) )
				output.append( klass.__name__ )

			await message.channel.send('Reloaded module with these plugins: %s' % ' '.join(output))
		else:
			await message.channel.send('Could not find a module with that name.')

with open('secrettoken', 'r') as f:
	client_token = f.read()

alkaline = AlkalineClient()
alkaline.run(client_token)
