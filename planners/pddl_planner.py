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
        """Check if Fast Downward is available (WSL or native)"""
        # Check WSL
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
        
        # Check native Windows
        fd_path = shutil.which("fast-downward.py")
        if fd_path:
            return True
        
        # Check if downward folder exists in common locations
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
        """Solve using Fast Downward"""
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = output_file or os.path.join(tmpdir, "plan.txt")
            
            # Convert Windows paths to WSL paths if using WSL
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
                # Convert paths for WSL
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
                
                # Fast Downward returns 0 on success
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
        except ImportError:
            return False, None, "unified-planning library not installed (try: pip install unified-planning)"
        
        try:
            # Disable credits output
            get_environment().credits_stream = None
            
            reader = PDDLReader()
            problem = reader.parse_problem(domain_file, problem_file)
            
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
            from pyperplan.pddl.parser import Parser
            
            # Parse domain and problem
            domain = Parser(domain_file).parse_domain()
            problem = Parser(problem_file).parse_problem(domain)
            
            # Get search and heuristic functions
            search_func = SEARCHES.get('astar')
            heuristic_class = HEURISTICS.get('hff')
            
            # Search for plan
            plan = search_plan(
                domain,
                problem,
                search_func,
                heuristic_class
            )
            
            if plan:
                # Convert to PDDL format
                plan_actions = []
                for action in plan:
                    action_str = f"({action.name}"
                    for sig in action.signature:
                        action_str += f" {sig[0]}"  # parameter name
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
        help='Output plan file (default: stdout)'
    )
    parser.add_argument(
        '--api',
        action='store_true',
        help='Output in API format (JSON)'
    )
    parser.add_argument(
        '--simple-api',
        action='store_true',
        help='Output in simple API format (compatible with mock planner)'
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
    
    # Only show planner info if not in simple-api mode
    if not args.simple_api:
        print(f"Using planner: {planner.planner_type}", file=sys.stderr)
    
    success, plan, error = planner.solve(
        args.domain,
        args.problem,
        args.output
    )
    
    if success:
        if args.simple_api or args.api:
            # Extract goal location from plan
            goal_location = None
            if plan:
                last_action = plan[-1]
                # Parse last action to get destination
                # Format: (navegar robo from to)
                parts = last_action.strip('()').split()
                if len(parts) >= 4:
                    goal_location = parts[3]
            
            if args.simple_api:
                # Simple API format (compatible with mock planner)
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
                
                destination_label = pretty_map.get(goal_location, goal_location.replace("_", " ")) if goal_location else None
                
                result = {
                    "task": "navigate",
                    "destination": goal_location,
                    "destination_label": destination_label
                }
                print(json.dumps(result, ensure_ascii=False))
            else:
                # Full API format
                result = {
                    "status": "success",
                    "planner": planner.planner_type,
                    "plan": plan,
                    "num_actions": len(plan) if plan else 0
                }
                if goal_location:
                    result["destination"] = goal_location
                
                print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if not args.output:
                print("; Plan found:")
                for action in plan:
                    print(action)
                print(f"; Plan length: {len(plan)}")
        
        return 0
    else:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

