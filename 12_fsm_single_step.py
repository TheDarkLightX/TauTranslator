#'/usr/bin/env python3

import subprocess
import os

# This script performs a single, correct step of the FSM simulation.
# It uses our new, definitive understanding of Tau syntax:
# - All definitions are zero-argument functions: `name() := ...`
# - Interaction happens via the REPL, not `--evaluate`.

TAU_EXECUTABLE = os.path.abspath("./.external_deps/tau-lang/build-Release/tau")

def run_repl_commands(commands):
    """Starts a tau REPL, feeds it commands, and returns the full stdout."""
    process = subprocess.Popen(
        [TAU_EXECUTABLE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1, # Line-buffered
        universal_newlines=True
    )
    stdout, stderr = process.communicate(input='\n'.join(commands) + '\n')
    return stdout, stderr

def parse_last_result(output):
    """Parses the last result from the REPL's stdout."""
    lines = [line.strip() for line in output.split('\n') if line.strip()]
    # The result is typically in the format '%1: 1' or '%1: 0'
    for line in reversed(lines):
        if line.startswith('%'):
            return line.split(':')[1].strip()
    return None

# --- FSM Logic for a single step ---
# Inputs for t=0
B0 = 1
B1 = 0

# Previous state (s_prev for t=0 is s0=0, s1=0)
S0_PREV = 0
S1_PREV = 0

# Convert FSM logic to Tau function definitions
fsm_definitions = [
    # Input definitions for current timestep
    f"b0() := {B0} .",
    f"b1() := {B1} .",
    
    # Previous state definitions
    f"s0_prev() := {S0_PREV} .",
    f"s1_prev() := {S1_PREV} .",

    # Next state logic (s0_next, s1_next)
    "s0_next() := (s0_prev() & s1_prev()' & b0()' & b1()') | (s0_prev() & s1_prev() & b0()' & b1()) .",
    "s1_next() := (s0_prev()' & s1_prev()' & b0()' & b1()) | (s0_prev()' & s1_prev() & b0()' & b1()') | (s0_prev() & s1_prev()' & b0()' & b1()) .",

    # Output logic (o0, o1)
    "o0() := (s0_prev()' & s1_prev() & b0()' & b1()') | (s0_prev() & s1_prev()' & b0()' & b1()') .",
    "o1() := (s0_prev() & s1_prev()' & b0()' & b1()) .",
]

# Commands to evaluate the outputs for the current step
evaluation_commands = [
    "n o0()",
    "n o1()",
    "n s0_next()",
    "n s1_next()"
]

# Run all definitions, then all evaluations
all_commands = fsm_definitions + evaluation_commands

print("--- Sending to REPL ---")
for cmd in all_commands:
    print(cmd)

stdout, stderr = run_repl_commands(all_commands)

print("\n--- Received from REPL ---")
print(f"Stdout:\n{stdout.strip()}")
if stderr.strip():
    print(f"Stderr:\n{stderr.strip()}")

print("\n--- CONCLUSION ---")
print("Single FSM step executed. Review stdout for evaluation results.")
