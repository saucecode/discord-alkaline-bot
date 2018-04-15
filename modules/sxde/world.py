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
import discord, aiohttp, time, json

def epoch_to_timestamp(when):
	return time.strftime('%Y-%m-%d %H:%M', time.localtime(when))

def epoch_to_24htime(when):
	return time.strftime('%H:%M', time.localtime(when))

class Weather(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.default_location = self.client.settings['default_location']
		self.apiKey = self.client.settings.get('openWeatherAPIKey', None)
		self.wxApiKey = self.client.settings.get('checkWXAPIKey', None)

		self.last_retrieved = {'weather': {self.default_location: 0}, 'forecast': {self.default_location: 0}}
		self.weather = {}
		self.forecast = {}

		self.name = 'Weather'
		self.version = '0.6'
		self.author = 'Julian'

	async def on_command(self, message: discord.Message, command : str, args : str):
		if command == 'weather' and len(args) == 0 and self.apiKey:

			now = time.time()
			location = self.default_location
			weather_message = None

			if now > self.last_retrieved['weather'][location] + 10*60:
				self.last_retrieved['weather'][location] = now
				print("Downloading weather data...")
				weather_message = await message.channel.send('Downloading weather data...')
				self.weather[location] = await self.do_weather_request(location)

			w = self.weather[location]
			func = message.channel.send

			if weather_message:
				func = lambda x: weather_message.edit(content=x)

			await func('{}, {}: {}. Temperature {} °C. Humidity {}%. Wind {}° {} km/h. Sunrise {}. Sunset {}.'.format( w['name'], w['sys']['country'], w['weather'][0]['description'], int(w['main']['temp']-273.15), w['main']['humidity'], w['wind']['deg'], int(round(w['wind']['speed']*3.6)), epoch_to_24htime(w['sys']['sunrise']), epoch_to_24htime(w['sys']['sunset'])
			))

		elif command == 'forecast' and len(args) == 0 and self.apiKey:

			now = time.time()
			location = self.default_location
			forecast_message = None

			if now > self.last_retrieved['forecast'][location] + 10*60:
				self.last_retrieved['forecast'][location] = now
				print('Downloading forecast data...')
				forecast_message = await message.channel.send('Downloading forecast data...')
				self.forecast[location] = await self.do_forecast_request(location)

			w = self.forecast[location]
			func = message.channel.send

			if forecast_message:
				func = lambda x: forecast_message.edit(content=x)

			def stringify_forecast(data):
				return '{} {} Temperature {} °C / {} K. Humidity {}%'.format(epoch_to_timestamp(data['dt']), data['weather'][0]['description'], int(data['main']['temp']-273.15), int(data['main']['temp']), data['main']['humidity'] )

			output = [stringify_forecast(x) for x in w['list']]

			await func('24 hour forecast for {}, {}\n{}'.format(w['city']['name'], w['city']['country'], '\n'.join(output)))

		elif command == 'metar' and len(args.split(' ')) == 1 and self.wxApiKey:
			if not len(args.split(' ')[0]) == 4:
				await message.channel.send('Requires 4-letter ICAO code.')

			resp = await self.do_metar_request(args.split(' ')[0])
			await message.channel.send('`{}`'.format( resp['data'][0] ))


	async def do_weather_request(self, location):
		async with aiohttp.ClientSession() as session:
			async with session.get('http://api.openweathermap.org/data/2.5/weather?id={}&appid={}'.format(location, self.apiKey)) as resp:
				return await resp.json()

	async def do_forecast_request(self, location):
		async with aiohttp.ClientSession() as session:
			async with session.get('http://api.openweathermap.org/data/2.5/forecast?id={}&cnt=8&appid={}'.format(location, self.apiKey)) as resp:
				return await resp.json()

	async def do_metar_request(self, icao):
		async with aiohttp.ClientSession() as session:
			async with session.get('https://api.checkwx.com/metar/{}'.format(icao), headers={'X-API-Key': self.wxApiKey}) as resp:
				return await resp.json()


plugins = [Weather]
commands = {
	'weather': {
		'desc':  'Prints out the current weather.'
	},
	'forecast': {
		'desc': 'Prints out the 24 hour forecast.'
	},
	'metar': {
		'desc': 'Prints out METAR for a specified ICAO code',
		'usage': '[ICAO code]'
	}
}
