# User Dictionary Guide for TCE Parser

## Overview

The TCE Parser now supports user-defined dictionaries, allowing you to:
- Add domain-specific vocabulary
- Define custom entities and their properties
- Create synonyms and abbreviations
- Define parsing patterns for complex expressions

## Quick Start

### 1. Create a Simple Dictionary File

Create a YAML file (e.g., `my_dictionary.yaml`):

```yaml
entities:
  employee:
    category: person
    plural_form: employees
    synonyms: [worker, staff]
    properties: [employee_id, department]
    typical_verbs: [works, manages, reports]
  
  database:
    category: system
    synonyms: [db, datastore]
    properties: [schema, tables, connections]

verbs:
  queries:
    past_tense: queried
    typical_subjects: [user, application]
    typical_objects: [database, table]

abbreviations:
  DB: database
  API: application programming interface
  CEO: chief executive officer
```

### 2. Load the Dictionary

```python
from backend.unified.enhanced_tce_parser_extensible import create_extensible_parser

# Create parser with dictionary
parser = create_extensible_parser()
parser.load_dictionary("my_dictionary.yaml")

# Parse using your vocabulary
result = parser.parse("All employees who query the DB must have permissions")
```

## Dictionary File Formats

### YAML Format (Recommended)

Most readable and flexible format:

```yaml
# Domain-specific vocabulary
domain: healthcare
entities:
  patient:
    category: person
    properties: [medical_id, age, conditions]
    synonyms: [client, individual]
    typical_verbs: [visits, receives, consents]
  
  medication:
    category: object
    plural_form: medications
    properties: [dosage, frequency]
    synonyms: [drug, medicine]

verbs:
  prescribes:
    past_tense: prescribed
    typical_subjects: [doctor, physician]
    typical_objects: [medication, treatment]

patterns:
  dosage_pattern:
    pattern: "([0-9]+)\\s*mg\\s+every\\s+([0-9]+)\\s+hours?"
    replacement: "dosage(\\1mg, \\2h)"
    examples: ["10mg every 4 hours", "5 mg every 12 hours"]

abbreviations:
  BP: blood pressure
  mg: milligrams
```

### JSON Format

Good for programmatic generation:

```json
{
  "domain": "finance",
  "entities": {
    "account": {
      "category": "object",
      "properties": ["balance", "account_number"],
      "typical_verbs": ["holds", "transfers"]
    },
    "transaction": {
      "category": "event",
      "properties": ["amount", "date", "type"],
      "synonyms": ["transfer", "payment"]
    }
  },
  "verbs": {
    "transfers": {
      "past_tense": "transferred",
      "typical_subjects": ["account", "user"],
      "typical_objects": ["money", "funds"]
    }
  },
  "abbreviations": {
    "APR": "annual percentage rate",
    "ATM": "automated teller machine"
  }
}
```

### CSV Format

Simple format for bulk entity/verb imports:

**entities.csv:**
```csv
name,category,plural,synonyms,properties,verbs
customer,person,customers,client|consumer,customer_id|status,purchases|orders|returns
product,object,products,item|merchandise,sku|price|stock,sells|ships
order,document,orders,purchase|transaction,order_id|total|status,contains|ships
```

**verbs.csv:**
```csv
verb,past_tense,synonyms,subjects,objects
purchases,purchased,buys|orders,customer|user,product|service
manages,managed,oversees|handles,employee|manager,project|team
processes,processed,handles|executes,system|application,request|data
```

## Runtime Dictionary Usage

### Adding Entities Programmatically

```python
parser = create_extensible_parser()

# Add a custom entity
parser.add_entity(
    "robot",
    category="system",
    plural_form="robots",
    synonyms=["bot", "automaton"],
    properties=["model", "capabilities"],
    typical_verbs=["performs", "executes", "navigates"]
)

# Now the parser understands robots
result = parser.parse("All robots must perform safety checks")
```

### Adding Verbs

```python
parser.add_verb(
    "analyzes",
    past_tense="analyzed",
    synonyms=["examines", "evaluates"],
    typical_subjects=["system", "analyst"],
    typical_objects=["data", "report", "performance"]
)
```

### Adding Custom Patterns

```python
# Add a pattern for time durations
parser.add_pattern(
    "duration_pattern",
    pattern=r"for\s+(\d+)\s+(seconds?|minutes?|hours?|days?)",
    replacement=r"duration(\1, \2)",
    description="Time duration pattern"
)

# Now it can parse: "block user for 5 minutes"
# Result: "block(user) && duration(5, minutes)"
```

## Domain-Specific Dictionaries

### Healthcare Example

