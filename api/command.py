class Command:

    MOVE_TO = 0
    MOVE_RAND = 1
    PICK_UP_RESOURCE = 2
    DROP_RESOURCE = 3
    DROP_ALL_RESOURCES = 4
    DIG_AT = 5
    START_SITE = 6
    CONSTRUCT_AT = 7
    DEPOSIT_RESOURCES = 8
    CANCEL_ACTION = 9
    START_LOOKING = 10
    START_SENDING = 11
    START_RECEIVING = 12

    PENDING    = 0
    ACTIVE     = 1
    REJECTED   = 2
    PREEMPTING = 3
    ABORTED    = 4
    SUCCEEDED  = 5
    PREEMPTED  = 6

    def __init__(self, world, function_id, *args):
        self.world = world
        self.id = self.world.get_new_id()
        self.world.command_queue.append(self)
        self.function_id = function_id
        self.args = args
        self.result = None
        self.state = Command.PENDING
        self.progress = 0.0

        self.fields = {"id": self.id, "function_id": self.function_id, "args": self.args, "result": self.result,
                       "state": self.state, "progress": self.progress}

    def perform(self):
        result = False
        actor = self.world.get_by_id(self.args[0], entity_type="Actor")
        if actor is not None:
            if self.function_id == Command.MOVE_TO and self.args.__len__() == 2:
                target_node = self.world.get_by_id(self.args[1], entity_type="Node")
                if target_node is not None:
                    self.set_result(actor.travel_to(target_node))
                    result = self.result
            elif self.function_id == Command.MOVE_RAND and self.args.__len__() == 1:
                self.set_result(actor.travel_rand())
                result = self.result
            elif self.function_id == Command.PICK_UP_RESOURCE and self.args.__len__() == 2:
                resource = self.world.get_by_id(self.args[1], entity_type="Resource")
                if  resource is not None:
                    self.set_result(actor.pick_up_resource(resource))
                    result = self.result
            elif self.function_id == Command.DROP_RESOURCE and self.args.__len__() == 2:
                resource = self.world.get_by_id(self.args[1], entity_type="Resource")
                if resource is not None:
                    self.set_result(actor.drop_resource(resource))
                    result = self.result
            elif self.function_id == Command.DROP_ALL_RESOURCES and self.args.__len__() == 1:
                self.set_result(actor.drop_everything())
                result = self.result
            elif self.function_id == Command.DIG_AT and self.args.__len__() == 2:
                mine = self.world.get_by_id(self.args[1], entity_type="Mine")
                if mine is not None:
                    self.set_result(actor.dig_at(mine))
                    result = self.result
            elif self.function_id == Command.START_SITE and self.args.__len__() == 2:
                self.set_result(actor.start_site(self.args[1]))
                result = self.result
            elif self.function_id == Command.CONSTRUCT_AT and self.args.__len__() == 2:
                site = self.world.get_by_id(self.args[1], entity_type="Site")
                if site is None:
                    site = self.world.get_by_id(self.args[1], entity_type="Building")
                    self.set_result(actor.construct_at(site))
                    result = self.result
            elif self.function_id == Command.DEPOSIT_RESOURCES and self.args.__len__() == 3:
                site = self.world.get_by_id(self.args[1], entity_type="Site")
                resource = self.world.get_by_id(self.args[2], entity_type="Resource")            
                if site is not None and resource is not None:
                    site = self.world.get_by_id(self.args[1], entity_type="Building")
                    self.set_result(actor.deposit(site, resource))
                    result = self.result
            elif self.function_id == Command.CANCEL_ACTION and self.args.__len__() == 1:
                self.set_result(actor.cancel_action())
                result = self.result
            elif self.function_id == Command.START_LOOKING and self.args.__len__() == 1:
                self.set_result(actor.look())
                result = self.result
            elif self.function_id == Command.START_SENDING and self.args.__len__() == 2:
                self.set_result(actor.start_sending(self.args[1]))
                result = self.result
            elif self.function_id == Command.START_RECEIVING and self.args.__len__() == 1:
                self.set_result(actor.start_receiving())
                result = self.result
            else:
                pass

        if result == None:
            self.set_state(Command.ACTIVE)
            actor.set_current_command(self)
        elif result == False:
            self.set_state(Command.REJECTED)
        elif result == True:
            self.set_state(Command.SUCCEEDED)
        return 

    def set_result(self, result):
        self.result = result
        self.fields.__setitem__("result", result)
        
    def set_state(self, state):
        self.state = state
        self.fields.__setitem__("state", state)
    
    def set_progress(self, progress: float):
        self.progress = progress
        self.fields.__setitem__("progress", progress)
