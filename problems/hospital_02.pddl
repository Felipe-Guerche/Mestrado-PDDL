;; Problema 2: Navegação com múltiplos locais
;; Comando: "Robô, vá para a sala de cirurgia"
;; Contexto: Hospital maior com múltiplos corredores e salas

(define (problem hospital-ir-cirurgia)
  (:domain hospital-robo-simples)
  
  (:objects
    pudu - robo
    base recepcao corredor_central corredor_ala_1
    farmacia sala_cirurgia quarto_101 quarto_102 - local
  )
  
  (:init
    ;; Posição inicial do robô
    (em pudu base)
    
    ;; Mapa do hospital (conectividade)
    ;; Base conecta com recepção
    (conectado base recepcao)
    (conectado recepcao base)
    
    ;; Recepção conecta com corredor central
    (conectado recepcao corredor_central)
    (conectado corredor_central recepcao)
    
    ;; Corredor central conecta com corredor ala 1
    (conectado corredor_central corredor_ala_1)
    (conectado corredor_ala_1 corredor_central)
    
    ;; Farmácia no corredor central
    (conectado corredor_central farmacia)
    (conectado farmacia corredor_central)
    
    ;; Salas no corredor ala 1
    (conectado corredor_ala_1 sala_cirurgia)
    (conectado sala_cirurgia corredor_ala_1)
    
    (conectado corredor_ala_1 quarto_101)
    (conectado quarto_101 corredor_ala_1)
    
    (conectado corredor_ala_1 quarto_102)
    (conectado quarto_102 corredor_ala_1)
  )
  
  (:goal
    (em pudu sala_cirurgia)
  )
)

