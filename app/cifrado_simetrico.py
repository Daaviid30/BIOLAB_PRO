from cryptography.fernet import Fernet

master_key = "SwxYuBMGNB8pgRb8WU_lV7e0rrrgE8nhHoOQkaQlbqI="

def encriptar_dato(dato):

    cifrado_simetrico = Fernet(master_key)

    return cifrado_simetrico.encrypt(dato.encode('utf-8'))

def desencriptar_dato(dato):

    cifrado_simetrico = Fernet(master_key)

    return cifrado_simetrico.decrypt(dato).decode('utf-8')
