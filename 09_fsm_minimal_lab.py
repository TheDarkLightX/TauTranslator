#!/usr/bin/env python3

import subprocess
import os

# This script is a laboratory for finding the minimal working Tau command.
# We will start with a known-good command structure and simplify it.

TAU_EXECUTABLE = os.path.abspath("./.external_deps/tau-lang/build-Release/tau")

# This is a hard reset of our testing strategy, returning to the ground truth
# of the tau.tgf grammar file.
# It tests the most fundamental command possible: a single assignment using the
# correct `:=` operator and a boolean constant, followed by an evaluation.
command_to_test = "a := 1 . n a"

# We will run the command without shell=True to avoid any shell interpretation issues.
# The command and its arguments are passed as a list.
command_as_list = [TAU_EXECUTABLE, "--evaluate", command_to_test]

print(f"Running command:\n{' '.join(command_as_list)}\n")

result = subprocess.run(command_as_list, capture_output=True, text=True)

print(f"Exit Code: {result.returncode}")
print(f"Stdout:\n{result.stdout}")
print(f"Stderr:\n{result.stderr}")

# Improved result reporting
if "Error" in result.stdout or "Error" in result.stderr:
    print("\nResult: FAILURE")
elif result.stdout.strip() == "1":
    print("\nResult: SUCCESS (Output is 1)")
else:
    # Handles case where output is 0 (empty stdout) or something else
    print(f"\nResult: SUCCESS (Output is '{result.stdout.strip()}')")
