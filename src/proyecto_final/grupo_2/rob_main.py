#!/usr/bin/python3

# Importaciones Propias
from control_robot import ControlRobot
from proyecto_final.vision.grupo_2.cube_tracker import CubeTracker
from action_client_master import MasterClient
from vision.grupo_2.image_processor_front_v2 import ImageProcessor_Front
from vision.grupo_2.image_processor_top import ImageProcessor_Top
from vision.grupo_2.generacion_figura import FigureGenerator

# Importaciones de Datos
from geometry_msgs.msg import Pose, Quaternion
from sensor_msgs.msg import JointState
from proyecto_final.msg import IdCubos

# Importaciones de ROS
import rospy
from tf.transformations import quaternion_from_euler

# Importaciones de Python
from math import pi
from copy import deepcopy
from typing import List

# Importaciones de Terceros
import numpy as np
import cv2

class SecuenceCommander:
    ''' 
    Clase que ejecuta las secuencias de movimiento del robot para la generación de la figura.
    
    Esta clase implementa varios métodos para:
        - Liberar el espacio de trabajo del robot.
        - Almacenar cubos en la zona de descarte.
        - Calibrar la posición del robot respecto a un marcador Aruco.
        - Transformar posiciones de la cámara en referencia al robot.
        - Generar la figura descrita en una matriz 3D con los cubos encontrados en el espacio de trabajo.
        - Mostrar todo el proceso en RViz (representación visual).
    
    Métodos:
        - __init__() - Inicializa el objeto y configura el espacio de trabajo.
        - _moveJoint() - Mueve las articulaciones del robot a una posición especificada.
        - _movePose() - Mueve el robot a una posición específica.
        - empty_workspace() - Vacía el espacio de trabajo del robot, descartando los cubos.
        - create_figure() - Crea una figura basada en los cubos encontrados.
        - _pick_cube() - Agarra un cubo en una posición determinada.
        - _drop_cube() - Deja un cubo en una nueva posición.
        - track_cubes() - Detecta y localiza cubos mediante visión computacional.
    '''
    def __init__(self, simulation:bool = False) -> None:
        '''
        Inicializa la clase y configura los parámetros de Aruco.
            @param simulation (bool) - Indica si es un modo de simulación (por defecto, False).
            @return None
        '''
        # Variables Internas
        self.data_abs_path = "/home/laboratorio/ros_workspace/src/proyecto_final/data"
        self.workspace_range = {'x_max': 10, 'x_min': -10, 'y_max': 10, 'y_min': -10}
        self.simulation = simulation
        self.discarded_cubes:list = [0, 0, 0, 0] # RGBY
        self.matriz3D = np.full((5, 5, 5), -1, dtype=int)
        self.cubos:List[IdCubos] = []
        self.cube_size = 0.025
        self.cube_separation = 0.01

        # Clases
        self.robot = ControlRobot('robot')
        self.cube_tracker = CubeTracker(cam_calib_path=f"{self.data_abs_path}/camera_data/ost.yaml")
        self.action_client = MasterClient()

        # Posiciones Maestras
        # Poses
        self.p_figure_origin:Pose = self.robot.read_from_yaml(f'{self.data_abs_path}/trayectorias/master_positions', 'P_MATRIX_ORIGIN')
        self.p_discard_origin:Pose = self.robot.read_from_yaml(f'{self.data_abs_path}/trayectorias/master_positions', 'P_DISCARD_ORIGIN')
        self.p_aruco = self.robot.read_from_yaml(f'{self.data_abs_path}/trayectorias/pose_aruco', 'P_ARUCO')        

        # JointStates
        self.j_link_1:JointState = self.robot.read_from_yaml(f'{self.data_abs_path}/trayectorias/master_positions', 'J_LINK_1')
        self.j_off_camera:JointState = self.robot.read_from_yaml(f'{self.data_abs_path}/trayectorias/master_positions', 'J_OFF_CAMERA')
        self.j_home:JointState = self.robot.read_from_yaml(f'{self.data_abs_path}/trayectorias/master_positions', 'J_HOME')
        self.j_prev_aruco:JointState = self.robot.read_from_yaml(f'{self.data_abs_path}/trayectorias/master_positions', 'J_PRE_ARUCO')
         
    def _moveJoint(self, jointstate:JointState) -> bool:   
        ''' 
        Mueve las articulaciones del robot a una posición especificada usando un JointState.
            @param jointstate (JointState) - Estado de las articulaciones a alcanzar.
            @return success (bool) - Indica si el movimiento fue exitoso.
        '''      
        success = self.robot.move_jointstates(jointstate)
        
        if success == True:
            rospy.loginfo('JointState alcanzada')
        else:
            rospy.logwarn('JointState inalcanzable')
        return success
    
    def _movePose(self, pose:Pose) -> bool:    
        ''' 
        Mueve el robot a una posición específica (pose).
            @param pose (Pose) - Posición a alcanzar.
            @return success (bool) - Indica si el movimiento fue exitoso.
        '''          
        success = self.robot.move_pose(pose)
        
        if success == True:
            rospy.loginfo('Pose alcanzada')
        else:
            rospy.logwarn('Pose inalcanzable')
        return success
    
    def empty_workspace(self) -> None:
        ''' 
        Libera el espacio de trabajo del robot, moviendo y descartando los cubos encontrados.
            @return None
        '''
        x_min = self.workspace_range['x_min']
        y_min = self.workspace_range['y_min']        
        x_max = self.workspace_range['x_max']        
        y_max = self.workspace_range['y_max']   
        
        self._moveJoint(self.j_link_1)     
                
        for cube_id, cubo in enumerate(self.cubos):
            pose = deepcopy(cubo.pose)
            color = cubo.color
            if pose.position.x > x_min and pose.position.x < x_max:
                if pose.position.y > y_min and pose.position.y < y_max:
                    self._pick_cube(pose, cube_id)
                    self._drop_cube(make_figure=False, cube_id=cube_id, matrix_position=[0, color, self.discarded_cubes[color]])
                    self.discarded_cubes[color] += 1

    def create_figure(self) -> None:
        ''' 
        Genera la figura a partir de los cubos disponibles en el espacio de trabajo.
            @return None
        '''
        self._moveJoint(self.j_link_1)     

        x, z, y = self.matriz3D.shape
        cube_matrix = np.full((x, z, y), 0, dtype=int)
        cubos_sin_color = []

        for j in range(z):
            for i in range(x):
                for k in range(y):
                    figure_color = self.matriz3D[i,j,k]
                    if figure_color != -1:
                        if self.discarded_cubes[figure_color] != 0:
                            pose = deepcopy(self.p_discard_origin)
                            pose.position.y += ((self.cube_size + self.cube_separation) * figure_color)
                            pose.position.z += ((self.cube_size) * self.discarded_cubes[figure_color])
                            cube_matrix[i,j,k] = pose
                            self.discarded_cubes[figure_color] -= 1
                        else:
                            for cube_id, cubo in enumerate(self.cubos):
                                if figure_color != 4 and cubo.color == figure_color:
                                    cube_matrix[i,j,k] = cubo.pose
                                    self.cubos.pop(cube_id)
                                else: # Color desconocido
                                    cubos_sin_color.append([i,j,k])
        
        cubos_descarte = True
        for w in range(cubos_sin_color):
            matrix_position = cubos_descarte[w]
            if cubos_descarte:
                for i in len(self.discarded_cubes):
                    cubos_descarte = False
                    if self.discarded_cubes[i] != 0:
                        pose = deepcopy(self.p_discard_origin)
                        pose.position.y += ((self.cube_size + self.cube_separation) * i)
                        pose.position.z += ((self.cube_size) * self.discarded_cubes[i])
                        cube_matrix[matrix_position[0], matrix_position[1], matrix_position[2]] = pose
                        self.discarded_cubes[i] -= 1
                        cubos_descarte = True
                        continue
            else: 
                cube_matrix[matrix_position[0], matrix_position[1], matrix_position[2]] = self.cubos[0].pose
                self.cubos.pop(0)


        for j in range(z):
            for i in range(x):
                for k in range(y):
                    try:
                        pose:Pose = cube_matrix[i,j,k]
                        pose.position.x = pose.position.x
                        self._pick_cube(cube_matrix[i,j,k], cube_id)
                        self._drop_cube(make_figure=True, cube_id=cube_id, matrix_position=[i, k, j])
                    except:
                        pass


    def _pick_cube(self, pose:Pose, cube_id:int) -> bool:
        ''' 
        Mueve el robot para agarrar un cubo y lo adjunta a la pinza.
            @param pose (Pose) - Posición objetivo del cubo.
            @param cube_id (int) - Identificador único del cubo.
            @return success (bool) - Indica si el movimiento fue exitoso.
        '''
        if not self.simulation:
            gripper, _ = self.robot.get_pinza_state()
            if gripper < 20.0:  # Si la pinza no está completamente cerrada, se cierra.
                self.robot.move_gripper(80.0, 10.0, 0.8)
        
        pose_previa = deepcopy(pose)
        pose_previa.position.z = 0.3  # Eleva la posición del cubo antes de moverlo

        self._movePose(pose_previa)  # Mueve el robot a la posición previa del cubo.

        # Si el movimiento al cubo es exitoso, se adjunta el cubo a la pinza.
        if self.robot.move_carthesian_trayectory([pose_previa, pose]):
            self.robot.scene.attach_box(link='onrobot_rg2_base_link', name=f'Cubo_{cube_id}')

            if not self.simulation:
                self.robot.move_gripper(0.0, 10.0, 1.5)  # Abre la pinza para tomar el cubo
                rospy.loginfo('Cubo Agarrado')

            # Si el movimiento de vuelta es exitoso, vuelve a la posición inicial.
            if self.robot.move_carthesian_trayectory([pose, pose_previa]):
                self._moveJoint(self.j_link_1)

                return True # Secuencia Completada
        return False # Secuencia Fallida


    def _drop_cube(self, make_figure:bool = True, cube_id:int = None, matrix_position:list = [0,0,0]) -> bool:
        ''' 
        Suelta el cubo en la posición deseada.
            @param make_figure (bool) - Determina si el cubo forma parte de una figura o es un descarte.
            @param cube_id (int) - Identificador único del cubo.
            @param matrix_position (list) - Posición 3D para colocar el cubo en una matriz.
            @return success (bool) - Indica si el movimiento fue exitoso.
        '''
        if not self.simulation:
            _, effort = self.robot.get_pinza_state()
            if not effort:  # Si no hay esfuerzo en la pinza, significa que no se tiene cubo.
                rospy.logerr('Sin Cubo Para Dejada')

        if len(matrix_position) != 3:  # Verifica que la matriz de posición tenga 3 elementos.
            raise ValueError('Invalid Input, Matrix position len must be 3')

        # Se determina la pose inicial dependiendo si el cubo forma parte de una figura.
        if make_figure:
            pose: Pose = deepcopy(self.p_figure_origin)  # Pose inicial para formar una figura.
        else:
            pose: Pose = deepcopy(self.p_discard_origin)  # Pose inicial para desechar el cubo.

        pose.position.z += 0.22  # Ajuste en la posición Z.

        # Ajuste en la posición X, Y y Z basados en la matriz de posición.
        pose.position.x += ((self.cube_size + self.cube_separation) * matrix_position[0])
        pose.position.y += ((self.cube_size + self.cube_separation) * matrix_position[1])
        pose.position.z += ((self.cube_size) * matrix_position[2])

        pose_previa: Pose = deepcopy(pose)
        pose_previa.position.z = 0.35  # Ajuste en la altura para la posición previa.

        self._movePose(pose_previa)  # Mueve el robot a la posición previa.

        # Si el movimiento al lugar de dejar el cubo es exitoso, se quita el cubo de la pinza.
        if self.robot.move_carthesian_trayectory([pose_previa, pose]):
            self.robot.scene.remove_attached_object(link='onrobot_rg2_base_link', name=f'Cubo_{cube_id}')

            if not self.simulation:
                self.robot.move_gripper(30.0, 10.0)  # Abre la pinza para soltar el cubo.
                rospy.loginfo('Cubo Soltado')

            # Si no es para formar una figura, se actualiza la pose del cubo en el diccionario.
            if not make_figure:
                self.cubos[cube_id].pose = deepcopy(pose)

            # Si el movimiento de vuelta es exitoso, vuelve a la posición inicial.
            if self.robot.move_carthesian_trayectory([pose, pose_previa]):
                self._moveJoint(self.j_link_1)

                return True # Secuencia Completada
        
        return False # Secuencia no Completada
                
                
    def track_cubes(self, cam_id:int, use_cam:bool = True, mostrar:bool = False, debug:bool = False) -> dict:
        ''' 
        Rastrea la posición de los cubos utilizando una cámara.
            @param cam_id (int) - Identificador de la cámara.
            @param use_cam (bool) - Determina si se usa una cámara real o una imagen almacenada.
            @param mostrar (bool) - Si es verdadero, muestra la imagen con los cubos.
            @param debug (bool) - Si es verdadero, muestra información de depuración.
            @return dict - Diccionario con la información de los cubos localizados.
        '''
        self._free_camera_space()

        if use_cam:
            cam = cv2.VideoCapture(cam_id)
            if cam.isOpened():
                _, frame = cam.read()
        else:
            num = 10
            ruta = f'{self.data_abs_path}/example_img/Cubos_Exparcidos/Cubos_Exparcidos_{num}.png'
            frame = cv2.imread(ruta)
        
        _, resultado = self.cube_tracker.process_image(frame, area_size=1000, mostrar=mostrar, debug=debug)
        
        cubos = self._dict_to_cube(resultado)
        
        return self._cube_to_aruco(cubos)

            
    def _cube_to_aruco(self, cubos:list) -> list:
        ''' 
        Convierte las posiciones de los cubos a coordenadas ArUco.
            @param cubos (list) - Lista de cubos con sus posiciones.
            @return cubos (list) - Lista de cubos con las nuevas posiciones ajustadas.
        '''
        cubo:IdCubos
        for i, cubo in enumerate(cubos):
            cubo.pose.position.x += self.p_aruco.position.x
            cubo.pose.position.y += self.p_aruco.position.y  
                   
            self.robot.add_box_obstacle(f"Cubo_{i}", cubo.pose, (0.025, 0.025, 0.025))
            
            cubo.pose.position.z = 0.2325
            
        return cubos
            
    
    def _dict_to_cube(self, dict_cubos:list) -> list:
        ''' 
        Convierte una lista de diccionarios con información de cubos a una lista de objetos cubo.
            @param dict_cubos (list) - Lista de diccionarios con la información de cada cubo.
            @return cubos (list) - Lista de objetos de tipo IdCubos.
        '''
        cubos = []
        for dict in dict_cubos:
            cubo = IdCubos()
            
            positions = dict['Position']
            angle = dict['Angle']
            color = dict['Color']

            cubo.pose.position.x = positions[0]
            cubo.pose.position.y = positions[1]
            cubo.pose.position.z = 0.0125  # Altura inicial del cubo.
            
            # Convierte el ángulo de Euler a quaternion.
            cubo.pose.orientation = Quaternion(*quaternion_from_euler(pi, 0, -angle, 'sxyz'))

            cubo.color = color
            cubos.append(cubo)
            
        return cubos


    def rob_camera_calibration(self) -> None:
        ''' 
        Realiza la calibración de la cámara del robot y guarda la pose de ArUco.
            @return None
        '''
        self.robot.move_gripper(30, 10)  # Cierra parcialmente la pinza para la calibración.
        
        self._moveJoint(self.j_prev_aruco)  # Mueve el robot a la posición previa de ArUco.
        
        input('¿Boli instalado?: ')  # Solicita confirmación del usuario sobre la instalación del boli.
        self.robot.move_gripper(0, 5)  # Abre la pinza ligeramente para manipular el boli.
        rospy.sleep(2)  # Espera para estabilizar el movimiento.
        
        # Solicita al usuario que coloque el robot en la pose de ArUco para la calibración.
        print('Llevar robot')
        input('¿Robot en Pose ArUco?: ')  # Espera la confirmación del usuario.
        
        self.robot.move_gripper(30, 10)  # Cierra nuevamente la pinza.
        rospy.sleep(2)  # Espera para estabilizar el movimiento.
        
        # Obtiene y guarda la pose de ArUco del robot.
        self.p_aruco = self.robot.get_pose()
        self.robot.save_in_yaml(f'{self.data_abs_path}/trayectorias/pose_aruco', 'P_ARUCO', self.p_aruco, True)


    def _free_camera_space(self):
        ''' 
        Libera el espacio de la cámara moviendo el robot a una posición fuera del área de visión.
            @return None
        '''
        self._moveJoint(self.j_off_camera)  # Mueve el robot a una posición predeterminada fuera del área de la cámara.


    def debug_main(self, get_aruco: bool = False, use_cam: bool = False, cam_id: int = 0) -> None:
        ''' 
        Función principal para depurar el proceso de rastreo de cubos y formación de figuras.
            @param get_aruco (bool) - Si es verdadero, realiza la calibración de la cámara ArUco.
            @param use_cam (bool) - Si es verdadero, usa la cámara en vivo, de lo contrario usa imágenes de ejemplo.
            @param cam_id (int) - Identificador de la cámara que se utiliza.
            @return None
        '''
        if get_aruco:
            self.pose_aruco = self.rob_camera_calibration()  # Realiza la calibración de la cámara si es necesario.
        else:
            # Si no se requiere calibración, lee la pose de ArUco desde un archivo YAML.
            self.pose_aruco = self.robot.read_from_yaml(f'{self.data_abs_path}/trayectorias/pose_aruco', 'P_ARUCO')

        # Realiza el rastreo de los cubos utilizando la cámara o imágenes de ejemplo.
        self.cubos = self.track_cubes(cam_id=cam_id, use_cam=True)
        
        # Limpia el espacio de trabajo antes de formar la figura.
        self.empty_workspace(cubos=self.cubos)

        # Crea la figura usando la matriz de cubos rastreados.
        self.create_figure(cubos=self.cubos)
        
        # Vuelve a la posición de inicio después de la ejecución.
        self._moveJoint(self.j_home)
        rospy.loginfo('Fin de la Ejecución')
    

    def secuencia_tkinter(self, manual: bool = False, procesar_figura: bool = True, localizar_cubos: bool = True, montar_figura: bool = True) -> None:
        ''' 
        Ejecuta una secuencia completa de acciones, que incluye procesamiento de figuras, localización de cubos y montaje de la figura.
            @param manual (bool) - Si es verdadero, permite el control manual de las acciones.
            @param procesar_figura (bool) - Si es verdadero, procesa las imágenes para generar una figura.
            @param localizar_cubos (bool) - Si es verdadero, localiza los cubos en la escena.
            @param montar_figura (bool) - Si es verdadero, monta la figura utilizando los cubos localizados.
            @return None
        '''
        if manual:
            """
            Input -> None

            Output -> None
            """
            pass  # Se omite el código para el control manual de las manos, si no se requiere.

        if procesar_figura and not manual:
            """
            Input -> Ninguno
            Output -> Matriz 3D con la forma de la figura a generar.
            """
            # Procesa una imagen lateral de una figura para generar la matriz de la figura.
            num = 14
            ruta_front = f'/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Figuras_Lateral/Figura_{num}_L.png'
            frame_front = cv2.imread(ruta_front)

            processor_front = ImageProcessor_Front()  # Procesador de la imagen frontal.
            matriz_front, _ = processor_front.process_image(frame_front, mostrar=True)  # Procesa la imagen frontal.

            # Procesa una imagen superior de la figura para generar la matriz superior.
            num = 15
            ruta_top = f'/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Figuras_Superior/Figura_{num}_S.png'
            frame_top = cv2.imread(ruta_top)

            processor_top = ImageProcessor_Top()  # Procesador de la imagen superior.

            matriz_top, _ = processor_top.process_image(frame_top, mostrar=True)  # Procesa la imagen superior.

            # Genera la figura a partir de las matrices procesadas.
            generator = FigureGenerator()
            self.matriz3D = generator.generate_figure_from_matrix(matriz_top, matriz_front)

        if localizar_cubos and not manual:
            """
            Input -> Ninguno
            Output -> Localización de los cubos (lista de objetos IdCubos).
            """
            # Localiza los cubos en la escena utilizando las imágenes o la cámara.
            self.cubos = self.track_cubes(0, False, True)
            
            # cubos = [IdCubos]  # Los cubos son objetos de tipo IdCubos.

        if montar_figura and not manual:
            """
            Input -> [IdCubos] y Matriz 3D de la figura.
            Output -> Ninguno
            """
            # Limpia el espacio de trabajo antes de montar la figura.
            self.empty_workspace(self.cubos)  # El orden es importante, primero se limpia el espacio.

            # Crea la figura con los cubos localizados.
            self.create_figure()


if __name__ == '__main__':
    use_cam = True
    
    robot = SecuenceCommander(simulation=False)
    #robot.free_camera_space()
    robot.secuencia_tkinter()