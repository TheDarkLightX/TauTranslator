# Dictionary Population Guide - Getting Started

## How Words Are Added to the Dictionary

### 1. **Word Addition Flow**

When you add a word to the dictionary, several things happen:

```
User adds "employee" as entity
    ↓
System registers:
- Base form: "employee" 
- Plural form: "employees" (if provided)
- Synonyms: "worker", "staff" → all map to "employee"
- Category: "person" (helps parser understand behavior)
- Properties: what attributes this entity can have
- Typical verbs: what actions this entity typically does
    ↓
Parser can now understand:
- "All employees must..." 
- "Every worker who..." (synonym recognition)
- "The staff reports to..." (synonym recognition)
```

### 2. **Three Ways to Add Words**

#### Method 1: Configuration Files (Recommended for bulk additions)
```yaml
# my_company_dictionary.yaml
entities:
  employee:
    category: person
    plural_form: employees
    synonyms: [worker, staff, personnel]
    properties: [employee_id, department, salary, role]
    typical_verbs: [works, reports, manages, attends]
```

#### Method 2: Programmatic (Good for dynamic additions)
```python
parser.add_entity(
    "employee",
    category="person",
    plural_form="employees",
    synonyms=["worker", "staff"],
    properties=["employee_id", "department"],
    typical_verbs=["works", "reports"]
)
```

#### Method 3: CSV Import (Best for bulk data from spreadsheets)
```csv
name,category,plural,synonyms,properties,verbs
employee,person,employees,worker|staff,employee_id|department,works|reports
manager,person,managers,supervisor|boss,team|department,manages|approves
```

## Building Your Initial Dictionary

### Step 1: Identify Your Domain

First, determine what domain you're working in. This helps organize vocabulary:

- **Business/Enterprise**: employees, departments, policies, processes
- **Healthcare**: patients, medications, symptoms, treatments  
- **Finance**: accounts, transactions, investments, currencies
- **Legal**: contracts, clauses, parties, obligations
- **Technical**: systems, databases, APIs, services

### Step 2: Core Entity Identification

Start by listing the main "things" in your domain:

```yaml
# TEMPLATE: Start with 5-10 core entities
entities:
  # People/Roles
  employee:
    category: person
    plural_form: employees
    
  manager:
    category: person
    plural_form: managers
    
  # Objects/Things  
  product:
    category: object
    plural_form: products
    
  # Documents/Data
  report:
    category: document
    plural_form: reports
    
  # Systems
  database:
    category: system
    plural_form: databases
```

### Step 3: Add Relationships Through Verbs

For each entity, think about what it DOES:

```yaml
verbs:
  # What do employees do?
  works:
    typical_subjects: [employee, worker]
    typical_objects: [project, task]
    
  reports:
    past_tense: reported
    typical_subjects: [employee, manager]
    typical_objects: [issue, progress, manager]
    prepositions: [to]  # "reports to"
    
  # What do systems do?
  processes:
    typical_subjects: [system, application]
    typical_objects: [request, data, transaction]
```

### Step 4: Add Properties and Attributes

What describes these entities?

```yaml
entities:
  employee:
    properties: 
      - employee_id      # Unique identifier
      - department       # Organizational unit
      - hire_date       # Temporal property
      - status          # active/inactive
      - clearance_level # Domain-specific
```

### Step 5: Create Synonyms and Variations

Think about how people actually talk:

```yaml
entities:
  customer:
    synonyms: 
      - client         # Formal variation
      - consumer       # Industry term
      - buyer          # Functional synonym
      - purchaser      # Formal synonym
      - account holder # Role-based synonym
```

## Starter Dictionary Templates

### 1. **Minimal Business Starter** (~ 20 words)

```yaml
# business_starter.yaml
entities:
  # People
  employee:
    category: person
    plural_form: employees
    synonyms: [worker, staff]
    
  customer:
    category: person  
    plural_form: customers
    synonyms: [client, buyer]
    
  manager:
    category: person
    plural_form: managers
    synonyms: [supervisor, boss]
    
  # Things
  product:
    category: object
    plural_form: products
    synonyms: [item, goods]
    
  order:
    category: document
    plural_form: orders
    synonyms: [purchase]
    
  # Abstract
  payment:
    category: event
    plural_form: payments
    synonyms: [transaction]

verbs:
  purchases:
    past_tense: purchased
    synonyms: [buys, orders]
    
  manages:
    past_tense: managed
    synonyms: [supervises, oversees]
    
  processes:
    past_tense: processed
    synonyms: [handles]

abbreviations:
  CEO: chief executive officer
  HR: human resources
  IT: information technology
```

