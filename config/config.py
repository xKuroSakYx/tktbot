from configparser import ConfigParser
import mysql.connector
import hashlib
from telegram.ext import ContextTypes
import logging
import re

def config(seccion='x6nge', archivo='config.ini'):
    # Crear el parser y leer el archivo
    parser = ConfigParser()
    parser.read(archivo)
    #print('se ejecuto config')
 
    # Obtener la sección de conexión a la base de datos
    db = {}
    if parser.has_section(seccion):
        params = parser.items(seccion)
        for param in params:
            db[param[0]] = param[1]
        return db
    else:
        raise Exception('Secccion {0} no encontrada en el archivo {1}'.format(seccion, archivo))

param = config("serverdata")
TOKEN = param['token']
MODE = param['mode']
SERVER_LINK = param['server']
WEBURL = f'https://{SERVER_LINK}/{TOKEN}'
OWNERCHATID = [-4066580199, 1958469014, -1001989495982]
welcomeMessage = '\n\n[Establece un mensaje de bienvenida con el comando /changeMsg nuevo mensaje de bienvenida y será reemplazado aqui]'
rudeList = ['imbecil', 'Imbecil', 'Ignorante', 'ignorante', 'baboso', 'Baboso', 'Estupido', 'estupido', 'gay', 'Gay','hpta', 'HPTA']

logging.basicConfig(#WARNING
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s," 
)
logger = logging.getLogger()
_COMMAND_ = ['/airdrop']

async def echo(update, context: ContextTypes.DEFAULT_TYPE):
    groupId = update.effective_chat.id
    if not int(groupId) in OWNERCHATID:
        print("el id de chat es " % groupId)
        return
    
    #print(update)
    bot = context.bot
    update_msg = getattr(update, "message", None) #get info of message
    msg_id = update_msg.message_id #get recently message id
    
    userName = update.effective_user['first_name']
    user_id = update.effective_user['id'] #get user id
    text = update.message.text #get message sent to the bot    
    logger.info(f"El usuario {userName}, ha enviado un mensaje de texto. {text} groupid {groupId}")
    
    await responseText(bot, text, groupId, msg_id, userName)

async def newUsers(update, context: ContextTypes.DEFAULT_TYPE):
    groupId = update.effective_chat.id
    if not int(groupId) in OWNERCHATID:
        print("no son iguales ")
        return
    bot = context.bot
    update_msg = getattr(update, "message", None) #get info of message
    msg_id = update_msg.message_id #get recently message id
    user_id = update.effective_user['id'] #get user id
    username = update.effective_user['username']
    userName = update.effective_user['first_name']
    
    #text = update.message.text #get message sent to the bot    
    #logger.info(f"{userName}, ha enviado un mensaje de texto. {text} groupid {groupId}")
    await storeUser(user_id, username)
    await bot.sendMessage(
        chat_id=groupId,
        parse_mode="HTML",
        text = f'<b>¡Welcome {userName} to The Key of True! community. You can access <a href="https://x6nge.io">X6NGE</a> to obtain the tokens for the ongoing Airdrop</b>.'
    )

async def airdrop(update, context: ContextTypes.DEFAULT_TYPE):
    groupId = update.effective_chat.id
    bot = context.bot
    update_msg = getattr(update, "message", None) #get info of message
    msg_id = update_msg.message_id #get recently message id
    user_id = update.effective_user['id'] #get user id
    username = update.effective_user['username']
    userName = update.effective_user['first_name']
    text = update.message.text #get message sent to the bot    
    #logger.info(f"{userName}, ha enviado un mensaje de texto. {text} groupid {groupId}")

    if not int(groupId) in OWNERCHATID:
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = f'{userName}, The /airdrop command has to be sent by the group <a href="https://t.me/x6ngeio">TKT GROUP</a>. Visit our website <a href="https://x6nge.io">X6NGE</a> and our twitter page <a href="https://twitter.com/x6nge">TWITTER</a>, you can also join our channel ### <a href="https://t.me/thekeyoftrueTKT">CHANEL</a>. Thank you, have a nice day'
        )
        print(f"no son iguales {groupId}")
        return

    isvalid = await storeUser(user_id, username)
    if isvalid == "user_ok":
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = f'{userName}, you have successfully registered, you can go to <a href="https://x6nge.io">X6NGE</a> to get the tokens for the ongoing Airdrop'
        )
    elif isvalid == "user_register":
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = f'{userName}, you have already registered previously, you can go to <a href="https://x6nge.io">X6NGE</a> to get the <b>Airdrop tokens.</b>'
        )
    elif isvalid == "user_register_paid":
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = f'{userName}, you have already received the Airdrop tokens.'
        )

