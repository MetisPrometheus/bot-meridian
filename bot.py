import os, asyncio, logging
from datetime import datetime
from zoneinfo import ZoneInfo
import discord
from aiohttp import web

TIMEZONES = ["America/Chicago", "Europe/Oslo", "Asia/Manila"]
FMT = "%H:%M"
TOKEN = os.environ["DISCORD_TOKEN"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


class TimeBot(discord.Client):
    async def on_ready(self):
        logging.info("Logged in as %s (%s)", self.user, self.user.id)
        asyncio.create_task(self._ticker())

    async def _ticker(self):
        while True:
            try:
                parts = [datetime.now(ZoneInfo(t)).strftime(FMT) for t in TIMEZONES]
                status = " | ".join(parts)[:128]
                await self.change_presence(
                    status=discord.Status.online,  # make sure it shows as Online
                    activity=discord.Activity(
                        type=discord.ActivityType.playing, name=status
                    ),
                )
                logging.info("Presence set: %s", status)
            except Exception:
                logging.exception("Ticker iteration failed")
            await asyncio.sleep(60)


bot = TimeBot(intents=discord.Intents.none())


# --- tiny web app (keepalive + state) ---
async def health(_):
    data = {
        "bot_ready": bot.is_ready(),
        "latency_sec": getattr(bot, "latency", None),
        "time_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    logging.info("Health hit: %s", data)
    return web.json_response(data)


app = web.Application()
app.router.add_get("/", health)
app.router.add_get("/healthz", health)


async def run_bot_forever():
    while True:
        try:
            await bot.start(TOKEN, reconnect=True)
        except Exception:
            logging.exception("Bot crashed; restarting in 10s")
            await asyncio.sleep(10)


async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "10000")))
    await site.start()
    await run_bot_forever()


if __name__ == "__main__":
    asyncio.run(main())
