"""
TCE Parser V1.51 - Optimal Extensible Parser
User dictionary support with minimal cyclomatic complexity.

Copyright: DarkLightX / Dana Edwards
"""

import re
from typing import Dict, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass
import logging

from backend.unified.tce_parser_v1_01 import TCEParserV101
from backend.unified.core.user_dictionary import UserDictionary, UserEntity, UserVerb, UserPattern


# === PURE FUNCTIONS (CC=1 each) ===

def validate_dictionary_path(path: Path) -> bool:
    """Validate dictionary file path."""
    return path.suffix in ['.yaml', '.yml', '.json']


def create_empty_user_patterns() -> Dict[str, Dict]:
    """Create empty user patterns structure."""
    return {}


def extract_pattern_name_and_data(name: str, pattern: UserPattern) -> tuple:
    """Extract pattern name and data."""
    return (name, pattern.pattern, pattern.replacement)


def compile_single_regex(pattern_str: str) -> Union[re.Pattern, None]:
    """Compile single regex pattern."""
    return try_compile_regex(pattern_str)


def try_compile_regex(pattern_str: str) -> Union[re.Pattern, None]:
    """Try to compile regex pattern."""
    return handle_regex_compilation(pattern_str)


def compile_regex_with_flags(pattern_str: str) -> re.Pattern:
    """Compile regex with standard flags."""
    return re.compile(pattern_str, re.IGNORECASE)


def create_pattern_entry(regex: re.Pattern, replacement: str) -> Dict:
    """Create pattern entry."""
    return {'regex': regex, 'replacement': replacement}


def log_pattern_error(logger: logging.Logger, name: str, error: Exception):
    """Log pattern compilation error."""
    logger.error(f"Invalid regex pattern '{name}': {error}")


def get_pattern_replacement(pattern_dict: Dict, name: str) -> str:
    """Get replacement string for pattern."""
    return pattern_dict.get(name, {}).get('replacement', r'\1')


def apply_single_regex_pattern(text: str, regex: re.Pattern, replacement: str) -> str:
    """Apply single regex pattern to text."""
    return regex.sub(replacement, text)


def expand_single_word(word: str, abbreviations: Dict[str, str]) -> str:
    """Expand single word abbreviation."""
    clean_word = word.upper().rstrip('.,!?')
    return abbreviations.get(clean_word, word)


def split_text_to_words(text: str) -> List[str]:
    """Split text into words."""
    return text.split()


def join_words_to_text(words: List[str]) -> str:
    """Join words back to text."""
    return ' '.join(words)


def preprocess_with_abbreviations(text: str, abbreviations: Dict[str, str]) -> str:
    """Preprocess text with abbreviations."""
    words = split_text_to_words(text)
    expanded_words = expand_all_words(words, abbreviations)
    return join_words_to_text(expanded_words)


def expand_all_words(words: List[str], abbreviations: Dict[str, str]) -> List[str]:
    """Expand all words using abbreviations."""
    return [expand_single_word(w, abbreviations) for w in words]


def find_entity_synonyms(entities: Dict, word: str) -> Union[str, None]:
    """Find canonical form for entity synonym."""
    return find_first_entity_match(entities, word)


def check_entity_match_and_return(entity_name: str, entity, word: str) -> Union[str, None]:
    """Check entity match and return name if matched."""
    return entity_name if is_entity_synonym_match(entity, word) else None


def is_entity_synonym_match(entity, word: str) -> bool:
    """Check if word matches entity synonyms."""
    return check_entity_has_synonyms(entity) and check_word_in_entity_synonyms(entity, word)


def check_entity_has_synonyms(entity) -> bool:
    """Check if entity has synonyms attribute."""
    return has_synonyms_attribute(entity)


def check_word_in_entity_synonyms(entity, word: str) -> bool:
    """Check if word is in entity synonyms."""
    return word_in_synonyms(word, entity.synonyms)


def find_verb_synonyms(verbs: Dict, word: str) -> Union[str, None]:
    """Find canonical form for verb synonym."""
    return find_first_verb_match(verbs, word)


def check_verb_match_and_return(verb_name: str, verb, word: str) -> Union[str, None]:
    """Check verb match and return name if matched."""
    return verb_name if is_verb_synonym_match(verb, word) else None


def is_verb_synonym_match(verb, word: str) -> bool:
    """Check if word matches verb synonyms."""
    return check_verb_has_synonyms(verb) and check_word_in_verb_synonyms(verb, word)


