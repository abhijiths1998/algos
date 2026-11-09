# Routine reminder bot

Sends your daily routine (wake-up, meditation, gym, gaming, class, journal,
reading, lights out) to you on Telegram at the right time. Weekdays and
weekends have different schedules. Everything lives in `schedule.yaml`.

It runs on GitHub Actions, so no computer has to stay on.

## Setup (about 5 minutes)

### 1. Create your Telegram bot

1. In Telegram, open **@BotFather** (it has a blue verified tick) and send `/newbot`.
2. Give it a display name (e.g. `My Routine`) and a username ending in `bot`
   (e.g. `abhi_routine_bot`).
3. BotFather replies with a **token** like `123456789:AAH...`. Keep it private:
   anyone with it can control your bot.
4. Tap the link BotFather gives you to open your new bot, and press **Start**
   (or send `/start`). A bot can't message you until you do this.

### 2. Add the token to GitHub

In the repo, go to **Settings → Secrets and variables → Actions → New
repository secret** and add `TELEGRAM_BOT_TOKEN` with the token.

### 3. Get your chat ID

Go to **Actions → Routine reminders → Run workflow**, choose mode `chatid`
and run it. Open the finished run and expand the **Run bot** step. It shows a
line like `TELEGRAM_CHAT_ID=123456789`.

Add that number as a second secret, `TELEGRAM_CHAT_ID`.

### 4. Test

Run the workflow again with mode `test`. You should get
"✅ Reminder bot is set up" in Telegram. From then on reminders arrive by
themselves.

## Good to know

- **Timing:** GitHub starts scheduled runs late, often by 5–20 minutes. To
  make up for it, each run also sends reminders due in the next 10 minutes
  (`send_early_minutes` in `schedule.yaml`). Each message starts with its real
  time, like `🕘 9:00 PM`, so you know when it's for. Reminders then arrive
  anywhere from about 10 minutes early to a few minutes late. Raise the
  setting if they're still late, or lower it if they're too early. The bot
  never sends the same reminder twice and skips anything over 45 minutes old.
- **60-day pause:** GitHub pauses scheduled workflows in repos with no commits
  for 60 days. If reminders stop, re-enable the workflow on the Actions tab.
- **Until both secrets are set**, scheduled runs skip quietly instead of
  failing every 5 minutes.

## Changing the schedule

Edit `schedule.yaml` and commit. Each reminder is:

```yaml
- time: "21:00"          # 24-hour, in the timezone at the top of the file
  days: weekdays         # weekdays | weekends | daily | [mon, wed, fri]
  message: "💻 FDE class starts now."
```

The schedule assumes class is 9–11 PM every day and office ends around
7:30 PM. If your class only runs on some days, change `days` on the class
reminders to a list like `[mon, wed, fri]`.

## Running it on your own machine instead

For on-the-minute reminders, run it on an always-on machine (Raspberry Pi,
VPS) instead of GitHub Actions:

```bash
cd reminder_bot
pip install -r requirements.txt
cp .env.example .env      # fill in TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
python bot.py chatid      # finds your chat ID after you've sent the bot /start
python bot.py test        # sends a test message
python bot.py run         # runs forever
```

`reminder-bot.service` keeps it running with systemd (instructions inside).
If you do this, disable the GitHub workflow so you don't get each reminder twice.

Other commands: `python bot.py today` lists today's reminders without sending.

## Other providers

The bot can also send over WhatsApp via CallMeBot, Twilio or Meta's Cloud
API. Set `REMINDER_PROVIDER` and that provider's keys (see `.env.example`).
