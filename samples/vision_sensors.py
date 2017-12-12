



'''
Ejemplo que demuestra como obtener las imágenes de los sensores de visión de una simulación V-rep
Para ejemplo, crear el robot e-Puck en el simulador.
'''

from vrep import Client
from PIL import Image

if __name__ == '__main__':
    with Client(address = '127.0.0.1:19997') as client:
        simulation = client.simulation
        scene = simulation.scene

        # Comenzamos la simulación
        simulation.resume()

        try:
            # Para obtener la cámara del e-Puck (cuyo nombre en el simulador es "ePuck_camera")

            vision_sensor = scene.vision_sensors.ePuck_camera
            # vision_sensor = scene.vision_sensors['ePuck_camera']
            # vision_sensor = scene.vision_sensors.get('ePuck_camera')

            # Mostramos la imágen de la cámara del e-Puck
            image = vision_sensor.get_image(size = (256, 256))
            image.transpose(Image.FLIP_TOP_BOTTOM).show()

        except Exception as e:
            print('Something went wrong: {}'.format(e))

        finally:
            # Paramos la simulación
            simulation.stop()