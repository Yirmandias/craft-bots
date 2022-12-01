import os
# récupérer le chemin du script
from agents.agent import Agent
from api.agent_api import AgentAPI
from api.command import Command
from craftbots.entities.actor import Actor
from craftbots.entities.resource import Resource
from craftbots.entities.building import Building
from craftbots.entities.task import Task
from craftbots.log_manager import Logger
from platform_interface_pb2_grpc import *
from platform_interface_pb2 import *
import threading
import concurrent.futures
import time
import traceback
from threading import Lock
from threading import Thread

PORT = 8257
TICK = "tick"
SCORE = "SCORE"
ACTOR_ID = "actor.id"
ACTOR_NODE = "actor.node"
ACTOR_STATE = "actor.state"
ACTOR_PROGRESS= "actor.progress"
ACTOR_TARGET = "actor.target"
ACTOR_RESSOURCES = "actor.ressources"

NODE_ID = "node.id"
NODE_ACTORS= "node.actors"
NODE_TASKS = "node.tasks"
NODE_SITES = "node.sites"
NODE_BUILDINGS = "node.buildings"
NODE_RESOURCES = "node.resources"
NODE_MINES = "node.mines"
NODE_EDGES = "node.edges"
NODE_X = "node.x"
NODE_Y = "node.y"

EDGE_ID = "edge.id"
EDGE_LENGTH = "edge.length"
EDGE_NODE_A = "edge.node_a"
EDEG_NODE_B = "edge.node_b"

MINE_ID = "mine.id"
MINE_NODE = "mine.node"
MINE_COLOUR = "mine.colour"
MINE_MAX_PROGRESS= "mine.max_progress"
MINE_PROGRESS = "mine.progress"

RESOURCE_ID = "resource.id"
RESOURCE_COLOUR = "resource.colour"
RESOURCE_LOCATION = "resource.location"
RESOURCE_TICK_CREATED = "resource.tick_created"
RESOURCE_USED = "resource.used"

SITE_ID = "site.id"
SITE_BUILDING_TYPE = "site.building_type"
SITE_NODE = "site.node"
SITE_NEDDED_RESOURCES = "site.needed_resources"
SITE_DEPOSITED_RESOURCES = "site.deposited_resources"
SITE_NEEDED_EFFORT = "site.needed_effort"
SITE_MAX_PROGRESS = "site.max_progress"
SITE_PROGRESS = "site.progress"

BUILDING_ID= "building.id"
BUILDING_NODE = "building.node"
BUILDING_TYPE = "building.type"

TASK_ID = "task.id"
TASK_COMPLETED = "task.completed"
TASK_DEADLINE = "task.deadline"
TASK_SCORE = "task.score"
TASK_NODE = "task.node"
TASK_SITE = "task.site"
TASK_START_TIME = "task.start_time"
TASK_DIFFICULTY = "task.difficulty"
TASK_NEEDED_RESOURCES = "task.needed_resources"

COMMAND_ID = "command.id"
COMMAND_FUNCTION = "command.function"
COMMAND_RESULT = "command.result"
COMMAND_STATE ="command.state"

SLEEP_TIME = 0.01



def state_from_int(state: int) -> str:
    string = ""
    match state:
        case Actor.IDLE :
            string = "idle"
        case Actor.MOVING:
            string = "moving"
        case Actor.DIGGING:
            string = "digging"
        case Actor.CONSTRUCTING:
            string = "constructing"
        case Actor.RECOVERING:
            string = "recovering"
        case Actor.LOOKING:
            string = "looking"
        case Actor.SENDING:
            string = "sending"
        case Actor.RECEIVING:
            string = "receiving"
    return string

def colour_from_int(colour: int) -> str:
    string = ""
    match colour:
        case Resource.RED:
            string = "red"
        case Resource.BLUE:
            string = "blue"
        case Resource.ORANGE:
            string ="orange"
        case Resource.BLACK:
            string ="black"
        case Resource.GREEN:
            string ="green"
    return string

