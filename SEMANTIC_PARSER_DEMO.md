# Semantic Parser Enhancement Demo

## The Problem

Current parser handles only simple sentences:
- "all cats are animals" → "all c: is_cat(c) -> is_animal(c)"

But real-world requirements are much more complex:
- "Every customer who has made purchases totaling more than $1000 in the last 12 months and has no outstanding payments receives a 15% discount"

## The Solution: Semantic Lexicon

### 1. **Rich Entity Knowledge**

Instead of treating "customer" as just a word, we store semantic information:

```python
"customer": SemanticEntity(
    name="customer",
    category=EntityCategory.PERSON,
    properties={"customer_id", "loyalty_status", "purchase_history"},
    typical_actions={"purchases", "orders", "returns", "pays"},
    typical_relations={
        RelationType.OWNERSHIP: {"account", "order", "subscription"},
        RelationType.PARTICIPATION: {"transaction", "purchase"}
    }
)
```

### 2. **Domain Pattern Recognition**

The lexicon recognizes business patterns:
- "purchases totaling more than $X" → aggregate constraint
- "in the last N months" → time window
- "receives a X% discount" → consequence with parameter

### 3. **Semantic Parsing Results**

**Simple sentence:**
```
Input: "all cats are animals"
Output: "all c: is_cat(c) -> is_animal(c)"
```

**Complex business rule:**
```
Input: "Every customer who has made purchases totaling more than $1000 
        in the last 12 months and has no outstanding payments 
        receives a 15% discount"

Output: "all c: is_customer(c) && 
        (exists purchases: total(purchases, c) > 1000 
         && in_time_window(purchases, 12_months) 
         && !exists payment: (outstanding(payment) && belongs_to(payment, c))) 
        -> receives_discount(c, 15)"
```

**Rate limiting rule:**
```
Input: "When a client makes more than 100 requests per minute, 
        the system must return a rate limit error and 
        block further requests from that client for 5 minutes"

Output: "all c: is_client(c) && 
        (request_rate(c) > 100_per_minute) -> 
        (return_error() && block(c, 5_minutes))"
```

## Key Improvements

### 1. **Entity Type Understanding**
- Knows that "customer" is a person who can purchase, pay, receive discounts
- Knows that "car" is an object that can be owned, driven, require insurance
- Knows that "system" can process, validate, return errors, block access

### 2. **Relationship Inference**
- "customer who has made purchases" → ownership/participation relation
- "person who owns a car" → ownership relation
- "employee who works for company" → employment relation

### 3. **Constraint Pattern Recognition**
- Aggregations: "totaling more than", "averaging", "counting"
- Time windows: "in the last X days/months/years"
- Thresholds: "more than", "exceeds", "at least"
- Exceptions: "unless", "except when"

### 4. **Action Semantics**
- "receives" → obtains/gets (with parameter)
- "blocks" → prevents/denies (with duration)
- "pays" → financial transaction

## Architecture

```
Enhanced Parser V3
├── Semantic Lexicon
│   ├── Entity Knowledge Base
│   ├── Action/Verb Semantics
│   ├── Property/Adjective Info
│   └── Domain Pattern Library
├── Pattern Recognizers
│   ├── Business Rule Patterns
│   ├── System Constraint Patterns
│   ├── Temporal Patterns
│   └── Aggregation Patterns
└── Semantic Analyzer
    ├── Entity Type Inference
    ├── Relationship Extraction
    ├── Constraint Parsing
    └── Scope Management
```

## Examples of Complex Sentences Now Supported

1. **Multi-condition Business Rules:**
   - "Customers with gold status who spend over $500 per month get free shipping on all orders"

2. **Temporal Constraints:**
   - "If the temperature remains above 30°C for more than 3 consecutive hours, activate cooling"

3. **System Rules with Exceptions:**
   - "All users must change passwords every 90 days unless they have biometric authentication enabled"

4. **Aggregated Conditions:**
   - "Employees who complete at least 80% of assigned tasks on time for 3 consecutive months receive a performance bonus"

5. **Nested Quantifiers with Relations:**
   - "Every department that has more than 10 employees where at least half have completed certification must submit quarterly reports"

## Conclusion

By adding semantic understanding through a rich lexicon, the parser can now handle:
- Real-world business rules with multiple conditions
- Temporal constraints and time windows  
- Aggregations and thresholds
- Domain-specific patterns
- Complex entity relationships

This transforms the parser from handling toy examples to processing actual requirements and specifications found in enterprise systems.