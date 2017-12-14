


'''
Es igual que el ejemplo 1 de como usar robots ePuck en la escena V-rep, solo que ahora se manejan
dos ePucks en vez de uno
'''

from time import sleep

from PIL import Image

from robots.epuck import EPuck
from vrep import Client
from math import pi

if __name__ == '__main__':
    with Client('127.0.0.1:19997') as client:
        simulation = client.simulation
        scene = simulation.scene

        epucks = list(scene.robots.epuck)
        print('Working with {} robots'.format(len(epucks)))

        # Iniciamos la simulación
        simulation.resume()

        try:
            print('Starting simulation')

            while True:
                for epuck in epucks:
                    v1, v2 = epuck.prox_sensor15.get_value(), epuck.prox_sensor345.get_value()
                    v3, v4 = epuck.prox_sensor90.get_value(), epuck.prox_sensor270.get_value()
                    if v3 > 0 or v1 > 0 or v2 > 0:
                        epuck.left_motor.set_velocity(-90)
                        epuck.right_motor.set_velocity(90)
                    elif v4 > 0:
                        epuck.left_motor.set_velocity(90)
                        epuck.right_motor.set_velocity(-90)
                    else:
                        epuck.right_motor.set_velocity(180)
                        epuck.left_motor.set_velocity(180)


        except Exception as e:
            print('Something went wrong: {}'.format(e))
        finally:
            # Paramos la simulación
            simulation.stop()

            print('Simulation finish')

