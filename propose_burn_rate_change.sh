#!/bin/bash

# This script demonstrates a live amendment to a deflationary token's
# economic policy using pointwise revision.

{
  # 1. Start the pointwise revision listener.
  echo "run u[t] = i1[t]"
  sleep 2

  # 2. Establish the Initial Economic Policy: High Burn Rate
  # This is the first 'constitutional' amendment.
  echo "o2[t]=1&&o3[t]=0"
  sleep 2

  # 3. Propose the New Economic Policy: Low Burn Rate
  # This contradicts the initial policy and should replace it.
  echo "o2[t]=0&&o3[t]=1"
  sleep 2

} | docker run -i --rm tau-lang:latest
