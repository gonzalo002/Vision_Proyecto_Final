#! /usr/bin/env python
import sys
import rospy

# Brings in the SimpleActionClient
import actionlib

# Brings in the messages used by the fibonacci action, including the
# goal message and the result message.
from proyecto_final.msg import FigurasAction, FigurasActionGoal, FigurasActionResult #Matriz Figura
from proyecto_final.msg import CubosAction, CubosActionGoal, CubosActionResult #Pose Cubos
from proyecto_final.msg import RLAction, RLActionGoal, RLActionResult # Orden Cubos

class MasterClient:
    def __init__(self) -> None:
        # rospy.init_node('master_action_client')
        pass

    def client_figura():
        # Creates the SimpleActionClient, passing the type of the action
        client = actionlib.SimpleActionClient('figura_to_robot', FigurasActionResult)

        # Espera hasta que se inicia el servidor y recibes el goal
        client.wait_for_server()

        # Creates a goal to send to the action server.
        goal = FigurasActionGoal()
        goal.goal.order = 1

        # Sends the goal to the action server.
        client.send_goal(goal)

        # Espera al servidor a finalizar la acción
        client.wait_for_result()

        # Muestra el resultado del action ejecutado
        return client.get_result()  # Reultado de las Figuras

    def client_cubo():
        # Creates the SimpleActionClient, passing the type of the action
        client = actionlib.SimpleActionClient('cubo_to_robot', CubosActionResult)

        # Espera hasta que se inicia el servidor y recibes el goal
        client.wait_for_server()

        # Creates a goal to send to the action server.
        goal = CubosActionGoal()
        goal.goal.order = 1

        # Sends the goal to the action server.
        client.send_goal(goal)

        # Espera al servidor a finalizar la acción
        client.wait_for_result()

        # Muestra el resultado del action ejecutado
        return client.get_result()  # Reultado de los Cubos

    def client_rl():
        # Creates the SimpleActionClient, passing the type of the action
        client = actionlib.SimpleActionClient('agent_to_robot', RLActionResult)

        # Espera hasta que se inicia el servidor y recibes el goal
        client.wait_for_server()

        # Creates a goal to send to the action server.
        goal = RLActionGoal()
        goal.goal.order = 1

        # Sends the goal to the action server.
        client.send_goal(goal)

        # Espera al servidor a finalizar la acción
        client.wait_for_result()

        # Muestra el resultado del action ejecutado
        return client.get_result()  # Reultado del Agente

    if __name__ == '__main__':
        try:
            # Initializes a rospy node so that the SimpleActionClient can
            # publish and subscribe over ROS.
            rospy.init_node('fibonacci_client_py')
            result = fibonacci_client()
            print("Result:", ', '.join([str(n) for n in result.sequence]))
        except rospy.ROSInterruptException:
            print("program interrupted before completion", file=sys.stderr)