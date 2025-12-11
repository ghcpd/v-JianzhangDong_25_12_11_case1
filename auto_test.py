import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent.resolve()
VENV = ROOT / ".venv"
TMP_VENV = ROOT / ".venv_tmp"
LOGS = ROOT / "logs"
LOG_FILE = LOGS / "test_run.log"


def run(cmd, env=None, cwd=None, logfile=None):
    proc = subprocess.run(cmd, shell=True, env=env, cwd=cwd, capture_output=True, text=True)
    out = proc.stdout or ""
    if logfile:
        logfile.write(out)
    else:
        print(out)
    if proc.stderr:
        if logfile:
            logfile.write(proc.stderr)
        else:
            print(proc.stderr)
    return proc.returncode


def recreate_venv(logfile):
    """Create a fresh venv. If this script is running from inside `VENV`, create
    and use a temporary venv (`.venv_tmp`) instead, since the running interpreter
    cannot delete itself."""

    current_py = Path(sys.executable).resolve()
    use_tmp = VENV in current_py.parents

    target = TMP_VENV if use_tmp else VENV

    if target.exists():
        shutil.rmtree(target)
        logfile.write(f"Removed existing {target}\n")

    logfile.write(f"Creating venv at {target}\n")
    rc = subprocess.call([sys.executable, "-m", "venv", str(target)])
    if rc != 0:
        logfile.write("Failed to create virtualenv\n")
        return rc

    pip = target / "Scripts" / "pip.exe"
    logfile.write("Installing requirements...\n")
    rc = subprocess.call([str(pip), "install", "-r", str(ROOT / "requirements.txt")], stdout=logfile, stderr=logfile)
    if rc != 0:
        logfile.write("Failed to install requirements\n")
        return rc

    # Create small shims in the venv Scripts dir to guarantee the venv's python is used
    scripts_dir = target / "Scripts"
    pytest_shim = scripts_dir / "pytest.bat"
    try:
        with pytest_shim.open("w", encoding="utf-8") as f:
            f.write("@echo off\n\"%~dp0\\python.exe\" -m pytest %*\n")
        logfile.write(f"Wrote pytest shim at {pytest_shim}\n")
    except Exception as e:
        logfile.write(f"Failed to write pytest shim: {e}\n")

    # Ensure fake deploy folder exists for CD pipeline
    fake_deploy = Path("C:/FakeDeployFolder")
    if not fake_deploy.exists():
        try:
            fake_deploy.mkdir(parents=True, exist_ok=True)
            logfile.write(f"Created fake deploy folder at {fake_deploy}\n")
        except Exception as e:
            logfile.write(f"Failed to create fake deploy folder: {e}\n")

    # Return the path to the venv that should be used for testing
    return target


def run_pipeline(script_path, logfile, venv_path):
    env = os.environ.copy()
    # Construct a minimal PATH that prefers the venv and keeps essential Windows locations
    essential = ["C:\\Windows\\system32", "C:\\Windows", "C:\\Windows\\System32\\Wbem", "C:\\Windows\\System32\\WindowsPowerShell\\v1.0"]
    env['PATH'] = os.pathsep.join([str(venv_path / 'Scripts')] + essential)
    # Prevent pytest from auto-loading plugins from the global environment
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    # Point PYTHONPATH to the venv site-packages so the venv packages are preferred
    site_packages = venv_path / "Lib" / "site-packages"
    env["PYTHONPATH"] = str(site_packages)

    logfile.write(f"PATH used: {env['PATH']}\n")
    # Log which python/pip/pytest executables will be resolved
    run("where python", env=env, cwd=str(ROOT), logfile=logfile)
    run("where pip", env=env, cwd=str(ROOT), logfile=logfile)
    run("where pytest", env=env, cwd=str(ROOT), logfile=logfile)

    logfile.write(f"Running {script_path} with PATH {env['PATH']}\n")
    # Run the batch file with its own directory as CWD so relative paths work as intended
    script_dir = Path(script_path).parent
    cwd = str(ROOT / script_dir)
    rc = run(f"cmd /c {script_path}", env=env, cwd=cwd, logfile=logfile)
    logfile.write(f"{script_path} exit code: {rc}\n")
    return rc


def append_env_info(logfile, venv_path):
    python_bin = venv_path / "Scripts" / "python.exe"
    pip_bin = venv_path / "Scripts" / "pip.exe"
    py_ver = subprocess.check_output([str(python_bin), "--version"], text=True).strip()
    pip_ver = subprocess.check_output([str(pip_bin), "--version"], text=True).strip()
    info = f"Environment: {venv_path.name}\nPath: {venv_path.resolve()}\n{py_ver}\n{pip_ver}\n"
    logfile.write("Appending environment info to README.md\n")
    readme = ROOT / "README.md"
    with readme.open("a", encoding="utf-8") as f:
        f.write("\n" + info + "\n")


def main():
    LOGS.mkdir(exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as logfile:
        logfile.write("=== Auto Test Run Start ===\n")

        venv_used = recreate_venv(logfile)
        if not venv_used:
            logfile.write("Environment setup failed.\n")
            sys.exit(1)

        rc_ci = run_pipeline("ci\\ci_pipeline.bat", logfile, venv_used)
        rc_cd = run_pipeline("cd\\cd_pipeline.bat", logfile, venv_used)

        append_env_info(logfile, venv_used)

        logfile.write("=== Auto Test Run End ===\n")

    if rc_ci == 0 and rc_cd == 0:
        print("Both pipelines succeeded")
        sys.exit(0)
    else:
        print("One or more pipelines failed (see logs/test_run.log)")
        sys.exit(2)


if __name__ == "__main__":
    main()
