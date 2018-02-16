discord-alkaline-bot
======

My second generation discord chat bot, and successor to [discord-acid-bot](https://github.com/saucecode/discord-acid-bot). Requires Python 3.5+.

Run as: `$ python3 discordbot.py` and make sure a file `secrettoken` exists in the same directory containing the bot's login token.

### Modules

The bot loads commands and non-critical functionality from the `modules` directory. A valid and loadable module contains at least one *Plugin* class, and defines the variables `plugins` and `commands`. See `exampleplugin.py` for a barebones starting point.

Included modules are:

 - `essentials` with commands `ping, whoami, whois, define, ud`
 - `notifications` with commands `remind, tell` for sending messages on delays and when users are active.
 - `backup` with commands `createbackup, grabbackup` see backup section.
 - `voice` with commands for playing music over voice chat.
 - `sxde.reddit` with commands `rr, rrtop` for quickly retrieving random reddit posts.
 - `sxde.reactions` with commands 'reactionadd' as well as the detection for posting 'reactions'.
 - `sxde.world` with commands 'weather'


### Backup Module

This is a very specific-to-me problem. I run the bot on my personal machine, and I occasionally switch between Linux and Windows. This means running two separate instances of the bot with two different sets of config/data files. If a reminder, for example, gets set while I'm on Linux, it won't trigger if I switch to Windows, since the Windows instance doesn't have the reminder saved. To make this as painless™ as possible to remedy, I've written this backup module, with two core commands.

`createbackup` will create a backup, encrypt it, and upload it to the home channel, and state the message ID. The files generated in `data/` can be ignored/deleted.  
`grabbackup [backup message ID]` will download the backup from the backup message attachment, decrypt it, and put it in the base directory.

The backup is encrypted with salsa20 (`pip install salsa20`) using the bot's login token as the key, by default. Encryption is done because the uploaded backup can be retrieved by anyone with access to the home channel. It's probably a bad idea.

The home_channel is the channel which the bot considers it's home. It is specified in `data/settings.json` with they key `home_channel` and value of any TextChannel ID.

Plugins can specify which files they'd like to be backed up by setting a list `BACKUP_FILES`. When `createbackup` is called, the backup plugin will go through all loaded plugins, and save the files listed in these lists to the backup. See `modules/notifications.py`'s constructor for an example.
