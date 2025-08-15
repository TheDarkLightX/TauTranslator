#!/usr/bin/env python3

import subprocess
import os

# This script interacts with the Tau REPL to discover its available commands.

TAU_EXECUTABLE = os.path.abspath("./.external_deps/tau-lang/build-Release/tau")

def run_repl_commands(commands):
    """Starts a tau REPL, feeds it commands, and returns the full output."""
    process = subprocess.Popen(
        [TAU_EXECUTABLE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    input_str = "\n".join(commands) + "\n"
    print(f"--- Sending to REPL ---\n{input_str.strip()}")
    stdout, stderr = process.communicate(input=input_str)

    print(f"--- Received from REPL ---")
    print(f"Stdout: {stdout.strip()}")
    print(f"Stderr: {stderr.strip()}")
    return stdout, stderr

# This tests our new hypothesis based on the `help examples` output.
# We will define a zero-argument function and then evaluate it.
commands_to_run = [
    "my_const() := 1 .",
    "n my_const()"
]

stdout, stderr = run_repl_commands(commands_to_run)

print("\n--- CONCLUSION ---")
print("The 'help' command was executed. Please review the stdout for available commands.")
