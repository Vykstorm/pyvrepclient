
import vrep_binds as binds
import numpy as np
from PIL import Image
from vectormath import Vector3
from vrep_errors import Exception

class Object:
    '''
    Representa un objeto de la escena. Esta clase no se instancia directamente. Las subclases de esta
    definen distintos tipos de objetos de la escena V-rep.
    '''
    def __init__(self, client, id):
        self.client = client
        self.id = id

    def __str__(self):
        return self.__class__.__name__

    def get_id(self):
        return self.id




class Joint(Object):
    '''
    Representa un objeto del tipo 'Joint' (una unión entre varios objetos) que puede ser pasivo o
    activo (actua como un motor)
    '''
    def _set_velocity(self, amount):
        '''
        Establece la velocidad del motor.
        :param amount: Es la velocidad del motor, en metros/segundo o en radianes/segundo en función del
        tipo de unión.
        :return:
        '''
        code = binds.simxSetJointTargetVelocity(self.client.get_id(), self.get_id(), amount, binds.simx_opmode_oneshot)
        if not code in [0, 1]:
            raise Exception('Failed to set velocity to V-rep joint object')

    def _set_linear_velocity(self, amount):
        '''
        Establece la velocidad lineal actual (en metros/segundo)
        :param amount:
        :return:
        '''
        self._set_velocity(amount)

    def _set_angular_velocity(self, amount):
        '''
        Establece la velocidad angular actual (en radianes / segundo)
        :param amount:
        :return:
        '''
        self._set_velocity(amount)


    def set_velocity(self, amount):
        raise NotImplementedError()


    @property
    def velocity(self):
        raise NotImplementedError()

    @velocity.setter
    def velocity(self, amount):
        self.set_velocity(amount)

    speed = velocity


class PrismaticJoint(Joint):
    '''
    Es un tipo de unión que puede llevar a cabo movimientos de translación con un grado de libertad.
    '''
    def set_velocity(self, amount):
        '''
        Establece la velocidad actual de la unión (en metros / segundo)
        :param amount:
        :return:
        '''
        self._set_linear_velocity(amount)

class SphericalJoint(Joint):
    '''
    Es un tipo de unión que puede realizar movimientos de rotación con tres grados de libertad.
    '''
    def set_velocity(self, amount):
        '''
        Establece la velocidad actual de la unión (en radianes / segundo)
        :param amount:
        :return:
        '''
        self._set_angular_velocity(amount)


class RevoluteJoint(Joint):
    '''
    Es un tipo de unión que realiza movimientos de rotación con un grado de libertad.
    '''
    def set_velocity(self, amount):
        '''
        Establece la velocidad actual de la unión (en radianes / segundo)
        :param amount:
        :return:
        '''
        self._set_angular_velocity(amount)



