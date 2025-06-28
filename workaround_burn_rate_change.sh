#!/bin/bash

# This script demonstrates the canonical workaround for complex state updates
# in pointwise revision. It encodes the economic policy into a single stream
# ('policy') and updates its value to change the contract's state.

{
  # 1. Start the pointwise revision listener.
  echo "run u[t] = i1[t]"
  sleep 2

  # 2. Establish the Initial Economic Policy: High Burn Rate (policy = 1)
  echo "policy[t]=1"
  sleep 2

  # 3. Propose the New Economic Policy: Low Burn Rate (policy = 2)
  # This is a simple, atomic update that the parser can handle.
  echo "policy[t]=2"
  sleep 2

} | docker run -i --rm tau-lang:latest
