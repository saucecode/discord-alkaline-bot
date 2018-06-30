
# FORMAT
'''

{
	"Bob": {
		"gender": "male",
		"0": ["1", "2", "Alice"],
		"my appendage": ["action", "target appendage", "target"]
	},
	"Alice": {
		"gender": "female",
		"4": ["3", "5", "Bob"],
		"6": ["1", "3", "Eve"]
	}
}

'''

import random, re
try:
	import discord
except ImportError:
	print('Discord not loaded.')

class VerbGraph:
	def __init__(self):
		self.graph = {}
		self.appendages = [
			'left foot', 'right foot', 'inner thigh', 'bellybutton', 'right arm', 'left arm', 'lower back',
			'buttocks', 'left hand', 'right hand', 'face', 'hair', 'ear', 'tooth', 'head', 'neck', 'mouth',
			'nose', 'nostrils', 'elbow', 'earlobe', 'large intestine', 'colon', 'liver'
		]
		self.actions = [
			'leaning on', 'massaging', 'stabbing', 'nuzzling', 'munching on',
			'wiping', 'sensually tracing', 'poorly massaging', 'kneading',
			'nibbling', 'licking', 'drooling all over', 'vomitting into',
			'crying into', 'grinding against', 'suffocating', 'caressing',
			'fondling'
		]
		self.pronouns = {
			"male": "his",
			"female": "her"
		}

	def modify_node(self, actor, actor_appendage, act, target_appendage, target, gender=None):
		if not actor in self.graph:
			self.graph[actor] = {'gender':'male'}

		if gender:
			self.graph[actor]['gender'] = gender

		self.graph[actor][str(actor_appendage)] = [str(act), str(target_appendage), target]

	def walk(self, actor, depth=8):
		if not actor in self.graph:
			raise KeyError('{} has no definition in graph.')

		seen_actors = []
		strings = []
		while not actor in seen_actors and actor in self.graph and len(strings) < depth:
			seen_actors.append(actor)
			actor_appendage = random.choice( [k for k in self.graph[actor] if k.isdigit()] )

			act, target_appendage, target = self.graph[actor][actor_appendage] # unpack actor's appendage definition
			pronoun = self.pronouns[self.graph[actor]['gender']]

			strings.append(
				'{actor} is {act} {target}\'s {target_appendage} with {pronoun} {actor_appendage}'.format(
					actor = actor,
					act = self.actions[int(act)],
					target = target,
					target_appendage = self.appendages[int(target_appendage)],
					actor_appendage = self.appendages[int(actor_appendage)],
					pronoun = pronoun
				)
			)

			actor = target

		return strings

	# does ID lookups to replace IDs with names -- assumes node keys are valid IDs
	def walk_named2(self, actor, message : discord.Message, depth=8):
		# discord.utils.get(message.guild.members, id=args)
		lookup = {}
		strings = self.walk(actor, depth)
		parsed_strings = []
		for s in strings:
			ids = re.findall('\\d{10,}', s)
			for i in ids:
				lookup[i] = discord.utils.get(message.guild.members, id=int(i)).display_name

		for s in strings:
			for i in lookup:
				s = s.replace(i, lookup[i])
			parsed_strings.append(s)

		return parsed_strings

	def attach_names(self, strings, message : discord.Message):
		lookup = {}
		parsed_strings = []
		for s in strings:
			ids = re.findall('\\d{10,}', s)
			for i in ids:
				lookup[i] = discord.utils.get(message.guild.members, id=int(i)).display_name

		for s in strings:
			for i in lookup:
				s = s.replace(i, lookup[i])
			parsed_strings.append(s)

		return parsed_strings

	def all_actions(self, actor):
		if not actor in self.graph:
			raise KeyError('{} has no definition in graph.')

		strings = []
		for actor_appendage in [i for i in self.graph[actor] if i.isdigit()]:

			act, target_appendage, target = self.graph[actor][actor_appendage] # unpack actor's appendage definition
			pronoun = self.pronouns[self.graph[actor]['gender']]

			strings.append(
				'{actor} is {act} {target}\'s {target_appendage} with {pronoun} {actor_appendage}'.format(
					actor = actor,
					act = self.actions[int(act)],
					target = target,
					target_appendage = self.appendages[int(target_appendage)],
					actor_appendage = self.appendages[int(actor_appendage)],
					pronoun = pronoun
				)
			)

		return strings


if __name__ == '__main__':
	graph = VerbGraph()
	graph.modify_node('saucecode', 1, 1, 3, 'Alice')
	graph.modify_node('Alice', 2, 3, 0, 'saucecode', 'female')
	graph.modify_node('Alice', 1, 0, 2, 'Bob')
	print('\n'.join(graph.walk('saucecode')))
	print('\n'.join(graph.walk('Alice')))
