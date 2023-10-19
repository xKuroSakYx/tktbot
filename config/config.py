from configparser import ConfigParser
import mysql.connector
import hashlib
from telegram.ext import ContextTypes, CallbackContext
import logging
import re
from datetime import datetime
import time

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
OWNERCHATID = [-4066580199, 1958469014, -1001989495982, -4075479334]
welcomeMessage = '\n\n[Establece un mensaje de bienvenida con el comando /changeMsg nuevo mensaje de bienvenida y será reemplazado aqui]'
rudeList = ['imbecil', 'Imbecil', 'Ignorante', 'ignorante', 'baboso', 'Baboso', 'Estupido', 'estupido', 'gay', 'Gay','hpta', 'HPTA']

logging.basicConfig(#WARNING
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s," 
)
logger = logging.getLogger()
_COMMAND_ = ['/airdrop']
_LASTSMS_ = None

async def echo(update, context: ContextTypes.DEFAULT_TYPE):
    groupId = update.effective_chat.id
    userName = update.effective_user['first_name']
    if not int(groupId) in OWNERCHATID:
        print("el id de chat es %s username %s" % (groupId, userName))
        return
    
    #print(update)
    bot = context.bot
    update_msg = getattr(update, "message", None) #get info of message
    msg_id = update_msg.message_id #get recently message id
    
    user_id = update.effective_user['id'] #get user id
    text = update.message.text #get message sent to the bot    
    logger.info(f"El usuario {userName}, ha enviado un mensaje de texto. {text} groupid {groupId}")
    
    await responseText(bot, text, groupId, msg_id, userName)
    await searchErrorCommand(bot, text, groupId, msg_id, userName)


async def newUsers(update, context: ContextTypes.DEFAULT_TYPE):
    groupId = update.effective_chat.id
    bot = context.bot
    update_msg = getattr(update, "message", None) #get info of message
    msg_id = update_msg.message_id #get recently message id
    user_id = update.effective_user['id'] #get user id
    username = update.effective_user['username']
    name = update.effective_user['first_name']

    if not int(groupId) in OWNERCHATID:
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = f'{name}, The /airdrop command has to be sent by the group <a href="https://t.me/x6ngeio">TKT GROUP</a>. Visit our website <a href="https://x6nge.io">X6NGE</a> and our twitter page <a href="https://twitter.com/x6nge">TWITTER</a>, you can also join our channel <a href="https://t.me/thekeyoftrueTKT">CHANEL</a>. Thank you, have a nice day'
        )
        print(f"no son iguales /newUser {groupId}")
        return
    
    #text = update.message.text #get message sent to the bot    
    #logger.info(f"{userName}, ha enviado un mensaje de texto. {text} groupid {groupId}")
    await storeUser(user_id, username)
    await bot.sendMessage(
        chat_id=groupId,
        parse_mode="HTML",
        text = f'<b>¡Welcome {name} to The Key of True! community. You can access <a href="https://x6nge.io">X6NGE</a> to obtain the tokens for the ongoing Airdrop</b>.'
    )
    lastsms = getLastSms(groupId, 0)
    if lastsms:
        for row in lastsms:
            print("se mando a imprimir en searchErrorCommand")
            await deleteMessage(bot, groupId, row[0])
    saveLastSms(groupId, msg_id, username, 0)

