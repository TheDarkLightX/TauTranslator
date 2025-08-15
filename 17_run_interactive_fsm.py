import subprocess
import time
import select

# --- Configuration ---
TAU_EXECUTABLE = ".external_deps/tau-lang/build-Release/tau"
SPEC_FILE = "17_fsm_interactive.tau"

def read_output(process, timeout=0.5):
    """Reads available output from the process stdout without blocking indefinitely."""
    output = ""
    while select.select([process.stdout], [], [], timeout)[0]:
        char = process.stdout.read(1)
        if char:
            output += char
        else:
            break
    return output

def main():
    """Runs a live, interactive FSM simulation."""
    print("--- Starting Live Vending Machine Simulation ---")
    print("Enter '1' for true, '0' for false at each prompt.")
    print("Type 'quit' at any time to exit.")

    process = subprocess.Popen(
        [TAU_EXECUTABLE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line-buffered
    )

    # Wait for REPL to start and clear welcome message
    time.sleep(1)
    initial_output = read_output(process, timeout=1)
    print(initial_output.strip())

    # Load the interactive FSM specification
    load_command = f'run "{SPEC_FILE}"\n'
    process.stdin.write(load_command)
    process.stdin.flush()
    time.sleep(1) # Give Tau time to load and process the spec
    load_output = read_output(process, timeout=1)
    print("\n--- FSM Spec Loaded. Initializing... ---")

    # The spec initializes the outputs for t=0
    # dispense, return_coin, ready
    initial_state_output = read_output(process, timeout=1).strip().split('\n')
    if len(initial_state_output) >= 3:
        print(f"Initial State (t=0): dispense={initial_state_output[-3]}, return_coin={initial_state_output[-2]}, ready={initial_state_output[-1]}")
    else:
        print("Could not read initial state. Check spec.")

    timestep = 0
    while True:
        timestep += 1
        print(f"\n--- Timestep {timestep} ---")
        try:
            coin = input("  Input 'coin' (0/1): ")
            if coin.lower() == 'quit': break
            button = input("  Input 'button' (0/1): ")
            if button.lower() == 'quit': break
            cancel = input("  Input 'cancel' (0/1): ")
            if cancel.lower() == 'quit': break

            if not all(c in '01' for c in [coin, button, cancel]):
                print("Invalid input. Please enter only 0 or 1.")
                continue

            # Send inputs to Tau (it expects them in order: coin, button, cancel)
            process.stdin.write(f"{coin}\n")
            process.stdin.write(f"{button}\n")
            process.stdin.write(f"{cancel}\n")
            process.stdin.flush()

            # Wait and read the 3 output values
            time.sleep(0.5)
            sim_output = read_output(process, timeout=1).strip().split('\n')
            
            if len(sim_output) >= 3:
                # Get the last 3 lines which should be our outputs
                dispense_out = sim_output[-3]
                return_out = sim_output[-2]
                ready_out = sim_output[-1]
                print(f"  Output: dispense={dispense_out}, return_coin={return_out}, ready={ready_out}")
            else:
                print("Error: Did not receive expected output from Tau.")
                print(f"Received: {sim_output}")

        except (KeyboardInterrupt, EOFError):
            break

    print("\n--- Simulation Ended ---")
    process.stdin.close()
    process.terminate()
    process.wait()

if __name__ == "__main__":
    main()
