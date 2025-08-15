#!/usr/bin/env python3

import subprocess
import os
import re

# This script implements the full, multi-step FSM simulation.
# It is the culmination of all our hard-won knowledge about the Tau language.

TAU_EXECUTABLE = os.path.abspath("./.external_deps/tau-lang/build-Release/tau")
INPUT_B0_FILE = "vending_inputs_b0.txt"
INPUT_B1_FILE = "vending_inputs_b1.txt"
OUTPUT_O0_FILE = "/tmp/fsm_o0.txt"
OUTPUT_O1_FILE = "/tmp/fsm_o1.txt"

def parse_all_results(output):
    """
    Parses all evaluation results from the REPL's stdout.
    The Tau REPL prints results in the format '%d: result'.
    This function finds all such lines and extracts the result.
    """
    # Regex to find patterns like '%1: 0' or '%12: 1'.
    # We remove the start-of-line anchor `^` to make the parsing more
    # robust against variations in the REPL's output formatting.
    pattern = re.compile(r"%\d+: (\d+)")
    return pattern.findall(output)

def main():
    """Runs the full FSM simulation."""
    # Read input files
    with open(INPUT_B0_FILE, 'r') as f:
        inputs_b0 = [line.strip() for line in f.readlines()]
    with open(INPUT_B1_FILE, 'r') as f:
        inputs_b1 = [line.strip() for line in f.readlines()]

    num_steps = len(inputs_b0)
    outputs_o0 = []
    outputs_o1 = []

    # Initial state
    s0, s1 = 0, 0

    print("--- Starting FSM Simulation ---")

    for t in range(num_steps):
        b0 = inputs_b0[t]
        b1 = inputs_b1[t]

        print(f"\n--- Timestep {t} ---")
        print(f"Inputs:  b0={b0}, b1={b1}")
        print(f"State:   s0={s0}, s1={s1}")

        fsm_logic = [
            f"b0() := {b0} .",
            f"b1() := {b1} .",
            f"s0_prev() := {s0} .",
            f"s1_prev() := {s1} .",
            "s0_next() := (s0_prev() & s1_prev()' & b0()' & b1()') | (s0_prev() & s1_prev() & b0()' & b1()) .",
            "s1_next() := (s0_prev()' & s1_prev()' & b0()' & b1()) | (s0_prev()' & s1_prev() & b0()' & b1()') | (s0_prev() & s1_prev()' & b0()' & b1()) .",
            "o0() := (s0_prev()' & s1_prev() & b0()' & b1()') | (s0_prev() & s1_prev()' & b0()' & b1()') .",
            "o1() := (s0_prev() & s1_prev()' & b0()' & b1()) .",
            # Evaluation commands must be part of the same input
            "n o0()",
            "n o1()",
            "n s0_next()",
            "n s1_next()"
        ]

        process = subprocess.Popen(
            [TAU_EXECUTABLE],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, universal_newlines=True
        )
        stdout, stderr = process.communicate(input='\n'.join(fsm_logic) + '\n')

        if stderr:
            print(f"ERROR at timestep {t}: {stderr}")
            break

        # Parse all results from the output sequentially
        results = parse_all_results(stdout)

        if len(results) != 4:
            print(f"Error: Expected 4 results, but found {len(results)}. Aborting.")
            print(f"Full stdout:\n{stdout}")
            break
        
        o0, o1, s0_next, s1_next = results

        print(f"Outputs: o0={o0}, o1={o1}")
        print(f"New State: s0={s0_next}, s1={s1_next}")

        outputs_o0.append(o0)
        outputs_o1.append(o1)

        # Update state for next timestep
        s0, s1 = int(s0_next), int(s1_next)

    # Write output files
    with open(OUTPUT_O0_FILE, 'w') as f:
        f.write('\n'.join(outputs_o0) + '\n')
    with open(OUTPUT_O1_FILE, 'w') as f:
        f.write('\n'.join(outputs_o1) + '\n')

    print("\n--- Simulation Complete ---")
    print(f"Output o0 written to {OUTPUT_O0_FILE}")
    print(f"Output o1 written to {OUTPUT_O1_FILE}")

if __name__ == "__main__":
    main()
