

'''
Este script define errores lanzados por esta librería
'''


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
    def __init__(self, ip, port):
        super().__init__('Failed to connect to V-rep remote API server at {}:{}', ip, port)


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

class ObjectsCollectionNotFoundError(Exception):
    '''
    Error lanzado al intentar obtener una colección de objetos no existente
    '''
    def __init__(self, collection_name):
        super().__init__('Failed to get object`s collection named "{}"', collection_name)