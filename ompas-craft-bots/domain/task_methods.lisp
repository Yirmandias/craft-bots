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
            (do
                (mapf (lambda (actor)
                    (begin
                    ;(define r (concatenate actor "_storage"))
                    (new-resource actor)
                    (new-resource r 3)))
                (instances actor))
                ;(define tasks (instances task))
                (define ?task (car (instances task)))
                ;(define list-h (mapf (lambda (__task__) (async (do_task __task__))) tasks))
                (define list-h (mapf (lambda (__task__) (async (do_task __task__))) (list ?task)))

                ;(define do_new_tasks
                ;    (lambda (tasks)
                ;        (begin
                ;            (wait-for `(> (len ,(instances task)) (len tasks)))
                ;            (define new-tasks (instances task))
                ;            (list-h 
                ;                (mapf 
                ;                    (lambda (task) (async (do_task task)))
                ;                    (sublist (new-tasks) (len tasks))))
                ;            (do_new_tasks new-tasks))))

                ;(define h-new-task (async (do_new_tasks tasks)))
                (mapf await list-h)
                ;(await h-new-task)
                )))

    (def-lambda needed-resources-as-list (lambda (resources)
        (begin
            (define gen-list (lambda (colour number)
                (if (= number 0)
                    nil
                    (cons colour (gen-list colour (- number 1))))))
            (append (gen-list 'red (get resources 0))
                (gen-list 'blue (get resources 1))
                (gen-list 'orange (get resources 2))
                (gen-list 'black (get resources 3))
                (gen-list 'green (get resources 4))
            ))))

    

    (def-task do_task (:params (?task task)))
    (def-method m_do_task
        (:task do_task)
        (:params (?task task))
        (:body
            (do 
                (create_site ?task)
                (define resources (task.needed_resources ?task))
                (define needed-resources (needed-resources-as-list resources))
                (print "needed resources for task " ?task ": " needed-resources)
                (define list-h (mapf (lambda (?color)
                    (async (do
                        (print "task = " ?task " color= " ?color)
                        (define h_r (acquire-in-list (instances actor)))
                        (define ?actor (first h_r))
                        (print "actor acquired")
                        (define ?mine (get-mine ?color))
                        (print "mine = " ?mine)
                        (move ?actor (mine.node ?mine))
                        (check (= (actor.node ?actor) (mine.node ?mine)))
                        (dig_at ?actor ?mine)
                        (wait-for `(> (len (node.resources ,(mine.node ?mine))) 0))
                        ;wait until a resource is dropped
                        (define ?resource (car (node.resources (mine.node ?mine))))
                        (pick_up_resource ?actor ?resource)
                        (move ?actor (task.node ?task))
                        (wait-for `(= (actor.state ,?actor) idle))
                        (deposit_resources ?actor (task.site ?task) ?resource)
                        (wait-for `(= (actor.state ,?actor) idle))
                    )))
                    needed-resources))
                (mapf await list-h)
                (define h_r (acquire-in-list (instances actor)))
                (define ?actor (first h_r))
                (move ?actor (task.node ?task))
                (define ?site (task.site ?task))
                (if (!= (site.deposited_resources ?site) (site.needed_resources ?site))
                    (print "error with deposited resource")
                    (construct_at ?actor (task.site ?task)))
            )
        )
    )

    (def-lambda get-mine (lambda (colour)
        (begin
            (define search-mine (lambda (mines) 
                (if (= (mine.colour (car mines)) colour)
                    (car mines)
                    (search-mine (cdr mines)))))
            (search-mine (instances mine)))))

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
                (deposit_resource ?actor (task.site ?task) ?resource)
            )))

    (def-task create_site (:params (?task task)))
    (def-method m_create_site
        (:task create_site)
        (:params (?task task))
        (:body
            (do
                (define ?node (task.node ?task))
                (define h_r (acquire-in-list (instances actor)))
                (define ?actor (first h_r))
                (move ?actor ?node)
                (check (= (actor.node ?actor) ?node))
                (start_site ?actor ?task)
            )
        )
    )

    (def-task move (:params (?actor actor) (?node node)))
    (def-method m_move_dijkstra
        (:task move)
        (:params (?actor actor) (?node node))
        (:pre-conditions (!= (actor.node ?actor) ?node))
        (:body 
            (do
                (define nodes (find_route (actor.node ?actor) ?node))
                (define move_in_list (lambda (nodes)
                    (if (null? nodes)
                        nil
                        (do
                            (define ?node (car nodes))
                            (move_to ?actor ?node)
                            (sleep 0.1)
                            (check (= (actor.node ?actor) ?node)) 
                            (move_in_list (cdr nodes))))))
                (move_in_list nodes)
                            )))
    (def-method m_move_idle
        (:task move)
        (:params (?actor actor) (?node node))
        (:pre-conditions (= (actor.node ?actor) ?node)))
)