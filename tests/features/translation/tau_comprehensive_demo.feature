Feature: Comprehensive Tau Language Translation
  As a Tau language user
  I want to translate complex Tau expressions bidirectionally
  So that I can work with Tau in both formal and natural language

  Background:
    Given the translation system is initialized with full Tau parser
    And I have access to all Tau language constructs

  @temporal @streams
  Scenario: Stream declarations with files
    When I translate "sbf input_stream = ifile(\"sensor_data.txt\")" from TAU to PLAIN_ENGLISH
    Then the translation should be "Define input stream 'input_stream' that reads from file \"sensor_data.txt\""
    When I translate "sbf output_stream = ofile(\"processed_data.txt\")" from TAU to PLAIN_ENGLISH
    Then the translation should be "Define output stream 'output_stream' that writes to file \"processed_data.txt\""

  @temporal @rules
  Scenario: Temporal rules with time indexing
    When I translate "r o1[t] = i1[t] & i2[t]" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: output stream o1 at time t equals input stream i1 at time t AND input stream i2 at time t"
    When I translate the result back from PLAIN_ENGLISH to TAU
    Then the translation should be "r o1[t] = i1[t] & i2[t]"

  @temporal @delayed
  Scenario: Delayed signals and temporal offsets
    When I translate "r output[t] = input[t-1]" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: output at time t equals input at time t minus 1"
    When I translate "r y[t+1] = x[t] | z[t]" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: y at time t plus 1 equals x at time t OR z at time t"

  @logic @gates
  Scenario: Logic gate implementations
    When I translate "r and_gate[t] = a[t] & b[t]" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: and_gate at time t equals a at time t AND b at time t"
    When I translate "r xor_gate[t] = (a[t] & !b[t]) | (!a[t] & b[t])" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: xor_gate at time t equals (a at time t AND NOT b at time t) OR (NOT a at time t AND b at time t)"

  @temporal @always
  Scenario: Temporal modalities
    When I translate "always (temperature[t] > 0 && temperature[t] < 100)" from TAU to PLAIN_ENGLISH
    Then the translation should be "It is always the case that temperature at time t is greater than 0 and temperature at time t is less than 100"
    When I translate "sometimes (alert[t] = true)" from TAU to PLAIN_ENGLISH
    Then the translation should be "Sometimes alert at time t equals true"
    When I translate "eventually (system_ready[t])" from TAU to PLAIN_ENGLISH
    Then the translation should be "Eventually system_ready at time t will be true"

  @arithmetic @binary
  Scenario: Binary arithmetic operations
    When I translate "r sum[0] = a[0] ^ b[0]" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: sum at position 0 equals a at position 0 XOR b at position 0"
    When I translate "r carry[0] = a[0] & b[0]" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: carry at position 0 equals a at position 0 AND b at position 0"

  @functions @definitions
  Scenario: Function definitions
    When I translate "max(x, y) := if x > y then x else y" from TAU to PLAIN_ENGLISH
    Then the translation should be "Define function max with parameters x and y as: if x is greater than y then return x else return y"
    When I translate the result back from PLAIN_ENGLISH to TAU
    Then the translation should be "max(x, y) := if x > y then x else y"

  @quantifiers @complex
  Scenario: Complex quantified expressions
    When I translate "forall t : (stable[t] -> stable[t+1])" from TAU to PLAIN_ENGLISH
    Then the translation should be "For all time t: if stable at time t then stable at time t plus 1"
    When I translate "exists t : (error[t] & !error[t+1])" from TAU to PLAIN_ENGLISH
    Then the translation should be "There exists a time t such that error at time t and not error at time t plus 1"

  @democracy @voting
  Scenario: Majority rule implementation
    When I translate "r decision[t] = (vote1[t] + vote2[t] + vote3[t]) > 1" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: decision at time t equals true when the sum of vote1 at time t, vote2 at time t, and vote3 at time t is greater than 1"

  @feedback @loops
  Scenario: Feedback loop patterns
    When I translate "r state[t+1] = state[t] & input[t]" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: state at time t plus 1 equals state at time t AND input at time t"
    When I translate "r output[t] = state[t] | external[t]" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: output at time t equals state at time t OR external at time t"