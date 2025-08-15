import subprocess

# --- Configuration ---
TAU_EXECUTABLE = ".external_deps/tau-lang/build-Release/tau"
SPEC_FILE = "16_fsm_pure_function_validation.tau"

def main():
    """Runs the self-validating FSM spec in batch mode."""
    print(f"--- Running Batch Validation for {SPEC_FILE} ---")

    # Using the user's canonical batch execution pattern
    command = f"cat {SPEC_FILE} | {TAU_EXECUTABLE}"

    try:
        # We use shell=True because the command uses a pipe
        result = subprocess.run(
            command,
            shell=True,
            check=True, # Raise an exception for non-zero exit codes
            capture_output=True,
            text=True,
            timeout=30 # Add a timeout for safety
        )

        print("--- Tau Execution Successful ---")
        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("--- STDERR ---")
            print(result.stderr)

        # Final validation check
        if "(Error)" in result.stdout or "(Error)" in result.stderr:
            print("\n--- VALIDATION FAILED: Errors detected in output. ---")
        else:
            print("\n--- VALIDATION SUCCEEDED: All tests passed successfully! ---")

    except subprocess.CalledProcessError as e:
        print(f"--- Tau Execution Failed with exit code {e.returncode} ---")
        print("STDOUT:")
        print(e.stdout)
        print("STDERR:")
        print(e.stderr)
    except subprocess.TimeoutExpired as e:
        print("--- Tau Execution Timed Out ---")
        print("The Tau process did not complete within the time limit.")
        print("STDOUT:")
        print(e.stdout)
        print("STDERR:")
        print(e.stderr)

if __name__ == "__main__":
    main()