def building_type_from_int(building_type: int) -> str:
    string = ""
    match building_type:
        case Building.BUILDING_TASK:
            string = "building_task"
        case Building.BUILDING_SPEED:
            string = "building_speed"
        case Building.BUILDING_MINE:
            string = "building_mine"
        case Building.BUILDING_CONSTRUCTION:
            string = "building_construction"
        case Building.BUILDING_INVENTORY:
            string = "building_inventory"
        case Building.BUILDING_ACTOR_SPAWN:
            string = "building_actor_spawn"
    return string

def difficulty_from_int(difficulty: int) -> str:
    string = ""
    match difficulty:
        case Task.EASY:
            string = "easy"
        case Task.MEDIUM:
            string = "medium"
        case Task.HARD:
            string = "hard"
    return string

def function_from_int(function: int) -> str:
    string = ""
    match function:
        case Command.MOVE_TO:
            string = "move_to"
        case Command.MOVE_RAND:
            string = "move_rand"
        case Command.PICK_UP_RESOURCE:
            string ="pick_up_resource"
        case Command.DROP_RESOURCE:
            string = "drop_resource"
        case Command.DROP_ALL_RESOURCES:
            string = "drop_all_resources"
        case Command.DIG_AT:
            string = "dig_at"
        case Command.START_SITE:
            string = "start_site"
        case Command.CONSTRUCT_AT:
            string = "construct_at"
        case Command.DEPOSIT_RESOURCES:
            string = "deposit_resources"
        case Command.CANCEL_ACTION:
            string = "cancel_action"
        case Command.START_LOOKING:
            string = "start_looking"
        case Command.START_SENDING:
            string = "start_sending"
        case Command.START_RECEIVING:
            string = "start_receiving"
    return string

def function_id_from_str(function: str) -> int:
    function_id = -1
    match function:
        case "move_to":
            function_id = Command.MOVE_TO
        case "move_rand":
            function_id = Command.MOVE_RAND
        case "pick_up_resource":
            function_id = Command.PICK_UP_RESOURCE
        case "drop_resource":
            function_id = Command.DROP_RESOURCE
        case "drop_all_resources":
            function_id = Command.DROP_ALL_RESOURCES
        case "dig_at":
            function_id = Command.DIG_AT
        case "start_site":
            function_id = Command.START_SITE
        case "construct_at":
            function_id = Command.CONSTRUCT_AT
        case "deposit_resources":
            function_id = Command.DEPOSIT_RESOURCES
        case "cancel_action":
            function_id = Command.CANCEL_ACTION
        case "start_looking":
            function_id = Command.START_LOOKING
        case "start_sending":
            function_id = Command.START_SENDING
        case "start_receiving":
            function_id = Command.START_RECEIVING
    return function_id

def command_state_from_int(state: int) -> str:
    string = ""
    match state:
        case Command.PENDING:
            string = "pending"
        case Command.ACTIVE:
            string = "active"
        case Command.REJECTED:
            string = "rejected"
        case Command.PREEMPTING:
            string = "preempting"
        case Command.ABORTED:
            string = "aborted"
        case Command.SUCCEEDED:
            string = "succeeded"
        case Command.PREEMPTED:
            string = "preempted"
    return string

