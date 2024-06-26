import requests,tabulate,logging,tempfile,json,os
import matplotlib.pyplot as plt
from telegram import  InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler,CallbackQueryHandler,filters, ContextTypes
API_URL= "http://52.72.84.66:8000/getData/"
API_URL_MONOXIDO = "http://52.72.84.66:8000/monoxido/"
API_URL_LUZ = "http://52.72.84.66:8000/luz/"

# Token de tºu bot
TOKEN_BOT = '7424854412:AAGrMcnVxQbhOmhpgNuehLbuHFeFChIBO-s'

HEADERS_GET = ['Fecha','Monóxido de Carbono','Luz']

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
   await update.message.reply_text(update.message.text)

def get_data_from_api(numRegistros) -> list:
    #numRegistros = int(numRegistros)
    data = {'numRegistros':numRegistros}
    dataJSON = json.dumps(data)
    print(f"Making a request to {API_URL} with data: {data}")  # Debug statement
    try:
        response = requests.post(API_URL,data=dataJSON)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")  # Print out the error
        return None
    return response.json()

def get_data_from_api_variable(numRegistros,tipo) -> list:
    #numRegistros = int(numRegistros)
    data = {"numRegistros":numRegistros}
    dataJSON = json.dumps(data)
    if tipo == "monoxido_de_carbono":
        url = API_URL_MONOXIDO
    elif tipo == "luz":
        url = API_URL_LUZ
    else:
        return None
    print(f"Making a request to {url} with data: {data}")  # Debug statement
    try:
        response = requests.get(url,data=dataJSON)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")  # Print out the error
        return None
    return response.json()
async def monoxido_carbono(update, context):
    await update.message.reply_text("Obteniendo información de monóxido de carbono...")
    # Obtener la información de la API
    data = get_data_from_api_variable(24,"monoxido_de_carbono")
    if data is None:
        await update.message.reply_text("No se pudo obtener la información.")
        return

    # Crear una grafica con la información obtenida
     # Asegurarse de que la data sea una lista de diccionarios
    print(data)
    try:
        x = []
        y = []
        for item in data:
            x.append(item[0])
            y.append(item[1])
    except (TypeError, KeyError) as e:
        await update.message.reply_text("Error procesando los datos de la API.")
        return

    plt.figure()
    plt.plot(x, y)
    plt.xlabel('Fecha')
    plt.ylabel('Monóxido de Carbono')
    plt.title('Niveles de Monóxido de Carbono')

# Guardar la gráfica en un archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
        plt.savefig(tmpfile.name)
        image_path = tmpfile.name

    plt.close()

    # Enviar el archivo de imagen a través del bot de Telegram
    with open(image_path, 'rb') as image_file:
        await context.bot.send_photo(chat_id=update.message.chat_id, photo=image_file,
                                      caption='Niveles de Monóxido de Carbono')

    # Eliminar el archivo temporal
    os.remove(image_path)
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
    application.add_handler(CommandHandler('monoxido', monoxido_carbono))
    application.add_handler(MessageHandler(None, echo))
    # Iniciar el bot
    application.run_polling()
    
    # Correr el bot hasta que se detenga con Ctrl+C
    application.idle()
if __name__ == '__main__':
    main()
