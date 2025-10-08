;; Problema 1: Navegação Simples
;; Comando: "Robô, vá para a farmácia"
;; Contexto: Robô está na base, precisa ir para farmácia

(define (problem hospital-ir-farmacia)
  (:domain hospital-robo-simples)
  
  (:objects
    robo - robo
    base farmacia - local
  )
  
  (:init
    ;; Posição inicial do robô
    (em robo base)
    
    ;; Mapa do hospital (conectividade)
    (conectado base farmacia)
    (conectado farmacia base)
  )
  
  (:goal
    (em robo farmacia)
  )
)