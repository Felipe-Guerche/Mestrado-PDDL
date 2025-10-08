#!/usr/bin/env python3
"""
Mock planner for the hospital-robot-simple domain.

This script parses a minimal subset of problem PDDL (em português) to:
- Extrair locais e o nome do robô
- Extrair (em robo <local>) posição inicial
- Extrair (conectado A B) arestas
- Extrair goal (em robo <local-objetivo>)

Then it computes a shortest path from the initial location to the goal location
using BFS and prints either:
- a plan with navigate actions (default), or
- an API-style intent object suitable for robot APIs.

Usage:
  python examples/mock_planner.py problems/hospital_01.pddl
  python examples/mock_planner.py problems/hospital_01.pddl --api

Output plan format:
  (navigate robo loc1 loc2)
  ...
"""

import re
import sys
from collections import deque, defaultdict
from typing import Dict
import json


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith(";;"):
            continue
        if s.startswith(";"):
            continue
        lines.append(line)
    return "\n".join(lines)


def parse_problem(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = strip_comments(content)

    # Extrair bloco de objetos
    objects_match = re.search(r"\(:objects([\s\S]*?)\)", content, re.IGNORECASE)
    if not objects_match:
        raise ValueError("No :objects block found")
    objects_block = objects_match.group(1)

    # Coletar tokens (nomes antes do "-" e tipos)
    # Procurar tipos 'robo' e 'local'
    robot_names = []
    locations = []
    # Split by lines, handle segments like: name1 name2 - location
    for line in objects_block.splitlines():
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        # pattern: names - type
        m = re.search(r"^(.*?)\s-\s(\w+)$", line)
        if not m:
            continue
        names_part, type_name = m.group(1), m.group(2)
        names = [n for n in names_part.strip().split() if n]
        if type_name.lower() == "robo":
            robot_names.extend(names)
        elif type_name.lower() == "local":
            locations.extend(names)

    if not robot_names:
        raise ValueError("No robot declared in :objects")
    robot = robot_names[0]

    # Extrair bloco :init
    init_match = re.search(r"\(:init([\s\S]*?)\)\s*\)\s*\Z|\(:init([\s\S]*?)\)\s*\(:goal", content, re.IGNORECASE)
    if not init_match:
        raise ValueError("No :init block found")
    init_block = next(g for g in init_match.groups() if g)

    # Posição inicial: (em robo <local>)
    init_loc_match = re.search(r"\(em\s+" + re.escape(robot) + r"\s+(\w+)\)", init_block, re.IGNORECASE)
    if not init_loc_match:
        # Fallback global
        init_loc_match = re.search(r"\(em\s+" + re.escape(robot) + r"\s+(\w+)\)", content, re.IGNORECASE)
        if not init_loc_match:
            raise ValueError("Posição inicial do robô não encontrada em :init")
    start_loc = init_loc_match.group(1)

    # Conexões: (conectado A B)
    edges = defaultdict(list)
    for m in re.finditer(r"\(conectado\s+(\w+)\s+(\w+)\)", init_block, re.IGNORECASE):
        a, b = m.group(1), m.group(2)
        edges[a].append(b)

    # Objetivo: buscar (em robo <local>) após :goal
    goal_loc_match = re.search(r":goal[\s\S]*?\(em\s+" + re.escape(robot) + r"\s+(\w+)\)", content, re.IGNORECASE)
    if not goal_loc_match:
        raise ValueError("Objetivo (em robo <local>) não encontrado em :goal")
    goal_loc = goal_loc_match.group(1)

    return robot, start_loc, goal_loc, edges


def bfs_path(edges, start, goal):
    if start == goal:
        return [start]
    visited = set([start])
    queue = deque([(start, [start])])
    while queue:
        node, path = queue.popleft()
        for nei in edges.get(node, []):
            if nei in visited:
                continue
            npath = path + [nei]
            if nei == goal:
                return npath
            visited.add(nei)
            queue.append((nei, npath))
    return None


def humanize_location(name: str, custom_map: Dict[str, str]) -> str:
    # Use custom overrides first (to handle accents etc.)
    if name in custom_map:
        return custom_map[name]
    # Replace underscores with spaces and keep lowercase as typical APIs do
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


