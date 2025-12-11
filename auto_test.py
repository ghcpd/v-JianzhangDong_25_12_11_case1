import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
venv_dir = root / '.venv'
logs_dir = root / 'logs'
logs_dir.mkdir(parents=True, exist_ok=True)
log_file = logs_dir / 'test_run.log'

# Use the virtualenv's Scripts on PATH so `python` and `pip` in the batch files resolve to the venv
if os.name == 'nt':
    venv_scripts = venv_dir / 'Scripts'
else:
    venv_scripts = venv_dir / 'bin'

if not venv_dir.exists():
    print("Virtual environment not found at .venv. Please create it before running this script.")
    sys.exit(2)

env = os.environ.copy()
env['PATH'] = str(venv_scripts) + os.pathsep + env.get('PATH', '')

# Ensure README exists (will be appended to below)
readme = root / 'README.md'
if not readme.exists():
    readme.write_text('# CI/CD Test Project\n')

# Start with a clean appended log header
with open(log_file, 'a', encoding='utf-8') as f:
    f.write('\n----- Running auto_test.py (begin) -----\n')

# Helper to run a batch file and append its output to the log
def run_pipeline(batch_path):
    batch_path = Path(batch_path)
    if not batch_path.exists():
        msg = f"Pipeline script not found: {batch_path}\n"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(msg)
        return 1

    # Use cmd.exe /c to run the batch in its directory
    proc = subprocess.run(["cmd.exe", "/c", str(batch_path.name)],
                          cwd=str(batch_path.parent),
                          env=env,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          text=True)

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(proc.stdout or '')
        f.write('\n')

    return proc.returncode

# Run CI then CD
ci_ret = run_pipeline(root / 'ci' / 'ci_pipeline.bat')
cd_ret = run_pipeline(root / 'cd' / 'cd_pipeline.bat')

# Append environment details to README.md
try:
    py_version = subprocess.run([str(venv_scripts / ('python.exe' if os.name=='nt' else 'python')), '--version'], capture_output=True, text=True).stdout.strip()
except Exception:
    py_version = 'unknown'

try:
    pip_version = subprocess.run([str(venv_scripts / ('pip.exe' if os.name=='nt' else 'pip')), '--version'], capture_output=True, text=True).stdout.strip()
except Exception:
    pip_version = 'unknown'

env_info = f"\nEnvironment: .venv\nPath: {str(venv_dir.resolve())}\n{py_version}\n{pip_version}\n"
with open(readme, 'a', encoding='utf-8') as f:
    f.write('\n' + env_info)

with open(log_file, 'a', encoding='utf-8') as f:
    f.write('----- Running auto_test.py (end) -----\n')

# Report final status
if ci_ret == 0 and cd_ret == 0:
    print('Both CI and CD pipelines completed successfully.')
    sys.exit(0)
else:
    print('One or more pipelines failed. See logs/test_run.log for details.')
    sys.exit(1)
