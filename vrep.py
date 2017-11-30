


import vrep_binds as binds
from re import fullmatch
from functools import reduce
import numpy as np
import PIL
from PIL import Image


class _Exception(Exception):
    '''
    Es la clase base para todas las excepciones lanzadas por algún método de este script
    '''
    def __init__(self, *args):
        message = args[0].format(*args[1:]) if len(args) > 0 and isinstance(args[0], str) else (str(args[0]) if len(args) > 0 else 'Unknown exception')
        super().__init__(message)

Exception = _Exception
del _Exception


class ConnectionError(Exception):
    '''
    Error generado cuando hay un error de conexión con la API remota V-rep
    '''
    def __init__(self, address):
        super().__init__('Failed to connect to V-rep remote API server at {}', address)


class ConnectionAlreadyClosedError(Exception):
    '''
    Error generado cuando se intenta usar el cliente después de haber cerrado la conexión con la API remota V-rep
    '''
    def __init__(self):
        super().__init__('Connection to V-rep remote API server already closed')


class InvalidArgumentValueError(Exception):
    '''
    Error generado cuando a uno de los métodos de este módulo se le pasa un argumento con un formato o valor incorrecto
    '''
    def __init__(self, arg, value):
        super().__init__('Invalid value argument specified for {} parameter. Got value "{}"', arg, value)


class InvalidObjectTypeError(Exception):
    '''
    Error generado al intentar obtener un objeto de la escena V-rep de un tipo específico cuando el objeto
    no es del tipo deseado
    '''
    def __init__(self, object, expected_type):
        super().__init__('Invalid object type. Expected "{}" object but got "{}"', object, expected_type.__name__)


class ObjectNotFoundError(Exception):
    '''
    Error lanzado al intentar obtener un objeto de la escena V-rep por nombre y este no exista.
    '''
    def __init__(self, object_name):
        super().__init__('Failed to get object from V-rep scene named "{}"',object_name)



def alive(unchecked_method):
    '''
    Decorador auxiliar para los métodos de esta clase. Sirve para añadir código de comprobación a los inicios de estas
    funciones para lanzar una excepción en caso de que se haya cerrado la conexión con la API remota.
    '''
    def checked_method(self, *args, **kwargs):
        if not self.is_alive():
            raise ConnectionAlreadyClosedError()
        return unchecked_method(self, *args, **kwargs)

    return checked_method


class Client:
    '''
    Esta clase gestiona la conexión con la API remota de V-Rep
    Crea un cliente que se comunica con la API via sockets.

    e.g:
    client = vrep.Client(address = '127.0.0.1:19997')
    client.do_something()
    client.close()

    Es importante invocar el método close() al finalizar.
    También es posible usar la clase client utilizandola bajo un contexto with

    with vrep.Client(address = '127.0.0.1:19997') as client:
        client.do_something()

    En este caso, el método close() es invocado automáticamente al finalizar el bloque with
    '''
    def __init__(self, address = '127.0.0.1:19997', comm_thread_cycle = 5):
        '''
        Crea un nuevo cliente que se comunica mediante sockets con la API remota de V-Rep
        :param address: Es la dirección IP del servidor que implementa la API V-Rep. Por defecto
        es 127.0.0.1:19997. Si no se especifica el puerto, por defecto es 19997

        :param comm_thread_cycle: Número de milisegundos que separan dos envíos consecutivos de paquetes por la
        red a la API remota. Reducir esta cantidad mejorará el tiempo de respuesta y la sincronización entre
        cliente y la API remota. Por defecto se establece un valor de 5ms
        '''

        # Separamos la ip del puerto
        result = fullmatch('([\d\.]+)(:\d+)?', address)
        if result is None:
            raise InvalidArgumentValueError('address', address)
        ip, port = result.groups()

        port = int(fullmatch(':(.+)', port).group(1)) if not port is None else 19997

        self.alive = True
        self.id = binds.simxStart(ip, port, True, True, 5000, comm_thread_cycle)

        if self.id == -1:
            raise ConnectionError(address)

        self.simulation = Simulation(self)
        self.scene = Scene(self)

    @alive
    def close(self):
        '''
        Este método cierra la conexión con la API remota V-rep establecida. Después de invocar esta función, este objeto
        quedará inutilizable (cualquier llamada al mismo generará una excepción). Para establecer una nueva conexión se debe
        crear una nueva instancia de esta clase.
        :return:
        '''
        self.alive = False

        # Nos aseguramos que el último comando ha llegado al servidor correctamente.
        binds.simxGetPingTime(self.id)

        # Cerramos la conexión
        binds.simxFinish(self.id)

        del self.id

    def is_alive(self):
        '''
        :return: Devuelve un valor booleano indicando si la conexión con la API remote V-rep sigue estando activa. Devolverá True hasta
        que se invoque el método close().
        '''
        return self.alive


    @alive
    def get_id(self):
        '''
        :return: Devuelve el identificador de la conexión con la API remota usadas en las llamadas a los binds
        de la librería V-rep
        '''
        return self.id


    @alive
    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_alive():
            self.close()




