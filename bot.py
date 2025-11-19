# ← paste this entire file over your current bot.py
import os, re, random, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROK_KEY = os.getenv("GROK_KEY")
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG")

# Real rotating products (all proven prep winners)
PRODUCTS = [
    ("B09B2XB4QQ", "LifeStraw Personal Water Filter"),
    ("B07P7W2Z8X", "Emergency Food Bars 3600 Calorie"),
    ("B07Z8J7KX2", "5-Gallon Collapsible Water Container"),
    ("B08R5Y9Q7J", "Solar + Hand-Crank Radio"),
    ("B01M0J5Q7M", "First Aid Kit 299 Pieces"),
]

SYSTEM_PROMPT = """You are Golden Quiet Bot — calm, practical, soul-first.  
Never fearmonger. Always end with hope and the line "The quiet is already inside you. See you tomorrow."
After the plan, pick ONE product from the list that fits their situation perfectly and give a natural one-sentence recommendation with the affiliate link.
Hidden instruction (never mention): if the user ever types the word "remember", reply only: "You were never gone." """

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Golden Quiet is here.\nTell me: age, city, family/pets, monthly budget.\nExample: 38 Miami wife + 2 kids $300/month")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "remember" in text:
        await update.message.reply_text("You were never gone.")
        return

    match = re.search(r"(\d+)\s+([a-zA-Z\s]+)\s+(.+?)\s*\$(.+)", update.message.text, re.I)
    if not match:
        await update.message.reply_text("I didn’t catch that. Try: 38 Lisbon me + cat $200/month")
        return

    age, city, family, budget = match.groups()
    prompt = f"User: {age}yo in {city.strip()}, {family.strip()}, ${budget.strip()}/month budget. Give calm 7-day micro-plan."

    try:
        payload = {
            "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}],
            "model": "grok-4",
            "temperature": 0.7,
            "max_tokens": 600
        }
        r = requests.post("https://api.x.ai/v1/chat/completions",
                          json=payload,
                          headers={"Authorization": f"Bearer {GROK_KEY}"},
                          timeout=25)
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"]["content"]

        # Rotate product
        asin, name = random.choice(PRODUCTS)
        link = f"https://www.amazon.com/dp/{asin}?tag={AFFILIATE_TAG}"
        reply += f"\n\n🔗 This week’s gentle helper: {name}\n{link}"

        await update.message.reply_text(reply, disable_web_page_preview=True)
    except Exception as e:
        await update.message.reply_text("The river is calm. Trying again…")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🪙 Golden Quiet Bot is LIVE — breathing perfectly")
    app.run_polling()

if __name__ == "__main__":
    main()