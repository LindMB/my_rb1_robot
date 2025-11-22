#! /usr/bin/env python

import rospy
from robot_rotate_class import RotateRobot
from my_rb1_ros.srv import Rotate, RotateResponse

def callback(request):

    rospy.loginfo("Service /rotate_robot Requested")
    rospy.loginfo("Requested rotation: "+str(request.degrees)+" degrees")

    rotate_robot_obj = RotateRobot()
    rotate_robot_obj.rotate_robot(request.degrees)

    rospy.loginfo("Service /rotate_robot Completed")

    response = RotateResponse()
    response.result = "Robot has successfully rotated of "+str(request.degrees)+" degrees !"
    return response

rospy.init_node('service_rotate_robot_server', log_level=rospy.DEBUG)

srv_server = rospy.Service('/rotate_robot', Rotate, callback)
rospy.loginfo("Service /rotate_robot Ready")

rospy.spin() # Keep the service open
