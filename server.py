#! /usr/bin/env python
from __future__ import print_function
import rospy
import actionlib
import serial
from move_arm.msg import *


class MoveAction(object):
    # create messages that are used to publish feedback/result
    _feedback = move_arm.msg.MoveFeedback()
    _result = move_arm.msg.MoveResult()

    def __init__(self, name):
        self._action_name = name
        self._as = actionlib.SimpleActionServer(
            self._action_name,
            move_arm.msg.MoveAction,
            execute_cb=self.execute_cb,
            auto_start=False)  # TODO: can we make this true and get rid of next line?
        self._as.start()

    def execute_cb(self, goal):
        # helper variables
        num_joints, port, baudrate = (rospy.get_param(param) for param in
                                      ["/num_joints", "/port", "/baudrate"])

        torques_string = ' '.join(goal.torques)  # TODO: configure
        assert len(goal.torques) == num_joints, \
            "%s should have %d values (num_joints)" % \
            (torques_string, num_joints)
        rate = rospy.Rate(10)
        success = True

        with serial.Serial(port=port, baudrate=baudrate) as ser:
            ser.write(torques_string)

            # append the seeds for the fibonacci sequence
            self._feedback.sequence = ser.readline()

        # publish info to the console for the user
        rospy.loginfo('%s: passing the following torques to arduino: %s' %
                      (self._action_name, torques_string))


        # publish the feedback
        self._as.publish_feedback(self._feedback)

        if success:
            self._result.sequence = self._feedback.sequence
            rospy.loginfo('%s: Succeeded' % self._action_name)
            self._as.set_succeeded(self._result)


if __name__ == '__main__':
    rospy.init_node('move_arm')
    MoveAction(rospy.get_name())
    rospy.spin()
