#!/usr/bin/env python3
"""
==============================================================================
MOCK PLANNER - Planejador Simulado para Demonstração Didática
==============================================================================

Este script implementa um planejador simplificado (mock) para o domínio de
navegação hospitalar. Ele foi desenvolvido para fins educacionais e serve
como um substituto rápido de planners PDDL completos durante desenvolvimento
e testes iniciais.

FUNCIONAMENTO:
  O script realiza parsing de um subconjunto mínimo de PDDL em português para:
  1. Extrair todos os locais declarados no problema
  2. Identificar o nome do robô definido
  3. Extrair a posição inicial do robô: (em robo <local>)
  4. Extrair todas as conexões entre locais: (conectado A B)
  5. Extrair o objetivo desejado: (em robo <local-objetivo>)

  Com essas informações, o planejador:
  - Constrói um grafo de conectividade do hospital
  - Calcula o caminho mais curto entre a posição inicial e o objetivo
    usando o algoritmo BFS (Busca em Largura)
  - Gera um plano de ações de navegação OU um objeto JSON estilo API

MODOS DE SAÍDA:
  1. Padrão: Plano PDDL com ações de navegação
  2. --api: Formato JSON simplificado para integração com APIs
  3. --api --verbose-api: Formato JSON detalhado com waypoints e ETA

EXEMPLOS DE USO:

  # Gerar plano PDDL padrão
  python examples/mock_planner.py problems/hospital_01.pddl
  
  # Gerar saída em formato API (JSON)
  python examples/mock_planner.py problems/hospital_01.pddl --api
  
  # Gerar saída API completa com detalhes
  python examples/mock_planner.py problems/hospital_01.pddl --api --verbose-api

FORMATO DE SAÍDA (Plano PDDL):
  (navigate robo loc1 loc2)
  (navigate robo loc2 loc3)
  ...

FORMATO DE SAÍDA (API JSON):
  {"task": "navigate", "destination": "farmacia", "destination_label": "farmácia"}

LIMITAÇÕES:
  - Este é um planejador SIMPLIFICADO para demonstração
  - Não valida precondições ou efeitos das ações
  - Assume que o grafo é conexo (existe caminho entre todos os pontos)
  - Para planejamento real, use planners completos como Fast Downward ou
    Unified Planning (disponível em planners/pddl_planner.py)
==============================================================================
"""

import re
import sys
from collections import deque, defaultdict
from typing import Dict
import json


def strip_comments(text: str) -> str:
    """
    Remove comentários PDDL do texto.
    
    Esta função processa o arquivo PDDL removendo todas as linhas que
    começam com ';' (comentários em PDDL), facilitando o parsing posterior.
    
    Args:
        text: Conteúdo completo do arquivo PDDL
        
    Returns:
        Texto sem as linhas de comentário
        
    Nota:
        Em PDDL, comentários começam com ';' (ponto e vírgula)
        Similar ao ';' em Lisp/Scheme
    """
    lines = []
    for line in text.splitlines():
        s = line.strip()
        # Ignora linhas que começam com comentário
        if s.startswith(";;"):
            continue
        if s.startswith(";"):
            continue
        lines.append(line)
    return "\n".join(lines)


