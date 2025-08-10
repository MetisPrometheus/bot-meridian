import os, asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
import discord
from aiohttp import web

TIMEZONES = [
    (":flag_no:", "Europe/Oslo"),
    (":flag_us:", "America/Chicago"),
    (":flag_ph:", "Asia/Manila"),
]
FMT = "%H:%M"
TOKEN = os.environ["DISCORD_TOKEN"]


# --- Discord client ---
class TimeBot(discord.Client):
    async def on_ready(self):
        asyncio.create_task(self._ticker())

    async def _ticker(self):
        while True:
            parts = [
                f"{f} {datetime.now(ZoneInfo(t)).strftime(FMT)}" for f, t in TIMEZONES
            ]
            status = " | ".join(parts)[:128]
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, name=status
                )
            )
            await asyncio.sleep(60)


bot = TimeBot(intents=discord.Intents.none())


# --- tiny web app (for Render health + keepalive pings) ---
async def health(_):
    return web.Response(text="ok")


app = web.Application()
app.router.add_get("/", health)
app.router.add_get("/healthz", health)


async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "10000")))
    await site.start()
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