async def airdrop(update, context: CallbackContext):
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
            text = f'{userName}, The /airdrop command has to be sent by the group <a href="https://t.me/x6ngeio">TKT GROUP</a>. Visit our website <a href="https://x6nge.io">X6NGE</a> and our twitter page <a href="https://twitter.com/x6nge">TWITTER</a>, you can also join our channel <a href="https://t.me/thekeyoftrueTKT">CHANEL</a>. Thank you, have a nice day'
        )
        print(f"no son iguales /airdrop {groupId}")
        return

    isvalid = await storeUser(user_id, username)
    if isvalid is not None:
        lastsms = getLastSms(groupId, 1)
        if lastsms:
            for row in lastsms:
                print("se mando a imprimir en airdrop")
                await deleteMessage(bot, groupId, row[0])

    if isvalid == "user_ok":
        text_en = f'{userName}, you have successfully registered, you can go to <a href="https://x6nge.io">X6NGE</a> to get the tokens for the ongoing Airdrop, the code will reach the @TKT_VerificationCode account once you verify your username in the airdrop, for more information use the commands: /airdrop to check the status of your registration, /help to get help on the steps to follow for the airdrop, /link the links to our social networks and pages. /contract to obtain the tkt smart contract.'
        text_es = f'{userName}, Usted se ha registrado correctamente, puede acceder a <a href="https://x6nge.io">X6NGE</a> para obtener los <b>Token del Airdrop</b> en curso, el codigo llegara a la cuenta @TKT_VerificationCode una ves verifique su usuario en el airdrop, para mas informacion utilice los comandos: /airdrop para consultar el estado de su registro, /help para obtener ayuda sobre los pasos a seguir para el airdrop,  /link los link de nuestras redes sociales y paginas./contract para obtener el smart contract de TKT.'
        
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = text_es
        )
    elif isvalid == "user_register":
        text_en = f'{userName}, you have already registered previously, you can go to <a href="https://x6nge.io">X6NGE</a> to get the <b>Airdrop tokens.</b>, the code will reach the @TKT_VerificationCode account once you verify your username in the airdrop, for more information use the commands: /airdrop to check the status of your registration, /help to get help on the steps to follow for the airdrop, /link the links to our social networks and pages. /contract to obtain the tkt smart contract.'
        text_es = f'{userName}, usted se ha registrado con anterioridad, puede acceder a <a href="https://x6nge.io">X6NGE</a> para obtener los <b>Token del Airdrop</b> en curso, el codigo llegara a la cuenta @TKT_VerificationCode una ves verifique su usuario en el airdrop, para mas informacion utilice los comandos: /airdrop para consultar el estado de su registro, /help para obtener ayuda sobre los pasos a seguir para el airdrop,  /link los link de nuestras redes sociales y paginas./contract para obtener el smart contract de TKT.'
        
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = text_es
        )
    elif isvalid == "user_register_paid":
        text_en = f'{userName}, you have already received the Airdrop tokens.'
        text_es = f'{userName}, usted ya ha obtenido los tokens de el <b>Airdrop TKT</b>. visite nuestra web https://x6nge.io.'

        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = text_es
        )
    saveLastSms(groupId, msg_id, username, 1)

async def cmd_help_3(update, context: CallbackContext):
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
            text = f'{userName}, The /help command has to be sent by the group <a href="https://t.me/x6ngeio">TKT GROUP</a>. Visit our website <a href="https://x6nge.io">X6NGE</a> and our twitter page <a href="https://twitter.com/x6nge">TWITTER</a>, you can also join our channel <a href="https://t.me/thekeyoftrueTKT">CHANEL</a>. Thank you, have a nice day'
        )
        
        print(f"no son iguales /airdrop {groupId}")
        return

    lastsms = getLastSms(groupId, 3)
    if lastsms:
        for row in lastsms:
            print("se mando a imprimir en cmd_help_3")
            await deleteMessage(bot, groupId, row[0])

    text_en = f'{userName}, you have already received the Airdrop tokens.'
    text_es = f"""Hola {userName}, por favor siga los pasos para obtener los token:
        1- Acceda al airdrop mediante su link de referido o directamente por la pagina principal <a href="https://x6nge.io">X6NGE</a>
        2- Verifique su cuenta de Twitter.
        3- Para validar su usuario es necesario que valla a los ajustes de telegram y verifique que tiene nombre de usuario colocado.
            3.1 Cuando se desbloquee el campo de código, este le llegara de forma automática por la cuenta <a href="https://t.me/TKT_VerificationCode">TKT_VerificationCode</a>.
        4-Coloque su wallet para obtener los token.
        5- En caso de errores enviar correo a soporte supportit@x6nge.io o contacte con los admin.
            5.1- En el reporte incluya:
                5.1.1- Captura de pantalla del error
                5.1.2- Nombre de usuario de Twitter
                5.1.3- Nombre de usuario de Telegram
                5.1.4- Direccion de la wallet
                5.1.5- Tipo de dispositivo(Pc o Movil)
                5.1.6- Systema Operativo
                5.1.7- Nombre del Navegador que utilizó
            5.2- Esta informacion se utiliza para identificar mas rápido el problema, imitando el mismo ambiente en el que les dio el error.
            5.3- De esta forma la respuesta es mas rápida y se deja de perder tiempo pidiendo estos datos.
        Gracias y Feliz Dia. Atentamente el equipo de soporte de TKT."""

    await bot.sendMessage(
        chat_id=groupId,
        parse_mode="HTML",
        text = text_es
    )
    saveLastSms(groupId, msg_id, username, 3)

async def cmd_contract_4(update, context: CallbackContext):
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
            text = f'{userName}, The /help command has to be sent by the group <a href="https://t.me/x6ngeio">TKT GROUP</a>. Visit our website <a href="https://x6nge.io">X6NGE</a> and our twitter page <a href="https://twitter.com/x6nge">TWITTER</a>, you can also join our channel <a href="https://t.me/thekeyoftrueTKT">CHANEL</a>. Thank you, have a nice day'
        )
        print(f"no son iguales /airdrop {groupId}")
        return
    lastsms = getLastSms(groupId, 4)
    if lastsms:
        for row in lastsms:
            print("se mando a imprimir en cmd_contract_4")
            await deleteMessage(bot, groupId, row[0])

    text_en = f'{userName}, you have already received the Airdrop tokens.'
    text_es = f'Hola {userName}, Smart Contracts TKT 0x4A5049b997FEf8DA8cEBEEd8883F1C3130812E66'
    await bot.sendMessage(
        chat_id=groupId,
        parse_mode="HTML",
        text = text_es
    )
    saveLastSms(groupId, msg_id, username, 4)

