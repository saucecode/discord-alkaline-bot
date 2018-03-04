"""
    Alkaline Bot - a modular Discord chat bot
    Copyright (C) 2018    Julian Cahill

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from ..alkalineplugin import AlkalinePlugin
from ..sailortalk import filthy_verb
import discord, io, time, random, os
from PIL import Image, ImageDraw, ImageFont

random.seed(os.urandom(100))

BOARD_SIZE = 400,300
CHECKMARK = "\u2705"
CROSSMARK = "\u274E"
ROLL =  "\U0001f3b2"
DIGIT = ["\U00002b50", "\U00000031\U000020e3", "\U00000032\U000020e3", "\U00000033\U000020e3", "\U00000034\U000020e3", "\U00000035\U000020e3", "\U00000036\U000020e3", "\U00000037\U000020e3", "\U00000038\U000020e3", "\U00000039\U000020e3"]

"""

	WARNING: HERE BE DRAGONS
	This was written in one sitting with the goal of getting it to work.
	It is not pretty, nor has anything resembling intelligent design.
	It works, and I'm not sure how.

	Redesigns welcome.

"""

class Square:
	def __init__(self, next=None):
		self.next = next
		self.last = False
		self.special = False
		self.marker = None
		self.neutral = False

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
			if prev_target == None:
				break
			target = target.next


			if type(target) == list:
				target = target[0] if self.color == 'red' else target[1]

		if target == None and prev_target == None:
			print('can\'t off the board unless you hit an exact')
			return False

		if target == None:
			if prev_target is not None and prev_target.last:
				return True
			return False

		if target.marker == None:
			return True

		if not target.marker.color == self.color and not target.neutral:
			return True

		return False


class TwentySquaresGame:
	def __init__(self, parent, playerRed : discord.User , playerBlue : discord.User, chan : discord.TextChannel ):
		self.parent = parent
		self.client = parent.client

		self.last_board_message = None
		self.last_status_message = None

		self.red = playerRed
		self.blue = playerBlue
		self.chan = chan

		self.turn = self.red
		self.status = None
		self.status_message = None
		self.amount = 0 # the last rolled amount

		self.redPieces = [Marker('red', i+1) for i in range(7)]
		self.bluePieces = [Marker('blue', i+1) for i in range(7)]
		self.redPoints = 0
		self.bluePoints = 0
		self.POINTS_LIMIT = 7

		# GENERATE A GRAPH OF SQUARES
		topSquare = Square()
		act = topSquare
		for i in range(7):
			act.next = Square()
			act = act.next
		bottomSquare = act
		topSquare.next.next.next.special = True
		topSquare.next.next.next.neutral = True

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

		r = self.redBottomSquare
		b = self.blueBottomSquare
		for i in range(6,8)[::-1]:
			draw.rectangle( [4 + i*48, 300-16-48-48-48, 4 + i*48 + 48, 300-16-48-48], fill='black', outline='blue' )
			draw.rectangle( [4 + i*48, 300-16-48, 4 + i*48 + 48, 300-16], fill='black', outline='red' )

			if b.marker is not None:
				draw.ellipse( [4 + i*48+16, 300-16-48-48-48+16, 4 + i*48 + 48-16, 300-16-48-48-16], outline='white', fill='blue' )
				draw.text( (4 + i*48+16+4, 300-16-48-48-48+16+4), str(b.marker.index) )

			if r.marker is not None:
				draw.ellipse( [4 + i*48+16, 300-16-48+16, 4 + i*48 + 48-16, 300-16-16], outline='white', fill='red' )
				draw.text( (4 + i*48+16+4, 300-16-48+16+4), str(r.marker.index) )

			r = r.next
			b = b.next

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

		if self.last_board_message:
			await self.last_board_message.delete()

		self.last_board_message = await self.chan.send(
			'Game between <@{}> ({}) and <@{}> ({})'.format(self.red.id, self.redPoints, self.blue.id, self.bluePoints),
			file=discord.File( image_bytes.getbuffer(), filename='{}.png'.format(int(time.time())) )
		)

	async def start(self):
		self.turn = random.choice( [self.red, self.blue] )
		self.status = 'waiting for roll'
		self.status_message = await self.chan.send('<@{.id}> rolls first. Click to roll.'.format(self.turn))
		await self.status_message.add_reaction( ROLL )
		self.last_status_message = self.status_message

	def check_win_condition(self):
		return self.redPoints == self.POINTS_LIMIT or self.bluePoints == self.POINTS_LIMIT

	async def next_turn(self):
		if self.check_win_condition():
			winner = self.red if self.redPoints == self.POINTS_LIMIT else self.blue
			await self.populate_board()
			await self.chan.send('**WINNER!** <@{.id}> has {} <@{.id}> by winning this 4500 year old game.'.format(winner, filthy_verb(), self.red if winner == self.blue else self.blue))

			self.parent.games.remove(self)
		else:
			self.turn = self.red if self.turn.id == self.blue.id else self.blue
			self.status = 'waiting for roll'
			await self.populate_board()
			if self.last_status_message:
				await self.last_status_message.delete()
			self.status_message = await self.chan.send('<@{.id}>\'s turn to roll. Click to roll.'.format(self.turn))
			await self.status_message.add_reaction( ROLL )
			self.last_status_message = self.status_message

	async def do_roll(self):
		if not self.status == 'waiting for roll': return
		self.amount = sum( [random.randint(0,1) for i in range(4)] )
		await self.status_message.remove_reaction( ROLL, self.client.user )
		possible_moves = await self.determine_possible_moves(self.turn, self.amount)

		print('A roll of {} has {} possible moves'.format(self.amount, possible_moves))

		if possible_moves == 0:
			await self.status_message.edit(content='<@{.id}> has rolled **{}** and **cannot move!**'.format(self.turn, self.amount), delete_after=3.0)
			self.last_status_message = None
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

		if marker.square.special:
			print('ROSETTE!')
			self.turn = self.red if self.turn == self.blue else self.blue

	async def attempt_advance(self, pieceNumber):
		markers = [m for m in (self.redPieces if self.turn == self.red else self.bluePieces) if m.index == pieceNumber]
		assert len(markers) == 1
		marker = markers[0]

		position = marker.square
		last_position = position
		for i in range(self.amount):
			if last_position == None:
				break
			last_position = position

			position = position.next
			if position == None and last_position == None:
				print('MOVE IMPOSSIBLE: Goes off the board')
				return

			if type(position) == list:
				position = position[0] if self.turn == self.red else position[1]

		if position == None and not last_position == None and last_position.last:
			marker.square.marker = None
			marker.square = None

			if self.turn == self.red:
				self.redPieces.remove(marker)
				self.redPoints += 1
			elif self.turn == self.blue:
				self.bluePieces.remove(marker)
				self.bluePoints += 1

			print('PIECE OFF THE BOARD')

			return

		# knock off enemy piece
		if position.marker is not None and position.marker.color == ('red' if self.turn == self.blue else 'blue'):
			if position.neutral:
				print('MOVE IMPOSSIBLE: Cannot move onto the neutral tile')
				return
			position.marker.square = None

		if position.marker is not None and position.marker.color == ('red' if self.turn == self.red else 'blue'):
			print('MOVE IMPOSSIBLE: Cannot move onto same color')
			return

		position.marker = marker
		marker.square.marker = None
		marker.square = position

		if marker.square.special:
			print('ROSETTE!')
			self.turn = self.red if self.turn == self.blue else self.blue



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
		if command == '20squares':
			if args == 'rules':
				with open('data/20squares.png','rb') as f:
					await message.channel.send('''The Royal Game of Ur (aka Twenty Squares) is a 2 player (red vs blue) race game.\n\nYou have seven pieces, and you must get them all the way to the end.\nYou can knock off enemy pieces if you land on them, unless they're on a yellow square. Landing on a yellow gets you another turn.\nOnly one piece may be on a square at a time.\nThe roll is equivalent to flipping four coins and counting the heads.\n\nTo challenge someone, type `\\20squares @someone`''', file=discord.File(f))
				return
			elif not len(message.mentions) == 1:
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
	'20squares': {
		'usage': '@player1',
		'desc':  'Challenges another player to a game of Ur.',
		'example': '@Marco'
	}
}
