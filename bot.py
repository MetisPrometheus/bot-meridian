"""Meridian's timezone presence, hosted as a systemd service."""
import logging
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

TIMEZONES = [("🇺🇸", "America/Toronto"), ("🇳🇴", "Europe/Oslo")]


def timezone_status(now=None):
    now = now or datetime.now(ZoneInfo("UTC"))
    return " | ".join(
        f"{flag} {now.astimezone(ZoneInfo(zone)):%H:%M}"
        for flag, zone in TIMEZONES
    )


class TimeBot(discord.Client):
    async def setup_hook(self):
        # setup_hook runs once at login; on_ready can repeat after reconnects.
        self.ticker.start()

    async def on_ready(self):
        logging.info("Logged in as %s (%s)", self.user, self.user.id)

    @tasks.loop(seconds=60)
    async def ticker(self):
        await self.wait_until_ready()
        status = timezone_status()
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(type=discord.ActivityType.playing, name=status),
        )
        logging.info("Presence sent: %s", status)

    @ticker.error
    async def ticker_error(self, error):
        logging.error("Presence loop failed", exc_info=(type(error), error, error.__traceback__))
        # Close the client so systemd starts a fresh process instead of leaving
        # a connected bot whose timezone display never advances.
        await self.close()

    async def close(self):
        self.ticker.cancel()
        await super().close()


def read_token():
    if token := os.environ.get("DISCORD_TOKEN"):
        return token.strip()
    return (Path(os.environ["CREDENTIALS_DIRECTORY"]) / "discord-token").read_text().strip()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    TimeBot(intents=discord.Intents.none()).run(read_token(), log_handler=None)
