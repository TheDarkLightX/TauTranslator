#!/usr/bin/env python3

import subprocess
import os

# This script proves that the run_fsm_simulation.py script is fundamentally broken.
# Its success was an illusion caused by a bug in its output parsing.

TAU_EXECUTABLE = os.path.abspath("./.external_deps/tau-lang/build-Release/tau")

def flawed_run_tau_eval(logic_str):
    """
    This function replicates the flawed logic from run_fsm_simulation.py.
    It incorrectly parses the syntax error message as a valid '1' output.
    """
    command = [TAU_EXECUTABLE, "--evaluate", logic_str]
    print(f"\nRunning command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    print(f"Stdout from tau: {result.stdout.strip()}")
    print(f"Stderr from tau: {result.stderr.strip()}")

    # This is the flawed logic from the original script
    is_one = "1" in result.stdout
    print(f"Does stdout contain '1'? {is_one}")
    
    final_result = "1" if is_one else "0"
    print(f"Flawed function returns: {final_result}")
    return final_result

print("--- PROOF OF FLAWED LOGIC IN run_fsm_simulation.py ---")
# This command is known to fail with a syntax error.
# The error message contains the digit '1' (for the line number).
failing_command = "a := 0 . n a"
print(f"Testing with known-failing command: '{failing_command}'")
output = flawed_run_tau_eval(failing_command)

print("\n--- CONCLUSION ---")
if output == "1":
    print("Hypothesis CONFIRMED. The original script is broken and misinterprets syntax errors as success.")
else:
    print("Hypothesis REJECTED. My understanding is still flawed.")
