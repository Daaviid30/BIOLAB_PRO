import conexion_db
from inicio_sesion import pasar_identificador


def recuperar():
    consulta = "SELECT user_name FROM solicitudes"
    conexion_db.cursor.execute(consulta)
    resultados = conexion_db.cursor.fetchall()

    return resultados

def anadir_solicitud():
    user_name = pasar_identificador()
    consulta = "SELECT user_name FROM solicitudes WHERE user_name = %s"
    values = (user_name,)
    conexion_db.cursor.execute(consulta, values)
    resultado = conexion_db.cursor.fetchall()
    
    if len(resultado) != 0:
        mensaje = "Ya has solicitado permiso de doctor"
        estado = "error"
    else:
        consulta = "INSERT INTO solicitudes (user_name) VALUES (%s)"
        values = (user_name,)
        conexion_db.cursor.execute(consulta, values)
        conexion_db.conexion.commit()
        mensaje = "Se ha solicitado el permiso correctamente"
        estado = "acceso"
    
    return mensaje, estado
