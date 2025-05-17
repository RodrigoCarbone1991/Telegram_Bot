import os
import re
import joblib
import unicodedata
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram import Update
from logger import setup_logger

modelo = joblib.load("modelo/modelo_entrenado.pkl")
vectorizer = joblib.load("modelo/vectorizer.pkl")

logger = setup_logger()

load_dotenv()
telegram_bot_token = os.getenv("telegram_bot_token")

if not telegram_bot_token:
    raise ValueError("No se encontró el token en el archivo .env")

def limpiar_texto(texto):
    texto = texto.lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\w\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def obtener_respuesta(pregunta_usuario):
    pregunta_limpia = limpiar_texto(pregunta_usuario)
    pregunta_vectorizada = vectorizer.transform([pregunta_limpia])
    respuesta = modelo.predict(pregunta_vectorizada)
    return respuesta[0]


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        pregunta = update.message.text
        # Limpiar mensaje
        mensaje_limpio = limpiar_texto(pregunta)
        #Reglas de validacion
        es_muy_corto = len(mensaje_limpio) < 2
        solo_una_letra_o_numero = mensaje_limpio.isalnum() and len(mensaje_limpio) == 1
        contiene_palabras = any(c.isalpha() for c in mensaje_limpio) and len(mensaje_limpio.split()) >= 1
        if es_muy_corto or solo_una_letra_o_numero or not contiene_palabras:
            await update.message.reply_text("Por ahi quisiste decir otra cosa o no entendi🧐, lo escribis de nuevo?.")
            return
        respuesta = obtener_respuesta(pregunta)
        await update.message.reply_text(f" {respuesta}")
    except Exception as e:
        logger.error(f"Error al responder: {e}")
        await update.message.reply_text("Si te digo que se cayo el sistema, me crees? jaja😂.")


async def main():
    app = ApplicationBuilder().token(telegram_bot_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    print("🤖 Bot en funcionamiento...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

if __name__ == "__main__":
    import asyncio
    async def safe_main():
        await main()
        await asyncio.Event().wait()

    try:
        asyncio.get_event_loop().run_until_complete(safe_main())
    except KeyboardInterrupt:
        print("🔴 Bot detenido manualmente.")

