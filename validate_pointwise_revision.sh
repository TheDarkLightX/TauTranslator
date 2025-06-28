#!/bin/bash

# This script validates the pointwise revision feature of the Tau language.
# It follows the minimal example from the official documentation by piping
# a sequence of updates into the Tau REPL.

{
  # 1. Start the REPL with the initial specification from the .tau file.
  cat tests/generated_specs/pointwise_revision_demo.tau
  sleep 2 # Wait for the REPL to process the 'run' command.

  # 2. Input the first update for t=0. This should be accepted.
  echo "o1[t] = 1"
  sleep 2

  # 3. Input the second, unsatisfiable update for t=1. This should be rejected.
  echo "o2[t] = 0 && o2[t] = 1"
  sleep 2

  # 4. Input the third, contradictory update for t=2. This should be accepted and replace the old rule.
  echo "o1[t] = 0"
  sleep 2

} | docker run -i --rm tau-lang:latest
