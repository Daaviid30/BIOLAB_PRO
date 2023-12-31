import conexion_db
import correo_2FA
from cifrado_simetrico import desencriptar_dato
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

# Definimos una serie de variables globales que luego utilizaremos en otros ficheros y funciones
codigo_verificacion = None
password_key = None
identificador = None

# Creamos la funcion que manejara y comprobara los datos introducidos en el formulario de login
def login_usuario(user_name, password):
    global codigo_verificacion
    global password_key
    global identificador
    # Damos valor a las variables globales password e identificador
    password_key = password
    identificador = user_name
    # En caso de que todos los datos introducidos sean correctos y no de error, se cambiara el valor a True
    error = True

    # Consultamos los datos relevantes para el log-in en la base de datos
    consulta = "SELECT user_name, salt, encryped_pass, email, permiso FROM usuarios WHERE user_name = %s"
    values = (user_name,)
    conexion_db.cursor.execute(consulta, values)
    # Guardamos los resultados de la consulta en una lista de tuplas (solo una tupla en este caso -> 1 coincidencia)
    resultados = conexion_db.cursor.fetchall()

    # Si la lista recibida de la consulta está vacía significará que no hay ningún usuario registrado con ese nombre usuario.
    if len(resultados) == 0:
        respuesta = 'El usuario no tiene una cuenta activa en BioLab'
    # Si el usuario está registrado pasamos a comprobar si las contraseñas coinciden.
    else:
        permiso = resultados[0][4]
        # Recuperamos el salt para añadirselo a la contraseña introducida por el usuario
        salt = resultados[0][1]
        # Recuperamos la contraseña correcta del usuario para comprobarla con la introducida
        real_pass = resultados[0][2]
        # Convertimos la contraseña en bytes y utilizamos el método de derivacion Scrypt
        password = password.encode('utf-8')
        metodo = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
        try:
            # Comparamos ambas contraseñas, si son iguales (.verify devuelve None) la contraseña es correcta
            metodo.verify(password, real_pass)
            respuesta = f"La contraseña es correcta, bienvenido {user_name}"
            error = False
            if permiso != "A":
                codigo_verificacion = correo_2FA.mandar_correo(desencriptar_dato(resultados[0][3]))
            return [respuesta, "acceso", permiso]
        except:
            # Si ambas contraseñas no coinciden entonces saltará una excepción de cryptography
            respuesta = f"La contraseña es incorrecta"
    # Devolvemos un mensaje en la pagina de log-in, este varía dependiendo de si la contraseña es correcta o no
    if error == True:    
        return [respuesta, "error", None]

# Creamos la funcion que comprueba si el codigo de verificacion mandado por correo es correcto
def comprobar_codigo_verificación(codigo_introducido):
    global codigo_verificacion
    global identificador
    if str(codigo_introducido) == str(codigo_verificacion):
        respuesta = "Codigo de verificacion correcto"
        estado = "acceso"
        # Recuperamos el nivel de privilegios que tiene el user
        consulta = "SELECT permiso FROM usuarios WHERE user_name = %s"
        values = (identificador,)
        conexion_db.cursor.execute(consulta, values)
        # Guardamos los resultados de la consulta en una lista de tuplas (solo una tupla en este caso -> 1 coincidencia)
        resultados = conexion_db.cursor.fetchall()
    else:
        respuesta = "Código de verificacion incorrecto"
        estado = "error"
    return [respuesta, estado, resultados[0][0]]

def pasar_identificador():
    global identificador
    return identificador