import subprocess
import sys
import os
import shutil

# Paths
workspace_path = r'd:\vscoderprojects\v-JianzhangDong_25_12_11_case1\grok-fast\v-JianzhangDong_25_12_11_case1'
venv_path = os.path.join(workspace_path, '.venv')
logs_path = os.path.join(workspace_path, 'logs')
log_file = os.path.join(logs_path, 'test_run.log')
readme_file = os.path.join(workspace_path, 'README.md')

# Ensure logs directory exists
os.makedirs(logs_path, exist_ok=True)

# Get venv python and pip
python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
pip_exe = os.path.join(venv_path, 'Scripts', 'pip.exe')

def run_command(command, log_file, description):
    with open(log_file, 'a') as f:
        f.write(f"Running {description}...\n")
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=workspace_path)
    with open(log_file, 'a') as f:
        f.write(result.stdout)
        if result.returncode != 0:
            f.write(f"{description} failed.\n")
        else:
            f.write(f"{description} passed.\n")
    return result.returncode == 0

# CI
ci_passed = True
ci_passed &= run_command(f'"{pip_exe}" install -r requirements.txt', log_file, 'CI install')
ci_passed &= run_command(f'"{python_exe}" -m pytest tests', log_file, 'CI test')

# CD
cd_passed = True
cd_passed &= run_command(f'"{python_exe}" setup.py sdist', log_file, 'CD build')
# Assume dist is created in workspace
dist_path = os.path.join(workspace_path, 'dist')
deploy_path = r'C:\FakeDeployFolder'
if os.path.exists(dist_path):
    # Copy files
    for file in os.listdir(dist_path):
        src = os.path.join(dist_path, file)
        dst = os.path.join(deploy_path, file)
        shutil.copy2(src, dst)
    with open(log_file, 'a') as f:
        f.write("CD deploy passed.\n")
else:
    cd_passed = False
    with open(log_file, 'a') as f:
        f.write("CD deploy failed: dist not found.\n")

# Check overall
test_passed = ci_passed and cd_passed

# Get versions
python_version = subprocess.run([python_exe, '--version'], capture_output=True, text=True).stdout.strip()
pip_version = subprocess.run([pip_exe, '--version'], capture_output=True, text=True).stdout.strip().split()[1]

# Append to README.md
with open(readme_file, 'a') as f:
    f.write(f"\nEnvironment Name: VirtualEnvironment\n")
    f.write(f"Absolute Path: {workspace_path}\n")
    f.write(f"Python Version: {python_version}\n")
    f.write(f"Pip Version: {pip_version}\n")

if test_passed:
    print("All tests passed.")
    sys.exit(0)
else:
    print("Some tests failed.")
    sys.exit(1)