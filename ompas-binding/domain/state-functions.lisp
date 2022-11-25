(begin
    (def-types 
        (actor_id node_id target_id ressource_id task_id site_id building_id mine_id edge_id int) 
        (state  ;possible state = {IDLE=0, MOVING, DIGGING, CONSTRUCTING, RECOVERING, LOOKING, SENDING, RECEIVING}
        resource_type ;possible colour = {RED, BLUE, ORANGE, BLACK, GREEN} 
        building_type ; possible building type = {BUILDING_TASK, BUILDING_SPEED, BUILDING_MINE, BUILDING_CONSTRUCTION, BUILDING_INVENTORY, BUILDING_ACTOR_SPAWN}
        symbol))
        

    (def-state-function tick (:result int))
    (def-state-function score (:result score))
    
    ;actors state function
    (def-state-function actor.id (:params (?id actor_id)) (:result actor_id))
    (def-state-function actor.node (:params (?id actor_id)) (:result state))
    (def-state-function actor.state (:params (?id actor_id)) (:result state))
    (def-state-function actor.progress (:params (?id actor_id)) (:result int))
    (def-state-function actor.target (:params (?id actor_id)) (:result target_id))
    (def-state-function actor.target (:params (?id actor_id)) (:result (list ressource_id)))

    ;nodes state function
    (def-state-function node.id (:params (?id node_id)) (:result node_id))
    (def-state-function node.actors (:params (?id node_id)) (:result (list actor_id)))
    (def-state-function node.tasks (:params (?id node_id)) (:result (list task_id)))
    (def-state-function node.sites (:params (?id node_id)) (:result (list site_id)))
    (def-state-function node.buildings (:params (?id node_id)) (:result (list building_id)))
    (def-state-function node.resources (:params (?id node_id)) (:result (list ressource_id)))
    (def-state-function node.mines (:params (?id node_id)) (:result (list mine_id)))
    (def-state-function node.edges (:params (?id node_id)) (:result (list edge_id)))
    (def-state-function node.x (:params (?id node_id)) (:result float))
    (def-state-function node.y (:params (?id node_id)) (:result float))

    ;edges
    (def-state-function edge.id (:params (?id edge_id)) (:result edge_id))
    (def-state-function edge.length (:params (?id edge_id)) (:result float))
    (def-state-function edge.node_a (:params (?id edge_id)) (:result node_id))
    (def-state-function edge.node_b (:params (?id edge_id)) (:result node_id))

    ;mines
    (def-state-function mine.id (:params (?id mine_id)) (:result mine_id))
    (def-state-function mine.node (:params (?id mine_id)) (:result node_id))
    (def-state-function mine.colour (:params (?id mine_id)) (:result resource_type))
    (def-state-function mine.max_progress (:params (?id mine_id)) (:result int))
    (def-state-function mine.progress (:params (?id mine_id)) (:result int))

    ;resources
    (def-state-function resource.id (:params (?id resource_id)) (:result resource_id))
    (def-state-function resource.colour (:params (?id resource_id)) (:result node_id))
    (def-state-function resource.location (:params (?id resource_id)) (:result location_id))
    (def-state-function resource.tick_created (:params (?id resource_id)) (:result int))
    (def-state-function resource.used (:params (?id resource_id)) (:result boolean))

    ;sites
    (def-state-function site.id (:params (?id site_id)) (:result site_id))
    (def-state-function site.building_type (:params (?id site_id)) (:result building_type))
    (def-state-function site.node (:params (?id site_id)) (:result node_id))
    (def-state-function site.needed_resources (:params (?id site_id)) (:result (tuple int int int int int)))
    (def-state-function site.deposited_resources (:params (?id site_id)) (:result (tuple int int int int int)))
    (def-state-function site.needed_effort (:params (?id site_id)) (:result int))
    (def-state-function site.max_progress (:params (?id site_id)) (:result int))
    (def-state-function site.progress (:params (?id site_id)) (:result int))

    ;buildings
    (def-state-function building.id (:params (?id site_id)) (:result building_id))
    (def-state-function building.node (:params (?id site_id)) (:result node_id))
    (def-state-function building.building_type (:params (?id site_id)) (:result building_type))

    ;tasks
    (def-state-function task.id (:params (?id site_id)) (:result task_id))
    (def-state-function task.completed (:params (?id site_id)) (:result boolean))
    (def-state-function task.deadline (:params (?id site_id)) (:result int))
    (def-state-function task.score (:params (?id site_id)) (:result int))
    (def-state-function task.node (:params (?id site_id)) (:result node_id))
    (def-state-function task.site (:params (?id site_id)) (:result site_id))
    (def-state-function task.start_time (:params (?id site_id)) (:result int))
    (def-state-function task.difficulty (:params (?id site_id)) (:result int))
    (def-state-function task.needed_resources (:params (?id site_id)) (:result (tuple int int int int int)))
)