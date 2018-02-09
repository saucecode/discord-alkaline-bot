import discord
import asyncio
import importlib

COMMAND_PREFIX = ']'

class AlkalineClient(discord.Client):

	async def on_ready(self):
		print('Logged in as')
		print(self.user.name)
		print(self.user.id)
		print('------')

		self.plugins = {}

		with open('default_modules','r') as f:
			for line in f:
				line = line.strip()
				if line[0] == '#' or len(line) < 3: continue

				self.load_chatbot_module(line)

	def load_chatbot_module(self, module_identifier):
		print('Loading module:',module_identifier, end=' ...')

		try:
			loaded_module = importlib.import_module('modules.%s' % (module_identifier,))
		except ImportError as err:
			print(' failed:', err.msg)
			return err.msg

		for klass in loaded_module.plugins:
			if not loaded_module in self.plugins:
				self.plugins[loaded_module] = []

			self.plugins[loaded_module].append( klass(self) )

		print(' done.')
		return True

	async def on_message(self, message):
		for mod in self.plugins:
			for plugin in self.plugins[mod]:
				await plugin.on_message(message)

		if message.content.startswith(COMMAND_PREFIX) and len(message.content) > 1 and message.author.id != self.user.id:
			command = message.content.split(' ')[0][1:]
			for key in self.plugins:
				if command in key.commands:
					for plugin in self.plugins[key]:
						await plugin.on_command(message, command, message.content[2 + len(command):])

		if message.content == COMMAND_PREFIX + 'modules':
			await message.channel.send( "```%s```" % '\n'.join([k.__name__ + '\n\t' + ' '.join([a.__class__.__name__ for a in self.plugins[k]]) for k in self.plugins]) )

		if message.content == COMMAND_PREFIX + 'reloadall':
			output = []

			for key in self.plugins:
				new_module = importlib.reload(key)
				del self.plugins[key]
				self.plugins[new_module] = []

				for klass in new_module.plugins:
					self.plugins[new_module].append( klass(self) )
					output.append( new_module.__name__ + '.' + klass.__name__ )

			await message.channel.send('Reloaded the following plugins: {}'.format( ' '.join(output) ))

		if message.content.startswith(COMMAND_PREFIX + 'loadmodule'):
			module_name = message.content.split(' ')[1]
			flag = self.load_chatbot_module(module_name)
			await message.channel.send('Successful.' if flag == True else flag)

		if message.content.startswith(COMMAND_PREFIX + 'reloadmodule'):
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
