from image_processor_front import ImageProcessor_Front
from image_processor_top import ImageProcessor_Top
from generacion_figura import FigureGenerator

import cv2
import numpy as np
from copy import deepcopy
import os

class ImageProcessor:
    def __init__(self, matrix_size:int = 5) -> None:
        self.frame_front = None
        self.front = ImageProcessor_Front()

        self.frame_top = None
        self.top = ImageProcessor_Top()

        self.frame_side = None

        self.matrix3D = None
        self.generator = FigureGenerator()

        self.matrix_size = matrix_size
        self.matrix_front = np.full((self.matrix_size, self.matrix_size), -1)
        self.matrix_top = np.full((self.matrix_size, self.matrix_size), -1)

        self.debug = False
    
    def save_images(self) -> None:
        file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', "/")
        i = len(os.listdir(f'{file_path}/data/figuras_alzado/'))+1

        cv2.imwrite(f'{file_path}/data/figuras_alzado/Figura_{i}_L.png', self.frame_front)
        cv2.imwrite(f'{file_path}/data/figuras_planta/Figura_{i}_S.png', self.frame_top)
        cv2.imwrite(f'{file_path}/data/figuras_perfil/Figura_{i}_F.png', self.frame_side)
        print(f"\033[32m --- IMAGEN GUARDADA ---\033[0m")

    def process_image(self, frame_top:np.ndarray, frame_front:np.ndarray, frame_side:np.ndarray, mostrar:bool=False, debug:bool=False, save_images:bool = False)-> tuple:
        ''' 
        Ejecuta el flujo completo de procesamiento de una imagen para detectar colores y posiciones de cubos.
            - Almacena la imagen original y una copia para dibujar contornos.
            - Realiza el preprocesamiento para limpiar la imagen y detectar bordes.
            - Encuentra y filtra los contornos relevantes basándose en su tamaño.
            - Identifica los colores predominantes dentro de cada contorno y calcula las posiciones en una matriz.
            - Dibuja contornos y anotaciones sobre la imagen de salida.
            @param frame (numpy array) - Imagen de entrada en formato BGR.
            @param area_size (int) - Umbral mínimo de área para considerar un contorno como válido. Por defecto, 2000.
            @param mostrar (bool) - Si es True, muestra la imagen procesada.
            @return (tuple) - Una tupla con:
                - matrix (numpy array) - Matriz 5x5 que representa la cuadrícula con los colores detectados.
                - contour_img (numpy array) - Imagen con los contornos y anotaciones dibujados.
        '''
        self.frame_top = deepcopy(frame_top)
        self.frame_front = deepcopy(frame_front)
        self.frame_side = deepcopy(frame_side)
        self.debug = debug

        self.matrix_front, cont_img_front  = self.front.process_image(self.frame_front)
        self.matrix_top, cont_img_top = self.top.process_image(self.frame_top)
        self.matrix_side, cont_img_side = self.front.process_image(frame=self.frame_side)

        if self.debug:
            print('Matrix Front')
            print(self.matrix_front)
            print('\n\n')
            print('Matrix Top')
            print(self.matrix_top)
            print('\n\n')
            print('Matrix Side')
            print(self.matrix_side)

        if save_images:
            self.save_images()

        if mostrar:
            cv2.imshow('Image_Front', cont_img_front)
            cv2.imshow('Image_Top', cont_img_top)
            cv2.imshow('Image_Side', cont_img_side)

            self.generator.generate_figure_from_matrix(self.matrix_top, self.matrix_front, self.matrix_side, paint=True)

            cv2.destroyAllWindows()

if __name__ == '__main__':
    processor = ImageProcessor()

    cam_front = cv2.VideoCapture(0)
    cam_top = cv2.VideoCapture(9)
    cam_side = cv2.VideoCapture(5)
    
    if not cam_front.isOpened() or not cam_top.isOpened() or not cam_side.isOpened():
        print("Error: No se pudo abrir el vídeo.")
    else:
        _, frame_top = cam_top.read()
        _, frame_front = cam_front.read()
        _, frame_side = cam_side.read()
        processor.process_image(frame_top=frame_top, frame_front=frame_front, frame_side=frame_side, mostrar=True, debug=True, save_images=True)

