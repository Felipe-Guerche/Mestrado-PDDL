;; Domain: Hospital Robot - (Apenas Navegação)
;; Descrição: Robô autônomo que navega entre locais de um hospital
;; Caso de uso: Pudu Robotics / Agliex em ambiente hospitalar
;; Versão: 1.0 - Navegação

(define (domain hospital-robo-simples)
  (:requirements :strips :typing)
  
  ;; ============================================================
  ;; TIPOS
  ;; ============================================================
  (:types 
    robo local - object
  )
  
  ;; ============================================================
  ;; PREDICADOS
  ;; ============================================================
  (:predicates
    ;; Localização do robô
    (em ?r - robo ?loc - local)
    
    ;; Conectividade entre locais
    ;; (conectado loc1 loc2) significa que o robô pode ir de loc1 para loc2
    (conectado ?de ?para - local)
  )
  
  ;; ============================================================
  ;; AÇÕES
  ;; ============================================================
  
  ;; Ação: NAVEGAR
  ;; Descrição: Move o robô de uma localização para outra conectada
  ;; Parâmetros:
  ;;   ?r - robô que vai se mover
  ;;   ?from - localização atual (origem)
  ;;   ?to - localização destino
  (:action navegar
    :parameters (?r - robo ?de ?para - local)
    :precondition (and 
      (em ?r ?de)             ; Robô deve estar na origem
      (conectado ?de ?para)   ; Deve existir caminho de de para para
    )
    :effect (and 
      (not (em ?r ?de))       ; Robô sai da origem
      (em ?r ?para)           ; Robô chega no destino
    )
  )
)