class Simulation:
    '''
    Esta clase permite controlar el estado de la simulación de V-rep, pudiendo ejecutarla,
    pausarla o pararla.

    e.g:
    with Client('127.0.0.1:19997') as client:
        sim = client.simulation
        sim.pause()
        ...
        sim.resume()
        ...
        sim.stop()

    Las instancias de esta clase pueden usarse en contextos with:
    with Client('127.0.0.1:19997') as client:
        with client.simulation as sim:
            ...

    El código anterior es equivalente a introducir una llamada a
    sim.resume() al principio del bloque y sim.stop() al final (de manera
    que al comenzar el bloque, la simulación esta activa y al finalizar queda parada)
    '''

    def __init__(self, client):
        '''
        Inicializa la instancia.
        :param client: Es una instancia de la clase Client con el que se ha establecido una conexión a la servidor
        API remoto de V-rep donde se llevará a cabo esta simulación.
        '''
        self.client = client

    def resume(self):
        '''
        Resume la simulación.
        '''
        code = binds.simxStartSimulation(self.client.get_id(), binds.simx_opmode_blocking)
        if code != 0:
            raise Exception('Failed to resume V-rep simulation')

    def pause(self):
        '''
        La ejecución de la simulación queda pausada.
        :return:
        '''
        code = binds.simxPauseSimulation(self.client.get_id(), binds.simx_opmode_blocking)
        if code != 0:
            raise Exception('Failed to pause V-rep simulation')


    def stop(self):
        '''
        La simulación finaliza. Para comenzar otra nueva simulación, ejecutar de nuevo el método
        resume()
        :return:
        '''
        code = binds.simxStopSimulation(self.client.get_id(), binds.simx_opmode_blocking)
        if code != 0:
            raise Exception('Failed to stop V-rep simulation')


    def __enter__(self):
        self.resume()
        return self

    def __exit__(self, exc_type, exc_val, exc_tc):
        self.stop()



