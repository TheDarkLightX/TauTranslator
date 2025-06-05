Feature: Basic Translation between TCE and TAU
  As a system user
  I want to translate between TCE (Tau Controlled English) and TAU logic
  So that I can work with formal specifications in a natural way

  Background:
    Given the translation system is initialized
    And the default vocabulary is loaded

  @core @translation
  Scenario: Translate simple predicate definition from TCE to TAU
    Given I have TCE input "define predicate bottom(x) as x = 0."
    When I translate from TCE to TAU
    Then the TAU output should be "bottom(x) := x = 0"
    And the translation should have no errors

  @core @translation
  Scenario: Translate function definition from TCE to TAU
    Given I have TCE input "define function halfAdderSum(a, b) as a xor b."
    When I translate from TCE to TAU
    Then the TAU output should be "halfAdderSum(a, b) := a + b"
    And the translation should have no errors

  @core @translation
  Scenario: Translate stream output assignment from TCE to TAU
    Given I have TCE input "output 1 at time t = 0."
    When I translate from TCE to TAU
    Then the TAU output should be "o1[t] = 0"
    And the translation should have no errors

  @core @translation
  Scenario: Translate universal quantification from TCE to TAU
    Given I have TCE input "for every x such that x > 0."
    When I translate from TCE to TAU
    Then the TAU output should be "{all x} (x > 0)"
    And the translation should have no errors

  @core @translation
  Scenario: Translate existential quantification from TCE to TAU
    Given I have TCE input "there exists x such that x = y."
    When I translate from TCE to TAU
    Then the TAU output should be "{ex x} (x = y)"
    And the translation should have no errors

  @core @translation
  Scenario: Translate implication from TCE to TAU
    Given I have TCE input "if x > 5 then valid(x)."
    When I translate from TCE to TAU
    Then the TAU output should be "(x > 5) -> valid(x)"
    And the translation should have no errors

  @core @translation
  Scenario: Translate boolean operations from TCE to TAU
    Given I have TCE input "x and y or z."
    When I translate from TCE to TAU
    Then the TAU output should be "x & y \\ z"
    And the translation should have no errors

  @core @translation
  Scenario: Translate negation from TCE to TAU
    Given I have TCE input "not x."
    When I translate from TCE to TAU
    Then the TAU output should be "x'"
    And the translation should have no errors

  @core @translation @bidirectional
  Scenario: Round-trip translation preserves meaning
    Given I have TCE input "define predicate is_valid(x) as x > 0 and x < 100."
    When I translate from TCE to TAU
    Then the TAU output should be "is_valid(x) := x > 0 & x < 100"
    When I translate the TAU back to TCE
    Then the TCE output should be "define predicate is_valid(x) as x > 0 and x < 100."

  @error_handling
  Scenario: Handle missing period gracefully
    Given I have TCE input "x = 5"
    When I translate from TCE to TAU
    Then the translation should fail
    And the error message should contain "period"

  @error_handling
  Scenario: Handle empty input
    Given I have TCE input ""
    When I translate from TCE to TAU
    Then the translation should fail
    And the error message should contain "empty"