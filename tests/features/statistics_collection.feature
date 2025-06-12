Feature: Translation Statistics Collection
  As a system administrator
  I want to track translation performance metrics
  So that I can monitor system health and optimize performance

  Background:
    Given a translation statistics service is initialized
    And no prior translation metrics exist

  Scenario: Recording successful translation
    Given an engine "pattern_based" exists
    When a translation request succeeds with:
      | direction       | to_tau      |
      | processing_time | 0.1 seconds |
      | confidence      | 0.85        |
    Then the total translations count should be 1
    And the successful translations count should be 1
    And the engine success rate should be 100%
    And the average processing time should be 0.1 seconds

  Scenario: Recording failed translation
    Given an engine "grammar_based" exists
    When a translation request fails with:
      | direction  | to_tau      |
      | error_type | PARSE_ERROR |
    Then the total translations count should be 1
    And the failed translations count should be 1
    And the engine success rate should be 0%
    And the error count for "PARSE_ERROR" should be 1

  Scenario: Performance metrics calculation
    Given multiple translation requests have been recorded
    When I request performance metrics for the last 1 hour
    Then I should receive:
      | average_response_time |
      | p95_response_time     |
      | requests_per_hour     |
      | success_rate          |

  Scenario: Thread-safe concurrent access
    Given multiple threads are recording translations simultaneously
    When 100 translations are recorded concurrently
    Then the total count should be exactly 100
    And no data corruption should occur
    And all metrics should be consistent

  Scenario: Multiple engine tracking
    Given engines "pattern_based" and "grammar_based" exist
    When translations are recorded for both engines:
      | engine         | direction | success | processing_time |
      | pattern_based  | to_tau    | true    | 0.1            |
      | pattern_based  | to_tce    | true    | 0.15           |
      | grammar_based  | to_tau    | false   | 0.0            |
    Then the overall success rate should be 66.67%
    And "pattern_based" should have 100% success rate
    And "grammar_based" should have 0% success rate

  Scenario: Error analysis aggregation
    Given multiple translation failures occur
    When errors are recorded:
      | engine        | error_type    | count |
      | pattern_based | PARSE_ERROR   | 3     |
      | pattern_based | TIMEOUT_ERROR | 1     |
      | grammar_based | PARSE_ERROR   | 2     |
    Then the most common error should be "PARSE_ERROR"
    And the total error count should be 6
    And "PARSE_ERROR" should occur 5 times across all engines

  Scenario: Metrics history size limit
    Given a statistics service with history limit of 10
    When 15 translation metrics are recorded
    Then the metrics history should contain only 10 entries
    And the total translation count should be 15
    And the oldest metrics should be automatically removed

  Scenario: Performance time window filtering
    Given translations recorded at different times:
      | time_offset | engine        | success |
      | -25 hours   | pattern_based | true    |
      | -1 hour     | pattern_based | true    |
      | -30 minutes | grammar_based | true    |
    When I request performance metrics for the last 24 hours
    Then only 2 translations should be included
    And the older translation should be excluded

  Scenario: Statistics reset functionality
    Given multiple translations have been recorded
    And engines have accumulated statistics
    When the statistics are reset
    Then all counters should return to zero
    And the metrics history should be empty
    And engine statistics should be cleared
    And the session start time should be updated

  Scenario: Confidence score weighted averaging
    Given an engine "pattern_based" exists
    When translations are recorded with confidence scores:
      | confidence |
      | 0.8        |
      | 1.0        |
      | 0.6        |
    Then the average confidence should be calculated using weighted averaging
    And recent translations should have higher weight in the average