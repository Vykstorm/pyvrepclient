# Copyright 2006-2017 Coppelia Robotics GmbH. All rights reserved. 
# marc@coppeliarobotics.com
# www.coppeliarobotics.com
# 
# -------------------------------------------------------------------
# THIS FILE IS DISTRIBUTED "AS IS", WITHOUT ANY EXPRESS OR IMPLIED
# WARRANTY. THE USER WILL USE IT AT HIS/HER OWN RISK. THE ORIGINAL
# AUTHORS AND COPPELIA ROBOTICS GMBH WILL NOT BE LIABLE FOR DATA LOSS,
# DAMAGES, LOSS OF PROFITS OR ANY OTHER KIND OF LOSS WHILE USING OR
# MISUSING THIS SOFTWARE.
# 
# You are free to use/modify/distribute this file for whatever purpose!
# -------------------------------------------------------------------
#
# This file was automatically created for V-REP release V3.4.0 rev. 1 on April 5th 2017

# Make sure to have the server side running in V-REP: 
# in a child script of a V-REP scene, add following command
# to be executed just once, at simulation start:
#
# simExtRemoteApiStart(19999)
#
# then start simulation, and run this program.
#
# IMPORTANT: for each successful call to simxStart, there
# should be a corresponding call to simxFinish at the end!

try:
    import vrep_binds
except:
    print ('--------------------------------------------------------------')
    print ('"vrep_binds.py" could not be imported. This means very probably that')
    print ('either "vrep_binds.py" or the remoteApi library could not be found.')
    print ('Make sure both are in the same folder as this file,')
    print ('or appropriately adjust the file "vrep_binds.py"')
    print ('--------------------------------------------------------------')
    print ('')

import time

from time import sleep
from PIL import Image
import PIL
import numpy

print ('Program started')
vrep_binds.simxFinish(-1) # just in case, close all opened connections
clientID=vrep_binds.simxStart('127.0.0.1', 19997, True, True, 5000, 5) # Connect to V-REP
if clientID!=-1:
    print ('Connected to remote API server')

    # Now try to retrieve data in a blocking fashion (i.e. a service call):
    res,objs=vrep_binds.simxGetObjects(clientID, vrep_binds.sim_handle_all, vrep_binds.simx_opmode_blocking)
    if res==vrep_binds.simx_return_ok:
        print ('Number of objects in the scene: ',len(objs))
    else:
        print ('Remote API function call returned with error code: ',res)


    code, left_motor = vrep_binds.simxGetObjectHandle(clientID, 'ePuck_leftJoint', vrep_binds.simx_opmode_blocking)
    code, right_motor = vrep_binds.simxGetObjectHandle(clientID, 'ePuck_rightJoint', vrep_binds.simx_opmode_blocking)


    code, sensor = vrep_binds.simxGetObjectHandle(clientID, 'ePuck_proxSensor1', vrep_binds.simx_opmode_blocking)


    code, camera = vrep_binds.simxGetObjectHandle(clientID, 'ePuck_camera', vrep_binds.simx_opmode_blocking)

    code, resolution, pixels = vrep_binds.simxGetVisionSensorImage(clientID, camera, 0, vrep_binds.simx_opmode_streaming)
    sleep(1)
    code, resolution, pixels = vrep_binds.simxGetVisionSensorImage(clientID, camera, 0, vrep_binds.simx_opmode_blocking)
    pixels = numpy.uint8(numpy.array(pixels))

    pixels = numpy.reshape(pixels, (128, 128, 3))

    #image = Image.new(mode = 'RGB', size = resolution)
    image = Image.fromarray(pixels, mode = 'RGB')
    image.show()


    # Before closing the connection to V-REP, make sure that the last command sent out had time to arrive. You can guarantee this with (for example):
    vrep_binds.simxGetPingTime(clientID)

    # Now close the connection to V-REP:
    vrep_binds.simxFinish(clientID)
else:
    print ('Failed connecting to remote API server')
print ('Program ended')
