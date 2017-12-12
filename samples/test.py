

from vrep import Client
import vrep_binds as binds
import json





with Client('127.0.0.1:19997') as client:
    simulation = client.simulation
    simulation.resume()


