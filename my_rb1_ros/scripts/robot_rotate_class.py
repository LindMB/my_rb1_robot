#! /usr/bin/env python

import rospy
from math import pi, atan2
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

class RotateRobot():

    def __init__(self):

        self.cmd = Twist()
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.rate = rospy.Rate(10)  # 10 messages par second
        
        self.odom_sub = rospy.Subscriber('/odom', Odometry, self.odom_callback)

        self.robot_yaw_z = 0.0
        self.odom_ready = False

        self.ctrl_c = False
        rospy.on_shutdown(self.shutdownhook)

    def publish_once_in_cmd_vel(self):

        while not self.ctrl_c: 
            
            connections = self.cmd_vel_pub.get_num_connections()
            if connections > 0:
                self.cmd_vel_pub.publish(self.cmd)
                rospy.loginfo("Cmd Published")
                break
            else:
                self.rate.sleep()

    def shutdownhook(self):
        self.stop_robot()
        self.ctrl_c = True

    def stop_robot(self):
        rospy.loginfo("Shutdown time! Stop the robot")
        self.cmd.angular.z = 0.0
        self.publish_once_in_cmd_vel()

    def quaternion_to_euler_yaw_z(self, x, y, z, w):
        t1 = 2.0 * (w * z + x * y)
        t2 = 1.0 - 2.0 * (y * y + z * z)
        yaw = atan2(t1, t2)
        return yaw

    def odom_callback(self, odom_msg):
        q = odom_msg.pose.pose.orientation
        self.robot_yaw_z = self.quaternion_to_euler_yaw_z(q.x, q.y, q.z, q.w)
        self.odom_ready = True

    # Normalize angle 
    # <=> When the robot crossed the boundary (of the "ROS" circle) from [0, 180] to [-180, 0] and inversely.
    def normalize_angle(self, angle):

        while angle > pi:
            angle -= 2*pi

        while angle < -pi:
            angle += 2*pi

        return angle

    def rotate_robot(self, rotation_deg):

        # Wait to get at least 1 valid odom message
        while not self.ctrl_c and not self.odom_ready :
            rospy.loginfo("Waiting for /odom...")
            self.rate.sleep()

        requested_rotation_rad = (rotation_deg * pi) / 180.0
        rospy.logdebug("Requested rotation: %s degrees (%.3f rad)" %
                      (rotation_deg, requested_rotation_rad))
        
        # Define angular speed
        angular_speed = 0.5
        if requested_rotation_rad > 0:
            self.cmd.angular.z = angular_speed
        else:
            self.cmd.angular.z = -angular_speed

        rospy.loginfo("Rotating Robot!")

        # Rotate as long the requested angle is not reached
        start_yaw_z = self.robot_yaw_z
        while not self.ctrl_c:
        
            current_yaw_z = self.robot_yaw_z
            delta_yaw_z = self.normalize_angle(current_yaw_z - start_yaw_z)
            rospy.logdebug("current_yaw_z = %.3f, delta_yaw_z = %.3f, req_yaw_z = %.3f" %
                          (current_yaw_z, delta_yaw_z, requested_rotation_rad))

            if abs(delta_yaw_z) >= abs(requested_rotation_rad):
                rospy.loginfo("Requested angle reached!")
                break

            self.publish_once_in_cmd_vel()
            self.rate.sleep()

        self.stop_robot()
