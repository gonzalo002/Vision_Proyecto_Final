

import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy

class FigureGenerator:
    def __init__(self) -> None:
        self.matriz3D = None

    def generate_figure_from_matrix(self, plant_matrix, front_matrix, side_matrix, figsize:tuple=(3,3), paint:bool = False, tkinter:bool=False):

        anchura, profundidad, plant_matrix_recortada = self._cut_matrix_finding_shape(plant_matrix)
        altura, anchura2, front_matrix_recortada = self._cut_matrix_finding_shape(front_matrix)
        altura2, profundidad2, side_matrix_recortada = self._cut_matrix_finding_shape(side_matrix)
        
        if altura is None or anchura is None or profundidad is None:
            print('Matrices Invalidas')
            return self._paint_matrix(np.array([[[]]]), figsize, tkinter)
        if anchura != anchura2 or profundidad != profundidad2 or altura != altura2:
            print('Matrices Invalidas')
            return self._paint_matrix(np.array([[[]]]), figsize, tkinter)

        self.matriz3D = deepcopy(np.full((anchura, altura, profundidad), -1))
        matriz3D = deepcopy(np.full((anchura, altura, profundidad), -1))

        # Definir el tamaño de cada cubo
        size = 1

        for columna_planta in range(profundidad-1, -1, -1):
            for fila_planta in range(anchura):
                if plant_matrix_recortada[fila_planta][columna_planta] != -1:
                    color_cubo = plant_matrix_recortada[fila_planta][columna_planta]
                    columna_lateral = x = profundidad - columna_planta - 1
                    columna_frontal = anchura - fila_planta -1
                    y = fila_planta
                    cube_found = False
                    for fila_lateral in range(altura):
                        fila_frontal = fila_lateral
                        z = altura - fila_lateral - 1
                        if not cube_found and plant_matrix_recortada[fila_planta][columna_planta] == side_matrix_recortada[fila_lateral][columna_lateral] and plant_matrix_recortada[fila_planta][columna_planta] == front_matrix_recortada[fila_frontal][columna_frontal]:
                            matriz3D[x][z][y] = color_cubo
                            side_matrix_recortada[fila_lateral][columna_lateral] = front_matrix_recortada[fila_frontal][columna_frontal] = 5
                            cube_found = True

                        elif not cube_found and plant_matrix_recortada[fila_planta][columna_planta] == front_matrix_recortada[fila_frontal][columna_frontal] and side_matrix_recortada[fila_lateral][columna_lateral] != -1:
                            matriz3D[x][z][y] = color_cubo
                            front_matrix_recortada[fila_frontal][columna_frontal] = 5
                            cube_found = True

                        elif not cube_found and plant_matrix_recortada[fila_planta][columna_planta] == side_matrix_recortada[fila_lateral][columna_lateral] and front_matrix_recortada[fila_frontal][columna_frontal] != -1:
                            if columna_planta == profundidad-1:
                                pass
                            else:
                                matriz3D[x][z][y] = color_cubo
                                side_matrix_recortada[fila_lateral][columna_lateral] = 5
                                cube_found = True

                        elif cube_found and side_matrix_recortada[fila_lateral][columna_lateral] == front_matrix_recortada[fila_frontal][columna_frontal] and front_matrix_recortada[fila_frontal][columna_frontal] != 5:
                            matriz3D[x][z][y] = side_matrix_recortada[fila_lateral][columna_lateral]
                            side_matrix_recortada[fila_lateral][columna_lateral] = front_matrix_recortada[fila_frontal][columna_frontal] = 5

                        elif cube_found and side_matrix_recortada[fila_lateral][columna_lateral] != 5 and front_matrix_recortada[fila_frontal][columna_frontal] == 5:
                            matriz3D[x][z][y] = side_matrix_recortada[fila_lateral][columna_lateral]
                            side_matrix_recortada[fila_lateral][columna_lateral] = 5

                        elif cube_found and front_matrix_recortada[fila_frontal][columna_frontal] != 5 and side_matrix_recortada[fila_lateral][columna_lateral] == 5:
                            matriz3D[x][z][y] = front_matrix_recortada[fila_frontal][columna_frontal] 
                            front_matrix_recortada[fila_frontal][columna_frontal]  = 5

                        elif cube_found and front_matrix_recortada[fila_frontal][columna_frontal] == 5 and side_matrix_recortada[fila_lateral][columna_lateral] == 5:
                            matriz3D[x][z][y] = 4

                    if not cube_found:
                        z= 0
                        matriz3D[x][z][y] = color_cubo
                            
        self.matriz3D =  matriz3D
        if paint:
            return self._paint_matrix(self.matriz3D, figsize, tkinter)
        else:
            return self.matriz3D
                
    def _cut_matrix(self, matriz, num_filas, num_columnas):
        # Recortar la matriz hasta el tamaño deseado
        matriz_recortada = [fila[:num_columnas] for fila in matriz[5-num_filas:5]]
        return matriz_recortada

    def _cut_matrix_finding_shape(self, matrix):
        i_max = None
        j_max = None
        # Iteramos sobre las filas de la última a la primera
        for i in range(len(matrix)): # Desde la primera fila hasta la ultima
            for j in range(len(matrix[i])): # Desde la última columna hasta la primera
                if matrix[i][4-j] != -1: # Si encontramos un valor distinto a -1
                    if i_max == None:
                        i_max = 5-i # Devolver la fila
                if matrix[j][4-i] != -1:
                    if j_max == None:
                        j_max = 5-i # Devolver la columna inversa
                if j_max != None and i_max != None:
                    return i_max, j_max, self._cut_matrix(matrix, i_max, j_max)

        return None, None, matrix # Si no hay valores diferentes a -1, retornar None

    def _paint_matrix(self, matriz3D, figsize:tuple=(3,3), tkinter:bool=False):
        
        size = 1
        # Definición de las variables
        color_map = {0: 'red', 1: 'green', 2: 'blue', 3: 'yellow', 4: 'gray'}
        anchura, altura, profundidad = matriz3D.shape

        # Dependiendo de si lo mostramos en la interfaz o no, se realizan dos acciones de plt
        if tkinter:
            fig_3d = plt.Figure(figsize=figsize, dpi=100)
            ax = fig_3d.add_subplot(111, projection='3d')
        else:
            fig_3d, ax = plt.subplots(figsize=figsize, dpi=100, subplot_kw={'projection': '3d'})


        # Se recorre la matriz para dibujar la figura
        for x in range(anchura):
            for y in range(profundidad):
                for z in range(altura): 
                    if matriz3D[x, z, y] != -1:
                        ax.bar3d(x*size,y*size,z*size, size, size, size, color=color_map[matriz3D[x, z, y]])
        
        # Configurar los límites del gráfico
        ax.set_xlim([0, 5 * size])
        ax.set_ylim([0,  5 * size])
        ax.set_zlim([0, 5 * size])

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # Ajustar la vista para que la figura se vea al fondo
        ax.view_init(elev=30, azim=-60)

        # Mostrar o devolver la figura
        if tkinter:
            return fig_3d
        else:
            plt.show()
            return None
    

