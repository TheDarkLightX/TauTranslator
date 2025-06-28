#!/bin/bash

# This script demonstrates amending the 'smart constitution' of the voting system.
# It loads the initial state, starts the pointwise revision listener, and then
# proposes an amendment to add a new proposal to the ballot.

{
  # 1. Load the initial constitution.
  cat tests/generated_specs/updatable_voting_contract.tau
  sleep 2

  # 2. Start the pointwise revision listener.
  echo "run u[t] = i1[t]"
  sleep 2

  # 3. Propose the amendment: Add Proposal C to the ballot.
  # This contradicts the initial constitution, so it should *replace* the old rule.
  echo "proposal_c_is_on_ballot() = T"
  sleep 2

} | docker run -i --rm tau-lang:latest
