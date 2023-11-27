import cv2
from mtcnn.mtcnn import MTCNN
import numpy as np
import keyboard
import json

detector_mtcnn = MTCNN()

cap = cv2.VideoCapture(0)

codificaciones = []

while True:
    # Capturar la imagen actual desde la cámara
    ret, frame = cap.read()

    # Mostrar la imagen actual con los rectángulos dibujados alrededor de las caras
    cv2.imshow("Reconocimiento Facial", frame)

    # Verificar si se presionó la tecla 'c' para capturar la cara
    if keyboard.is_pressed('c'):
        # Detectar caras con MTCNN
        resultados = detector_mtcnn.detect_faces(frame)

        for resultado in resultados:
            # Extraer las coordenadas de la caja delimitadora
            x, y, w, h = resultado['box']

            # Extraer la región de la cara
            cara = frame[y:y+h, x:x+w]

            # Redimensionar la cara a un tamaño fijo
            cara_redimensionada = cv2.resize(cara, (96, 96))

            # Codificar la cara como un vector de características
            codificacion_actual = np.array(cara_redimensionada.flatten())

            # Almacenar la codificación en la lista
            codificaciones.append(codificacion_actual)

    # Romper el bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()


# ...

# Convertir las codificaciones de ndarray a list antes de guardar en JSON
codificaciones_en_lista = [codificacion.tolist() for codificacion in codificaciones]

# Crear un diccionario para almacenar las codificaciones
codificaciones_dict = {'codificaciones': codificaciones_en_lista}

# Guardar el diccionario en un archivo JSON
with open('app/static/json/codificaciones.json', 'w') as json_file:
    json.dump(codificaciones_dict, json_file)