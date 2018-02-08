
class Essentials:

	def __init__(self, client):
		self.client = client

		self.name = 'Essentials'
		self.version = '1.0'
		self.author = 'Julian'

	async def on_message(self, message):
		if message.content == ']ping':
			await message.channel.send('Pingo')

class Essential_Cats:

	def __init__(self, client):
		self.client = client

		self.name = 'Essentials'
		self.version = '1.0'
		self.author = 'Julian'

	async def on_message(self, message):
		if message.content == ']cats':
			await message.channel.send('http://i.imgur.com/jg0bGqX.jpg')

plugins = [Essentials, Essential_Cats]