def actors_state_variables(world_info : dict) -> list[StateVariable]:
    state_variables = []
    # Actor state variables
    for actor_id, actor in world_info['actors'].items():
        # id of the actor
        state_variables.append(StateVariable
            (type = STATIC,
            state_function=ACTOR_ID,
            parameters=[Atom(int = actor_id)],
            value = Expression(atom=Atom(int = actor_id))))
        # id of the current node of the actor
        state_variables.append(StateVariable
            (type = DYNAMIC,
            state_function=ACTOR_NODE,
            parameters=[Atom(int = actor_id)],
            value = Expression(atom=Atom(int = actor['node']))))
        # state of the actor
        state_variables.append(StateVariable
            (type = DYNAMIC,
            state_function=ACTOR_STATE,
            parameters=[Atom(int = actor_id)],
            value = Expression(atom=Atom(symbol= state_from_int(actor['state'])))))
        # progress of the actor
        state_variables.append(StateVariable
            (type = DYNAMIC,
            state_function=ACTOR_PROGRESS,
            parameters=[Atom(int = actor_id)],
            value = Expression(atom=Atom(float = actor['progress']))))
        
        # target of the actor
        value= Expression(atom = Atom(boolean = False))
        target = actor['target']
        if isinstance(target, tuple):
            value = Expression(list = [Expression(atom = Atom(int = target[0])), Expression(atom = Atom(int = target[1]))])
        elif isinstance(target, int):
            value = Expression(list = [Expression(atom= Atom(int = target))])

        state_variables.append(StateVariable
            (type = DYNAMIC,
            state_function=ACTOR_TARGET,
            parameters=[Atom(int = actor_id)],
            value = value))
        # resources of the actor
        resources = []
        for r in actor['resources']:
            resources.append(Expression(atom = Atom(int = r)))

        state_variables.append(StateVariable
            (type = DYNAMIC,
            state_function=ACTOR_RESSOURCES,
            parameters=[Atom(int = actor_id)],
            value = Expression(list=resources)))
    return state_variables

def nodes_state_variables(world_info: dict) -> list[StateVariable]:
    state_variables = []

    # Node state variables
    for node_id, node in world_info['nodes'].items():
        # id of the node
        state_variables.append(StateVariable(
            type = STATIC,
            state_function= NODE_ID,
            parameters=[Atom(int = node_id)],
            value = Expression(atom = Atom(int = node_id))
        ))
        
        # list of actors present at the node
        actors = []
        for actor in node['actors']:
            actors.append(Expression(atom = Atom(int = actor)))
        state_variables.append(StateVariable(
            type = DYNAMIC,
            state_function= NODE_ACTORS,
            parameters=[Atom(int = node_id)],
            value = Expression(list = actors)))
        
        # list of tasks present at the node
        tasks = []
        for task in node['tasks']:
            tasks.append(Expression(atom = Atom(int = task)))
        state_variables.append(StateVariable(
            type = DYNAMIC,
            state_function= NODE_TASKS,
            parameters=[Atom(int = node_id)],
            value = Expression(list = tasks)))
        
        # list of sites present at the node
        sites = []
        for site in node['sites']:
            sites.append(Expression(atom = Atom(int = site)))
        state_variables.append(StateVariable(
            type = DYNAMIC,
            state_function= NODE_SITES,
            parameters=[Atom(int = node_id)],
            value = Expression(list = sites)))

        # list of buildings present at the node
        buildings = []
        for building in node['buildings']:
            buildings.append(Expression(atom= Atom(int = building)))
        state_variables.append(StateVariable(
            type = DYNAMIC,
            state_function= NODE_BUILDINGS,
            parameters=[Atom(int = node_id)],
            value = Expression(list = buildings)))

        # list of resources present at the node
        resources = []
        for resource in node['resources']:
            resources.append(Expression(atom = Atom(int = resource)))
        state_variables.append(StateVariable(
            type = DYNAMIC,
            state_function= NODE_RESOURCES,
            parameters=[Atom(int = node_id)],
            value = Expression(list = resources)))

        # list of mines present at the node
        mines = []
        for mine in node['mines']:
            mines.append(Expression(atom = Atom(int = mine)))
        state_variables.append(StateVariable(
            type = STATIC,
            state_function= NODE_MINES,
            parameters=[Atom(int = node_id)],
            value = Expression(list = mines)))
        
        # list of edges present at the node
        
        edges = []
        for edge in node['edges']:
            edges.append(Expression(atom = Atom(int = edge)))
        
        state_variables.append(StateVariable(
            type = STATIC,
            state_function= NODE_EDGES,
            parameters=[Atom(int = node_id)],
            value = Expression(list = edges)))
        
        # x position of the node
        state_variables.append(StateVariable(
            type = STATIC,
            state_function= NODE_X,
            parameters=[Atom(int = node_id)],
            value = Expression(atom = Atom(float = node['x']))))

        # y position of the node
        state_variables.append(StateVariable(
            type = STATIC,
            state_function= NODE_Y,
            parameters=[Atom(int = node_id)],
            value = Expression(atom = Atom(float = node['y']))))
    return state_variables

