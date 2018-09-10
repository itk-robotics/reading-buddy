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
from flask import Flask, render_template, request

flaskapp = Flask(__name__)


#from utilities.sendMail import choregrapheMail
#from time import time, sleep
#import datetime
#import random
#import threading

#startLock = threading.Lock()
DEBUG = True
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


        # Do not load html content.
        # For readingbuddy: use LOG for prototype
        if False:
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
                self.systemMail.sendMessage(_strMessage)



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

    @qi.nobind
    def start_app(self):
        self.logger.info("Started!")
        print "\033[95m Starting app \033[0m"
        self.audio.playSoundSetFile('sfx_confirmation_1')
        print "DEBUG = " + str(DEBUG)

        """
        #TODO make separate function
        except Exception as e:
            self.logger.error(e)
            _strMessage = __file__ + "\n" + "Exception occurred on " + str(datetime.datetime.now()) + "\n" + str(e)
            self.systemMail.sendMessage, _strMessage  # TODO send async?
            self.stop_app
        """

        STORY = "story_1" + os.sep #dir name

        @flaskapp.route('/')
        @flaskapp.route('/index')
        def index():
            user = {'username': 'Miguel'}
            posts = [
                {
                    'author': {'username': 'John'},
                    'body': 'Beautiful day in Portland!'
                },
                {
                    'author': {'username': 'Susan'},
                    'body': 'The Avengers movie was so cool!'
                }
            ]
            return render_template(STORY+'index.html', title='Home', user=user, posts=posts)

        #first HTML solution disabled.
        """
        @flaskapp.route('/02.html', methods=['POST', 'GET'])
        def send_page2():
            self.beman.runBehavior("aarhustest-c0d5d9/Intro")
            return render_template('02.html')

        @flaskapp.route('/03.html', methods=['POST', 'GET'])
        def send_page3():
            return render_template('03.html')

        @flaskapp.route('/04.html', methods=['POST', 'GET'])
        def send_page4():
            return render_template('04.html')

        @flaskapp.route('/05.html', methods=['POST', 'GET'])
        def send_page5():
            return render_template('05.html')

        @flaskapp.route('/06.html', methods=['POST', 'GET'])
        def send_page6():
            return render_template('06.html')

        @flaskapp.route('/07.html', methods=['POST', 'GET'])
        def send_page7():
            return render_template('07.html')

        @flaskapp.route('/08.html', methods=['POST', 'GET'])
        def send_page8():
            qi.async(self.beman.runBehavior, "aarhustest-c0d5d9/Nedslag1")
            return render_template('08.html')

        @flaskapp.route('/09.html', methods=['POST', 'GET'])
        def send_page9():
            return render_template('09.html')

        @flaskapp.route('/10.html', methods=['POST', 'GET'])
        def send_page10():
            qi.async(self.beman.runBehavior,"aarhustest-c0d5d9/Bange")

            return render_template('10.html')

        @flaskapp.route('/11.html', methods=['POST', 'GET'])
        def send_page11():
            qi.async(self.beman.runBehavior,"aarhustest-c0d5d9/Bekymret")
            return render_template('11.html')

        @flaskapp.route('/12.html', methods=['POST', 'GET'])
        def send_page12():
            self.animatedSpeech.say("Tak, nu forstår jeg historien meget bedre. Skal vi ikke læse næste kapitel nu?\\pau=500\\ Er den næste klar til at læse højt for mig? Jeg lytter nu.")
            return render_template('12.html')

        @flaskapp.route('/13.html', methods=['POST', 'GET'])
        def send_page13():
            return render_template('13.html')

        @flaskapp.route('/14.html', methods=['POST', 'GET'])
        def send_page14():
            return render_template('14.html')

        @flaskapp.route('/15.html', methods=['POST', 'GET'])
        def send_page15():
            return render_template('15.html')

        @flaskapp.route('/16.html', methods=['POST', 'GET'])
        def send_page16():
            return render_template('16.html')

        @flaskapp.route('/17.html', methods=['POST', 'GET'])
        def send_page17():
            return render_template('17.html')

        @flaskapp.route('/18.html', methods=['POST', 'GET'])
        def send_page18():
            qi.async(self.beman.runBehavior, "aarhustest-c0d5d9/Nedslag_2")
            return render_template('18.html')

        @flaskapp.route('/19.html', methods=['POST', 'GET'])
        def send_page19():
            return render_template('19.html')

        @flaskapp.route('/20.html', methods=['POST', 'GET'])
        def send_page20():
            qi.async(self.beman.runBehavior, "aarhustest-c0d5d9/Familie")
            return render_template('20.html')

        @flaskapp.route('/21.html', methods=['POST', 'GET'])
        def send_page21():
            self.beman.runBehavior("aarhustest-c0d5d9/Venner")
            return render_template('21.html')

        @flaskapp.route('/22.html', methods=['POST', 'GET'])
        def send_page22():
            qi.async(self.animatedSpeech.say,"Det var de første 2 kapitler af Drageridderne, Tiggerdrengen Tam. Tak for oplæsningen.")
            return render_template('22.html')
        """

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
    def monologue(self,strForceSelect = None):
        startLock.acquire(False) #non-blocking
        intWait = 1

        def mono1():
            self.memory.raiseEvent("memShowString",
                                   "Vi stemmer til kommunalvalget tirsdag 21. november.")  #optional, displayed on tablet
            qi.async(self.animationPlayer.runTag, "all")         #animation overriding random gestures
            self.animatedVoiceFile("speech_20171031153516996.ogg")  #path to voice file
            sleep(intWait)

            if not self.boolStopMonologue:
                self.memory.raiseEvent("memShowString",
                                       "På rådhuset bestemmer byrådet hvad byens millioner af kroner skal buges til, og du bestemmer hvem der sidder i byrådet.")
                qi.async(self.animationPlayer.runTag, "estimate", delay=4500000)
                self.animatedVoiceFile("speech_20171102085118631.ogg")
                sleep(intWait)

            if not self.boolStopMonologue:
                self.memory.raiseEvent("memShowString",
                                       "Du kan finde dit valgsted på kortet, som snart kommer i din postkasse.")
                qi.async(self.animationPlayer.runTag, "you")
                self.animatedVoiceFile("speech_20171102090127292.ogg")
                sleep(intWait)


        def mono2():

            self.memory.raiseEvent("memShowString",
                                   "Jeg elsker mennesker og deres love og demokrati")

            self.animatedVoiceFile("speech_20171031095654144.ogg")
            sleep(intWait)

            if not self.boolStopMonologue:
                qi.async(self.animationPlayer.runTag, "offer", delay=4000000)
                self.memory.raiseEvent("memShowString",
                                       "Jeg kan ikke stemme til kommunalvalget tirsdag 21. november. Men det kan du!")

                self.animatedVoiceFile("speech_20171102090819771.ogg")
                sleep(intWait)
            if not self.boolStopMonologue:
                qi.async(self.animationPlayer.runTag, "give")
                self.memory.raiseEvent("memShowString",
                                       "Du kan finde dit valgsted på valgkortet, som kommer med posten.")
                self.animatedVoiceFile("speech_20171102091150340.ogg")
                sleep(intWait)

        def mono3():

            self.memory.raiseEvent("memShowString",
                                   "Vi stemmer til kommunalvalget tirsdag 21. november.")
            qi.async(self.animationPlayer.runTag, "all")
            self.animatedVoiceFile("speech_20171031153516996.ogg")
            sleep(intWait)
            if not self.boolStopMonologue:
                self.memory.raiseEvent("memShowString",
                                       "I gamle dage havde man en borg mester. Han sørgede for at alle i en by eller borg havde det godt.")
                qi.async(self.animationPlayer.runTag, "tall")
                self.animatedVoiceFile("speech_20171102092141304.ogg")
                sleep(intWait)

            if not self.boolStopMonologue:
                self.memory.raiseEvent("memShowString",
                                       "Idag har vi stadig en borgmester og borgere. Du er borger og du kan være med til at bestemme hvem vores næste borgmester bliver.")
                qi.async(self.animationPlayer.runTag, "you", delay=3000000)
                self.animatedVoiceFile("speech_20171102092301011.ogg")
                sleep(intWait)

            if not self.boolStopMonologue:
                self.memory.raiseEvent("memShowString",
                                       "Hvis du ikke har tid den 21. november kan du brevstemme på lokalbibliotekerne eller her på DOKK1.")
                #qi.async(self.animationPlayer.runTag, "you", delay=3000000)
                self.animatedVoiceFile("speech_20171102093920160.ogg")
                sleep(intWait)


        _selector = ['mono1', 'mono2', 'mono3']
        _selector = random.choice(_selector)

        if strForceSelect:
            _selector = strForceSelect

        if _selector == 'mono1':
            mono1()
        elif _selector == 'mono2':
            mono2()
        elif _selector == 'mono3':
            mono3()

        if not self.boolStopMonologue:
            #final monolouge to person
            qi.async(self.animationPlayer.runTag, "cloud", delay=3000000)
            self.memory.raiseEvent("memShowString",
                                   "Hvis du ikke ved hvem du vil stemme på endnu kan du lære mere til de mange valgarrangementer her på DOKK1.")
            self.animatedVoiceFile("speech_20171031112419159.ogg")

            sleep(3)
            self.waveAnimation()

        self.memory.raiseEvent("memHideString", 1)
        self.boolStopMonologue = False
        startLock.release()

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
            return True

        intNotificationID = 0

        list = self.notification.notifications()
        if list:
            # list is not empty
            for sublist in list:
                for subsublist in sublist:
                    if 'internet connection offline' in subsublist:
                        intNotificationID = sublist[0][1]

        if self.session.service("ALConnectionManager").state() == 'online':
            self.logger.info("internet connection online")
            if intNotificationID != 0:
                self.notification.remove(intNotificationID)
            return True
        else:
            #connection not online
            self.logger.info("internet connection offline")
            if intNotificationID == 0:
                self.notification.add({"message": "internet connection offline", "severity": "warning", "removeOnRead": True})
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
    def stopMonologue(self, boolExpressionValue):
        print "expression condition = " + str(boolExpressionValue)
        if boolExpressionValue and startLock.locked():
            print "\033[95mStopping monologue\033[0m"
            self.boolStopMonologue = True
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
        self.stopMonologue(True)
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
    flaskapp.run(host='0.0.0.0', port=5000)  # start flask
    app.run()



    service_instance.cleanup()
    app.session.unregisterService(service_id)