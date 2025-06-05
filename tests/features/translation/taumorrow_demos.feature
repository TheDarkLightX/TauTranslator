Feature: Taumorrow Community Demos Translation
  As a Tau language user
  I want to translate community-created Tau demos
  So that I can understand complex Tau programs in natural language

  Background:
    Given the translation system is initialized
    And I am working with taumorrow demo files

  @binary @arithmetic
  Scenario: Binary Adder Translation
    When I translate "halfAdderSum(a,b) := a + b" from TAU to PLAIN_ENGLISH
    Then the translation should be "Define function halfAdderSum with parameters a and b as a XOR b"
    When I translate "halfAdderCarry(a,b) := a & b" from TAU to PLAIN_ENGLISH
    Then the translation should be "Define function halfAdderCarry with parameters a and b as a AND b"
    When I translate "fullAdderSum(a,b,c) := a + b + c" from TAU to PLAIN_ENGLISH
    Then the translation should be "Define function fullAdderSum with parameters a, b and c as a XOR b XOR c"

  @binary @bitwise
  Scenario: Bit Operations Translation
    When I translate "bit0(x) := halfAdderSum(a4(x),b4(x))" from TAU to PLAIN_ENGLISH
    Then the translation should contain "bit0 of x"
    And the translation should contain "halfAdderSum of a4(x) and b4(x)"
    When I translate "carry0(x) := halfAdderCarry(a4(x),b4(x))" from TAU to PLAIN_ENGLISH
    Then the translation should contain "carry0 of x"
    And the translation should contain "halfAdderCarry"

  @logic_gates @streams
  Scenario: Logic Gates with Streams
    When I translate "sbf i1 = ifile(\"input1.in\")" from TAU to PLAIN_ENGLISH
    Then the translation should be "Define input stream i1 that reads from file \"input1.in\""
    When I translate "sbf o1 = ofile(\"and.out\")" from TAU to PLAIN_ENGLISH
    Then the translation should be "Define output stream o1 that writes to file \"and.out\""
    When I translate "r o1[t] = i1[t] & i2[t]" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: o1 at time t equals i1 at time t AND i2 at time t"

  @logic_gates @complement
  Scenario: NOT Gate Translation
    When I translate "r o3[t] = i1[t]'" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: o3 at time t equals the complement of i1 at time t"
    When I translate "Rule: output at time t equals NOT input at time t" from PLAIN_ENGLISH to TAU
    Then the translation should be "r output[t] = input[t]'"

  @logic_gates @xor
  Scenario: XOR Gate Translation
    When I translate "r o4[t] = (i1[t] & i2[t]') | (i1[t]' & i2[t])" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: o4 at time t equals (i1 at time t AND complement of i2 at time t) OR (complement of i1 at time t AND i2 at time t)"

  @democracy @consensus
  Scenario: Majority Voting Translation
    When I translate "r o1[t] = (i1[t] & i2[t]) | (i2[t] & i3[t]) | (i1[t] & i3[t])" from TAU to PLAIN_ENGLISH
    Then the translation should be "Rule: o1 at time t equals majority vote of i1, i2, and i3 at time t"
    And the translation should describe it as "at least two of three inputs are true"

  @democracy @temporal
  Scenario: Temporal Democracy Translation
    When I translate "r o3[t] = (i1[t] & i2[t]) | (i2[t] & i3[t]) | (i1[t] & i3[t]) & (i4[t-1] | (i1[t] & i2[t] & i3[t]))" from TAU to PLAIN_ENGLISH
    Then the translation should contain "majority vote"
    And the translation should contain "at time t-1"
    And the translation should describe temporal dependency

  @democracy @complex
  Scenario: Complex Democratic Strength
    When I translate "r o4[t] = ((i1[t] & i2[t]) | (i2[t] & i3[t]) | (i1[t] & i3[t])) & ((i1[t-1] & i2[t-1]) | (i2[t-1] & i3[t-1]) | (i1[t-1] & i3[t-1])) & i5[t]" from TAU to PLAIN_ENGLISH
    Then the translation should describe "current majority" and "previous majority"
    And the translation should mention "harmony" from i5

  @file_paths
  Scenario: File Path Translation
    When I translate "sbf o1 = ofile(\"/simple_test/outputs/consensus.out\")" from TAU to PLAIN_ENGLISH
    Then the translation should be "Define output stream o1 that writes to file \"/simple_test/outputs/consensus.out\""
    And the file path should be preserved exactly

  @roundtrip @binary
  Scenario: Binary Adder Round-trip
    Given the Tau expression "fullAdderCarry(a,b,c) := (a & b) | (a & c) | (b & c)"
    When I translate it from TAU to PLAIN_ENGLISH
    And I translate the result back from PLAIN_ENGLISH to TAU
    Then the final translation should be semantically equivalent to the original

  @roundtrip @streams
  Scenario: Stream Rule Round-trip
    Given the Tau expression "r output[t] = (input1[t] & input2[t]) | input3[t]"
    When I translate it from TAU to PLAIN_ENGLISH
    And I translate the result back from PLAIN_ENGLISH to TAU
    Then the final translation should be semantically equivalent to the original