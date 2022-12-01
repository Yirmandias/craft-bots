(begin
    (def-task rand)
    (def-method m_rand
        (:task rand)
        (:body
            (begin
                (define agents (instances agent))
                (loop
                    (begin
                        (define handles (mapf (lambda (agent) (async (move_rand agent))) agents))
                        (mapf await handles)
                    ))))))