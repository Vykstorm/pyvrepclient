import vrep_binds as binds

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
        self.running = False

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