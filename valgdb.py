#!/usr/bin/python3
'''
'''

import gdb
import os
import re
import subprocess
import time
from colorama import *

init()

MAGI_HEADER = f"{Fore.MAGENTA+Style.BRIGHT}[ValGDB]{Style.RESET_ALL}:"
print(f"{MAGI_HEADER} Type 'valgdb' to turn on valgrind debugging!")

class ValGDB(gdb.Command):
    def __init__(self, name):
        super().__init__(name, gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        obj_files = gdb.objfiles()
        if len(obj_files) == 1:
            objfile = obj_files[0].filename
            gdb.vgdb_call = subprocess.Popen(["valgrind", "--tool=memcheck", "--vgdb=yes", "--vgdb-error=0", objfile])
            time.sleep(1)
            gdb.execute("target remote | vgdb")
            gdb.execute("break main")
            gdb.execute("c")
        else:
            print(f"{MAGI_HEADER} Correct file could not be determined. Have you loaded a file yet?")

ValGDB("valgdb")