class Scene:
    '''
    Esta clase permite obtener información de los objetos de la escena del simulador V-rep.

    e.g:

    with Client(address = '127.0.0.1:19997') as client:
        scene = client.scene

        # Puedes consultar los objetos de la escena de varias formas. En este caso obtenemos un
        # objeto llamado 'camera'
        cam = scene.objects.camera
        cam = scene.objects['camera']
        cam = scene.get_object('camera')

        # En el primer caso, si el objeto 'camera' no existe, genera una excepción. En los dos últimos
        # casos simplemente devolvería None

        # Para asegurarnos que un objeto es de un determinado tipo, podemos consultarlo de la siguiente
        # forma...
        cam = scene.vision_sensors.camera
        cam = scene.vision_sensors.get('camera')
        cam = scene.vision_sensors['camera']

        # De esta forma, si 'camera' no es un sensor de visión, se genera una excepción.
        # Puedes usar también: scene.cameras, scene.proximity_sensors, scene.joints y scene.shapes
        # de la misma forma.

        # Podemos obtener todos los objetos de la escena
        objs = list(scene.objects)
        objs = [object for object in scene.objects]
        objs = scene.get_all_objects()

        # O también obtener todos los objetos de la misma con un tipo específico.
        sensors = list(scene.proximity_sensors)
        sensors = [sensor for sensor in scene.proximity_sensors]
        sensors = scene.get_all_objects_of_type(ProximitySensor)
    '''


    def __init__(self, client):
        '''
        Inicializa la instancia.
        :param client:  Es una instancia de la clase Client con el que se ha establecido una conexión a la servidor
        API remoto de V-rep donde se llevará a cabo esta simulación.
        '''
        self.client = client

        self.objects = ObjectsProxy(self.client)
        self.joints = self.objects.joints
        self.cameras = self.objects.cameras
        self.proximity_sensors = self.objects.proximity_sensors
        self.vision_sensors = self.objects.vision_sensors
        self.shapes = self.objects.shapes

    def get_object(self, name):
        '''
        Devuelve un objeto de la escena cuyo nombre es que se indica como parámetro.
        :param name:
        :return: Devuelve el objeto cuyo nombre es el que se indica, o None si el objeto no existe.
        '''
        return self.objects.get(name)

    def get_all_objects(self):
        '''
        Devuelve todos los objetos de la escena.
        Es igual que self.objects.get_all()
        :return:
        '''
        return self.objects.get_all()

    def get_all_objects_of_type(self, object_type):
        '''
        Devuelve todos los objetos de la escena que son de un tipo en concreto.
        e.g: get_all_objects_of_type(Joint)
        Es igual que self.objects.get_all_of_type
        :param object_type:
        :return:
        '''
        return self.objects.get_all_of_type(object_type)

class ObjectsProxy:
    '''
    Clase auxiliar usada por la clase Scene para obtener información de los objetos de la escena V-rep.
    '''
    def __init__(self, client):
        self.client = client
        self.object_type = {}
        self.cached_objects = {}
        self.object_types = [Joint, ProximitySensor, VisionSensor, Camera, Shape]
        self.bind_object_types = {
            Joint : binds.sim_object_joint_type,
            ProximitySensor : binds.sim_object_proximitysensor_type,
            VisionSensor : binds.sim_object_visionsensor_type,
            Camera : binds.sim_object_camera_type,
            Shape : binds.sim_object_shape_type
        }
        self.joints = TypedObjectsProxy(self, Joint)
        self.proximity_sensors = TypedObjectsProxy(self, ProximitySensor)
        self.vision_sensors = TypedObjectsProxy(self, VisionSensor)
        self.cameras = TypedObjectsProxy(self, Camera)
        self.shapes = TypedObjectsProxy(self, Shape)

    def get(self, object_name):
        '''
        Consulta un objeto de la escena V-rep cuyo nombre es el que se indica como argumento.
        :param object_name:
        :return: Devuelve un objeto cuyo nombre es el que se indica, o None si no existe ningún objeto con ese
        nombre
        '''
        if object_name in self.cached_objects:
            return self.cached_objects[object_name]

        code, handler = binds.simxGetObjectHandle(self.client.get_id(), object_name, binds.simx_opmode_blocking)
        if code != 0:
            return None

        object_type = self._get_type(handler)

        if object_type is None:
            raise Exception('Object retrieve from V-rep remote API has unrecognized type')

        cls = object_type
        object = cls(client = self.client, id = handler)
        self.cached_objects[object_name] = object

        return object


    def _get_type(self, handler):
        if handler in self.object_type:
            return self.object_type[handler]
        else:
            object_types = self.object_types
            for object_type in object_types:
                objects = self.get_all_of_type(object_type)
                for object in objects:
                    self.object_type[object.get_id()] = object_type

                if handler in [object.get_id() for object in objects]:
                    return object_type

            return None


    def get_all_of_type(self, object_type):
        '''
        Devuelve todos los objetos de un tipo específico.
        e.g:
        .get_all_of_type(object_type = Joint)
        :param object_type:
        :return:
        '''
        code, handlers = binds.simxGetObjects(self.client.get_id(), self.bind_object_types[object_type], binds.simx_opmode_blocking)
        if code != 0:
            raise Exception('Failed to retrieve objects of type {} from V-rep remote api server', object_type.__name__)

        cls = object_type
        objects = []
        cached_handlers = [object.get_id() for object in self.cached_objects.values()]
        for handler in handlers:
            if handler in cached_handlers:
                object = next(iter([object for object in self.cached_objects.values() if object.get_id() == handler]))
            else:
                object = cls(client = self.client, id = handler)
            objects.append(object)
        return objects


    def get_all(self):
        '''
        Devuelve todos los objetos de la escena V-rep
        :return:
        '''
        return reduce(lambda x,y:x+y, [self.get_all_of_type(object_type) for object_type in self.object_types])



    def __iter__(self):
        return iter(self.get_all())

    def __getattr__(self, object_name):
        object = self.get(object_name)
        if object is None:
            raise ObjectNotFoundError(object_name)
        return object

    def __getitem__(self, object_name):
        return self.get(object_name)


