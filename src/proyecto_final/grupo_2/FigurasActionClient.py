#! /usr/bin/env python

import rospy
from proyecto_final.msg import FigurasAction, FigurasActionFeedback, FigurasActionGoal, FigurasActionResult

# Brings in the SimpleActionClient
import actionlib

def figuras_action_client():
    # Creates the SimpleActionClient, passing the type of the action
    # (FibonacciAction) to the constructor.
    client = actionlib.SimpleActionClient('FigureMakerActionServer', FigurasAction)

    # Waits until the action server has started up and started
    # listening for goals.
    client.wait_for_server()

    # Creates a goal to send to the action server.
    pueba = FigurasActionGoal()
    pueba.order = 1

    # Sends the goal to the action server.
    client.send_goal(pueba)

    # Waits for the server to finish performing the action.
    client.wait_for_result()

    # Prints out the result of executing the action
    return client.get_result()  # A FibonacciResult

if __name__ == '__main__':
    try:
        # Initializes a rospy node so that the SimpleActionClient can
        # publish and subscribe over ROS.
        rospy.init_node('fibonacci_client_py')
        result = figuras_action_client()
        # print("Result:", ', '.join([str(n) for n in result.sequence]))
    except rospy.ROSInterruptException:
        print("program interrupted before completion")
