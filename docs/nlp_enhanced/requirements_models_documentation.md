# Documentation: Requirements Analyzer Data Models

**File:** `src/tau_translator_omega/core_engine/translators/nlp_enhanced/requirements_models.py`

This document provides a detailed explanation of the data models used by the Requirements Analyzer. These models are crucial for structuring the information extracted from natural language requirements into a machine-readable format.

---

## 1. Enumerations

Enumerations are used to define a set of named constants for requirement types and categories, ensuring consistency and preventing errors from using plain strings.

### `RequirementType(Enum)`

Defines the specific functional or non-functional type of an individual requirement.

- **`CONSTRAINT`**: A mandatory rule or condition that the system must satisfy (e.g., "The password must be at least 8 characters long").
- **`BEHAVIOR`**: Describes how the system should act or respond to certain inputs or conditions (e.g., "The system shall log out the user after 15 minutes of inactivity").
- **`PERFORMANCE`**: A requirement related to timing, throughput, or resource usage (e.g., "The API response time must be under 200ms").
- **`VALIDATION`**: A rule for validating user input or data integrity (e.g., "The email address must be in a valid format").
- **`OUTPUT`**: Specifies the format or content of system output (e.g., "The report must be generated in PDF format").
- **`SECURITY`**: A requirement related to security, access control, or data protection (e.g., "All user data must be encrypted at rest").
- **`EXCEPTION`**: Defines how the system should handle errors or exceptional cases (e.g., "If the database is unavailable, the system shall display a maintenance message").

### `RequirementCategory(Enum)`

Defines the high-level category of a requirement.

- **`FUNCTIONAL`**: Pertains to the system's features and functionality.
- **`NON_FUNCTIONAL`**: Relates to the system's quality attributes, such as performance, security, or usability.
- **`UI_UX`**: Specific to the user interface and user experience.
- **`UNCATEGORIZED`**: Used for requirements that do not fit into the other categories.

---

## 2. Data Classes

Data classes are used to create lightweight, immutable structures for holding extracted data.

### `LogicalStructure`

Represents the logical and temporal structure identified within a requirement's text.

- **`quantifiers` (`List[str]`):** Stores universal or existential quantifiers (e.g., "all", "any", "every").
- **`conditionals` (`List[str]`):** Stores conditional phrases (e.g., "if...then", "when").
- **`logical_operators` (`List[str]`):** Stores logical connectives (e.g., "and", "or", "not").
- **`temporal_operators` (`List[str]`):** Stores temporal operators (e.g., "always", "eventually", "until").
- **`has_quantification` (`bool`):** A flag indicating if any quantifiers were found.
- **`has_conditionals` (`bool`):** A flag indicating if any conditionals were found.
- **`has_temporal` (`bool`):** A flag indicating if any temporal operators were found.

### `FormalConstraint`

Represents a requirement that has been partially translated into a formal, structured representation.

- **`constraint_type` (`str`):** The type of constraint (e.g., "temporal", "logical").
- **`variables` (`List[str]`):** A list of variables involved in the constraint.
- **`predicates` (`List[str]`):** A list of predicates or actions.
- **`logical_form` (`str`):** A semi-formal representation of the constraint's logic (e.g., "always(request -> response)").
- **`confidence` (`float`):** The model's confidence score (0.0 to 1.0) for the accuracy of the extracted constraint.

### `RequirementItem`

This is the main data model that aggregates all extracted information for a single requirement.

- **`raw_text` (`str`):** The original, unprocessed requirement text.
- **`type` (`RequirementType`):** The specific type of the requirement.
- **`category` (`RequirementCategory`):** The high-level category.
- **`entities` (`List[str]`):** A list of key nouns or actors identified.
- **`predicates` (`List[str]`):** A list of key verbs or actions.
- **`logical_structure` (`LogicalStructure`):** The identified logical structure of the text.
- **`formal_constraints` (`List[FormalConstraint]`):** A list of formal constraints extracted from the text.
- **`confidence` (`float`):** The overall confidence score for the entire extraction.
- **`has_quantification` (`bool`):** A convenience flag, often derived from `logical_structure`, indicating the presence of quantification.
