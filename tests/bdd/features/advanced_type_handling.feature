Feature: Advanced Type Definition and Usage
  As a developer, I want to define custom types and use them in subsequent statements
  so that I can create complex and expressive data structures.

  Scenario: Translate a function definition from TCE to Tau
    Given a fresh Tau translator instance
    When the user provides the TCE statement: "define function get_user(id: user_id) returns bool."
    Then the translator successfully processes the statement
    And the resulting Tau output is "fn get_user(id:user_id) -> bool;"

  Scenario: Define a new type with a simple constraint
    Given the TCE "Let a 'PositiveInteger' be an integer where the value is greater than 0."
    When the translator processes the TCE
    Then the resulting Tau specification should be:
      """
      typedef PositiveInteger as integer where value > 0;
      """
