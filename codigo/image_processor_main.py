from image_processor_front import ImageProcessor_Front
from image_processor_top import ImageProcessor_Top
from generacion_figura import FigureGenerator

import cv2
import numpy as np
from copy import deepcopy
import os
import matplotlib.pyplot as plt

class ImageProcessor:
    ''' 
    Clase que procesa las imagenes de las 3 perspectivas de una figura para representar la figura tridimensional resultante.
    Este proceso se realiza a traves de tecnicas de visión tradicional las cuales estan contenidas en las clases importadas
    ImageProcessor_Front e ImageProcessor_Top. A su vez, el procesamiento de las matrices resultantes de las clases anteriores
    es procesado en la figura 3D a traves de la clase FigureGenerator.

    Esta clase realiza los siguientes pasos:
        - Recoge las imagenes de las diferentes cámaras.
        - Procesa las 3 imagenes a traves de las clases correspondientes, obteniendo la matriz resultante y la imagen con el resultado.
        - Procesa las 3 matrices a traves de la clase FigureGenerator mostrando la figura resultante del proceso.

    Métodos:
        - __init__() - Inicializa el objeto, inicializa las clases a utilizar y define las variables necesarias del programa.
        - _save_images() - En caso de solicitarlo, guarda las imagenes introducidas en la clase
        - process_image() - Procesa las imagenes y obtiene la figura tridimensional resultante
    '''
    def __init__(self, matrix_size:int = 5) -> None:
        ''' 
        Inicializa los atributos de la clase.
        - matrix_size: Tamaño de la matriz cuadrada que representa la cuadrícula de colores (por defecto, 5x5).
        - matrix: Matriz inicializada con valores -1, que se usará para almacenar los colores detectados.
        - frame: Imagen original introducida en la clase.
            @param matrix_size (int) - Tamaño de la matriz cuadrada. Por defecto, 5.
        '''
        self.procesador_lateral = ImageProcessor_Front()
        self.procesador_superior = ImageProcessor_Top()
        self.generator = FigureGenerator()

        self.frame_perfil = None
        self.frame_planta = None
        self.frame_alzado = None

        self.matrix_size = matrix_size
        self.matrix_alzado = np.full((self.matrix_size, self.matrix_size), -1)
        self.matrix_planta = np.full((self.matrix_size, self.matrix_size), -1)
        self.matrix_perfil = np.full((self.matrix_size, self.matrix_size), -1)


    def _save_images(self) -> None:
        """
        Guarda las imagenes capturadas en la carpeta data del repositorio
            @return None
        """
        file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', "/")
        i = len(os.listdir(f'{file_path}/data/figuras_alzado/'))+1

        cv2.imwrite(f'{file_path}/data/figuras_alzado/Figura_{i}_F.png', self.frame_front)
        cv2.imwrite(f'{file_path}/data/figuras_planta/Figura_{i}_S.png', self.frame_top)
        cv2.imwrite(f'{file_path}/data/figuras_perfil/Figura_{i}_L.png', self.frame_side)
        print(f"\033[32m --- IMAGEN GUARDADA ---\033[0m")


    def process_image(self, frame_alzado:np.ndarray, frame_perfil:np.ndarray, frame_planta:np.ndarray, mostrar:bool=False, debug:bool=False, save_images:bool = False)-> tuple:
        ''' 
        Recoge las imagenes de las diferentes camaras, las procesa y muestra la figura 3D resultante
            - Almacena la imagen original.
            - Realiza el procesamiento para obtener la matriz resultante de la imagen.
            - Analiza las diferentes matrices para mostrar la figura final.
                @param frame_alzado (np.nd_array) - Imagen capturada por la camara con la perspectiva del alzado
                @param frame_perfil (np.nd_array) - Imagen capturada por la camara con la perspectiva del perfil
                @param frame_planta (np.nd_array) - Imagen capturada por la camara con la perspectiva del planta
                @param mostrar = False (bool) - Muestra las imagenes resultantes del proceso
                @param debug = False (bool) - Muestra los estados intermedios del proceso
                @param save_images = False (bool) - Almacena las imagenes en la carpeta data
        '''
        # Guardado de las Imagenes
        self.frame_alzado = deepcopy(frame_alzado)
        self.frame_perfil = deepcopy(frame_perfil)
        self.frame_planta = deepcopy(frame_planta)

        # Procesamiento de las Imagenes
        self.matrix_alzado, img_final_alzado  = self.procesador_lateral.process_image(self.frame_alzado, debug=debug)
        self.matrix_perfil, img_final_perfil = self.procesador_lateral.process_image(frame=self.frame_perfil, debug=debug)
        self.matrix_planta, img_final_planta = self.procesador_superior.process_image(self.frame_planta, debug=debug)


        if mostrar: # En caso de querer mostrar resultados Finales
            print('Matriz Alzado')
            print(self.matrix_alzado)
            print('\n\n')
            print('Matriz Perfil')
            print(self.matrix_perfil)
            print('\n\n')
            print('Matriz Planta')
            print(self.matrix_planta)
            
            fig = plt.figure(figsize=(10,7))

            ax = fig.add_subplot(2,2, 1)
            img_final_alzado = cv2.cvtColor(img_final_alzado, cv2.COLOR_BGR2RGB)
            ax.imshow(img_final_alzado)
            ax.set_title('Imagen Alzado')
            ax.axis('off')

            ax = fig.add_subplot(2, 2, 2)
            img_final_perfil = cv2.cvtColor(img_final_perfil, cv2.COLOR_BGR2RGB)
            ax.imshow(img_final_perfil)
            ax.set_title('Imagen Perfil')
            ax.axis('off')

            ax = fig.add_subplot(2, 2, 3)
            img_final_planta = cv2.cvtColor(img_final_planta, cv2.COLOR_BGR2RGB)
            ax.imshow(img_final_planta)
            ax.set_title('Imagen Planta')
            ax.axis('off')
            

            fig_3d = self.generator.generate_figure_from_matrix(self.matrix_planta, self.matrix_perfil, self.matrix_alzado, paint=mostrar, tkinter=True)
            ax = fig.add_subplot(2, 2, 4)
            fig_3d.savefig("/tmp/figura_secundaria.png", format="png")
            ax.set_title('Figura 3D')
            ax.axis('off')
            ax.imshow(plt.imread("/tmp/figura_secundaria.png"))

            # Ajustar el espaciado entre los subgráficos
            plt.tight_layout()

            # Mostrar todos los gráficos
            plt.show()
        else:
            # Mostrar la figura tridimensional
            fig_3d = self.generator.generate_figure_from_matrix(self.matrix_planta, self.matrix_alzado, self.matrix_perfil, paint=True)


