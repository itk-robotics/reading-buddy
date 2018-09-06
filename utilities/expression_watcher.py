#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""
Example: Use the ALExpressionWatcher Module

Use the parameter --qi-url=tcp://10.0.0.2:9559 on the command line to connect
to your robot, replacing 10.0.0.2 with your robot's IP address.
"""

import qi
import sys
from datetime import datetime

def onExpressionReport(expression_value):

    print "Got ALExpressionWatcher signal with value: ", expression_value
    # you can check the expression value, though report_mode=2 gauanteed it is true
    if expression_value:
        print datetime.now()
        TTS.say("expression true")



if __name__ == "__main__":

    # Initialize qi framework by creating a local app and connecting to robot
    app = qi.Application(sys.argv)
    app.start()

    # Get a reference to the Expression Watcher service
    expression_svc = app.session.service("ALExpressionWatcher")
    TTS = app.session.service("ALTextToSpeech")
    life = app.session.service("ALAutonomousLife")
    life.setState('interactive')

    # Setup the expression
    report_mode = 2  # see API doc for behavior of different report modes
    expression_condition = "'Launchpad/DistanceOfTrackedHuman' == -1.0 && (('Launchpad/DistanceOfTrackedHuman' == -1.0) ~ 5) " #there is noone and has been noone for x seconds

    # Add the expression, and get back an object representing it.
    # When this object goes out of memory scope, the expression is deleted.
    expression_obj = expression_svc.add(expression_condition, report_mode)
    # Connect expression object signal to a callback, which is called based on report_mode
    # To stop listening to this callback, you can call expression_obj.signal.disconnect(signal_id)
    signal_id = expression_obj.signal.connect(onExpressionReport)

    app.run() # Will block until the app connection is destroyed, or ctrl+c