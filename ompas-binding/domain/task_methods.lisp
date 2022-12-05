(begin
    (def-task rand)
    (def-method m_rand
        (:task rand)
        (:body
            (begin
                (define actors (instances actor))
                (loop
                    (begin
                        (define handles (mapf (lambda (actor) (async (move_rand actor))) actors))
                        (mapf await handles)
                        ;(print "ok")
                    )))))

    
    
    (def-task do_tasks)
    (def-method m_do_tasks
        (:task do_tasks)
        (:body 
            (begin
                (mapf (lambda (actor)
                    (define r (concatenate actor "_storage"))
                    (new-resource actor)
                    (new-resource r 3)) 
                (instance actor))
                (define tasks (instances task))
                (define list-h (mapf (lambda (task) (async (do_task task))) tasks))
                (define do_new_tasks
                    (lambda (tasks)
                        (begin
                            (wait-for `(> (len ,(instances task)) (len tasks)))
                            (new-tasks (instances task))
                            (list-h 
                                (mapf 
                                    (lambda (task) (async (do_task task)))
                                    (sublist (new-tasks) (len tasks))))
                            (do_new_tasks new-tasks))))

                (define h-new-task (async (do_new_tasks tasks)))
                (mapf await list-h)
                (await h-new-task))))

    

    (def-task do_task (:params (?task task)))
    (def-method m_do_task
        (:task do_task)
        (:params (task_id int))
        (:body
            (begin 
                (define resources (task.resources task_id))
                (create_site task)


            )
        )
    )

    (def-lambda get-mine (lambda (colour)
        (begin
            (define search-mine (lambda mines 
                (if (= (mine.colour) colour)
                    mine
                    (search-mine (cdr mines)))))
            (search mine (instances mine)))))

    (def-task mine_resource (:params (?colour colour) (?actor actor)))
    (def-method m_mine_resource
        (:task mine_resource)
        (:params (?colour colour) (?actor actor))
        (:body
            (begin
                (define ?mine (get-mine))
                (move ?actor (mine.node ?mine))
                (check (= (actor.node ?actor) (mine.node ?mine)))
                (dig_at ?actor ?mine)
                (wait-for `(> (len (node.resources ,(mine.node ?mine))) 0))
                ;wait until a resource is dropped
                (pick_up_resource ?actor (car (node.resources (mine.node ?mine))))
            )))

    (def-task deposit_resource (:params (?resource resource) (?task task) (?actor actor)))
    (def-method m_deposit_resource
        (:task deposit_resource)
        (:params (?resource resource) (?task task) (?actor actor))
        (:body
            (begin
                (move ?actor (task.node ?task))
                (deposit_resources ?actor (task.site ?task) ?resource)
            )))

    (def-task create_site (:params (?task task)))
    (def-method m_create_site
        (:task create_site)
        (:params (task task))
        (:body
            (begin
                (define node (task.node task))
                (define actor ...)
                (move actor node)
                (start_site actor task)
            )
        )
    )

    (def-task move (:params (?actor actor) (?node node)))
    (def-method m_move_dijkstra
        (:task move)
        (:params (?actor actor) (?node node))
        (:pre-conditions (!= (actor.node ?actor) node))
        (:body 
            (do
                (define nodes (find_route (actor.node ?actor) ?node))
                (define move_in_list (lambda (nodes)
                    (if (null? nodes)
                        nil
                        (do
                            (define node (car nodes))
                            (move_to ?actor node)
                            (check (= (actor.node ?actor) node)) 
                            (move_in_list (cdr nodes))))))
                (move_in_list nodes)
                            )))
)