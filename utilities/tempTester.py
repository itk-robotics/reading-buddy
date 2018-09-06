#!/usr/bin/env python
# coding=utf-8
"""
Author Anders Krogsager. ITK October 2017
Main behavior for SoftBank Pepper 1.7
uuid="borgerservice_valg_2017"
"""

import sys
import qi
from time import time, sleep
import threading
startLock = threading.Lock()
stopLock = threading.Lock()
global future
future = None

class PythonAppMain(object):

    def __init__(self, application):

        _start_time = time() #TODO delete
        # Getting a session that will be reused everywhere
        self.application = application
        self.session = application.session
        self.service_name = self.__class__.__name__

        # Getting a logger. Logs will be in /var/log/naoqi/servicemanager/{application id}.{service name}
        self.logger = qi.Logger(self.service_name)

        # Do some initializations before the service is registered to NAOqi
        self.logger.info("Initializing...")
        self.logger.info("Initialized!")
        self.logger.info("initialization time: " + str(time() - _start_time)) #TODO delete. Very early test time is ~0.05 sec

    @qi.nobind
    def start_app(self):
        print "\033[95m Starting app \033[0m"
        self.running = True
        options = ["lock", "unlock", "state", "exit"]
        import threading
        lock = threading.Lock()
        while self.running:
            command = raw_input("Enter command\n")
            if command == options[0]:

                lock.acquire(False)

            elif command == options[1]:

                lock.release()

            elif command == options[2]:

                print lock.locked()

            elif command == options[3]:

                self.stop_app()

            else:
                print '[%s]' % ', '.join(map(str, options))



    @qi.nobind
    def stop_app(self):
        # To be used if internal methods need to stop the service from inside.
        # external NAOqi scripts should use ALServiceManager.stopService if they need to stop it.
        self.logger.info("Stopping service...")
        self.application.stop()
        self.running = False
        self.logger.info("Stopped!")

    @qi.nobind
    def cleanup(self):
        # called when your module is stopped
        self.logger.info("Cleaning...")
        self.logger.info("Cleaned!")


if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = PythonAppMain(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)
