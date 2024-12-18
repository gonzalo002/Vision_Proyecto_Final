import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy

class FigureGenerator:
    def __init__(self) -> None:
        self.matriz3D = None
        self.message = None
        self.message_type = 0 # 1=Info, 2=Warn, 3=Error

    def generate_figure_from_matrix(self, matriz_planta:list, matriz_alzado:list, matriz_perfil:list, figsize:tuple=(3,3), paint:bool = False, tkinter:bool=False):

        profundidad, anchura, matriz_planta_recortada = self._cut_matrix_finding_shape(matriz_planta)
        altura, anchura2, matriz_alzado_recortada = self._cut_matrix_finding_shape(matriz_alzado)
        altura2, profundidad2, matriz_perfil_recortada = self._cut_matrix_finding_shape(matriz_perfil)
        
        if (altura is None) and (anchura is None) and (profundidad is None):
            return self._paint_matrix(np.array([[[]]]), figsize, tkinter)
        
        if altura is None or anchura is None or profundidad is None:
            self.message = "Las matrices introduccidas son inválidas, no se puede realizar figura 3D."
            self.message_type = 3
            print('Matrices Invalidas')
            return self._paint_matrix(np.array([[[]]]), figsize, tkinter)
        
        if anchura != anchura2 or profundidad != profundidad2 or altura != altura2:
            print('Matrices Invalidas')
            self.message = "Las matrices introduccidas son inválidas, no se puede realizar figura 3D."
            self.message_type = 3
            return self._paint_matrix(np.array([[[]]]), figsize, tkinter)

        self.matriz3D = deepcopy(np.full((anchura, altura, profundidad), -1))
        matriz3D = deepcopy(np.full((anchura, altura, profundidad), -1))

        # Definir el tamaño de cada cubo
        size = 1
        for fila_planta in range(0, profundidad):
            for columna_planta in range(anchura-1, -1, -1):
                if matriz_planta_recortada[fila_planta][columna_planta] != -1:
                    color_cubo = matriz_planta_recortada[fila_planta][columna_planta]
                    columna_perfil = profundidad - fila_planta -1
                    columna_alzado = x = anchura - columna_planta - 1
                    y = fila_planta
                    cube_found = False
                    for fila_alzado in range(altura):
                        fila_perfil = fila_alzado
                        z = altura - fila_alzado - 1
                        if not cube_found and matriz_planta_recortada[fila_planta][columna_planta] == matriz_perfil_recortada[fila_perfil][columna_perfil] and matriz_planta_recortada[fila_planta][columna_planta] == matriz_alzado_recortada[fila_alzado][columna_alzado]:
                            matriz3D[x][z][y] = color_cubo
                            matriz_perfil_recortada[fila_perfil][columna_perfil] = matriz_alzado_recortada[fila_alzado][columna_alzado] = 5
                            cube_found = True

                        elif not cube_found and matriz_planta_recortada[fila_planta][columna_planta] == matriz_alzado_recortada[fila_alzado][columna_alzado] and matriz_perfil_recortada[fila_perfil][columna_perfil] != -1:
                            matriz3D[x][z][y] = color_cubo
                            matriz_alzado_recortada[fila_alzado][columna_alzado] = 5
                            cube_found = True

                        elif not cube_found and matriz_planta_recortada[fila_planta][columna_planta] == matriz_perfil_recortada[fila_perfil][columna_perfil] and matriz_alzado_recortada[fila_alzado][columna_alzado] != -1:
                            if columna_planta == profundidad-1:
                                pass
                            else:
                                matriz3D[x][z][y] = color_cubo
                                matriz_perfil_recortada[fila_perfil][columna_perfil] = 5
                                cube_found = True

                        elif cube_found and matriz_perfil_recortada[fila_perfil][columna_perfil] == matriz_alzado_recortada[fila_alzado][columna_alzado] and matriz_alzado_recortada[fila_alzado][columna_alzado] != 5:
                            matriz3D[x][z][y] = matriz_perfil_recortada[fila_perfil][columna_perfil]
                            matriz_perfil_recortada[fila_perfil][columna_perfil] = matriz_alzado_recortada[fila_alzado][columna_alzado] = 5

                        elif cube_found and matriz_perfil_recortada[fila_perfil][columna_perfil] != 5 and matriz_alzado_recortada[fila_alzado][columna_alzado] == 5:
                            for i in range(columna_planta, anchura):
                                if matriz_perfil_recortada[fila_perfil][columna_perfil] == matriz_planta_recortada[fila_planta][i]:
                                    matriz3D[x][z][y] = 4
                            if matriz3D[x][z][y] != 4:
                                matriz3D[x][z][y] = matriz_perfil_recortada[fila_perfil][columna_perfil]
                                matriz_perfil_recortada[fila_perfil][columna_perfil] = 5

                        elif cube_found and matriz_alzado_recortada[fila_alzado][columna_alzado] != 5 and matriz_perfil_recortada[fila_perfil][columna_perfil] == 5:
                            for i in range(fila_planta, 0):
                                if matriz_alzado_recortada[fila_alzado][columna_alzado] == matriz_planta_recortada[i][columna_planta]:
                                    matriz3D[x][z][y] = 4
                            if matriz3D[x][z][y] != 4:
                                matriz3D[x][z][y] = matriz_alzado_recortada[fila_alzado][columna_alzado]
                                matriz_alzado_recortada[fila_alzado][columna_alzado] = 5

                        elif cube_found and matriz_alzado_recortada[fila_alzado][columna_alzado] != 5 and matriz_perfil_recortada[fila_perfil][columna_perfil] != 5:
                            if columna_planta != profundidad-1:
                                matriz3D[x][z][y] = matriz_perfil_recortada[fila_perfil][columna_perfil]
                                matriz_perfil_recortada[fila_perfil][columna_perfil] = 5
                            else:
                                matriz3D[x][z][y] = matriz_alzado_recortada[fila_alzado][columna_alzado]
                                matriz_alzado_recortada[fila_alzado][columna_alzado] = 5

                        elif cube_found and matriz_alzado_recortada[fila_alzado][columna_alzado] == 5 and matriz_perfil_recortada[fila_perfil][columna_perfil] == 5:
                            matriz3D[x][z][y] = 4

                    if not cube_found:
                        z= 0
                        matriz3D[x][z][y] = color_cubo
                            
        self.matriz3D =  matriz3D
        self.message = "Se ha calculado la figura 3D"
        self.message_type = 1
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
