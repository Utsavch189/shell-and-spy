import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.

build_exe_options = {"packages": ["json","pymongo","dns","numpy","requests"]}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "shell",
    version = "0.1",
    description = "shell",
    options = {"build_exe": build_exe_options},
    executables = [Executable("shell.py", base='Console')]
)