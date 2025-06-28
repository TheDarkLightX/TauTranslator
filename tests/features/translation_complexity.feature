Feature: Translation complexity ladder for English -> Tau Language
  Verifies how well the translation pipeline copes with increasingly complex and ambiguous English sentences.

  Background:
    Given the Tau translator is initialised

  @complexity
  Scenario Outline: Translate English sentence with complexity level <level>
    When I translate "<sentence>"
    Then the translation should succeed

    Examples:
      | level | sentence |
      | 0 | The sensor is active. |
      | 1 | The door is locked and the alarm is armed. |
      | 2 | Every user who has administrator privileges must authenticate with two factors. |
      | 3 | Each transaction that exceeds ten-thousand credits shall be logged before completion. |
      | 4 | If the temperature rises above eighty degrees, the cooling system shall activate within five seconds. |
      | 5 | I toggled the switch with the remote control. |
