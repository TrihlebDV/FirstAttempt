#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client

class Interval(object):
    def __init__(self):
        self.ip_robot = '10.42.0.69'
        self.control_port = 9000
        self.robot = xmlrpc.client.ServerProxy('http://%s:%d' % (self.ip_robot, self.control_port))

    def onButnCallback(self, state):
        self.robot.changePower(state)
