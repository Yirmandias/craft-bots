from agents.ompas import OMPASAgent
from platform_interface_pb2_grpc import *
from platform_interface_pb2 import *
from craftbots.simulation import Simulation
import argparse
import time


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-f', help="configuration file", type=str, default='craftbots/config/simple_configuration.yaml')
args = arg_parser.parse_args()

# Simulation
sim = Simulation(configuration_file=args.f)

agent = OMPASAgent()
sim.agents.append(agent)

sim.reset_simulation()
sim.start_simulation()

time.sleep(1)
channel = grpc.insecure_channel('localhost:8257')
stub = platform_interfaceStub(channel)

updates = stub.GetUpdates(InitGetUpdate())
print('waiting for updates')

for update in updates:
    print(update)
    print('\n')
