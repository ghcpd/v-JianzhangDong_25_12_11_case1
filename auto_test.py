#!/usr/bin/env python
"""
Auto test script for CI/CD pipeline validation.
This script runs the CI and CD pipelines using the virtual environment
and logs all output to logs/test_run.log.
"""

import subprocess
import sys
import os
from pathlib import Path

def get_environment_info():
    """Get Python environment information."""
    python_version = sys.version.split()[0]
    python_executable = sys.executable
    
    # Get pip version
    try:
        pip_version = subprocess.check_output(
            [sys.executable, "-m", "pip", "--version"],
            text=True
        ).strip()
    except Exception as e:
        pip_version = f"Error: {str(e)}"
    
    return {
        "python_executable": python_executable,
        "python_version": python_version,
        "pip_version": pip_version,
        "absolute_path": os.getcwd()
    }

def run_ci_pipeline(log_file):
    """Run the CI pipeline."""
    print("Running CI pipeline...")
    try:
        # Create a wrapper batch script that activates venv and runs ci_pipeline.bat
        venv_activate = os.path.join(os.getcwd(), ".venv", "Scripts", "activate.bat")
        
        # Run from ci directory with activated venv
        batch_script = f'@echo off\ncall "{venv_activate}"\nci_pipeline.bat'
        
        result = subprocess.run(
            batch_script,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.join(os.getcwd(), "ci")
        )
        
        # Append output to log file
        with open(log_file, "a") as f:
            f.write(result.stdout)
            if result.stderr:
                f.write(result.stderr)
        
        if result.returncode != 0:
            print(f"CI Pipeline Error (exit code {result.returncode}):")
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"Error running CI pipeline: {str(e)}\n")
        print(f"Exception in CI pipeline: {str(e)}")
        return False

def run_cd_pipeline(log_file):
    """Run the CD pipeline."""
    print("Running CD pipeline...")
    try:
        # Create a wrapper batch script that activates venv and runs cd_pipeline.bat
        venv_activate = os.path.join(os.getcwd(), ".venv", "Scripts", "activate.bat")
        
        # Run from cd directory with activated venv
        batch_script = f'@echo off\ncall "{venv_activate}"\ncd_pipeline.bat'
        
        result = subprocess.run(
            batch_script,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.join(os.getcwd(), "cd")
        )
        
        # Append output to log file
        with open(log_file, "a") as f:
            f.write(result.stdout)
            if result.stderr:
                f.write(result.stderr)
        
        if result.returncode != 0:
            print(f"CD Pipeline Error (exit code {result.returncode}):")
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"Error running CD pipeline: {str(e)}\n")
        print(f"Exception in CD pipeline: {str(e)}")
        return False

def append_to_readme(env_info):
    """Append environment information to README.md."""
    readme_path = Path("README.md")
    
    # Create or append to README
    content = f"""# CI/CD Test Project

## Environment Information
- **Environment Name**: .venv
- **Absolute Path**: {env_info['absolute_path']}
- **Python Executable**: {env_info['python_executable']}
- **Python Version**: {env_info['python_version']}
- **Pip Information**: {env_info['pip_version']}

## Project Structure
- `apps/`: Application modules (calc.py, string_utils.py)
- `tests/`: Unit tests for the application
- `ci/`: Continuous Integration pipeline
- `cd/`: Continuous Deployment pipeline
- `logs/`: Test execution logs
- `.venv/`: Python virtual environment
"""
    
    with open(readme_path, "w") as f:
        f.write(content)
    
    print(f"Updated README.md with environment information")

def main():
    """Main entry point."""
    # Get workspace root directory
    workspace_root = Path(__file__).parent
    os.chdir(workspace_root)
    
    # Ensure logs directory exists
    logs_dir = workspace_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    log_file = logs_dir / "test_run.log"
    
    # Get environment info
    env_info = get_environment_info()
    
    print(f"Python Version: {env_info['python_version']}")
    print(f"Python Executable: {env_info['python_executable']}")
    print(f"Working Directory: {env_info['absolute_path']}")
    print(f"Log File: {log_file}")
    print()
    
    # Clear log file
    with open(log_file, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("AUTO TEST EXECUTION LOG\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Environment: .venv\n")
        f.write(f"Absolute Path: {env_info['absolute_path']}\n")
        f.write(f"Python Executable: {env_info['python_executable']}\n")
        f.write(f"Python Version: {env_info['python_version']}\n")
        f.write(f"{env_info['pip_version']}\n")
        f.write("\n" + "=" * 80 + "\n\n")
    
    # Run pipelines
    ci_passed = run_ci_pipeline(log_file)
    cd_passed = run_cd_pipeline(log_file)
    
    # Append environment info to README
    append_to_readme(env_info)
    
    # Write final results to log
    with open(log_file, "a") as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write("TEST SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"CI Pipeline: {'PASSED' if ci_passed else 'FAILED'}\n")
        f.write(f"CD Pipeline: {'PASSED' if cd_passed else 'FAILED'}\n")
        f.write(f"Overall Result: {'ALL TESTS PASSED' if (ci_passed and cd_passed) else 'TESTS FAILED'}\n")
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"CI Pipeline: {'PASSED' if ci_passed else 'FAILED'}")
    print(f"CD Pipeline: {'PASSED' if cd_passed else 'FAILED'}")
    print(f"Overall Result: {'ALL TESTS PASSED' if (ci_passed and cd_passed) else 'TESTS FAILED'}")
    print("=" * 80)
    
    # Return exit code
    return 0 if (ci_passed and cd_passed) else 1

if __name__ == "__main__":
    sys.exit(main())
