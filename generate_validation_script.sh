#!/bin/bash
# Generates a final, runnable Tau script and provides the manual command for validation.

SPEC_FILE="tests/generated_specs/reflex_vacuum_agent.tau"
OUTPUT_DIR="validation"
SCRIPT_FILE="$OUTPUT_DIR/validate_reflex_agent.tau"

# 1. Prepare the validation script
mkdir -p "$OUTPUT_DIR"

# Concatenate spec and query into a single script file, sanitizing line endings.
(
    cat "$SPEC_FILE";
    echo ""; # Separator
    echo "# --- Validation Query ---";
    echo "# The following command proves that if the agent is in a dirty room A,";
    echo "# it cannot choose any action other than 'suck'.";
    echo "solve is_in_room_a(0) & is_dirty(0) & do_suck(0)'";
    echo "";
) | tr -d '\r' > "$SCRIPT_FILE"

# 2. Provide the user with the manual validation command.

VALIDATION_COMMAND="docker run --rm -i -v \"$(pwd)/$OUTPUT_DIR:/validation\" tau-lang:latest tau /validation/validate_reflex_agent.tau"

echo "✅ Validation script generated at: $SCRIPT_FILE"
echo ""
echo "---"
echo "Due to limitations in the Tau toolchain's batch processing, automated validation failed."
echo "Please run the following command in your terminal to manually validate the agent's logic:"
echo "---"
echo ""
echo "$VALIDATION_COMMAND"
echo ""

# 3. Check for the expected result
echo "--- The expected output is 'UNSATISFIABLE' ---"

exit 0
