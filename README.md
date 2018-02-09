discord-alkaline-bot
======

My second generation discord chat bot, and successor to [discord-acid-bot](https://github.com/saucecode/discord-acid-bot).

Run as: `$ python3 discordbot.py` and make sure a file `secrettoken` exists in the same directory containing the bot's login token.

### Modules

The bot loads commands and non-critical functionality from the `modules` directory. A valid and loadable module contains at least one *Plugin* class, and defines the variables `plugins` and `commands`. See `exampleplugin.py` for a barebones starting point.

Included modules are:

 - `essentials` with commands `ping, whoami, whois, define, ud`
 - `notifications` with commands `remind, tell` for sending messages on delays and when users are active.
 - `sxde.reddit` with commands `rr, rrtop` for quickly retrieving random reddit posts.
 - `sxde.reactions` with commands 'reactionadd' as well as the detection for posting 'reactions'.
