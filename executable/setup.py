import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.

build_exe_options = {"packages": ["os","rsa","json","socket","win32api","pymongo","pyasn1","dns","numpy","glob2","cv2"]}


# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "spy",
    version = "0.1",
    description = "spy",
    options = {"build_exe": build_exe_options},
    executables = [Executable("spy.py", base=base)]
)