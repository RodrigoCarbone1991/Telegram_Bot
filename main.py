import asyncio
import unicodedata
import re
from telegram import Bot
from dotenv import load_dotenv
import os
from logger import setup_logger
import joblib
from sklearn.naive_bayes import MultinomialNB

# Cargar modelo y vectorizador
modelo = joblib.load("modelo/modelo_entrenado.pkl")
vectorizer = joblib.load("modelo/vectorizer.pkl")

# Función para limpiar texto
def limpiar_texto(texto):
    # Pasar a minúsculas
    texto = texto.lower()
    # Eliminar tildes
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn')
    # Eliminar signos de puntuación
    texto = re.sub(r'[^\w\s]', '', texto)
    # Eliminar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def obtener_respuesta(pregunta_usuario):
    pregunta_limpia = limpiar_texto(pregunta_usuario)
    pregunta_vectorizada = vectorizer.transform([pregunta_limpia])
    respuesta = modelo.predict(pregunta_vectorizada)
    return respuesta[0]


# Configurar el logger
logger = setup_logger()

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener el token desde el archivo .env
telegram_bot_token = os.getenv("telegram_bot_token")

# Verificar que el token esté cargado correctamente
if not telegram_bot_token:
    raise ValueError("El token de Telegram no se cargó. Verificar archivo .env y la clave telegram_bot_token.")

async def send_message():
    try:
        bot = Bot(token=telegram_bot_token)
        user_id = 1076844476  # tu ID

        # Simulamos una pregunta (después podés leer desde consola o integrar handlers)
        pregunta = "¿Cómo doy de alta un usuario?"
        respuesta = obtener_respuesta(pregunta)

        await bot.send_message(chat_id=user_id, text=f"🧠 Pregunta: {pregunta}\n💬 Respuesta: {respuesta}")
        print("Mensaje enviado correctamente.")

    except Exception as e:
        logger.error(f"Error al enviar mensaje: {e}")


# Ejecutar la función asincrónica
asyncio.run(send_message())
