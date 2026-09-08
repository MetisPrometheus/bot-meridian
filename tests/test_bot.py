import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import discord
from bot import TimeBot, timezone_status


class StatusTests(unittest.TestCase):
    def test_winter_and_summer_offsets(self):
        self.assertEqual(timezone_status(datetime(2026, 1, 1, 12, tzinfo=timezone.utc)), "07:00 | 13:00")
        self.assertEqual(timezone_status(datetime(2026, 7, 1, 12, tzinfo=timezone.utc)), "08:00 | 14:00")


class LifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_repeated_ready_does_not_spawn_tickers(self):
        bot = TimeBot(intents=discord.Intents.none())
        bot._connection.user = Mock(id=123)
        with patch.object(bot.ticker, "start") as start:
            await bot.setup_hook()
            await bot.on_ready()
            await bot.on_ready()
            start.assert_called_once()
        await bot.close()

    async def test_presence_is_sent_after_ready(self):
        bot = TimeBot(intents=discord.Intents.none())
        bot.wait_until_ready = AsyncMock()
        bot.change_presence = AsyncMock()
        with patch('bot.timezone_status', return_value='12:00 | 18:00'):
            await bot.ticker()
        bot.wait_until_ready.assert_awaited_once()
        kwargs = bot.change_presence.call_args.kwargs
        self.assertEqual(kwargs['status'], discord.Status.online)
        self.assertEqual(kwargs['activity'].name, '12:00 | 18:00')
        await bot.close()
