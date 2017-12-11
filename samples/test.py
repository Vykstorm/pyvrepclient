


from vrep import Client


with Client('127.0.0.1:19997') as client:
    scene = client.scene

    for myrobots in scene.robots.epuck:
        print(myrobots)