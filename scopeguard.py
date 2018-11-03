
#!/usr/bin/python3
'''
Active comment allows gdb to automatically set breakpoints and provide information based on the content of files.
'''

import gdb
import os
import re

from colorama import *

init()

gdb.sg_active = True

SCOPE_HEADER = f"{Fore.GREEN+Style.BRIGHT}[ScopeGuard]{Style.RESET_ALL}:"

print(f"{SCOPE_HEADER} ScopeGuard active. Disable with sg off")

def is_local_path(f):
    return not any([
        f is None,
        f == "",
        f.startswith("../sysdeps"),
        f.startswith("/usr/"),
        f.startswith("/build/"),
        ".so" in f[-6:],
        "system-suppplied" in f,
    ])

def on_break(event):
    if not gdb.sg_active:
        return
    local_frames = []
    local_frame_info = []
    
    other_frames = []
    
    frame_num = 1
    lowest_frame = 0
    cur_frame = gdb.newest_frame()
    while cur_frame is not None:
        frame_function = cur_frame.function()
        if frame_function is None:
            print(f"{SCOPE_HEADER} Did you not include debug information in your files?")
            break
        frame_file = frame_function.name
        frame_path = frame_function.symtab.fullname()
        frame_line = frame_function.line
        
        frame_num += 1

        if is_local_path(frame_path):
            local_frames.append(cur_frame)
            frame_info = f"{frame_file}({frame_function}:{frame_line})"
            local_frame_info.append((frame_num, frame_info))
        else:
            other_frames.append(cur_frame)
        
        if len(local_frames) == 0:
            lowest_frame += 1
        
        cur_frame = cur_frame.older()
        
    if local_frames:
        local_frames[0].select()
    else:
        print(f"{SCOPE_HEADER} Could not find a local frame!")
        return

    if lowest_frame > 0:
        gdb.execute(f"up {lowest_frame}")
        print(f"{SCOPE_HEADER} Skipped over {lowest_frame} frames to show your function.")
        if len(local_frames) > 1:
            print(f"{SCOPE_HEADER} Use {Style.DIM}f <number>{Style.RESET_ALL} to inspect that function:")
            for f_num, f_info in local_frame_info:
                print(f"{SCOPE_HEADER} {Style.DIM}f {f_num}{Style.RESET_ALL} | {f_info}")


gdb.events.stop.connect(on_break)

class ScopeGuardToggle(gdb.Command):
    def __init__(self, name):
        super().__init__(name, gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        if arg.lower() in ["off", "false"]:
            gdb.sg_active = False
            print(f"{SCOPE_HEADER} ScopeGuard inactive.")
        elif arg.lower() in ["on", "true"]:
            gdb.sg_active = True
            print(f"{SCOPE_HEADER} ScopeGuard active.")
        else:
            print("scopeguard used incorrectly. use sg [on/off]")

ScopeGuardToggle("sg")
