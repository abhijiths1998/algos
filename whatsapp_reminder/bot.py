"""WhatsApp reminder bot for a daily routine.

Reads reminders from schedule.yaml and sends each one to your WhatsApp
at its scheduled time.

Usage:
    python bot.py today      # list today's reminders (sends nothing)
    python bot.py test       # send one test message to check your setup
    python bot.py run        # run forever and send reminders on time
    python bot.py once       # send what's due since the last run, then exit
                             # (used by the GitHub Actions workflow)

Configuration comes from environment variables, or from a .env file next
to this script. See .env.example and README.md.
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

HERE = Path(__file__).resolve().parent
DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DAY_GROUPS = {
    "daily": set(range(7)),
    "weekdays": {0, 1, 2, 3, 4},
    "weekends": {5, 6},
}
TICK_SECONDS = 20
# If the machine was asleep, reminders older than this are skipped, not sent late.
GRACE = timedelta(minutes=10)
# GitHub Actions schedules often run late, so allow more slack in 'once' mode.
ONCE_GRACE = timedelta(minutes=45)


# ---------------------------------------------------------------- config

def load_dotenv(path):
    """Minimal .env loader: KEY=value lines, # comments. Real env vars win."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(f"Missing setting {name}. Add it to .env (see .env.example).")
    return value


def parse_days(days):
    if isinstance(days, str):
        key = days.lower()
        if key in DAY_GROUPS:
            return DAY_GROUPS[key]
        days = [days]
    result = set()
    for d in days:
        d = str(d).lower()[:3]
        if d not in DAY_NAMES:
            raise ValueError(f"Unknown day {d!r}")
        result.add(DAY_NAMES.index(d))
    return result


def load_schedule(path):
    data = yaml.safe_load(Path(path).read_text())
    tz = ZoneInfo(data.get("timezone", "Asia/Kolkata"))
    reminders = []
    for i, r in enumerate(data.get("reminders", []), 1):
        try:
            hh, mm = (int(x) for x in str(r["time"]).split(":"))
            if not (0 <= hh < 24 and 0 <= mm < 60):
                raise ValueError("time out of range")
            reminders.append({
                "hour": hh,
                "minute": mm,
                "days": parse_days(r.get("days", "daily")),
                "message": str(r["message"]).strip(),
            })
        except (KeyError, ValueError) as e:
            sys.exit(f"schedule.yaml: reminder #{i} is invalid ({e}): {r}")
    reminders.sort(key=lambda r: (r["hour"], r["minute"]))
    return tz, reminders


def occurrences(reminders, day, tz):
    """Datetimes (with message) of reminders that fall on the given date."""
    for r in reminders:
        if day.weekday() in r["days"]:
            at = datetime(day.year, day.month, day.day, r["hour"], r["minute"], tzinfo=tz)
            yield at, r["message"]


# ---------------------------------------------------------------- senders

