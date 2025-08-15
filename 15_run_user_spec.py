import subprocess
import time
import re

# --- Configuration ---
TAU_EXECUTABLE = ".external_deps/tau-lang/build-Release/tau"
# Use the user's canonical FSM specification
SPEC_FILE = ".external_deps/novel_tau_specs/simple_vending_machine_fsm.tau"

# Input files for the user's spec
INPUT_COIN_FILE = "vending_inputs_coin.txt"
INPUT_BUTTON_FILE = "vending_inputs_button.txt"
INPUT_CANCEL_FILE = "vending_inputs_cancel.txt"

# Output files for the simulation results
OUTPUT_DISPENSE_FILE = "/tmp/fsm_dispense.txt"
OUTPUT_RETURN_FILE = "/tmp/fsm_return_coin.txt"
OUTPUT_READY_FILE = "/tmp/fsm_ready.txt"

def read_inputs(coin_file, button_file, cancel_file):
    """Reads the multiple input streams from their respective files."""
    with open(coin_file, 'r') as f:
        coin_inputs = [line.strip() for line in f.readlines()]
    with open(button_file, 'r') as f:
        button_inputs = [line.strip() for line in f.readlines()]
    with open(cancel_file, 'r') as f:
        cancel_inputs = [line.strip() for line in f.readlines()]
    return coin_inputs, button_inputs, cancel_inputs

def parse_stream_output(output):
    """Parses the REPL output to find all stream value assignments."""
    # Example output: dispense[t] = 0
    pattern = re.compile(r"(\w+)\[\d+\] = (\d+)")
    matches = pattern.findall(output)
    # Return a dictionary of stream_name: value
    return {match[0]: match[1] for match in matches}

def main():
    """Runs the full FSM simulation interactively using a user-provided spec."""
    print("--- Starting Interactive FSM Simulation with User Spec ---")

    coin_inputs, button_inputs, cancel_inputs = read_inputs(
        INPUT_COIN_FILE, INPUT_BUTTON_FILE, INPUT_CANCEL_FILE
    )
    num_timesteps = len(coin_inputs)

    process = subprocess.Popen(
        [TAU_EXECUTABLE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # Give the REPL a moment to start
    time.sleep(1)
    # Clear the welcome message
    process.stdout.read(4096)

    # Load the specification file
    load_command = f'run "{SPEC_FILE}"\n'
    process.stdin.write(load_command)
    process.stdin.flush()
    time.sleep(1) # Give it a moment to load and process the spec
    process.stdout.read(4096) # Clear loading output

    outputs_dispense = []
    outputs_return = []
    outputs_ready = []

    for t in range(num_timesteps):
        print(f"\n--- Timestep {t} ---")
        coin, button, cancel = coin_inputs[t], button_inputs[t], cancel_inputs[t]
        print(f"Inputs: coin={coin}, button={button}, cancel={cancel}")

        # Send inputs for the current timestep
        input_command = f"coin[t] = {coin}\nbutton[t] = {button}\ncancel[t] = {cancel}\n"
        process.stdin.write(input_command)
        process.stdin.flush()
        time.sleep(0.5) # Wait for the temporal solver

        output = process.stdout.read(8192) # Read a large chunk of output
        results = parse_stream_output(output)

        dispense = results.get('dispense', 'ERROR')
        return_coin = results.get('return_coin', 'ERROR')
        ready = results.get('ready', 'ERROR')

        if 'ERROR' in [dispense, return_coin, ready]:
            print("Error: Failed to parse one or more output streams.")
            print(f"Full REPL output for timestep {t}:\n{output}")
            break

        print(f"Outputs: dispense={dispense}, return_coin={return_coin}, ready={ready}")
        outputs_dispense.append(dispense)
        outputs_return.append(return_coin)
        outputs_ready.append(ready)

    process.stdin.close()
    process.terminate()
    process.wait()

    with open(OUTPUT_DISPENSE_FILE, 'w') as f:
        f.write('\n'.join(outputs_dispense) + '\n')
    with open(OUTPUT_RETURN_FILE, 'w') as f:
        f.write('\n'.join(outputs_return) + '\n')
    with open(OUTPUT_READY_FILE, 'w') as f:
        f.write('\n'.join(outputs_ready) + '\n')

    print("\n--- Simulation Complete ---")
    print(f"Outputs written to {OUTPUT_DISPENSE_FILE}, {OUTPUT_RETURN_FILE}, {OUTPUT_READY_FILE}")

if __name__ == "__main__":
    main()
