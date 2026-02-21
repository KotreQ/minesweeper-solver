import os


__clear_cmd = "cls" if os.name == "nt" else "clear"

def clear_console():
    os.system(__clear_cmd)