### 2. **Comprehensive Starter** (~ 100 words)

```yaml
# comprehensive_starter.yaml
entities:
  # === PEOPLE/ROLES ===
  person:
    category: person
    plural_form: people
    synonyms: [individual, human]
    
  user:
    category: person
    plural_form: users
    synonyms: [operator, account-holder]
    
  employee:
    category: person
    plural_form: employees
    synonyms: [worker, staff, personnel]
    properties: [id, department, role, status]
    
  customer:
    category: person
    plural_form: customers
    synonyms: [client, consumer, buyer]
    properties: [id, status, history]
    
  manager:
    category: person
    plural_form: managers
    synonyms: [supervisor, boss, lead]
    
  # === OBJECTS/THINGS ===
  system:
    category: system
    plural_form: systems
    synonyms: [application, platform, service]
    properties: [status, version, configuration]
    
  database:
    category: system
    plural_form: databases
    synonyms: [db, datastore]
    properties: [schema, size, type]
    
  product:
    category: object
    plural_form: products
    synonyms: [item, merchandise, goods]
    properties: [sku, price, stock]
    
  # === DOCUMENTS/DATA ===
  document:
    category: document
    plural_form: documents
    synonyms: [file, record]
    properties: [type, status, version]
    
  report:
    category: document
    plural_form: reports
    properties: [type, period, status]
    
  # === EVENTS/ACTIONS ===
  transaction:
    category: event
    plural_form: transactions
    properties: [amount, date, status]
    
  payment:
    category: event
    plural_form: payments
    properties: [amount, method, status]

verbs:
  # === OWNERSHIP/POSSESSION ===
  owns:
    past_tense: owned
    synonyms: [has, possesses]
    
  # === ACTIONS ===
  creates:
    past_tense: created
    synonyms: [makes, generates, produces]
    
  updates:
    past_tense: updated
    synonyms: [modifies, changes, edits]
    
  deletes:
    past_tense: deleted
    synonyms: [removes, erases]
    
  # === BUSINESS ACTIONS ===
  purchases:
    past_tense: purchased
    synonyms: [buys, orders, acquires]
    
  sells:
    past_tense: sold
    synonyms: [vends, markets]
    
  # === SYSTEM ACTIONS ===
  processes:
    past_tense: processed
    synonyms: [handles, executes]
    
  validates:
    past_tense: validated
    synonyms: [verifies, checks]

patterns:
  # Time patterns
  time_window:
    pattern: "in the (?:last|past|next) (\\d+) (days?|weeks?|months?|years?)"
    replacement: "time_window(\\1, \\2)"
    
  # Comparison patterns
  greater_than:
    pattern: "(?:more|greater) than (\\d+)"
    replacement: "> \\1"
    
  # Status patterns
  has_status:
    pattern: "with status ['\"]?(\\w+)['\"]?"
    replacement: "status = \\1"

abbreviations:
  API: application programming interface
  DB: database
  UI: user interface
  CEO: chief executive officer
  CFO: chief financial officer
  HR: human resources
  IT: information technology
  QA: quality assurance
```

## Quick Population Strategies

### 1. **Domain Analysis Method**

1. List 10 key sentences from your domain
2. Extract all nouns → entities
3. Extract all verbs → actions
4. Identify relationships

Example:
```
"All employees who report to managers must submit timesheets"
Entities: employees, managers, timesheets
Verbs: report (to), submit
Relationship: employees --report to--> managers
```

### 2. **Spreadsheet Import Method**

Create a spreadsheet with your vocabulary, then export as CSV:

| name | category | plural | synonyms | typical_verbs |
|------|----------|---------|----------|---------------|
| developer | person | developers | programmer,coder | writes,tests,deploys |
| code | object | - | source,program | compiles,runs,executes |
| bug | object | bugs | defect,issue | causes,occurs,fixes |

### 3. **Incremental Building**

Start minimal and add as you parse:

```python
# Start with empty dictionary
parser = create_extensible_parser()

# Try to parse
result = parser.parse("All developers must test code")
# If it fails on "developers", add it:

parser.add_entity("developer", category="person", 
                 plural_form="developers",
                 typical_verbs=["writes", "tests"])

# Try again - success!
```

