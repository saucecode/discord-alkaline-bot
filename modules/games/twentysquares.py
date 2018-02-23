from ..alkalineplugin import AlkalinePlugin
import discord, io, time
from PIL import Image, ImageDraw, ImageFont

BOARD_SIZE = 400,300
CHECKMARK = "\u2705"
CROSSMARK = "\u274E"

class Square:
	def __init__(self, next=None):
		self.next = next
		self.last = False
		self.special = False

class Marker:
	def __init__(self, color):
		self.color = color
		self.square = None

class TwentySquaresGame:
	def __init__(self, parent, playerRed : discord.User , playerBlue : discord.User, chan : discord.TextChannel ):
		self.parent = parent
		self.client = parent.client

		self.red = playerRed
		self.blue = playerBlue
		self.chan = chan

		self.redPieces = [Marker('red') for i in range(7)]
		self.bluePieces = [Marker('blue') for i in range(7)]

		# GENERATE A GRAPH OF SQUARES
		topSquare = Square()
		act = topSquare
		for i in range(7):
			act.next = Square()
			act = act.next
		bottomSquare = act
		topSquare.next.next.next.special = True

		redBottomSquare = Square()
		redBottomSquare.next = Square()
		redBottomSquare.next.last = True
		redBottomSquare.next.special = True

		blueBottomSquare = Square()
		blueBottomSquare.next = Square()
		blueBottomSquare.next.last = True
		blueBottomSquare.next.special = True

		bottomSquare.next = [redBottomSquare, blueBottomSquare]

		redSpawnSquare = Square()
		act = redSpawnSquare
		for i in range(3):
			act.next = Square()
			act = act.next
		act.special = True

		blueSpawnSquare = Square()
		act = redSpawnSquare
		for i in range(3):
			act.next = Square()
			act = act.next
		act.special = True


		self.redSpawnSquare = redSpawnSquare
		self.blueSpawnSquare = blueSpawnSquare
		self.topSquare = topSquare
		self.bottomSquare = bottomSquare
		self.redBottomSquare = redBottomSquare
		self.blueBottomSquare = blueBottomSquare

	async def populate_board(self):
		im = Image.new('RGB', size=BOARD_SIZE)
		font = ImageFont.truetype('Kenney Pixel.ttf', 24)
		draw = ImageDraw.Draw(im)
		draw.text((BOARD_SIZE[0]/2 - 48,4), 'Game of Ur', fill='white', font=font)
		draw.text( (4,64), self.red.display_name, fill='red', font=font )
		draw.text( (BOARD_SIZE[0] - 10*len(self.blue.display_name),64), self.blue.display_name, fill='blue', font=font )

		for i in range(4):
			draw.rectangle( [4 + i*48, 300-16-48-48-48, 4 + i*48 + 48, 300-16-48-48], fill='black', outline='blue' )
			draw.rectangle( [4 + i*48, 300-16-48, 4 + i*48 + 48, 300-16], fill='black', outline='red' )

		for i in range(6,8):
			draw.rectangle( [4 + i*48, 300-16-48-48-48, 4 + i*48 + 48, 300-16-48-48], fill='black', outline='blue' )
			draw.rectangle( [4 + i*48, 300-16-48, 4 + i*48 + 48, 300-16], fill='black', outline='red' )

		for i in range(8):
			draw.rectangle( [4 + i*48, 300-16-48-48, 4 + i*48 + 48, 300-16-48], fill='black', outline='white' )

		draw.rectangle( [ 4+12, 300-16-48-48-48+12, 4+48-12, 300-16-48-48-12], fill='black', outline='yellow' )
		draw.rectangle( [ 4+12, 300-16-48+12, 4+48-12, 300-16-12], fill='black', outline='yellow' )

		draw.rectangle( [ 4+12+6*48, 300-16-48-48-48+12, 4+48-12+6*48, 300-16-48-48-12], fill='black', outline='yellow' )
		draw.rectangle( [ 4+12+6*48, 300-16-48+12, 4+48-12+6*48, 300-16-12], fill='black', outline='yellow' )

		draw.rectangle( [4 + 3*48+12, 300-16-48-48+12, 4 + 3*48 + 48-12, 300-16-48-12], fill='black', outline='yellow' )

		image_bytes = io.BytesIO()
		im.save(image_bytes, format='png')

		await self.chan.send(
			'Game between <@{}> and <@{}>'.format(self.red.id, self.blue.id),
			file=discord.File( image_bytes.getbuffer(), filename='{}.png'.format(int(time.time())) )
		)


class TwentySquares(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.challenges = {}
		self.games = []

		self.name = 'The Royal Game of Ur'
		self.version = '0.2'
		self.author = 'Julian'

	async def on_command(self, message: discord.Message, command : str, args : str):
		if command == 'ts':
			if not len(message.mentions) == 1:
				await message.channel.send('You must @highlight who you wish to challenge.')
				return

			other = message.mentions[0]
			challenge_msg = await message.channel.send('<@{.id}> You have been challenged by <@{.id}> to a game of Ur. Do you accept?'.format(other, message.author))
			await challenge_msg.add_reaction(CHECKMARK)
			await challenge_msg.add_reaction(CROSSMARK)
			self.challenges[challenge_msg.id] = (other, message.author)

	async def on_reaction_add(self, reaction : discord.Reaction, user : discord.User):
		if not reaction.message.id in self.challenges: return
		other, challenger = self.challenges[reaction.message.id]

		if not user.id == other.id:
			return

		if reaction.emoji == CROSSMARK:
			await reaction.message.channel.send('<@{.id}> The challenge was rejected.'.format(challenger))
			del self.challenges[reaction.message.id]

		elif reaction.emoji == CHECKMARK:
			board = await reaction.message.channel.send('<@{.id}> The challenge was accepted. Starting the game...'.format(challenger))
			del self.challenges[reaction.message.id]

			instance = TwentySquaresGame(self, challenger, other, board.channel)
			self.games.append( instance )
			await instance.populate_board()


plugins = [TwentySquares]
commands = {
	'ts': {
		'usage': '@player1',
		'desc':  'Challenges another player to a game of Ur.',
		'example': '@Marco'
	}
}
