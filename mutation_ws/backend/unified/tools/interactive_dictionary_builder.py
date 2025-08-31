"""
Interactive Dictionary Builder - User-friendly tool for creating dictionaries
Provides a guided interface for building custom vocabularies.

Copyright: DarkLightX / Dana Edwards
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional


class InteractiveDictionaryBuilder:
    """Interactive tool for building dictionaries."""
    
    def __init__(self):
        self.dictionary = {
            'entities': {},
            'verbs': {},
            'patterns': {},
            'abbreviations': {}
        }
        self.current_domain = None
    
    def run(self):
        """Run the interactive builder."""
        print("🚀 Interactive Dictionary Builder for TCE Parser")
        print("=" * 60)
        print("This tool will help you create a custom vocabulary dictionary.")
        print()
        
        # Get domain
        self.current_domain = input("What domain is this dictionary for? (e.g., healthcare, finance, general): ").strip()
        if self.current_domain:
            self.dictionary['domain'] = self.current_domain
        
        while True:
            print("\n📋 Main Menu:")
            print("1. Add entities (people, objects, systems)")
            print("2. Add verbs (actions)")
            print("3. Add patterns (complex expressions)")
            print("4. Add abbreviations")
            print("5. View current dictionary")
            print("6. Save dictionary")
            print("7. Load example sentences")
            print("8. Quick start wizard")
            print("9. Exit")
            
            choice = input("\nSelect option (1-9): ").strip()
            
            if choice == '1':
                self.add_entities_interactive()
            elif choice == '2':
                self.add_verbs_interactive()
            elif choice == '3':
                self.add_patterns_interactive()
            elif choice == '4':
                self.add_abbreviations_interactive()
            elif choice == '5':
                self.view_dictionary()
            elif choice == '6':
                self.save_dictionary_interactive()
            elif choice == '7':
                self.analyze_sentences_interactive()
            elif choice == '8':
                self.quick_start_wizard()
            elif choice == '9':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def add_entities_interactive(self):
        """Interactively add entities."""
        print("\n📝 Add Entities")
        print("Entities are the 'things' in your domain (people, objects, systems, etc.)")
        print("Press Enter with empty name to finish.\n")
        
        while True:
            name = input("Entity name (e.g., 'customer', 'product'): ").strip().lower()
            if not name:
                break
            
            # Category selection
            print("\nSelect category:")
            categories = ['person', 'object', 'system', 'document', 'location', 'event', 'abstract']
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")
            
            cat_choice = input("Category (1-7): ").strip()
            category = categories[int(cat_choice) - 1] if cat_choice.isdigit() and 1 <= int(cat_choice) <= 7 else 'object'
            
            # Optional fields
            entity = {'category': category}
            
            plural = input(f"Plural form (default: '{name}s'): ").strip()
            if plural:
                entity['plural_form'] = plural
            
            synonyms = input("Synonyms (comma-separated, e.g., 'client, buyer'): ").strip()
            if synonyms:
                entity['synonyms'] = [s.strip() for s in synonyms.split(',')]
            
            properties = input("Properties (comma-separated, e.g., 'id, name, status'): ").strip()
            if properties:
                entity['properties'] = [p.strip() for p in properties.split(',')]
            
            typical_verbs = input("Typical actions (comma-separated, e.g., 'purchases, orders'): ").strip()
            if typical_verbs:
                entity['typical_verbs'] = [v.strip() for v in typical_verbs.split(',')]
            
            self.dictionary['entities'][name] = entity
            print(f"✅ Added entity: {name}")
    
    def add_verbs_interactive(self):
        """Interactively add verbs."""
        print("\n🔧 Add Verbs")
        print("Verbs are the actions in your domain.")
        print("Press Enter with empty verb to finish.\n")
        
        while True:
            verb = input("Verb (e.g., 'purchases', 'manages'): ").strip().lower()
            if not verb:
                break
            
            verb_info = {}
            
            past = input(f"Past tense (default: '{verb}ed'): ").strip()
            if past:
                verb_info['past_tense'] = past
            
            synonyms = input("Synonyms (comma-separated): ").strip()
            if synonyms:
                verb_info['synonyms'] = [s.strip() for s in synonyms.split(',')]
            
            # Show existing entities for reference
            if self.dictionary['entities']:
                print("\nExisting entities:", ', '.join(self.dictionary['entities'].keys()))
            
            subjects = input("Typical subjects (comma-separated): ").strip()
            if subjects:
                verb_info['typical_subjects'] = [s.strip() for s in subjects.split(',')]
            
            objects = input("Typical objects (comma-separated): ").strip()
            if objects:
                verb_info['typical_objects'] = [o.strip() for o in objects.split(',')]
            
            self.dictionary['verbs'][verb] = verb_info
            print(f"✅ Added verb: {verb}")
    
    def add_patterns_interactive(self):
        """Interactively add patterns."""
        print("\n🎯 Add Patterns")
        print("Patterns help parse complex expressions.")
        print("Example: '10% discount' → pattern: '(\\d+)% discount'")
        print("Press Enter with empty name to finish.\n")
        
        while True:
            name = input("Pattern name (e.g., 'discount_pattern'): ").strip()
            if not name:
                break
            
            print("\nRegex pattern (use \\d for digits, \\w for words)")
            pattern = input("Pattern: ").strip()
            if not pattern:
                continue
            
            replacement = input("Replacement (use \\1, \\2 for captured groups): ").strip()
            
            examples = input("Example matches (comma-separated): ").strip()
            
            pattern_info = {
                'pattern': pattern,
                'replacement': replacement
            }
            
            if examples:
                pattern_info['examples'] = [e.strip() for e in examples.split(',')]
            
            self.dictionary['patterns'][name] = pattern_info
            print(f"✅ Added pattern: {name}")
    
    def add_abbreviations_interactive(self):
        """Interactively add abbreviations."""
        print("\n🔤 Add Abbreviations")
        print("Press Enter with empty abbreviation to finish.\n")
        
        while True:
            abbrev = input("Abbreviation (e.g., 'CEO'): ").strip().upper()
            if not abbrev:
                break
            
            expansion = input(f"Expansion of {abbrev}: ").strip()
            if expansion:
                self.dictionary['abbreviations'][abbrev] = expansion
                print(f"✅ Added abbreviation: {abbrev}")
    
    def quick_start_wizard(self):
        """Quick start wizard for common setups."""
        print("\n🧙 Quick Start Wizard")
        print("This will help you create a basic dictionary quickly.")
        
        # Domain selection
        print("\nSelect your domain:")
        domains = {
            '1': ('business', ['employee', 'manager', 'customer', 'product', 'order']),
            '2': ('healthcare', ['patient', 'doctor', 'medication', 'diagnosis', 'treatment']),
            '3': ('education', ['student', 'teacher', 'course', 'assignment', 'grade']),
            '4': ('technical', ['user', 'system', 'database', 'application', 'server'])
        }
        
        for key, (domain, _) in domains.items():
            print(f"{key}. {domain.title()}")
        
        choice = input("\nSelect domain (1-4): ").strip()
        
        if choice in domains:
            domain, entities = domains[choice]
            self.dictionary['domain'] = domain
            
            print(f"\n✨ Setting up {domain} dictionary...")
            
            # Add common entities
            for entity in entities:
                category = 'person' if entity in ['employee', 'manager', 'customer', 'patient', 'doctor', 'student', 'teacher', 'user'] else 'object'
                self.dictionary['entities'][entity] = {
                    'category': category,
                    'plural_form': entity + 's'
                }
            
            # Add common verbs based on domain
            if domain == 'business':
                self.dictionary['verbs'] = {
                    'purchases': {'past_tense': 'purchased'},
                    'manages': {'past_tense': 'managed'},
                    'sells': {'past_tense': 'sold'}
                }
            elif domain == 'healthcare':
                self.dictionary['verbs'] = {
                    'diagnoses': {'past_tense': 'diagnosed'},
                    'treats': {'past_tense': 'treated'},
                    'prescribes': {'past_tense': 'prescribed'}
                }
            
            print(f"✅ Created basic {domain} dictionary with {len(entities)} entities!")
    
    def analyze_sentences_interactive(self):
        """Analyze example sentences to suggest vocabulary."""
        print("\n📄 Analyze Example Sentences")
        print("Enter sentences from your domain to analyze for vocabulary.")
        print("Type 'done' when finished.\n")
        
        sentences = []
        while True:
            sentence = input("Sentence: ").strip()
            if sentence.lower() == 'done':
                break
            if sentence:
                sentences.append(sentence)
        
        if sentences:
            # Simple analysis
            words = set()
            for sentence in sentences:
                words.update(word.lower() for word in sentence.split() 
                           if len(word) > 2 and word.isalpha())
            
            print(f"\n📊 Found {len(words)} unique words")
            print("\nSuggested entities (nouns):")
            
            # Simple heuristic: words that might be nouns
            potential_entities = [w for w in words if not w.endswith('ing') and not w.endswith('ed')]
            for word in sorted(potential_entities)[:20]:
                if word not in self.dictionary['entities']:
                    print(f"  - {word}")
            
            add = input("\nAdd these to dictionary? (y/n): ").strip().lower()
            if add == 'y':
                for word in potential_entities[:20]:
                    if word not in self.dictionary['entities']:
                        self.dictionary['entities'][word] = {'category': 'object'}
                print("✅ Added suggested entities!")
    
    def view_dictionary(self):
        """View current dictionary."""
        print("\n📚 Current Dictionary")
        print("=" * 50)
        
        if self.dictionary.get('domain'):
            print(f"Domain: {self.dictionary['domain']}")
        
        print(f"\nEntities ({len(self.dictionary['entities'])}):")
        for name, info in list(self.dictionary['entities'].items())[:10]:
            print(f"  - {name} ({info['category']})")
        if len(self.dictionary['entities']) > 10:
            print(f"  ... and {len(self.dictionary['entities']) - 10} more")
        
        print(f"\nVerbs ({len(self.dictionary['verbs'])}):")
        for verb in list(self.dictionary['verbs'].keys())[:10]:
            print(f"  - {verb}")
        
        if self.dictionary['patterns']:
            print(f"\nPatterns ({len(self.dictionary['patterns'])}):")
            for name in list(self.dictionary['patterns'].keys())[:5]:
                print(f"  - {name}")
        
        if self.dictionary['abbreviations']:
            print(f"\nAbbreviations ({len(self.dictionary['abbreviations'])}):")
            for abbrev, expansion in list(self.dictionary['abbreviations'].items())[:5]:
                print(f"  - {abbrev}: {expansion}")
    
    def save_dictionary_interactive(self):
        """Save dictionary to file."""
        print("\n💾 Save Dictionary")
        
        filename = input("Filename (without extension): ").strip()
        if not filename:
            filename = f"{self.current_domain or 'custom'}_dictionary"
        
        print("\nFormat:")
        print("1. YAML (recommended)")
        print("2. JSON")
        
        format_choice = input("Select format (1-2): ").strip()
        
        if format_choice == '2':
            filepath = Path(f"{filename}.json")
            with open(filepath, 'w') as f:
                json.dump(self.dictionary, f, indent=2)
        else:
            filepath = Path(f"{filename}.yaml")
            with open(filepath, 'w') as f:
                yaml.dump(self.dictionary, f, default_flow_style=False)
        
        print(f"✅ Dictionary saved to: {filepath}")
        print(f"\nTo use this dictionary:")
        print(f"  parser = create_extensible_parser()")
        print(f"  parser.load_dictionary('{filepath}')")


def main():
    """Run the interactive builder."""
    builder = InteractiveDictionaryBuilder()
    builder.run()


if __name__ == "__main__":
    main()