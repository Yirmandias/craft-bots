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
                    ))))))