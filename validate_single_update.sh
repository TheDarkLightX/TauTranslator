#!/bin/bash

# This script validates the computational cost of a single pointwise revision.
# It pipes a single, non-contradictory update into the Tau REPL.

{
  # 1. Start the REPL with the initial specification from the .tau file.
  cat tests/generated_specs/pointwise_revision_single_update.tau
  sleep 2 # Wait for the REPL to process the 'run' command.

  # 2. Input a single update for t=0. This should be accepted.
  echo "o1[t] = 1"
  sleep 2

} | docker run -i --rm tau-lang:latest
