import os
import logging #report bot events   
import telegram
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, Updater, CommandHandler, MessageHandler, filters
#Updater, receive messages from telegram to process that

from config.config import config, storeUser

#configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s," 
)
logger = logging.getLogger()

welcomeMessage = '\n\n[Establece un mensaje de bienvenida con el comando /changeMsg nuevo mensaje de bienvenida y será reemplazado aqui]'
rudeList = ['imbecil', 'Imbecil', 'Ignorante', 'ignorante', 'baboso', 'Baboso', 'Estupido', 'estupido', 'gay', 'Gay'
            ,'hpta', 'HPTA'
            ]
OWNERCHATID = -4072756889

eventos = 'Eventos: \nAgéndate en este enlace: https://app.interacpedia.com/mass-events'

#agregar comando de eventos para que los administradores, agreguen los eventos disponibles con sus fechas y horarios
#datos como: el clima, noticias de tecnologia, o alguna informacion relevante

#request TOKEN
#this bot will be on the net and heroku, so for security, the token of the bot should be hidden 
#in the environment variable

param = config("serverdata")
TOKEN = param['token']
MODE = param['mode']
SERVER_LINK = param['server']

#TOKEN = os.getenv("TOKEN") #create an environment variable. pwershell = $env:TOKEN="token code", cmd = set TOKEN=token code
#MODE = os.getenv('MODE') #for know if is running in cmd or in web heroku
#SERVER_LINK = "x6nge.com/telegrambot"
print(f"el modo de ejecucion es {MODE}")
if MODE == 'dev':#is running in cmd
    def run(updater):
        updater.run_polling()#constantly ask if there are messages
        print("BOT RUNNING")
        updater.idle()
elif MODE == 'prod': #is running on web, heroku
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443")) #assign a port for bot execution
        updater.run_webhook(listen="0.0.0.0", port= PORT, url_path=TOKEN, webhook_url=f'https://{SERVER_LINK}/{TOKEN}')
        #updater.start_webhook(listen="0.0.0.0", port= PORT, url_path=TOKEN)
        #updater.bot.set_webhook(f'https://{SERVER_LINK}/{TOKEN}')
else:
    logger.info('No se especificó el modo de ejecucion del bot')
    sys.exit()  

def userisAdmin(bot, userId, chatId): #method for find and get the chat admins, identify if the new user is an admin
    try:
        groupAdmins = bot.get_chat_administrators(chatId)
    except Exception as e:
        print(e)

    isAdmin = False
    for admin in groupAdmins:
        if admin.user.id == userId:
            isAdmin = True
    
    return isAdmin

def changeMsg(update, context): #change default welcome message
    # ''' /changeMsg nuevo mensaje de bienvenida '''
    bot = context.bot
    args = context.args #get extra info from the command
    user_id = update.effective_user['id'] #get user id
    userName = update.effective_user['first_name'] #
    groupId = update.message.chat_id 
    global welcomeMessage

    if userisAdmin(bot, user_id, groupId) == True: #if the user that sent command is an admin
        if len(args) == 0: #if there is not extra info in command
            logger.info(f'{userName} no ha establecido correctamente un Mensaje de bienvenida')
            bot.sendMessage(
                chat_id=groupId,
                text=f'{userName}, no has establecido ningun mensaje, intentalo de nuevo por ej: /changeMsg este es un nuevo mensaje de bienvenida'
            )
        else: #there is extra info
            welcomeMessage = " ".join(args) #get all exra info and set in var
            welcomeMessage = "\n" + welcomeMessage   #change welcome message 
            bot.sendMessage(
                chat_id=groupId,
                text=f'Mensaje de bienvenida cambiado correctamente'
            )
    else: #is not admin
        logger.info(f'{userName} ha intentado cambiar el mensaje de bienvenida, pero no tiene permisos')    
        bot.sendMessage(
            chat_id=groupId,
            text=f'{userName}, no tienes permiso para cambiar el mensaje de bienvenida.'
        )

