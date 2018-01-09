
'''
Collection of robots. In order to access the robots, you muest register them in the 'classes' dictionary.
Each entry is a pair: (shorthand name of the robot, class of the robot)
e.g: 'epuck' : epuck.EPuck
epuck robot will be accessible via scene.robots.epuck
'''

from .epuck import EPuck

classes = {
    'epuck' : EPuck
}



