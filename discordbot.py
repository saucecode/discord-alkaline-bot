import discord
import asyncio
import importlib

client = discord.Client()

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

	loaded_module = importlib.import_module('modules.%s' % (module_identifier,))

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

	if message.content == ']modules':
		await message.channel.send( "```%s```" % '\n'.join([k.__name__ + '\n\t' + ' '.join([a.__class__.__name__ for a in client.plugins[k]]) for k in client.plugins]) )

	if message.content == ']reloadall':
		output = []

		for key in client.plugins:
			new_module = importlib.reload(key)
			del client.plugins[key]
			client.plugins[new_module] = []

			for klass in new_module.plugins:
				client.plugins[new_module].append( klass(client) )
				output.append( new_module.__name__ + '.' + klass.__name__ )

		await message.channel.send('Reloaded the following plugins: {}'.format( ' '.join(output) ))

with open('secrettoken', 'r') as f:
	client_token = f.read()

client.run(client_token)
