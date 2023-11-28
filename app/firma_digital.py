from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
import conexion_db


def generar_claves(static_path, user_name):
    path_to_private_key_pem = static_path + "/private_keys/" + user_name + ".pem"
    csr_path = static_path + "/solicitudes_certificado/" + user_name + ".pem"

    # Generar la clave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Guardamos la clave privada en un archivo .pem
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(b'password for digital signature')
    )

    with open(path_to_private_key_pem, 'wb') as pem_manager:
        pem_manager.write(pem)

    # Generar CSR (solicitud de certificado) con información del sujeto
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"ES"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"MADRID"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"UC3M"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u"INF"),
        x509.NameAttribute(NameOID.COMMON_NAME, user_name),
    ])

    csr = x509.CertificateSigningRequestBuilder().subject_name(subject).sign(private_key, hashes.SHA256())

    # Guardar CSR en un archivo
    with open(csr_path, 'wb') as csr_manager:
        csr_manager.write(csr.public_bytes(serialization.Encoding.PEM))


def firma_digital(static_path, user_name):
    path_to_private_key_pem = static_path + "/private_keys/" + user_name + ".pem"
    path_to_public_key_pem = static_path + "/certificados/" + user_name + ".pem"

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

    # Obtenemos el certificado del usuario que garantiza su identidad y contiene su clave pública
    with open(path_to_public_key_pem, 'rb') as cert_file:
        certificado = cert_file.read()

    # Cargamos el certificado (está en pem) y lo parseamos para obtener la clave pública
    certificado = x509.load_pem_x509_certificate(certificado, default_backend())
    public_key = certificado.public_key()

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