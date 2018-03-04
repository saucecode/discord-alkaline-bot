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
import random

__firsts =  'shit fuck muffin dumb piss muppet mother goat whore ass pussy cock fugly swamp cake tart old tasteless'.split(' ')
__seconds = 'cunt bitch tard face fuck stain stick muppet fucker ass face bandit eater fart lard'.split(' ')
__singles = [
	'cuck', 'muppet', 'sex offender', 'cumslut', 'reasonable human being', 'buffoon', 'ignoramus', 'dense mother fucker',
	'FOOL!', 'mouth breather', 'imbecile', 'waste of space', 'withered old hag', 'statistician'
]

def sailor_word():
	if random.random() > len(__singles) / ( (len(__firsts) + len(__seconds)) ):
		f = random.choice(__firsts)
		s = random.choice([x for x in __seconds if not x == f])
		return '%s%s' % (f, s)
	else:
		return 'you %s' % random.choice(__singles)

def filthy_verb():
	return random.choice([
		'fucking destroyed',
		'publicly humiliated',
		'decimated',
		'shat on',
		'butt fucked',
		'shamed',
		'induced vomiting in',
		'stolen the boyfriend of',
		'stolen the girlfriend of',
		'completely fucking owned',
		'pwned'
	])
