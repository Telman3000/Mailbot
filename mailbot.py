import os
from pyrogram import Client, filters
from imap_tools import MailBox
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import ssl

# Load .env
load_dotenv()

# Telegram credentials
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
ALLOWED_USER = int(os.getenv("ALLOWED_USER"))

# Email credentials
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

IMAP_SERVER = "mail.innopolis.ru"
SMTP_SERVER = "mail.innopolis.ru"

# Bot
app = Client(
    "mail_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
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

# INBOX
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

# SEND
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

        msg = EmailMessage()
        msg["From"] = EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        context = ssl.create_default_context()

        server = smtplib.SMTP_SSL(
            SMTP_SERVER,
            465,
            timeout=15,
            context=context
        )

        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()

        await message.reply("✅ Письмо отправлено!")

    except Exception as e:
        await message.reply(f"Ошибка SMTP: {e}")

# Block others
@app.on_message(~filters.user(ALLOWED_USER))
async def block_others(client, message):
    await message.reply("⛔ Доступ запрещён.")


app.run()
