import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from copy import deepcopy
import cv2



class NodoCamara:
    def __init__(self) -> None:
        rospy.init_node('nodo_vision')
        self.bridge = CvBridge()
        self.subs_cam = rospy.Subscriber('/usb_cam/image_raw', Image, self.__cb_image)
        
        
    def __cb_image(self, image: Image):
        self.cv_image = self.bridge.imgmsg_to_cv2(image, 
                                        desired_encoding='passthrough')
    
    
    def run(self):
        while True:
            imagen = deepcopy(self.cv_image)
            cv2.imshow("Prueba", imagen)
            if cv2.waitKey(0):
                exit()
            imagen
            rospy.sleep(1)
    
    
    
if __name__=="__main__":
    nodo = NodoCamara()
    nodo.run()
    
    
    