def edges_state_variables(world_info: dict) -> list[StateVariable]:
    state_variables = []
    #Edges state variables
    for edge_id, edge in world_info['edges'].items():
        # id of the edge
        state_variables.append(StateVariable(
            type=STATIC,
            state_function= EDGE_ID,
            parameters=[Atom(int = edge_id)],
            value = Expression(atom = Atom(int = edge_id))
        ))

        # length of the edge
        state_variables.append(StateVariable(
            type=STATIC,
            state_function= EDGE_LENGTH,
            parameters=[Atom(int = edge_id)],
            value = Expression(atom = Atom(int = edge['length']))
        ))

        # node_a of the edge
        state_variables.append(StateVariable(
            type=STATIC,
            state_function= EDGE_NODE_A,
            parameters=[Atom(int = edge_id)],
            value = Expression(atom = Atom(int = edge['node_a']))
        ))

        # node_b of the edge
        state_variables.append(StateVariable(
            type=STATIC,
            state_function= EDEG_NODE_B,
            parameters=[Atom(int = edge_id)],
            value = Expression(atom = Atom(int = edge['node_b']))
        ))
    return state_variables

def mines_state_variables(world_info: dict) -> list[StateVariable]:
    state_variables = []
    for mine_id, mine in world_info["mines"].items():
        # id of the mine
        state_variables.append(StateVariable(
            type = STATIC,
            state_function=MINE_ID,
            parameters=[Atom(int = mine_id)],
            value = Expression(atom = Atom(int = mine_id))
        ))

        # node of the mine
        state_variables.append(StateVariable(
            type=STATIC,
            state_function=MINE_NODE,
            parameters=[Atom(int = mine_id)],
            value = Expression(atom= Atom(int = mine['node']))
        ))

        # colour of the mine
        state_variables.append(StateVariable(
            type=STATIC,
            state_function=MINE_COLOUR,
            parameters=[Atom(int = mine_id)],
            value = Expression(atom = Atom(symbol = colour_from_int(mine['colour'])))
        ))

        # max_progress of the mine
        state_variables.append(StateVariable(
            type=STATIC,
            state_function=MINE_MAX_PROGRESS,
            parameters=[Atom(int = mine_id)],
            value = Expression(atom = Atom(int = mine['max_progress']))
        ))

        # progress of the mine
        state_variables.append(StateVariable(
            type=DYNAMIC,
            state_function=MINE_PROGRESS,
            parameters=[Atom(int = mine_id)],
            value = Expression(atom= Atom(int = mine['progress']))
        ))
    return state_variables

def resources_state_variables(world_info: dict) -> list[StateVariable]:
    state_variables = []
    for resource_id, resource in world_info['resources'].items():
        # id of the resource
        state_variables.append(StateVariable(
            type = STATIC,
            state_function=RESOURCE_ID,
            parameters=[Atom(int = resource_id)],
            value = Expression(atom = Atom(int = resource_id))
        ))

        # colour of the resource
        state_variables.append(StateVariable(
            type = STATIC,
            state_function=RESOURCE_COLOUR,
            parameters=[Atom(int = resource_id)],
            value = Expression(atom = Atom(symbol = colour_from_int(resource['colour'])))
        ))

        # location of the resource
        state_variables.append(StateVariable(
            type = STATIC,
            state_function=RESOURCE_LOCATION,
            parameters=[Atom(int = resource_id)],
            value = Expression(atom = Atom(int = resource['location']))
        ))

        # tick at which of the resource was create
        state_variables.append(StateVariable(
            type = STATIC,
            state_function=RESOURCE_TICK_CREATED,
            parameters=[Atom(int = resource_id)],
            value = Expression(atom = Atom(int = resource['tick_created']))
        ))

        # tick at which of the resource was create
        state_variables.append(StateVariable(
            type = STATIC,
            state_function=RESOURCE_USED,
            parameters=[Atom(int = resource_id)],
            value = Expression(atom = Atom(boolean = resource['used']))
        ))
        pass
    return state_variables

