#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float32 as Float

def callback(data):
  rospy.loginfo(rospy.get_caller_id() + "inner_temp=%f", data.data)
  
def listener():
  rospy.init_node('listener', anonymous=True)
  rospy.Subscriber('/watchdog/inner_temp', Float, callback)
  
  rospy.spin()
  
if __name__ == '__main__':
  listener()