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
#dictionarycom

import requests, re, urllib

def get_definitions(word):
	html = requests.get('http://www.dictionary.com/browse/%s' % word).text
	if 'There are no results for: ' in html: return []
	definition_block = html.split('<div class="def-list">')[1].split('</section>')[0]
	definitions = definition_block.split('<div class="def-set">')[1:]
	strings = [ re.sub(' +',' ', re.sub('<[^<]+?>', '', i.split('<div class="def-content">')[1].split('</div>')[0].strip()).strip()) for i in definitions ]
	return strings

def get_urban_definitions(word):
	url = 'http://api.urbandictionary.com/v0/define?term=%s' % urllib.parse.quote(word)
	dat = requests.get(url).json()
	return dat['list']
