

'''
Ejemplo que demuestra como utilizar esta librería para manejar el robot ePuck, obtener información
de los sensores de proximidad y controlar los motores del mismo de forma remota.

Carga antes primero la escena preparada para este programa en el simulador V-rep llamada "epuck_example1.ttt", en
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

            while True:
                v1, v2 = epuck.prox_sensor15.value, epuck.prox_sensor345.value
                v3, v4 = epuck.prox_sensor90.value, epuck.prox_sensor270.value

                if v1 <= 0.04 or v2 <= 0.04 or v3 <= 0.04:
                    epuck.left_motor.speed = -90
                    epuck.right_motor.speed = 90
                elif v4 <= 0.04:
                    epuck.left_motor.speed = 90
                    epuck.right_motor.speed = -90
                else:
                    epuck.right_motor.speed = 180
                    epuck.left_motor.speed = 180


        except Exception as e:
            print('Something went wrong: {}'.format(e))

        finally:
            # Paramos la simulación
            simulation.stop()

            print('Simulation finish')
