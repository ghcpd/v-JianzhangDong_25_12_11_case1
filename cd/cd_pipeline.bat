@echo off
echo === CD PIPELINE START ===
xcopy app.py deploy\app.py /Y
python apps.py
echo === CD END ===
