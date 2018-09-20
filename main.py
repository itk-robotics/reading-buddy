#!/usr/bin/env python
# coding=utf-8
"""
Author Anders Krogsager. ITK October 2017
Main behavior for SoftBank Pepper 1.7
uuid="readingbuddy001"
"""

import sys
import os
import qi

sys.path.append(os.getcwd()+os.sep+'packages')
from flask import render_template
from flask import request
from flask_server import flaskapp
import json
#from utilities.sendMail import choregrapheMail
from time import time, sleep
#import datetime
#import random
#import threading



DEBUG = True
CONNECTION_NOTIFICATION = "internet connection offline"
PORT=5000
"""when debug is true: people are ignored by autonomous life. Head touch triggers monologue"""

OPTIONAL_NET_CONNECTON = False #If set to False, then internet connection is required.

class PythonAppMain(object):

    def __init__(self, application):


        # Getting a session that will be reused everywhere
        self.application = application
        self.session = application.session
        self.service_name = self.__class__.__name__

        # Getting a logger. Logs will be in /var/log/naoqi/servicemanager/{application id}.{service name}
        self.logger = qi.Logger(self.service_name)

        # Do some initializations before the service is registered to NAOqi
        self.logger.info("Initializing...")
        self.motion = self.session.service("ALMotion")
        self.posture = self.session.service("ALRobotPosture")
        self.beman = self.session.service("ALBehaviorManager")
        self.conman = self.session.service("ALConnectionManager")
        #self.mail = choregrapheMail()
        #self.systemMail = self.mail
        self.audio = self.session.service("ALAudioPlayer")
        #self.boolStopMonologue = False

        self.animatedSpeech = self.session.service("ALAnimatedSpeech")
        self.animationPlayer = self.session.service("ALAnimationPlayer")
        self.life = self.session.service("ALAutonomousLife")
        'skip set state interactive' if DEBUG == True else self.life.setState('interactive')
        self.perception = self.session.service("ALPeoplePerception")
        self.tracker = self.session.service("ALTracker")

        #Setup
        #self.perception.setTimeBeforePersonDisappears(5.0) #seconds
        #self.perception.setMaximumDetectionRange(2) #meters
        self.life.setAutonomousAbilityEnabled("All",False)
        #self.life.setAutonomousAbilityEnabled("SpeakingMovement", True)"""http://doc.aldebaran.com/2-5/naoqi/interaction/autonomousabilities/alspeakingmovement.html"""
        self.tracker.unregisterAllTargets()
        self.motion.setBreathEnabled("Arms",True)
        #TODO breathing chest/head?
        self.posture.applyPosture('Stand',0.5)
        self.notification = self.session.service("ALNotificationManager")


        try:
            folder = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
            self.ts = self.session.service("ALTabletService")
            self.ts.loadApplication(folder) #may be disrupted if launched before or simultaniously with ALAutonomousLife.setState('interactive')
            print "ts.loadApplication(folder)= " + folder
            self.ts.showWebview()
            self.logger.info("Tablet loaded!")
        except Exception, e:
            self.logger.error(e)
            self.notification.add(
                {"message": "loading error. I cant use my tablet", "severity": "warning", "removeOnRead": True})
            _strMessage = __file__ + "\n" + "Exception occurred on " + str(datetime.datetime.now()) + "\n" + str(e)
            #self.systemMail.sendMessage(_strMessage)


        #Do not prepare face led group
        if False:
            # START custom speech recognition feedback
            self.leds = self.session.service("ALLeds")
            for x in range(1,9):
                self.leds.createGroup("thinkingFace"+str(x), ["RightFaceLed"+str(x), "LeftFaceLed"+str(x)])
            # STOP custom speech recognition feedback

        self.memory = self.session.service("ALMemory")

        self.callbackMiddleTactile = self.memory.subscriber('MiddleTactilTouched')
        self.intSignalIDHeadtouch = self.callbackMiddleTactile.signal.connect(self.headtouchEvent)
        self.perception.resetPopulation()
        self.logger.info("Initialized!")

        #*** variables for HTML content ***
        self.stories = next(os.walk('flask_server/static/stories/'))[1]  # subfile-, and dir names in the stories dir
        # print ("stories from json file: " + str(stories) + ".\nExpecting type list; " + str(type(stories)))

        for idx, book in enumerate(self.stories):
            self.stories[idx] = "static/stories/%s/%s.json" % (book, book)

        # expected format: #stories = ['static/stories/book1/book1.json', 'static/stories/book2/book2.json']

        self.story_data = []
        self.story_id = -1
        self.my_story = None
        self.json_path = ""
        self.current_chapter = -1
        self.current_page = -1
        self.active_story = ""  # dict from json
        self.last_page = False
        self.the_end = False

        self._json_paths = []

        for story_path in self.stories:
            self._json_paths.append(story_path.rsplit('/', 1)[0])
            self.story_data.append(self.read_json(story_path))


    @qi.nobind
    def start_app(self):
        self.logger.info("Started!")
        print "\033[95m Starting app \033[0m"
        self.audio.playSoundSetFile('sfx_confirmation_1')
        print "DEBUG = " + str(DEBUG)


        while self.internetOk() != True:
            print "INTERNET PROBLEM"
            self.memory.raiseEvent("memShowString", "WiFi: " + str(self.conman.state()))  # optional, displayed on tablet
            sleep(3)

        _start_time = time()
        try:
            sleep(1) #necessary or tablet wont show? initialization delay when testing?
            self.memory.raiseEvent("memShowString", "Undersøger WiFi... ")
            #self.conman.scan()
            #TODO Enable conamn scan
        except Exception, e:
            print "ConnectionManager scan failed"
            self.memory.raiseEvent("memShowString", "Kunne ikke hente WiFi oplysninger")
            self.stop_app()

        services = self.conman.services()
        print ("conman time: " + str(time()-_start_time))
        for service in services:
            network = dict(service)
            if network['State'] == "online":
                _name = network['Name']
                _address =  network['IPv4'][1][1] #'IPv4': [['Method', 'dhcp'], ['Address', '192.168.8.100'], ...

        self.memory.raiseEvent("memShowString",
                               "WiFi: " + _name + "<br>Bogreol: " + _address+":"+str(PORT))

        @flaskapp.route('/')
        @flaskapp.route('/index')
        def index():

            print (self._json_paths)

            return render_template('index.html', title='Robotten min laesemakker', story_data=self.story_data,
                                   story_path=self._json_paths)

        @flaskapp.route('/story')
        def story():

            self.the_end = False  # starting a new story?
            self.story_id = int(request.args.get('story', None))
            self.json_path = self.stories[self.story_id]
            print (self.json_path)
            self.json_path.rsplit('/', 1)[0]  # cut off *.json in path.
            self.init_story(self.json_path)
            return render_template('story.html', title='story', story_data=self.story_data, story_id=self.story_id,
                                   story_path=self.json_path.rsplit('/', 1)[0])

        @flaskapp.route('/page')
        def page():

            # from json: chapters -> pages -> content
            # check for animations.
            if not self.the_end:
                print ("current_page: " + str(self.current_page))
                print ("current_chapter: " + str(self.current_chapter))
                page_content = self.active_story['chapters'][self.current_chapter]['pages'][self.current_page]['content']
                self.next_page()  # increment current_page and current_chapter
            else:
                page_content = ["the end"]

            # print ("page content:")
            # print (page_content)
            # print ("last_page = "+ str(self.last_page))

            return render_template('page.html', title='page', content=page_content, story_id=self.story_id,
                                   lastpage=self.last_page, theend=self.the_end)

        @flaskapp.route('/question')
        def question():

            question = self.active_story['chapters'][self.current_chapter]['question']
            choice_1 = self.active_story['chapters'][self.current_chapter]['options'].keys()[0]
            choice_2 = self.active_story['chapters'][self.current_chapter]['options'].keys()[1]

            return render_template('question.html', title='question', question=question, choice_1=choice_1,
                                   choice_2=choice_2)

        @flaskapp.route('/choice')
        def choice():

            self.user_choice = request.args.get('choice', None)
            print ("choice content, user selected: " + self.user_choice)
            print ("initiate say or animation:")
            print (self.active_story['chapters'][self.current_chapter]['options'][self.user_choice])
            self.last_page = False  # reset bool to default
            self.current_chapter = self.current_chapter + 1

            return render_template('choice.html', title='choice', choice=self.user_choice)


    """"*** HTML utilities ***"""
    @qi.nobind
    def read_json(self, path):
        with flaskapp.open_resource(path) as f:
            return json.load(f)

    @qi.nobind
    def init_story(self, path):

        self.active_story = self.read_json(path)
        self.current_chapter = 0
        self.current_page = 0
        print ("story name: " + self.active_story['title'] + ". Story author: " + self.active_story['author'])

    @qi.nobind
    def next_page(self):

        if (self.current_page + 1) == len(self.active_story['chapters'][self.current_chapter]['pages']):
            print ("end of chapter")
            self.current_page = 0
            self.last_page = True

        if (self.current_chapter + 1) == len(self.active_story['chapters']):
            print ("end of story")
            self.the_end = True

        self.current_page = self.current_page + 1
        # print "number of pages in current chapter:"
        # print len(self.active_story['chapters'][self.current_chapter]['pages'])



    @qi.nobind
    def headtouchEvent(self,var):
        if var == 0.0:
            return #skip on hand-lift
        #TODO CHANGE TO A HEAD MIDDLE TOUCH *DOWN* LISTENER / SIGNAL
        self.callbackMiddleTactile.signal.disconnect(self.intSignalIDHeadtouch)
        #print "signal disconnected: intSignalIDHeadtouch = " + str(self.intSignalIDHeadtouch)
        self.intSignalIDHeadtouch = self.callbackMiddleTactile.signal.connect(self.headtouchEvent)
        #print "signal connected: self.intSignalIDHeadtouch = " + str(self.intSignalIDHeadtouch)

    @qi.nobind
    def waveAnimation(self):
        """From head to arm"""
        # get angle, select arm
        #"'skip' if DEBUG == True else self.motion.stiffnessInterpolation("Head", 0, 0.1) #head stiffness off
        self.velocity = 1
        self.headYaw = self.motion.getAngles("HeadYaw", True)
        self.headYaw = self.headYaw[0]  # from list to float
        #print "head yaw = " + str(self.headYaw)

        # inverse angles depeding on left or right arm.
        if self.headYaw > 0.0:
            self.side = "L"
            self.mod = -1
        else:
            self.side = "R"
            self.mod = 1

        # prep arm
        self.names = [self.side + "ShoulderPitch", self.side + "ShoulderRoll", self.side + "Hand",
                      self.side + "ElbowRoll", self.side + "WristYaw"]
        self.angles = [0.0, self.headYaw, 0.9, (2.0 * self.mod), (-1.7 * self.mod)]
        self.motion.angleInterpolation(self.names, self.angles, self.velocity, True)

        # wave loop
        names = [self.side + "ElbowYaw"] #result: LElbowYaw / RElbowYaw
        times = [0.4]
        isAbsolute = False

        for x in range(2):
            # wave out
            angles = [(0.3 * self.mod)]
            self.motion.angleInterpolation(names, angles, times, isAbsolute)

            # wave in
            angles = [(-0.3 * self.mod)]
            self.motion.angleInterpolation(names, angles, times, isAbsolute)

        self.posture.applyPosture('Stand',0.5)

    @qi.nobind
    def eyesProcessing(self,boolToggle):
        self.toggle = boolToggle
        while self.toggle:
            self.leds.rotateEyes(65280, 1, 1)

        self.leds.on("FaceLeds")

    @qi.nobind
    def animatedVoiceFile(self, strPath):

        """This function is portable. Given filepath f, the robot will play it with animation.

        Call example:
        strPath = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'polly' + os.sep + 'speech_20170825090904153.ogg'
        self.animatedVoiceFile(strPath)
        """
        #self.logger.info("animatedVoiceFile loading: " + strPath)
        strPath = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'polly' + os.sep + strPath
        taskID = self.audio.loadFile(strPath)
        fileSeconds = self.audio.getFileLength(taskID)
        qi.async(self.audio.play, taskID)
        self.animatedSpeech.say("\\pau=" + str(int(fileSeconds)) + "000\\")
        #qi.async(self.posture.applyPosture, 'Stand', 0.5) #TODO reenamble?
        sleep(0.5)

    @qi.nobind
    def internetOk(self):
        """returns True/False if connection is online/offline. Creates notification if offline.
        If connection becomes online some time after a notification is created, this notification is removed.
        Notification return-format:
        [['id', 2], ['message', 'internet connection offline'], ['severity', 'warning'], ['removeOnRead', True]]
        """
        if OPTIONAL_NET_CONNECTON == True:
            return True #do nothing.

        intNotificationID = 0

        list = self.notification.notifications()
        if list:
            # list is not empty
            for sublist in list:
                for subsublist in sublist:
                    if CONNECTION_NOTIFICATION in subsublist:
                        intNotificationID = sublist[0][1]

        if self.conman.state() == 'online':
            self.logger.info("internet connection online")
            if intNotificationID != 0:
                self.notification.remove(intNotificationID)
            return True
        else:
            #connection not online
            self.logger.info(CONNECTION_NOTIFICATION)
            if intNotificationID == 0:
                self.notification.add({"message": CONNECTION_NOTIFICATION, "severity": "warning", "removeOnRead": True})
            return False

    @qi.nobind
    def ledWheel(self, intDuration):
        # hex to Int,0x00RRGGBB; 0x004b4bff = 4934655 (RR 0-255 -> 00-FF)
        #self.leds.rotateEyes(4934655, intDuration, intDuration)
        #self.leds.on("FaceLeds")

        self.leds.off("FaceLeds")
        floatWait = (float(intDuration) / 8.0)  #there are 8 led groups
        #print "floatWait = " + str(floatWait)
        for x in range(1,9):
            self.leds.fadeRGB("thinkingFace"+str(x),"blue", floatWait)
        self.leds.on("FaceLeds")

    @qi.nobind
    def stop_app(self):
        # To be used if internal methods need to stop the service from inside.
        # external NAOqi scripts should use ALServiceManager.stopService if they need to stop it.
        self.logger.info("Stopping service...")
        self.application.stop()
        # TODO call al behaviormanager and stop the behavior. It block s The Dialog.
        self.logger.info("Stopped!")

    @qi.nobind
    def stopMonologue(self):

        self.audio.stopAll()
        self.animatedSpeech._stopAll(True)

        #self.audio.unloadAllFiles() #nødvendig?
        #self.animatedSpeech.exit() KILLS THE SERVICE. Dead end. #expected to fail! No pretty way to stop animated speech.
        #self.animatedSpeech = None virker heller ikke
        #self.animatedSpeech = self.session.service("ALAnimatedSpeech") virker heller ikke

    @qi.nobind
    def cleanup(self):
        # called when your module is stopped
        self.logger.info("Cleaning...")
        self.stopMonologue()
        self.memory.raiseEvent("memHideString", 1)
        self.ts.resetTablet()
        #TODO Clean subscribed signals?
        self.leds.on("FaceLeds")
        self.logger.info("Cleaned!")


if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = PythonAppMain(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    flaskapp.run('0.0.0.0', PORT)  # start flask
    app.run()



    service_instance.cleanup()
    app.session.unregisterService(service_id)