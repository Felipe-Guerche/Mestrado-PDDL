;; ============================================================
;; DOMÍNIO: Hospital Robot - Navegação Básica
;; ============================================================
;; Descrição: 
;;   Este domínio modela um robô autônomo que é capaz de navegar
;;   entre diferentes locais dentro de um ambiente hospitalar.
;;   O robô pode se mover de um local para outro, desde que exista
;;   uma conexão (corredor, passagem) entre esses locais.
;;
;; Caso de uso prático:
;;   Baseado em robôs de serviço hospitalar que realizam entregas
;;   de medicamentos, alimentos e outros itens em hospitais e clínicas.
;;   Exemplos incluem robôs autônomos de navegação indoor.
;;
;; Versão: 1.0 - Navegação Básica (sem transporte de objetos)
;; ============================================================

(define (domain hospital-robo-simples)
  (:requirements :strips :typing)
  
  ;; ============================================================
  ;; TIPOS DE OBJETOS
  ;; ============================================================
  ;; Define os tipos de entidades que existem neste domínio:
  ;;   - robo: representa o robô autônomo que irá navegar
  ;;   - local: representa os diferentes locais do hospital
  ;;            (salas, corredores, recepção, etc.)
  ;; ============================================================
  (:types 
    robo local - object
  )
  
  ;; ============================================================
  ;; PREDICADOS (Estados do Mundo)
  ;; ============================================================
  ;; Define as relações e propriedades que podem ser verdadeiras
  ;; ou falsas em um determinado momento.
  ;; ============================================================
  (:predicates
    ;; Indica onde o robô está localizado no momento
    ;; Exemplo: (em r1 farmacia) = "o robô r1 está na farmácia"
    (em ?r - robo ?loc - local)
    
    ;; Indica se existe um caminho direto entre dois locais
    ;; Representa a topologia/mapa do hospital
    ;; Exemplo: (conectado base farmacia) = "é possível ir da base para a farmácia"
    ;; Nota: A conexão é direcional, então é necessário definir
    ;;       (conectado A B) E (conectado B A) para movimento bidirecional
    (conectado ?de ?para - local)
  )
  
  ;; ============================================================
  ;; AÇÕES DISPONÍVEIS
  ;; ============================================================
  ;; Define as ações que o robô pode executar para modificar
  ;; o estado do mundo.
  ;; ============================================================
  
  ;; ------------------------------------------------------------
  ;; Ação: NAVEGAR
  ;; ------------------------------------------------------------
  ;; Descrição:
  ;;   Move o robô de sua localização atual para um local adjacente,
  ;;   desde que exista uma conexão entre os dois locais.
  ;;
  ;; Parâmetros:
  ;;   ?r    - O robô que irá realizar o movimento
  ;;   ?de   - Local de origem (onde o robô está atualmente)
  ;;   ?para - Local de destino (para onde o robô quer ir)
  ;;
  ;; Pré-condições (o que deve ser verdade antes da ação):
  ;;   1. O robô deve estar fisicamente no local de origem
  ;;   2. Deve existir uma conexão/caminho do local de origem
  ;;      para o local de destino
  ;;
  ;; Efeitos (o que muda após a ação ser executada):
  ;;   1. O robô não está mais no local de origem
  ;;   2. O robô agora está no local de destino
  ;; ------------------------------------------------------------
  (:action navegar
    :parameters (?r - robo ?de ?para - local)
    :precondition (and 
      (em ?r ?de)
      (conectado ?de ?para)
    )
    :effect (and 
      (not (em ?r ?de))
      (em ?r ?para)
    )
  )
)