discord-alkaline-bot
======

My second generation discord chat bot, and successor to [discord-acid-bot](https://github.com/saucecode/discord-acid-bot). Requires Python 3.5+.

Run as: `$ python3 discordbot.py` and make sure a file `secrettoken` exists in the same directory containing the bot's login token. If you make changes to the bot and are running it on a public server, you must modify "source" in settings.json to link to the modified source code (as per the AGPLv3 License).

### Modules

The bot loads commands and non-critical functionality from the `modules` directory. A valid and loadable module contains at least one *Plugin* class, and defines the variables `plugins` and `commands`. See `exampleplugin.py` for a barebones starting point.

Included modules are:

 - `essentials` with commands `ping, whoami, whois, define, ud`
 - `notifications` with commands `remind, tell` for sending messages on delays and when users are active.
 - `backup` with commands `createbackup, grabbackup` see backup section.
 - `voice` with commands for playing music over voice chat.
 - `sxde.reddit` with commands `rr, rrtop` for quickly retrieving random reddit posts.
 - `sxde.reactions` with commands 'reactionadd' as well as the detection for posting 'reactions'.
 - `sxde.world` with commands 'weather, forecast'
 - `games.twentysquares` implementation of the 2-player game of Ur. Type '\20squares rules' to see how to play it.

### Per-Server Plugin Whitelist

The bot was designed primarily for single-server operation. The bot will run fine on multiple servers, save for the voice commands not working *across* servers. So far, only one feature has been implemented to make multi-server operation managable: A `per-server-plugin-whitelist` setting in the settings.json.

```
settings.json

{
	...,

	"per-server-plugin-whitelist": {
		"417059418010812416": ["games.twentysquares", "sxde.reddit"]
	}
}
```

By default, all modules and command are accessible to users of all servers the bot is connected to. If a server is listed in this list as shown, however, only the modules attached to it can be used. In this case, the server 417059418010812416 may use *only* the twenty squares game and the reddit-browsing commands.

### Core Commands

These commands are part of the core code (not a plugin), their behavior is defined directly in discordbot.py, and they can only be run with the 'admin' permission (defined in the bot, not the server role). The core commands and their usages are as follows.

 - `\reloadall` Reload all currently loaded modules.
 - `\loadmodule [module name]` Attempts to load plugins from the specified module.
 - `\reloadmodule [module name]` Attempts to reload an already loaded module.
 - `\unloadmodule [module name]` Attempts to unload a loaded module (disabling its commands).
 - `\modules` Prints a list of all the loaded modules and their plugins.

Module names are relative to the modules directory. A `[module name]` like `sxde.world` represents `modules/sxde/world.py`. One like `essentials` represents `modules/essentials.py`. Remember that not every source file in the modules directory has plugins. Some of them are utilities, such as `sailortalk.py`, which is used by a veritable variety of plugin modules.

### settings.json

Here is a quick rundown of what you ought to put in this file. The only required option here is the `command_prefix`. Everything else can be left blank.

The `home_channel` and `backup_key` keys are used by the backup module and are only required to make backups. `home_channel` is the channel ID to upload the backup to, and `backup_key` is the encrypt/decrypt key on the backup.

`openWeatherAPIKey` is an API key used by the weather module. The weather module uses [Open Weather Map](http://openweathermap.org/) as its source, and requires a free account to get an API key. `default_location` is also specific to the weather command, and all weather queries are made for that location. 2193734 is the key for Auckland, New Zealand, which is where my server's users are based. Try [here for a full list](http://openweathermap.org/help/city_list.txt).

```
{
	"home_channel": 304959901376053248,
	"command_prefix": "\\",
	"default_location": 2193734,
	"openWeatherAPIKey": "redacted",
	"backup_key": "secret",

	"per-server-plugin-whitelist": {
		"417059418010812416": ["games.twentysquares", "sxde.reddit"]
	}
}
```

### sxde.reddit module

This is the reddit-browsing module, which lets you quickly browse subreddits (primarily images) with your friends from the chat room. As of 2018-03-04, the official Discord client does not support playing videos hosted on reddit.com (specifically v.redd.it) in the same way that it supports playing gfycat webm videos. To remedy this, the sxde.reddit module will download, rescale, and post a v.redd.it link's video into the chat whenever one is posted.

Here is [a webm of this behavior](https://gfycat.com/QuaintDopeyGannet) in action. It was implemented on [2018-03-04 in this commit](https://github.com/saucecode/discord-alkaline-bot/commit/301a1f54404d0c2dca5a898a727d2059f6ac370d). The behavior is also triggered whenever someone posts a reddit video link *on it's own*.

The downscaled videos should **NOT** be used or shared outside of a Discord chat. They are lower quality than their originals (literally 400x224). If you spread them around, then low quality versions of perfectly decent HD content could start diluting The Internet.


### Backup Module

This is a very specific-to-me problem. I run the bot on my personal machine, and I occasionally switch between Linux and Windows. This means running two separate instances of the bot with two different sets of config/data files. If a reminder, for example, gets set while I'm on Linux, it won't trigger if I switch to Windows, since the Windows instance doesn't have the reminder saved. To make this as painless™ as possible to remedy, I've written this backup module, with two core commands.

`createbackup` will create a backup, encrypt it, and upload it to the home channel, and state the message ID. The files generated in `data/` can be ignored/deleted.  
`grabbackup [backup message ID]` will download the backup from the backup message attachment, decrypt it, and put it in the base directory.

The backup is encrypted with salsa20 (`pip install salsa20`) using the bot's login token as the key, by default. Encryption is done because the uploaded backup can be retrieved by anyone with access to the home channel. It's probably a bad idea.

The home_channel is the channel which the bot considers it's home. It is specified in `data/settings.json` with they key `home_channel` and value of any TextChannel ID.

Plugins can specify which files they'd like to be backed up by setting a list `BACKUP_FILES`. When `createbackup` is called, the backup plugin will go through all loaded plugins, and save the files listed in these lists to the backup. See `modules/notifications.py`'s constructor for an example.
