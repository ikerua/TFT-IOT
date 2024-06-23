import requests
import tabulate
from telegram.ext import Application, CommandHandler, MessageHandler, filters
API_URL= "http://localhost:8000/getData/"
# Token de tºu bot
TOKEN_BOT = '7424854412:AAGrMcnVxQbhOmhpgNuehLbuHFeFChIBO-s'
# Función de inicio
def start(update, context):
    update.message.reply_text("¡Hola! Soy tu bot cuidador de plantas!!!.")
    
def echo(update, context):
    update.message.reply_text(update.message.text)

def get_data_from_api(numRegistros) -> list:
    data = { "numeroRegistros": numRegistros}
    response = requests.post(API_URL, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        return []
def obtenInformacion(update, context):
    # Preguntar al usuario el numero de informacion que quiere obtener en minutos y enviarla
    update.message.reply_text("Dime el número de registros que quieres obtener (1 minuto = 1 registro) :")
    numeroRegistros = update.message.text
    # Validar que el número sea un entero
    if not numeroRegistros.isdigit():
        update.message.reply_text("Por favor, introduce un número válido:")
        numeroRegistros = update.message.text

    # Obtener la información de la API
    data = get_data_from_api(numeroRegistros)
    if not data:
        update.message.reply_text("No se pudo obtener la información.")
        return
    # Crear una tabla con la información obtenida
    headers = data[0].keys()
    rows = [list(x.values()) for x in data]
    table = tabulate.tabulate(rows, headers, tablefmt="grid")
    update.message.reply_text(f'<pre>{table}</pre>', parse_mode='HTML')
    

def main():
    # Crear la aplicación
    application = Application.builder().token("TOKEN").build()

    # Comandos y manejo de mensajes
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('informacion', obtenInformacion))

    application.add_handler(MessageHandler(filters.text & ~filters.command, echo))
    
    # Iniciar el bot
    application.start_polling()
    
    # Correr el bot hasta que se detenga con Ctrl+C
    application.idle()
if __name__ == '__main__':
    main()
