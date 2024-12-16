#!/usr/bin/python3
import rospy
from math import pi
from tf.transformations import quaternion_from_euler
from geometry_msgs.msg import Quaternion
import actionlib
import cv2

from proyecto_final.scripts.vision.grupo_2.cube_tracker import CubeTracker
from proyecto_final.msg import RLAction
from proyecto_final.msg import IdCubos



class CubeTrackerActionClient(object):
    # create messages that are used to publish feedback/result
    _feedback = RLAction().action_feedback
    _result = RLAction().action_result
    
    def __init__(self, name):
        self._action_client = actionlib.SimpleActionClient("CubeTracker_Cliebt", RLAction)
    
    def send_goal(self, id_cubes_position:dict, cubes_order:list):
        goal_msg = RLAction().action_goal
        goal_msg.cubes_position = id_cubes_position
        goal_msg.cubes_order = cubes_order


        self._action_client.wait_for_server()

        # Returns future to goal handle; client runs feedback_callback after sending the goal
        self._send_goal_future = self._action_client.send_goal(goal_msg, active_cb=self.goal_response_callback, feedback_cb=self.feedback_callback, done_cb = self.get_result_callback)

        rospy.loginfo("Goal sent!")


    def _create_msg_list(self, cube_position):
        msg_list = []
        msg = IdCubos()
        for cube in cube_position:
            msg.pose.position.x = cube["Position"][0]
            msg.pose.position.y = cube["Position"][1]
            msg.orientation = Quaternion(*quaternion_from_euler(pi, 0, cube["Angle"], 'sxyz'))
            msg.color = cube["Color"]

            msg_list.append(msg)

        return msg

            
            
if __name__ == "__main__":
    use_cam = False
    cube_tracker = CubeTracker(cam_calib_path="src/proyecto_final/data/camera_data/ost.yaml")

    if use_cam:
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            _, frame = cam.read()
    else:
        num = 1
        ruta = f'/home/laboratorio/ros_workspace/src/proyecto_final/data/example_img/Cubos_Exparcidos/Cubos_Exparcidos_{num}.png'
        frame = cv2.imread(ruta)

    resultado = cube_tracker.analizar_imagen(frame, area_size=800, mostrar=False)
    print(resultado)
    if use_cam:
        cam.release()

    cube_tracker_action = CubeTrackerActionClient()
    print(cube_tracker_action._create_msg_list(resultado))
    