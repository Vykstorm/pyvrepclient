


import vrep_binds as binds
from re import fullmatch


class _Exception(Exception):
    '''
    Es la clase base para todas las excepciones lanzadas por algún método de este script
    '''
    def __init__(self, message, *args):
        super().__init__(message.format(*args))

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


class OperationError(Exception):
    '''
    Esta clase de errores son lanzados cuando no falla algún método de la API remota V-rep
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args ,**kwargs)



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
            raise OperationError('Failed to resume V-rep simulation')

    def pause(self):
        '''
        La ejecución de la simulación queda pausada.
        :return:
        '''
        code = binds.simxPauseSimulation(self.client.get_id(), binds.simx_opmode_blocking)
        if code != 0:
            raise OperationError('Failed to pause V-rep simulation')


    def stop(self):
        '''
        La simulación finaliza. Para comenzar otra nueva simulación, ejecutar de nuevo el método
        resume()
        :return:
        '''
        code = binds.simxStopSimulation(self.client.get_id(), binds.simx_opmode_blocking)
        if code != 0:
            raise OperationError('Failed to stop V-rep simulation')


    def __enter__(self):
        self.resume()
        return self

    def __exit__(self, exc_type, exc_val, exc_tc):
        self.stop()


