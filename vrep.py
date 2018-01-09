


import vrep_binds as binds
from vrep_errors import *
from vrep_objects import *

from re import fullmatch
from functools import reduce
import json



def alive(unchecked_method):
    '''
    Decorador auxiliar para los métodos de la clase Client. Sirve para añadir código de comprobación al inicio de estas
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
            raise ConnectionError(ip, port)

        self.remote_methods = RemoteMethodsProxy(self)
        self.simulation = Simulation(self)

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
    def __init__(self, client):
        '''
        Inicializa la instancia.
        :param client: Es una instancia de la clase Client con el que se ha establecido una conexión a la servidor.
        API remoto de V-rep donde se llevará a cabo esta simulación.
        '''
        self.client = client
        self.running = False
        self.init()
        self.scene = Scene(self.client)

    def init(self):
        '''
        Inicializa la simulación. Debe invocarse este método antes de usar cualquier otro.
        :return:
        '''
        try:
            code = binds.simxStartSimulation(self.client.get_id(), binds.simx_opmode_blocking)
            if code != 0:
                raise Exception()
            code = binds.simxPauseSimulation(self.client.get_id(), binds.simx_opmode_blocking)
            if code != 0:
                raise Exception()
        except:
            raise Exception('Failed to initialize V-rep simulation')

    def resume(self):
        '''
        Resume la simulación.
        '''
        if not self.running:
            code = binds.simxStartSimulation(self.client.get_id(), binds.simx_opmode_blocking)
            if code != 0:
                raise Exception('Failed to resume V-rep simulation')

            self.running = True

    def pause(self):
        '''
        La ejecución de la simulación queda pausada.
        :return:
        '''
        if self.running:
            code = binds.simxPauseSimulation(self.client.get_id(), binds.simx_opmode_blocking)
            if code != 0:
                raise Exception('Failed to pause V-rep simulation')


    def stop(self):
        '''
        La simulación finaliza. Para comenzar otra nueva simulación, ejecutar de nuevo el método
        resume()
        :return:
        '''
        if self.running:
            code = binds.simxStopSimulation(self.client.get_id(), binds.simx_opmode_blocking)
            if code != 0:
                raise Exception('Failed to stop V-rep simulation')

            self.running = False

    def is_running(self):
        '''
        Comprueba si la simulación esta activa. Será True después de haber invocado resume() y False después
        de la ejecución del método stop()
        '''
        return self.running

    def __enter__(self):
        self.resume()
        return self

    def __exit__(self, exc_type, exc_val, exc_tc):
        self.stop()


class RemoteMethodsProxy:
    '''
    Clase auxiliar usada por Client para hacer llamadas a procedimientos remotos en un script lua en el
    simulador V-rep
    '''
    class RemoteMethod:
        def __init__(self, client, name):
            self.client = client
            self.name = name

        def __call__(self, *args):
            result = binds.simxCallScriptFunction(self.client.get_id(), 'ScriptHandler',
                                                  binds.sim_scripttype_childscript,
                                                  'function_proxy',
                                                  [], [], [self.name, json.dumps(args)], bytearray(),
                                                  binds.simx_opmode_blocking)
            code, ints, floats, strings, buffer = result
            try:
                if code != 0:
                    raise Exception()
                try:
                    result = tuple(json.loads(strings[0]))
                    if len(result) == 0:
                        return None
                    return result[0] if len(result) == 1 else result
                except:
                    raise Exception()
            except:
                raise RemoteMethodError(self.name)


    def __init__(self, client):
        self.client = client

    def __getitem__(self, method_name):
        return self.RemoteMethod(self.client, method_name)

    def __getattr__(self, method_name):
        return self.__getitem__(method_name)



class Scene:
    '''
    Esta clase permite obtener información de los objetos de la escena del simulador V-rep.
    '''
    def __init__(self, client):
        '''
        Inicializa la instancia.
        :param client:  Es una instancia de la clase Client con el que se ha establecido una conexión a la servidor
        API remoto de V-rep donde se llevará a cabo esta simulación
        '''
        self.client = client

        self.objects = ObjectsProxy(self.client)
        self.joints = self.objects.joints
        self.proximity_sensors = self.objects.proximity_sensors
        self.vision_sensors = self.objects.vision_sensors
        self.shapes = self.objects.shapes
        self.robots = ObjectsCollectionsProxy(self, robots.classes)

    def get_object(self, object_name):
        '''
        Devuelve un objeto de la escena cuyo nombre es que se indica como parámetro.
        :param name:
        :return: Devuelve el objeto cuyo nombre es el que se indica, o None si el objeto no existe.
        '''
        return self.objects.get(object_name)


    def get_robot(self, robot_name):
        '''
        Devuelve un robot de la escena V-rep cuyo nombre se indica como parámetro.
        :param robot_name: Es el nombre del robot
        :return: Devuelve una instancia de la clase ObjectsCollection (una colección de objetos con los
        componentes del robot). Devuelve None si no existe ningún robot con ese nombre.
        '''
        return self.robots.get(robot_name)


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

    def object_exists(self, object_name):
        '''
        Comprueba si un objeto con el nombre indicado como parámetro existe o no.
        :param object_name: Es el nombre del objeto.
        :return:
        '''
        return self.object.has(object_name)



class ObjectsProxy:
    '''
    Clase auxiliar usada por la clase Scene para obtener información de los objetos de la escena V-rep.
    '''
    def __init__(self, client):
        self.client = client

        self.cached_objects = {}
        self.bind_object_types = {
            # binds.sim_object_joint_type : Joint,
            binds.sim_joint_revolute_subtype : RevoluteJoint,
            binds.sim_joint_prismatic_subtype : PrismaticJoint,
            binds.sim_joint_spherical_subtype : SphericalJoint,
            binds.sim_object_proximitysensor_type : ProximitySensor,
            binds.sim_object_visionsensor_type : VisionSensor,
            binds.sim_object_shape_type : Shape
        }
        objects_info = self.client.remote_methods.get_objects_info()
        objects_info = [(object_handler, object_name, object_type) for object_handler, object_name, object_type in objects_info if object_type in self.bind_object_types]

        self.object_handlers = dict([(object_name, object_handler) for object_handler, object_name, object_type in objects_info])
        self.object_types = dict([(object_name, self.bind_object_types[object_type]) for object_handler, object_name, object_type in objects_info])
        self.objects_by_type = dict([(object_type, [object_name for object_name in self.object_types if self.object_types[object_name] == object_type])
                                     for object_type in self.bind_object_types.values()])

        self.joints = TypedObjectsProxy(self, Joint)
        self.proximity_sensors = TypedObjectsProxy(self, ProximitySensor)
        self.vision_sensors = TypedObjectsProxy(self, VisionSensor)
        self.shapes = TypedObjectsProxy(self, Shape)



    def get(self, object_name):
        '''
        Consulta un objeto de la escena V-rep cuyo nombre es el que se indica como argumento.
        :param object_name:
        :return: Devuelve un objeto cuyo nombre es el que se indica, o None si no existe ningún objeto con ese nombre
        '''
        if object_name in self.cached_objects:
            return self.cached_objects[object_name]

        if not self.has(object_name):
            return None
        object_handler = self.object_handlers[object_name]
        object_type = self.object_types[object_name]

        cls = object_type
        object = cls(client = self.client, id = object_handler)
        self.cached_objects[object_name] = object

        return object

    def has(self, object_name):
        '''
        Comprueba si un objeto cuyo nombre se especifica como parámetro, existe en la escena V-rep
        :param object_name:
        :return:
        '''
        return object_name in self.object_handlers



    def get_all_of_type(self, object_type):
        '''
        Devuelve todos los objetos de un tipo específico.
        e.g:
        .get_all_of_type(object_type = Joint)
        :param object_type:
        :return:
        '''
        return [self.get(object_name) for object_name in self.objects_by_type[object_type]]


    def get_all(self):
        '''
        Devuelve todos los objetos de la escena V-rep
        :return:
        '''
        return [self.get(object_name) for object_name in self.object_handlers]

    def __iter__(self):
        return iter(self.get_all())


    def __getitem__(self, object_name):
        object = self.get(object_name)
        if object is None:
            raise ObjectNotFoundError(object_name)
        return object

    def __getattr__(self, object_name):
        return self.__getitem__(object_name)

    def __contains__(self, object_name):
        return self.has(object_name)


class TypedObjectsProxy:
    '''
    Es usada por la clase Scene para acceder a los objetos de la escena V-rep. Es igual que la clase
    ObjectsProxy, pero además realiza una comprobación del tipo de objeto (se asegura que los objetos
    accedidos son del tipo adecuado)
    '''
    def __init__(self, objects, object_type):
        self.objects = objects
        self.object_type = object_type

    def get(self, object_name):
        object = self.objects.get(object_name)
        if not object is None and not isinstance(object, self.object_type):
            raise InvalidObjectTypeError(object, self.object_type)
        return object

    def has(self, object_name):
        object = self.objects.get(object_name)
        return object is None and isinstance(object, self.object_type)

    def get_all(self):
        return self.objects.get_all_of_type(self.object_type)

    def __getitem__(self, object_name):
        object = self.get(object_name)
        if object is None:
            raise ObjectNotFoundError(object_name)
        return object

    def __getattr__(self, object_name):
        return self.__getitem__(object_name)

    def __iter__(self):
        return iter(self.get_all())

    def __contains__(self, object_name):
        return self.has(object_name)


class ObjectsCollectionsProxy:
    '''
    Clase usada para acceder a colleciones de objetos de la escena V-rep, usada por la clase Scene
    '''
    def __init__(self, scene, collection_classes):
        self.scene = scene
        self.collection_classes = collection_classes
        self.cached = {}

    def get(self, collection_name):
        if not collection_name in self.collection_classes:
            return None
        if collection_name in self.cached:
            return self.cached[collection_name]

        try:
            cls = self.collection_classes[collection_name]
            collection = cls(self.scene)
            self.cached[collection_name] = collection
        except:
            return None
        return collection

    def __getitem__(self, collection_name):
        collection = self.get(collection_name)
        if collection is None:
            raise ObjectsCollectionNotFoundError(collection_name)
        return collection

    def __getattr__(self, collection_name):
        return self.__getitem__(collection_name)





class ObjectsCollection:
    '''
    Se usa para definir colecciones de objetos en la escena V-rep
    '''

    root = None

    proximity_sensors = {

    }

    vision_sensors = {

    }

    joints = {

    }

    shapes = {

    }

    class ObjectsProxy(TypedObjectsProxy):
        def __init__(self, objects, object_type, name_mapping, duplicate_offset):
            super().__init__(objects, object_type)

            if not duplicate_offset is None:
                if isinstance(name_mapping, dict):
                    self.name_mapping = dict([(object_alias, object_name + '#' + str(duplicate_offset - 1)) for object_alias, object_name in name_mapping.items()])
                else:
                    self.name_mapping = [object_name + '#' + str(duplicate_offset - 1) for object_name in name_mapping]
            else:
                self.name_mapping = name_mapping


        def get(self, object_name):
            if isinstance(self.name_mapping, dict):
                if not object_name in self.name_mapping:
                    return None
                return super().get(self.name_mapping[object_name])

            else:
                object_index = object_name
                if object_index >= len(self.name_mapping) or object_index < 0:
                    return None
                return super().get(self.name_mapping[object_name])

        def __getitem__(self, object_name):
            try:
                return super().__getitem__(object_name)
            except:
                if not object_name in self.name_mapping:
                    if isinstance(self.name_mapping, dict):
                        raise Exception('No {} named "{}" is part of the collection', self.object_type.__name__, object_name)
                    else:
                        object_index = object_name
                        if object_index >= len(self.name_mapping) or object_index < 0:
                            raise Exception('Trying to get {0} at index {1}. There are only {2} in the collection', self.object_type.__name__, object_index, len(self.name_mapping))
                        else:
                            raise ObjectNotFoundError(self.name_mapping[object_name])
                else:
                    raise ObjectNotFoundError(self.name_mapping[object_name])

        def get_all(self):
            object_names = self.name_mapping.keys() if isinstance(self.name_mapping, dict) else range(0, len(self.name_mapping))
            return [self[object_name] for object_name in object_names]

        def __len__(self):
            return len(self.name_mapping)


    def __init__(self, scene, duplicate_offset = None):
        self.duplicate_offset = duplicate_offset
        self.scene = scene

        try:
            if self.root is None:
                raise Exception()
            if duplicate_offset is None:
                if not scene.objects.has(self.root):
                    raise ObjectNotFoundError(self.root)
            else:
                if not scene.objects.has(self.root + '#' + str(self.duplicate_offset - 1)):
                    raise Exception()
        except:
            raise Exception('Failed to retrieve object`s collection root')


        self.proximity_sensors = self.ObjectsProxy(self.scene.objects, ProximitySensor, self.__class__.proximity_sensors, self.duplicate_offset)
        self.vision_sensors = self.ObjectsProxy(self.scene.objects, VisionSensor, self.__class__.vision_sensors, self.duplicate_offset)
        self.joints = self.ObjectsProxy(self.scene.objects, Joint, self.__class__.joints, self.duplicate_offset)
        self.shapes = self.ObjectsProxy(self.scene.objects, Shape, self.__class__.shapes, self.duplicate_offset)


    def __getitem__(self, index):
        if not self.duplicate_offset is None:
            raise NotImplementedError()

        if index == 0:
            return self
        try:
            cls = self.__class__
            duplicate = cls(self.scene, duplicate_offset = index)
            return duplicate
        except:
            raise ObjectsCollectionNotFoundError(self.__class__.__name__)


    class Iterator:
        def __init__(self, collection):
            self.collection = collection
            self.index = 0

        def __next__(self):
            try:
                item = self.collection[self.index]
                self.index += 1
                return item
            except:
                raise StopIteration

    def __iter__(self):
        if not self.duplicate_offset is None:
            raise NotImplementedError()
        return self.Iterator(self)

import robots