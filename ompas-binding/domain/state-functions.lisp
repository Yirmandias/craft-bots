(begin
    (def-types 
        (state  ;possible state = {IDLE=0, MOVING, DIGGING, CONSTRUCTING, RECOVERING, LOOKING, SENDING, RECEIVING}
        resource_type ;possible colour = {RED, BLUE, ORANGE, BLACK, GREEN} 
        building_type ; possible building type = {BUILDING_TASK, BUILDING_SPEED, BUILDING_MINE, BUILDING_CONSTRUCTION, BUILDING_INVENTORY, BUILDING_ACTOR_SPAWN}
        symbol)
        (actor node edge site resource building mine task command object))
    
    (def-objects 
        (idle moving digging constructing recovering looking sending receiving state)
        (red blue orange black green resource_type)
        (building_task building_speed building_mine building_construction building_inventory building_actor_spawn building_type)
    )
        

    (def-state-function tick (:result int))
    (def-state-function score (:result score))
    
    ;actors state function
    (def-state-function actor.id (:params (?id actor)) (:result int))
    (def-state-function actor.node (:params (?id actor)) (:result node))
    (def-state-function actor.state (:params (?id actor)) (:result state))
    (def-state-function actor.progress (:params (?id actor)) (:result int))
    (def-state-function actor.target (:params (?id actor)) (:result (list object)))
    ;(def-state-function actor.target (:params (?id actor)) (:result (list ressource_id)))

    ;nodes state function
    (def-state-function node.id (:params (?id node)) (:result int))
    (def-state-function node.actors (:params (?id node)) (:result (list actor)))
    (def-state-function node.tasks (:params (?id node)) (:result (list task)))
    (def-state-function node.sites (:params (?id node)) (:result (list site)))
    (def-state-function node.buildings (:params (?id node)) (:result (list building)))
    (def-state-function node.resources (:params (?id node)) (:result (list resource)))
    (def-state-function node.mines (:params (?id node)) (:result (list mine)))
    (def-state-function node.edges (:params (?id node)) (:result (list edge)))
    (def-state-function node.x (:params (?id node)) (:result float))
    (def-state-function node.y (:params (?id node)) (:result float))

    ;edges
    (def-state-function edge.id (:params (?id edge)) (:result int))
    (def-state-function edge.length (:params (?id edge)) (:result float))
    (def-state-function edge.node_a (:params (?id edge)) (:result int))
    (def-state-function edge.node_b (:params (?id edge)) (:result int))

    ;mines
    (def-state-function mine.id (:params (?id mine)) (:result int))
    (def-state-function mine.node (:params (?id mine)) (:result node))
    (def-state-function mine.colour (:params (?id mine)) (:result resource_type))
    (def-state-function mine.max_progress (:params (?id mine)) (:result int))
    (def-state-function mine.progress (:params (?id mine)) (:result int))

    ;resources
    (def-state-function resource.id (:params (?id resource)) (:result int))
    (def-state-function resource.colour (:params (?id resource)) (:result resource_type))
    (def-state-function resource.location (:params (?id resource)) (:result object))
    (def-state-function resource.tick_created (:params (?id int)) (:result int))
    (def-state-function resource.used (:params (?id resource)) (:result boolean))

    ;sites
    (def-state-function site.id (:params (?id site)) (:result int))
    (def-state-function site.building_type (:params (?id site)) (:result building_type))
    (def-state-function site.node (:params (?id site)) (:result node))
    (def-state-function site.needed_resources (:params (?id site)) (:result (tuple int int int int int)))
    (def-state-function site.deposited_resources (:params (?id site)) (:result (tuple int int int int int)))
    (def-state-function site.needed_effort (:params (?id site)) (:result int))
    (def-state-function site.max_progress (:params (?id site)) (:result int))
    (def-state-function site.progress (:params (?id site)) (:result int))

    ;buildings
    (def-state-function building.id (:params (?id building)) (:result int))
    (def-state-function building.node (:params (?id building)) (:result node))
    (def-state-function building.building_type (:params (?id int)) (:result building_type))

    ;tasks
    (def-state-function task.id (:params (?id task)) (:result int))
    (def-state-function task.completed (:params (?id task)) (:result boolean))
    (def-state-function task.deadline (:params (?id task)) (:result int))
    (def-state-function task.score (:params (?id task)) (:result int))
    (def-state-function task.node (:params (?id task)) (:result node))
    (def-state-function task.site (:params (?id task)) (:result site))
    (def-state-function task.start_time (:params (?id task)) (:result int))
    (def-state-function task.difficulty (:params (?id task)) (:result int))
    (def-state-function task.needed_resources (:params (?id int)) (:result (tuple int int int int int)))
)