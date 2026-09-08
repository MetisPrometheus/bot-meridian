# Meridian timezone bot

A personal Discord bot displaying Chicago, Oslo and Manila times in its status,
updated every minute. Python's timezone database handles daylight saving time.

## Hetzner hosting

The bot runs directly on the shared Hetzner box as `meridian-bot.service`.
Systemd starts it at boot and restarts it after a crash. It needs no web server,
public port, database, Render service or GitHub keepalive pings.

Deployment files are prepared for Hetzner. Cutover requires installing the bot
token and verifying the live Discord status before retiring the old Render host.

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

For cutover, suspend the old Render service before starting this instance, then
check that Meridian is online in Discord and its times advance across a minute.
Retire Render and the legacy Actions pinger only after that check. The legacy
`render.yaml` and pinger remain temporarily for rollback; do not re-enable them
while the Hetzner instance is running.

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
