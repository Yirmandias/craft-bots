import os
# récupérer le chemin du script
from agents.agent import Agent
from api.agent_api import AgentAPI
from craftbots.entities.actor import Actor
from craftbots.log_manager import Logger
from platform_interface_pb2_grpc import *
from platform_interface_pb2 import *
import threading
import concurrent.futures
import time

PORT = 8257
ACTOR_ID = "actor.id"
ACTOR_NODE = "actor.node"
ACTOR_STATE = "actor.state"
ACTOR_PROGRESS= "actor.progress"
ACTOR_TARGET = "actor.target"
ACTOR_RESSOURCES = "actor.ressources"

class CraftBotsServicer(platform_interfaceServicer):
    def __init__(self, api: AgentAPI):
        self.api = api

    def GetUpdates(self, request, context):
        api = self.api
        while True:
            world_info = api.get_world_info()
            if world_info != None:
                state = StateUpdate()
                for actor_id, actor in world_info['actors'].items():
                    state.state_variables.append(StateVariable
                    (type = STATIC,
                    state_function=ACTOR_ID,
                    parameters=[Atom(int = actor_id)],
                    value = Expression(atom=Atom(int = actor_id)))) 
                    update = PlatformUpdate(state = state)
                    #print(actor)
                yield update
                time.sleep(1)
            else:
                pass
        
        #Updating actors info:
        
        #for actor in self.world_info["actors"]:
        #    state.state_variables.append(StateVariable(type = StateVariableType(), state_function=ACTOR_ID, parameters=actor["id"], value = actor["id"]))
        #    pass
        # update = PlatformUpdate(state)
        #update = PlatformUpdate()    
        #yield update
        #context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        #context.set_details('Method not implemented!')
        #raise NotImplementedError('Method not implemented!')

    def SendCommands(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

"""
    def GetUpdates(self, request: InitGetUpdate, context):
        
        # See how to await updates
        self.world_info : dict
        while True :
            state = StateUpdate()
            
            #Updating actors info:
            
            for actor in self.world_info["actors"]:
                state.state_variables.append(StateVariable(type = StateVariableType(), state_function=ACTOR_ID, parameters=actor["id"], value = actor["id"]))
                pass
            yield state
"""        
        
        #context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        #context.set_details('Method not implemented!')
        #raise NotImplementedError('Method not implemented!')

class OMPASAgent(Agent):
    def __init__(self):
        super().__init__()
        pass           

    def get_next_commands(self):
        api= self.api
        self.platform_interface_server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
        add_platform_interfaceServicer_to_server(CraftBotsServicer(api), self.platform_interface_server)
        port = self.platform_interface_server.add_insecure_port(f'localhost:{PORT}')
        print(f"port: {port}")
        self.platform_interface_server.start()
        while True:
            pass
            #print(f'world_info = {self.world_info}')
