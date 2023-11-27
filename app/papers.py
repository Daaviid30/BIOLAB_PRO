import os
import conexion_db
from cifrado_simetrico import encriptar_dato, master_key
from inicio_sesion import pasar_identificador
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


# Guardamos el paper introducido, cifrandolo en el proceso
def guardar_paper(titulo, cuerpo):
    # Obtenemos la master key y el nombre de usuario para saber de quien es el paper
    password_key, identificador = master_key, pasar_identificador()
    # Encriptamos con un MAC la contraseña en claro para crear una clave de encriptación
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=333333)

    key = kdf.derive(password_key.encode('utf-8'))

    # Creamos un nonce y un aad necesarios para encriptar el cuerpo, usamos como aad el titulo del paper
    data = cuerpo.encode('utf-8')
    aad = titulo.encode('utf-8')
    chacha = ChaCha20Poly1305(key)
    nonce = os.urandom(12)

    encrypted_data = chacha.encrypt(nonce, data, aad)

    # Introducimos en la base de datos los datos del paper que necesitamos conservar
    try:
        insertar_datos = "INSERT INTO papers (user_name, titulo, cuerpo, salt, nonce) VALUES (%s, %s, %s, %s, %s)"
        values = (identificador, titulo, encrypted_data, salt, nonce)
        conexion_db.cursor.execute(insertar_datos, values)
        conexion_db.conexion.commit()
        mensaje = "El paper ha sido almacenado correctamente"
        return mensaje, "acceso"

    except:
        mensaje = "No se pudo guardar el paper"
        return mensaje, "error"

# Creamos una funcion que haga una consulta  a la bbdd y devuelva una lista con todos los titulos de los papers
# de un usuario
def listar_papers():
    consulta = "SELECT titulo, user_name FROM papers"
    conexion_db.cursor.execute(consulta)
    resultados = conexion_db.cursor.fetchall()

    return resultados

# Creamos una funcion que recupere el cuerpo para mostrarlo descifrado, si se ha modificado el texto dará error al mostrar
def recuperar_cuerpo(titulo, user_name):
    password = master_key

    try:
        consulta = "SELECT cuerpo, salt, nonce FROM papers WHERE user_name = %s AND titulo = %s"
        values = (user_name, titulo)
        conexion_db.cursor.execute(consulta, values)
        resultados = conexion_db.cursor.fetchall()

        kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=resultados[0][1],
        iterations=333333)
        key = kdf.derive(password.encode('utf-8'))

        chacha = ChaCha20Poly1305(key)
        cuerpo = chacha.decrypt(resultados[0][2], resultados[0][0], titulo.encode('utf-8'))
        cuerpo = cuerpo.decode('utf-8')
        mensaje = "El paper ha sido recuperado correctamente"
        estado = "acceso"

    except:
        cuerpo = None
        mensaje = "No se pudo recuperar el paper"
        estado = "error"

    return cuerpo, user_name, mensaje, estado