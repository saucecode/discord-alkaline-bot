from ..alkalineplugin import AlkalinePlugin
import random, aiohttp, time

LEFT_ARROW = '\u25C0'
TWISTED_ARROWS = '\U0001F500'
RIGHT_ARROW = '\u25B6'
REDDIT_CACHE = {}
EXPIRY_TIME = 600


class RollingMessage:
    def __init__(self, client, message, url, links, index=0):
        self.client = client
        self._message = message
        self.url = url
        self.links = links
        self.index = index

    @classmethod
    async def from_command(cls, client, msg, command, subreddit):
        endpoint = 'top/.json?t=all&limit=100' if command == 'rrtop' else '.json?limit=100'
        url = "https://reddit.com/r/{subreddit}/{endpoint}".format(subreddit=subreddit, endpoint=endpoint)
        message = await client.send_message(msg.channel, 'Requesting data...')
        links = await cls.fetch(url)
        instance = cls(client, message, url, links)
        await instance.update_message()
        return instance

    @property
    def item_text(self):
        return '{item[title]} | {item[url]}'.format(item=self.links[self.index].get('data'))

    async def update_message(self):
        self.links = await self.fetch(self.url)
        await self.client.edit_message(self._message, '{}/{} {}'.format(self.index + 1, len(self.links), self.item_text))
        await self.set_reactions()

    async def roll_next(self):
        self.index += 1
        await self.update_message()

    async def roll_previous(self):
        self.index -= 1
        await self.update_message()

    async def roll_random(self):
        self.index = random.randrange(len(self.links))
        await self.update_message()

    async def set_reactions(self):
        await self.client.clear_reactions(self._message)
        for emoji in [LEFT_ARROW, TWISTED_ARROWS, RIGHT_ARROW]:
            await self.client.add_reaction(self._message, emoji)

    @staticmethod
    async def fetch(url):
        now = time.time()
        cached_item = REDDIT_CACHE.get(url, None)
        if cached_item and now < cached_item['expiration']:
            print('Cache hit: ', url)
            return cached_item['content']
        print('Cache miss: ', url)
        async with aiohttp.ClientSession() as sesh, sesh.get(url, headers={'User-Agent': 'Discord-Alkaline-Bot'}) as resp:
                dat = await resp.json()
                REDDIT_CACHE[url] = dict(expiration=now+EXPIRY_TIME, content=dat['data']['children'])
                return REDDIT_CACHE[url]['content']

    def __getattr__(self, item):
        return getattr(self._message, item)


class Reddit(AlkalinePlugin):
    def __init__(self, client):
        self.client = client
        self.rolling_messages = {}
        self.name = 'Reddit'
        self.version = '0.1'
        self.author = 'Julian'

    async def on_command(self, msg, command, args):
            subreddit = args.strip()
            rolling_message = await RollingMessage.from_command(self.client, msg, command, subreddit)
            self.rolling_messages[rolling_message.id] = rolling_message

    async def on_reaction_add(self, reaction, user):
        rolling_message = self.rolling_messages.get(reaction.message.id, None)
        if rolling_message is None:
            return
        options = {
            LEFT_ARROW: rolling_message.roll_previous,
            RIGHT_ARROW: rolling_message.roll_next,
            TWISTED_ARROWS: rolling_message.roll_random
        }
        action = options[reaction.emoji]
        return await action()


plugins = [Reddit]
commands = {
    'rr': {
        'usage': '[subreddit]',
        'desc': 'Retrieve a random reddit post from [subreddit].'
    },
    'rrtop': {
        'usage': '[subreddit]',
        'desc': 'Retrieve a random all-time best reddit post from [subreddit].'
    }
}
