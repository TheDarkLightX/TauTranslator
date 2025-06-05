Feature: Arithmetic and Binary Operations Translation
  As a user working with binary arithmetic
  I want to translate arithmetic and bit operations
  So that I can model computational logic

  Background:
    Given the translation system is initialized
    And the arithmetic vocabulary is loaded

  @arithmetic @translation
  Scenario: Translate binary adder function definitions from TCE to TAU
    Given I have TCE input "halfAdderSum(a, b) := a xor b."
    When I translate from TCE to TAU
    Then the TAU output should be "halfAdderSum(a, b) := a + b"
    And the translation should have no errors

  @arithmetic @translation
  Scenario: Translate binary carry function from TCE to TAU
    Given I have TCE input "halfAdderCarry(a, b) := a and b."
    When I translate from TCE to TAU
    Then the TAU output should be "halfAdderCarry(a, b) := a & b"
    And the translation should have no errors

  @arithmetic @translation
  Scenario: Translate full adder sum from TCE to TAU
    Given I have TCE input "fullAdderSum(a, b, c) := a xor b xor c."
    When I translate from TCE to TAU
    Then the TAU output should be "fullAdderSum(a, b, c) := a + b + c"
    And the translation should have no errors

  @arithmetic @translation
  Scenario: Translate full adder carry from TCE to TAU
    Given I have TCE input "fullAdderCarry(a, b, c) := (a and b) or (a and c) or (b and c)."
    When I translate from TCE to TAU
    Then the TAU output should be "fullAdderCarry(a, b, c) := (a & b) \\ (a & c) \\ (b & c)"
    And the translation should have no errors

  @arithmetic @translation
  Scenario: Translate bit definitions from TCE to TAU
    Given I have TCE input "a4(x) := 1."
    When I translate from TCE to TAU
    Then the TAU output should be "a4(x) := 1"
    And the translation should have no errors

  @arithmetic @translation
  Scenario: Translate binary addition using adders from TCE to TAU
    Given I have TCE input "bit0(x) := halfAdderSum(a4(x), b4(x))."
    When I translate from TCE to TAU
    Then the TAU output should be "bit0(x) := halfAdderSum(a4(x), b4(x))"
    And the translation should have no errors

  @arithmetic @translation
  Scenario: Translate normalization statement from TCE to TAU
    Given I have TCE input "normalize bit0(x) and bit1(x) and bit2(x) and bit3(x) and bit4(x)."
    When I translate from TCE to TAU
    Then the TAU output should be "normalize bit0(x) & bit1(x) & bit2(x) & bit3(x) & bit4(x)"
    And the translation should have no errors

  @arithmetic @translation
  Scenario Outline: Translate various arithmetic expressions
    Given I have TCE input "<tce_input>"
    When I translate from TCE to TAU
    Then the TAU output should be "<tau_output>"

    Examples:
      | tce_input                                      | tau_output                                |
      | x + y = z.                                    | x + y = z                                |
      | x - y > 0.                                    | x - y > 0                                |
      | x * y < 100.                                  | x * y < 100                              |
      | x / y >= 2.                                   | x / y >= 2                               |
      | (x + y) * z = w.                              | (x + y) * z = w                          |