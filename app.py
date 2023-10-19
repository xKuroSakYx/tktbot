import os
import logging #report bot events   
import telegram
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, Updater, CommandHandler, MessageHandler, filters
#Updater, receive messages from telegram to process that

from config.config import config, changeMsg, airdrop, newUsers, echo, cmd_help_3, cmd_contract_4, cmd_link_5, cmd_metamask_6

#configure logging
logging.basicConfig(#WARNING
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s," 
)
logger = logging.getLogger()


#agregar comando de eventos para que los administradores, agreguen los eventos disponibles con sus fechas y horarios
#datos como: el clima, noticias de tecnologia, o alguna informacion relevante

#request TOKEN
#this bot will be on the net and heroku, so for security, the token of the bot should be hidden 
#in the environment variable

param = config("serverdata")
TOKEN = param['token']
MODE = param['mode']
SERVER_LINK = param['server']
WEBURL = f'https://{SERVER_LINK}/{TOKEN}'
OWNERCHATID = [-4066580199, 1958469014, -1001989495982]

#TOKEN = os.getenv("TOKEN") #create an environment variable. pwershell = $env:TOKEN="token code", cmd = set TOKEN=token code
#MODE = os.getenv('MODE') #for know if is running in cmd or in web heroku
#SERVER_LINK = "x6nge.io/telegrambot"
print(f"el modo de ejecucion es {MODE}")
if MODE == 'dev':#is running in cmd
    def run(updater):
        updater.run_polling()#constantly ask if there are messages
        print("BOT RUNNING")
        
elif MODE == 'prod': #is running on web, heroku
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443")) #assign a port for bot execution
        updater.run_webhook(listen="0.0.0.0", port= PORT, url_path=TOKEN, webhook_url=WEBURL)
        #updater.start_webhook(listen="0.0.0.0", port= PORT, url_path=TOKEN)
        #updater.bot.set_webhook(f'https://{SERVER_LINK}/{TOKEN}')
else:
    logger.info('No se especificó el modo de ejecucion del bot')
    sys.exit()  


if __name__ == "__main__":
    #obtain bot info
    myBot = telegram.Bot(token= TOKEN)       
    #print(myBot.getMe())

#connect Updater with our bot
#updater = Updater(myBot.token, update_queue=True)

application = ApplicationBuilder().token(TOKEN).build()

#create handler
application.add_handler(CommandHandler('airdrop', airdrop))
application.add_handler(CommandHandler('help', cmd_help_3))
application.add_handler(CommandHandler('contract', cmd_contract_4))
application.add_handler(CommandHandler('link', cmd_link_5))
application.add_handler(CommandHandler('metamask', cmd_metamask_6))
application.add_handler(CommandHandler('changeMsg', changeMsg))
application.add_handler(MessageHandler(filters.TEXT, echo)) #waiting for text input in chat
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, newUsers)) #getting new members

run(application)

#run(updater)