async def cmd_link_5(update, context: CallbackContext):
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
            text = f'{userName}, The /help command has to be sent by the group <a href="https://t.me/x6ngeio">TKT GROUP</a>. Visit our website <a href="https://x6nge.io">X6NGE</a> and our twitter page <a href="https://twitter.com/x6nge">TWITTER</a>, you can also join our channel <a href="https://t.me/thekeyoftrueTKT">CHANEL</a>. Thank you, have a nice day'
        )
        return

    lastsms = getLastSms(groupId, 5)
    if lastsms:
        for row in lastsms:
            print("se mando a imprimir en cmd?link?5")
            await deleteMessage(bot, groupId, row[0])

    text_en = f'{userName}, you have already received the Airdrop tokens.'
    text_es = f"""Hola {userName}, Listado de enlaces de paginas y redes
        1- <a href="https://x6nge.io">Página Principal</a>
        2- <a href="https://medium.com/@thekeyoftrue">Blog Medium</a>
        3- <a href="https://x.com/x6nge">Cuenta de Twitter</a>
        4- <a href="https://x.com/supportit">Cuenta de soporte de Twitter</a>
        5- <a href="https://t.me/thekeyoftrueTKT">Canal de Telegram</a>
        6- <a href="https://t.me/x6ngeio">Grupo de telegram en español</a>
        7- <a href="https://medium.com/@thekeyoftrue">Canal de Whatsapp</a>
        8- <a href="https://instagram.com/x6nge?igshid=NTc4MTIwNjQ2YQ">Instagram</a>
        9- <a href="https://m.me/61551078728179">Facebook</a>
        10- <a href="https://medium.com/@thekeyoftrue">Discord</a>
    """
    await bot.sendMessage(
        chat_id=groupId,
        parse_mode="HTML",
        text = text_es
    )
    saveLastSms(groupId, msg_id, username, 5)

async def responseText(bot, text, groupId, msg_id, userName):
    for rude in rudeList:
        if rude in str(text):
            await deleteMessage(bot, groupId, msg_id, userName)
            await bot.sendMessage(
                chat_id=groupId,
                parse_mode="HTML",
                text = f'El mensaje de <b>{userName}</b> ha sido eliminado porque tenia palabras ofensivas o caracteres desconocidos.'
        )
    
    
    
    #await searchErrorCommand(bot, text, groupId, msg_id, userName)

async def searchErrorCommand(bot, text, groupId, msg_id, username):
    #/airdrop
    cmd1 = re.match('^airdrop$', text, re.I)
    cmd2 = re.match('^help$', text, re.I)
    cmd3 = re.match('^/[a-zA-Z0-9]*', text, re.I)
    
    if(cmd1 is not None):
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = f'{username}, el {cmd1.group()} commando esta mal escrito, le falta el /, los comandos son: /airdrop para consultar el estado de su registro, /help para obtener ayuda sobre los pasos a seguir para el airdrop,  /link los link de nuestras redes sociales y paginas. /contrat para obtener el smart contract de TKT.'
        )
        lastsms = getLastSms(groupId, 2)
        if lastsms:
            for row in lastsms:
                print("se mando a imprimir en searchErrorCommand")
                await deleteMessage(bot, groupId, row[0])
        saveLastSms(groupId, msg_id, username, 2)
        print(f"no son iguales /searchErrorCommand {groupId}")

    elif(cmd2 is not None):
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = f'{username}, el {cmd2.group()} commando esta mal escrito, le falta el /, los comandos son: /airdrop para consultar el estado de su registro, /help para obtener ayuda sobre los pasos a seguir para el airdrop,  /link los link de nuestras redes sociales y paginas./contract para obtener el smart contract de TKT.'
        )
        lastsms = getLastSms(groupId, 2)
        if lastsms:
            for row in lastsms:
                print("se mando a imprimir en searchErrorCommand")
                await deleteMessage(bot, groupId, row[0])
        saveLastSms(groupId, msg_id, username, 2)
        print(f"no son iguales /searchErrorCommand {groupId}")

    elif(cmd3 is not None):
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = f'{username}, el {cmd3.group()} commando esta mal escrito, los comandos son: /airdrop para consultar el estado de su registro, /help para obtener ayuda sobre los pasos a seguir para el airdrop,  /link los link de nuestras redes sociales y paginas./contract para obtener el smart contract de TKT.'
        )
        lastsms = getLastSms(groupId, 2)
        if lastsms:
            for row in lastsms:
                print("se mando a imprimir en searchErrorCommand")
                await deleteMessage(bot, groupId, row[0])
        saveLastSms(groupId, msg_id, username, 2)
        print(f"no son iguales /searchErrorCommand {groupId}")

