import gdb
import os

fydb_folder = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
print(__file__)

FILES_TO_SOURCE = [
    "activecomment.py",
    "scopeguard.py",
    "valgdb.py",
    "magi.py",
]

for f in FILES_TO_SOURCE:
    path = os.path.join(fydb_folder, f)
    gdb.execute(f'source {path}')