```yaml
domain: healthcare
entities:
  physician:
    category: person
    synonyms: [doctor, MD, practitioner]
    typical_verbs: [diagnoses, prescribes, treats, refers]
  
  symptom:
    category: abstract
    plural_form: symptoms
    properties: [severity, duration, location]
    
  diagnosis:
    category: abstract
    plural_form: diagnoses
    properties: [code, confidence, date]

patterns:
  symptom_duration:
    pattern: "experiencing\\s+(\\w+)\\s+for\\s+(\\d+)\\s+(days?|weeks?)"
    replacement: "symptom(\\1, duration(\\2, \\3))"
    
abbreviations:
  Rx: prescription
  Dx: diagnosis
  Hx: history
```

### Legal Domain Example

```yaml
domain: legal
entities:
  contract:
    category: document
    properties: [parties, terms, effective_date]
    typical_verbs: [signs, executes, breaches, terminates]
    
  clause:
    category: abstract
    properties: [type, section, enforceability]

verbs:
  obligates:
    typical_subjects: [contract, agreement, law]
    typical_objects: [party, entity, person]
    
patterns:
  legal_reference:
    pattern: "pursuant\\s+to\\s+([Ss]ection\\s+\\d+\\.\\d+)"
    replacement: "reference(\\1)"
```

## Best Practices

### 1. Use Meaningful Categories

- `person`: humans, users, roles
- `object`: physical things, tangible items
- `system`: software, applications, services
- `document`: files, records, reports
- `event`: actions, occurrences, transactions
- `abstract`: concepts, properties, states

### 2. Define Relationships

Use `typical_verbs` and `typical_subjects/objects` to help the parser understand relationships:

```yaml
entities:
  manager:
    category: person
    typical_verbs: [supervises, approves, assigns]
    
verbs:
  supervises:
    typical_subjects: [manager, supervisor]
    typical_objects: [employee, team, project]
```

### 3. Create Useful Patterns

Patterns should capture domain-specific expressions:

```yaml
patterns:
  price_threshold:
    pattern: "priced?\\s+(?:at|above|below)\\s+\\$([0-9,]+(?:\\.[0-9]{2})?)"
    replacement: "price_constraint(\\1)"
    examples: ["priced at $99.99", "price above $1,000"]
```

### 4. Document Your Dictionary

Add descriptions and examples:

```yaml
patterns:
  api_rate_limit:
    pattern: "([0-9]+)\\s+requests?\\s+per\\s+(second|minute|hour)"
    replacement: "rate_limit(\\1, \\2)"
    description: "Matches API rate limit expressions"
    examples:
      - "100 requests per second"
      - "5000 requests per hour"
```

## Troubleshooting

### Pattern Not Matching

1. Check regex syntax - test at regex101.com
2. Ensure case-insensitive flag is appropriate
3. Look for typos in pattern

### Entity Not Recognized

1. Check synonyms are defined
2. Verify plural forms
3. Ensure dictionary is loaded

### Debugging

```python
# Check if entity is loaded
entity_info = parser.get_entity_info("employee")
if entity_info:
    print(f"Entity found: {entity_info}")
    
# Check if verb is loaded
verb_info = parser.get_verb_info("manages")
if verb_info:
    print(f"Verb found: {verb_info}")
```

## Example: Building a Complete Domain Dictionary

Here's a complete example for a project management domain:

```yaml
domain: project_management
entities:
  project:
    category: object
    plural_form: projects
    properties: [name, deadline, budget, status]
    synonyms: [initiative, effort]
    typical_verbs: [starts, completes, delays, delivers]
    
  milestone:
    category: event
    properties: [date, deliverables, status]
    typical_verbs: [reaches, misses, achieves]
    
  developer:
    category: person
    plural_form: developers
    synonyms: [programmer, engineer, coder]
    properties: [skills, experience, team]
    typical_verbs: [codes, tests, deploys, debugs]
    
  task:
    category: object
    plural_form: tasks
    synonyms: [ticket, issue, work-item]
    properties: [priority, assignee, status, estimate]

verbs:
  assigns:
    past_tense: assigned
    typical_subjects: [manager, lead, system]
    typical_objects: [task, project, developer]
    
  completes:
    past_tense: completed
    synonyms: [finishes, concludes, delivers]
    typical_subjects: [developer, team]
    typical_objects: [task, project, milestone]

patterns:
  deadline_pattern:
    pattern: "(?:by|before)\\s+(\\d{4}-\\d{2}-\\d{2}|today|tomorrow|next\\s+\\w+)"
    replacement: "deadline(\\1)"
    
  priority_pattern:
    pattern: "(high|medium|low)\\s+priority"
    replacement: "priority(\\1)"
    
  completion_rate:
    pattern: "(\\d+)%\\s+(?:complete|done|finished)"
    replacement: "completion_rate(\\1)"

abbreviations:
  PM: project manager
  QA: quality assurance
  MVP: minimum viable product
  ETA: estimated time of arrival
```

Save this as `project_management.yaml` and load it to parse project-related sentences accurately!