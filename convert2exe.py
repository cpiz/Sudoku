# -*- coding: utf-8 -*-
# python转exe脚本
#
# 安装cx_Freeze
# 执行 python convert2exe.py build
# 将自动生成build目录, 其下所有文件都必须打包
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

