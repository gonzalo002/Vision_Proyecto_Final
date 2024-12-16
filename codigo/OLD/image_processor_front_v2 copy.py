import cv2
import numpy as np
from copy import deepcopy

class ImageProcessor_Front:
    '''
    Clase que procesa imágenes para detectar y clasificar cubos en función de su color, forma y tamaño.
    Utiliza técnicas de procesamiento de imágenes como la detección de bordes, segmentación de contornos
    y análisis del color dominante.
    '''
        
    def __init__(self, matrix_size:int=5) -> None:
        '''
        Inicializa los atributos de la clase.
        @param matrix_size (int): Tamaño de la matriz 5x5.
        '''
        self.matrix_size = matrix_size
        self.matrix = np.full((self.matrix_size, self.matrix_size), -1)  # Matriz de colores detectados.
        self.contour_img = None  # Imagen donde se dibujan los contornos.
        self.frame = None  # Imagen original.
        self.debug = False  # Flag para habilitar el modo debug.
        self.filtered_colors = []  # Lista de imágenes filtradas por color.
        
    def _preprocess_image(self) -> np.ndarray:
        '''
        Convierte la imagen a escala de grises, aplica detección de bordes y limpieza morfológica.
        @return morph_clean (numpy array) - Imagen binaria con los bordes detectados y limpiados.
        '''
        self.filtered_colors = self._get_contrast_img(self.frame)
        cropper_frame = self._get_cubes_location(self.filtered_colors)
        
        gray = cv2.cvtColor(cropper_frame, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)  # Filtro Sobel en X
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)  # Filtro Sobel en Y
        sobel_combined = cv2.magnitude(sobelx, sobely)
        sobel_combined = np.uint8(sobel_combined)
        
        _, sobel_umbralized = cv2.threshold(sobel_combined, 150, 255, cv2.THRESH_BINARY)
        kernel = np.ones((7, 7), np.uint8)
        sobel_umbralized = cv2.morphologyEx(sobel_umbralized, cv2.MORPH_CLOSE, kernel)

        new_gray = cv2.bitwise_or(gray, gray, mask=cv2.bitwise_not(sobel_umbralized))
        _, new_gray = cv2.threshold(new_gray, 2, 255, cv2.THRESH_BINARY)
        new_gray = cv2.morphologyEx(new_gray, cv2.MORPH_CLOSE, kernel)
        
        edges = cv2.Canny(new_gray, 20, 200)
        
        if self.debug:
            cv2.imshow('Sobel Combined', sobel_combined)
            cv2.imshow('Sobel Umbralized', sobel_umbralized)
            cv2.imshow('New Gray', new_gray)
            cv2.imshow('Canny', edges)
        
        return new_gray

    def _get_cubes_location(self, contrast_images:list) -> np.ndarray:
        '''
        Combina las imágenes de contraste de colores y aplica la máscara para detectar los cubos.
        @param contrast_images (list) - Lista de imágenes filtradas por colores.
        @return result (numpy array) - Imagen con los cubos detectados.
        '''
        mask = np.zeros_like(self.frame[:,:,0]) 
        for img in contrast_images:
            mask_combined = cv2.bitwise_or(mask, img)  
        result = cv2.bitwise_and(self.frame, self.frame, mask=mask_combined)

        if self.debug:
            cv2.imshow('Cube Location Mask', mask_combined)
            cv2.imshow('Cube Location', result)

        return result

    def _get_contrast_img(self, frame:np.ndarray) -> list:
        '''
        Convierte la imagen a espacio HSV y filtra los colores en el rango de rojo, verde, azul y amarillo.
        @return resultado (list) - Lista de imágenes filtradas por colores.
        '''
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        height, width = hsv.shape[:2]
        black_mask = np.zeros((height, width), dtype=np.uint8)
        
        lower_green = np.array([30, 150, 0])   
        upper_green = np.array([110, 255, 255])
        
        lower_red1 = np.array([0, 70, 70], np.uint8)
        upper_red1 = np.array([20, 255, 255], np.uint8)
        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([179, 255, 255])
        
        lower_blue = np.array([100, 135, 115], np.uint8)
        upper_blue = np.array([130, 255, 255], np.uint8)
        
        lower_yellow = np.array([20, 70, 30], np.uint8)
        upper_yellow = np.array([60, 255, 255], np.uint8)
        
        lower_values = [lower_red1, lower_green, lower_blue, lower_yellow, lower_red2]
        upper_values = [upper_red1, upper_green, upper_blue, upper_yellow, upper_red2]
        filtered_images = []
        
        for i in range(len(lower_values)):
            mask = cv2.inRange(hsv, lower_values[i], upper_values[i]) 
            value_threshold = 70
            value_mask = hsv[:, :, 2] > value_threshold
            value_mask = np.uint8(value_mask) * 255
            mask = cv2.bitwise_and(mask, mask, mask=value_mask)

            filtered_image = cv2.bitwise_and(frame, frame, mask=mask)
            filtered_images.append(filtered_image)

        filtered_images[0] = cv2.bitwise_or(filtered_images[0], filtered_images[4])
        filtered_images.pop(4)

        contrast_images = []
        kernel = np.ones((5, 5), np.uint8)
        for img in filtered_images:
            contrast_img = cv2.convertScaleAbs(img, alpha=1.3, beta=1)
            contrast_img = cv2.morphologyEx(contrast_img, cv2.MORPH_CLOSE, kernel)
            contrast_images.append(contrast_img)
        
        resultado = []
        for i, img in enumerate(contrast_images):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, inv = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
            resultado.append(inv)

        return resultado

    def _filter_contours(self, contours:list) -> list:
        '''
        Filtra los contornos por tamaño, eliminando aquellos que sean demasiado pequeños.
        @param contours (list) - Lista de contornos encontrados.
        @return filtered_contours (list) - Lista de contornos filtrados.
        '''
        correct_contour = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                correct_contour.append(cnt)
        return correct_contour

    def _get_color(self, center:list) -> int:
        '''
        Determina el color predominante en un contorno basado en la imagen HSV.
        @param center (list) - Coordenadas del centro del contorno.
        @return color (int) - Índice del color detectado (0=Rojo, 1=Verde, 2=Azul, 3=Amarillo).
        '''
        for i, color in enumerate(self.filtered_colors):
            if color[center[1], center[0]] > 20:
                return i
        return 4

    def _align_equidistant(self, points:list, side_length:float) -> list:
        '''
        Alinea los puntos detectados en una cuadrícula equidistante.
        @param points (list) - Lista de coordenadas de los puntos.
        @param side_length (float) - Longitud de los lados de la cuadrícula.
        @return aligned_points_indices (list) - Índices de los puntos alineados.
        '''
        min_x = min(points, key=lambda p: p[0])[0]
        max_y = max(points, key=lambda p: p[1])[1]
        
        num_elements = 5
        lista_resultado_x = [min_x + side_length * i for i in range(num_elements)]
        lista_resultado_y = [max_y - side_length * i for i in range(num_elements)]

        aligned_points_indices = []
        for point in points:
            x, y = point
            index_x = min(range(len(lista_resultado_x)), key=lambda i: abs(x - lista_resultado_x[i]))
            index_y = min(range(len(lista_resultado_y)), key=lambda i: abs(y - lista_resultado_y[i]))
            aligned_points_indices.append([index_x, index_y])
        
        return aligned_points_indices

    def _map_to_matrix(self, centers:list, colors:list, areas:list) -> np.ndarray:
        '''
        Mapea los centros de los cubos detectados a una matriz 5x5 con sus colores.
        @param centers (list) - Centros de los cubos.
        @param colors (list) - Colores detectados de los cubos.
        @param areas (list) - Áreas de los cubos detectados.
        @return matrix (np.ndarray) - Matriz 5x5 con los colores de los cubos.
        '''
        # Asignación de colores a la matriz 5x5.
        for center, color in zip(centers, colors):
            x, y = center
            if 0 <= x < self.matrix_size and 0 <= y < self.matrix_size:
                self.matrix[y, x] = color
        return self.matrix

    def _draw_contours(self, contour:np.ndarray, color:tuple=(0, 255, 0), thickness:int=2):
        '''
        Dibuja el contorno de un cubo sobre la imagen original.
        @param contour (np.ndarray) - Contorno que se desea dibujar.
        @param color (tuple) - Color del contorno.
        @param thickness (int) - Grosor del contorno.
        '''
        rect = cv2.boundingRect(contour)
        cv2.rectangle(self.contour_img, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), color, thickness)

    def process_image(self, frame:np.ndarray, mostrar:bool=False, debug:bool=False) -> tuple:
        '''
        Procesa la imagen completa: detección de cubos, identificación de colores y clasificación en matriz.
        @param frame (np.ndarray) - Imagen de entrada.
        @param mostrar (bool) - Indica si se deben mostrar los resultados visuales.
        @param debug (bool) - Activar el modo de depuración.
        @return tuple - Matriz de colores y la imagen con los contornos.
        '''
        self.frame = frame
        self.contour_img = deepcopy(frame)
        self.debug = debug
        
        self._preprocess_image()
        
        # Procesamiento de los contornos, colores y áreas de los cubos
        contours, _ = cv2.findContours(self.contour_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = self._filter_contours(contours)
        
        colors = []
        centers = []
        areas = []
        
        for cnt in contours:
            rect = cv2.boundingRect(cnt)
            x, y, w, h = rect
            center = [int(x + w / 2), int(y + h / 2)]
            areas.append(cv2.contourArea(cnt))
            centers.append(center)
            color = self._get_color(center)
            colors.append(color)
            self._draw_contours(cnt)
        
        aligned_indices = self._align_equidistant(centers, max(areas)**0.5)
        self.matrix = self._map_to_matrix(aligned_indices, colors, areas)
        
        if mostrar:
            cv2.imshow("Detected Colors", self.contour_img)
            cv2.imshow("Matrix", self.matrix)
        
        return self.matrix, self.contour_img


# Ejecutar el programa
if __name__ == "__main__":
    # Crear instancia de ImageProcessor con la ruta de la imagen
    use_cam = False
    if use_cam:
        cam = cv2.VideoCapture(4)
        if cam.isOpened():
            _, frame = cam.read()
    else:
        for i in range(8, 25, 1):
            num = i
            ruta = f'/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Figuras_Lateral/Figura_{num}_L.png'
            frame = cv2.imread(ruta)

            processor = ImageProcessor_Front()
            # frame = cv2.imread(ruta)
            processor.process_image(frame, mostrar = True, debug=True)
            # print(np.array2string(matriz, separator=', ', formatter={'all': lambda x: f'{int(x)}'}))
            # print(np.array(matriz))