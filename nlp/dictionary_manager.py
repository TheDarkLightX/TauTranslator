#!/usr/bin/env python3
"""
Dictionary Management System
============================

Manages loading, validation, and merging of custom dictionary files.
Supports JSON, YAML, and CSV formats for user-defined vocabulary.
"""

import json
import csv
import os
import yaml
from typing import Dict, List, Any, Optional, NamedTuple
from dataclasses import dataclass
from .nlp_vocabulary import TauVocabulary, VocabularyEntry

class LoadResult(NamedTuple):
    """Result of dictionary loading operation"""
    success: bool
    message: str
    entries_loaded: int = 0

@dataclass
class DictionaryInfo:
    """Information about a loaded dictionary"""
    name: str
    path: str
    format: str
    enabled: bool
    metadata: Dict[str, Any]
    entries_count: int

class DictionaryLoader:
    """Loads and parses different dictionary file formats"""
    
    def __init__(self):
        self.supported_formats = ['.json', '.yaml', '.yml', '.csv']
    
    def load_file(self, file_path: str) -> LoadResult:
        """Load dictionary from file based on extension"""
        if not os.path.exists(file_path):
            return LoadResult(False, f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.json':
                return self._load_json(file_path)
            elif file_ext in ['.yaml', '.yml']:
                return self._load_yaml(file_path)
            elif file_ext == '.csv':
                return self._load_csv(file_path)
            else:
                return LoadResult(False, f"Unsupported format: {file_ext}")
        
        except Exception as e:
            return LoadResult(False, f"Error loading {file_path}: {str(e)}")
    
    def _load_json(self, file_path: str) -> LoadResult:
        """Load JSON format dictionary"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            validation_result = self._validate_dictionary_structure(data)
            if not validation_result.success:
                return validation_result
            
            return LoadResult(True, f"Successfully loaded JSON dictionary: {os.path.basename(file_path)}", 
                            self._count_entries(data))
        
        except json.JSONDecodeError as e:
            return LoadResult(False, f"Invalid JSON format: {str(e)}")
    
    def _load_yaml(self, file_path: str) -> LoadResult:
        """Load YAML format dictionary"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Validate structure
            validation_result = self._validate_dictionary_structure(data)
            if not validation_result.success:
                return validation_result
            
            return LoadResult(True, f"Successfully loaded YAML dictionary: {os.path.basename(file_path)}", 
                            self._count_entries(data))
        
        except yaml.YAMLError as e:
            return LoadResult(False, f"Invalid YAML format: {str(e)}")
    
    def _load_csv(self, file_path: str) -> LoadResult:
        """Load CSV format dictionary"""
        try:
            data = {"domain_specific": {}}
            entries_count = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validate CSV headers
                required_headers = ['category', 'key', 'canonical', 'variants']
                if not all(header in reader.fieldnames for header in required_headers):
                    return LoadResult(False, f"CSV missing required headers: {required_headers}")
                
                for row in reader:
                    if not row['key'] or not row['canonical']:
                        continue  # Skip empty rows
                    
                    # Parse variants (comma-separated)
                    variants = [v.strip() for v in row['variants'].split(',') if v.strip()]
                    
                    # Determine category for organization
                    category = row['category']
                    if category not in data:
                        if category in ['logical_operator', 'quantifier', 'temporal_operator']:
                            data[category + 's'] = {}
                        else:
                            data['domain_specific'] = data.get('domain_specific', {})
                    
                    # Create entry
                    entry_data = {
                        "canonical": row['canonical'],
                        "variants": variants,
                        "category": category,
                        "context": row.get('context', ''),
                        "examples": [row['examples']] if row.get('examples') else []
                    }
                    
                    # Add to appropriate category
                    if category in ['logical_operator', 'quantifier', 'temporal_operator']:
                        category_key = category + 's'
                        if category_key not in data:
                            data[category_key] = {}
                        data[category_key][row['key']] = entry_data
                    else:
                        data['domain_specific'][row['key']] = entry_data
                    
                    entries_count += 1
            
            return LoadResult(True, f"Successfully loaded CSV dictionary: {os.path.basename(file_path)}", entries_count)
        
        except Exception as e:
            return LoadResult(False, f"Error parsing CSV: {str(e)}")
    
    def _validate_dictionary_structure(self, data: Dict[str, Any]) -> LoadResult:
        """Validate dictionary structure and required fields"""
        if not isinstance(data, dict):
            return LoadResult(False, "Dictionary must be a JSON object")
        
        # Check for at least one valid category
        valid_categories = ['logical_operators', 'quantifiers', 'temporal_operators', 'domain_specific', 'predicates']
        if not any(category in data for category in valid_categories):
            return LoadResult(False, f"Dictionary must contain at least one category: {valid_categories}")
        
        # Validate entries in each category
        for category_name, category_data in data.items():
            if category_name == 'metadata':
                continue  # Skip metadata validation
            
            if category_name in valid_categories:
                if not isinstance(category_data, dict):
                    return LoadResult(False, f"Category '{category_name}' must be an object")
                
                for entry_key, entry_data in category_data.items():
                    # Validate required fields
                    if not isinstance(entry_data, dict):
                        return LoadResult(False, f"Entry '{entry_key}' must be an object")
                    
                    required_fields = ['canonical', 'variants', 'category']
                    missing_fields = [field for field in required_fields if field not in entry_data]
                    if missing_fields:
                        return LoadResult(False, f"Entry '{entry_key}' missing required fields: {missing_fields}")
                    
                    # Validate variants is a list
                    if not isinstance(entry_data['variants'], list):
                        return LoadResult(False, f"Entry '{entry_key}' variants must be a list")
        
        return LoadResult(True, "Dictionary structure is valid")
    
    def _count_entries(self, data: Dict[str, Any]) -> int:
        """Count total entries in dictionary"""
        count = 0
        valid_categories = ['logical_operators', 'quantifiers', 'temporal_operators', 'domain_specific', 'predicates']
        
        for category_name in valid_categories:
            if category_name in data and isinstance(data[category_name], dict):
                count += len(data[category_name])
        
        return count

class DictionaryManager:
    """Manages multiple dictionaries and provides unified vocabulary"""
    
    def __init__(self):
        self.loader = DictionaryLoader()
        self.dictionaries: Dict[str, Dict[str, Any]] = {}
        self.dictionary_info: Dict[str, DictionaryInfo] = {}
        self.base_vocabulary = TauVocabulary()
        
        # Register default dictionary
        self._register_default_dictionary()
    
    def _register_default_dictionary(self):
        """Register the default vocabulary as a dictionary"""
        self.dictionary_info["default"] = DictionaryInfo(
            name="default",
            path="built-in",
            format="built-in",
            enabled=True,
            metadata={"name": "Default Tau Vocabulary", "version": "1.0"},
            entries_count=self._count_default_entries()
        )
    
    def _count_default_entries(self) -> int:
        """Count entries in default vocabulary"""
        count = 0
        count += len(self.base_vocabulary.logical_operators)
        count += len(self.base_vocabulary.quantifiers)
        count += len(self.base_vocabulary.temporal_operators)
        count += len(self.base_vocabulary.predicates)
        return count
    
    def load_dictionary_file(self, file_path: str, allow_override: bool = False) -> LoadResult:
        """Load a dictionary file and add to managed dictionaries"""
        # Load and validate file
        load_result = self.loader.load_file(file_path)
        if not load_result.success:
            return load_result
        
        # Read the actual data
        file_ext = os.path.splitext(file_path)[1].lower()
        try:
            if file_ext == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
            elif file_ext in ['.yaml', '.yml']:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
            elif file_ext == '.csv':
                # CSV loading is handled differently
                data = self._load_csv_data(file_path)
            else:
                return LoadResult(False, f"Unsupported format: {file_ext}")
        
        except Exception as e:
            return LoadResult(False, f"Error reading file: {str(e)}")
        
        # Check for conflicts
        dict_name = os.path.basename(file_path)
        if dict_name in self.dictionaries and not allow_override:
            return LoadResult(False, f"Dictionary '{dict_name}' already loaded. Use allow_override=True to replace.")
        
        # Store dictionary data
        self.dictionaries[dict_name] = data
        
        # Create dictionary info
        metadata = data.get('metadata', {})
        self.dictionary_info[dict_name] = DictionaryInfo(
            name=dict_name,
            path=file_path,
            format=file_ext,
            enabled=True,
            metadata=metadata,
            entries_count=self.loader._count_entries(data)
        )
        
        message = f"Successfully loaded dictionary '{dict_name}'"
        if dict_name in self.dictionaries and allow_override:
            message += " (override existing)"
        
        return LoadResult(True, message, load_result.entries_loaded)
    
    def _load_csv_data(self, file_path: str) -> Dict[str, Any]:
        """Load CSV data into dictionary format"""
        data = {"domain_specific": {}}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if not row['key'] or not row['canonical']:
                    continue
                
                variants = [v.strip() for v in row['variants'].split(',') if v.strip()]
                
                entry_data = {
                    "canonical": row['canonical'],
                    "variants": variants,
                    "category": row['category'],
                    "context": row.get('context', ''),
                    "examples": [row['examples']] if row.get('examples') else []
                }
                
                # Organize by category
                category = row['category']
                if category in ['logical_operator', 'quantifier', 'temporal_operator']:
                    category_key = category + 's'
                    if category_key not in data:
                        data[category_key] = {}
                    data[category_key][row['key']] = entry_data
                else:
                    data['domain_specific'][row['key']] = entry_data
        
        return data
    
    def list_dictionaries(self) -> List[Dict[str, Any]]:
        """List all loaded dictionaries with their info"""
        result = []
        for name, info in self.dictionary_info.items():
            result.append({
                "name": info.name,
                "path": info.path,
                "format": info.format,
                "enabled": info.enabled,
                "metadata": info.metadata,
                "entries_count": info.entries_count
            })
        return result
    
    def set_dictionary_enabled(self, dict_name: str, enabled: bool) -> LoadResult:
        """Enable or disable a specific dictionary"""
        if dict_name not in self.dictionary_info:
            return LoadResult(False, f"Dictionary '{dict_name}' not found")
        
        self.dictionary_info[dict_name].enabled = enabled
        action = "enabled" if enabled else "disabled"
        return LoadResult(True, f"Dictionary '{dict_name}' {action}")
    
    def remove_dictionary(self, dict_name: str) -> LoadResult:
        """Remove a dictionary from management"""
        if dict_name == "default":
            return LoadResult(False, "Cannot remove default dictionary")
        
        if dict_name not in self.dictionary_info:
            return LoadResult(False, f"Dictionary '{dict_name}' not found")
        
        # Remove from both stores
        del self.dictionaries[dict_name]
        del self.dictionary_info[dict_name]
        
        return LoadResult(True, f"Dictionary '{dict_name}' removed")
    
    def get_vocabulary(self) -> TauVocabulary:
        """Get merged vocabulary from all enabled dictionaries"""
        # Start with base vocabulary
        merged_vocab = TauVocabulary()
        
        # Add domain_specific category if not exists
        if not hasattr(merged_vocab, 'domain_specific'):
            merged_vocab.domain_specific = {}
        
        # Merge enabled custom dictionaries
        for dict_name, info in self.dictionary_info.items():
            if not info.enabled:
                continue
            
            if dict_name == "default":
                continue  # Already included in base
            
            dict_data = self.dictionaries.get(dict_name, {})
            self._merge_dictionary_into_vocabulary(dict_data, merged_vocab)
        
        return merged_vocab
    
    def _merge_dictionary_into_vocabulary(self, dict_data: Dict[str, Any], vocabulary: TauVocabulary):
        """Merge dictionary data into vocabulary object"""
        # Merge each category
        category_mappings = {
            'logical_operators': 'logical_operators',
            'quantifiers': 'quantifiers',
            'temporal_operators': 'temporal_operators',
            'predicates': 'predicates',
            'domain_specific': 'domain_specific'
        }
        
        for dict_category, vocab_category in category_mappings.items():
            if dict_category in dict_data:
                # Ensure vocabulary has the category
                if not hasattr(vocabulary, vocab_category):
                    setattr(vocabulary, vocab_category, {})
                
                vocab_cat = getattr(vocabulary, vocab_category)
                
                # Add entries
                for key, entry_data in dict_data[dict_category].items():
                    vocab_entry = VocabularyEntry(
                        canonical=entry_data['canonical'],
                        variants=entry_data['variants'],
                        category=entry_data['category'],
                        context=entry_data.get('context'),
                        examples=entry_data.get('examples')
                    )
                    vocab_cat[key] = vocab_entry

# Export main classes
__all__ = ['DictionaryManager', 'DictionaryLoader', 'LoadResult', 'DictionaryInfo']