import re
import conexion_db
import os
from cifrado_simetrico import encriptar_dato
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def registrar_usuario(user_name, name, surname, email, phone, password, password2):

    error = True

    # Realizamos varias comprobaciones para que la inserccion de datos en la bbdd sea correcta
    if not (5 < len(user_name) < 40):
        respuesta = 'El nombre de usuario debe tener entre 5 y 40 caracteres'
    
    elif len(name) > 30:
        respuesta = 'El nombre no puede superar los 30 carácteres'

    elif len(surname) > 100:
        respuesta = 'Los apellidos no pueden superar los 100 carácteres'

    elif len(email) > 150:
        respuesta = 'El email no puede tener mas de 150 carácteres'

    elif not(re.match('^[0-9]{9}$', phone)):
        respuesta = 'El teléfono está formado por 9 dígitos'

    # Utilizamos una expresión regular para indicar que la password debe de tener minimo: una mayúscala
    # una minúscula y un dígito, ademas debe tener al menos 10 carácteres
    elif not(re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+", password)) or len(password) < 8:
        respuesta = 'La contraseña debe de ser de 8 caracteres mínimo y debe tener una mayúscula, una minúscula y un digito.'

    # Realizamos una comprobación para que el usuario se asegure de insertar bien la contraseña
    elif password != password2:
        respuesta = 'Las contraseñas introducidas no coinciden'
    
    else:
        consulta = "SELECT user_name FROM usuarios WHERE user_name = %s"
        values = (user_name,)
        conexion_db.cursor.execute(consulta, values)
        # Guardamos los resultados de la consulta en una lista de tuplas (solo una tupla en este caso -> 1 coincidencia)
        resultados = conexion_db.cursor.fetchall()
        # En caso de que ya exista el usuario no guardamos en la bbdd
        if len(resultados) != 0:
            respuesta = "Ya existe un usuario con ese nombre de usuario registrado"
            return [respuesta, "error"]
        # Una vez que todos los datos son correctos, procedemos a su insercción en la base de datos
        # Encriptamos la contraseña para almacenarla de forma segura en la bbdd
        # Generamos un salt en forma de bytes aleatorio para cada contraseña
        salt = os.urandom(16)
        # Transformamos a bytes la contraseña pasada por el formulario
        password = password.encode('utf-8')
        # Utilizamos el método de encriptación Scrypt
        metodo = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
        encryped_password = metodo.derive(password)

        # Insertamos todos los datos en la bbdd, utilizando %s para evitar inyecciones SQL.
        query = "INSERT INTO usuarios (user_name, nombre, apellidos, email, telefono, salt, encryped_pass, permiso) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (user_name, encriptar_dato(name), encriptar_dato(surname), encriptar_dato(email)
                  , encriptar_dato(phone), salt, encryped_password, 'U')

        conexion_db.cursor.execute(query, values)
        conexion_db.conexion.commit()
        respuesta = "El usuario ha sido creado correctamente"
        error = False
        return [respuesta, "acceso"]
        

    # Mostramos el mensaje correspondiente según se haya dado una respuesta u otra.
    if error == True:
        return [respuesta, "error"]