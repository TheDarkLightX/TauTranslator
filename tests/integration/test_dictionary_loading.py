#!/usr/bin/env python3
"""
TDD Tests for Custom Dictionary Loading
=======================================

Test-driven development for:
1. Loading custom dictionary files
2. Merging with default vocabulary
3. Different dictionary formats (JSON, YAML, CSV)
4. Validation and error handling
5. Dictionary management (add, remove, update)

These tests define the expected behavior BEFORE implementation.
"""

import unittest
import json
import tempfile
import os
from typing import Dict, List, Any

# These imports will work once we implement the dictionary system
from nlp_vocabulary import TauVocabulary, VocabularyEntry
from dictionary_manager import DictionaryManager, DictionaryLoader

class TestDictionaryFileFormats(unittest.TestCase):
    """Test different dictionary file format support"""
    
    def setUp(self):
        """Set up test environment with temporary files"""
        self.temp_dir = tempfile.mkdtemp()
        self.dict_manager = DictionaryManager()
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_json_dictionary(self):
        """Test loading JSON format dictionary"""
        # Create sample JSON dictionary
        sample_dict = {
            "logical_operators": {
                "implies": {
                    "canonical": "implies",
                    "variants": ["leads to", "results in", "causes", "means"],
                    "category": "logical_operator",
                    "context": "implication",
                    "examples": ["A implies B", "rain leads to wet ground"]
                }
            },
            "domain_specific": {
                "user_authenticated": {
                    "canonical": "user is authenticated",
                    "variants": ["user logged in", "user verified", "valid user session"],
                    "category": "predicate",
                    "context": "authentication",
                    "examples": ["if user is authenticated then allow access"]
                }
            }
        }
        
        # Write to temporary file
        json_file = os.path.join(self.temp_dir, "custom_dict.json")
        with open(json_file, 'w') as f:
            json.dump(sample_dict, f)
        
        # Load dictionary
        result = self.dict_manager.load_dictionary_file(json_file)
        
        # Should successfully load
        self.assertTrue(result.success)
        self.assertIn("loaded", result.message.lower())
        
        # Should add entries to vocabulary
        vocab = self.dict_manager.get_vocabulary()
        self.assertIn("user_authenticated", vocab.domain_specific)
        
        # Should preserve entry structure
        auth_entry = vocab.domain_specific["user_authenticated"]
        self.assertEqual(auth_entry.canonical, "user is authenticated")
        self.assertIn("user logged in", auth_entry.variants)
    
    def test_load_yaml_dictionary(self):
        """Test loading YAML format dictionary"""
        yaml_content = """
logical_operators:
  custom_and:
    canonical: "and also"
    variants: ["and also", "plus", "in addition to"]
    category: "logical_operator"
    context: "conjunction"
    examples: ["A and also B"]

domain_specific:
  security_check:
    canonical: "security validation"
    variants: ["security check", "validation", "verification"]
    category: "predicate"
    context: "security"
    examples: ["perform security validation before access"]
"""
        
        # Write to temporary file
        yaml_file = os.path.join(self.temp_dir, "custom_dict.yaml")
        with open(yaml_file, 'w') as f:
            f.write(yaml_content)
        
        # Load dictionary
        result = self.dict_manager.load_dictionary_file(yaml_file)
        
        # Should successfully load YAML
        self.assertTrue(result.success)
        
        # Should add YAML entries
        vocab = self.dict_manager.get_vocabulary()
        self.assertIn("security_check", vocab.domain_specific)
    
    def test_load_csv_dictionary(self):
        """Test loading CSV format dictionary"""
        csv_content = """category,key,canonical,variants,context,examples
logical_operator,custom_or,or alternatively,"or alternatively,either,alternatively",disjunction,"A or alternatively B"
predicate,data_valid,data is valid,"data valid,valid data,clean data",validation,"ensure data is valid"
"""
        
        # Write to temporary file
        csv_file = os.path.join(self.temp_dir, "custom_dict.csv")
        with open(csv_file, 'w') as f:
            f.write(csv_content)
        
        # Load dictionary
        result = self.dict_manager.load_dictionary_file(csv_file)
        
        # Should successfully load CSV
        self.assertTrue(result.success)
        
        # Should parse CSV entries correctly
        vocab = self.dict_manager.get_vocabulary()
        self.assertIn("data_valid", vocab.domain_specific)
        
        data_entry = vocab.domain_specific["data_valid"]
        self.assertEqual(data_entry.canonical, "data is valid")
        self.assertIn("valid data", data_entry.variants)