def sites_state_variables(world_info: dict) -> list[StateVariable]:
    state_variables = []
    for site_id, site in world_info['sites'].items():
        state_variables.append(StateVariable(
            type = STATIC,
            state_function=SITE_ID,
            parameters=[Atom(int = site_id)],
            value = Expression(atom = Atom(int = site_id))
        ))

        state_variables.append(StateVariable(
            type = STATIC,
            state_function=SITE_BUILDING_TYPE,
            parameters=[Atom(int = site_id)],
            value = Expression(atom = Atom(symbol = building_type_from_int(site['building_type'])))
        ))

        state_variables.append(StateVariable(
            type = STATIC,
            state_function=SITE_NODE,
            parameters=[Atom(int = site_id)],
            value = Expression(atom = Atom(int = site['node']))
        ))

        needed_resources = []
        for r in site['needed_resources']:
            needed_resources.append(Expression(atom = Atom(int = r)))

        state_variables.append(StateVariable(
            type = STATIC,
            state_function=SITE_NEDDED_RESOURCES,
            parameters=[Atom(int = site_id)],
            value = Expression(list = needed_resources))
        )

        deposited_resources = []
        for r in site['deposited_resources']:
            needed_resources.append(Expression(atom = Atom(int = r)))

        state_variables.append(StateVariable(
            type = DYNAMIC,
            state_function=SITE_DEPOSITED_RESOURCES,
            parameters=[Atom(int = site_id)],
            value = Expression(list = deposited_resources))
        )

        state_variables.append(StateVariable(
            type = STATIC,
            state_function=SITE_NEEDED_EFFORT,
            parameters=[Atom(int = site_id)],
            value = Expression(atom = Atom(int = site['needed_effort'])))
        )

        state_variables.append(StateVariable(
            type = STATIC,
            state_function=SITE_MAX_PROGRESS,
            parameters=[Atom(int = site_id)],
            value = Expression(atom = Atom(int = site['max_progress'])))
        )

        state_variables.append(StateVariable(
            type = DYNAMIC,
            state_function=SITE_PROGRESS,
            parameters=[Atom(int = site_id)],
            value = Expression(atom = Atom(int = site['progress'])))
        )

    return state_variables

def buildings_state_variables(world_info: dict) -> list[StateVariable]:
    state_variables =[]
    for building_id, building in world_info['buildings'].items():
        state_variables.append(StateVariable(
            type = STATIC,
            state_function=BUILDING_ID,
            parameters=[Atom(int = building_id)],
            value = Expression(atom = Atom(int = building_id))
        ))

        state_variables.append(StateVariable(
            type = STATIC,
            state_function=BUILDING_NODE,
            parameters=[Atom(int = building_id)],
            value = Expression(atom = Atom(int = building['node']))
        ))

        state_variables.append(StateVariable(
            type = STATIC,
            state_function=BUILDING_NODE,
            parameters=[Atom(int = building_id)],
            value = Expression(atom = Atom(symbol = building_type_from_int(building['building_type'])))
        ))
    return state_variables

