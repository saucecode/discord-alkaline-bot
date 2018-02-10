import discord, os, json, random

class Reactions:

	def __init__(self, client):
		self.client = client

		self.BACKUP_FILES = ['data/reactions.json']

		self.reactions = {}
		self.load_reactions()

		self.name = 'Reactions'
		self.version = '0.1'
		self.author = 'Julian'

	def load_reactions(self):
		if not os.path.exists('data/reactions.json'):
			self.save_reactions()

		with open('data/reactions.json', 'r') as f:
			self.reactions = json.load(f)

	def save_reactions(self):
		with open('data/reactions.json', 'w') as f:
			json.dump(self.reactions, f, indent=4, separators=(',', ': '))

	async def on_message(self, message):
		if message.content[:2] == self.client.COMMAND_PREFIX * 2 and len(message.content) > 2:
			reaction_name = message.content[2:]
			if reaction_name in self.reactions:
				await message.channel.send(random.choice(self.reactions[reaction_name]))

	async def on_command(self, message, command, args):
		if command == 'reactionadd':
			if len(args.split(' ')) < 2:
				await message.channel.send('Invalid syntax. Usage: %s%s' % (self.client.COMMAND_PREFIX, commands[command]['usage']))

			reaction_name = args.split(' ')[0]
			reaction_data = args[len(reaction_name)+1:]

			if not reaction_name in self.reactions:
				self.reactions[reaction_name] = []

			self.reactions[reaction_name].append(reaction_data)

			self.save_reactions()

			await message.channel.send('Added reaction. %s now has %i reactions.' % (reaction_name, len(self.reactions[reaction_name])))


plugins = [Reactions]
commands = {
	'reactionadd': {
		'usage': 'reactionadd [reaction name] [reaction]',
	}
}
