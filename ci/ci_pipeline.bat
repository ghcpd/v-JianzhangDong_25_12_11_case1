@echo off
set LOG_FILE=..\logs\test_run.log
echo Running CI... > %LOG_FILE%

pip install -r ..\requirements.txt >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo CI failed. >> %LOG_FILE%
    exit /b 1
)

pytest ..\tests >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo CI failed. >> %LOG_FILE%
    exit /b 1
)

echo CI passed. >> %LOG_FILE%
exit /b 0