def tasks_state_variables(world_info: dict) -> list[StateVariable]:
    state_variables =[]
    for task_id, task in world_info['tasks'].items():
        state_variables.append(StateVariable(
            type = STATIC,
            state_function=TASK_ID,
            parameters = [Atom(int = task_id)],
            value = Expression(atom = Atom(int = task_id))
        ))

        state_variables.append(StateVariable(
            type = DYNAMIC,
            state_function=TASK_COMPLETED,
            parameters = [Atom(int = task_id)],
            value = Expression(atom = Atom(boolean= task['completed']))
        ))

        state_variables.append(StateVariable(
            type = STATIC,
            state_function=TASK_DEADLINE,
            parameters = [Atom(int = task_id)],
            value = Expression(atom = Atom(int = task['deadline']))
        ))

        state_variables.append(StateVariable(
            type = STATIC,
            state_function=TASK_SCORE,
            parameters = [Atom(int = task_id)],
            value = Expression(atom = Atom(int= task['score']))
        ))

        state_variables.append(StateVariable(
            type = STATIC,
            state_function=TASK_NODE,
            parameters = [Atom(int = task_id)],
            value = Expression(atom = Atom(int= task['node']))
        ))

        site = Atom(boolean=False)
        if task['site'] != None:
            site = Atom(int = task['site'])
        state_variables.append(StateVariable(
            type = DYNAMIC,
            state_function=TASK_SITE,
            parameters = [Atom(int = task_id)],
            value = Expression(atom = site)
        ))

        state_variables.append(StateVariable(
            type = STATIC,
            state_function=TASK_START_TIME,
            parameters = [Atom(int = task_id)],
            value = Expression(atom = Atom(int= task['start_time']))
        ))

        state_variables.append(StateVariable(
            type = STATIC,
            state_function=TASK_DIFFICULTY,
            parameters = [Atom(int = task_id)],
            value = Expression(atom = Atom(symbol= difficulty_from_int(task['difficulty'])))
        ))

        needed_resources = []
        for r in task['needed_resources']:
            needed_resources.append(Expression(atom = Atom(int = r)))

        state_variables.append(StateVariable(
            type = STATIC,
            state_function=TASK_NEEDED_RESOURCES,
            parameters = [Atom(int = task_id)],
            value = Expression(list = needed_resources))
        )
    return state_variables

def commands_state_variables(world_info: dict) -> list[StateVariable]:
    state_variables=[]
    for command_id, command in world_info['commands'].items():
        state_variables.append(StateVariable(
            type=STATIC,
            state_function=COMMAND_ID,
            parameters=[Atom(int = command_id)],
            value = Expression(atom = Atom(int = command_id))
        ))

        state_variables.append(StateVariable(
            type=STATIC,
            state_function=COMMAND_FUNCTION,
            parameters=[Atom(int = command_id)],
            value = Expression(atom = Atom(symbol= function_from_int(command['function_id'])))
        ))

        state_variables.append(StateVariable(
            type=DYNAMIC,
            state_function=COMMAND_RESULT,
            parameters=[Atom(int = command_id)],
            value = Expression(atom = Atom(boolean= command['result']))
        ))

        state_variables.append(StateVariable(
            type=DYNAMIC,
            state_function=COMMAND_STATE,
            parameters=[Atom(int = command_id)],
            value = Expression(atom = Atom(symbol= command_state_from_int(command['state'])))
        ))
    return state_variables


class CurrentCommandCollection:
    def __init__(self):
        self.list = []
        self.list: list[int]
        self.lock = Lock()
        self.platform_id_to_ompas_id = dict()
    
    def add(self, ompas_id: int, craft_bots_id: int):
        self.lock.acquire()
        self.list.append(craft_bots_id)
        self.platform_id_to_ompas_id[craft_bots_id] = ompas_id
        self.lock.release()

    def get_ompas_id(self, craft_bots_id: int) -> int:
        self.lock.acquire()
        value = self.platform_id_to_ompas_id[craft_bots_id]
        self.lock.release()
        return value
    
    def get_currents(self) -> list[int]:
        self.lock.acquire()
        value = self.list.copy()
        self.lock.release()
        return value

    def remove(self, craft_bots_id: int):
        self.lock.acquire()
        self.list.remove(craft_bots_id)
        del self.platform_id_to_ompas_id[craft_bots_id]
        self.lock.release()

class CommandResponseCollection:
    def __init__(self):
        self.list = []
        self.list: list[CommandResponse]
        self.lock = Lock()
    
    def push(self, response: CommandResponse):
        self.lock.acquire()
        self.list.append(response)
        self.lock.release()

    def pop(self) -> CommandResponse | None:
        self.lock.acquire()
        if len(self.list) > 0:
            value = self.list.pop()
        else:
            value = None
        self.lock.release()
        return value

