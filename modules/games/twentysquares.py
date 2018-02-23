from ..alkalineplugin import AlkalinePlugin
import discord, io, time, random
from PIL import Image, ImageDraw, ImageFont

BOARD_SIZE = 400,300
CHECKMARK = "\u2705"
CROSSMARK = "\u274E"
ROLL = "\U0001F504"
DIGIT = ["\U00000030\U000020e3", "\U00000031\U000020e3", "\U00000032\U000020e3", "\U00000033\U000020e3", "\U00000034\U000020e3", "\U00000035\U000020e3", "\U00000036\U000020e3", "\U00000037\U000020e3", "\U00000038\U000020e3", "\U00000039\U000020e3"]

class Square:
	def __init__(self, next=None):
		self.next = next
		self.last = False
		self.special = False
		self.marker = None

class Marker:
	def __init__(self, color, index):
		self.color = color
		self.index = index
		self.square = None

	def can_advance(self, spaces):
		if spaces == 0: return True

		target = self.square
		prev_target = None
		for i in range(spaces):
			prev_target = target
			target = target.next

		if target == None:
			if prev_target is not None and prev_target.special:
				return True
			return False

		if target.marker == None:
			return True

		if not target.marker.color == self.color:
			return True

		return False


class TwentySquaresGame:
	def __init__(self, parent, playerRed : discord.User , playerBlue : discord.User, chan : discord.TextChannel ):
		self.parent = parent
		self.client = parent.client

		self.red = playerRed
		self.blue = playerBlue
		self.chan = chan

		self.turn = self.red
		self.status = None
		self.status_message = None
		self.amount = 0 # the last rolled amount

		self.redPieces = [Marker('red', i+1) for i in range(7)]
		self.bluePieces = [Marker('blue', i+1) for i in range(7)]

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
		act.next = topSquare

		blueSpawnSquare = Square()
		act = blueSpawnSquare
		for i in range(3):
			act.next = Square()
			act = act.next
		act.special = True
		act.next = topSquare


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

		r = self.redSpawnSquare
		b = self.blueSpawnSquare
		for i in range(4)[::-1]:
			draw.rectangle( [4 + i*48, 300-16-48-48-48, 4 + i*48 + 48, 300-16-48-48], fill='black', outline='blue' )
			if b.marker is not None:
				draw.ellipse( [4 + i*48+16, 300-16-48-48-48+16, 4 + i*48 + 48-16, 300-16-48-48-16], outline='white', fill='blue' )
				draw.text( (4 + i*48+16+4, 300-16-48-48-48+16+4), str(b.marker.index) )

			draw.rectangle( [4 + i*48, 300-16-48, 4 + i*48 + 48, 300-16], fill='black', outline='red' )
			if r.marker is not None:
				draw.ellipse( [4 + i*48+16, 300-16-48+16, 4 + i*48 + 48-16, 300-16-16], outline='white', fill='red' )
				draw.text( (4 + i*48+16+4, 300-16-48+16+4), str(r.marker.index) )

			r = r.next
			b = b.next

		for i in range(6,8):
			draw.rectangle( [4 + i*48, 300-16-48-48-48, 4 + i*48 + 48, 300-16-48-48], fill='black', outline='blue' )
			draw.rectangle( [4 + i*48, 300-16-48, 4 + i*48 + 48, 300-16], fill='black', outline='red' )

		act = self.topSquare
		for i in range(8):
			draw.rectangle( [4 + i*48, 300-16-48-48, 4 + i*48 + 48, 300-16-48], fill='black', outline='white' )
			if act.marker is not None:
				draw.ellipse( [4 + i*48+16, 300-16-48-48+16, 4 + i*48 + 48-16, 300-16-48-16], outline='white', fill=act.marker.color )
				draw.text( (4 + i*48+16+4, 300-16-48-48+16+4), str(act.marker.index) )
			act = act.next

		draw.rectangle( [ 4+12, 300-16-48-48-48+12, 4+48-12, 300-16-48-48-12], fill=None, outline='yellow' )
		draw.rectangle( [ 4+12, 300-16-48+12, 4+48-12, 300-16-12], fill=None, outline='yellow' )

		draw.rectangle( [ 4+12+6*48, 300-16-48-48-48+12, 4+48-12+6*48, 300-16-48-48-12], fill=None, outline='yellow' )
		draw.rectangle( [ 4+12+6*48, 300-16-48+12, 4+48-12+6*48, 300-16-12], fill=None, outline='yellow' )

		draw.rectangle( [4 + 3*48+12, 300-16-48-48+12, 4 + 3*48 + 48-12, 300-16-48-12], fill=None, outline='yellow' )

		image_bytes = io.BytesIO()
		im.save(image_bytes, format='png')

		await self.chan.send(
			'Game between <@{}> and <@{}>'.format(self.red.id, self.blue.id),
			file=discord.File( image_bytes.getbuffer(), filename='{}.png'.format(int(time.time())) )
		)

	async def start(self):
		self.turn = random.choice( [self.red, self.blue] )
		self.status = 'waiting for roll'
		self.status_message = await self.chan.send('<@{.id}> rolls first. Click to roll.'.format(self.turn))
		await self.status_message.add_reaction( ROLL )

	async def next_turn(self):
		self.turn = self.red if self.turn.id == self.blue.id else self.blue
		self.status = 'waiting for roll'
		await self.populate_board()
		self.status_message = await self.chan.send('<@{.id}>\'s turn to roll. Click to roll.'.format(self.turn))
		await self.status_message.add_reaction( ROLL )

	async def do_roll(self):
		if not self.status == 'waiting for roll': return
		self.amount = sum( [random.randint(0,1) for i in range(4)] )
		await self.status_message.remove_reaction( ROLL, self.client.user )
		possible_moves = await self.determine_possible_moves(self.turn, self.amount)

		print('A roll of {} has {} possible moves'.format(self.amount, possible_moves))

		if possible_moves == 0:
			await self.status_message.edit(content='<@{.id}> has rolled **{}** and **cannot move!**'.format(self.turn, self.amount))
			await self.next_turn()
		else:
			if self.can_move_onto_board():
				await self.status_message.edit(content='<@{.id}> has rolled **{}** and has {} possible moves. Select a piece to move or move a piece onto the board.'.format(self.turn, self.amount, possible_moves))
				await self.status_message.add_reaction(DIGIT[0])
			else:
				await self.status_message.edit(content='<@{.id}> has rolled **{}** and has {} possible moves. Select a piece to move.'.format(self.turn, self.amount, possible_moves))

			for piece in (self.redPieces if self.turn == self.red else self.bluePieces):
				if piece.square is not None and piece.can_advance(self.amount):
					await self.status_message.add_reaction(DIGIT[piece.index])

			self.status = 'waiting for selection'

	def can_move_onto_board(self):
		if len([m for m in (self.redPieces if self.turn == self.red else self.bluePieces) if m.square == None]) == 0:
			return False

		start = self.redSpawnSquare if self.turn == self.red else self.blueSpawnSquare
		for i in range(self.amount-1):
			start = start.next

		if start.marker is not None:
			return False

		return True

	async def move_onto_board(self):
		marker = [m for m in (self.redPieces if self.turn == self.red else self.bluePieces) if m.square == None][0]
		marker.square = self.blueSpawnSquare if self.turn == self.blue else self.redSpawnSquare
		for i in range(self.amount-1):
			marker.square = marker.square.next
		marker.square.marker = marker

	async def attempt_advance(self, pieceNumber):
		markers = [m for m in (self.redPieces if self.turn == self.red else self.bluePieces) if m.index == pieceNumber]
		assert len(markers) == 1
		marker = markers[0]

		position = marker.square
		for i in range(self.amount):
			position = position.next
			if position == None:
				print('MOVE IMPOSSIBLE: Goes off the board')
				return

		# knock off enemy piece
		if position.marker is not None and position.marker.color == ('red' if self.turn == self.blue else 'blue'):
			position.marker.square = None

		if position.marker is not None and position.marker.color == ('red' if self.turn == self.red else 'blue'):
			print('MOVE IMPOSSIBLE: Cannot move onto same color')
			return

		position.marker = marker
		marker.square.marker = None
		marker.square = position



	async def determine_possible_moves(self, player, spaces):
		if spaces == 0: return 0

		rv = 0

		# Possible moves: Moving a piece onto the board, moving a piece off the board, moving a piece between two places, moving a piece onto an opposing piece
		if player == self.red:
			# moving a piece onto a board position
			if len([p for p in self.redPieces if p.square == None]) > 0:
				target = self.redSpawnSquare
				for i in range(spaces-1):
					target = target.next
				if target.marker == None:
					rv += 1

			# advancing a piece onto a free space or an opponent
			for piece in self.redPieces:
				if piece.square == None: continue
				if piece.can_advance(spaces):
					rv += 1

		elif player == self.blue:
			# moving a piece onto a board position
			if len([p for p in self.bluePieces if p.square == None]) > 0:
				target = self.blueSpawnSquare
				for i in range(spaces-1):
					target = target.next
				if target.marker == None:
					rv += 1

			# advancing a piece onto a free space or an opponent
			for piece in self.bluePieces:
				if piece.square == None: continue
				if piece.can_advance(spaces):
					rv += 1

		return rv

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
		if reaction.message.id in self.challenges:
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
				await instance.start()

		elif reaction.message.id in [game.status_message.id for game in self.games]:
			game = [game for game in self.games if game.status_message.id == reaction.message.id][0]

			if reaction.emoji == ROLL and game.turn.id == user.id and game.status == 'waiting for roll': # if roll was clicked by the person whose turn it is, and we're waiting for a roll
				await game.do_roll()

			elif reaction.emoji in DIGIT and game.turn.id == user.id and game.status == 'waiting for selection':
				if reaction.emoji == DIGIT[0]:
					await game.move_onto_board()
					await game.next_turn()
				else:
					await game.attempt_advance(DIGIT.index(reaction.emoji))
					await game.next_turn()



plugins = [TwentySquares]
commands = {
	'ts': {
		'usage': '@player1',
		'desc':  'Challenges another player to a game of Ur.',
		'example': '@Marco'
	}
}
