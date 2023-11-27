import conexion_db
from inicio_sesion import pasar_identificador
from cifrado_simetrico import desencriptar_dato


def obtener_nombre_completo(user_name):
    consulta = "SELECT nombre, apellidos FROM usuarios WHERE user_name = %s"
    values = (user_name,)
    conexion_db.cursor.execute(consulta, values)
    resultado = conexion_db.cursor.fetchall()

    nombre_completo = desencriptar_dato(resultado[0][0]) + " " + desencriptar_dato(resultado[0][1])
    return nombre_completo

def recuperar_solicitudes():
    # Solo listamos las solicitudes que no han sido ya rechazadas
    consulta = "SELECT user_name, rechazada FROM solicitudes"
    conexion_db.cursor.execute(consulta)
    resultados = conexion_db.cursor.fetchall()
    solicitudes = []
    # En la solicitud mostramos tanto el nombre de usuario como el nombre completo de la persona
    for resultado in resultados:
        if resultado[1] == 0:
            nombre_completo = obtener_nombre_completo(resultado[0])
            solicitudes.append([resultado[0], nombre_completo])

    return solicitudes

def anadir_solicitud():
    user_name = pasar_identificador()

    # Comprobar si ya tiene permiso de doctor
    consulta = "SELECT permiso FROM usuarios WHERE user_name = %s"
    values = (user_name,)
    conexion_db.cursor.execute(consulta, values)
    permiso = conexion_db.cursor.fetchall()[0][0]
    if permiso[0] == 'D':
        return "Ya tienes permisos de doctor", "error"
    

    consulta = "SELECT user_name, rechazada FROM solicitudes WHERE user_name = %s"
    values = (user_name,)
    conexion_db.cursor.execute(consulta, values)
    resultado = conexion_db.cursor.fetchall()
    
    # Comprobar si ya ha solicitado permiso
    if len(resultado) != 0:
        # Comprobar si la solicitud fue rechazada
        if resultado[0][1] == 1:
            mensaje = "Su solicitud fue rechazada previamente. Contacte con un administrador"
        else:    
            mensaje = "Ya has solicitado permisos de doctor"
        estado = "error"
    # Si no ha solicitado permiso, se añade a la base de datos    
    else:
        consulta = "INSERT INTO solicitudes (user_name, rechazada) VALUES (%s, %s)"
        values = (user_name, 0,)
        conexion_db.cursor.execute(consulta, values)
        conexion_db.conexion.commit()
        mensaje = "Se ha solicitado el permiso correctamente"
        estado = "acceso"
    
    return mensaje, estado