def parse_problem(file_path: str):
    """
    Faz parsing de um arquivo PDDL de problema e extrai as informações essenciais.
    
    Esta função analisa o arquivo PDDL e extrai:
    - O nome do robô
    - A localização inicial do robô
    - O objetivo (localização desejada)
    - O grafo de conectividade (quais locais estão conectados)
    
    Args:
        file_path: Caminho para o arquivo .pddl do problema
        
    Returns:
        Uma tupla contendo (nome_robo, local_inicial, local_objetivo, grafo_conexoes)
        onde grafo_conexoes é um dicionário {local_origem: [lista_destinos]}
        
    Raises:
        ValueError: Se alguma seção obrigatória não for encontrada
        
    Exemplo:
        robot, start, goal, edges = parse_problem("problems/hospital_01.pddl")
        # robot = "r1"
        # start = "base"
        # goal = "farmacia"
        # edges = {"base": ["farmacia"], "farmacia": ["base"]}
    """
    # Ler o arquivo PDDL
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remover comentários para facilitar o parsing
    content = strip_comments(content)

    # =========================================================================
    # PASSO 1: Extrair objetos declarados no problema
    # =========================================================================
    # Procura o bloco (:objects ...) no PDDL
    objects_match = re.search(r"\(:objects([\s\S]*?)\)", content, re.IGNORECASE)
    if not objects_match:
        raise ValueError("Bloco :objects não encontrado no arquivo PDDL")
    objects_block = objects_match.group(1)

    # Parsear objetos: procurar padrões como "pudu - robo" ou "base farmacia - local"
    robot_names = []
    locations = []
    
    for line in objects_block.splitlines():
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        
        # Procurar padrão: nome1 nome2 ... - tipo
        m = re.search(r"^(.*?)\s-\s(\w+)$", line)
        if not m:
            continue
            
        names_part, type_name = m.group(1), m.group(2)
        names = [n for n in names_part.strip().split() if n]
        
        # Categorizar por tipo
        if type_name.lower() == "robo":
            robot_names.extend(names)
        elif type_name.lower() == "local":
            locations.extend(names)

    # Validar que existe pelo menos um robô
    if not robot_names:
        raise ValueError("Nenhum robô declarado no bloco :objects")
    robot = robot_names[0]  # Usar o primeiro robô encontrado

    # =========================================================================
    # PASSO 2: Extrair estado inicial (:init)
    # =========================================================================
    # O bloco :init contém o estado inicial do mundo
    init_match = re.search(r"\(:init([\s\S]*?)\)\s*\)\s*\Z|\(:init([\s\S]*?)\)\s*\(:goal", content, re.IGNORECASE)
    if not init_match:
        raise ValueError("Bloco :init não encontrado no arquivo PDDL")
    init_block = next(g for g in init_match.groups() if g)

    # Extrair posição inicial do robô: (em <robo> <local>)
    init_loc_match = re.search(r"\(em\s+" + re.escape(robot) + r"\s+(\w+)\)", init_block, re.IGNORECASE)
    if not init_loc_match:
        # Tentar buscar em todo o conteúdo como fallback
        init_loc_match = re.search(r"\(em\s+" + re.escape(robot) + r"\s+(\w+)\)", content, re.IGNORECASE)
        if not init_loc_match:
            raise ValueError(f"Posição inicial do robô '{robot}' não encontrada em :init")
    start_loc = init_loc_match.group(1)

    # Extrair todas as conexões: (conectado <origem> <destino>)
    # Constrói um grafo direcionado de navegação
    edges = defaultdict(list)
    for m in re.finditer(r"\(conectado\s+(\w+)\s+(\w+)\)", init_block, re.IGNORECASE):
        origem, destino = m.group(1), m.group(2)
        edges[origem].append(destino)

    # =========================================================================
    # PASSO 3: Extrair objetivo (:goal)
    # =========================================================================
    # Procurar onde o robô deve estar ao final: (em <robo> <local>)
    goal_loc_match = re.search(r":goal[\s\S]*?\(em\s+" + re.escape(robot) + r"\s+(\w+)\)", content, re.IGNORECASE)
    if not goal_loc_match:
        raise ValueError(f"Objetivo para o robô '{robot}' não encontrado em :goal")
    goal_loc = goal_loc_match.group(1)

    return robot, start_loc, goal_loc, edges


def bfs_path(edges, start, goal):
    """
    Calcula o caminho mais curto entre dois locais usando BFS (Busca em Largura).
    
    Este algoritmo explora o grafo de conectividade nível por nível,
    garantindo que o primeiro caminho encontrado até o objetivo seja
    também o caminho com menor número de passos (ótimo).
    
    Args:
        edges: Dicionário representando o grafo {local: [vizinhos]}
        start: Local de partida (onde o robô está)
        goal: Local de destino (onde o robô quer chegar)
        
    Returns:
        Lista ordenada de locais formando o caminho, incluindo início e fim.
        Exemplo: ["base", "recepcao", "farmacia"]
        Retorna None se não houver caminho possível.
        
    Complexidade:
        O(V + E) onde V = número de locais, E = número de conexões
        
    Algoritmo:
        BFS (Breadth-First Search) - Busca em Largura
        Garante encontrar o caminho mais curto em grafos não-ponderados
    """
    # Caso especial: já está no destino
    if start == goal:
        return [start]
    
    # Conjunto de locais já visitados (para evitar ciclos)
    visited = set([start])
    
    # Fila de exploração: (local_atual, caminho_até_aqui)
    queue = deque([(start, [start])])
    
    while queue:
        # Pegar próximo local a explorar
        node, path = queue.popleft()
        
        # Explorar todos os vizinhos deste local
        for neighbor in edges.get(node, []):
            # Pular se já visitamos este vizinho
            if neighbor in visited:
                continue
            
            # Construir novo caminho incluindo este vizinho
            new_path = path + [neighbor]
            
            # Verificar se chegamos no objetivo
            if neighbor == goal:
                return new_path
            
            # Marcar como visitado e adicionar à fila para exploração
            visited.add(neighbor)
            queue.append((neighbor, new_path))
    
    # Não foi possível encontrar um caminho
    # (grafo desconexo - locais não estão conectados)
    return None


