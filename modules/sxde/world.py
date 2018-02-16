from ..alkalineplugin import AlkalinePlugin
import discord, aiohttp, time, json

class Weather(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.default_location = self.client.settings['default_location']
		self.apiKey = self.client.settings['openWeatherAPIKey']

		self.last_retrieved = {'weather': {self.default_location: 0}, 'forecast': {self.default_location: 0}}
		self.weather = {}
		self.forecast = {}

		self.name = 'Weather'
		self.version = '0.6'
		self.author = 'Julian'

	async def on_command(self, message: discord.Message, command : str, args : str):
		if command == 'weather' and len(args) == 0:

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

			await func('{}, {}: {}. Temperature {} °C / {} K. Humidity {}%. Sunrise is at {} and sunset is at {}'.format( w['name'], w['sys']['country'], w['weather'][0]['description'], int(w['main']['temp']-273.15), w['main']['temp'], w['main']['humidity'], time.ctime(w['sys']['sunrise']).split(' ')[3], time.ctime(w['sys']['sunset']).split(' ')[3]
			))

		elif command == 'forecast' and len(args) == 0:

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
				return '{} {} Temperature {} °C / {} K. Humidity {}%'.format(time.ctime(data['dt']), data['weather'][0]['description'], int(data['main']['temp']-273.15), data['main']['temp'], data['main']['humidity'] )

			output = [stringify_forecast(x) for x in w['list']]

			await func('24 hour forecast for {}, {}\n{}'.format(w['city']['name'], w['city']['country'], '\n'.join(output)))

	async def do_weather_request(self, location):
		async with aiohttp.ClientSession() as session:
			async with session.get('http://api.openweathermap.org/data/2.5/weather?id={}&appid={}'.format(location, self.apiKey)) as resp:
				return await resp.json()

	async def do_forecast_request(self, location):
		async with aiohttp.ClientSession() as session:
			async with session.get('http://api.openweathermap.org/data/2.5/forecast?id={}&cnt=8&appid={}'.format(location, self.apiKey)) as resp:
				return await resp.json()


plugins = [Weather]
commands = {
	'weather': {
		'desc':  'Prints out the current weather.'
	},
	'forecast': {
		'desc': 'Prints out the 24 hour forecast.'
	}
}