def handle_incoming_commands(api: AgentAPI, request_iterator, command_responses: CommandResponseCollection, current_commands: CurrentCommandCollection):
    print("start new commands")
    try:
        while True:
            for command_request in request_iterator:
                # treating new commands
                command_request: CommandRequest
                if command_request.execution != None:
                    #print(f'new execution request received: {command_request.execution}')
                    execution: CommandExecutionRequest
                    execution = command_request.execution
                    command_id = execution.command_id
                    command = execution.arguments[0]
                    actor = execution.arguments[1].atom.symbol
                    actor_id = int(actor.removeprefix("actor_"))
                    other = execution.arguments[2:]
                    #print(f'params = {params}')
                    function_id = function_id_from_str(command.atom.symbol)
                    if function_id == -1:
                        # the command name is no match with the available commands
                        command_responses.push(CommandResponse(rejected=CommandRejected(command_id)))
                    else:
                        # if the command corresponds to an available command, then we can analyse the arguments and maybe execute it
                        r = -1
                        match function_id:
                            case Command.MOVE_TO:
                                node_id = other[0].atom.int
                                r = api.move_to(actor_id, node_id)
                            case Command.MOVE_RAND:
                                #print(f'actor_id = {actor_id}')
                                r = api.move_rand(actor_id)
                            case Command.PICK_UP_RESOURCE:
                                actor_id = other[0].atom.int
                                resource_id = other[1].atom.int
                                r = api.pick_up_resource(actor_id, resource_id)
                            case Command.DROP_RESOURCE:
                                actor_id = other[0].atom.int
                                resource_id = other[1].atom.int
                                r = api.drop_resource(actor_id, resource_id)
                            case Command.DROP_ALL_RESOURCES:
                                actor_id = other[0].atom.int
                                r = api.drop_all_resources(actor_id)
                            case Command.DIG_AT:
                                actor_id = other[0].atom.int
                                mine_id = other[1].atom.int
                                r = api.dig_at(actor_id, mine_id)
                            case Command.START_SITE:
                                actor_id = other[0].atom.int
                                task_id = other[1].atom.int
                                r = api.start_site(actor_id, task_id)
                            case Command.CONSTRUCT_AT:
                                actor_id = other[0].atom.int
                                site_id = other[1].atom.int
                                r = api.construct_at(actor_id, site_id)
                            case Command.DEPOSIT_RESOURCES:
                                actor_id = other[0].atom.int
                                site_id = other[1].atom.int
                                resource_id = other[2].atom.int
                                r = api.deposit_resources(actor_id, site_id)
                            case Command.CANCEL_ACTION:
                                actor_id = other[0].atom.int
                                r = api.cancel_action(actor_id)
                            case Command.START_LOOKING:
                                actor_id = other[0].atom.int
                                r = api.start_looking(actor_id)
                            case Command.START_SENDING:
                                actor_id = other[0].atom.int
                                message = other[1].atom.symbol
                                r = api.start_sending(actor_id, message)
                            case Command.START_RECEIVING:
                                actor_id = other[0].atom.int
                                r = api.start_receiving(actor_id)
                        if r == -1:
                            # command has not been accepted by API
                            print('rejected')
                            command_responses.push(CommandResponse(rejected=CommandRejected(command_id= command_id)))
                        else:
                            command_responses.push(CommandResponse(accepted=CommandAccepted(command_id = command_id)))
                            current_commands.add(command_id, r)
                # if a cancel request has been sent                
                elif command_request.cancel != None:
                    pass
    except Exception:
        print(traceback.format_exc())
    
    print("end new commands")

