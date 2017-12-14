
from vrep import ObjectsCollection
from types import SimpleNamespace as Namespace

class EPuck(ObjectsCollection):
    '''
    Clase de utilidad para trabajar con el robot ePuck en una simulación V-rep

    Las mediciones de los sensores de proximidad están normalizadas en el rango [0, 1]
    '''

    # Objeto raíz de ePuck en la escena V-rep
    root = 'ePuck'

    # Definición de los componentes del robot E-Puck

    # Sensores de proximidad
    proximity_sensors = [
        'ePuck_proxSensor1',
        'ePuck_proxSensor2',
        'ePuck_proxSensor3',
        'ePuck_proxSensor4',
        'ePuck_proxSensor5',
        'ePuck_proxSensor6',
        'ePuck_proxSensor7',
        'ePuck_proxSensor8'
    ]

    # Sensores de visión
    vision_sensors = {
        'camera' : 'ePuck_camera',
        'light_sensor' : 'ePuck_lightSensor'
    }

    # Motores
    joints = {
        'left_motor' : 'ePuck_leftJoint',
        'right_motor' : 'ePuck_rightJoint'
    }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Definimos algunos alias para acceder a los componentes del robot.
        self.camera = self.vision_sensors.camera
        self.light_sensor = self.vision_sensors.light_sensor

        self.prox_sensors15 = Namespace(left = self.proximity_sensors[2],
                                        right = self.proximity_sensors[3])
        self.prox_sensors45 = Namespace(left = self.proximity_sensors[1],
                                        right = self.proximity_sensors[4])
        self.prox_sensors90 = Namespace(left = self.proximity_sensors[0],
                                        right = self.proximity_sensors[5])
        self.prox_sensors135 = Namespace(left = self.proximity_sensors[7],
                                         right = self.proximity_sensors[6])

        self.prox_sensor15 = self.proximity_sensors[3]
        self.prox_sensor45 = self.proximity_sensors[4]
        self.prox_sensor90 = self.proximity_sensors[5]
        self.prox_sensor135 = self.proximity_sensors[6]
        self.prox_sensor225 = self.proximity_sensors[7]
        self.prox_sensor270 = self.proximity_sensors[0]
        self.prox_sensor315 = self.proximity_sensors[1]
        self.prox_sensor345 = self.proximity_sensors[2]

        self.motors = Namespace(left = self.joints.left_motor,
                                right = self.joints.right_motor)
        self.left_motor = self.motors.left
        self.right_motor = self.motors.right


        # Configuramos los sensores de proximidad para normalizar las mediciones en
        # el rango [0, 1]
        for proximity_sensor in self.proximity_sensors:
            proximity_sensor.set_max_detection_distance(0.04)