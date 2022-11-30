(begin
    (def-types 
        (state  ;possible state = {IDLE=0, MOVING, DIGGING, CONSTRUCTING, RECOVERING, LOOKING, SENDING, RECEIVING}
        resource_type ;possible colour = {RED, BLUE, ORANGE, BLACK, GREEN} 
        building_type ; possible building type = {BUILDING_TASK, BUILDING_SPEED, BUILDING_MINE, BUILDING_CONSTRUCTION, BUILDING_INVENTORY, BUILDING_ACTOR_SPAWN}
        symbol))
    
    (def-objects 
        (idle moving digging constructing recovering looking sending receiving state)
        (red blue orange black green resource_type)
        (building_task building_speed building_mine building_construction building_inventory building_actor_spawn building_type)
    )
        

    (def-state-function tick (:result int))
    (def-state-function score (:result score))
    
    ;actors state function
    (def-state-function actor.id (:params (?id int)) (:result int))
    (def-state-function actor.node (:params (?id int)) (:result state))
    (def-state-function actor.state (:params (?id int)) (:result state))
    (def-state-function actor.progress (:params (?id int)) (:result int))
    (def-state-function actor.target (:params (?id int)) (:result target_id))
    (def-state-function actor.target (:params (?id int)) (:result (list ressource_id)))

    ;nodes state function
    (def-state-function node.id (:params (?id int)) (:result int))
    (def-state-function node.actors (:params (?id int)) (:result (list int)))
    (def-state-function node.tasks (:params (?id int)) (:result (list int)))
    (def-state-function node.sites (:params (?id int)) (:result (list int)))
    (def-state-function node.buildings (:params (?id int)) (:result (list int)))
    (def-state-function node.resources (:params (?id int)) (:result (list int)))
    (def-state-function node.mines (:params (?id int)) (:result (list int)))
    (def-state-function node.edges (:params (?id int)) (:result (list int)))
    (def-state-function node.x (:params (?id int)) (:result float))
    (def-state-function node.y (:params (?id int)) (:result float))

    ;edges
    (def-state-function edge.id (:params (?id int)) (:result int))
    (def-state-function edge.length (:params (?id int)) (:result float))
    (def-state-function edge.node_a (:params (?id int)) (:result int))
    (def-state-function edge.node_b (:params (?id int)) (:result int))

    ;mines
    (def-state-function mine.id (:params (?id int)) (:result int))
    (def-state-function mine.node (:params (?id int)) (:result int))
    (def-state-function mine.colour (:params (?id int)) (:result resource_type))
    (def-state-function mine.max_progress (:params (?id int)) (:result int))
    (def-state-function mine.progress (:params (?id int)) (:result int))

    ;resources
    (def-state-function resource.id (:params (?id int)) (:result int))
    (def-state-function resource.colour (:params (?id int)) (:result resource_type))
    (def-state-function resource.location (:params (?id int)) (:result int))
    (def-state-function resource.tick_created (:params (?id int)) (:result int))
    (def-state-function resource.used (:params (?id int)) (:result boolean))

    ;sites
    (def-state-function site.id (:params (?id int)) (:result int))
    (def-state-function site.building_type (:params (?id int)) (:result building_type))
    (def-state-function site.node (:params (?id int)) (:result int))
    (def-state-function site.needed_resources (:params (?id int)) (:result (tuple int int int int int)))
    (def-state-function site.deposited_resources (:params (?id int)) (:result (tuple int int int int int)))
    (def-state-function site.needed_effort (:params (?id int)) (:result int))
    (def-state-function site.max_progress (:params (?id int)) (:result int))
    (def-state-function site.progress (:params (?id int)) (:result int))

    ;buildings
    (def-state-function building.id (:params (?id int)) (:result int))
    (def-state-function building.node (:params (?id int)) (:result int))
    (def-state-function building.building_type (:params (?id int)) (:result building_type))

    ;tasks
    (def-state-function task.id (:params (?id int)) (:result int))
    (def-state-function task.completed (:params (?id int)) (:result boolean))
    (def-state-function task.deadline (:params (?id int)) (:result int))
    (def-state-function task.score (:params (?id int)) (:result int))
    (def-state-function task.node (:params (?id int)) (:result int))
    (def-state-function task.site (:params (?id int)) (:result int))
    (def-state-function task.start_time (:params (?id int)) (:result int))
    (def-state-function task.difficulty (:params (?id int)) (:result int))
    (def-state-function task.needed_resources (:params (?id int)) (:result (tuple int int int int int)))
)