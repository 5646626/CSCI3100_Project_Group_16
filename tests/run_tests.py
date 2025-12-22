#!/usr/bin/env python3
"""
Quick test runner script for CLI Kanban system.
Provides easy access to common testing commands.
"""
import sys
import subprocess
import os


def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n{'=' * 70}")
    print(f"  {description}")
    print(f"{'=' * 70}\n")
    # Use shell=True for simplicity since we're using platform-agnostic Python commands
    # All commands invoke Python which handles cross-platform execution
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def main():
    if len(sys.argv) < 2:
        print("""
CLI Kanban Test Runner
======================

Usage: python run_tests.py [command]

Commands:
    all           Run all tests
    service       Run service tests only (exclude integration/benchmarks)
    integration   Run integration tests only
    benchmarks    Run performance benchmarks
    coverage      Run tests with coverage report
    coverage-html Generate HTML coverage report
    auth          Run authentication tests
    board         Run board management tests
    task          Run task management tests
    licence       Run licence service tests
    search        Run search service tests
    quick         Quick test run (service tests only, no verbose)
  
Examples:
  python run_tests.py all
  python run_tests.py coverage
  python run_tests.py benchmarks
        """)
        return 0
    
    command = sys.argv[1].lower()
    
    # Change to project root (parent of tests/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
    os.chdir(project_root)

    # Ensure 'Software' directory is on PYTHONPATH so product code is importable
    software_dir = os.path.join(project_root, 'Software')
    if os.path.isdir(software_dir):
        existing_py_path = os.environ.get('PYTHONPATH', '')
        os.environ['PYTHONPATH'] = (
            software_dir + os.pathsep + existing_py_path
        ) if existing_py_path else software_dir
    else:
        print(f"Warning: Software directory not found at {software_dir}")
    
    # Use sys.executable to ensure we use the same Python interpreter
    # that's running this script (works on both Windows and Linux)
    python_cmd = sys.executable
    pytest_cfg = os.path.join('tests', 'pytest.ini')
    
    commands = {
        'all': (
            f'"{python_cmd}" -m pytest -c {pytest_cfg} tests/ -v',
            'Running all tests with verbose output'
        ),
        'service': (
            f'"{python_cmd}" -m pytest -c {pytest_cfg} tests/ -v -k "not integration and not benchmark"',
            'Running service tests only'
        ),
        'integration': (
            f'"{python_cmd}" -m pytest -c {pytest_cfg} tests/test_integration.py -v',
            'Running integration tests'
        ),
        'benchmarks': (
            f'"{python_cmd}" -m pytest -c {pytest_cfg} tests/test_benchmarks.py -v -s',
            'Running performance benchmarks'
        ),
        'coverage': (
            f'"{python_cmd}" -m pytest -c {pytest_cfg} --cov=services --cov=repositories --cov=models --cov-report=term-missing tests/',
            'Running tests with coverage report'
        ),
        'coverage-html': (
            f'"{python_cmd}" -m pytest -c {pytest_cfg} --cov=services --cov=repositories --cov=models --cov-report=html tests/',
            'Generating HTML coverage report (see htmlcov/index.html)'
        ),
        'auth': (
            f'"{python_cmd}" -m pytest -c {pytest_cfg} tests/test_auth_service.py -v',
            'Running authentication tests'
        ),
        'board': (
            f'"{python_cmd}" -m pytest -c {pytest_cfg} tests/test_board_service.py -v',
            'Running board management tests'
        ),
        'task': (
            f'"{python_cmd}" -m pytest -c {pytest_cfg} tests/test_task_service.py -v',
            'Running task management tests'
        ),
        'licence': (
            f'"{python_cmd}" -m pytest -c {pytest_cfg} tests/test_licence_service.py -v',
            'Running licence service tests'
        ),
        'search': (
            f'"{python_cmd}" -m pytest -c {pytest_cfg} tests/test_search_service.py -v',
            'Running search service tests'
        ),
        'quick': (
            f'"{python_cmd}" -m pytest -c {pytest_cfg} tests/ -k "not integration and not benchmark"',
            'Quick test run (service tests only)'
        )
    }
    
    if command not in commands:
        print(f"Error: Unknown command '{command}'")
        print("Run 'python run_tests.py' for usage information")
        return 1
    
    cmd, description = commands[command]
    return run_command(cmd, description)


if __name__ == '__main__':
    sys.exit(main())