def humanize_location(name: str, custom_map: Dict[str, str]) -> str:
    """
    Converte identificadores técnicos de locais para rótulos legíveis por humanos.
    
    Esta função transforma nomes de locais no formato de identificador
    (ex: "farmacia", "corredor_central") em textos mais apresentáveis
    para interfaces de usuário (ex: "farmácia", "corredor central").
    
    Args:
        name: Identificador técnico do local (formato ASCII, sem acentos)
        custom_map: Dicionário de mapeamento customizado para casos especiais
                    onde é necessário adicionar acentuação ou formatação específica
        
    Returns:
        String formatada para apresentação ao usuário
        
    Exemplo:
        >>> humanize_location("farmacia", {"farmacia": "farmácia"})
        "farmácia"
        >>> humanize_location("corredor_central", {})
        "corredor central"
        
    Comportamento:
        1. Se existe mapeamento customizado, usa ele (para acentuação)
        2. Caso contrário, substitui underscores por espaços
        3. Mantém lowercase (padrão para APIs REST)
    """
    # Primeiro: verificar se existe tradução customizada
    # (necessário para adicionar acentuação em português)
    if name in custom_map:
        return custom_map[name]
    
    # Caso padrão: substituir underscores por espaços
    # Exemplos: "sala_cirurgia" -> "sala cirurgia"
    #           "quarto_101" -> "quarto 101"
    return name.replace("_", " ")


def main():
    if len(sys.argv) < 2:
        print("Usage: python examples/mock_planner.py <problem.pddl>")
        sys.exit(2)

    problem_file = sys.argv[1]
    api_mode = any(arg == "--api" for arg in sys.argv[2:])
    verbose_api = any(arg == "--verbose-api" for arg in sys.argv[2:])
    try:
        robot, start, goal, edges = parse_problem(problem_file)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    path = bfs_path(edges, start, goal)
    if path is None:
        if api_mode:
            # Minimal API-style error payload (didactic)
            result = {
                "task": "navigate",
                "destination": goal,
                "status": "no_path",
            }
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("No solution found (disconnected graph)")
        sys.exit(1)

    if api_mode:
        # Minimal didactic API payload by default
        pretty_map = {
            "farmacia": "farmácia",
            "recepcao": "recepção",
            "corredor_central": "corredor central",
            "corredor_ala_1": "corredor ala 1",
            "corredor_ala_2": "corredor ala 2",
            "corredor_ala_3": "corredor ala 3",
            "sala_cirurgia": "sala de cirurgia",
        }
        human_dest = humanize_location(goal, pretty_map)

        if not verbose_api:
            result = {
                "task": "navigate",
                "destination": goal,
                "destination_label": human_dest,
            }
            print(json.dumps(result, ensure_ascii=False))
        else:
            # Verbose API payload (optional)
            hops = max(0, len(path) - 1)
            eta_seconds = hops * 30
            human_waypoints = [humanize_location(w, pretty_map) for w in path]
            result = {
                "intent": "NAVIGATE",
                "destination": goal,
                "destination_label": human_dest,
                "task": "navigate",
                "waypoints": path,
                "waypoint_labels": human_waypoints,
                "priority": "normal",
                "constraints": [],
                "eta_seconds": eta_seconds,
            }
            print(json.dumps(result, ensure_ascii=False))
    else:
        # Emit plan as navigate steps
        for a, b in zip(path, path[1:]):
            print(f"(navigate {robot} {a} {b})")


if __name__ == "__main__":
    main()


