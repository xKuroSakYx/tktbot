from configparser import ConfigParser
import mysql.connector
import hashlib


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

def calculate_sha256(data):
    password = "ecfbeb0a78c04e5.*692a4*..e5c___69..0f9c*f1f**0cdae__f723e6346f2b8af187$@7f21d4b4$$3a0b33c1.__26afd40a$$3b**.125ce8a$$457.*b0bba"

    data = "%s %s"%(data, password)
    if isinstance(data, str):
        data = data.encode()
    md5hash = hashlib.md5(data).hexdigest().encode()
    sha256_hash = hashlib.sha256(md5hash).hexdigest()
    
    return sha256_hash
