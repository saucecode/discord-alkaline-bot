from ..alkalineplugin import AlkalinePlugin
import discord, aiohttp, time, json

class Weather(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.default_location = self.client.settings['default_location']
		self.apiKey = self.client.settings['openWeatherAPIKey']

		self.weather_last_retrieved = {self.default_location: 0}
		self.weather = {}
		self.forecast = {}

		self.name = 'Weather'
		self.version = '0.6'
		self.author = 'Julian'

	async def on_command(self, message: discord.Message, command : str, args : str):
		if command == 'weather' and len(args) == 0:

			now = time.time()
			location = self.default_location

			if now > self.weather_last_retrieved[location] + 10*60:
				self.weather_last_retrieved[location] = now
				print("Downloading weather data...")
				self.weather[location] = await self.do_weather_request(location)

			w = self.weather[location]

			await message.channel.send('{}, {}: {}. Temperature {} °C / {} K. Humidity {}%. Sunrise is at {} and sunset is at {}'.format( w['name'], w['sys']['country'], w['weather'][0]['description'], int(w['main']['temp']-273.15), w['main']['temp'], w['main']['humidity'], time.ctime(w['sys']['sunrise']).split(' ')[3], time.ctime(w['sys']['sunset']).split(' ')[3]
			))

	async def do_weather_request(self, location):
		async with aiohttp.ClientSession() as session:
			async with session.get('http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(location, self.apiKey)) as resp:
				return await resp.json()


plugins = [Weather]
commands = {
	'weather': {
		'desc':  'Prints out the current weather.'
	}
}
