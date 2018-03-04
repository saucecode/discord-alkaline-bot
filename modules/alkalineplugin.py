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

import discord

class AlkalinePlugin:

	async def on_message(self, message : discord.Message):
		pass

	async def on_command(self, message : discord.Message, command : str, args : str):
		pass

	async def on_message_edit(self, before : discord.Message, after : discord.Message):
		pass

	async def on_reaction_add(self, reaction : discord.Reaction, user : discord.User):
		pass

	async def on_pm_command(self, message: discord.Message, command : str, args: str):
		pass