class TypedObjectsProxy:
    def __init__(self, objects, object_type):
        self.objects = objects
        self.object_type = object_type

    def get(self, object_name):
        object = self.objects.get(object_name)
        if not object is None and not isinstance(object, self.object_type):
            raise InvalidObjectTypeError(object, self.object_type)
        return object

    def get_all(self):
        return self.objects.get_all_of_type(self.object_type)


    def __getitem__(self, object_name):
        return self.get(object_name)

    def __getattr__(self, object_name):
        object = self.get(object_name)
        if object is None:
            raise ObjectNotFoundError(object_name)
        return object

    def __iter__(self):
        return iter(self.get_all())


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
    Representa un objeto del tipo 'Joint' (motor)
    '''
    pass

class ProximitySensor(Object):
    '''
    Representa un sensor de proximidad
    '''
    pass

class VisionSensor(Object):
    '''
    Representa un sensor de visión.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.streamed = False

    def get_image(self, mode = 'RGB', size = None, resample = Image.NEAREST):
        '''
        :param mode: Es el modo de la imágen, que puede ser RGB o L (escala de grises)
        :param size: Es una tupla con la resolución deseada de la imágen. Por defecto es None. Si es None,
        se devolverá la imágen con la resolución original captada en el simulador. Si se indica y la resolución
        deseada es distinta a la original, la imágen será redimensionada al tamaño indicado.
        :param resample: Es el algoritmo de redimensionamiento de la imágen. Por defecto es NEAREST.
        También puede ser BOX, BILINEAR, BICUBIC, HAMMING y LANCZOS.
        :return: Devuelve la imágen actual, una instancia de la clase Image de la librería PIL.

        En caso de error se genera una excepción.
        '''
        print(self.streamed)
        mode = mode.upper()
        if not mode in ['RGB', 'L']:
            raise InvalidArgumentValueError('mode', mode)

        if not self.streamed:
            code, native_size, pixels = binds.simxGetVisionSensorImage(self.client.get_id(), self.get_id(), 0 if mode == 'RGB' else 1, binds.simx_opmode_streaming)

            if not code in [0, 1]:
                raise Exception()
            code, native_size, pixels = binds.simxGetVisionSensorImage(self.client.get_id(), self.get_id(), 0 if mode == 'RGB' else 1, binds.simx_opmode_blocking)
            if code != 0:
                raise Exception()

            self.streamed = True
        else:
            code, native_size, pixels = binds.simxGetVisionSensorImage(self.client.get_id(), self.get_id(), 0 if mode == 'RGB' else 1, binds.simx_opmode_buffer)
            if not code in [0, 1]:
                raise Exception()

        native_size = tuple(native_size)

        pixels = np.reshape(np.array(pixels, dtype = np.uint8), native_size + ((3,) if mode == 'RGB' else ()))
        image = Image.fromarray(pixels, mode = mode)

        if not size is None and native_size != size:
            image = image.resize(size, resample)

        return image






class Camera(Object):
    '''
    Representa una cámara de la escena (no es lo mismo que un sensor de visión).
    '''
    pass

class Shape(Object):
    '''
    Representa una figura geométrica de la escena (Esferas, cubos, ...)
    '''
    pass