async def searchHelp(bot, text, groupId, msg_id, username):
    #/airdrop
    cmd1 = re.match('^/[a-zA-Z0-9]*', text)
    cmd2 = re.match('^[aA]irdrop*', text)
    
    if(cmd1 is not None):
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = f'{username}, el {cmd1.group()} commando esta mal escrito, los comandos son: /airdrop para consultar el estado de su registro, /help para obtener ayuda sobre los pasos a seguir para el airdrop,  /link los link de nuestras redes sociales y paginas./contract para obtener el smart contract de TKT.'
        )
        lastsms = getLastSms(groupId, 2)
        if lastsms:
            for row in lastsms:
                print("se mando a imprimir en searchErrorCommand")
                await deleteMessage(bot, groupId, row[0])
        saveLastSms(groupId, msg_id, username, 2)
        print(f"no son iguales /searchErrorCommand {groupId}")

    if(cmd2 is not None):
        await bot.sendMessage(
            chat_id=groupId,
            parse_mode="HTML",
            text = f'{username}, el {cmd2.group()} commando esta mal escrito, los comandos son: /airdrop para consultar el estado de su registro, /help para obtener ayuda sobre los pasos a seguir para el airdrop,  /link los link de nuestras redes sociales y paginas./contract para obtener el smart contract de TKT.'
        )
        lastsms = getLastSms(groupId, 2)
        if lastsms:
            for row in lastsms:
                print("se mando a imprimir en searchErrorCommand")
                await deleteMessage(bot, groupId, row[0])
        saveLastSms(groupId, msg_id, username, 2)
        print(f"no son iguales /searchErrorCommand {groupId}")

async def deleteMessage(bot, chatId, messageId): #delete messages
    try:
        print('mensage a eliminar %s msgid %s'%(chatId, messageId))
        await bot.delete_message(chatId, messageId)
        await bot.delete_message(chatId, (messageId + 1))

    except Exception as e:
        print('mensage a eliminar error %s msgid %s'%(chatId, messageId))
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

def saveLastSms(groupId, msgid, username, tipo):
    try:
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
        cur.execute("CREATE TABLE IF NOT EXISTS LastMensage (id bigint(255) not null AUTO_INCREMENT, fecha int(11) not null, chatid bigint(255) not null, msgid bigint(255) not null, username varchar(255) not null, tipo int(1) not null default 0, primary key (id))  ENGINE = InnoDB")
        #print("ingresando un nuevo usuario final %s"% userid)
        sql="insert into LastMensage(fecha, chatid, msgid, username, tipo) values (%s, %s, %s, %s, %s)"
        datos=(timestamp(), groupId, msgid, username, tipo)
        cur.execute(sql, datos)
        #print("se inserto la fila correctamente final hash %s "% hash)
        conexion.commit()
        conexion.close()
        
        return "user_ok"
        
    except (Exception) as error:
        print("error en saveLastMessage")
        print(error)
    finally:
        if conexion is not None:
            conexion.close()

def getLastSms(chatid, tipo):
    try:
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
        cur.execute("CREATE TABLE IF NOT EXISTS LastMensage (id bigint(255) not null AUTO_INCREMENT, fecha int(11) not null, chatid bigint(255) not null, msgid bigint(255) not null, username varchar(255) not null, tipo int(1) not null default 0, primary key (id))  ENGINE = InnoDB")
        #cur.execute("CREATE INDEX userids ON telegram (userid)")

        cur.execute( "SELECT msgid, username FROM LastMensage where chatid=%s and tipo=%s", (chatid, tipo) )

        # Recorremos los resultados y los mostramos

        userlist = cur.fetchall()
        print(userlist)
        if(userlist is not None):
            for row in userlist:
                print(row)
                cur.execute( "DELETE FROM lastmensage WHERE chatid=%s and tipo=%s", (row[0], tipo) )
                conexion.commit()
            return userlist
        else:
            return False
        
    except (Exception) as error:
        print("error en getLastsms")
        print(error)
    finally:
        if conexion is not None:
            conexion.close()
            #print('Conexión finalizada.')

def timestamp():
    fecha = "%s" % datetime.now()
    timeret = time.mktime(datetime.strptime(fecha[:19], "%Y-%m-%d %H:%M:%S").timetuple())
    return timeret