def check_verb_has_synonyms(verb) -> bool:
    """Check if verb has synonyms attribute."""
    return has_synonyms_attribute(verb)


def check_word_in_verb_synonyms(verb, word: str) -> bool:
    """Check if word is in verb synonyms."""
    return word_in_synonyms(word, verb.synonyms)


def has_synonyms_attribute(obj) -> bool:
    """Check if object has synonyms attribute."""
    return hasattr(obj, 'synonyms')


def word_in_synonyms(word: str, synonyms: List[str]) -> bool:
    """Check if word is in synonyms list."""
    return word in synonyms


def normalize_single_word(word: str, entities: Dict, verbs: Dict) -> str:
    """Normalize single word with synonyms."""
    lower_word = word.lower()
    return find_word_replacement(lower_word, entities, verbs, word)


def find_word_replacement(lower_word: str, entities: Dict, verbs: Dict, original_word: str) -> str:
    """Find replacement for word in dictionaries."""
    entity_match = find_entity_synonyms(entities, lower_word)
    return get_best_word_match(entity_match, lower_word, verbs, original_word)


def get_best_word_match(entity_match: Union[str, None], lower_word: str, verbs: Dict, original_word: str) -> str:
    """Get best word match from available options."""
    return entity_match or find_verb_synonyms(verbs, lower_word) or original_word


def postprocess_with_synonyms(text: str, entities: Dict, verbs: Dict) -> str:
    """Postprocess text with synonym normalization."""
    words = split_text_to_words(text)
    normalized_words = normalize_all_words(words, entities, verbs)
    return join_words_to_text(normalized_words)


def normalize_all_words(words: List[str], entities: Dict, verbs: Dict) -> List[str]:
    """Normalize all words using synonym dictionaries."""
    return [normalize_single_word(w, entities, verbs) for w in words]


def apply_patterns_to_text(text: str, user_patterns: Dict) -> str:
    """Apply all user patterns to text."""
    result = text
    for name, pattern_data in user_patterns.items():
        result = apply_single_pattern_iteration(result, pattern_data)
    return result


def apply_single_pattern_iteration(text: str, pattern_data: Dict) -> str:
    """Apply single pattern iteration."""
    return apply_pattern_to_result(text, pattern_data)


def apply_pattern_to_result(text: str, pattern_data: Dict) -> str:
    """Apply single pattern to text result."""
    return apply_single_user_pattern(text, pattern_data)


def apply_single_user_pattern(text: str, pattern_data: Dict) -> str:
    """Apply single user pattern."""
    regex = get_pattern_regex(pattern_data)
    replacement = get_pattern_replacement_string(pattern_data)
    return apply_regex_if_exists(text, regex, replacement)


def get_pattern_regex(pattern_data: Dict):
    """Get regex from pattern data."""
    return pattern_data.get('regex')


def get_pattern_replacement_string(pattern_data: Dict) -> str:
    """Get replacement string from pattern data."""
    return pattern_data.get('replacement', r'\1')


def apply_regex_if_exists(text: str, regex, replacement: str) -> str:
    """Apply regex if it exists, otherwise return original text."""
    return apply_single_regex_pattern(text, regex, replacement) if regex else text


