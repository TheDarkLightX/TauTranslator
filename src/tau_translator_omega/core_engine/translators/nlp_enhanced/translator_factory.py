#!/usr/bin/env python3
"""
Translator Factory
================

Factory pattern implementation for creating and configuring translator components.
Provides clean, consistent instantiation of NLP enhanced translation system.

This factory encapsulates the complexity of component creation and configuration,
following the Factory Method and Abstract Factory patterns for clean architecture.

Usage:
    ```python
    # Simple usage - get default configured translator
    translator = TranslatorFactory.create_english_to_tau_translator()
    
    # Advanced usage - custom configuration
    config = TranslatorConfig(
        enable_amr_analysis=True,
        confidence_threshold=0.7,
        domain_specialization=['medical', 'financial']
    )
    translator = TranslatorFactory.create_translator(config)
    
    # Quick setup for different use cases
    medical_translator = TranslatorFactory.create_medical_translator()
    financial_translator = TranslatorFactory.create_financial_translator()
    ```

Design Patterns:
    - **Factory Method**: Creates specific translator types
    - **Builder Pattern**: Configurable translator construction  
    - **Strategy Pattern**: Pluggable semantic analyzers
    - **Dependency Injection**: Clean component composition
"""

from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field
from enum import Enum, auto

from .english_to_tau_translator import EnglishToTauTranslator
from .requirements_analyzer import RequirementsAnalyzer
from .amr_semantic_layer import AMRSemanticAnalyzer
from .incremental_parser import IncrementalTCEParser


class DomainSpecialization(Enum):
    """Supported domain specializations"""
    GENERAL = "general"
    MEDICAL = "medical"
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    BUSINESS = "business"
    SECURITY = "security"


class TranslationStrategy(Enum):
    """Translation strategy options"""
    PATTERN_BASED = "pattern_based"
    SEMANTIC_ENHANCED = "semantic_enhanced"
    HYBRID = "hybrid"


@dataclass
class TranslatorConfig:
    """
    Configuration for translator creation.
    
    Provides comprehensive configuration options for customizing
    translator behavior, performance, and specialization.
    """
    # Core settings
    enable_amr_analysis: bool = True
    enable_incremental_parsing: bool = True
    confidence_threshold: float = 0.6
    
    # Performance settings
    cache_size: int = 1000
    max_sentence_length: int = 200
    timeout_seconds: float = 5.0
    
    # Domain specialization
    domain_specializations: List[DomainSpecialization] = field(default_factory=list)
    custom_vocabulary: Dict[str, List[str]] = field(default_factory=dict)
    
    # Translation strategy
    translation_strategy: TranslationStrategy = TranslationStrategy.HYBRID
    
    # Quality settings
    require_high_confidence: bool = False
    enable_detailed_logging: bool = False
    
    # Advanced features
    enable_bidirectional: bool = True
    enable_document_processing: bool = True


