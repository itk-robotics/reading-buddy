#!/usr/bin/env python
# coding=utf-8
"""
Author Anders Krogsager. ITK October 2018
Pepper 1.7
uuid="reading_buddy"
"""


import sys
import os
import qi

import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout) #prevent print to console from crashing on special characters
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

sys.path.append(os.getcwd()+os.sep+'packages')
from flask import render_template
from flask import request
from flask_server import flaskapp
import json
#from utilities.sendMail import choregrapheMail
from time import time, sleep
import datetime
import random

with open('logfile.txt', 'a') as the_file:
    the_file.write('imports OK, started at ' + str(datetime.datetime.now()) + ', ')


DEBUG = False
CONNECTION_NOTIFICATION = "jeg kan ikke få forbindelse til internettet"
PORT=5000
"""when debug is true: people are ignored by autonomous life. Head touch triggers monologue"""

OPTIONAL_NET_CONNECTON = False #If set to False, then internet connection is required.

class PythonAppMain(object):

    def __init__(self, application):
        with open('logfile.txt', 'a') as the_file:
            the_file.write('begin init, ')


        # Getting a session that will be reused everywhere
        self.application = application
        self.session = application.session
        self.service_name = self.__class__.__name__

        # Getting a logger. Logs will be in /var/log/naoqi/servicemanager/{application id}.{service name}
        self.logger = qi.Logger(self.service_name)

        # Do some initializations before the service is registered to NAOqi
        self.logger.info("Initializing...")
        self.leds = self.session.service("ALLeds")
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
        self.life.setAutonomousAbilityEnabled("SpeakingMovement", True)
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
            
        with open('logfile.txt', 'a') as the_file:
            the_file.write('init OK\n')


    @qi.nobind
    def start_app(self):
        with open('logfile.txt', 'a') as the_file:
            the_file.write('starting app\n')
    
        self.logger.info("Started!")
        print "\033[95m Starting app \033[0m"
        self.audio.playSoundSetFile('sfx_confirmation_1')
        self.logger.info("DEBUG = " + str(DEBUG))


        while self.internetOk() != True:
            self.logger.warning("INTERNET PROBLEM")
            self.memory.raiseEvent("memShowString", "WiFi: " + str(self.conman.state()))  # optional, displayed on tablet
            self.animatedSpeech.say("jeg er ikke forbundet til internettet.")
            #self.stop_app()
            sleep(5)

        _start_time = time()
        try:
            sleep(2) #necessary or tablet wont show? initialization delay when testing?
            self.memory.raiseEvent("memShowString", "Undersøger WiFi... ")
            self.conman.scan()#TODO Disble conamn scan

        except Exception, e:
            self.logger.warning("ConnectionManager scan failed")
            self.memory.raiseEvent("memShowString", "Kunne ikke hente WiFi oplysninger")
            self.stop_app()

        services = self.conman.services()
        self.logger.info("conman time: " + str(time()-_start_time))
        for service in services:
            network = dict(service)
            if network['State'] == "online":
                _name = network['Name']
                _address =  network['IPv4'][1][1] #'IPv4': [['Method', 'dhcp'], ['Address', '192.168.8.100'], ...
        sleep(2)  # necessary or tablet wont show? initialization delay when testing?
        self.memory.raiseEvent("memShowString",
                               "WiFi: " + _name + "<br>Bogreol: " + _address+":"+str(PORT))

        @flaskapp.route('/')
        @flaskapp.route('/index')
        def index():
            self.memory.raiseEvent("memHideString", 1)
            self.logger.info(self._json_paths)
            return render_template('index.html', title='Robotten min laesemakker', story_data=self.story_data,
                                   story_path=self._json_paths)

        @flaskapp.route('/story')
        def story():

            self.the_end = False  # starting a new story?
            self.story_id = int(request.args.get('story', None))
            self.json_path = self.stories[self.story_id]
            self.json_path.rsplit('/', 1)[0]  # cut off *.json in path.
            self.init_story(self.json_path)

            try:
                #look for intro
                _intro_say = self.active_story['intro_say']
                self.logger.info(_intro_say)
                qi.async(self.animatedSpeech.say, _intro_say)

            except:
                self.logger.info("no intro_say was found")
            return render_template('story.html', title='story', story_data=self.story_data, story_id=self.story_id,
                                   story_path=self.json_path.rsplit('/', 1)[0])

        @flaskapp.route('/page')
        def page():

            # from json: chapters -> pages -> content
            try:
                #look for animations
                page_animation = self.active_story['chapters'][self.current_chapter]['pages'][self.current_page]['animation']
                self.logger.info("runBehavior " + page_animation)
                self.beman.runBehavior(page_animation)

            except:
                self.logger.info("no page-specific animation was found")

            if not (self.current_chapter == len(self.active_story['chapters'])):
                print ("current_page: " + str(self.current_page))
                print ("current_chapter: " + str(self.current_chapter))
                page_content = self.active_story['chapters'][self.current_chapter]['pages'][self.current_page]['content']
                self.next_page()  # increment current_page and current_chapter
            else:
                print ("end of story")
                self.the_end = True
                page_content = ["the end"]

                try:
                    # look for outtro
                    _outtro_say = self.active_story['outtro_say']
                    self.logger.info(_outtro_say.encode('utf-8'))
                    qi.async(self.animatedSpeech.say, _outtro_say)

                except:
                    self.logger.info("no outtro_say was found")

            # print ("page content:")
            # print (page_content)
            # print ("last_page = "+ str(self.last_page))

            return render_template('page.html', title='page', content=page_content, story_id=self.story_id,
                                   lastpage=self.last_page, theend=self.the_end)

        @flaskapp.route('/question')
        def question():
            try:
                _question_animation = self.active_story['chapters'][self.current_chapter]['question_animation']
                self.logger.info(_question_animation)
                #sleep(3)  #disabled because the delay might annoys user
                self.logger.info("async runBehavior " + _question_animation)
                qi.async(self.beman.runBehavior, _question_animation)

            except:
                self.logger.info("no question_animation animation was found")

            question = self.active_story['chapters'][self.current_chapter]['question']
            choice_1 = self.active_story['chapters'][self.current_chapter]['options'].keys()[0]
            choice_2 = self.active_story['chapters'][self.current_chapter]['options'].keys()[1]

            return render_template('question.html', title='question', question=question, choice_1=choice_1,
                                   choice_2=choice_2)

        @flaskapp.route('/choice')
        def choice():

            self.user_choice = request.args.get('choice', None)
            self.logger.info("choice content, user selected: " + self.user_choice)

            _user_choice = self.active_story['chapters'][self.current_chapter]['options'][self.user_choice]
            self.last_page = False  # reset bool to default
            self.current_chapter = self.current_chapter + 1
            self.current_page = 0
            #sleep(3) #disabled because the delay might annoy user
            self.logger.info("runBehavior " + _user_choice)
            self.logger.info("Is installed: " + str(self.beman.isBehaviorInstalled(_user_choice)))
            self.logger.info("Is present: " + str(self.beman.isBehaviorPresent(_user_choice)))
            self.beman.runBehavior(_user_choice)


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

        self.feedback()
        if (self.current_page + 1) == len(self.active_story['chapters'][self.current_chapter]['pages']):
            print ("end of chapter")
            #print "\033[95m self.current_page = 0 \033[0m"
            #self.current_page = 0
            self.last_page = True


        #if (self.current_chapter == len(self.active_story['chapters'])):
        #    print ("end of story")
        #    self.the_end = True

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

        if self.conman.state() == 'online' or 'ready':
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
    def feedback(self):
        animation = ["animations/Stand/Gestures/Kisses_1",
         "animations/Stand/Emotions/Positive/Excited_1",
         "animations/Stand/Emotions/Positive/Excited_2",
         "animations/Stand/Emotions/Positive/Excited_3",
         "animations/Stand/Emotions/Positive/Happy_4"
         ]
        _a = random.choice(animation)
        self.logger.info("running animation %s" % _a)
        self.beman.runBehavior(_a)

        self.leds.on("FaceLeds")



    @qi.nobind
    def stop_app(self):
        # To be used if internal methods need to stop the service from inside.
        # external NAOqi scripts should use ALServiceManager.stopService if they need to stop it.
        
        with open('logfile.txt', 'a') as the_file:
            the_file.write('stopping at ' + str(datetime.datetime.now()) + ', ')
        
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
        #self.leds.on("FaceLeds")
        self.logger.info("Cleaned!")


if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    with open('logfile.txt', 'a') as the_file:
        the_file.write('main called\n')
    app = qi.Application(sys.argv)
    app.start()
    service_instance = PythonAppMain(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    flaskapp.run('0.0.0.0', PORT)  # start flask
    app.run()



    service_instance.cleanup()
    app.session.unregisterService(service_id)