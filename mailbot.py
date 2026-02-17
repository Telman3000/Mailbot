import os
from pyrogram import Client, filters
from imap_tools import MailBox
from dotenv import load_dotenv
import resend

# Load ENV
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USER = int(os.getenv("ALLOWED_USER"))

EMAIL = os.getenv("EMAIL")          # используется для IMAP
PASSWORD = os.getenv("PASSWORD")    # используется для IMAP
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

IMAP_SERVER = "mail.innopolis.ru"

# Init Resend
resend.api_key = RESEND_API_KEY

# Bot
app = Client(
    "mail_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# START
@app.on_message(filters.command("start") & filters.user(ALLOWED_USER))
async def start_handler(client, message):
    await message.reply(
        "🤖 Mail Bot запущен!\n\n"
        "Команды:\n"
        "/inbox — последние 5 писем\n"
        "/send email subject text — отправить письмо"
    )

# INBOX (через IMAP)
@app.on_message(filters.command("inbox") & filters.user(ALLOWED_USER))
async def get_mail(client, message):
    try:
        with MailBox(IMAP_SERVER, 993).login(
            EMAIL,
            PASSWORD,
            initial_folder="INBOX"
        ) as mailbox:

            emails = list(mailbox.fetch(limit=5, reverse=True))

            if not emails:
                await message.reply("Inbox пуст.")
                return

            text = "📥 Последние письма:\n\n"

            for mail in emails:
                text += f"От: {mail.from_}\n"
                text += f"Тема: {mail.subject}\n"
                text += f"Дата: {mail.date}\n"
                text += "-" * 30 + "\n"

            await message.reply(text)

    except Exception as e:
        await message.reply(f"Ошибка IMAP: {e}")

# SEND (через Resend API)
@app.on_message(filters.command("send") & filters.user(ALLOWED_USER))
async def send_mail(client, message):
    try:
        parts = message.text.split(" ", 3)

        if len(parts) < 4:
            await message.reply("Формат: /send email subject text")
            return

        to_email = parts[1]
        subject = parts[2]
        body = parts[3]

        resend.Emails.send({
            "from": "onboarding@resend.dev",  # для теста
            "to": [to_email],
            "subject": subject,
            "text": body,
        })

        await message.reply("✅ Письмо отправлено через Resend!")

    except Exception as e:
        await message.reply(f"Ошибка SEND: {e}")

# BLOCK OTHERS
@app.on_message(~filters.user(ALLOWED_USER))
async def block_others(client, message):
    await message.reply("⛔ Доступ запрещён.")

app.run()
