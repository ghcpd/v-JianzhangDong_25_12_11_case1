@echo off
set LOG_FILE=..\logs\test_run.log
echo Running CD... >> %LOG_FILE%

python ..\setup.py sdist >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo CD failed. >> %LOG_FILE%
    exit /b 1
)

xcopy dist\* C:\FakeDeployFolder /s /y >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo CD failed. >> %LOG_FILE%
    exit /b 1
)

echo CD passed. >> %LOG_FILE%
exit /b 0
