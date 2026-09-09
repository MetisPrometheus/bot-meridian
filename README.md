# Meridian timezone bot

A personal Discord bot displaying US Pacific time on the left and Norway time on the right,
updated every minute: `🇺🇸 HH:MM | 🇳🇴 HH:MM`. Pacific uses `America/Los_Angeles`
and Norway uses `Europe/Oslo`; Python's timezone database handles daylight saving time.

## Hetzner hosting

The bot runs directly on the shared Hetzner box as `meridian-bot.service`.
Systemd starts it at boot and restarts it after a crash. It needs no web server,
public port, database, Render service or GitHub keepalive pings.

Meridian is hosted on Hetzner. The former Render service is suspended, and the
GitHub Actions keepalive workflow has been removed.

```bash
# Clone this repository to /opt/projects/meridian, then provision:
sudo bash /opt/projects/iw-infra/setup.sh meridian

# In an interactive terminal, paste the existing bot token at the hidden prompt:
sudo python3 /opt/projects/meridian/deploy/set-token.py
sudo systemctl start meridian-bot.service
sudo systemctl status meridian-bot.service
sudo journalctl -u meridian-bot.service -n 30
```

The token lives in `/etc/meridian/discord-token` (root-only, mode 0600).
Systemd passes it through `LoadCredential`; it is never committed. Without that
file, the enabled service safely skips startup. The shared provisioner also
creates its standard environment file and unused database roles; the bot does
not use a database. The service has a 128 MB memory cap.

The suspended Render instance is retained only as a rollback option. Do not
resume it while the Hetzner service is running; two instances would compete to
set the same Discord presence. The old Render configuration is available in
Git history.

To deploy later updates, pull the reviewed code, install `requirements.txt` into
`venv/`, run the tests, then restart `meridian-bot.service`.

```bash
venv/bin/python -m unittest discover -s tests -v
sudo systemctl restart meridian-bot.service
```

## Local development

Python 3.11+ is required. Install `requirements.txt` into a virtual environment,
provide `DISCORD_TOKEN` through your local secret manager, and run `python bot.py`.
No health endpoint or ping process is needed. The presence loop starts once per
login rather than spawning another loop for each Discord reconnect.
