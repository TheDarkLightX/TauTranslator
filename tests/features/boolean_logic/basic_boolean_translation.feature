# Copyright (c) DarkLightX / Dana Edwards

Feature: Basic Boolean Logic Translation
  As a user,
  I want to translate simple English statements into Boolean expressions
  So that I can verify the fundamental translation capabilities of TauTranslator.

  Background:
    Given the system is configured with the "boolean.tgf" grammar

  Scenario: Translate a single affirmative variable
    Given the English input "P is true"
    When the input is translated
    Then the translated output should be "P"

  Scenario: Translate a single negated variable
    Given the English input "P is false"
    When the input is translated
    Then the translated output should be "P'"

  Scenario: Translate a simple conjunction using 'and'
    Given the English input "P and Q are true"
    When the input is translated
    Then the translated output should be "P & Q"

  Scenario: Translate a simple disjunction using 'or'
    Given the English input "P or Q is true"
    When the input is translated
    Then the translated output should be "P | Q"

  Scenario: Translate a conjunction with a negated second term
    Given the English input "P is true and Q is false"
    When the input is translated
    Then the translated output should be "P & Q'"

  Scenario: Translate a disjunction with a negated first term
    Given the English input "P is false or Q is true"
    When the input is translated
    Then the translated output should be "P' | Q"

  Scenario: Translate a nested conjunction and disjunction
    Given the English input "P is true and (Q is true or R is true)"
    When the input is translated
    Then the translated output should be "P & (Q | R)"

  Scenario: Translate a negation of a conjunction
    Given the English input "it is not the case that P and Q are true"
    When the input is translated
    Then the translated output should be "(P & Q)'"

  Scenario: Translate a variable with multiple characters
    Given the English input "Var1 is true"
    When the input is translated
    Then the translated output should be "Var1"

  Scenario: Translate conjunction using space as separator (as per boolean.tgf)
    Given the English input "P Q are true"
    When the input is translated
    Then the translated output should be "P Q"
