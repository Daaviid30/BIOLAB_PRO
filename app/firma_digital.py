from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import conexion_db


def generar_claves(pems_path, user_name):
    path_to_private_key_pem = pems_path + "/" + user_name + "_private_key.pem"

    # Generar la clave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Generamos la clave publica, la transformamos a bytes y la guardamos en la base de datos
    public_key = private_key.public_key()
    public_key_der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    consulta = "UPDATE usuarios SET public_key = %s WHERE user_name = %s"
    values = (public_key_der, user_name,)
    conexion_db.cursor.execute(consulta, values)
    conexion_db.conexion.commit()

    # Guardamos la clave privada en un archivo .pem
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(b'password for digital signature')
    )

    with open(path_to_private_key_pem, 'wb') as pem_manager:
        pem_manager.write(pem)


def firma_digital(pems_path, user_name):
    path_to_private_key_pem = pems_path + "/" + user_name + "_private_key.pem"

    # El usuario tendría guardada su clave privada en su dispositivo, y con ella firmaría el mensaje
    with open(path_to_private_key_pem, 'rb') as pem_manager:
        private_key = serialization.load_pem_private_key(
            pem_manager.read(),
            password=b'password for digital signature'
        )

    message = b"message to be signed"
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # El usuario envía el mensaje firmado, por lo que el sistema, gracias a la clave pública del usuario, 
    # puede verificar la firma
    consulta = "SELECT public_key FROM usuarios WHERE user_name = %s"
    values = (user_name,)
    conexion_db.cursor.execute(consulta, values)
    resultado = conexion_db.cursor.fetchall()
    public_key = serialization.load_der_public_key(resultado[0][0])

    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        mensaje = "Firma digital verificada"
        estado = "acceso"

    except:
        mensaje = "Error al verificar la firma digital"
        estado = "error"

    return mensaje, estado