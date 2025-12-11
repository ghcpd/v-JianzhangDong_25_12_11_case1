@echo off
echo === CI PIPELINE START ===
python3 -m pip install -r requirements.txt
python3 -m pytest tests
echo === CI END ===
