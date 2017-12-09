

'''
You can contribute to this library adding new robots.

This is a template script to add a new robot to this library.
For example, if the new robot is named "myrobot", you can later access
the components of the robot (sensors, joints, ...) with
scene.robots.myrobot

Example:
with Client('127.0.0.1:19997') as client:
    scene = client.scene
    myrobot = scene.robots.myrobot

    # Print the value of the first proximity sensor
    print(myrobot.proximity_sensors[0].get_value())
'''

from vrep import ObjectsCollection

class MyRobot(ObjectsCollection):
    '''
    This class is a template to define the robot. Must be inherited from
    class ObjectsCollection
    '''

    '''
    This variable defines the proximity sensors of the robot.
    Each entry of the dictionary defines a component of the robot, in this case
    a proximity sensor. The key is an alias to access the component and the value
    is the name of the component in the vrep's scene.
    for example:
    'prox_sensor1' : 'vrep_proximity_sensor1'
    
    Now if you can reference the sensor with myrobot.proximity_sensors.prox_sensor1 
    '''
    proximity_sensors = {
        # 'prox_sensor' : 'vrep_prox_sensor1'
    }


    '''
    Last variable could be a list of components.
    e.g: 
    [ 'vrep_prox_sensor1', 'vrep_prox_sensor2']
    And sensors could be referenced with:
    myrobot.proximity_sensors[0], myrobot.proximity_sensors[1]
    '''
    #proximity_sensors = [
    #    'vrep_prox_sensor1',
    #    'vrep_prox_sensor2'
    #]



    # This variable define vision sensors of the robot.
    vision_sensor = {
        # 'camera' : 'vrep_vision_sensor'
    }


    # This variable define joints of the robot
    joints = {
        # 'motor' : 'vrep_joint'
    }

    # This variable define the shapes of the robot
    shapes = {
        # 'shape' : 'vrep_shape'
    }



    # The robot is defined now, but if you want to customize it,
    # you can define a constructor like this
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # For example, if you want to reference a sensor like:
        # myrobot.camera
        # you could do...

        # self.camera = self.vision_sensors.camera
