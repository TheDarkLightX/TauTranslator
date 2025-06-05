Feature: Stream Processing Translation
  As a user working with temporal logic
  I want to translate stream-based operations
  So that I can model time-dependent systems

  Background:
    Given the translation system is initialized
    And the stream vocabulary is loaded

  @streams @translation
  Scenario: Translate stream input definition from TCE to TAU
    Given I have TCE input "sbf i1 = input file(\"input1.in\")."
    When I translate from TCE to TAU
    Then the TAU output should be "sbf i1 = i(\"input1.in\")"
    And the translation should have no errors

  @streams @translation
  Scenario: Translate stream output definition from TCE to TAU
    Given I have TCE input "sbf o1 = output file(\"and.out\")."
    When I translate from TCE to TAU
    Then the TAU output should be "sbf o1 = o(\"and.out\")"
    And the translation should have no errors

  @streams @translation
  Scenario: Translate stream rule with current time from TCE to TAU
    Given I have TCE input "rule o1[t] = i1[t] and i2[t]."
    When I translate from TCE to TAU
    Then the TAU output should be "o1[t] = i1[t] & i2[t]"
    And the translation should have no errors

  @streams @translation
  Scenario: Translate stream rule with time offset from TCE to TAU
    Given I have TCE input "rule o3[t] = i4[t-1] or i5[t+1]."
    When I translate from TCE to TAU
    Then the TAU output should be "o3[t] = i4[t-1] \\ i5[t+1]"
    And the translation should have no errors

  @streams @translation
  Scenario: Translate temporal always operator from TCE to TAU
    Given I have TCE input "always (o1[t] equals (i1[t] and i2[t]))."
    When I translate from TCE to TAU
    Then the TAU output should be "always (o1[t] = (i1[t] & i2[t]))"
    And the translation should have no errors

  @streams @translation
  Scenario: Translate complex stream logic from TCE to TAU
    Given I have TCE input "rule o4[t] = (i1[t] and i2[t] complement) or (i1[t] complement and i2[t])."
    When I translate from TCE to TAU
    Then the TAU output should be "o4[t] = (i1[t] & i2[t]') \\ (i1[t]' & i2[t])"
    And the translation should have no errors

  @streams @translation @democracy
  Scenario: Translate majority voting logic from TCE to TAU
    Given I have TCE input "rule o1[t] = (i1[t] and i2[t]) or (i2[t] and i3[t]) or (i1[t] and i3[t])."
    When I translate from TCE to TAU
    Then the TAU output should be "o1[t] = (i1[t] & i2[t]) \\ (i2[t] & i3[t]) \\ (i1[t] & i3[t])"
    And the translation should have no errors

  @streams @translation
  Scenario Outline: Translate various stream operations
    Given I have TCE input "<tce_input>"
    When I translate from TCE to TAU
    Then the TAU output should be "<tau_output>"

    Examples:
      | tce_input                                | tau_output                        |
      | rule o1[t] = i1[t].                     | o1[t] = i1[t]                    |
      | rule o2[t] = i1[t] xor i2[t].          | o2[t] = i1[t] + i2[t]            |
      | rule o3[t] = i1[t] complement.         | o3[t] = i1[t]'                   |
      | rule o4[t] = always i1[t].             | o4[t] = always i1[t]             |
      | rule o5[t] = sometimes i1[t].          | o5[t] = sometimes i1[t]          |