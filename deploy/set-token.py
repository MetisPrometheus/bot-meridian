"""Run with sudo from an interactive terminal. Never pass a token as an argument."""
import getpass
import os
from pathlib import Path

if os.geteuid() != 0:
    raise SystemExit("Run with sudo.")
token = getpass.getpass("Meridian Discord bot token (hidden): ").strip()
if not token or any(c.isspace() for c in token):
    raise SystemExit("Token must be nonempty and contain no whitespace.")
path = Path("/etc/meridian/discord-token")
path.parent.mkdir(mode=0o750, exist_ok=True)
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as f:
    os.fchmod(f.fileno(), 0o600)
    os.fchown(f.fileno(), 0, 0)
    f.write(token + "\n")
print("Token saved privately. Start meridian-bot.service when ready to cut over.")
