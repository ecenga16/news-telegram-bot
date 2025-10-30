import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from telegram.ext import Application, MessageHandler, filters
from telegram import InputFile

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def handler(update, context):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("Dërgo link lajmi.")
        return

    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("meta", property="og:title")
    title = title["content"] if title else "Lajm"

    img = soup.find("meta", property="og:image")
    img_url = img["content"] if img else None

    if not img_url:
        await update.message.reply_text("Nuk gjeta foto.")
        return

    img_data = requests.get(img_url).content
    img = Image.open(BytesIO(img_data)).convert("RGB").resize((900, 600))

    canvas = Image.new("RGB", (900, 1200), (150, 30, 30))
    canvas.paste(img, (0, 0))

    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((20, 650), title[:70], font=font, fill="white")

    buf = BytesIO()
    canvas.save(buf, format="JPEG")
    buf.seek(0)

    await update.message.reply_photo(InputFile(buf, "news.jpg"))

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handler))
app.run_polling()