### 4. **Copy from Existing Ontologies**

Use existing vocabularies as starting points:

- **Schema.org**: Standard web vocabularies
- **WordNet**: General English meanings
- **Domain Ontologies**: Industry-specific terms
- **Company Glossaries**: Internal terminology

## Auto-Population Tools

### 1. **Extract from Documents**

```python
def extract_vocabulary_from_docs(documents):
    """Extract potential entities and verbs from documents."""
    import nltk
    
    entities = set()
    verbs = set()
    
    for doc in documents:
        # Tokenize and tag parts of speech
        tokens = nltk.word_tokenize(doc)
        pos_tags = nltk.pos_tag(tokens)
        
        for word, pos in pos_tags:
            if pos.startswith('NN'):  # Nouns
                entities.add(word.lower())
            elif pos.startswith('VB'):  # Verbs
                verbs.add(word.lower())
    
    return entities, verbs
```

### 2. **Import from Glossary**

```python
def import_glossary(glossary_file):
    """Import from company glossary format."""
    dictionary = {}
    
    with open(glossary_file) as f:
        for line in f:
            if ':' in line:
                term, definition = line.split(':', 1)
                # Parse definition for category hints
                if any(word in definition.lower() 
                       for word in ['person', 'employee', 'user']):
                    category = 'person'
                elif any(word in definition.lower() 
                         for word in ['system', 'application']):
                    category = 'system'
                else:
                    category = 'object'
                    
                dictionary[term.strip()] = {
                    'category': category,
                    'description': definition.strip()
                }
    
    return dictionary
```

## Best Practices for Dictionary Building

### 1. **Start Small, Grow Organically**
- Begin with 10-20 core terms
- Add new terms as you encounter them
- Review and refine quarterly

### 2. **Be Consistent**
- Use consistent categories
- Follow naming conventions
- Document your choices

### 3. **Think in Relationships**
- What does X do to Y?
- What properties does X have?
- What states can X be in?

### 4. **Test Your Dictionary**
```python
# Test sentences that should work
test_sentences = [
    "All employees must complete training",
    "Every manager who supervises employees reviews performance",
    "No customer can access restricted data"
]

for sentence in test_sentences:
    result = parser.parse(sentence)
    print(f"✓ {sentence}")
    print(f"  → {result}")
```

### 5. **Version Your Dictionary**
```yaml
# my_dictionary_v1.yaml
metadata:
  version: "1.0"
  created: "2024-01-15"
  author: "Team Name"
  description: "Initial vocabulary for project X"
  
entities:
  # ... your entities ...
```

## Example: Building a Dictionary for a Specific Project

Let's say you're building a dictionary for an e-commerce platform:

```yaml
# ecommerce_dictionary.yaml
domain: ecommerce

# Step 1: Core entities (the main "things")
entities:
  customer:
    category: person
    synonyms: [shopper, buyer, user]
    properties: [customer_id, email, shipping_address]
    typical_verbs: [browses, purchases, reviews, returns]
    
  product:
    category: object
    synonyms: [item, merchandise, sku]
    properties: [price, stock_level, category, rating]
    
  order:
    category: document
    properties: [order_id, total, status, date]
    typical_verbs: [contains, ships, delivers]
    
  cart:
    category: object
    synonyms: [basket, shopping_cart]
    properties: [items, total, session_id]

# Step 2: Key actions in the domain
verbs:
  purchases:
    past_tense: purchased
    typical_subjects: [customer]
    typical_objects: [product, item]
    
  adds:
    past_tense: added
    typical_subjects: [customer, user]
    typical_objects: [product, item]
    prepositions: [to]  # "adds to cart"
    
  checkout:
    past_tense: checked_out
    typical_subjects: [customer]
    
# Step 3: Domain patterns
patterns:
  price_range:
    pattern: "between \\$(\\d+) and \\$(\\d+)"
    replacement: "price >= \\1 && price <= \\2"
    
  discount:
    pattern: "(\\d+)% (?:off|discount)"
    replacement: "discount(\\1)"

# Step 4: Common abbreviations
abbreviations:
  SKU: stock keeping unit
  B2C: business to consumer
  COD: cash on delivery
```

This gives your parser immediate understanding of e-commerce concepts!