async def responseText(bot, text, groupId, msg_id, userName):
    for rude in rudeList:
        if rude in str(text):
            await deleteMessage(bot, groupId, msg_id, userName)
            await bot.sendMessage(
                chat_id=groupId,
                parse_mode="HTML",
                text = f'El mensaje de <b>{userName}</b> ha sido eliminado porque tenia palabras ofensivas o caracteres desconocidos.'
        )
    
    await searchErrorCommand(bot, text, groupId, msg_id, userName)

async def searchErrorCommand(bot, text, groupId, msg_id, userName):
    reg = re.compile('^/[a-zA-Z]0-9@]')


def deleteMessage(bot, chatId, messageId, userName): #delete messages
    try:
        bot.delete_message(chatId, messageId)
        logger.info(f'El mensaje de {userName} ha sido eliminado porque tenia palabras ofensivas')
    except Exception as e:
        print(e)

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

async def storeUser(userid, username):
    try:
        hash = calculate_sha256("%s" % userid)
        conexion = None
        #params = config()
        params = config('localdb')
        #print(params)
    
        # Conexion al servidor de MySql
        #print('Conectando a la base de datos MySql...validateUsername')
        conexion = mysql.connector.connect(**params)
        #print("se conectpo a la base de datos")
        # creación del cursor
        cur = conexion.cursor()
        
        # creando la tabla si no existe
        #tktid bigint(255) not null,
        cur.execute("CREATE TABLE IF NOT EXISTS telegram (id bigint(255) not null AUTO_INCREMENT, userid bigint(255) not null, username varchar(255) not null, valid int(1) not null, mhash varchar(255) not null, primary key (id))  ENGINE = InnoDB")
        #cur.execute("CREATE INDEX userids ON telegram (userid)")

        cur.execute( "SELECT valid, mhash FROM telegram where userid=%s", (userid, ) )

        # Recorremos los resultados y los mostramos

        userlist = cur.fetchall()
        for valid in userlist :
            #print("el user id %s el valid %s"%(userid, valid))
            if(valid[0] == 0 and valid[1] == hash):
                #print("el usuario %s esta regisrado en el canal pero no ha recibido los token "% userid)
                conexion.close()
                return "user_register"
                
            elif(valid[0] == 1 and valid[1] == hash):
                #print("el usuario %s ya recibio los token"% userid)
                conexion.close()
                return "user_register_paid"
        
        #print("ingresando un nuevo usuario final %s"% userid)
        sql="insert into telegram(userid, username, valid, mhash) values (%s, %s, 0, %s)"
        datos=(userid, username, hash)
        cur.execute(sql, datos)
        #print("se inserto la fila correctamente final hash %s "% hash)
        conexion.commit()
        conexion.close()
        
        return "user_ok"
        
    except (Exception) as error:
        print(error)
    finally:
        if conexion is not None:
            conexion.close()
            #print('Conexión finalizada.')

def calculate_sha256(data):
    password = "ecfbeb0a78c04e5.*692a4*..e5c___69..0f9c*f1f**0cdae__f723e6346f2b8af187$@7f21d4b4$$3a0b33c1.__26afd40a$$3b**.125ce8a$$457.*b0bba"

    data = "%s %s"%(data, password)
    if isinstance(data, str):
        data = data.encode()
    md5hash = hashlib.md5(data).hexdigest().encode()
    sha256_hash = hashlib.sha256(md5hash).hexdigest()
    
    return sha256_hash
