"""
Bot Telegram - Réception paiement (Transcash / PCS / Paysafecard / PayPal)
Version optimisée pour Render (avec serveur web fictif)
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
ADMIN_ID = 8587257274
ADMIN_USERNAME = "fashionfali"
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

# Lance le serveur web en arrière-plan
Thread(target=start_web_server, daemon=True).start()

TEXTES = {
    "fr": {
        "bienvenue": "👋 Bienvenue !\n\nChoisis ton moyen de paiement :\n\nEn cas de problème : {support}",
        "demande_infos": "✅ Moyen choisi : <b>{moyen}</b>\n\nEnvoie tes informations :\n• Adresse crypto\n• Codes des coupons\n• Montant total\n• Photos (optionnel)\n\nTu peux envoyer <b>plusieurs messages</b>.\nQuand tu as tout envoyé, clique sur le bouton ci-dessous.",
        "demande_infos_paypal": "✅ Moyen choisi : <b>PayPal</b>\n\n⚠️ <b>Important :</b>\n• Paiement <b>entre proches uniquement</b>\n• Montant maximum : <b>1000€</b>\n• Si l’argent est suspendu (pas entre proches) → pas de notre ressort\n\n👉 Envoie l’argent ici :\n<b>{paypal_link}</b>\n\nEnsuite envoie :\n• Adresse crypto\n• Montant envoyé\n• Photo de preuve\n\nTu peux envoyer <b>plusieurs messages</b>.\nQuand tu as tout envoyé, clique sur le bouton ci-dessous.",
        "bouton_fini": "✅ J’ai fini d’envoyer",
        "recu": "✅ Bien reçu !\n\n📦 Numéro de demande : <b>{num}</b>\n\nOn a bien pris en compte toutes tes infos.\nTu reçois la crypto dans <b>maximum 1 heure</b> (souvent moins).\n\nEn cas de problème : {support}",
        "confirme": "✅ Transaction confirmée !\n\nLa crypto a été envoyée.\nMerci pour ta confiance 🙏\n\nEn cas de problème : {support}",
        "probleme": "❌ Problème avec ta demande.\n\nContacte le support : {support}",
        "support": "💬 Pour toute question, contacte {support}.",
    },
    "en": {
        "bienvenue": "👋 Welcome!\n\nChoose your payment method:\n\nIf anything goes wrong: {support}",
        "demande_infos": "✅ Method chosen: <b>{moyen}</b>\n\nSend your information:\n• Crypto address\n• Coupon codes\n• Total amount\n• Photos (optional)\n\nYou can send <b>multiple messages</b>.\nWhen you're done, click the button below.",
        "demande_infos_paypal": "✅ Method chosen: <b>PayPal</b>\n\n⚠️ <b>Important:</b>\n• Payment <b>between friends only</b>\n• Maximum amount: <b>1000€</b>\n• If money is suspended (not between friends) → not our responsibility\n\n👉 Send the money here:\n<b>{paypal_link}</b>\n\nThen send:\n• Crypto address\n• Amount sent\n• Payment proof photo\n\nYou can send <b>multiple messages</b>.\nWhen you're done, click the button below.",
        "bouton_fini": "✅ I'm done sending",
        "recu": "✅ Received!\n\n📦 Request number: <b>{num}</b>\n\nAll your information has been registered.\nYou will receive the crypto in <b>maximum 1 hour</b> (often less).\n\nIf anything goes wrong: {support}",
        "confirme": "✅ Transaction confirmed!\n\nThe crypto has been sent.\nThank you for your trust 🙏\n\nIf anything goes wrong: {support}",
        "probleme": "❌ Problem with your request.\n\nContact support: {support}",
        "support": "💬 For any question, contact {support}.",
    },
    "de": {
        "bienvenue": "👋 Willkommen!\n\nWähle deine Zahlungsmethode:\n\nBei Problemen: {support}",
        "demande_infos": "✅ Methode gewählt: <b>{moyen}</b>\n\nSende deine Informationen:\n• Crypto-Adresse\n• Gutscheincodes\n• Gesamtbetrag\n• Fotos (optional)\n\nDu kannst <b>mehrere Nachrichten</b> senden.\nWenn du fertig bist, klicke auf den Button unten.",
        "demande_infos_paypal": "✅ Methode gewählt: <b>PayPal</b>\n\n⚠️ <b>Wichtig:</b>\n• Zahlung nur unter Freunden\n• Maximaler Betrag: 1000€\n• Wenn Geld gesperrt wird (nicht unter Freunden) → nicht unsere Verantwortung\n\n👉 Sende das Geld hierhin:\n<b>{paypal_link}</b>\n\nDann sende:\n• Crypto-Adresse\n• Gesendeter Betrag\n• Zahlungsnachweis-Foto\n\nDu kannst <b>mehrere Nachrichten</b> senden.\nWenn du fertig bist, klicke auf den Button unten.",
        "bouton_fini": "✅ Fertig mit dem Senden",
        "recu": "✅ Erhalten!\n\n📦 Anfragenummer: <b>{num}</b>\n\nAlle deine Informationen wurden registriert.\nDu erhältst die Crypto in <b>maximal 1 Stunde</b> (oft weniger).\n\nBei Problemen: {support}",
        "confirme": "✅ Transaktion bestätigt!\n\nDie Crypto wurde gesendet.\nDanke für dein Vertrauen 🙏\n\nBei Problemen: {support}",
        "probleme": "❌ Problem mit deiner Anfrage.\n\nKontaktiere den Support: {support}",
        "support": "💬 Bei Fragen kontaktiere {support}.",
    },
    "el": {
        "bienvenue": "👋 Καλώς ήρθες!\n\nΕπίλεξε τον τρόπο πληρωμής:\n\nΣε περίπτωση προβλήματος: {support}",
        "demande_infos": "✅ Μέθοδος επιλέχθηκε: <b>{moyen}</b>\n\nΣτείλε τις πληροφορίες σου:\n• Διεύθυνση crypto\n• Κωδικοί κουπονιών\n• Συνολικό ποσό\n• Φωτογραφίες (προαιρετικό)\n\nΜπορείς να στείλεις <b>πολλά μηνύματα</b>.\nΌταν τελειώσεις, πάτησε το κουμπί παρακάτω.",
        "demande_infos_paypal": "✅ Μέθοδος επιλέχθηκε: <b>PayPal</b>\n\n⚠️ <b>Σημαντικό:</b>\n• Πληρωμή μόνο μεταξύ φίλων\n• Μέγιστο ποσό: 1000€\n• Αν μπλοκαριστούν τα χρήματα (όχι μεταξύ φίλων) → δεν είναι δική μας ευθύνη\n\n👉 Στείλε τα χρήματα εδώ:\n<b>{paypal_link}</b>\n\nΜετά στείλε:\n• Διεύθυνση crypto\n• Ποσό που έστειλες\n• Φωτογραφία απόδειξης\n\nΜπορείς να στείλεις <b>πολλά μηνύματα</b>.\nΌταν τελειώσεις, πάτησε το κουμπί παρακάτω.",
        "bouton_fini": "✅ Τελείωσα την αποστολή",
        "recu": "✅ Ελήφθη!\n\n📦 Αριθμός αιτήματος: <b>{num}</b>\n\nΌλες οι πληροφορίες σου καταγράφηκαν.\nΘα λάβεις τα crypto σε <b>μέγιστο 1 ώρα</b> (συχνά λιγότερο).\n\nΣε περίπτωση προβλήματος: {support}",
        "confirme": "✅ Η συναλλαγή επιβεβαιώθηκε!\n\nΤα crypto στάλθηκαν.\nΕυχαριστούμε για την εμπιστοσύνη 🙏\n\nΣε περίπτωση προβλήματος: {support}",
        "probleme": "❌ Πρόβλημα με το αίτημά σου.\n\nΕπικοινώνησε με την υποστήριξη: {support}",
        "support": "💬 Για οποιαδήποτε ερώτηση, επικοινώνησε με {support}.",
    },
}

LANGUES_NOMS = {
    "fr": "Français 🇫🇷",
    "en": "English 🇬🇧",
    "de": "Deutsch 🇩🇪",
    "el": "Ελληνικά 🇬🇷",
}

FICHIER_ADMIN = "candidatures_admin_id.txt"


def id_candidatures() -> int:
    try:
        with open(FICHIER_ADMIN) as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return ADMIN_ID


def est_admin(user) -> bool:
    return user.id in (ADMIN_ID, id_candidatures()) or (
        user.username or "").lower() == ADMIN_USERNAME.lower()


def nouveau_numero() -> str:
    return "DEM-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


async def reperer_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user and (user.username or "").lower() == ADMIN_USERNAME.lower():
        if id_candidatures() != user.id:
            with open(FICHIER_ADMIN, "w") as f:
                f.write(str(user.id))
            print(f"ID de @{ADMIN_USERNAME} enregistré : {user.id}")


async def erreur(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"⚠️ Erreur ignorée : {context.error}")


def langue(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "fr")


def clavier_moyens():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Transcash", callback_data="moyen_transcash")],
        [InlineKeyboardButton("💳 PCS", callback_data="moyen_pcs")],
        [InlineKeyboardButton("🇬🇷 Paysafecard", callback_data="moyen_paysafecard_grecque")],
        [InlineKeyboardButton("🇫🇷 Paysafecard", callback_data="moyen_paysafecard_france")],
        [InlineKeyboardButton("🇩🇪 Paysafecard", callback_data="moyen_paysafecard_allemagne")],
        [InlineKeyboardButton("💰 PayPal", callback_data="moyen_paypal")],
    ])


def clavier_fini(lang: str):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(TEXTES[lang]["bouton_fini"], callback_data="fini")
    ]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clavier = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de"),
         InlineKeyboardButton("🇬🇷 Ελληνικά", callback_data="lang_el")],
    ])
    await update.message.reply_text(
        "Choisis ta langue / Choose your language / Sprache wählen / Επίλεξε γλώσσα :",
        reply_markup=clavier
    )


async def choix_langue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["lang"] = query.data.split("_")[1]
    await query.edit_message_text(
        TEXTES[langue(context)]["bienvenue"].format(support=SUPPORT_USERNAME),
        parse_mode="HTML",
        reply_markup=clavier_moyens()
    )


async def choix_moyen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    moyen = query.data.replace("moyen_", "")
    context.user_data["moyen_en_attente"] = moyen
    context.user_data["messages_collectes"] = []
    lang = langue(context)
    t = TEXTES[lang]

    noms = {
        "transcash": "Transcash",
        "pcs": "PCS",
        "paysafecard_grecque": "Paysafecard 🇬🇷",
        "paysafecard_france": "Paysafecard 🇫🇷",
        "paysafecard_allemagne": "Paysafecard 🇩🇪",
        "paypal": "PayPal",
    }
    moyen_affiche = noms.get(moyen, moyen.capitalize())

    texte = t["demande_infos_paypal"].format(paypal_link=PAYPAL_LINK) if moyen == "paypal" else t["demande_infos"].format(moyen=moyen_affiche)

    await query.edit_message_text(
        texte,
        parse_mode="HTML",
        reply_markup=clavier_fini(lang)
    )


async def bouton_fini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = langue(context)
    t = TEXTES[lang]

    moyen = context.user_data.get("moyen_en_attente")
    messages = context.user_data.get("messages_collectes", [])

    if not moyen or not messages:
        await query.answer("Tu n'as rien envoyé pour le moment.", show_alert=True)
        return

    client = query.from_user
    pseudo = f"@{client.username}" if client.username else "(pas de pseudo)"
    numero = nouveau_numero()
    langue_affichee = LANGUES_NOMS.get(lang, lang)

    noms = {
        "transcash": "Transcash",
        "pcs": "PCS",
        "paysafecard_grecque": "Paysafecard 🇬🇷",
        "paysafecard_france": "Paysafecard 🇫🇷",
        "paysafecard_allemagne": "Paysafecard 🇩🇪",
        "paypal": "PayPal",
    }
    moyen_affiche = noms.get(moyen, moyen)

    header = (
        "📩 Nouvelle demande\n\n"
        f"📦 Numéro : {numero}\n"
        f"👤 {client.full_name} {pseudo}\n"
        f"🆔 {client.id}\n"
        f"🌐 Langue : {langue_affichee}\n"
        f"💳 Moyen : {moyen_affiche}\n\n"
        f"📝 Messages reçus ({len(messages)}) :"
    )

    boutons_admin = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Confirmé", callback_data=f"ok|{client.id}|{lang}"),
        InlineKeyboardButton("❌ Problème", callback_data=f"no|{client.id}|{lang}"),
    ]])

    await context.bot.send_message(
        chat_id=id_candidatures(),
        text=header,
        reply_markup=boutons_admin
    )

    for msg in messages:
        if msg["type"] == "text":
            await context.bot.send_message(id_candidatures(), msg["content"])
        elif msg["type"] == "photo":
            await context.bot.send_photo(
                id_candidatures(),
                msg["file_id"],
                caption=msg.get("caption", "")
            )

    await query.edit_message_text(
        t["recu"].format(num=numero, support=SUPPORT_USERNAME),
        parse_mode="HTML"
    )

    context.user_data.pop("moyen_en_attente", None)
    context.user_data.pop("messages_collectes", None)


async def recevoir_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if est_admin(update.effective_user) and update.message.reply_to_message:
        original = update.message.reply_to_message
        text_original = (original.caption or original.text or "")
        client_id = None
        for line in text_original.split("\n"):
            if "🆔" in line:
                try:
                    client_id = int(line.split("🆔")[-1].strip())
                    break
                except:
                    continue
        if client_id:
            if update.message.text:
                await context.bot.send_message(client_id, f"📩 Message de l'admin :\n\n{update.message.text}")
            elif update.message.photo:
                await context.bot.send_photo(
                    client_id,
                    update.message.photo[-1].file_id,
                    caption=update.message.caption or "📩 Message de l'admin"
                )
            await update.message.reply_text("✅ Message envoyé au client")
            return

    if "moyen_en_attente" not in context.user_data:
        await update.message.reply_text(
            "Choisis d'abord un moyen de paiement.",
            reply_markup=clavier_moyens()
        )
        return

    if "messages_collectes" not in context.user_data:
        context.user_data["messages_collectes"] = []

    if update.message.text:
        context.user_data["messages_collectes"].append({
            "type": "text",
            "content": update.message.text
        })
    elif update.message.photo:
        context.user_data["messages_collectes"].append({
            "type": "photo",
            "file_id": update.message.photo[-1].file_id,
            "caption": update.message.caption or ""
        })

    lang = langue(context)
    await update.message.reply_text(
        "✅ Reçu. Tu peux continuer ou cliquer sur le bouton quand tu as fini.",
        reply_markup=clavier_fini(lang)
    )


async def decision_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not est_admin(query.from_user):
        await query.answer("Non autorisé", show_alert=True)
        return
    await query.answer()

    choix, client_id, lang = query.data.split("|")
    client_id = int(client_id)
    t = TEXTES.get(lang, TEXTES["fr"])

    if choix == "ok":
        await context.bot.send_message(
            client_id,
            t["confirme"].format(support=SUPPORT_USERNAME),
            parse_mode="HTML"
        )
        statut = "✅ CONFIRMÉ – client notifié"
    else:
        await context.bot.send_message(
            client_id,
            t["probleme"].format(support=SUPPORT_USERNAME),
            parse_mode="HTML"
        )
        statut = "❌ PROBLÈME – client notifié"

    try:
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(statut)
    except Exception:
        pass


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        TEXTES[langue(context)]["support"].format(support=SUPPORT_USERNAME)
    )


def creer_app():
    app = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .build()
    )
    app.add_handler(TypeHandler(Update, reperer_admin), group=-1)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CallbackQueryHandler(choix_langue, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(choix_moyen, pattern="^moyen_"))
    app.add_handler(CallbackQueryHandler(bouton_fini, pattern="^fini$"))
    app.add_handler(CallbackQueryHandler(decision_admin, pattern="^(ok|no)\\|"))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, recevoir_message))
    app.add_error_handler(erreur)
    return app


def main():
    while True:
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            print("Bot lancé ✅")
            creer_app().run_polling()
            break
        except NetworkError as e:
            print(f"⚠️ Connexion impossible ({e}), nouvel essai dans 10 s...")
            import time
            time.sleep(10)


if __name__ == "__main__":
    main()
