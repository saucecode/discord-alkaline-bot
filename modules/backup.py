from .alkalineplugin import AlkalinePlugin
import discord, hashlib, io

from zipfile import ZipFile

class Backup(AlkalinePlugin):

	def __init__(self, client):
		self.client = client

		self.BACKUP_FILES = ['data/settings.json', 'data/permissions.json']
		self.backup_key = self.client.settings['backup_key']

		self.name = 'BackupOperator'
		self.version = '0.5'
		self.author = 'Julian'

	async def on_command(self, message, command, args):
		if command == 'createbackup':
			if not 'home_channel' in self.client.settings:
				await message.channel.send('No home channel specified. Set `home_channel` to a channel ID in `data/settings.json`.')
				return

			home_channel = self.client.get_channel(self.client.settings['home_channel'])
			await home_channel.send('Starting backup...')

			# gather relevant files, create the zip file
			with ZipFile('data/backup.zip', 'w') as zf:
				for mod in self.client.plugins:
					for plugin in self.client.plugins[mod]:
						if hasattr(plugin, 'BACKUP_FILES') and type(plugin.BACKUP_FILES) == list:
							for fname in plugin.BACKUP_FILES:
								zf.write(fname)

			# encrypt the zipfile
			with open('data/backup.zip', 'rb') as fi:
				with open('data/backup.zip.salsa20', 'wb') as fo:
					fo.write( self.encrypt_bytes(fi.read()) )

			# upload the encrypted zipfile
			with open('data/backup.zip.salsa20', 'rb') as f:
				backup_message = await home_channel.send(file=discord.File(f))

			await home_channel.send('Backup message ID: %i' % backup_message.id)



		elif command == 'grabbackup':
			if not 'home_channel' in self.client.settings:
				await message.channel.send('No home channel specified. Set `home_channel` to a channel ID in `data/settings.json`.')
				return

			home_channel = self.client.get_channel(self.client.settings['home_channel'])
			backup_message_id = int(args.split(' ')[0])

			# find the mesage with the encrypted zipfile attachment
			messages = [a for a in await home_channel.history(limit=10, around=discord.utils.snowflake_time(backup_message_id)).flatten() if a.id == backup_message_id]

			if not len(messages) == 1:
				await message.channel.send('Could not find this backup (Found %i candidates)' % len(messages))
				return

			backup_message = messages[0]

			if not len(backup_message.attachments) == 1:
				await message.channel.send('Found the message but could not find 1 attachment.')
				return

			# download zipfile, decrypt, and put it in working directory
			with open('fetched_backup.zip','wb') as f:
				backup_bytes_encrypted = io.BytesIO()
				await backup_message.attachments[0].save(backup_bytes_encrypted)
				f.write(self.encrypt_bytes( backup_bytes_encrypted.getvalue() ))

			await message.channel.send('Fetched backup.')



	def encrypt_bytes(self, data):
		from salsa20 import Salsa20_xor as salsa20
		key = hashlib.sha256(self.backup_key.encode('utf-8')).digest()
		IV = b'0' * 8
		return salsa20(data, IV, key)



plugins = [Backup]
commands = {'createbackup':{'perms':['op']}, 'grabbackup':{'perms':['op']}}