class TranslatorFactory:
    """
    Factory for creating configured translator components.
    
    This factory provides multiple creation methods for different use cases,
    from simple default configurations to highly customized setups.
    """
    
    @staticmethod
    def create_english_to_tau_translator(config: Optional[TranslatorConfig] = None) -> EnglishToTauTranslator:
        """
        Create a standard English to Tau translator.
        
        Args:
            config: Optional configuration. Uses defaults if not provided.
            
        Returns:
            EnglishToTauTranslator: Configured translator instance
        """
        if config is None:
            config = TranslatorConfig()
        
        # Create core translator
        translator = EnglishToTauTranslator()
        
        # Apply configuration if needed
        if hasattr(translator, '_apply_config'):
            translator._apply_config(config)
        
        return translator
    
    @staticmethod
    def create_requirements_analyzer(config: Optional[TranslatorConfig] = None) -> RequirementsAnalyzer:
        """
        Create a configured requirements analyzer.
        
        Args:
            config: Optional configuration for analyzer setup
            
        Returns:
            RequirementsAnalyzer: Configured analyzer instance
        """
        if config is None:
            config = TranslatorConfig()
        
        analyzer = RequirementsAnalyzer()
        
        # Apply domain specializations if specified
        if config.domain_specializations:
            TranslatorFactory._apply_domain_specialization(analyzer, config.domain_specializations)
        
        return analyzer
    
    @staticmethod
    def create_amr_analyzer(config: Optional[TranslatorConfig] = None) -> AMRSemanticAnalyzer:
        """
        Create a configured AMR semantic analyzer.
        
        Args:
            config: Optional configuration for AMR setup
            
        Returns:
            AMRSemanticAnalyzer: Configured AMR analyzer instance
        """
        if config is None:
            config = TranslatorConfig()
        
        return AMRSemanticAnalyzer()
    
    @staticmethod
    def create_incremental_parser(config: Optional[TranslatorConfig] = None) -> IncrementalTCEParser:
        """
        Create a configured incremental parser.
        
        Args:
            config: Optional configuration for parser setup
            
        Returns:
            IncrementalTCEParser: Configured parser instance
        """
        if config is None:
            config = TranslatorConfig()
        
        return IncrementalTCEParser(cache_size=config.cache_size)
    
    @staticmethod
    def create_medical_translator() -> EnglishToTauTranslator:
        """
        Create a translator specialized for medical domain.
        
        Pre-configured with medical vocabulary and specialized patterns
        for healthcare and medical device requirements.
        
        Returns:
            EnglishToTauTranslator: Medical-specialized translator
        """
        config = TranslatorConfig(
            domain_specializations=[DomainSpecialization.MEDICAL],
            confidence_threshold=0.8,  # Higher threshold for medical
            custom_vocabulary={
                'medical_devices': ['cardiac', 'monitoring', 'arrhythmia', 'defibrillator', 'pacemaker'],
                'medical_actions': ['detect', 'monitor', 'therapy', 'stimulate', 'sense'],
                'safety_terms': ['patient', 'safety', 'critical', 'fail-safe', 'emergency']
            }
        )
        
        return TranslatorFactory.create_english_to_tau_translator(config)
    
    @staticmethod
    def create_financial_translator() -> EnglishToTauTranslator:
        """
        Create a translator specialized for financial domain.
        
        Pre-configured with financial vocabulary and specialized patterns
        for trading systems and financial regulations.
        
        Returns:
            EnglishToTauTranslator: Financial-specialized translator
        """
        config = TranslatorConfig(
            domain_specializations=[DomainSpecialization.FINANCIAL],
            confidence_threshold=0.75,
            custom_vocabulary={
                'financial_entities': ['portfolio', 'leverage', 'exposure', 'asset', 'transaction'],
                'financial_actions': ['trade', 'execute', 'settle', 'clear', 'hedge'],
                'risk_terms': ['risk', 'volatility', 'margin', 'collateral', 'limit']
            }
        )
        
        return TranslatorFactory.create_english_to_tau_translator(config)
    
    @staticmethod
    def create_security_translator() -> EnglishToTauTranslator:
        """
        Create a translator specialized for security domain.
        
        Pre-configured with security vocabulary and specialized patterns
        for cryptographic and access control requirements.
        
        Returns:
            EnglishToTauTranslator: Security-specialized translator
        """
        config = TranslatorConfig(
            domain_specializations=[DomainSpecialization.SECURITY],
            confidence_threshold=0.8,  # Higher threshold for security
            custom_vocabulary={
                'crypto_terms': ['encrypt', 'decrypt', 'key', 'cipher', 'hash', 'signature'],
                'access_terms': ['authenticate', 'authorize', 'permission', 'privilege', 'access'],
                'security_concepts': ['confidentiality', 'integrity', 'availability', 'secure']
            }
        )
        
        return TranslatorFactory.create_english_to_tau_translator(config)
    
    @staticmethod
    def create_high_performance_translator() -> EnglishToTauTranslator:
        """
        Create a translator optimized for high performance.
        
        Configured for maximum speed with larger caches and
        optimized processing for high-throughput scenarios.
        
        Returns:
            EnglishToTauTranslator: Performance-optimized translator
        """
        config = TranslatorConfig(
            cache_size=5000,  # Large cache
            enable_detailed_logging=False,  # Reduce overhead
            translation_strategy=TranslationStrategy.PATTERN_BASED,  # Faster strategy
            confidence_threshold=0.5  # Lower threshold for speed
        )
        
        return TranslatorFactory.create_english_to_tau_translator(config)
    
    @staticmethod
    def create_high_accuracy_translator() -> EnglishToTauTranslator:
        """
        Create a translator optimized for maximum accuracy.
        
        Configured for highest quality output with comprehensive
        analysis and strict confidence requirements.
        
        Returns:
            EnglishToTauTranslator: Accuracy-optimized translator
        """
        config = TranslatorConfig(
            enable_amr_analysis=True,
            enable_incremental_parsing=True,
            confidence_threshold=0.8,  # High confidence required
            require_high_confidence=True,
            enable_detailed_logging=True,
            translation_strategy=TranslationStrategy.SEMANTIC_ENHANCED
        )
        
        return TranslatorFactory.create_english_to_tau_translator(config)
    
    @staticmethod
    def _apply_domain_specialization(analyzer: RequirementsAnalyzer, 
                                   specializations: List[DomainSpecialization]) -> None:
        """
        Apply domain specializations to a requirements analyzer.
        
        Args:
            analyzer: Requirements analyzer to configure
            specializations: List of domain specializations to apply
        """
        # This would extend the analyzer with domain-specific patterns
        # For now, this is a placeholder for future enhancement
        pass


# Convenience functions for backward compatibility
def create_english_to_tau_translator() -> EnglishToTauTranslator:
    """Convenience function for creating default translator."""
    return TranslatorFactory.create_english_to_tau_translator()


def create_requirements_analyzer() -> RequirementsAnalyzer:
    """Convenience function for creating default requirements analyzer."""
    return TranslatorFactory.create_requirements_analyzer()


def create_amr_semantic_analyzer() -> AMRSemanticAnalyzer:
    """Convenience function for creating default AMR analyzer."""
    return TranslatorFactory.create_amr_analyzer()


def create_incremental_parser() -> IncrementalTCEParser:
    """Convenience function for creating default incremental parser."""
    return TranslatorFactory.create_incremental_parser()