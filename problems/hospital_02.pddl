;; ============================================================
;; PROBLEMA 2: Navegação Complexa - Ir para a Sala de Cirurgia
;; ============================================================
;; Comando recebido: "Robô, vá para a sala de cirurgia"
;;
;; Cenário:
;;   O robô está na base de carregamento e precisa navegar
;;   por um hospital de médio porte até chegar à sala de cirurgia,
;;   que fica em uma ala específica do hospital.
;;   
;; Layout do ambiente:
;;   Este cenário representa um hospital com múltiplas áreas:
;;   - Base de carregamento (ponto inicial)
;;   - Recepção (entrada principal)
;;   - Corredor Central (via principal de circulação)
;;   - Corredor Ala 1 (corredor lateral com salas de atendimento)
;;   - Farmácia (localizada no corredor central)
;;   - Sala de Cirurgia (no corredor da ala 1)
;;   - Quartos 101 e 102 (também na ala 1)
;;
;; Complexidade:
;;   Ao contrário do Problema 1, este requer navegação por
;;   múltiplos corredores e o planejador precisará encontrar
;;   a rota mais eficiente entre vários caminhos possíveis.
;;
;; Objetivo:
;;   Planejar uma rota da base até a sala de cirurgia,
;;   passando pelos corredores necessários.
;; ============================================================

(define (problem hospital-ir-cirurgia)
  (:domain hospital-robo-simples)
  
  ;; ----------------------------------------------------------
  ;; OBJETOS DO MUNDO
  ;; ----------------------------------------------------------
  ;; Define todas as entidades que existem neste cenário
  ;; mais complexo do hospital.
  ;; ----------------------------------------------------------
  (:objects
    r1 - robo                                                      ; O robô autônomo
    base recepcao corredor_central corredor_ala_1                 ; Áreas de circulação
    farmacia sala_cirurgia quarto_101 quarto_102 - local          ; Salas e destinos
  )
  
  ;; ----------------------------------------------------------
  ;; ESTADO INICIAL
  ;; ----------------------------------------------------------
  ;; Configuração inicial: define onde o robô está e como os
  ;; diferentes locais do hospital estão conectados entre si.
  ;; ----------------------------------------------------------
  (:init
    ;; Posição inicial: robô está na base de carregamento
    (em r1 base)
    
    ;; ========================================================
    ;; TOPOLOGIA DO HOSPITAL (Mapa de Conectividade)
    ;; ========================================================
    ;; Define quais locais estão conectados entre si através
    ;; de corredores ou passagens. Todas as conexões são
    ;; bidirecionais para permitir ida e volta.
    ;; ========================================================
    
    ;; Conexão: Base ↔ Recepção
    ;; A base de carregamento está conectada diretamente à recepção
    (conectado base recepcao)
    (conectado recepcao base)
    
    ;; Conexão: Recepção ↔ Corredor Central
    ;; Da recepção, o robô pode acessar o corredor central
    (conectado recepcao corredor_central)
    (conectado corredor_central recepcao)
    
    ;; Conexão: Corredor Central ↔ Corredor Ala 1
    ;; O corredor central dá acesso ao corredor da ala 1
    (conectado corredor_central corredor_ala_1)
    (conectado corredor_ala_1 corredor_central)
    
    ;; Conexão: Corredor Central ↔ Farmácia
    ;; A farmácia fica diretamente acessível pelo corredor central
    (conectado corredor_central farmacia)
    (conectado farmacia corredor_central)
    
    ;; Conexão: Corredor Ala 1 ↔ Sala de Cirurgia
    ;; A sala de cirurgia está localizada no corredor da ala 1
    (conectado corredor_ala_1 sala_cirurgia)
    (conectado sala_cirurgia corredor_ala_1)
    
    ;; Conexão: Corredor Ala 1 ↔ Quarto 101
    ;; O quarto 101 também está nesta ala
    (conectado corredor_ala_1 quarto_101)
    (conectado quarto_101 corredor_ala_1)
    
    ;; Conexão: Corredor Ala 1 ↔ Quarto 102
    ;; O quarto 102 também está nesta ala
    (conectado corredor_ala_1 quarto_102)
    (conectado quarto_102 corredor_ala_1)
  )
  
  ;; ----------------------------------------------------------
  ;; OBJETIVO (Meta a ser alcançada)
  ;; ----------------------------------------------------------
  ;; O planejador deve encontrar uma sequência de ações de
  ;; navegação que leve o robô da base até a sala de cirurgia.
  ;; 
  ;; Rota esperada:
  ;;   Base → Recepção → Corredor Central → Corredor Ala 1 → Sala de Cirurgia
  ;; ----------------------------------------------------------
  (:goal
    (em r1 sala_cirurgia)        ; O robô deve estar na sala de cirurgia
  )
)

