"""Proyecto de criptografía
Autores: David Martín (100472099) / Iván Llorente (100472242)"""

#Importamos las librerias necesarias para la ejecución de la app
import inicio_sesion
import os
import registro
import papers
import solicitud
import reconocimiento_facial
import firma_digital
from flask import Flask, request, render_template

# Creamos la aplicación Flask
app = Flask(__name__)

# Obtén la ruta al directorio actual del script
script_dir = os.path.dirname(__file__)

# Construye la ruta completa al archivo 'codificaciones.json'
codificaciones_path = os.path.join(script_dir, 'static', 'json', 'codificaciones.json')

# Construye la ruta completa al directorio 'pem'
pems_path = os.path.join(script_dir, 'static', 'pem')

# La ruta de inicio de la app será la pagina de log-in
@app.route('/')
def inicio():
    return render_template('login.html')

# La ruta /formulario dentro de la app llevará al manejo de datos del panel de log-in
@app.route('/formulario', methods=['POST'])
def procesar():
    user_name = request.form['user_name']
    password = request.form['password']
    
    mensaje_estado = inicio_sesion.login_usuario(user_name, password)
    if mensaje_estado[2] == "A":
        estado = reconocimiento_facial.reconocer_cara(codificaciones_path)
        if estado == "reconocido":
            mensaje_estado[0] = "Reconocimiento exitoso"
            return render_template('administrador.html', msg=mensaje_estado[0], msg_class=mensaje_estado[1])
        else:
            mensaje_estado[0] = "Reconocimiento erroneo" 
            mensaje_estado[1] = "error"   
    return render_template('login.html', msg=mensaje_estado[0], msg_class=mensaje_estado[1])

# La ruta /sing-up te lleva a la pagina de sing-up
@app.route('/sing-up')
def sing_up():
    return render_template('singup.html')


# La ruta /form-singup maneja los datos del formulario de registro
@app.route('/form-singup', methods=['POST'])
def form_singup():
    user_name = request.form['user_name']
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']
    password2 = request.form['password2']

    # La validación de datos se lleva a cabo en el fichero registro.py
    mensaje_estado = registro.registrar_usuario(user_name, name, surname, email, phone, password, password2)
    return render_template('singup.html', msg=mensaje_estado[0], msg_class=mensaje_estado[1])

# La ruta segundo factor, al ser invocada redirige a la pagina segundo_factor.html
@app.route('/segundo_factor')
def segundo_factor():
    return render_template('segundo_factor.html')

# La siguiente ruta maneja los datos reccibidos desde la pantalla de 2FA
@app.route('/form-2fa', methods=['POST'])
def form_2fa():
    codigo_verificacion = request.form['codigo']

    # Los datos los maneja el fichero inicio_sesion.py
    mensaje_estado = inicio_sesion.comprobar_codigo_verificación(codigo_verificacion)
    return render_template('segundo_factor.html', msg=mensaje_estado[0], msg_class=mensaje_estado[1], permiso=mensaje_estado[2])

# Creamos la ruta principal que te redirigira a la pagina principal.html
@app.route('/principal')
def principal():
    # En esta pagina se mostraran los papers disponibles de este usuario
    # La obtencion de los titulos se da en el fichero papers.py
    titulos = papers.listar_papers()
    return render_template('principal.html', titulos=titulos)

# En esta ruta se procesan los datos de los nuevos papers introducidos
@app.route('/form-principal', methods=['POST'])
def form_principal():
    titulo = request.form['titulo']
    cuerpo = request.form['cuerpo']

    # El procesamiento de los datos introducidos es dado por el fichero papers.py
    mensaje, estado, permiso = papers.guardar_paper(titulo, cuerpo, pems_path)
    titulos = papers.listar_papers()

    # Al introducir nuevos papers se redirige a la misma pagina pero con la lista de titulos actualizada
    if permiso != 'A':
        return render_template('principal.html', msg=mensaje, msg_class=estado, titulos=titulos)
    else:
        return render_template('principal-admin.html', msg=mensaje, msg_class=estado, titulos=titulos)
    

@app.route('/form-solicitud', methods=['POST'])
def form_solicitud():
    titulos = papers.listar_papers()
    mensaje, estado = solicitud.anadir_solicitud()
    return render_template('principal.html', msg=mensaje, msg_class=estado, titulos=titulos)

# Esta ruta muestra el paper seleccionado
@app.route('/paper', methods=['POST'])
def paper():
    titulo_username = request.form['titulo']
    # Dividir la cadena utilizando el separador "-"
    partes = titulo_username.split('-')
    # Eliminar espacios adicionales alrededor del título y el nombre de usuario
    titulo = partes[0].strip()
    user_name = partes[1].strip()

    cuerpo, user_name, mensaje, estado, permiso = papers.recuperar_cuerpo(titulo, user_name)
    # Si no existe cuerpo en el paper, significa que no se pudo recuperar dicho paper, por lo que aparecera un 
    # mensaje de error
    if not cuerpo:
        titulos = papers.listar_papers()
        if permiso != 'A':
            return render_template('principal.html', msg=mensaje, msg_class=estado, titulos=titulos)
        else:
            return render_template('principal-admin.html', msg=mensaje, msg_class=estado, titulos=titulos)
    return render_template('paper.html', titulo=titulo, cuerpo=cuerpo, user=user_name, msg=mensaje, msg_class=estado)

@app.route('/administrador')
def administrador():
    return render_template('administrador.html')

@app.route('/volver-administrador', methods=['POST'])
def volver_administrador():
    return render_template('administrador.html')

@app.route('/solicitudes', methods=['POST'])
def solicitudes():

    solicitudes = solicitud.recuperar_solicitudes()
    return render_template('solicitudes.html', solicitudes=solicitudes)

@app.route('/aceptar-solicitud', methods=['POST'])
def aceptar_solicitud():
    user_name = request.form['user_name']
    solicitud.aceptar_solicitud(user_name)
    # Como el usuario ha sido aceptado y se le han dado permisos de doctor, es necesario generar sus claves
    firma_digital.generar_claves(pems_path, user_name)

    solicitudes = solicitud.recuperar_solicitudes()
    return render_template('solicitudes.html', solicitudes=solicitudes)

@app.route('/denegar-solicitud', methods=['POST'])
def denegar_solicitud():
    user_name = request.form['user_name']
    solicitud.denegar_solicitud(user_name)

    solicitudes = solicitud.recuperar_solicitudes()
    return render_template('solicitudes.html', solicitudes=solicitudes)

@app.route('/principal-admin', methods=['POST'])
def principal_admin():
    titulos = papers.listar_papers()
    return render_template('principal-admin.html', solicitudes=solicitudes, titulos=titulos)


# Ejecución del programa
if __name__ == '__main__':
    app.run(debug=True)