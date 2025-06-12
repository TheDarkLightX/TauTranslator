# Complex English Parser - Development Plan & Testing Strategy

## 🎯 Current Status

We successfully implemented a `ComplexEnglishParser` that can handle:
- ✅ Basic quantifiers (all, every, some)
- ✅ Simple relative clauses (who owns a car)
- ✅ Basic coreference resolution (the car → a car)
- ✅ Simple conditionals (if...then)
- ✅ Binary relations (owns, has)

**Target sentence achieved:**
```
"for every person who owns a car, if the car is red then the person must pay extra"
→ ∀x: (person(x) → own(x, y))
```

## 📋 Next Phase: Push Complexity Limits

### 1. **Linguistic Structures to Test**

#### Level 1: Multiple Nested Relative Clauses
- "Every student who takes a class that is taught by a professor who has a PhD must submit assignments"
- "All companies that manufacture products which contain chemicals that harm the environment must pay fines"

#### Level 2: Multiple Coreference Chains
- "Every person who owns a car must register it, and if they fail to register it, they must pay a fine"
- "When a student takes a test and the test is difficult, the student may request that the test be regraded"

#### Level 3: Nested Quantifiers with Different Scopes
- "For every teacher, there exists at least one student such that the student admires the teacher"
- "There exists a book such that every person who reads the book recommends it to someone"

#### Level 4: Complex Temporal Relations
- "Every employee who worked at the company before it was acquired still has their benefits"
- "All students who will graduate next year must have completed their thesis by December"

#### Level 5: Disjunctive and Conjunctive Conditions
- "Every person who owns a car or a motorcycle and lives in the city must pay parking fees"
- "All employees who either work remotely or have been with the company for over 5 years receive additional benefits"

#### Level 6: Negation and Exception Handling
- "Every student except those who have a medical exemption must attend all classes"
- "No person who does not have a license may drive a car"
- "All cars that are not electric must pay an additional tax unless they are vintage"

#### Level 7: Comparative and Superlative Constructions
- "Every employee who earns more than their manager must be reviewed"
- "The student who scores the highest on the test receives a prize"
- "All buildings taller than 50 meters must have safety inspections"

#### Level 8: Modal Verb Combinations
- "Every person who might want to travel abroad should have a passport"
- "All students who could have submitted their work early will receive bonus points"
- "Anyone who must leave early shall notify their supervisor"

#### Level 9: Recursive and Self-Referential Structures
- "Every person who knows someone who knows the mayor can request a meeting"
- "All committees that oversee other committees which regulate themselves must be audited"

#### Level 10: Multi-Clause Coordinated Sentences
- "Every company that hires employees who work in states where the minimum wage is above $15 per hour, and those employees work more than 30 hours per week, must provide health insurance, unless the company has fewer than 50 employees or the employees are contractors"

### 2. **Testing Framework Enhancements Needed**

```python
@dataclass
class ComplexityFeatures:
    """Detailed breakdown of linguistic complexity."""
    quantifier_depth: int  # Nesting level of quantifiers
    relative_clause_count: int
    coreference_chains: int
    conditional_depth: int
    negation_count: int
    modal_verb_count: int
    coordination_level: int  # and/or complexity
    temporal_markers: int
    comparison_operators: int
    exception_clauses: int
    
    def complexity_score(self) -> float:
        """Calculate overall complexity score."""
        return sum([
            self.quantifier_depth * 3,
            self.relative_clause_count * 2,
            self.coreference_chains * 2.5,
            self.conditional_depth * 2,
            self.negation_count * 1.5,
            self.modal_verb_count * 1,
            self.coordination_level * 2,
            self.temporal_markers * 1.5,
            self.comparison_operators * 1,
            self.exception_clauses * 3
        ])
```

### 3. **Parser Enhancements Required**

#### A. Enhanced Entity Resolution
- Track multiple entity types (person, car, company, etc.)
- Handle plural entities and sets
- Manage entity properties and states over time

#### B. Advanced Scope Management
```python
class ScopeManager:
    def __init__(self):
        self.scope_stack = []
        self.variable_bindings = {}
        self.quantifier_precedence = []
    
    def enter_scope(self, quantifier_type, variable, domain):
        """Enter a new quantifier scope."""
        pass
    
    def resolve_variable(self, name):
        """Resolve variable in current scope."""
        pass
```

#### C. Temporal Logic Support
- Past/present/future tense handling
- Temporal operators (before, after, during)
- State changes over time

