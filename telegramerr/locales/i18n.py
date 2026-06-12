import json
import os
from telegramerr.config import settings

def load_translations(lang: str) -> dict:
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, f"{lang}.json")
    if not os.path.exists(file_path):
        file_path = os.path.join(base_dir, "en.json") # fallback
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

translations = load_translations(settings.BOT_LANGUAGE)

def t(key: str, **kwargs) -> str:
    text = translations.get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
