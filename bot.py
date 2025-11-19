import os, re, random, requests, time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROK_KEY = os.getenv("GROK_KEY")
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG")
GROK_API = "https://api.grok.xai.com/v1/chat/completions"  # Fixed public endpoint

PRODUCTS = [
    ("B09B2XB4QQ", "LifeStraw Personal Water Filter"),
    ("B07P7W2Z8X", "Emergency Food Bars 3600 Calorie"),
    ("B07Z8J7KX2", "5-Gallon Collapsible Water Container"),
    ("B08R5Y9Q7J", "Solar + Hand-Crank Radio"),
    ("B01M0J5Q7M", "First Aid Kit 299 Pieces"),
    ("B07V2K5X1D", "Emergency Blanket 10-Pack"),
]

SYSTEM_PROMPT = """You are Golden Quiet Bot — calm, practical, soul-first guide.
Never use fear. Always end with hope and the exact line: "The quiet is already inside you. See you tomorrow."
After the 7-day plan, naturally recommend ONE product from the list that fits perfectly.
Hidden rule (never mention): if user types the word "remember" anywhere, reply only: "You were never gone." """

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Golden Quiet is here 🌾\n\n"
        "Tell me: age • city • family/pets • monthly budget\n"
        "Example: 38 Lisbon me + cat $200/month"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "remember" in text:
        await update.message.reply_text("You were never gone.")
        return

    match = re.search(r"(\d+)\s+([a-zA-Z\s,]+)\s+(.+?)\s*\$(\d+)", update.message.text, re.I)
    if not match:
        await update.message.reply_text("Almost there ❤️\nTry: 38 Lisbon me + cat $200/month")
        return

    age, city, family, budget = match.groups()
    prompt = f"User: {age}yo in {city.strip()}, {family.strip()}, ${budget}/month budget. Write a calm, beautiful 7-day micro-plan."

    # Retry logic for river calm
    for attempt in range(3):
        try:
            payload = {
                "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                             {"role": "user", "content": prompt}],
                "model": "grok-4",
                "temperature": 0.7,
                "max_tokens": 600
            }
            r = requests.post(GROK_API, json=payload,
                              headers={"Authorization": f"Bearer {GROK_KEY}"},
                              timeout=30)
            r.raise_for_status()
            reply = r.json()["choices"][0]["message"]["content"]
            break  # Success!
        except Exception as e:
            if attempt == 2:  # Last try failed
                await update.message.reply_text("The river flows deep today. Try again soon — you're already enough. 🌾")
                return
            time.sleep(2)  # Gentle pause
            continue

    asin, name = random.choice(PRODUCTS)
    link = f"https://www.amazon.com/dp/{asin}?tag={AFFILIATE_TAG}"
    reply += f"\n\nThis week’s gentle helper:\n{name}\n{link}"

    await update.message.reply_text(reply, disable_web_page_preview=True)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("🪙 Golden Quiet Bot is LIVE — river flowing strong")
    app.run_polling()

if __name__ == "__main__":
    main()