def handle_current_commands(api: AgentAPI, command_responses: CommandResponseCollection, current_commands: CurrentCommandCollection):
    print("start current commands")
    last_tick = -1
    try:
        while True:
            world_info = api.get_world_info()
            world_info: dict
            new_tick = world_info['tick']
            if last_tick < new_tick:
                last_tick = new_tick
                commands = world_info['commands']
                current = current_commands.get_currents()
                # print(current)
                for command_id in current:
                    command = commands[command_id]                      
                    print(command)
                    command: dict
                    ompas_id = current_commands.get_ompas_id(command_id)
                    match command["state"]:
                        case Command.PENDING:
                            pass
                        case Command.ACTIVE:
                            command_responses.push(CommandResponse(progress=CommandProgress(command_id = ompas_id, progress = 0.0)))
                        case Command.REJECTED:
                            current_commands.remove(command_id)
                            command_responses.push( CommandResponse(progress=CommandRejected(command_id = ompas_id)))
                        case Command.PREEMPTING:
                            pass
                        case Command.ABORTED:
                            current_commands.remove(command_id)
                            command_responses.push(CommandResponse(result = CommandResult(command_id = ompas_id, result = False)))
                        case Command.SUCCEEDED:
                            current_commands.remove(command_id)
                            command_responses.push(CommandResponse(result = CommandResult(command_id = ompas_id, result = True)))
                        case Command.PREEMPTED:
                            current_commands.remove(command_id)
                            command_responses.push(CommandResponse(cancelled=CommandCancelled(command_id = ompas_id, result = True)))
    except Exception:
        print(traceback.format_exc())
    
    print("end current commands")


TYPE_AGENT = "agent"


class CraftBotsServicer(platform_interfaceServicer):
    def __init__(self, api: AgentAPI):
        self.api = api

    def GetUpdates(self, request, context):
        print('start updates')

        api = self.api
        last_tick=0

        list_actors = []
        list_nodes= []
        list_edges = []
        try:
            while True:
                world_info = api.get_world_info()
                if world_info != None:
                    new_tick = world_info['tick']
                    if last_tick < new_tick:
                        last_tick = new_tick

                        current_actors = world_info['actors'].keys()
                        for actor in current_actors:
                            if not list_actors.__contains__(actor):
                                yield PlatformUpdate(event = Event(instance=Instance(type=TYPE_AGENT, object = 'actor_'+ str(actor))))

                        list_actors = current_actors

                        state = StateUpdate()
                        # Current simulation tick
                        state.state_variables.append(StateVariable(
                            type=DYNAMIC,
                            state_function=TICK,
                            parameters=[],
                            value=Expression(atom = Atom(int = world_info['tick']))
                        ))

                        # Current total score
                        state.state_variables.append(StateVariable(
                            type=DYNAMIC,
                            state_function=SCORE,
                            parameters=[],
                            value=Expression(atom = Atom(int = world_info['score']))
                        ))

                        state.state_variables.extend(actors_state_variables(world_info))
                        state.state_variables.extend(nodes_state_variables(world_info))
                        state.state_variables.extend(edges_state_variables(world_info))
                        state.state_variables.extend(mines_state_variables(world_info))
                        state.state_variables.extend(resources_state_variables(world_info))
                        state.state_variables.extend(sites_state_variables(world_info))
                        state.state_variables.extend(buildings_state_variables(world_info))
                        state.state_variables.extend(tasks_state_variables(world_info))
                        state.state_variables.extend(commands_state_variables(world_info))
                        # Return the whole state
                        yield PlatformUpdate(state = state)
                    else:
                        pass
        except Exception:
            print(traceback.format_exc())
        print('end updates')

    def SendCommands(self, request_iterator, context):
        print('start send commands')

        current_commands= CurrentCommandCollection()
        command_responses = CommandResponseCollection()

        thread_incoming = Thread(target=handle_incoming_commands, args=(self.api, request_iterator, command_responses, current_commands))
        thread_current = Thread(target=handle_current_commands, args=(self.api, command_responses, current_commands))
        
        thread_incoming.start()
        thread_current.start()


        while True:
            while True:
                response = command_responses.pop()
                if response != None:
                    yield response
                else:
                    break
            
            time.sleep(SLEEP_TIME)
        
        print('end commands')

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
            time.sleep(1)
