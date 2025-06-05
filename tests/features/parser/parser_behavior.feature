Feature: Parser Behavior and Error Handling
  As a developer
  I want the parser to handle various inputs correctly
  So that users get helpful feedback and correct parsing

  Background:
    Given the CNL parser is initialized
    And the grammar rules are loaded

  @parser @core
  Scenario: Parse simple sentence with period
    Given I have input text "true."
    When I parse the input
    Then parsing should succeed
    And the AST root should be a SentenceNode
    And the sentence content should be a FactNode

  @parser @core
  Scenario: Reject sentence without period
    Given I have input text "true"
    When I parse the input
    Then parsing should fail
    And the error should mention "period"

  @parser @tokenization
  Scenario: Tokenize complex expression correctly
    Given I have input text "x > 5 and y < 10."
    When I tokenize the input
    Then I should get tokens:
      | type       | value | position |
      | IDENTIFIER | x     | 0        |
      | OPERATOR   | >     | 2        |
      | NUMBER     | 5     | 4        |
      | KEYWORD    | and   | 6        |
      | IDENTIFIER | y     | 10       |
      | OPERATOR   | <     | 12       |
      | NUMBER     | 10    | 14       |
      | PERIOD     | .     | 16       |

  @parser @ast
  Scenario: Build correct AST for predicate call
    Given I have input text "is_valid(user, session)."
    When I parse the input
    Then the AST should contain:
      | node_type          | property | value     |
      | PredicateCallNode  | name     | is_valid  |
      | PredicateCallNode  | args[0]  | user      |
      | PredicateCallNode  | args[1]  | session   |

  @parser @error_recovery
  Scenario: Provide helpful error for unclosed parenthesis
    Given I have input text "func(x, y."
    When I parse the input
    Then parsing should fail
    And the error should mention "closing parenthesis"
    And the error should indicate position 10

  @parser @performance
  Scenario: Parse large expression within time limit
    Given I have a complex expression with 100 nested operations
    When I parse the input
    Then parsing should complete within 100 milliseconds
    And memory usage should be under 10 MB

  @parser @unicode
  Scenario: Handle Unicode characters correctly
    Given I have input text "température > 20°C."
    When I parse the input
    Then parsing should succeed
    And the identifier should be "température"
    And the string should contain "20°C"

  @parser @grammar
  Scenario Outline: Parse various grammar constructs
    Given I have input text "<input>"
    When I parse the input
    Then parsing should <result>
    And the main construct should be "<construct>"

    Examples:
      | input                    | result  | construct        |
      | true.                    | succeed | constant         |
      | x equals 5.              | succeed | comparison       |
      | p(a, b, c).              | succeed | predicate        |
      | [1, 2, 3].               | succeed | list             |
      | {x: x > 0}.              | succeed | set_builder      |
      | not (x or y).            | succeed | logical_negation |