if __name__ in "__main__":
    generator = FigureGenerator()

    # Figura 1
    top_side_1 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 3, 1, -1, -1],
                    [2, 0, 3, -1, -1]]

    front_side_1 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [0, -1, -1, -1, -1],
                    [3, 1, -1, -1, -1]]

    # Figura 2
    top_side_2 = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [0, -1, -1, -1, -1],
                [2, -1, -1, -1, -1],
                [0, 3, 1, 3, -1]]

    front_side_2 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [0, -1, -1, -1, -1],
                    [3, 2, 0, -1, -1]]

    # Figura 3
    top_side_3 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 3, 0, -1, -1],
                    [0, 1, 2, -1, -1],
                    [-1, 3, 1, -1, -1]]

    front_side_3 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [1, 2, 0, -1, -1]]

    # Figura 4
    top_side_4 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 3, 1, -1, -1],
                    [3, -1, 2, -1, -1],
                    [-1, 3, 1, -1, -1]]

    front_side_4 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 3, 1, -1, -1],
                    [1, 2, 0, -1, -1]]

    # Figura 5
    top_side_5 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 1, -1, -1, -1],
                    [2, 3, 1, -1, -1],
                    [-1, 0, -1, -1, -1]]

    front_side_5 = [[-1, 3, -1, -1, -1],
                    [-1, 0, -1, -1, -1],
                    [-1, 3, -1, -1, -1],
                    [-1, 1, -1, -1, -1],
                    [0, 1, 1, -1, -1]]

    # Figura 6 y Ultima
    top_side_6 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [0, 1, 3, -1, -1],
                    [2, 3, 1, -1, -1],
                    [1, 2, 3, -1, -1]]

    front_side_6 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [2, 3, 1, -1, -1],
                    [3, 1, 3, -1, -1]]
    
    # Figura 7 y Ultima
    top_side_7 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [3, 3, 1, -1, -1],
                    [3, 1, 3, -1, -1],
                    [3, 3, 3, -1, -1]]

    front_side_7 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 1, -1, -1, -1],
                    [1, 3, 3, -1, -1]]
    
    top_side_8 = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [ 0,  2,  2, -1, -1],
                [ 3, -1,  1, -1, -1],
                [ 3,  1,  0, -1, -1]]
    
    front_side_8 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1,  2, -1, -1],
                    [ 3, -1,  1, -1, -1],
                    [ 0,  2,  3, -1, -1]]
    
    front_side_9 = [[-1, -1, -1, -1, -1],
                    [-1,  0, -1, -1, -1],
                    [-1,  2,  1, -1, -1],
                    [-1,  3,  2, -1, -1],
                    [ 1,  2,  1,  0, -1]]
    top_side_9 = [[-1, -1, -1, -1, -1],
                    [ 2,  3,  3,  0, -1],
                    [ 3,  0,  1,  1, -1],
                    [ 1,  0,  3,  2, -1],
                    [ 2,  2,  3,  1, -1]]
    
    front_side_10 = [[-1, -1, -1, -1, -1,],
                    [-1,  -1, -1, -1, -1,],
                    [ 1,  0, -1, -1, -1,],
                    [ 0,  2, -1, -1, -1,],
                    [ 2,  1,  0, 3, -1,]]
    
    top_side_10 = [[-1, -1, -1, -1, -1,],
                [ 3,  2,  1,  3, -1,],
                [ 1,  3,  3,  0, -1,],
                [ 1,  3,  0,  1, -1,],
                [ 2,  1,  0,  2, -1,]]
    
    side_matrix_10 = [[-1, -1, -1, -1, -1],
                    [ -1,  -1,  -1,  -1, -1],
                    [ -1,  0,  1,  -1, -1],
                    [ -1,  2,  3,  -1, -1],
                    [ 3,  1,  2,  3, -1]]
    
    front_side_11 = [[-1, -1, -1, -1, -1],
                     [-1, -1, -1, -1, -1],
                     [ 0, -1, -1, -1, -1],
                     [ 1, -1,  0, -1, -1],
                     [ 1,  1,  2, -1, -1]]
    top_side_11 = [[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [ 3,  2,  0, -1, -1],
                [ 2, -1,  1, -1, -1],
                [ 0,  3,  1, -1, -1]]
    
    front_side_12 = [[-1, -1, -1, -1, -1],
                     [-1, -1, -1, -1, -1],
                     [ 1, 0, -1, -1, -1],
                     [ 0, 2,  -1, -1, -1],
                     [ 2,  1,  0, 3, -1]]
    top_side_12 = [[-1, -1, -1, -1, -1],
                    [3, 2,  1, 3, -1],
                    [1, 3,  3, 0, -1],
                    [1, 3,  0, 1, -1],
                    [2, 1,  0, 2, -1]]

    top_side_13 = [[0, 1, 2, 2, 0],
                    [-1, -1,  -1, -1, 3],
                    [-1, -1,  -1, -1, 1],
                    [-1, -1,  -1, -1, 2],
                    [-1, -1,  -1, -1, 0]]

    front_side_13 = [[-1, -1, -1, -1, -1],
                    [-1, -1,  -1, -1, -1],
                    [-1, -1,  -1, -1, -1],
                    [0, -1,  1, -1, 0],
                    [1, 2,  3, 3, 1]]
    
    side_matrix_13 = [[-1, -1, -1, -1, -1],
                    [-1, -1,  -1, -1, -1],
                    [-1, -1,  -1, -1, -1],
                    [0, -1,  2, -1, 0],
                    [1, 2,  1, 1, 3]]
    
    front_side_14 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1,],
                    [-1, -1, -1, -1, -1,],
                    [-1,  2,  0, -1, -1,],
                    [ 3,  1,  2,  3, -1,]]
    top_side_14 = [[-1, -1, -1, -1, -1],
                [ 3,  3, -1, -1, -1],
                [ 2,  0,  2, -1, -1],
                [ 2,  1,  2, -1, -1],
                [ 3,  3, -1, -1, -1]]
    side_matrix_14 = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [ 2,  0,  2, -1, -1],
                    [ 2,  3,  3, -1, -1]]
    
    pruebas_front = [[-1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1],
                    [-1, 0, -1, -1, -1],
                    [1, 2, -1, -1, -1],
                    [ 3, 3, -1, -1, -1]]


    pruebas_top=[[-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, -1, -1, -1, -1],
                [-1, 0, 1, -1, -1],
                [3, 1, -1, -1, -1]]

    pruebas_limites_top = [[-1, -1, -1, -1, -1],
                            [-1, -1, 0, -1, -1],
                            [-1, 2, -1, -1, -1],
                            [-1, -1, -1, -1, -1],
                            [-1, -1, -1, -1, -1]]

    pruebas_limites_front = [[-1, -1, -1, -1, -1],
                            [-1, -1, -1, -1, -1],
                            [-1, 0, -1, -1, -1],
                            [1, 2, -1, -1, -1],
                            [3, 2, -1, -1, -1]]

    vacia = [[-1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1]]

    generator.generate_figure_from_matrix(top_side_14, front_side_14, side_matrix_14, paint=True)