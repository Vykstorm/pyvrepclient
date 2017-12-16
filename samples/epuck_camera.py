


'''
Este ejemplo demuestra como obtener la imágen del sensor de visión del robot ePuck.
Antes de ejecutar este código, carga la escena llamada "epuck_example.ttt" que está en el directorio
scenes/ en el simulador V-rep.
'''

from vrep import Client
from PIL import Image

if __name__ == '__main__':
    with Client(address = '127.0.0.1') as client:
        simulation = client.simulation
        scene = simulation.scene

        epuck = scene.robots.epuck


        # Iniciamos la simulación
        simulation.resume()
        print('Simulation started')

        try:
            # Obtenemos la imágen (es un objeto PIL)
            image = epuck.camera.get_image(mode = 'RGB', size = (256, 256))

            # Mostramos la imágen
            image.transpose(Image.FLIP_TOP_BOTTOM).show()

        except Exception as e:
            print('Something went wrong: {}'.format(e))
        finally:
            simulation.stop()
            print('Simulation stopped')