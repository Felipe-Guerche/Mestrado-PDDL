#!/usr/bin/env python3
"""
PDDL Planner Wrapper - Supports multiple planners
Supports:
- Fast Downward (via WSL or native)
- Unified Planning (Python library)
- Pyperplan (Python fallback)
"""

import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import shutil


class PDDLPlanner:
    """Wrapper for PDDL planners with multiple backend support"""
    
    SUPPORTED_PLANNERS = ["fast-downward", "unified-planning", "pyperplan"]
    
    def __init__(self, planner_type: str = "auto"):
        """
        Initialize planner
        
        Args:
            planner_type: "fast-downward", "unified-planning", "pyperplan", or "auto"
        """
        self.planner_type = planner_type
        self.available_planners = self._detect_available_planners()
        
        if planner_type == "auto":
            self.planner_type = self._select_best_planner()
        elif planner_type not in self.available_planners:
            raise ValueError(
                f"Planner '{planner_type}' not available. "
                f"Available: {', '.join(self.available_planners)}"
            )
    
    def _detect_available_planners(self) -> List[str]:
        """Detect which planners are available"""
        available = []
        
        # Check for Fast Downward
        if self._check_fast_downward():
            available.append("fast-downward")
        
        # Check for Unified Planning
        try:
            import unified_planning
            available.append("unified-planning")
        except ImportError:
            pass
        
        # Check for Pyperplan
        try:
            import pyperplan
            available.append("pyperplan")
        except ImportError:
            pass
        
        return available
    
    def _check_fast_downward(self) -> bool:
        """Check if Fast Downward is available.

        Preference:
        1) Python engine via unified-planning (up_fast_downward)
        2) System binary (native/WSL)
        """
        # 1) Python engine via unified-planning
        try:
            # Importing registers the engine if installed
            import up_fast_downward  # type: ignore
            from unified_planning.shortcuts import OneshotPlanner
            try:
                with OneshotPlanner(name='fast-downward'):
                    return True
            except Exception:
                # Engine importable but not usable
                pass
        except Exception:
            pass

        # 2) Check system binary via WSL
        try:
            result = subprocess.run(
                ["wsl", "which", "fast-downward.py"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # 3) Check native binary in PATH
        fd_path = shutil.which("fast-downward.py")
        if fd_path:
            return True

        # 4) Common install locations
        common_paths = [
            Path.home() / "downward",
            Path("C:/downward"),
            Path("~/downward").expanduser(),
        ]
        for path in common_paths:
            if (path / "fast-downward.py").exists():
                return True

        return False
    
    def _select_best_planner(self) -> str:
        """Select the best available planner"""
        if not self.available_planners:
            raise RuntimeError(
                "No PDDL planner available. Please install one of: "
                "Fast Downward, unified-planning, or pyperplan"
            )
        
        # Preference order
        for preferred in ["fast-downward", "unified-planning", "pyperplan"]:
            if preferred in self.available_planners:
                return preferred
        
        return self.available_planners[0]
    
    def solve(
        self,
        domain_file: str,
        problem_file: str,
        output_file: Optional[str] = None
    ) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """
        Solve a PDDL problem
        
        Args:
            domain_file: Path to domain PDDL file
            problem_file: Path to problem PDDL file
            output_file: Optional path to save plan
        
        Returns:
            (success, plan_actions, error_message)
            plan_actions: List of action strings like "(navigate robo base farmacia)"
        """
        if self.planner_type == "fast-downward":
            return self._solve_fast_downward(domain_file, problem_file, output_file)
        elif self.planner_type == "unified-planning":
            return self._solve_unified_planning(domain_file, problem_file, output_file)
        elif self.planner_type == "pyperplan":
            return self._solve_pyperplan(domain_file, problem_file, output_file)
        else:
            return False, None, f"Unknown planner type: {self.planner_type}"
    
    def _solve_fast_downward(
        self,
        domain_file: str,
        problem_file: str,
        output_file: Optional[str]
    ) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """Solve using Fast Downward.

        Prefer the unified-planning engine (up_fast_downward). If not available,
        fall back to system binary (native/WSL).
        """
        # Try via unified-planning engine first
        try:
            from unified_planning.shortcuts import OneshotPlanner, get_environment
            from unified_planning.io import PDDLReader
            # Disable credits output
            get_environment().credits_stream = None

            # Read with UTF-8 and pass to UP reader to avoid encoding issues
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.pddl', delete=False) as temp_domain:
                with open(domain_file, 'r', encoding='utf-8') as df:
                    temp_domain.write(df.read())
                temp_domain_path = temp_domain.name
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.pddl', delete=False) as temp_problem:
                with open(problem_file, 'r', encoding='utf-8') as pf:
                    temp_problem.write(pf.read())
                temp_problem_path = temp_problem.name

            try:
                reader = PDDLReader()
                problem = reader.parse_problem(temp_domain_path, temp_problem_path)
                with OneshotPlanner(name='fast-downward') as planner:
                    result = planner.solve(problem)
                if result.status.name in ['SOLVED_SATISFICING', 'SOLVED_OPTIMALLY']:
                    plan = self._convert_up_plan_to_pddl(result.plan)
                    if output_file:
                        with open(output_file, 'w') as f:
                            f.write('\n'.join(plan))
                    return True, plan, None
                return False, None, f"No solution found: {result.status.name}"
            finally:
                try:
                    os.unlink(temp_domain_path)
                    os.unlink(temp_problem_path)
                except Exception:
                    pass
        except Exception:
            # If unified-planning engine not available, try system binary as fallback
            pass

        # Fallback: call system binary (native/WSL)
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = output_file or os.path.join(tmpdir, "plan.txt")

            use_wsl = False
            try:
                result = subprocess.run(
                    ["wsl", "which", "fast-downward.py"],
                    capture_output=True,
                    timeout=5
                )
                use_wsl = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

            if use_wsl:
                domain_wsl = self._windows_to_wsl_path(domain_file)
                problem_wsl = self._windows_to_wsl_path(problem_file)
                plan_wsl = self._windows_to_wsl_path(plan_file)
                cmd = [
                    "wsl",
                    "fast-downward.py",
                    domain_wsl,
                    problem_wsl,
                    "--search", "astar(lmcut())",
                    "--plan-file", plan_wsl
                ]
            else:
                cmd = [
                    "fast-downward.py",
                    domain_file,
                    problem_file,
                    "--search", "astar(lmcut())",
                    "--plan-file", plan_file
                ]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0 and os.path.exists(plan_file):
                    with open(plan_file, 'r') as f:
                        plan = self._parse_fast_downward_plan(f.read())
                    return True, plan, None
                else:
                    return False, None, f"Fast Downward failed: {result.stderr}"
            except subprocess.TimeoutExpired:
                return False, None, "Planner timeout (60s)"
            except Exception as e:
                return False, None, f"Error running Fast Downward: {str(e)}"
    
    def _solve_unified_planning(
        self,
        domain_file: str,
        problem_file: str,
        output_file: Optional[str]
    ) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """Solve using Unified Planning library"""
        try:
            from unified_planning.shortcuts import OneshotPlanner, get_environment
            from unified_planning.io import PDDLReader
            from unified_planning.model import Problem
        except ImportError:
            return False, None, "unified-planning library not installed (try: pip install unified-planning)"
        
        try:
            import tempfile
            import shutil
            
            # Disable credits output
            get_environment().credits_stream = None
            
            # Create temporary files with UTF-8 encoding
            # This solves Windows encoding issues
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.pddl', delete=False) as temp_domain:
                with open(domain_file, 'r', encoding='utf-8') as df:
                    temp_domain.write(df.read())
                temp_domain_path = temp_domain.name
            
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.pddl', delete=False) as temp_problem:
                with open(problem_file, 'r', encoding='utf-8') as pf:
                    temp_problem.write(pf.read())
                temp_problem_path = temp_problem.name
            
            try:
                reader = PDDLReader()
                problem = reader.parse_problem(temp_domain_path, temp_problem_path)
            
                # Try with pyperplan engine (native Python)
                with OneshotPlanner(name='pyperplan') as planner:
                    result = planner.solve(problem)
                    
                    if result.status.name in ['SOLVED_SATISFICING', 'SOLVED_OPTIMALLY']:
                        plan = self._convert_up_plan_to_pddl(result.plan)
                        
                        if output_file:
                            with open(output_file, 'w') as f:
                                f.write('\n'.join(plan))
                        
                        return True, plan, None
                    else:
                        return False, None, f"No solution found: {result.status.name}"
            finally:
                # Clean up temporary files
                try:
                    os.unlink(temp_domain_path)
                    os.unlink(temp_problem_path)
                except:
                    pass
        
        except Exception as e:
            import traceback
            return False, None, f"Error with unified-planning: {str(e)}\n{traceback.format_exc()}"
    
    def _solve_pyperplan(
        self,
        domain_file: str,
        problem_file: str,
        output_file: Optional[str]
    ) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """Solve using Pyperplan"""
        try:
            import pyperplan
        except ImportError:
            return False, None, "pyperplan library not installed (try: pip install pyperplan)"
        
        try:
            from pyperplan.planner import search_plan, SEARCHES, HEURISTICS
            
            # Get search and heuristic functions
            search_func = SEARCHES.get('astar')
            heuristic_class = HEURISTICS.get('hff')
            
            # pyperplan.search_plan expects file paths (domain, problem)
            plan = search_plan(
                domain_file,
                problem_file,
                search_func,
                heuristic_class
            )
            
            if plan:
                # Convert to PDDL-like action strings
                plan_actions = []
                for action in plan:
                    action_str = f"({getattr(action, 'name', 'action')}"
                    # Try common attribute names for parameters in pyperplan
                    params = []
                    if hasattr(action, 'args') and action.args is not None:
                        params = [str(p) for p in action.args]
                    elif hasattr(action, 'parameters') and action.parameters is not None:
                        params = [str(p) for p in action.parameters]
                    elif hasattr(action, 'signature') and action.signature is not None:
                        # Fallback: original (older custom structure)
                        params = [str(sig[0]) for sig in action.signature]
                    for p in params:
                        action_str += f" {p}"
                    action_str += ")"
                    plan_actions.append(action_str)
                
                if output_file:
                    with open(output_file, 'w') as f:
                        f.write('\n'.join(plan_actions))
                
                return True, plan_actions, None
            else:
                return False, None, "No solution found"
        
        except Exception as e:
            import traceback
            return False, None, f"Error with pyperplan: {str(e)}\n{traceback.format_exc()}"
    
    def _parse_fast_downward_plan(self, plan_text: str) -> List[str]:
        """Parse Fast Downward plan output"""
        plan = []
        for line in plan_text.strip().split('\n'):
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith(';'):
                plan.append(line)
        return plan
    
    def _convert_up_plan_to_pddl(self, up_plan) -> List[str]:
        """Convert Unified Planning plan to PDDL action strings"""
        plan = []
        for action in up_plan.actions:
            # Convert action to PDDL string format
            action_str = f"({action.action.name}"
            for param in action.actual_parameters:
                action_str += f" {param}"
            action_str += ")"
            plan.append(action_str)
        return plan
    
    def _windows_to_wsl_path(self, windows_path: str) -> str:
        """Convert Windows path to WSL path"""
        path = Path(windows_path).resolve()
        path_str = str(path)
        
        # Convert C:\Users\... to /mnt/c/Users/...
        if path_str[1] == ':':
            drive = path_str[0].lower()
            rest = path_str[2:].replace('\\', '/')
            return f"/mnt/{drive}{rest}"
        
        return path_str.replace('\\', '/')


def main():
    """CLI interface for the planner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PDDL Planner Wrapper')
    parser.add_argument('domain', nargs='?', help='Domain PDDL file')
    parser.add_argument('problem', nargs='?', help='Problem PDDL file')
    parser.add_argument(
        '--planner',
        choices=['auto', 'fast-downward', 'unified-planning', 'pyperplan'],
        default='auto',
        help='Planner to use (default: auto-detect)'
    )
    parser.add_argument(
        '--output',
        help='Optional: save full plan (one action per line) to this file'
    )
    parser.add_argument(
        '--raw',
        action='store_true',
        help='Output raw PDDL plan (one action per line) instead of JSON'
    )
    parser.add_argument(
        '--list-planners',
        action='store_true',
        help='List available planners and exit'
    )
    
    args = parser.parse_args()
    
    # Handle --list-planners early
    if args.list_planners:
        planner = PDDLPlanner(args.planner)
        print(f"Active planner: {planner.planner_type}")
        print(f"Available planners: {', '.join(planner.available_planners)}")
        return 0
    
    # Check required arguments
    if not args.domain or not args.problem:
        parser.error("domain and problem are required (unless using --list-planners)")
    
    planner = PDDLPlanner(args.planner)
    
    success, plan, error = planner.solve(
        args.domain,
        args.problem,
        args.output
    )
    
    if success:
        # Optionally: write full plan to file if requested
        if args.output and plan:
            with open(args.output, 'w') as f:
                f.write('\n'.join(plan))

        if args.raw:
            # Raw PDDL plan output
            if plan:
                for action in plan:
                    print(action)
        else:
            # Default: emit SIMPLE per-step JSON to stdout
            pretty_map = {
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

            def _extract_dest(action_str: str) -> Optional[str]:
                s = action_str.strip()
                while s.startswith('(') and s.endswith(')'):
                    inner = s[1:-1].strip()
                    if not inner or inner.startswith('(') and inner.endswith(')'):
                        s = inner
                    else:
                        s = '(' + inner + ')'
                        break
                parts = s.strip('()').split()
                if len(parts) >= 4:
                    return parts[3]
                return None

            if plan:
                for act in plan:
                    dest = _extract_dest(act)
                    if not dest:
                        continue
                    destination_label = pretty_map.get(dest, dest.replace('_', ' '))
                    result = {
                        "task": "navigate",
                        "destination": dest,
                        "destination_label": destination_label,
                    }
                    print(json.dumps(result, ensure_ascii=False))
        return 0
    else:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

