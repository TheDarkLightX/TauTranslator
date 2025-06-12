Feature: Natural Language to TCE Translation
  As a user of TauTranslator
  I want to translate plain English to TCE (Tau Controlled English)
  So that I can express logical statements in a formal language

  Background:
    Given I have a natural language to TCE translator

  Scenario: Simple variable assignment
    When I translate "x equals 5" to TCE
    Then the TCE output should be "x = 5."

  Scenario: Variable definition with 'is'
    When I translate "temperature is 25" to TCE
    Then the TCE output should be "temperature = 25."

  Scenario: Boolean AND operation
    When I translate "x and y" to TCE
    Then the TCE output should be "x and y."

  Scenario: Boolean OR operation
    When I translate "a or b" to TCE
    Then the TCE output should be "a or b."

  Scenario: Boolean NOT operation
    When I translate "not p" to TCE
    Then the TCE output should be "not p."

  Scenario: Greater than comparison
    When I translate "x is greater than 10" to TCE
    Then the TCE output should be "x > 10."

  Scenario: Less than comparison
    When I translate "y is less than 5" to TCE
    Then the TCE output should be "y < 5."

  Scenario: Greater than or equal comparison
    When I translate "z is at least 0" to TCE
    Then the TCE output should be "z >= 0."

  Scenario: Less than or equal comparison
    When I translate "w is at most 100" to TCE
    Then the TCE output should be "w <= 100."

  Scenario: Simple conditional
    When I translate "if x then y" to TCE
    Then the TCE output should be "if x then y."

  Scenario: Conditional with comparison
    When I translate "if temperature is greater than 30 then cooling is on" to TCE
    Then the TCE output should be "if temperature > 30 then cooling = on."

  Scenario: Universal quantification with 'all'
    When I translate "for all x, x equals x" to TCE
    Then the TCE output should be "for all x, x = x."

  Scenario: Universal quantification with 'every'
    When I translate "for every student, student has id" to TCE
    Then the TCE output should be "for all student, student has id."

  Scenario: Existential quantification
    When I translate "there exists x such that x is prime" to TCE
    Then the TCE output should be "exists x such that x is prime."

  Scenario: Temporal always
    When I translate "always system is secure" to TCE
    Then the TCE output should be "always system is secure."

  Scenario: Temporal sometimes
    When I translate "sometimes door is open" to TCE
    Then the TCE output should be "sometimes door is open."

  Scenario: Complex requirement
    When I translate "all users must have valid passwords" to TCE
    Then the TCE output should be "for all users, users have valid passwords."

  Scenario: Mathematical expression
    When I translate "x plus y equals z" to TCE
    Then the TCE output should be "x + y = z."

  Scenario: Multiple conditions
    When I translate "x is greater than 0 and y is less than 10" to TCE
    Then the TCE output should be "x > 0 and y < 10."