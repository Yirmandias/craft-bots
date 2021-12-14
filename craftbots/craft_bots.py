from craftbots.world import World
from api.agent_api import AgentAPI
from agents.blank_agent import BlankAgent
import craftbots.view as view
from gui.main_window import CraftBotsGUI
import threading
import random as r
import math
import time

from entities.building import Building

simulation_stop = None
sim_stopped = False
sim_paused = False
gui_updating = False
root = None
world = World()
start_time = time.time()


def default_scenario(modifiers, world_gen_modifiers):
    global world
    for _ in range(modifiers["NUM_OF_ACTORS"]):
        actor = world.add_actor(world.nodes[r.randint(0, world.nodes.__len__() - 1)])
        for _ in range(world_gen_modifiers["ACTOR_NUM_OF_RED_RESOURCES"]):
            world.add_resource(actor, 0)
        for _ in range(world_gen_modifiers["ACTOR_NUM_OF_BLUE_RESOURCES"]):
            world.add_resource(actor, 1)
        for _ in range(world_gen_modifiers["ACTOR_NUM_OF_ORANGE_RESOURCES"]):
            world.add_resource(actor, 2)
        for _ in range(world_gen_modifiers["ACTOR_NUM_OF_BLACK_RESOURCES"]):
            world.add_resource(actor, 3)
        for _ in range(world_gen_modifiers["ACTOR_NUM_OF_GREEN_RESOURCES"]):
            world.add_resource(actor, 4)

    for _ in range(world_gen_modifiers["NUM_OF_RED_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 0)
    for _ in range(world_gen_modifiers["NUM_OF_RED_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 0)

    for _ in range(world_gen_modifiers["NUM_OF_BLUE_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 1)
    for _ in range(world_gen_modifiers["NUM_OF_BLUE_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 1)

    for _ in range(world_gen_modifiers["NUM_OF_ORANGE_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 2)
    for _ in range(world_gen_modifiers["NUM_OF_ORANGE_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 2)

    for _ in range(world_gen_modifiers["NUM_OF_BLACK_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 3)
    for _ in range(world_gen_modifiers["NUM_OF_BLACK_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 3)

    for _ in range(world_gen_modifiers["NUM_OF_GREEN_RESOURCES"]):
        world.add_resource(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 4)
    for _ in range(world_gen_modifiers["NUM_OF_GREEN_MINES"]):
        world.add_mine(world.nodes[r.randint(0, world.nodes.__len__() - 1)], 4)

    for key in world_gen_modifiers:

        # initial buildings
        if key.startswith("NUM_BUILDING"):
            for _ in range(world_gen_modifiers[key]):
                building_type_name = key[4:] # removes "NUM_"
                building_type = Building.__dict__[building_type_name]
                world.add_building(world.nodes[r.randint(0, world.nodes.__len__() - 1)], building_type)

        # initial sites
        if key.startswith("NUM_SITE"):
            for _ in range(world_gen_modifiers[key]):
                building_type_name = "BUILDING" + key[9:] # removes "NUM_SITE_"
                building_type = Building.__dict__[building_type_name]
                world.add_site(world.nodes[r.randint(0, world.nodes.__len__() - 1)], building_type)


def start_simulation(agent_class=BlankAgent, use_gui=True, scenario=default_scenario,modifier_file=None,world_modifier_file=None,rule_file=None):
    """
        The command used to start the CraftBots simulation. The simulation will run on a separate thread and the current
        thread will wait for the simulation to finish and return the score achieved.

        :param agent_class: (optional) the class constructor for the Agent to be used. Default: BlankAgent (from agents folder)
        :param use_gui: (optional) if the GUI should be displayed. Default: True
        :param scenario: (optional) the scenario that should be created in the world, regarding actors, mine, resources, sites, and buildings. Documentation to create a scenario still WIP. Default: default_scenario (using modifiers and world_gen_modifiers)
        :param modifier_file: (optional) path to the text file that is used to initialise the modifiers for the simulation. Default: None (the default parameters are used)
        :param world_modifier_file: (optional) path to the text file that is used to initialise the world parameters for the simulation. Default: None (the default parameters are used)
        :param rule_file: (optional) path to the text file that is used to set the rules for the simulation.  Default: None (the default parameters are used)
        :return:
        """
    sim_thread = threading.Thread(target=prep_simulation, args=(agent_class, use_gui, scenario, modifier_file, world_modifier_file, rule_file), daemon=True)
    sim_thread.start()
    while not sim_stopped:
        time.sleep(1)
    return world.total_score

def pause_simulation():
    global sim_paused
    sim_paused = not sim_paused

def prep_simulation(agent_class, use_gui, scenario, modifier_file, world_modifier_file, rule_file):
    global world
    world_gen_modifiers = get_world_gen_modifiers(world_modifier_file)
    modifiers = get_modifiers(modifier_file)
    rules = get_rules(rule_file)
    world = World(modifiers, world_gen_modifiers, rules)
    scenario(modifiers, world_gen_modifiers)

    if rules["LIMITED_COMMUNICATIONS"]:
        agents = []
        for actor in world.get_all_actors():
            new_agent = agent_class()
            new_agent.api = AgentAPI(world, [actor.id])
            new_agent.world_info = new_agent.api.get_world_info()
            agents.append(new_agent)
    else:
        agents = [agent_class()]
        actor_ids = []
        for actor in world.get_all_actors():
            actor_ids.append(actor.id)
        agents[0].api = AgentAPI(world, actor_ids)
        agents[0].world_info = agents[0].api.get_world_info()

    if rules["RT_OR_LOCK_STEP"] == 0:
        global simulation_stop
        simulation_stop = call_repeatedly(1 / rules["TICK_HZ"], refresh_world, agents)

        # if use_gui:
        #     gui = init_gui()
        #     refresh_gui(gui, rules["TICK_HZ"])
        #     gui.mainloop()

    else:
        if use_gui:
            gui = init_gui()
            # sim_thread = threading.Thread(target=lock_step_sim, args=(agents, None))
            # sim_thread.start()
            lock_step_sim(agents,gui)
            # gui_thread = threading.Thread(target=CraftBotsGUI.update_window)
            # gui_thread.start()

        else:
            sim_thread = threading.Thread(target=lock_step_sim, args=(agents, None))
            sim_thread.start()


def lock_step_sim(agents, update_model):
    global world
    while not sim_stopped:
        for agent in agents:
            agent.world_info = agent.api.get_world_info()
            agent.get_next_commands()

        time.sleep(1 / world.rules["LOCK_STEP_RATE"])
        if not sim_paused: world.run_tick()

        for agent in agents:
            agent.api.num_of_current_commands = 0

        if world.rules["TIME_LENGTH_TYPE"] == 0:
            if time.time() - world.rules["SIM_LENGTH"] >= start_time:
                return on_close()
        else:
            if world.tick >= world.rules["SIM_LENGTH"] * world.rules["TICK_HZ"]:
                return on_close()

        if update_model is not None:
            # TODO list all agent world info to pick from
            update_model.update_window(agent.api.get_world_info(), sim_length=world.rules["SIM_LENGTH"] * world.rules["TICK_HZ"])


def refresh_gui(gui, tick_hz):

    def refresh_gui_wrapper():
        if not sim_stopped:
            global gui_updating
            gui_updating = True
            gui.update_model()
            gui_updating = False
            refresh_gui(gui, tick_hz)

    gui.after(math.ceil(1000 / tick_hz), refresh_gui_wrapper)


def refresh_world(agents):
    global world
    for agent in agents:
        if not agent.thinking:
            agent.thinking = True
            agent.world_info = agent.api.get_world_info()
            agent_thread = threading.Thread(target=agent.get_next_commands)
            agent_thread.start()
    world.run_tick()
    for agent in agents:
        agent.api.num_of_current_commands = 0
    if world.rules["TIME_LENGTH_TYPE"] == 0:
        if time.time() - world.rules["SIM_LENGTH"] >= start_time:
            return on_close()
    else:
        if world.tick >= world.rules["SIM_LENGTH"] * world.rules["TICK_HZ"]:
            return on_close()


def call_repeatedly(interval, func, *args):
    stopped = threading.Event()

    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            func(*args)
    threading.Thread(target=loop, daemon=True).start()
    return stopped.set


def init_gui():
    gui = CraftBotsGUI(
        reset_callback=None,
        pause_callback=pause_simulation)
    gui_thread = threading.Thread(target=gui.start_window)
    gui_thread.start()
    return gui


def on_close():
    global world
    print("Simulation time up")
    global sim_stopped, simulation_stop
    if simulation_stop is not None:
        simulation_stop()
    sim_stopped = True
    if root is not None:
        try:
            root.destroy()
        except:
            return on_close()
    return world.total_score


def get_world_gen_modifiers(modifier_file):
    return read_ini_file(modifier_file, "craftbots/initialisation_files/default_world_gen_modifiers")


def get_modifiers(modifier_file):
    return read_ini_file(modifier_file, "craftbots/initialisation_files/default_modifiers")
    

def get_rules(rule_file):
    return read_ini_file(rule_file, "craftbots/initialisation_files/default_rules")


def read_ini_file(path, default_path):
    default_file = open(default_path, "r")
    parameters = {}
    for line in default_file:
        data = line.strip("\n").split(" ")
        if data[0] != '' and data[0][0] != "#":
            try:
                parameters[data[0]] = int(data[2])
                continue
            except ValueError:
                try:
                    parameters[data[0]] = float(data[2])
                    continue
                except ValueError:
                    temp = []
                    for value in data[2].split(","):
                        temp.append(int(value))
                    parameters[data[0]] = temp
    default_file.close()

    if path is None: return parameters
    try:
        file = open(path, "r")
        for line in file:
            data = line.strip("\n").split(" ")
            if data[0] != '' and data[0][0] != "#":
                try:
                    parameters[data[0]] = int(data[2])
                    continue
                except ValueError:
                    try:
                        parameters[data[0]] = float(data[2])
                        continue
                    except ValueError:
                        temp = []
                        for value in data[2].split(","):
                            temp.append(int(value))
                        parameters[data[0]] = temp
        file.close()
    except FileNotFoundError:
        pass
    return parameters
