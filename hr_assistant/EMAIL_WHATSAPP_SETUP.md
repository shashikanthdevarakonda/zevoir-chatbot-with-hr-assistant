# Setting Up Real Email & WhatsApp Sending

By default, the HR Assistant only _shows_ the info in the chat with a
"✅ sent" confirmation — it doesn't actually deliver anything anywhere.
Follow the steps below to make it send for real.

---

## Part 1: Real Email (Gmail)

You need ONE Gmail account to send from (it can be your personal Gmail —
it does NOT need to belong to the recipient).

1. Go to your Google Account: https://myaccount.google.com/security
2. Turn on **2-Step Verification** if it isn't already on (required for App Passwords).
3. Go to https://myaccount.google.com/apppasswords
4. Under "App name", type something like `HR Assistant` and click **Create**.
5. Google will show you a **16-character password** (looks like `abcd efgh ijkl mnop`).
   Copy it — you won't be able to see it again.
6. In your project folder (same folder as `app.py`), create a new file named
   exactly `.env` (copy `.env.example` and rename it, or create it fresh).
7. Fill in:
   ```
   GMAIL_ADDRESS=xyz@gmail.com
   GMAIL_APP_PASSWORD=umclgrhrkldbghcz
   ```
   (paste the 16-character password with NO spaces)

That's it for email — no Gmail API, no OAuth, no billing.

---

## Part 2: Real WhatsApp (Twilio Sandbox — free)

1. Create a free account at https://www.twilio.com/try-twilio
2. Once logged in, go to the Twilio Console dashboard: https://console.twilio.com
   You'll see your **Account SID** and **Auth Token** right there.
3. In your `.env` file, add:
   ```
   TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
   TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
   TWILIO_WHATSAPP_FROM=whatsapp:+your_sandbox_number
   ```
4. Go to Twilio Console → Messaging → Try it out → **Send a WhatsApp message**
   (or search "WhatsApp Sandbox" in the console search bar).
5. It'll show a join code like `join happy-tiger`. From the phone number you
   want to RECEIVE messages on (e.g. your own number, 0000000000), send that
   exact message to the WhatsApp number shown (usually +222222222222).
6. You'll get a confirmation reply on WhatsApp — you're now in the sandbox
   and can receive messages from the bot.

**Important limitation:** Twilio's free sandbox can only send WhatsApp
messages to numbers that have joined the sandbox this way. Every number you
want to test with (yours, a friend's, etc.) has to send that join code once.
This restriction goes away only if you apply for a paid, approved WhatsApp
Business sender — not needed for testing/demoing the assignment.

---

## Part 3: Install the new dependency & restart

```
pip install -r requirements.txt
python app.py
```

Look for these lines when it starts (not strictly required, but confirms
the .env file was found):

```
✅ RAG loaded
✅ HR Assistant loaded (...)
```

Then test in the widget:

```
can you send sick leave data to my mail YOUR_REAL_EMAIL@gmail.com
```

Check that inbox — you should receive an actual email within a few seconds.

```
can you send sick leave data to my whatsapp number YOUR_NUMBER
```

(only works if that number already sent the Twilio join code as above)

---

## If something fails

The bot will tell you exactly what's wrong instead of silently failing —
e.g. "Email not sent — GMAIL_ADDRESS / GMAIL_APP_PASSWORD are not set" or
"WhatsApp message failed to send: ...". Common issues:

- `.env` file not in the same folder as `app.py`
- App Password copied with spaces still in it
- 2-Step Verification not enabled on the Gmail account (App Passwords won't
  even show up as an option until it is)
- The recipient WhatsApp number never sent the Twilio join code
- Gmail blocking the sign-in as suspicious — check that account's inbox for
  a security alert email and approve it if so
