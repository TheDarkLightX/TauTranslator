Feature: Natural Language to CNL to TAU Translation
  As a user
  I want to translate from natural language to CNL (TCE) and then to TAU
  So that I can express ideas naturally and get formal logic representations

  Background:
    Given the translation system is initialized
    And the NLP engine is loaded
    And the vocabulary includes common concepts

  @nlp @translation @user_story
  Scenario: Translate natural English to TCE to TAU
    Given I have natural language input "The sun is always hot"
    When I translate from natural language to TCE
    Then the TCE output should be "Always sun is hot."
    When I translate the TCE to TAU
    Then the TAU output should be "□hot(sun)"
    And the translation chain should have no errors

  @nlp @translation @user_story
  Scenario: Translate conditional statement from natural language
    Given I have natural language input "If it's raining, then the ground is wet"
    When I translate from natural language to TCE
    Then the TCE output should be "raining implies ground is wet."
    When I translate the TCE to TAU
    Then the TAU output should be "raining → wet(ground)"
    And the translation chain should have no errors

  @nlp @translation @user_story
  Scenario: Translate quantified statement from natural language
    Given I have natural language input "All birds can fly"
    When I translate from natural language to TCE
    Then the TCE output should be "Always x is bird implies x can fly."
    When I translate the TCE to TAU
    Then the TAU output should be "∀x(bird(x) → can_fly(x))"
    And the translation chain should have no errors

  @nlp @translation @bidirectional
  Scenario: Full round-trip translation natural -> TCE -> TAU -> TCE -> natural
    Given I have natural language input "Every student has a teacher"
    When I translate from natural language to TCE
    Then the TCE output should be "Always student exists teacher such that has(student, teacher)."
    When I translate the TCE to TAU
    Then the TAU output should be "∀student∃teacher(has(student, teacher))"
    When I translate the TAU back to TCE
    Then the TCE output should be "Always student exists teacher such that has(student, teacher)."
    When I translate the TCE back to natural language
    Then the natural language output should be semantically equivalent to "Every student has a teacher"

  @nlp @translation @user_story
  Scenario: Handle ambiguous natural language
    Given I have natural language input "The bank is near the river"
    When I translate from natural language to TCE
    Then the system should recognize potential ambiguity
    And provide clarification options for "bank"
    When I select "financial institution" for "bank"
    Then the TCE output should be "financial_institution is near river."
    When I translate the TCE to TAU
    Then the TAU output should be "near(financial_institution, river)"

  @nlp @translation @user_story
  Scenario Outline: Translate common natural language patterns
    Given I have natural language input "<natural_input>"
    When I translate from natural language to TCE
    Then the TCE output should be "<tce_output>"
    When I translate the TCE to TAU
    Then the TAU output should be "<tau_output>"

    Examples:
      | natural_input                          | tce_output                                  | tau_output                           |
      | John loves Mary                        | John loves Mary.                            | loves(John, Mary)                    |
      | Someone is happy                       | Sometimes x is happy.                       | ∃x(happy(x))                        |
      | Nobody is perfect                      | Always x implies not perfect(x).            | ∀x(¬perfect(x))                     |
      | If you work hard, you will succeed    | work_hard(you) implies succeed(you).        | work_hard(you) → succeed(you)       |
      | Either it's day or it's night         | day or night.                               | day ∨ night                         |

  @nlp @error_handling
  Scenario: Handle grammatically incorrect natural language
    Given I have natural language input "The cat are sleeping on mat"
    When I translate from natural language to TCE
    Then the system should provide grammar correction suggestions
    And suggest "The cat is sleeping on the mat"
    When I accept the correction
    Then the TCE output should be "cat is sleeping on mat."

  @nlp @context
  Scenario: Use context for pronoun resolution
    Given I have established context "John is a student. Mary is a teacher."
    And I have natural language input "He studies hard and she teaches well"
    When I translate from natural language to TCE with context
    Then the TCE output should be "John studies hard and Mary teaches well."
    When I translate the TCE to TAU
    Then the TAU output should be "studies_hard(John) ∧ teaches_well(Mary)"