import requests
import tabulate
import logging
from telegram import  InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler,CallbackQueryHandler,filters, ContextTypes
API_URL= "http://52.72.84.66:8000/getData/"
# Token de tºu bot
TOKEN_BOT = '7424854412:AAGrMcnVxQbhOmhpgNuehLbuHFeFChIBO-s'

HEADERS_GET = ['Fecha','Monóxido de Carbono','Luz','Presión', 'Altitud','Temperatura', 'Humedad']

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Variable para almacenar el resultado
user_data = {}

# Función de inicio
async def start(update, context):
    await update.message.reply_text("¡Hola! Soy tu bot cuidador de plantas!!!.")
    
async def echo(update, context: ContextTypes.DEFAULT_TYPE):
    update.message.reply_text(update.message.text)

def get_data_from_api(numRegistros) -> list:
    data = {'numRegistros': numRegistros}
    print(f"Making a request to {API_URL} with data: {data}")  # Debug statement
    try:
        response = requests.post(API_URL, data=data)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")  # Print out the error
        return None
    return response.json()
async def obtenInformacion(update, context):
    # Preguntar al usuario el numero de informacion que quiere obtener en minutos y enviarla
     # Crear los botones
    keyboard = [
        [InlineKeyboardButton("12", callback_data='12')],
        [InlineKeyboardButton("24", callback_data='24')],
        [InlineKeyboardButton("48", callback_data='48')]
    ]
    
    numeroRegistros = InlineKeyboardMarkup(keyboard)
    numRegistros = None

    # Enviar mensaje con los botones
    await update.message.reply_text('Elige un valor:', reply_markup=numeroRegistros)

    
async def button_callback(update, context):
    query = update.callback_query
    query.answer()

    # Almacenar el valor del botón presionado
    user_data[query.from_user.id] = query.data

    # Responder con el valor del botón presionado
    await query.edit_message_text(text=f"Seleccionaste: {query.data}")   

    # Obtener el valor seleccionado por el usuario
    numRegistros = query.data
    await query.message.reply_text(f"Obteniendo información de los últimos {numRegistros} registros...")

    # Obtener la información de la API
    data = get_data_from_api(numRegistros)
    # data =[{'id': 1, 'fecha': '2021-10-01 00:00:00', 'temperatura': 25.0, 'humedad': 50.0, 'luz': 100.0, 'humedad_suelo': 50.0, 'riego': 1}, {'id': 2, 'fecha': '2021-10-01 00:00:00', 'temperatura': 25.0, 'humedad': 50.0, 'luz': 100.0, 'humedad_suelo': 50.0, 'riego': 1}, {'id': 3, 'fecha': '2021-10-01 00:00:00', 'temperatura': 25.0, 'humedad': 50.0, 'luz': 100.0, 'humedad_suelo': 50.0, 'riego': 1}, {'id': 4, 'fecha': '2021-10-01 00:00:00', 'temperatura': 25.0, 'humedad': 50.0, 'luz': 100.0, 'humedad_suelo': 50.0, 'riego': 1}, {'id': 5, 'fecha': '2021-10-01 00:00:00', 'temperatura': 25.0, 'humedad': 50.0, 'luz': 100.0, 'humedad_suelo': 50.0, 'riego': 1}, {'id': 6, 'fecha': '2021-10-01 00:00:00', 'temperatura': 25.0, 'humedad': 50.0, 'luz': 100.0, 'humedad_suelo': 50.0, 'riego': 1}, {'id': 7, 'fecha': '2021-10-01 00:00:00', 'temperatura': 25.0, 'humedad': 50.0, 'luz': 100.0, 'humedad_suelo': 50.0, 'riego': 1}]
    if data is None:
        await query.message.reply_text("No se pudo obtener la información.")
        return
    # Crear una tabla con la información obtenida
    print(data)
    headers = HEADERS_GET
    
    table = tabulate.tabulate(data, headers, tablefmt="grid")
    await query.message.reply_text(f'<pre>{table}</pre>', parse_mode='HTML')

def main():
    # Crear la aplicación
    application = Application.builder().token(TOKEN_BOT).build()

    # Comandos y manejo de mensajes
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('informacion', obtenInformacion))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(None, echo))
    
    # Iniciar el bot
    application.run_polling()
    
    # Correr el bot hasta que se detenga con Ctrl+C
    application.idle()
if __name__ == '__main__':
    main()
