# coding=gbk
# pythonתexe�ű�
#
# ��װcx_Freeze
# ִ�� python convert2exe.py build
# ���Զ�����buildĿ¼, ���������ļ���������
#

import sys

from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

buildOptions = dict(
    compressed = True,
    include_files = ['calc.png', 'random.png', 'restart.png', '28.pzl', '100.pzl'])

setup(
        name = "Sudoku",
        version = "0.1",
        description = "Python Sudoku",
        options = dict(build_exe = buildOptions),
        executables = [Executable("SudokuApp.py", base = base)])

