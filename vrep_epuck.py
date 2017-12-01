
from vrep import InvalidArgumentValueError, TypedObjectsProxy
from vrep import Joint, ProximitySensor, VisionSensor

class EPuck:
    '''
    Clase de utilidad para trabajar con el robot ePuck en una simulación V-rep
    '''

    def __init__(self, scene, proximity_sensors = None, camera = None, light_sensor = None,
                 left_motor = None, right_motor = None):
        '''
        Inicializa la instancia.
        Pueden especificarse como parámetro los nombres de los componentes del robot e-Puck
        Si no se especifican, se buscarán por sus nombres que tienen por defecto al añadir e-Puck al
        simulador V-rep
        :param scene: Es la escena V-Rep
        :param proximity_sensors: Debe ser una lista con los nombres de los sensores de proximidad del e-Puck
        (en total deben ser ocho)
        El primer elemento será el primer sensor, el segundo el siguiente en la lista e.t.c, ...
        :param camera: Debe ser el nombre del sensor de visión del ePuck
        :param light_sensor: Debe ser el nombre del sensor de luz del ePuck (es otro sensor de visión)
        :param left_motor: Debe ser el nombre del motor izquierdo del ePuck
        :param right_motor: Debe ser el nombre del motor derecho del ePuck
        '''
        default_names = {
            'proximity_sensors' : [
                'ePuck_proxSensor1',
                'ePuck_proxSensor2',
                'ePuck_proxSensor3',
                'ePuck_proxSensor4',
                'ePuck_proxSensor5',
                'ePuck_proxSensor6',
                'ePuck_proxSensor7',
                'ePuck_proxSensor8'
            ],
            'camera' : 'ePuck_camera',
            'light_sensor' : 'ePuck_lightSensor',
            'left_motor' : 'ePuck_leftJoint',
            'right_motor' : 'ePuck_rightJoint'
        }

        if not proximity_sensors is None and len(proximity_sensors) != 8:
            raise InvalidArgumentValueError('proximity_sensors', proximity_sensors)

        names = {
            'proximity_sensors' : proximity_sensors,
            'camera' : camera,
            'light_sensor' : light_sensor,
            'left_motor' : left_motor,
            'right_motor' : right_motor
        }


        names = dict([(key, value) for key, value in names.items() if not value is None] +\
                     [(key, value) for key, value in default_names.items() if names[key] is None])


        # Obtenemos los componentes del robot
        class Proxy(TypedObjectsProxy):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def __getitem__(self, object_name):
                return super().__getattr__(object_name)

        joints = Proxy(scene.objects, Joint)
        proximity_sensors = Proxy(scene.objects, ProximitySensor)
        vision_sensors = Proxy(scene.objects, VisionSensor)

        # Motores izquierdo y derecha
        class Motors:
            def __init__(self):
                self.left = joints[names.get('left_motor')]
                self.right = joints[names.get('right_motor')]

        self.motors = Motors()
        self.left_motor = self.motors.left
        self.right_motor = self.motors.right

        # Cámara
        self.camera = vision_sensors[names.get('camera')]

        # Sensores de luz
        self.light_sensor = vision_sensors[names.get('light_sensor')]

        # Sensores de proximidad
        self.proximity_sensors = [proximity_sensors[name] for name in names.get('proximity_sensors')]