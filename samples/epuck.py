

'''
Ejemplo que demuestra como utilizar la clase EPuck que se provee para trabajar con robots ePuck en V-rep
'''

from time import sleep

from PIL import Image

from robots.epuck import EPuck
from vrep import Client

if __name__ == '__main__':
    with Client('127.0.0.1:19997') as client:
        scene = client.scene

        epuck = scene.robots.epuck

        # Para obtener la cámara y el sensor de luz
        camera = epuck.camera
        light_sensor = epuck.light_sensor

        # Para obtener los motores izquierdo y derecho
        left_motor = epuck.left_motor
        right_motor = epuck.right_motor

        # Sensores de proximidad
        proximity_sensors = epuck.proximity_sensors


        # Iniciamos la simulación
        simulation = client.simulation
        simulation.resume()

        try:
            print('Starting simulation')

            # Paramos los motores
            left_motor.set_velocity(0)
            right_motor.set_velocity(0)

            # Mostramos mediciones de los sensores (La primera medición suele ser lenta,
            # porque se lleva acabo de forma sincrona con el servidor remoto V-REP)
            for i in range(0, len(proximity_sensors)):
                sensor = proximity_sensors[i]
                print('Sensor {} value: {}'.format(i+1, sensor.get_value()))

            sleep(2)

            # Movemos los motores

            print('Moving engines')

            left_motor.set_velocity(10)
            right_motor.set_velocity(5)
            sleep(3)

            right_motor.set_velocity(10)
            sleep(4)

            left_motor.set_velocity(5)
            sleep(3)

            left_motor.set_velocity(0)
            right_motor.set_velocity(0)

            print('Engines stopped')

            # Finalmente obtenemos y mostramos la imágen actual de la cámara

            print('Getting image from camera...')

            image = camera.get_image(mode = 'RGB', size = (256, 256))
            image.transpose(Image.FLIP_TOP_BOTTOM).show()

        except Exception as e:
            print('An error occurred: {}'.format(e))
        finally:
            # Paramos la simulación
            simulation.stop()

            print('Simulation finish')