def http(method, url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def send_callmebot(text):
    query = urllib.parse.urlencode({
        "phone": env("CALLMEBOT_PHONE"),
        "apikey": env("CALLMEBOT_APIKEY"),
        "text": text,
    })
    status, body = http("GET", f"https://api.callmebot.com/whatsapp.php?{query}")
    # CallMeBot answers 200 even for some errors, so check the body too.
    if status != 200 or "error" in body.lower():
        raise RuntimeError(f"CallMeBot: {status} {body[:200]}")


def send_twilio(text):
    sid, token = env("TWILIO_ACCOUNT_SID"), env("TWILIO_AUTH_TOKEN")
    data = urllib.parse.urlencode({
        "From": env("TWILIO_FROM"),  # e.g. whatsapp:+14155238886
        "To": env("TWILIO_TO"),      # e.g. whatsapp:+919876543210
        "Body": text,
    }).encode()
    auth = base64.b64encode(f"{sid}:{token}".encode()).decode()
    http("POST", f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
         data, {"Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded"})


def send_meta(text):
    payload = {
        "messaging_product": "whatsapp",
        "to": env("META_TO"),
        "type": "text",
        "text": {"body": text},
    }
    http("POST", f"https://graph.facebook.com/v21.0/{env('META_PHONE_NUMBER_ID')}/messages",
         json.dumps(payload).encode(),
         {"Authorization": f"Bearer {env('META_TOKEN')}",
          "Content-Type": "application/json"})


SENDERS = {"callmebot": send_callmebot, "twilio": send_twilio, "meta": send_meta}


def get_sender():
    name = os.environ.get("WHATSAPP_PROVIDER", "callmebot").strip().lower()
    if name not in SENDERS:
        sys.exit(f"WHATSAPP_PROVIDER must be one of {', '.join(SENDERS)}, not {name!r}")
    return SENDERS[name]


def send_with_retry(sender, text, attempts=3):
    for n in range(1, attempts + 1):
        try:
            sender(text)
            return True
        except (urllib.error.URLError, RuntimeError, OSError) as e:
            detail = e.read().decode("utf-8", "replace")[:200] if isinstance(e, urllib.error.HTTPError) else ""
            log(f"send failed (attempt {n}/{attempts}): {e} {detail}")
            if n < attempts:
                time.sleep(5 * n)
    return False


def log(msg):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


# ---------------------------------------------------------------- commands

def cmd_today(schedule_path):
    tz, reminders = load_schedule(schedule_path)
    today = datetime.now(tz).date()
    print(f"Reminders for {today:%A %d %b} ({tz.key}):")
    for at, msg in occurrences(reminders, today, tz):
        print(f"  {at:%H:%M}  {msg}")


def cmd_test(schedule_path):
    load_schedule(schedule_path)  # validate the file as well
    sender = get_sender()
    ok = send_with_retry(sender, "✅ Reminder bot is set up. You'll get your routine reminders here.")
    log("test message sent" if ok else "test message FAILED")
    sys.exit(0 if ok else 1)


def cmd_run(schedule_path):
    tz, reminders = load_schedule(schedule_path)
    sender = get_sender()
    log(f"bot started: {len(reminders)} reminders, timezone {tz.key}")
    last = datetime.now(tz)
    while True:
        time.sleep(TICK_SECONDS)
        now = datetime.now(tz)
        # Look at both dates in case the window crosses midnight.
        days = {last.date(), now.date()}
        due = sorted(
            (at, msg)
            for day in days
            for at, msg in occurrences(reminders, day, tz)
            if last < at <= now
        )
        for at, msg in due:
            if now - at > GRACE:
                log(f"skipped stale {at:%H:%M} reminder (machine was asleep?)")
                continue
            if send_with_retry(sender, msg):
                log(f"sent {at:%H:%M}: {msg}")
        last = now


def cmd_once(schedule_path, state_path):
    """Send whatever came due since the previous run, then exit.

    Meant for schedulers like GitHub Actions that start the bot every few
    minutes (and often late). The time of the last check is kept in a small
    state file so nothing is sent twice or missed between runs.
    """
    tz, reminders = load_schedule(schedule_path)
    sender = get_sender()
    now = datetime.now(tz)
    state = Path(state_path)
    try:
        last = datetime.fromisoformat(json.loads(state.read_text())["last_check"])
    except (OSError, ValueError, KeyError):
        last = now - timedelta(minutes=10)  # first run: don't replay the whole day
        log("no previous state, looking back 10 minutes")
    days = {last.astimezone(tz).date() + timedelta(days=i)
            for i in range((now.date() - last.astimezone(tz).date()).days + 1)}
    due = sorted(
        (at, msg)
        for day in days
        for at, msg in occurrences(reminders, day, tz)
        if last < at <= now
    )
    for at, msg in due:
        if now - at > ONCE_GRACE:
            log(f"skipped stale {at:%a %H:%M} reminder")
        elif send_with_retry(sender, msg):
            log(f"sent {at:%H:%M} ({(now - at).seconds // 60} min late): {msg}")
        else:
            log(f"FAILED {at:%H:%M}: {msg}")
    if not due:
        log("nothing due")
    state.write_text(json.dumps({"last_check": now.isoformat()}))


def main():
    load_dotenv(HERE / ".env")
    parser = argparse.ArgumentParser(description="WhatsApp routine reminder bot")
    parser.add_argument("command", choices=["run", "once", "test", "today"])
    parser.add_argument("--schedule", default=str(HERE / "schedule.yaml"))
    parser.add_argument("--state", default=str(HERE / "state.json"),
                        help="state file used by the 'once' command")
    args = parser.parse_args()
    if args.command == "once":
        cmd_once(args.schedule, args.state)
    else:
        {"run": cmd_run, "test": cmd_test, "today": cmd_today}[args.command](args.schedule)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("stopped")