#### D. Exception and Negation Handling
- "except", "unless", "without" clauses
- Negative quantifiers ("no", "none")
- Double negation resolution

### 4. **Formal Specification Format**

```yaml
test_case:
  id: "complex_001"
  category: "nested_quantifiers_with_exceptions"
  
  input:
    sentence: "Every person who owns a car, except those who live in rural areas, must register it"
    
  expected_parse:
    logical_form: "∀x: (person(x) ∧ ∃y: (car(y) ∧ owns(x,y)) ∧ ¬rural_resident(x) → must_register(x,y))"
    
  linguistic_features:
    - universal_quantification
    - existential_quantification
    - relative_clause
    - exception_clause
    - modal_obligation
    - coreference_resolution
    
  complexity_metrics:
    quantifier_depth: 2
    relative_clauses: 1
    exception_clauses: 1
    coreferences: 1
    
  expected_entities:
    - {type: "person", quantifier: "universal", variable: "x"}
    - {type: "car", quantifier: "existential", variable: "y"}
    
  expected_predicates:
    - owns(x, y)
    - rural_resident(x)
    - must_register(x, y)
```

### 5. **Test Implementation Strategy**

#### Phase 1: Systematic Feature Testing
1. Test each linguistic feature in isolation
2. Test pairs of features
3. Test combinations of 3+ features
4. Identify failure patterns

#### Phase 2: Real-World Sentence Testing
1. Legal documents
2. Technical specifications
3. Business requirements
4. Academic papers
5. Government regulations

#### Phase 3: Stress Testing
1. Extremely long sentences (100+ words)
2. Deeply nested structures (5+ levels)
3. Multiple coreference chains
4. Ambiguous constructions

### 6. **Expected Failure Points**

Based on current implementation, we expect failures at:

1. **Ambiguous Pronoun Resolution**
   - "Every person who knows someone who likes them"
   - "them" could refer to either person

2. **Complex Coordination**
   - Mixed AND/OR without clear precedence
   - Scope ambiguity in coordinated clauses

3. **Pragmatic Inference**
   - "Every student must submit their assignment" 
   - Implicit: each student submits their own assignment

4. **Ellipsis and Gapping**
   - "John owns a car and Mary a motorcycle"
   - Missing verb in second clause

5. **Quantifier Scope Ambiguity**
   - "Every person loves someone"
   - Could mean: ∀x∃y: loves(x,y) OR ∃y∀x: loves(x,y)

### 7. **Implementation Roadmap**

#### Week 1: Enhanced Parser Components
- [ ] Implement ScopeManager
- [ ] Add temporal logic support
- [ ] Enhance coreference resolution
- [ ] Add exception clause handling

#### Week 2: Comprehensive Test Suite
- [ ] Create 100+ test cases across all complexity levels
- [ ] Implement automated complexity scoring
- [ ] Build test result analytics

#### Week 3: Parser Optimization
- [ ] Performance profiling
- [ ] Memory usage optimization
- [ ] Parallel parsing for long sentences

#### Week 4: Documentation and Integration
- [ ] Complete API documentation
- [ ] Integration guide
- [ ] Performance benchmarks
- [ ] Failure mode analysis

### 8. **Success Metrics**

1. **Coverage Metrics**
   - 90%+ success on Level 1-5 complexity
   - 70%+ success on Level 6-8 complexity
   - Document all failure modes for Level 9-10

2. **Performance Metrics**
   - Parse 95% of sentences under 100ms
   - Handle sentences up to 200 words
   - Memory usage under 100MB for typical sentences

3. **Accuracy Metrics**
   - Correct logical form: 85%+ for supported structures
   - Entity extraction: 95%+ accuracy
   - Coreference resolution: 80%+ accuracy

### 9. **Next Steps**

1. Implement the comprehensive test suite
2. Run tests to find exact breaking points
3. Document failure modes
4. Prioritize parser enhancements based on common failures
5. Iterate until reaching target metrics

## 📝 Notes for Continuation

When resuming this work:
1. Start with `test_complex_english_limits.py`
2. Implement the `ComplexityFeatures` scoring system
3. Create test cases for each linguistic structure level
4. Run progressive tests to find breaking points
5. Update this document with findings

**Key files to reference:**
- `/backend/unified/domain/complex_english_parser.py` - Current parser
- `/test_complex_english_parser.py` - Basic tests
- `/test_progressive_complexity.py` - Complexity progression framework