Feature: Complex Translation Scenarios
  As an advanced user
  I want to translate complex logical expressions
  So that I can express sophisticated formal specifications

  Background:
    Given the translation system is initialized
    And the advanced vocabulary is loaded

  @complex @translation
  Scenario: Translate nested quantifiers
    Given I have TCE input "Always x exists y such that x is less than y."
    When I translate from TCE to TAU
    Then the TAU output should be "∀x∃y(x < y)"
    And the translation should have no errors

  @complex @translation
  Scenario: Translate logical connectives
    Given I have TCE input "x and y or z implies w."
    When I translate from TCE to TAU
    Then the TAU output should be "((x ∧ y) ∨ z) → w"
    And the translation should have no errors

  @complex @translation
  Scenario: Translate mixed quantifiers and predicates
    Given I have TCE input "Always person exists friend such that likes(person, friend) and trusts(person, friend)."
    When I translate from TCE to TAU
    Then the TAU output should be "∀person∃friend(likes(person, friend) ∧ trusts(person, friend))"
    And the translation should have no errors

  @complex @translation @temporal
  Scenario: Translate temporal logic expressions
    Given I have TCE input "Always eventually x holds."
    When I translate from TCE to TAU
    Then the TAU output should be "□◇x"
    And the translation should have no errors

  @complex @translation @modal
  Scenario: Translate modal logic expressions
    Given I have TCE input "It is necessary that x implies y."
    When I translate from TCE to TAU
    Then the TAU output should be "□(x → y)"
    And the translation should have no errors

  @complex @translation
  Scenario Outline: Translate various complex expressions
    Given I have TCE input "<tce_input>"
    When I translate from TCE to TAU
    Then the TAU output should be "<tau_output>"
    And the translation should have no errors

    Examples:
      | tce_input                                    | tau_output                    |
      | not x or y and z.                          | ¬x ∨ (y ∧ z)                 |
      | if x then y else z.                         | (x → y) ∧ (¬x → z)           |
      | x is between 1 and 10.                      | (1 ≤ x) ∧ (x ≤ 10)          |
      | set S contains x.                           | x ∈ S                         |
      | function f of x equals y.                   | f(x) = y                      |