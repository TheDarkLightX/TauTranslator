#!/bin/bash

# This script is a control experiment to validate the exact syntax from the
# official pointwise revision documentation. It proves that the 'u' stream
# expects a *stream specification*, not a timeless predicate definition.

{
  # 1. Start the pointwise revision listener.
  echo "run u[t] = i1[t]"
  sleep 2

  # 2. Propose the update using the exact syntax from the documentation.
  echo "o1[t] = 1"
  sleep 2

} | docker run -i --rm tau-lang:latest