class Sensor(Object):
    '''
    Representa un sensor. Puede ser un sensor de proximidad o un sensor de visión.
    La escena debe estar activa (debe haberse invocado scene.simulation.resume()) antes de muestrar
    un sensor.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.streamed = False
        self.initial_value = None

    def start_streaming(self):
        '''
        Este método inicializa el sensor y crea un stream de datos entre cliente y servidor
        para actualizar la medición del sensor cada cierto tiempo. Después de invocar este método,
        el valor de muestra del sensor se obtiene de un buffer en el cliente (normalmente es un valor
        de medición anterior), es decir, no envía una petición al servidor para obtener la medición.
        Debe ser implementado por las subclases y deben asignar la variable streamed a True
        '''
        self.streamed = True

    def _get_data(self, streamed):
        '''
        Este método debe devolver el valor de medición actual del sensor.
        Debe ser implementado por las subclases.
        :param streamed: Si streamed es True, debe devolver la medición actual almacenada en el buffer del cliente.
        En caso contrario, debe hacer un petición al simulador V-rep para obtener el valor del sensor
        :return:
        '''
        raise NotImplementedError()

    def get_value(self):
        ''''
        Este método devuelve la medición actual del sensor.
        La simulación debe estar ejecutandose para obtener valores de los sensores.
        '''
        simulation = self.client.simulation

        if not simulation.is_running():
            raise Exception('Error getting sensor data: V-rep simulation is not running')

        if not self.streamed:
            data = self._get_data(streamed=False)
            self.start_streaming()
            self.initial_value = data
            value = data
        else:
            try:
                data = self._get_data(streamed=True)
                value = data
                if not self.initial_value is None:
                    self.initial_value = None
            except Exception as exc:
                if self.initial_value is None:
                    raise exc
                value = self.initial_value

        return value


    @property
    def value(self):
        return self.get_value()

class ProximitySensor(Sensor):
    '''
    Representa un sensor de proximidad

    El sensor puede calcular la distancia a un objeto detectado.
    El valor del sensor está en metros. Si no se detecta ningún objeto, el valor del sensor devuelve float('inf')
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def start_streaming(self):
        super().start_streaming()

        try:
            values = binds.simxReadProximitySensor(self.client.get_id(), self.get_id(), binds.simx_opmode_streaming)
            code = values[0]
            if not code in [0, 1]:
                raise Exception()
        except:
            raise Exception('Error initializing proximity sensor data stream on V-rep remote API server')

    def _get_data(self, streamed):
        opmode = binds.simx_opmode_blocking if not streamed else binds.simx_opmode_buffer
        values = binds.simxReadProximitySensor(self.client.get_id(), self.get_id(), opmode)
        code = values[0]
        if code != 0:
            raise Exception('Error getting proxmity sensor data from client buffer')

        detected_state, detected_point, detected_object, detected_surface_normal = values[1:]
        if not detected_state:
            return float('inf')
        detected_point = Vector3(detected_point)
        length = detected_point.length
        return length

class VisionSensor(Sensor):
    '''
    Representa un sensor de visión.
    '''

    def start_streaming(self):
        super().start_streaming()

        try:
            values = binds.simxGetVisionSensorImage(self.client.get_id(), self.get_id(), 0, binds.simx_opmode_streaming)
            code = values[0]
            if not code in [0, 1]:
                raise Exception()
        except:
            raise Exception('Error initializing vision sensor data stream on V-rep remote API server')


    def _get_data(self, streamed):
        opmode = binds.simx_opmode_blocking if not streamed else binds.simx_opmode_buffer

        values = binds.simxGetVisionSensorImage(self.client.get_id(), self.get_id(), 0, opmode)
        code = values[0]
        if code != 0:
            raise Exception('Error getting vision sensor data from client buffer')
        native_size, pixels = values[1:]
        native_size = tuple(native_size)
        pixels = np.reshape(np.array(pixels, dtype=np.uint8), (native_size + (3,)))

        return pixels


    def get_image(self, mode = 'RGB', size = None, resample = Image.NEAREST):
        '''
        Interpreta la medición del sensor como una imágen.
        :param mode: Es el modo de la imágen (RGB, 1, L, P, ...). Son modos de imágen definidos por la librería Pillow
        :param size: Es una tupla con la resolución deseada de la imágen. Por defecto es None. Si es None,
        se devolverá la imágen con la resolución original captada en el simulador. Si se indica y la resolución
        deseada es distinta a la original, la imágen será redimensionada al tamaño indicado.
        :param resample: Es el algoritmo de redimensionamiento de la imágen. Por defecto es NEAREST.
        También puede ser BOX, BILINEAR, BICUBIC, HAMMING y LANCZOS.
        :return: Devuelve la imágen actual, una instancia de la clase Image de la librería Pillow.
        En caso de error se genera una excepción.
        '''
        pixels = self.get_value()
        try:
            native_size = pixels.shape[0:2]
            image = Image.fromarray(pixels, mode='RGB')

            if mode != 'RGB':
                image = image.convert(mode = mode)

            if not size is None and native_size != size:
                image = image.resize(size, resample)

            return image
        except:
            raise Exception('Error getting image`s pixels data from vision sensor')

    @property
    def image(self):
        return self.get_image()

class Shape(Object):
    '''
    Representa una figura geométrica de la escena (Esferas, cubos, ...)
    '''
    pass