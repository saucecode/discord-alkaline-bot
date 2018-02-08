import discord
import asyncio
import importlib

client = discord.Client()
COMMAND_PREFIX = ']'

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

	client.plugins = {}

	with open('default_modules','r') as f:
		for line in f:
			line = line.strip()
			if line[0] == '#' or len(line) < 3: continue

			load_chatbot_module(client, line)

def load_chatbot_module(client, module_identifier):
	print('Loading module:',module_identifier, end=' ...')

	try:
		loaded_module = importlib.import_module('modules.%s' % (module_identifier,))
	except ImportError as err:
		print(' failed:', err.msg)
		return

	for klass in loaded_module.plugins:
		if not loaded_module in client.plugins:
			client.plugins[loaded_module] = []

		client.plugins[loaded_module].append( klass(client) )

	print(' done.')

@client.event
async def on_message(message):
	for mod in client.plugins:
		for plugin in client.plugins[mod]:
			await plugin.on_message(message)

	if message.content.startswith(COMMAND_PREFIX) and len(message.content) > 1 and message.author.id != client.user.id:
		command = message.content.split(' ')[0][1:]
		for key in client.plugins:
			if command in key.commands:
				for plugin in client.plugins[key]:
					await plugin.on_command(message, command, message.content[2 + len(command):])

	if message.content == COMMAND_PREFIX + 'modules':
		await message.channel.send( "```%s```" % '\n'.join([k.__name__ + '\n\t' + ' '.join([a.__class__.__name__ for a in client.plugins[k]]) for k in client.plugins]) )

	if message.content == COMMAND_PREFIX + 'reloadall':
		output = []

		for key in client.plugins:
			new_module = importlib.reload(key)
			del client.plugins[key]
			client.plugins[new_module] = []

			for klass in new_module.plugins:
				client.plugins[new_module].append( klass(client) )
				output.append( new_module.__name__ + '.' + klass.__name__ )

		await message.channel.send('Reloaded the following plugins: {}'.format( ' '.join(output) ))

	if message.content.startswith(COMMAND_PREFIX + 'loadmodule'):
		module_name = message.content.split(' ')[1]
		load_chatbot_module(client, module_name)

	if message.content.startswith(COMMAND_PREFIX + 'reloadmodule'):
		module_name = 'modules.' + message.content.split(' ')[1]
		module_to_reload = None

		for mod in client.plugins:
			if mod.__name__ == module_name:
				module_to_reload = mod
				break

		if module_to_reload:
			output = []
			reloaded_module = importlib.reload(module_to_reload)
			del client.plugins[module_to_reload]
			client.plugins[reloaded_module] = []

			for klass in reloaded_module.plugins:
				client.plugins[reloaded_module].append( klass(client) )
				output.append( klass.__name__ )

			await message.channel.send('Reloaded module with these plugins: %s' % ' '.join(output))
		else:
			await message.channel.send('Could not find a module with that name.')



with open('secrettoken', 'r') as f:
	client_token = f.read()

client.run(client_token)
