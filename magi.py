#!/usr/bin/python3
'''
Magi is a tool to help gdb beginners get accustomed to the environment.
It prints out information, and some helpful tips so beginners know where they are.
It also colorises gdb to make it more approachable.
'''

import gdb
import os
import re
import string
import traceback

from colorama import *

init()
gdb.magi_active = True

MAGI_HEADER = f"{Fore.BLUE+Style.BRIGHT}[MAGI]{Style.RESET_ALL}:"
print(f"{MAGI_HEADER} Magi active. Disable with magi off")

START_PANEL = f"""{Fore.BLUE+Style.BRIGHT}[GETTING STARTED]{Style.RESET_ALL}
- Type {Style.DIM}r{Style.RESET_ALL} to start the program
- Type {Style.DIM}b function_name{Style.RESET_ALL} to schedule a stop at a function.
- Type {Style.DIM}tb file:line_num{Style.RESET_ALL} to schedule a stop in file at line_num.
"""
print(START_PANEL)

HELP_PANEL = f"""[SHORTCUT HINTS]
- {Style.DIM}info locals{Style.RESET_ALL}: list local vars
- {Style.DIM}p <var>{Style.RESET_ALL}: print value of var
- {Style.DIM}finish{Style.RESET_ALL}: go to end of func
- {Style.DIM}b <place>{Style.RESET_ALL} always stop here
- {Style.DIM}tb <place>{Style.RESET_ALL}: stop here once
- {Style.DIM}n{Style.RESET_ALL}: go to next line
- {Style.DIM}c{Style.RESET_ALL}: keep going til next break
|{Style.BRIGHT}<place> can be a:{Style.RESET_ALL}
- func name (e.g. main)       
- file:num (e.g. myfile.c:37) 
- +line (e.g. +1 = next line)"""
MAX_HELP_LEN = 30

PRINT_BEFORE = 4
PRINT_AFTER = 6


def get_num_ansi_chars(text):
    """
    Get the number of characters used to do ansi formatting.

    """
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    result = ansi_escape.sub('', text)
    return len(text) - len(result)

def ansi_ljust(text, width):
    return text.ljust(width + get_num_ansi_chars(text))


def get_gdb_lines(start, nlines):
    to_return = ""
    try:
        to_return = gdb.execute(f"with listsize {nlines} -- l {start},", to_string=True)
    except gdb.error as e:
        # cannot get lines
        return None

    # reset l so user can use it
    earlier = gdb.execute(f"l {start - PRINT_BEFORE}, {start - 1}", to_string=True)

    return to_return

def get_line_number(line):
    try:
        return int(line.split('\t')[0])
    except ValueError:
        return None

def get_info_prompt(line):
    cur_line_num = int(line)
    prompt = ""

    before_line = max(1, cur_line_num - PRINT_BEFORE)
    gdb_lines = get_gdb_lines(before_line, PRINT_BEFORE + PRINT_AFTER + 1)
    
    if gdb_lines is None:
        gdb_lines = [f"{Fore.RED}Could not get lines.{Style.RESET_ALL}"] + [""]*10
    else:
        gdb_lines = [f"[Code]"+" "*30] + gdb_lines.split("\n")

    help_panel_lines = HELP_PANEL.split('\n')

    is_title_line = True

    for help_panel_line, src_line in zip(help_panel_lines, gdb_lines):
        src_line_num = get_line_number(src_line)
        if src_line_num == cur_line_num:
            src_line = Style.BRIGHT + Fore.CYAN + src_line + Style.RESET_ALL
        if is_title_line:
            prompt += Back.BLUE

        prompt += f"{ansi_ljust(help_panel_line, 32)} {Style.DIM}|{Style.NORMAL} {src_line}"
        
        if is_title_line:
            prompt += Style.RESET_ALL
            is_title_line = False
        prompt += "\n"

    gdb_locals = gdb.execute("info locals", to_string=True).split('\n')
    
    return prompt

def make_prompt(s):
    return f"{Fore.WHITE+Style.BRIGHT}({Fore.BLUE}GDB @{Style.RESET_ALL} {s}{Style.BRIGHT+Fore.WHITE}){Style.RESET_ALL} "

def prompt(prev_prompt):
    if not gdb.magi_active:
        return prev_prompt
    try:
        frame = gdb.execute("frame", to_string=True)
    except gdb.error as e:
        return make_prompt(f"{Fore.BLUE}Not Started{Fore.RESET}")
    
    frame_re = r".* (?P<func>[\w_]*) \(.*\) at (?P<file>.*):(?P<line>\d*)"
    frame_match = re.match(frame_re, frame)
    if frame_match is None:
        return make_prompt(f"{Fore.RED}Unknown{Fore.RESET}")
    
    func = frame_match.group("func")
    f = frame_match.group("file")
    line = frame_match.group("line")
    
    old_prompt_line = prev_prompt.split('\n')[-1]
    new_prompt_line = make_prompt(f"{Fore.BLUE}{f}:{line} in {func}{Fore.RESET}")

    if old_prompt_line == new_prompt_line:
        return new_prompt_line
    
    return get_info_prompt(line) + '\n' + new_prompt_line


gdb.prompt_hook = prompt

class MagiToggle(gdb.Command):
    def __init__(self, name):
        super().__init__(name, gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        if arg.lower() in ["off", "false"]:
            gdb.magi_active = False
            print(f"{MAGI_HEADER} Magi inactive.")
        elif arg.lower() in ["on", "true"]:
            gdb.magi_active = True
            print(f"{MAGI_HEADER} Magi active.")
        else:
            print("magi used incorrectly. use magi [on/off]")

MagiToggle("magi")
