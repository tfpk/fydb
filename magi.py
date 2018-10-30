#!/usr/bin/python3
'''
Magi is a tool to help gdb beginners get accustomed to the environment.
It prints out information, and some helpful tips so beginners know where they are.
It also colorises gdb to make it more approachable.
'''

import gdb
import os
import re

from colorama import *

init()

MAGI_HEADER = f"{Fore.BLUE+Style.BRIGHT}[MAGI]{Style.RESET_ALL}:"
print(f"{MAGI_HEADER} Magi (alpha version) active. Disable with magi off")

class ScopeGuardToggle(gdb.Command):
    def __init__(self, name):
        super().__init__(name, gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        if arg.lower() in ["off", "false"]:
            gdb.sg_active = False
            print(f"{MAGI} Magi inactive.")
        elif arg.lower() in ["on", "true"]:
            gdb.sg_active = True
            print(f"{MAGI} Magi active.")
        else:
            print("magi used incorrectly. use magi [on/off]")

ScopeGuardToggle("magi")
