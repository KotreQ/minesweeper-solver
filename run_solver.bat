@echo off
setlocal

echo Installing requirements...
python -m pip install -r "requirements.txt"

echo Running the Minesweeper solver...
python -m solver
