#!/usr/bin/env python3
"""
==============================================================================
SISTEMA INTEGRADO DE PLANNERS PDDL
==============================================================================

Sistema unificado para execução de planners PDDL com configuração centralizada.

USO:
    python planner.py [opções] <planner> <domain> <problem> [formato]

OPÇÕES:
    --help, -h          Mostrar ajuda
    --list-planners     Listar planners disponíveis
    --list-domains      Listar domínios disponíveis  
    --list-problems     Listar problemas disponíveis
    --list-formats      Listar formatos disponíveis
    --config            Mostrar configuração atual
    --debug             Modo debug

EXEMPLOS:
    # Execução básica
    python planner.py fast-downward hospital 01
    
    # Com formato específico
    python planner.py mock hospital 02 raw
    
    # Salvar em arquivo
    python planner.py unified-planning hospital 01 save plano.txt
    
    # Listar opções
    python planner.py --list-planners

==============================================================================
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from settings import *


class PlannerSystem:
    """Sistema integrado de planners PDDL"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self):
        """Carrega configurações do settings.py"""
        return {
            'planners': PLANNERS,
            'domains': DOMAINS, 
            'problems': PROBLEMS,
            'formats': FORMATS,
            'default_planner': DEFAULT_PLANNER,
            'default_format': DEFAULT_FORMAT,
            'venv_path': VENV_PATH,
            'timeout': EXECUTION_TIMEOUT,
            'debug': DEBUG_MODE
        }
    
    def _print_colored(self, message, color="reset"):
        """Imprime mensagem colorida se suportado"""
        if color in COLORS:
            print(f"{COLORS[color]}{message}{COLORS['reset']}")
        else:
            print(message)
    
    def _validate_environment(self):
        """Valida se o ambiente está configurado corretamente"""
        if VALIDATE_VENV and not os.path.exists(self.config['venv_path']):
            self._print_colored(f"{SYMBOLS['error']} Ambiente virtual não encontrado: {self.config['venv_path']}", "error")
            self._print_colored("Execute: python3 -m virtualenv .venv && source .venv/bin/activate && pip install -r requirements.txt", "info")
            return False
        return True
    
    def _validate_files(self, domain_file, problem_file):
        """Valida se os arquivos existem"""
        if VALIDATE_FILES:
            if not os.path.exists(domain_file):
                self._print_colored(f"{SYMBOLS['error']} Domínio não encontrado: {domain_file}", "error")
                return False
            
            if not os.path.exists(problem_file):
                self._print_colored(f"{SYMBOLS['error']} Problema não encontrado: {problem_file}", "error")
                return False
        return True
    
    def list_planners(self):
        """Lista planners disponíveis"""
        self._print_colored(f"{SYMBOLS['info']} Planners Disponíveis:", "info")
        for key, config in self.config['planners'].items():
            default_mark = " (padrão)" if key == self.config['default_planner'] else ""
            print(f"  {key:<15} - {config['name']}{default_mark}")
            print(f"    {config['description']}")
    
    def list_domains(self):
        """Lista domínios disponíveis"""
        self._print_colored(f"{SYMBOLS['info']} Domínios Disponíveis:", "info")
        for key, config in self.config['domains'].items():
            print(f"  {key:<10} - {config['name']}")
            print(f"    {config['description']}")
            print(f"    Arquivo: {config['file']}")
    
    def list_problems(self):
        """Lista problemas disponíveis"""
        self._print_colored(f"{SYMBOLS['info']} Problemas Disponíveis:", "info")
        for key, config in self.config['problems'].items():
            print(f"  {key:<5} - {config['name']}")
            print(f"    {config['description']}")
            print(f"    Arquivo: {config['file']}")
    
    def list_formats(self):
        """Lista formatos disponíveis"""
        self._print_colored(f"{SYMBOLS['info']} Formatos Disponíveis:", "info")
        for key, config in self.config['formats'].items():
            default_mark = " (padrão)" if key == self.config['default_format'] else ""
            print(f"  {key:<10} - {config['name']}{default_mark}")
            print(f"    {config['description']}")
    
    def show_config(self):
        """Mostra configuração atual"""
        self._print_colored(f"{SYMBOLS['config']} Configuração Atual:", "info")
        print(f"  Planner padrão: {self.config['default_planner']}")
        print(f"  Formato padrão: {self.config['default_format']}")
        print(f"  Ambiente virtual: {self.config['venv_path']}")
        print(f"  Timeout: {self.config['timeout']}s")
        print(f"  Debug: {'Ativado' if self.config['debug'] else 'Desativado'}")
    
    def run_planner(self, planner_key, domain_key, problem_key, format_key="json", output_file=None):
        """Executa o planner com as configurações especificadas"""
        
        # Validar planner
        if planner_key not in self.config['planners']:
            self._print_colored(f"{SYMBOLS['error']} Planner inválido: {planner_key}", "error")
            return False
        
        # Validar domínio
        if domain_key not in self.config['domains']:
            self._print_colored(f"{SYMBOLS['error']} Domínio inválido: {domain_key}", "error")
            return False
        
        # Validar problema
        if problem_key not in self.config['problems']:
            self._print_colored(f"{SYMBOLS['error']} Problema inválido: {problem_key}", "error")
            return False
        
        # Validar formato
        if format_key not in self.config['formats']:
            self._print_colored(f"{SYMBOLS['error']} Formato inválido: {format_key}", "error")
            return False
        
        # Obter configurações
        planner_config = self.config['planners'][planner_key]
        domain_config = self.config['domains'][domain_key]
        problem_config = self.config['problems'][problem_key]
        format_config = self.config['formats'][format_key]
        
        # Construir caminhos dos arquivos
        domain_file = domain_config['file']
        problem_file = problem_config['file']
        
        # Validar ambiente e arquivos
        if not self._validate_environment():
            return False
        
        if not self._validate_files(domain_file, problem_file):
            return False
        
        # Construir comando
        cmd = planner_config['command'].copy()
        
        # Adicionar argumentos específicos do planner
        if planner_key == "mock":
            # Mock planner só precisa do arquivo de problema
            cmd.append(problem_file)
        else:
            # Outros planners precisam de domínio e problema
            cmd.extend([domain_file, problem_file])
        
        cmd.extend(planner_config['args'])
        
        # Adicionar argumentos de formato
        if format_config['raw_flag']:
            cmd.append("--raw")
        elif format_key == "save" and output_file:
            cmd.extend(["--output", output_file])
        
        # Executar
        self._print_colored(f"{SYMBOLS['running']} Executando planner...", "info")
        if self.config['debug']:
            self._print_colored(f"  Planner: {planner_config['name']}", "info")
            self._print_colored(f"  Domínio: {domain_config['name']} ({domain_file})", "info")
            self._print_colored(f"  Problema: {problem_config['name']} ({problem_file})", "info")
            self._print_colored(f"  Formato: {format_config['name']}", "info")
            if output_file:
                self._print_colored(f"  Arquivo: {output_file}", "info")
            self._print_colored(f"  Comando: {' '.join(cmd)}", "info")
        
        try:
            # Executar com ambiente virtual se necessário
            if planner_config['requires_venv']:
                full_cmd = ["bash", "-lc", f"source {self.config['venv_path']} && {' '.join(cmd)}"]
            else:
                full_cmd = cmd
            
            result = subprocess.run(
                full_cmd,
                cwd=os.getcwd(),
                timeout=self.config['timeout']
            )
            
            if result.returncode == 0:
                self._print_colored(f"{SYMBOLS['success']} Execução concluída com sucesso!", "success")
                return True
            else:
                self._print_colored(f"{SYMBOLS['error']} Erro na execução (código: {result.returncode})", "error")
                return False
                
        except subprocess.TimeoutExpired:
            self._print_colored(f"{SYMBOLS['error']} Timeout na execução ({self.config['timeout']}s)", "error")
            return False
        except Exception as e:
            self._print_colored(f"{SYMBOLS['error']} Erro: {e}", "error")
            return False


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Sistema Integrado de Planners PDDL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Opções de listagem
    parser.add_argument("--list-planners", action="store_true", help="Listar planners disponíveis")
    parser.add_argument("--list-domains", action="store_true", help="Listar domínios disponíveis")
    parser.add_argument("--list-problems", action="store_true", help="Listar problemas disponíveis")
    parser.add_argument("--list-formats", action="store_true", help="Listar formatos disponíveis")
    parser.add_argument("--config", action="store_true", help="Mostrar configuração atual")
    parser.add_argument("--debug", action="store_true", help="Ativar modo debug")
    
    # Argumentos posicionais
    parser.add_argument("planner", nargs="?", help="Planner a usar")
    parser.add_argument("domain", nargs="?", help="Domínio a usar")
    parser.add_argument("problem", nargs="?", help="Problema a usar")
    parser.add_argument("format", nargs="?", default="json", help="Formato de saída")
    parser.add_argument("output_file", nargs="?", help="Arquivo de saída (para formato 'save')")
    
    args = parser.parse_args()
    
    # Criar sistema
    system = PlannerSystem()
    
    # Ativar debug se solicitado
    if args.debug:
        system.config['debug'] = True
    
    # Processar opções de listagem
    if args.list_planners:
        system.list_planners()
        return
    
    if args.list_domains:
        system.list_domains()
        return
    
    if args.list_problems:
        system.list_problems()
        return
    
    if args.list_formats:
        system.list_formats()
        return
    
    if args.config:
        system.show_config()
        return
    
    # Verificar se argumentos necessários foram fornecidos
    if not args.planner or not args.domain or not args.problem:
        parser.print_help()
        print(f"\n{SYMBOLS['info']} Exemplos de uso:")
        print("  python planner.py fast-downward hospital 01")
        print("  python planner.py mock hospital 02 raw")
        print("  python planner.py unified-planning hospital 01 save plano.txt")
        return
    
    # Executar planner
    success = system.run_planner(
        args.planner,
        args.domain, 
        args.problem,
        args.format,
        args.output_file
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
