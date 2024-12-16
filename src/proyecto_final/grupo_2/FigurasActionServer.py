import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from copy import deepcopy
import actionlib
from proyecto_final.msg import FigurasAction
import sys
sys.path.append("/home/laboratorio/ros_workspace/src/proyecto_final/scripts/vision")
from frontal import ImageProcessor

class CamaraFrontal(object):
    # create messages that are used to publish feedback/result
    _feedback = FigurasAction().action_feedback
    _result = FigurasAction().action_result
    
    def __init__(self, name):
        self._action_name = name
        rospy.init_node('nodo_camara')
        action = FigurasAction()
        self.image_processor = ImageProcessor()
        self.subs_cam = rospy.Subscriber('/usb_cam/image_raw', Image, self.__cb_image)
        self._as = actionlib.SimpleActionServer(self._action_name, FigurasAction, execute_cb=self.execute_cb, auto_start = False)
        self._as.start()
    
    def __cb_image(self, image: Image):
        self.cv_image = self.bridge.imgmsg_to_cv2(image, desired_encoding='passthrough')

    def execute_cb(self, goal):
        # helper variables
        r = rospy.Rate(1)
        image = deepcopy(self.cv_image)
        self.image_processor.process_image(image)
        
        # append the seeds for the fibonacci sequence
        
            
            
if __name__ == "__main__":
    CamaraFrontal("itsasne")