if __name__ == '__main__':
    processor = ImageProcessor()

    use_cam = False # Si se quiere trabajar directamente de la camara (True) o a traves de imagenes (False)
    num_figure = 8 # ID de la figura guardada en imagenes
    mostrar = True # Si se quiere enseñar el resultado final de las diferentes cámaras = True
    debug = False # Si se quiere mostrar el proceso intermedio de cada cámara = True
    save_image = False # Si se quieres guardar las imagenes mostradas por la cámara = True
    error = False

    if use_cam:    
        # Modificar el ID de la cámara en caso de cambiar
        cam_alzado = cv2.VideoCapture(0)
        cam_perfil = cv2.VideoCapture(5)
        cam_planta = cv2.VideoCapture(9)
        
        if not cam_alzado.isOpened() or not cam_perfil.isOpened() or not cam_planta.isOpened():
            print("Error: No se pudo abrir el vídeo.")
            raise ValueError('ID de camaras incorrecto')
        else:
            success_alzado, frame_alzado = cam_alzado.read()
            success_perfil, frame_perfil = cam_perfil.read()
            success_planta, frame_planta = cam_planta.read()

            if not success_alzado and not success_perfil and not success_planta:
                error = True
                raise ValueError('Error al leer de las camaras')
    else:
        save_image = False
        file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', "/")
        frame_alzado = cv2.imread(f'{file_path}/data/figuras_alzado/Figura_{num_figure}_F.png')
        frame_perfil = cv2.imread(f'{file_path}/data/figuras_perfil/Figura_{num_figure}_L.png')
        frame_planta = cv2.imread(f'{file_path}/data/figuras_planta/Figura_{num_figure}_S.png')
    
    processor.process_image(frame_alzado=frame_alzado, frame_perfil=frame_perfil, frame_planta=frame_planta, mostrar=mostrar, debug=debug, save_images=save_image)

