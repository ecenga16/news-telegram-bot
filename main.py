import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from telegram.ext import Application, MessageHandler, filters
from telegram import InputFile

BOT_TOKEN = os.getenv("BOT_TOKEN")

def extract_image_and_title(url):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    # Merr titullin
    title = None
    title_meta = soup.find("meta", property="og:title")
    if title_meta and title_meta.get("content"):
        title = title_meta["content"]
    else:
        title = soup.find("title").text if soup.find("title") else "Lajm"

    # Rrjedha për imazhe
    img_url = None

    og_img = soup.find("meta", property="og:image")
    if og_img and og_img.get("content"):
        img_url = og_img["content"]

    if not img_url:
        tw_img = soup.find("meta", attrs={"name": "twitter:image"})
        if tw_img and tw_img.get("content"):
            img_url = tw_img["content"]

    if not img_url:
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            img_url = img_tag["src"]

    # Rregullo URL relative
    if img_url:
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        elif img_url.startswith("/"):
            base = url.split("/")[0] + "//" + url.split("/")[2]
            img_url = base + img_url

    return title, img_url

def generate_image(title, img_url):
    # Merr imazhin
    img_data = requests.get(img_url).content
    img = Image.open(BytesIO(img_data)).convert("RGB").resize((900, 600))

    # Krijo canvas më të madh për titull
    canvas = Image.new("RGB", (900, 1200), (150, 30, 30))
    canvas.paste(img, (0, 0))

    draw = ImageDraw.Draw(canvas)

    # Ngarko font të madh
    try:
        font = ImageFont.truetype("arial.ttf", 40)  # mund të ndryshosh font-in
    except:
        font = ImageFont.load_default()

    # Tekst i wrap-uar
    import textwrap
    wrapper = textwrap.TextWrapper(width=25)
    wrapped_title = "\n".join(wrapper.wrap(title.upper()))

    # Pozicioni i tekstit
    text_x = 20
    text_y = 650

    # Vendos tekst me outline për qartësi
    for offset in [(1,1), (-1,-1), (1,-1), (-1,1)]:
        draw.text((text_x + offset[0], text_y + offset[1]), wrapped_title, font=font, fill="black")
    draw.text((text_x, text_y), wrapped_title, font=font, fill="white")

    buf = BytesIO()
    canvas.save(buf, format="JPEG")
    buf.seek(0)
    return buf

async def handler(update, context):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("Dërgo link lajmi.")
        return

    title, img_url = extract_image_and_title(url)

    if not img_url:
        await update.message.reply_text("Nuk gjeta foto te lajmit ❌")
        return

    image = generate_image(title, img_url)

    await update.message.reply_photo(InputFile(image, "news.jpg"))

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handler))
app.run_polling()
