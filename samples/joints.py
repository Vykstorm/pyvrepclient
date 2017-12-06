

'''
Ejemplo que demuestra como enviar comandos a los motores.
Para este ejemplo, se usa el robot ePuck, y sus motores, cuyos nombres son
"ePuck_leftJoint", "ePuck_rightJoint"
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

            # Para obtener una referencia al motor izquierdo y derecho ("ePuck_leftJoint" y "ePuck_rightJoint")

            left_motor = scene.joints.ePuck_leftJoint
            #left_motor = scene.joints['ePuck_leftJoint']
            #left_motor =  scene.joints.get('ePuck_leftJoint')

            right_motor = scene.joints.ePuck_rightJoint


            # Modificamos la velocidad de los motores
            left_motor.set_velocity(6.28 / 2)
            right_motor.set_velocity(6.28 / 2)

            # Dejamos la simulación durante 10 segundos
            sleep(20)

        finally:
            # Paramos la simulación
            simulation.stop()