import os
import re
import joblib
import unicodedata
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from logger import setup_logger

# Cargar modelo y vectorizador
modelo = joblib.load("modelo/modelo_entrenado.pkl")
vectorizer = joblib.load("modelo/vectorizer.pkl")

# Configurar logger
logger = setup_logger()

# Cargar variables de entorno
load_dotenv()
telegram_bot_token = os.getenv("telegram_bot_token")

if not telegram_bot_token:
    raise ValueError("No se encontró el token en el archivo .env")

# --- Funciones auxiliares ---

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

# --- Handler de mensajes ---

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        pregunta = update.message.text
        respuesta = obtener_respuesta(pregunta)
        await update.message.reply_text(f"💬 {respuesta}")
    except Exception as e:
        logger.error(f"Error al responder: {e}")
        await update.message.reply_text("Ocurrió un error al procesar tu mensaje.")

# --- Función principal ---

async def main():
    app = ApplicationBuilder().token(telegram_bot_token).build()

    # Manejador para todos los mensajes de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🤖 Bot en funcionamiento...")
    await app.run_polling()

# Ejecutar
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
