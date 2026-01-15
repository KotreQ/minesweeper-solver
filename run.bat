@echo off
setlocal

echo Installing requirements...
python -m pip install -r "requirements.txt"

echo Running the Minesweeper game...
python -m minesweeper_game
