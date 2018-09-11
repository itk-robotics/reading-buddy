#!/usr/bin/env python

#Author: Anders Krogsager
#@Brainbotics.com

import sys
import qi
import naoqi
import almath
import platform


if __name__ == '__main__':

    print "script name: " + __name__ + "\n"
    print "***Platform info***"
    print platform.processor()
    print platform.version()
    print platform.machine()
    print platform.uname()
    print platform.system()
    print platform.platform() + "\n"

    print "***naoqi info***"
    print qi.__file__
    print naoqi.__file__
    print almath.__file__ + "\n"

    print "*** sys invote path, sys path[0] ***"
    print sys.path[0] + "\n"

    print '\n'.join(sys.path)

    raw_input("press any key to closes")