class TCEParserV151(TCEParserV101):
    """
    Extensible parser with user dictionary support.
    All methods have CC=1.
    """
    
    def __init__(self, dictionary_path: Optional[Path] = None):
        """Initialize with optional user dictionary path."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.user_dict = create_user_dictionary(dictionary_path)
        self.user_patterns = create_empty_user_patterns()
        self._compile_user_patterns()
    
    def load_dictionary(self, filepath: Union[str, Path]) -> bool:
        """Load additional dictionary from file."""
        success = load_dictionary_from_file(self.user_dict, filepath)
        return handle_dictionary_load_result(self, success)
    
    def add_entity(self, name: str, category: str = "object", **kwargs):
        """Add a custom entity to the dictionary."""
        entity = create_user_entity(name, category, **kwargs)
        add_entity_to_dictionary(self.user_dict, entity)
    
    def add_verb(self, verb: str, **kwargs):
        """Add a custom verb to the dictionary."""
        verb_obj = create_user_verb(verb, **kwargs)
        add_verb_to_dictionary(self.user_dict, verb_obj)
    
    def add_pattern(self, name: str, pattern: str, replacement: str, **kwargs):
        """Add a custom pattern to the dictionary."""
        pattern_obj = create_user_pattern(name, pattern, replacement, **kwargs)
        add_pattern_to_dictionary(self.user_dict, pattern_obj)
        self._compile_user_patterns()
    
    def parse(self, sentence: str) -> str:
        """Parse with user dictionary enhancements."""
        preprocessed = self._preprocess_with_user_dict(sentence)
        pattern_applied = self._apply_user_patterns(preprocessed)
        result = super().parse(pattern_applied)
        postprocessed = self._postprocess_with_user_dict(result)
        return postprocessed
    
    def _compile_user_patterns(self):
        """Compile regex patterns from user dictionary."""
        self.user_patterns = compile_all_user_patterns(self.user_dict, self.logger)
    
    def _preprocess_with_user_dict(self, text: str) -> str:
        """Pre-process text using user dictionary."""
        return preprocess_with_abbreviations(text, self.user_dict.abbreviations)
    
    def _apply_user_patterns(self, text: str) -> str:
        """Apply user patterns to text."""
        return apply_patterns_to_text(text, self.user_patterns)
    
    def _postprocess_with_user_dict(self, text: str) -> str:
        """Post-process text using user dictionary."""
        return postprocess_with_synonyms(text, self.user_dict.entities, self.user_dict.verbs)


# === HELPER FUNCTIONS ===

def create_user_dictionary(dictionary_path: Optional[Path]) -> UserDictionary:
    """Create user dictionary instance."""
    dictionary = UserDictionary(dictionary_path)
    return dictionary


def load_dictionary_from_file(user_dict: UserDictionary, filepath: Union[str, Path]) -> bool:
    """Load dictionary from file."""
    return user_dict.load_from_file(filepath)


def create_user_entity(name: str, category: str, **kwargs) -> UserEntity:
    """Create user entity."""
    return UserEntity(name=name, category=category, **kwargs)


def create_user_verb(verb: str, **kwargs) -> UserVerb:
    """Create user verb."""
    return UserVerb(verb=verb, **kwargs)


def create_user_pattern(name: str, pattern: str, replacement: str, **kwargs) -> UserPattern:
    """Create user pattern."""
    return UserPattern(name=name, pattern=pattern, replacement=replacement, **kwargs)


def add_entity_to_dictionary(user_dict: UserDictionary, entity: UserEntity):
    """Add entity to dictionary."""
    user_dict.add_entity(entity)


def add_verb_to_dictionary(user_dict: UserDictionary, verb: UserVerb):
    """Add verb to dictionary."""
    user_dict.add_verb(verb)


def add_pattern_to_dictionary(user_dict: UserDictionary, pattern: UserPattern):
    """Add pattern to dictionary."""
    user_dict.add_pattern(pattern)


def handle_dictionary_load_result(parser_instance, success: bool) -> bool:
    """Handle dictionary load result."""
    execute_compile_if_success(parser_instance, success)
    return success


def execute_compile_if_success(parser_instance, success: bool):
    """Execute compile patterns if successful."""
    execute_compile_patterns(parser_instance) if success else None


def compile_all_user_patterns(user_dict: UserDictionary, logger: logging.Logger) -> Dict:
    """Compile all user patterns."""
    patterns = create_empty_user_patterns()
    compile_main_patterns(patterns, user_dict.patterns, logger)
    compile_domain_patterns(patterns, user_dict.domains, logger)
    return patterns


def compile_main_patterns(patterns: Dict, main_patterns: Dict, logger: logging.Logger):
    """Compile patterns from main dictionary."""
    process_all_main_patterns(patterns, main_patterns, logger)


def process_main_pattern_entry(patterns: Dict, name: str, pattern, logger: logging.Logger):
    """Process main pattern entry."""
    process_single_main_pattern(patterns, name, pattern, logger)


def process_single_main_pattern(patterns: Dict, name: str, pattern, logger: logging.Logger):
    """Process single main pattern."""
    compile_and_store_pattern(patterns, name, pattern, logger)


def compile_domain_patterns(patterns: Dict, domains: Dict, logger: logging.Logger):
    """Compile patterns from domain dictionaries."""
    process_all_domains(patterns, domains, logger)


def process_domain_entry(patterns: Dict, domain, logger: logging.Logger):
    """Process domain entry."""
    process_single_domain(patterns, domain, logger)


def process_single_domain(patterns: Dict, domain, logger: logging.Logger):
    """Process single domain patterns."""
    compile_domain_specific_patterns(patterns, domain, logger)


def compile_domain_specific_patterns(patterns: Dict, domain, logger: logging.Logger):
    """Compile patterns for specific domain."""
    process_all_domain_patterns(patterns, domain, logger)


def process_domain_pattern_item(patterns: Dict, domain, name: str, pattern, logger: logging.Logger):
    """Process domain pattern item."""
    process_domain_pattern_entry(patterns, domain, name, pattern, logger)


def process_domain_pattern_entry(patterns: Dict, domain, name: str, pattern, logger: logging.Logger):
    """Process single domain pattern entry."""
    key = create_domain_pattern_key(domain.domain, name)
    compile_and_store_pattern(patterns, key, pattern, logger)


def create_domain_pattern_key(domain_name: str, pattern_name: str) -> str:
    """Create domain pattern key."""
    return f"{domain_name}:{pattern_name}"


def compile_and_store_pattern(patterns: Dict, name: str, pattern: UserPattern, logger: logging.Logger):
    """Compile and store single pattern."""
    regex = compile_single_regex(pattern.pattern)
    handle_pattern_compilation_result(patterns, name, regex, pattern.replacement, logger)


def handle_pattern_compilation_result(patterns: Dict, name: str, regex, replacement: str, logger: logging.Logger):
    """Handle pattern compilation result."""
    execute_regex_action(patterns, name, regex, replacement, logger)


def execute_regex_action(patterns: Dict, name: str, regex, replacement: str, logger: logging.Logger):
    """Execute appropriate action based on regex compilation."""
    execute_regex_success_action(patterns, name, regex, replacement) if regex else execute_regex_failure_action(logger, name)


def store_compiled_pattern(patterns: Dict, name: str, regex: re.Pattern, replacement: str):
    """Store compiled pattern."""
    patterns[name] = create_pattern_entry(regex, replacement)


def log_pattern_compilation_error(logger: logging.Logger, name: str):
    """Log pattern compilation error."""
    logger.error(f"Failed to compile pattern: {name}")


def create_extensible_parser(dictionary_path: Optional[Path] = None) -> TCEParserV151:
    """Create an extensible parser instance."""
    return TCEParserV151(dictionary_path)


def handle_regex_compilation(pattern_str: str) -> Union[re.Pattern, None]:
    """Handle regex compilation with error handling."""
    try:
        return compile_regex_with_flags(pattern_str)
    except re.error:
        return None


def find_first_entity_match(entities: Dict, word: str) -> Union[str, None]:
    """Find first matching entity."""
    matches = [check_entity_match_and_return(n, e, word) for n, e in entities.items()]
    return get_first_truthy_value(matches)


def find_first_verb_match(verbs: Dict, word: str) -> Union[str, None]:
    """Find first matching verb."""
    matches = [check_verb_match_and_return(n, v, word) for n, v in verbs.items()]
    return get_first_truthy_value(matches)


def get_first_truthy_value(values: List) -> Union[str, None]:
    """Get first truthy value from list."""
    return next((v for v in values if v), None)


def process_all_main_patterns(patterns: Dict, main_patterns: Dict, logger: logging.Logger):
    """Process all main patterns."""
    list(map(lambda item: process_main_pattern_entry(patterns, item[0], item[1], logger), main_patterns.items()))


def process_all_domains(patterns: Dict, domains: Dict, logger: logging.Logger):
    """Process all domains."""
    list(map(lambda domain: process_domain_entry(patterns, domain, logger), domains.values()))


def process_all_domain_patterns(patterns: Dict, domain, logger: logging.Logger):
    """Process all patterns in domain."""
    list(map(lambda item: process_domain_pattern_item(patterns, domain, item[0], item[1], logger), domain.patterns.items()))


def execute_regex_success_action(patterns: Dict, name: str, regex, replacement: str):
    """Execute action for successful regex compilation."""
    store_compiled_pattern(patterns, name, regex, replacement)


def execute_regex_failure_action(logger: logging.Logger, name: str):
    """Execute action for failed regex compilation."""
    log_pattern_compilation_error(logger, name)


def execute_compile_patterns(parser_instance):
    """Execute compile patterns."""
    parser_instance._compile_user_patterns()


# Aliases
ExtensibleTCEParser = TCEParserV151