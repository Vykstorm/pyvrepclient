

'''
Ejemplo que demuestra como obtener mediciones de los sensores de proximidad de una simulación V-rep
Se usar el sensor con el nombre "ePuck_proxSensor1". Asegurate que has añadido un robot ePuck a la escena,
o un sensor de proximidad con ese nombre.
'''

from vrep import Client
from time import sleep

if __name__ == '__main__':
    with Client(address = '127.0.0.1:19997') as client:
        scene = client.scene
        simulation = client.simulation


        # Comenzamos la simulación
        simulation.resume()

        try:
            # Para obtener una referencia al sensor (cuyo nombre en el simulador es "ePuck_proxSensor1")

            proximity_sensor = scene.proximity_sensors.ePuck_proxSensor1
            #proximity_sensor = scene.proximity_sensors['ePuck_proxSensor1']
            #proximity_sensor =  scene.proximity_sensors.get('ePuck_proxSensor1')


            # Mostramos 30 mediciones del sensor, 1 por segundo.
            for i in range(0, 30):
                value = proximity_sensor.get_value()
                print('Sensor value: {}'.format(value))
                sleep(1)
        finally:
            # Paramos la simulación
            simulation.stop()