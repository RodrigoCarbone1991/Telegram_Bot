import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener el token desde el archivo .env
telegram_bot_token = os.getenv("telegram_bot_token")

# Verificar que el token esté cargado correctamente
if not telegram_bot_token:
    raise ValueError("El token de Telegram no se cargó. Verificar archivo .env y la clave telegram_bot_token.")

async def send_message():
    """
    Función asincrónica para enviar un mensaje a un usuario específico.
    """
    try:
        bot = Bot(token=telegram_bot_token)

        # ID de usuario (reemplaza con tu propio ID)
        user_id = 1076844476

        # Mensaje a enviar
        message = "Hola Rodri, yo soy vos"

        # Enviar mensaje y confirmar éxito
        await bot.send_message(chat_id=user_id, text=message)
        print("Mensaje enviado con éxito.")
    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")

# Ejecutar la función asincrónica
asyncio.run(send_message())
