import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
VENV_DIR = ROOT / '.venv'
LOGS_DIR = ROOT / 'logs'
LOG_FILE = LOGS_DIR / 'test_run.log'
CI_SCRIPT = ROOT / 'ci' / 'ci_pipeline.bat'
CD_SCRIPT = ROOT / 'cd' / 'cd_pipeline.bat'
REQUIREMENTS = ROOT / 'requirements.txt'
README = ROOT / 'README.md'


def run(cmd, cwd=None, env=None):
    # Run a command (cmd as string) with shell=True and return CompletedProcess
    return subprocess.run(cmd, cwd=cwd, env=env, shell=True)


def ensure_logs():
    LOGS_DIR.mkdir(exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text('')


def recreate_venv():
    # Avoid deleting the running interpreter if the script is executed inside .venv
    try:
        current = Path(sys.executable).resolve()
        if VENV_DIR.resolve() in current.parents:
            print('Refusing to recreate .venv while running inside it. Run this script with the system Python (outside .venv).')
            sys.exit(2)
    except Exception:
        pass

    if VENV_DIR.exists():
        # On Windows files in .venv can be locked; try rmtree with an onerror handler
        def on_rm_error(func, path, exc_info):
            try:
                os.chmod(path, 0o700)
                func(path)
            except Exception:
                pass
        try:
            shutil.rmtree(VENV_DIR, onerror=on_rm_error)
        except Exception:
            # final attempt using system commands
            if os.name == 'nt':
                subprocess.run(f'rmdir /S /Q "{str(VENV_DIR)}"', shell=True)
            else:
                subprocess.run(f'rm -rf "{str(VENV_DIR)}"', shell=True)
    print(f"Creating virtualenv at {VENV_DIR}")
    # If we are running under a python executable that might be part of an existing .venv,
    # prefer the 'py -3' launcher on Windows to create the new venv with the system Python.
    if os.name == 'nt' and 'venv' in str(sys.executable).lower():
        cmd = ['py', '-3', '-m', 'venv', str(VENV_DIR)]
    else:
        cmd = [sys.executable, '-m', 'venv', str(VENV_DIR)]
    subprocess.check_call(cmd)


def install_requirements(pip_path):
    print('Installing requirements...')
    return run(f'"{pip_path}" install -r "{REQUIREMENTS}"')


def run_pipeline(script_path, workdir, env):
    print(f'Running pipeline: {script_path} (cwd={workdir})')
    return run(f'"{script_path}"', cwd=workdir, env=env)


def append_readme(python_path, pip_path):
    python_version = subprocess.run(f'"{python_path}" --version', shell=True, capture_output=True, text=True).stdout.strip()
    pip_version = subprocess.run(f'"{pip_path}" --version', shell=True, capture_output=True, text=True).stdout.strip()
    env_name = '.venv'
    abs_path = str(ROOT)
    content = f"\nEnvironment: {env_name}\nPath: {abs_path}\n{python_version}\n{pip_version}\n"
    with open(README, 'a', encoding='utf-8') as f:
        f.write(content)


def main():
    ensure_logs()

    # recreate venv
    recreate_venv()

    # determine paths
    if os.name == 'nt':
        scripts_dir = VENV_DIR / 'Scripts'
        py = scripts_dir / 'python.exe'
        pip = scripts_dir / 'pip.exe'
    else:
        scripts_dir = VENV_DIR / 'bin'
        py = scripts_dir / 'python'
        pip = scripts_dir / 'pip'

    if not py.exists():
        print('ERROR: Python executable not found in venv', file=sys.stderr)
        sys.exit(2)

    # Install requirements into venv
    res = install_requirements(str(pip))
    if res.returncode != 0:
        print('requirements installation failed')
        sys.exit(res.returncode)

    # Prepare env with venv at front of PATH
    env = os.environ.copy()
    env['PATH'] = str(scripts_dir) + os.pathsep + env.get('PATH', '')

    # Run CI
    ci_res = run_pipeline(str(CI_SCRIPT), str(CI_SCRIPT.parent), env)

    # Run CD only if CI succeeded
    cd_res = None
    if ci_res.returncode == 0:
        cd_res = run_pipeline(str(CD_SCRIPT), str(CD_SCRIPT.parent), env)

    # Evaluate success
    success = (ci_res.returncode == 0) and (cd_res is not None and cd_res.returncode == 0)

    # Append environment info to README.md
    append_readme(str(py), str(pip))

    # Log summary
    with open(LOG_FILE, 'a', encoding='utf-8') as lf:
        lf.write('\n--- AUTO TEST SUMMARY ---\n')
        lf.write(f"CI return code: {ci_res.returncode}\n")
        if cd_res is not None:
            lf.write(f"CD return code: {cd_res.returncode}\n")
        else:
            lf.write("CD was not run because CI failed.\n")
        lf.write(f"AUTO_TEST PASSED: {success}\n")

    if not success:
        print('AUTO_TEST FAILED. See logs/test_run.log for details')
        sys.exit(1)
    else:
        print('AUTO_TEST PASSED')
        sys.exit(0)


if __name__ == '__main__':
    main()
