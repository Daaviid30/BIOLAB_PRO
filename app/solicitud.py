import conexion_db
from inicio_sesion import pasar_identificador


def recuperar():
    consulta = "SELECT user_name FROM solicitudes"
    conexion_db.cursor.execute(consulta)
    resultados = conexion_db.cursor.fetchall()

    return resultados

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
            mensaje = "Ya has solicitado permiso de doctor"
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
