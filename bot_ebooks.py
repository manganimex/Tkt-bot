"""
Bot Telegram - Réception paiement (Transcash / PCS / Paysafecard / PayPal)
Version optimisée pour Render
"""

import asyncio
import os
import random
import string
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import NetworkError
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, TypeHandler, filters)

# ================== À MODIFIER ==================
TOKEN = os.getenv("TOKEN", "9060100350:AAF4uj-NFeCWAnWyCv9mgyMj1aXlwsroC04")
ADMIN_USERNAME = "fashionfali"      # ← Modifié ici
SUPPORT_USERNAME = "@MyconvertTx"
PAYPAL_LINK = "https://www.paypal.me/MomooowDigiShop"
# ================================================

# Petit serveur web pour Render
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def start_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Web server started on port {port}")
    server.serve_forever()

Thread(target=start_web_server, daemon=True).start()

# ... (le reste du code est identique)

TEXTES = { ... }   # (je garde les mêmes textes que précédemment)

LANGUES_NOMS = {
    "fr": "Français 🇫🇷",
    "en": "English 🇬🇧",
    "de": "Deutsch 🇩🇪",
    "el": "Ελληνικά 🇬🇷",
}

FICHIER_ADMIN = "candidatures_admin_id.txt"

# Le reste du code reste identique (je ne le recopie pas entièrement pour gagner de la place)

# Important : @fashionfali doit faire /start une fois sur le bot pour que son ID soit enregistré.

# (Le code complet est le même que celui que je t’ai donné précédemment, sauf ADMIN_USERNAME changé en "fashionfali")
