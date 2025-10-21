import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id_) for id_ in os.getenv("ADMIN_IDS", "").split(",") if id_.strip()]

# Owner contacts
OWNER_PHONE = os.getenv("OWNER_PHONE", "+380123456789")
OWNER_TELEGRAM = os.getenv("OWNER_TELEGRAM", "@owner")
OWNER_INSTAGRAM = os.getenv("OWNER_INSTAGRAM", "https://instagram.com/owner")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

# Pricing
RETAIL_PRICE = 55  # грн за литр (розница)
WHOLESALE_PRICE = 52  # грн за литр (опт)
WHOLESALE_THRESHOLD = 100  # литров для оптовой цены

# Referral bonus
REFERRAL_BONUS = 50  # грн бонус за приглашение

# Languages
LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "uk": "🇺🇦 Українська"
}

DEFAULT_LANGUAGE = "ru"