def deleteMessage(bot, chatId, messageId, userName): #delete messages
    try:
        bot.delete_message(chatId, messageId)
        logger.info(f'El mensaje de {userName} ha sido eliminado porque tenia palabras ofensivas')
    except Exception as e:
        print(e)

async def echo(update, context: ContextTypes.DEFAULT_TYPE):
    groupId = update.effective_chat.id
    if OWNERCHATID != int(groupId):
        return
    
    #print(update)
    bot = context.bot
    update_msg = getattr(update, "message", None) #get info of message
    msg_id = update_msg.message_id #get recently message id
    
    userName = update.effective_user['first_name']
    user_id = update.effective_user['id'] #get user id
    text = update.message.text #get message sent to the bot    
    logger.info(f"El usuario {userName}, ha enviado un mensaje de texto. {text} groupid {groupId}")
    

    if 'conquistar el mundo' in text and 'TecDataBot' in text:
        await bot.sendMessage( #send message to telegram chat
            chat_id=groupId,
            parse_mode="HTML",
            text = f'Claro que si {userName}, ese es el objetivo con el que mi creador me trajo al mundo muajajajaja'
        )
    elif 'TecDataBot' in text and 'buena suerte' in text:
        await bot.sendMessage(
            chat_id=groupId,
            text= f'Muchas Gracias {userName}, aunque creo que no la necesito!!!'
        )
    else:
        for rude in rudeList: #delete message if there is bad word there
            if rude in str(text):
                await deleteMessage(bot, groupId, msg_id, userName)
                await bot.sendMessage(
                    chat_id=groupId,
                    parse_mode="HTML",
                    text = f'El mensaje de <b>{userName}</b> ha sido eliminado porque tenia palabras ofensivas o caracteres desconocidos.'
            )    

async def airdrop(update, context: ContextTypes.DEFAULT_TYPE):
    groupId = update.effective_chat.id
    if OWNERCHATID != int(groupId):
        print("no son iguales ")
        return

    bot = context.bot
    update_msg = getattr(update, "message", None) #get info of message
    msg_id = update_msg.message_id #get recently message id
    user_id = update.effective_user['id'] #get user id
    username = update.effective_user['username']
    userName = update.effective_user['first_name']
    text = update.message.text #get message sent to the bot    
    #logger.info(f"{userName}, ha enviado un mensaje de texto. {text} groupid {groupId}")
    isvalid = await storeUser(user_id, username)
    if isvalid == "user_ok":
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = f'{userName}, usted se ha registrado correctamente para poder obtener los tokens del Airdrop.'
        )
    elif isvalid == "user_register":
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = f'{userName}, usted ya se ha registrado previamente, puede acceder a https://x6nge.com para obtener los tokens del Airdrop.'
        )
    elif isvalid == "user_register_paid":
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = f'{userName}, usted ya ha recibido los tokens del Airdrop.'
        )

async def newUsers(update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    update_msg = getattr(update, "message", None) #get info of message
    msg_id = update_msg.message_id #get recently message id
    groupId = update.effective_chat.id
    user_id = update.effective_user['id'] #get user id
    username = update.effective_user['username']
    userName = update.effective_user['first_name']
    
    #text = update.message.text #get message sent to the bot    
    #logger.info(f"{userName}, ha enviado un mensaje de texto. {text} groupid {groupId}")
    await storeUser(user_id, username)
    await bot.sendMessage(
        chat_id=groupId,
        parse_mode="HTML",
        text = f"<b>¡Bienvenid@ {userName} a la comunidad de TheKeyOfTrue!. Acceda a https://x6nge.com para el Airdrop</b>."
    )

if __name__ == "__main__":
    #obtain bot info
    myBot = telegram.Bot(token= TOKEN)       
    #print(myBot.getMe())

#connect Updater with our bot
#updater = Updater(myBot.token, update_queue=True)

application = ApplicationBuilder().token(TOKEN).build()

#create handler
application.add_handler(CommandHandler('airdrop', airdrop))
application.add_handler(CommandHandler('changeMsg', changeMsg))
application.add_handler(MessageHandler(filters.TEXT, echo)) #waiting for text input in chat
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, newUsers)) #getting new members

run(application)

#run(updater)