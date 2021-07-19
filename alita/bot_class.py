# Copyright (C) 2020 - 2021 Divkix. All rights reserved. Source code available under the AGPL.
#
# This file is part of Alita_Robot.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from uvloop import install

# Install uvloop to make bot faster
install()

from platform import python_version
from threading import RLock
from time import gmtime, strftime, time

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from pyromod.helpers import ikb

from alita import (
    API_HASH,
    APP_ID,
    BOT_TOKEN,
    LOG_DATETIME,
    LOGFILE,
    LOGGER,
    MESSAGE_DUMP,
    NO_LOAD,
    UPTIME,
    WORKERS,
    get_self,
    load_cmds,
)
from alita.database import MongoDB
from alita.plugins import all_plugins
from alita.tr_engine import lang_dict
from alita.utils.paste import paste

INITIAL_LOCK = RLock()

# Check if MESSAGE_DUMP is correct
if MESSAGE_DUMP == -100 or not str(MESSAGE_DUMP).startswith("-100"):
    raise Exception(
        "Please enter a vaild Supergroup ID, A Supergroup ID starts with -100",
    )


class Alita(Client):
    """Starts the Pyrogram Client on the Bot Token when we do 'python3 -m alita'"""

    def __init__(self):
        name = self.__class__.__name__.lower()

        super().__init__(
            "tessia_bot",
            bot_token=BOT_TOKEN,
            plugins=dict(root=f"{name}.plugins", exclude=NO_LOAD),
            api_id=APP_ID,
            api_hash=API_HASH,
            workers=WORKERS,
        )

    async def start(self):
        """Start the bot."""
        await super().start()

        meh = await get_self(self)  # Get bot info from pyrogram client
        LOGGER.info("Starting bot...")

        startmsg = await self.send_message(MESSAGE_DUMP, "<i>Starting Bot...</i>")

        # Load Languages
        lang_status = len(lang_dict) >= 1
        LOGGER.info(f"Loading Languages: {lang_status}\n")

        # Show in Log that bot has started
        LOGGER.info(
            f"Pyrogram v{__version__} (Layer - {layer}) started on {meh.username}",
        )
        LOGGER.info(f"Python Version: {python_version()}\n")

        # Get cmds and keys
        cmd_list = await load_cmds(await all_plugins())

        LOGGER.info(f"Plugins Loaded: {cmd_list}")

        # Send a message to MESSAGE_DUMP telling that the
        # bot has started and has loaded all plugins!
        await startmsg.edit_text(
            (
                f"<b><i>@{meh.username} started on Pyrogram v{__version__} (Layer - {layer})</i></b>\n"
                f"\n<b>Python:</b> <u>{python_version()}</u>\n"
                "\n<b>Loaded Plugins:</b>\n"
                f"<i>{cmd_list}</i>\n"
            ),
        )

        LOGGER.info("Bot Started Successfully!\n")

    async def stop(self):
        """Stop the bot and send a message to MESSAGE_DUMP telling that the bot has stopped."""
        runtime = strftime("%Hh %Mm %Ss", gmtime(time() - UPTIME))
        LOGGER.info("Uploading logs before stopping...!\n")
        with open(LOGFILE) as f:
            txt = f.read()
            neko, raw = await paste(txt)
        # Send Logs to MESSAGE_DUMP and LOG_CHANNEL
        await self.send_document(
            MESSAGE_DUMP,
            document=LOGFILE,
            caption=(
                "Bot Stopped!\n\n"
                f"Uptime: {runtime}\n"
                f"Logs for last run, pasted to [NekoBin]({neko}) as well as uploaded a file here.\n"
                f"<code>{LOG_DATETIME}</code>"
            ),
            reply_markup=ikb([[("Raw Logs", raw, "url")], [("Neko", neko, "url")]]),
        )
        if MESSAGE_DUMP:
            # LOG_CHANNEL is not necessary
            await self.send_document(
                MESSAGE_DUMP,
                document=LOGFILE,
                caption=f"Uptime: {runtime}\n[NekoBin]({neko})\n[Raw]({raw})",
            )
        await super().stop()
        MongoDB.close()
        LOGGER.info(
            f"""Bot Stopped.
            Logs have been uploaded to the MESSAGE_DUMP Group!
            Runtime: {runtime}s\n
        """,
        )
