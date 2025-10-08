#!/usr/bin/env python3
"""
==============================================================================
CONFIGURAÇÕES DO SISTEMA PDDL
==============================================================================

Arquivo de configuração centralizado para o sistema de planners PDDL.
Modifique as configurações aqui para personalizar o comportamento.

==============================================================================
"""

# ============================================================================
# CONFIGURAÇÕES DE PLANNERS
# ============================================================================

# Planner padrão (usado quando não especificado)
DEFAULT_PLANNER = "fast-downward"

# Planners disponíveis e suas configurações
PLANNERS = {
    "fast-downward": {
        "name": "Fast Downward",
        "description": "Planner clássico de alto desempenho",
        "command": ["python", "planners/pddl_planner.py"],
        "args": ["--planner", "fast-downward"],
        "requires_venv": True
    },
    "unified-planning": {
        "name": "Unified Planning", 
        "description": "Biblioteca Python moderna",
        "command": ["python", "planners/pddl_planner.py"],
        "args": ["--planner", "unified-planning"],
        "requires_venv": True
    },
    "pyperplan": {
        "name": "Pyperplan",
        "description": "Planner Python puro e simples",
        "command": ["python", "planners/pddl_planner.py"],
        "args": ["--planner", "pyperplan"],
        "requires_venv": True
    },
    "mock": {
        "name": "Mock Planner",
        "description": "Planejador didático (BFS)",
        "command": ["python", "examples/mock_planner.py"],
        "args": [],
        "requires_venv": True
    }
}

# ============================================================================
# CONFIGURAÇÕES DE DOMÍNIOS E PROBLEMAS
# ============================================================================

# Domínios disponíveis
DOMAINS = {
    "hospital": {
        "name": "Hospital Robot",
        "description": "Navegação de robô em hospital",
        "file": "domains/hospital_robot.pddl"
    }
}

# Problemas disponíveis
PROBLEMS = {
    "01": {
        "name": "Problema Simples",
        "description": "Navegação base → farmácia (2 locais)",
        "file": "problems/hospital_01.pddl"
    },
    "02": {
        "name": "Problema Complexo", 
        "description": "Navegação base → sala cirurgia (8 locais)",
        "file": "problems/hospital_02.pddl"
    }
}

# ============================================================================
# CONFIGURAÇÕES DE FORMATOS DE SAÍDA
# ============================================================================

# Formato padrão
DEFAULT_FORMAT = "json"

# Formatos disponíveis
FORMATS = {
    "json": {
        "name": "JSON Simples",
        "description": "Uma linha JSON por passo (waypoint)",
        "raw_flag": False
    },
    "raw": {
        "name": "Plano PDDL Cru",
        "description": "Ações PDDL tradicionais, uma por linha",
        "raw_flag": True
    },
    "save": {
        "name": "Salvar Arquivo",
        "description": "Salva plano completo em arquivo",
        "raw_flag": False,
        "requires_file": True
    }
}

# ============================================================================
# CONFIGURAÇÕES DE AMBIENTE
# ============================================================================

# Caminho do ambiente virtual
VENV_PATH = ".venv/bin/activate"

# Timeout para execução (segundos)
EXECUTION_TIMEOUT = 60

# Mostrar informações de debug
DEBUG_MODE = False

# ============================================================================
# CONFIGURAÇÕES DE INTERFACE
# ============================================================================

# Símbolos para interface
SYMBOLS = {
    "success": "✅",
    "error": "❌", 
    "info": "ℹ️",
    "warning": "⚠️",
    "running": "🚀",
    "config": "📋"
}

# Cores para terminal (se suportado)
COLORS = {
    "success": "\033[92m",    # Verde
    "error": "\033[91m",      # Vermelho
    "info": "\033[94m",       # Azul
    "warning": "\033[93m",    # Amarelo
    "reset": "\033[0m"        # Reset
}

# ============================================================================
# CONFIGURAÇÕES DE MAPEAMENTO DE LABELS
# ============================================================================

# Mapeamento de locais para labels humanizados
LOCATION_LABELS = {
    "farmacia": "farmácia",
    "recepcao": "recepção", 
    "corredor_central": "corredor central",
    "corredor_ala_1": "corredor ala 1",
    "corredor_ala_2": "corredor ala 2",
    "corredor_ala_3": "corredor ala 3",
    "sala_cirurgia": "sala de cirurgia",
    "quarto_101": "quarto 101",
    "quarto_102": "quarto 102",
}

# ============================================================================
# CONFIGURAÇÕES DE VALIDAÇÃO
# ============================================================================

# Validar se arquivos existem antes de executar
VALIDATE_FILES = True

# Validar se ambiente virtual existe
VALIDATE_VENV = True

# Mostrar créditos dos planners
SHOW_CREDITS = True

# ============================================================================
# CONFIGURAÇÕES DE LOG
# ============================================================================

# Nível de log (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = "INFO"

# Salvar logs em arquivo
SAVE_LOGS = False
LOG_FILE = "planner.log"
