# WhatsApp routine reminder bot

Sends your daily routine (wake-up, meditation, gym, gaming, class, journal,
reading, lights out) to your WhatsApp at the right time. Weekdays and
weekends have different schedules. Everything lives in `schedule.yaml`.

## 1. Pick how messages get sent

| Provider | Cost | Setup | Catch |
|---|---|---|---|
| **CallMeBot** (default) | Free | 2 minutes | Personal use only, can only message your own number. Messages come from CallMeBot's number. |
| **Twilio** | Pay per message (sandbox is free) | 10 minutes | In the sandbox you must re-send the join code every 72 hours, and free-form messages only work within 24 hours of your last message to it. |
| **Meta WhatsApp Cloud API** | Free tier | 30+ minutes, needs a Meta business app | Free-form text only works within 24 hours of your last message. For daily reminders you'd need approved message templates. |

For reminding yourself, **CallMeBot is the right choice**.

### CallMeBot setup

1. Open the WhatsApp page on callmebot.com and save the bot's phone number
   listed there to your contacts.
2. Send it this exact message on WhatsApp: `I allow callmebot to send me messages`
3. It replies with your API key.

## 2. Configure

```bash
cd whatsapp_reminder
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `CALLMEBOT_PHONE` (e.g. `919876543210`) and `CALLMEBOT_APIKEY`.

## 3. Check it works

```bash
python bot.py today   # prints today's reminders, sends nothing
python bot.py test    # sends one test message to your WhatsApp
```

## 4. Run it

```bash
python bot.py run
```

### Option A: GitHub Actions (no machine needed)

`.github/workflows/whatsapp-reminders.yml` checks every 5 minutes and sends
whatever came due. It's free for public repos, but GitHub often starts these
runs 5–20 minutes late, so reminders can arrive late.

1. In the repo on GitHub, go to **Settings → Secrets and variables → Actions**
   and add two repository secrets: `CALLMEBOT_PHONE` and `CALLMEBOT_APIKEY`.
2. The workflow must be on the default branch, because scheduled workflows
   only run from there.
3. Go to **Actions → WhatsApp reminders → Run workflow** (mode `test`) to
   send a test message.

GitHub pauses scheduled workflows in repos with no commits for 60 days. If
reminders stop, re-enable the workflow on the Actions tab.

### Option B: your own always-on machine

The bot has to keep running to send reminders, so run it on something that's
always on:

- **A Raspberry Pi, old laptop or home server:** use `reminder-bot.service`
  (instructions are inside the file) so it starts on boot and restarts if it
  crashes.
- **A free cloud VM** (e.g. Oracle Cloud free tier, or a small VPS): same
  systemd setup.
- **Quick and dirty:** `nohup python bot.py run > bot.log 2>&1 &`

If the machine sleeps and wakes up later, reminders older than 10 minutes are
skipped instead of all arriving at once.

## Changing the schedule

Edit `schedule.yaml` and restart the bot. Each reminder is:

```yaml
- time: "21:00"          # 24-hour, in the timezone at the top of the file
  days: weekdays         # weekdays | weekends | daily | [mon, wed, fri]
  message: "💻 FDE class starts now."
```

The schedule assumes class is 9–11 PM every day and office ends around
7:30 PM. If your class only runs on some days, change `days` on the class
reminders to a list like `[mon, wed, fri]`.
