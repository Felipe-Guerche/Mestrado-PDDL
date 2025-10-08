;; ============================================================
;; PROBLEMA 1: Navegação Simples - Ir para a Farmácia
;; ============================================================
;; Comando recebido: "Robô, vá para a farmácia"
;;
;; Cenário:
;;   O robô está estacionado na base de carregamento e
;;   recebe uma solicitação para ir até a farmácia do hospital.
;;   
;; Layout do ambiente:
;;   Este é um cenário minimalista com apenas dois locais:
;;   - Base (onde o robô inicia)
;;   - Farmácia (destino desejado)
;;   
;;   Os dois locais estão diretamente conectados por um corredor.
;;
;; Objetivo:
;;   O robô deve planejar e executar uma rota para chegar
;;   da base até a farmácia.
;; ============================================================

(define (problem hospital-ir-farmacia)
  (:domain hospital-robo-simples)
  
  ;; ----------------------------------------------------------
  ;; OBJETOS DO MUNDO
  ;; ----------------------------------------------------------
  ;; Define todas as entidades que existem neste problema
  ;; específico.
  ;; ----------------------------------------------------------
  (:objects
    r1 - robo                ; O robô autônomo que irá navegar
    base farmacia - local    ; Os dois locais do hospital neste cenário
  )
  
  ;; ----------------------------------------------------------
  ;; ESTADO INICIAL
  ;; ----------------------------------------------------------
  ;; Descreve como o mundo está configurado no momento inicial,
  ;; antes de qualquer ação ser executada.
  ;; ----------------------------------------------------------
  (:init
    ;; Posição inicial: o robô começa na base de carregamento
    (em r1 base)
    
    ;; Topologia do ambiente: define quais locais estão conectados
    ;; Neste caso, há uma conexão bidirecional entre base e farmácia
    (conectado base farmacia)      ; Caminho: base → farmácia
    (conectado farmacia base)      ; Caminho: farmácia → base (retorno)
  )
  
  ;; ----------------------------------------------------------
  ;; OBJETIVO (Meta a ser alcançada)
  ;; ----------------------------------------------------------
  ;; Define o estado desejado que o planejador deve tentar
  ;; alcançar através de uma sequência de ações.
  ;; ----------------------------------------------------------
  (:goal
    (em r1 farmacia)        ; O robô deve estar na farmácia
  )
)