Feature: Tau Solver Demo Translation
  As a Tau language user
  I want to translate solver expressions between Tau and Plain English
  So that I can understand and work with constraint solving

  Background:
    Given the translation system is initialized
    And I have access to the Tau parser

  @solver @demo
  Scenario: Simple equation solving
    When I translate "solve x = 0" from TAU to PLAIN_ENGLISH
    Then the translation should be "Find a value for x such that x equals zero"
    When I translate the result back from PLAIN_ENGLISH to TAU
    Then the translation should be "solve x = 0"

  @solver @demo
  Scenario: Conjunction of equations
    When I translate "solve x = 0 && y = 0" from TAU to PLAIN_ENGLISH
    Then the translation should be "Find values for x and y such that x equals zero and y equals zero"
    When I translate the result back from PLAIN_ENGLISH to TAU
    Then the translation should be "solve x = 0 && y = 0"

  @solver @demo @type_annotation
  Scenario: Typed variable solving
    When I translate "solve {a}:sbf x = 0" from TAU to PLAIN_ENGLISH
    Then the translation should be "Find a value for x where a is of type sbf such that x equals zero"
    When I translate the result back from PLAIN_ENGLISH to TAU
    Then the translation should be "solve {a}:sbf x = 0"

  @solver @demo @complement
  Scenario: Complement operator in solving
    When I translate "solve x != 0 && x' != 0" from TAU to PLAIN_ENGLISH
    Then the translation should be "Find a value for x such that x is not equal to zero and the complement of x is not equal to zero"
    When I translate the result back from PLAIN_ENGLISH to TAU
    Then the translation should be "solve x != 0 && x' != 0"

  @solver @demo @existential_quantifier
  Scenario: Existential quantifiers in constraints
    When I translate "solve {ex a a = 0} x != 0 && {ex b b = 0} x != 0" from TAU to PLAIN_ENGLISH
    Then the translation should be "Find a value for x such that there exists a where a equals zero implies x is not equal to zero, and there exists b where b equals zero implies x is not equal to zero"
    When I translate the result back from PLAIN_ENGLISH to TAU
    Then the translation should be "solve {ex a a = 0} x != 0 && {ex b b = 0} x != 0"

  @solver @demo @complex_expression
  Scenario: Complex arithmetic solving
    When I translate "solve {ex x x = 0} a + {ex y y = 0} b = 0" from TAU to PLAIN_ENGLISH
    Then the translation should be "Find values such that the sum of a (where there exists x such that x equals zero) and b (where there exists y such that y equals zero) equals zero"
    When I translate the result back from PLAIN_ENGLISH to TAU
    Then the translation should be "solve {ex x x = 0} a + {ex y y = 0} b = 0"

  @solver @demo @linear_equation
  Scenario: Linear equation solving
    When I translate "solve a x + b y = 0" from TAU to PLAIN_ENGLISH
    Then the translation should be "Find values for x and y such that a times x plus b times y equals zero"
    When I translate the result back from PLAIN_ENGLISH to TAU
    Then the translation should be "solve a x + b y = 0"