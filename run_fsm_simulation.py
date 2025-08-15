#!/usr/bin/env python3

import subprocess
import os

# --- Configuration ---
TAU_EXECUTABLE = os.path.abspath("./.external_deps/tau-lang/build-Release/tau")
INPUT_B1_FILE = "vending_inputs_b1.txt"
INPUT_B0_FILE = "vending_inputs_b0.txt"

OUTPUT_STATE_B1_FILE = "/tmp/vending_state_b1.txt"
OUTPUT_STATE_B0_FILE = "/tmp/vending_state_b0.txt"
OUTPUT_ACTION_B1_FILE = "/tmp/vending_action_b1.txt"
OUTPUT_ACTION_B0_FILE = "/tmp/vending_action_b0.txt"

# The core FSM logic definitions, to be included in every command.
# Note the lack of spaces around `:=` which is critical.
FSM_LOGIC_TEMPLATE = (
    "s1_prev:={s1_prev} . "
    "s0_prev:={s0_prev} . "
    "i1_curr:={i1_curr} . "
    "i2_curr:={i2_curr} . "
    "s1_curr := s1_prev's0_prev i1_curr . "
    "s0_curr := (s1_prev'i1_curr') | (s1_prev's0_prev i1_curr i2_curr') . "
    "a1_curr := s1_prev's0_prev i1_curr i2_curr' . "
    "a0_curr := s1_prev's0_prev i1_curr i2_curr . "
)

def run_tau_eval(command_str):
    """Runs a tau --evaluate command and returns 1 if output is present, 0 otherwise."""
    # We use the 'n' (normalize) command as it's the correct way to evaluate
    # a non-temporal formula and get an output.
    full_command = f'{TAU_EXECUTABLE} --evaluate "{command_str}"'
    
    result = subprocess.run(full_command, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        # The command that previously worked had a non-zero exit code but was benign.
        # We check for the specific syntax error that has plagued us.
        if "Syntax Error: Unexpected ':'" in result.stdout:
             print(f"FATAL: Persistent syntax error encountered.\nCommand: {full_command}\nOutput: {result.stdout}")
             exit(1)

    # The tool prints '1' for true and nothing for false.
    return 1 if result.stdout.strip() == '1' else 0

def main():
    """Main simulation loop."""
    print("Starting Tau FSM simulation...")

    try:
        with open(INPUT_B1_FILE, 'r') as f1, open(INPUT_B0_FILE, 'r') as f0:
            inputs_b1 = [int(line.strip()) for line in f1.readlines()]
            inputs_b0 = [int(line.strip()) for line in f0.readlines()]
    except FileNotFoundError as e:
        print(f"Error: Input file not found - {e}. Make sure you are in the project root.")
        return

    # Initial state
    s1, s0 = 0, 0

    # Storage for the output streams
    history_s1, history_s0 = [], []
    history_a1, history_a0 = [], []

    num_steps = len(inputs_b1)
    print(f"Found {num_steps} time steps to simulate.")

    for t in range(num_steps):
        i1, i2 = inputs_b1[t], inputs_b0[t]
        print(f"Step {t+1}/{num_steps}: State=({s1},{s0}), Input=({i1},{i2}) -> ", end="")

        base_logic = FSM_LOGIC_TEMPLATE.format(s1_prev=s1, s0_prev=s0, i1_curr=i1, i2_curr=i2)

        # Calculate next state and action by running tau for each bit
        s1_next = run_tau_eval(base_logic + "n s1_curr")
        s0_next = run_tau_eval(base_logic + "n s0_curr")
        a1_next = run_tau_eval(base_logic + "n a1_curr")
        a0_next = run_tau_eval(base_logic + "n a0_curr")

        print(f"New State=({s1_next},{s0_next}), Action=({a1_next},{a0_next})")

        # Update state for the next iteration
        s1, s0 = s1_next, s0_next

        # Record history
        history_s1.append(str(s1_next))
        history_s0.append(str(s0_next))
        history_a1.append(str(a1_next))
        history_a0.append(str(a0_next))

    # Write results to output files
    print("\nSimulation complete. Writing output files...")
    with open(OUTPUT_STATE_B1_FILE, 'w') as f: f.write('\n'.join(history_s1) + '\n')
    with open(OUTPUT_STATE_B0_FILE, 'w') as f: f.write('\n'.join(history_s0) + '\n')
    with open(OUTPUT_ACTION_B1_FILE, 'w') as f: f.write('\n'.join(history_a1) + '\n')
    with open(OUTPUT_ACTION_B0_FILE, 'w') as f: f.write('\n'.join(history_a0) + '\n')

    print(f"Outputs written to:")
    print(f" - {OUTPUT_STATE_B1_FILE}")
    print(f" - {OUTPUT_STATE_B0_FILE}")
    print(f" - {OUTPUT_ACTION_B1_FILE}")
    print(f" - {OUTPUT_ACTION_B0_FILE}")

if __name__ == "__main__":
    main()
