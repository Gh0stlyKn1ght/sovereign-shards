"""Application package for the J"""
from .file_tools import read_file, write_file, list_dir
from .system_tools import get_system_snapshot
#from .python_tools import run_python
#from .shell_tools import run_shell

TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_dir": list_dir,
    "system_snapshot": get_system_snapshot,
    #"run_python": run_python,
    #"run_shell": run_shell,
}

