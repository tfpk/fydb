#!/usr/bin/python3
'''
Active comment allows gdb to automatically set breakpoints and provide information based on the content of files.
'''

import gdb
import os
import re

from colorama import *

init()

PROGRAM_HEADER = f"{Fore.RED+Style.BRIGHT}[ActiveComment]{Style.RESET_ALL}:"
# gdb exists even in events, so we assign globals there
gdb.ac_scanned_files = set()
gdb.sym_table_loaded = True

def get_user_source_files():
    LIST_SOURCES_CMD = "info sources"
    def filter_files(f):
        return not any([
            f == "",
            f.startswith("../sysdeps"),
            f.startswith("/usr/"),
            f.startswith("/build/"),
            ".so" in f[-6:],
            "system-suppplied" in f,
            *[f.endswith(x) for x in gdb.ac_scanned_files],
            *[f.endswith(x) for x in [".h", ".hpp", ".s"]]
        ])

    def filter_source_cmd(x):
        if x.strip() == "":
            return False
        if x.startswith("Source files"):
            return False
        return True

    try:
        sources = gdb.execute(LIST_SOURCES_CMD, to_string=True)
    except gdb.error as e:
        if "No symbol table" in str(e):
            print(f"{PROGRAM_HEADER} ActiveComment Disabled (no debug info): Did you compile with -g?")
            gdb.sym_table_loaded = False
            return []
    sources_cmd_lines = sources.split('\n')
    sources_cmd_lines = filter(filter_source_cmd, sources_cmd_lines)
    files_list = ','.join(sources_cmd_lines).replace(' ', '').split(',')
    files_list = filter(filter_files, files_list)

    return files_list


def get_source_lines():
    GET_SOURCE_CMD = "with listsize 0 -- l {f_name}:1,"
        
    SOURCE = {}

    for f in get_user_source_files():
        f_name = os.path.basename(f)
        f_base, f_ext = os.path.splitext(f_name)
        

        command = GET_SOURCE_CMD.format(f_name=f_name)
        source_file = gdb.execute(command, to_string=True)
        
        SOURCE[f_name] = []
        for line in source_file.split('\n'):
            if re.match(r'\d+\t.*', line):
                split_line = line.split('\t')
                SOURCE[f_name].append((int(split_line[0]), split_line[1]))

        # this prevents gdb from complaining when using l before run
        fix_line_nums = gdb.execute(f"l {f_name}:1", to_string=True)
    return SOURCE

def register_code_breaks(sources):
    SET_BREAK_CMD = "break {f_name}:{line}"
    SET_BREAK_COND_CMD = "break {f_name}:{line} if {cond}"

    BREAK_REGEX = r'//\s*b(?:reak)\s*$'
    BREAK_COND_REGEX = r'//\s*b(?:reak)\s*if\s*(?P<cond>.*)\s*$'
    
    for source_name, code in sources.items():
        for line_num, line in code:
            bp_set = None
            if re.search(BREAK_COND_REGEX, line):
                cond = re.search(BREAK_COND_REGEX, line).group('cond')
                command = SET_BREAK_COND_CMD.format(f_name=source_name, line=line_num, cond=cond)
                try:
                    bp_set = gdb.execute(command, to_string=True)
                except gdb.error as e:
                    if "No symbol" in str(e):
                        var = re.match(r"No symbol \"(.*)\"", str(e)).group(1)
                        e = f"Condition failed, variable {var} does not exist in code"
                    print(f"{PROGRAM_HEADER} Adding Condition failed: {e}.")

            if re.search(BREAK_REGEX, line):
                command = SET_BREAK_CMD.format(f_name=source_name, line=line_num)
                bp_set = gdb.execute(command, to_string=True)
            
            if bp_set and "No source file named" in bp_set:
                print(f"{PROGRAM_HEADER} Breakpoint could not be set. {source_name} not found.")
            elif bp_set:
                bp_info = f"{source_name}:{line_num}" 
                print(f"{PROGRAM_HEADER} Breakpoint Added {Style.BRIGHT}{bp_info}{Style.RESET_ALL}")
    gdb.ac_scanned_files |= set(sources.keys())
        

def on_new_objfile(event):
    sources = get_source_lines()
    register_code_breaks(sources)

"""
GDB Event: new_objfile

Whenever a new object file is registered, scan all loaded files to determine if any
user made c files should be scanned for breakpoints.

If scanned, they can contain either:
 - //break
 - //break if (condition == 1)

If they contain either, an appropriate breakpoint will be set.
"""
gdb.events.new_objfile.connect(on_new_objfile)

