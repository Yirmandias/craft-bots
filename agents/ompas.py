from agents.agent import Agent
from api import agent_api
from craftbots.entities.actor import Actor
from craftbots.log_manager import Logger
from platform_interface_pb2_grpc import *
from platform_interface_pb2 import *
import threading
import concurrent.futures

PORT = 8259
ACTOR_ID = "actor.id"
ACTOR_NODE = "actor.node"
ACTOR_STATE = "actor.state"
ACTOR_PROGRESS= "actor.progress"
ACTOR_TARGET = "actor.target"
ACTOR_RESSOURCES = "actor.ressources"


class CraftBotsServicer(platform_interfaceServicer):
    def __init__(self, world_info: dict, api: agent_api.AgentAPI):
        self.world_info = world_info
        self.api = api

    def GetUpdates(self, request: InitGetUpdate, context):
        # See how to await updates
        self.world_info : dict
        while True :
            state = StateUpdate()
            """
            Updating actors info:
            """
            for actor in self.world_info["actors"]:
                state.state_variables.append(StateVariable(type = StateVariableType(), state_function=ACTOR_ID, parameters=actor["id"], value = actor["id"]))
                pass
            yield state
        """Missing associated documentation comment in .proto file."""
        #context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        #context.set_details('Method not implemented!')
        #raise NotImplementedError('Method not implemented!')

    def SendCommands(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        
        
        #context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        #context.set_details('Method not implemented!')
        #raise NotImplementedError('Method not implemented!')

class OMPASAgent(Agent):
    def __init__(self):
        super().__init__()
        self.platform_interface_server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
        add_platform_interfaceServicer_to_server(CraftBotsServicer(self.world_info,self.api), self.platform_interface_server)
        self.platform_interface_server.add_insecure_port('[::]:8259')
        self.platform_interface_server.start()
        pass           

    def get_next_commands(self):
        pass
