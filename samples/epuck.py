

'''
Ejemplo que demuestra como utilizar esta librería para manejar el robot ePuck, obtener información
de los sensores de proximidad y controlar los motores del mismo de forma remota.

Carga antes primero la escena preparada para este programa en el simulador V-rep llamada "epuck.ttt", en
el directorio scenes/
'''

from vrep import Client
from math import pi

if __name__ == '__main__':
    with Client('127.0.0.1:19997') as client:
        simulation = client.simulation
        scene = simulation.scene
        epuck = scene.robots.epuck


        # Iniciamos la simulación
        simulation.resume()

        try:
            print('Starting simulation')

            epuck.left_motor.set_velocity(0)
            epuck.right_motor.set_velocity(0)
            while True:
                v1, v2 = epuck.prox_sensor15.get_value(), epuck.prox_sensor345.get_value()
                v3, v4 = epuck.prox_sensor90.get_value(), epuck.prox_sensor270.get_value()
                if v3 > 0 or v1 > 0 or v2 > 0:
                    epuck.left_motor.set_velocity(-pi / 2)
                    epuck.right_motor.set_velocity(pi / 2)
                elif v4 > 0:
                    epuck.left_motor.set_velocity(pi / 2)
                    epuck.right_motor.set_velocity(-pi / 2)
                else:
                    epuck.right_motor.set_velocity(pi)
                    epuck.left_motor.set_velocity(pi)


        except Exception as e:
            print('Something went wrong: {}'.format(e))

        finally:
            # Paramos la simulación
            simulation.stop()

            print('Simulation finish')
