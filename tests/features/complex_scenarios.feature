Feature: Advanced Translation Scenarios
  As a user, I want to translate complex statements to and from CNL
  to ensure the system's NLP and semantic analysis capabilities are robust.

  Scenario: Translate a multi-step arithmetic expression from English to CNL
    Given a grammar for arithmetic expressions is loaded
    When I provide the source text "(10 + 5) * 2"
    Then the transformed output should be "( 10 + 5 ) * 2"

  Scenario: Translate an arithmetic expression with variables from English to CNL
    Given a grammar for arithmetic expressions is loaded
    When I provide the source text "let x = 10; x * 5"
    Then the transformed output should be "let x = 10 ; x * 5"

  Scenario: Translate a natural language question into a CNL expression
    Given a grammar for arithmetic expressions is loaded
    When I provide the source text "what is seven times six"
    Then the transformed output should be "7 * 6"