class TestDictionaryValidation(unittest.TestCase):
    """Test dictionary validation and error handling"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.dict_manager = DictionaryManager()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_invalid_json_format(self):
        """Test handling of invalid JSON files"""
        # Create malformed JSON
        invalid_json = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_json, 'w') as f:
            f.write('{"invalid": json content}')
        
        # Should handle gracefully
        result = self.dict_manager.load_dictionary_file(invalid_json)
        self.assertFalse(result.success)
        self.assertIn("invalid", result.message.lower())
    
    def test_missing_required_fields(self):
        """Test validation of required fields"""
        # Dictionary missing required fields
        incomplete_dict = {
            "logical_operators": {
                "incomplete_entry": {
                    "canonical": "test",
                    # Missing variants, category, etc.
                }
            }
        }
        
        json_file = os.path.join(self.temp_dir, "incomplete.json")
        with open(json_file, 'w') as f:
            json.dump(incomplete_dict, f)
        
        # Should validate and report missing fields
        result = self.dict_manager.load_dictionary_file(json_file)
        self.assertFalse(result.success)
        self.assertIn("missing", result.message.lower())
    
    def test_duplicate_entries_handling(self):
        """Test handling of duplicate entries"""
        # Dictionary with duplicate key
        duplicate_dict = {
            "logical_operators": {
                "and": {  # This conflicts with default vocabulary
                    "canonical": "custom and",
                    "variants": ["custom and", "custom plus"],
                    "category": "logical_operator",
                    "context": "custom_conjunction"
                }
            }
        }
        
        json_file = os.path.join(self.temp_dir, "duplicate.json")
        with open(json_file, 'w') as f:
            json.dump(duplicate_dict, f)
        
        # Should handle duplicates (merge or override based on policy)
        result = self.dict_manager.load_dictionary_file(json_file, allow_override=True)
        self.assertTrue(result.success)
        
        # Should report the override
        self.assertIn("override", result.message.lower())

class TestDictionaryManagement(unittest.TestCase):
    """Test dictionary management operations"""
    
    def setUp(self):
        self.dict_manager = DictionaryManager()
    
    def test_list_loaded_dictionaries(self):
        """Test listing all loaded dictionaries"""
        # Initially should have default dictionary
        dictionaries = self.dict_manager.list_dictionaries()
        self.assertGreater(len(dictionaries), 0)
        self.assertTrue(any(d["name"] == "default" for d in dictionaries))
    
    def test_enable_disable_dictionaries(self):
        """Test enabling/disabling specific dictionaries"""
        # Load a custom dictionary first
        temp_dir = tempfile.mkdtemp()
        try:
            custom_dict = {"domain_specific": {"test_entry": {"canonical": "test", "variants": ["test"], "category": "test"}}}
            json_file = os.path.join(temp_dir, "test.json")
            with open(json_file, 'w') as f:
                json.dump(custom_dict, f)
            
            self.dict_manager.load_dictionary_file(json_file)
            
            # Should be enabled by default
            dictionaries = self.dict_manager.list_dictionaries()
            test_dict = next(d for d in dictionaries if "test.json" in d["name"])
            self.assertTrue(test_dict["enabled"])
            
            # Disable dictionary
            self.dict_manager.set_dictionary_enabled("test.json", False)
            
            # Should be disabled
            dictionaries = self.dict_manager.list_dictionaries()
            test_dict = next(d for d in dictionaries if "test.json" in d["name"])
            self.assertFalse(test_dict["enabled"])
            
            # Should not appear in active vocabulary
            vocab = self.dict_manager.get_vocabulary()
            self.assertNotIn("test_entry", vocab.domain_specific)
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_remove_dictionary(self):
        """Test removing loaded dictionaries"""
        # Load and then remove a dictionary
        temp_dir = tempfile.mkdtemp()
        try:
            custom_dict = {"domain_specific": {"removable_entry": {"canonical": "test", "variants": ["test"], "category": "test"}}}
            json_file = os.path.join(temp_dir, "removable.json")
            with open(json_file, 'w') as f:
                json.dump(custom_dict, f)
            
            # Load dictionary
            self.dict_manager.load_dictionary_file(json_file)
            initial_count = len(self.dict_manager.list_dictionaries())
            
            # Remove dictionary
            result = self.dict_manager.remove_dictionary("removable.json")
            self.assertTrue(result.success)
            
            # Should have fewer dictionaries
            final_count = len(self.dict_manager.list_dictionaries())
            self.assertEqual(final_count, initial_count - 1)
            
            # Should not appear in vocabulary
            vocab = self.dict_manager.get_vocabulary()
            self.assertNotIn("removable_entry", vocab.domain_specific)
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)

class TestDictionaryMerging(unittest.TestCase):
    """Test merging multiple dictionaries"""
    
    def setUp(self):
        self.dict_manager = DictionaryManager()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_merge_multiple_dictionaries(self):
        """Test merging vocabulary from multiple sources"""
        # Create first dictionary
        dict1 = {
            "domain_specific": {
                "auth_check": {
                    "canonical": "authentication check",
                    "variants": ["auth check", "login verification"],
                    "category": "predicate",
                    "context": "security"
                }
            }
        }
        
        # Create second dictionary
        dict2 = {
            "domain_specific": {
                "data_validation": {
                    "canonical": "data validation",
                    "variants": ["data check", "validation"],
                    "category": "predicate", 
                    "context": "validation"
                }
            }
        }
        
        # Write both dictionaries
        file1 = os.path.join(self.temp_dir, "dict1.json")
        file2 = os.path.join(self.temp_dir, "dict2.json")
        
        with open(file1, 'w') as f:
            json.dump(dict1, f)
        with open(file2, 'w') as f:
            json.dump(dict2, f)
        
        # Load both dictionaries
        self.dict_manager.load_dictionary_file(file1)
        self.dict_manager.load_dictionary_file(file2)
        
        # Should have entries from both dictionaries
        vocab = self.dict_manager.get_vocabulary()
        self.assertIn("auth_check", vocab.domain_specific)
        self.assertIn("data_validation", vocab.domain_specific)
    
    def test_priority_ordering(self):
        """Test that dictionary loading order affects priority"""
        # Create dictionaries with same key but different values
        dict1 = {
            "domain_specific": {
                "common_term": {
                    "canonical": "first version",
                    "variants": ["first", "version1"],
                    "category": "test"
                }
            }
        }
        
        dict2 = {
            "domain_specific": {
                "common_term": {
                    "canonical": "second version",
                    "variants": ["second", "version2"],
                    "category": "test"
                }
            }
        }
        
        file1 = os.path.join(self.temp_dir, "first.json")
        file2 = os.path.join(self.temp_dir, "second.json")
        
        with open(file1, 'w') as f:
            json.dump(dict1, f)
        with open(file2, 'w') as f:
            json.dump(dict2, f)
        
        # Load in order: first, then second
        self.dict_manager.load_dictionary_file(file1)
        self.dict_manager.load_dictionary_file(file2, allow_override=True)
        
        # Second should override first
        vocab = self.dict_manager.get_vocabulary()
        entry = vocab.domain_specific["common_term"]
        self.assertEqual(entry.canonical, "second version")

class TestIntegrationWithAutoComplete(unittest.TestCase):
    """Test integration with existing auto-complete system"""
    
    def test_custom_dictionary_in_autocomplete(self):
        """Test that custom dictionary entries appear in auto-complete"""
        from nlp_integration import NLPTranslationService
        
        # Create custom dictionary with domain terms
        temp_dir = tempfile.mkdtemp()
        try:
            custom_dict = {
                "domain_specific": {
                    "user_story": {
                        "canonical": "user story",
                        "variants": ["user story", "story", "requirement"],
                        "category": "predicate",
                        "context": "agile",
                        "examples": ["As a user story specifies"]
                    }
                }
            }
            
            json_file = os.path.join(temp_dir, "agile.json")
            with open(json_file, 'w') as f:
                json.dump(custom_dict, f)
            
            # Create NLP service with custom dictionary
            nlp_service = NLPTranslationService()
            nlp_service.dictionary_manager = DictionaryManager()
            nlp_service.dictionary_manager.load_dictionary_file(json_file)
            
            # Reload vocabulary with custom dictionary
            nlp_service.vocabulary = nlp_service.dictionary_manager.get_vocabulary()
            nlp_service.autocomplete_engine.vocab = nlp_service.vocabulary
            
            # Test auto-complete with custom terms
            suggestions = nlp_service.get_autocomplete_suggestions("user")
            suggestion_texts = [s["text"] for s in suggestions]
            
            # Should include custom dictionary terms (case insensitive)
            self.assertTrue(any("user story" in text.lower() for text in suggestion_texts))
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)

def run_failing_tests():
    """Run all dictionary tests - they should fail initially"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    print("🔴 TDD RED Phase: Dictionary Loading Tests")
    print("=" * 50)
    print("These tests define custom dictionary requirements.")
    print("They SHOULD fail initially - that's the point of TDD!")
    print("=" * 50)
    
    run_failing_tests()