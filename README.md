# Minesweeper Solver

A ~~reckless~~ **clever** bot that plays Minesweeper so you don’t have to.  
Point it at a board, grab a coffee, and watch it crunch probabilities.

---

## 🚀 Features

- Automatic solving of standard Minesweeper boards.
- Playable game mode with the same logic engine under the hood.
- Pluggable solving strategies so you can experiment with new ideas.
- Clear separation between **solver** and **game** modules.

---

## Getting Started

### Prerequisites

- Python 3.10+

Installing requirements:
```bash
pip install -r requirements.txt
```

## Running

To run the solver:
```bash
python -m solver
```

To run the game:
```bash
python -m game
```

## 💡 TODO List:
- Find where tile's surroundings are a subset of another one's and adjust mine constraints accordingly
