> And the star they had seen in the east went ahead of them until it stopped over the place where the child was.
>
> (Matthew 2:9)

# GDB Tools

GDB is a daunting environment for new programmers. It requires understanding a lot of history, as well as remembering multiple commands and new concepts (breaks, frames, etc.).
The tools in this repo all serve to help lessen the strain on those programmers.

## Disclaimer

These tools are designed for Linux, and specifically for the UNSW CSE environment. They may work on other systems, but no guarantees are made about their usefulness.

## Magi

The centerpiece of these tools, Magi aims to give constant helpful information to the user, including the current state of the program, and what commands to run.


## ScopeGuard

One of the big issues in using GDB is dealing with frames that lead to unintelligble places. ScopeGuard automatically stops breaks or signals from dropping the user below their code.
The user can still use up/down if necessary, but they are automatically dropped into the most useful frame.

## ActiveComment

A feature designed for both new and old users, often we want to maintain breakpoints between runs, and we don't want to have to remember files or lines in which breaks occur.
ActiveComment allows the comment `//b` or `//break if (cond)` to automatically create breakpoints in files. This massively simplifies the process of debugging.

## ValGDB

Primarily for older users, this allows you to setup a debugger on valgrind. It may help decipher memory errors.
To use, just run `valgdb` inside `gdb ./program`. The program will start inside valgrind.

## Installation

To install these programs, use this one liner:
```bash
echo "Command not ready yet."
```

