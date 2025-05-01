#!/usr/bin/python3

import time, os, random, logging
from paho.mqtt import client as mqtt_client

dt = 10    # time interval between measurement points
points = 10 # smoothing decay time in points

sensors = [] # list of sensors for the drivecage

