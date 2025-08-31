"""Adapter layer for educational autocomplete service.

This module bridges the API layer with the core autocomplete service,
transforming between API models and domain models while maintaining
backward compatibility.

Copyright (c) 2025 DarkLightX/Dana Edwards. All rights reserved.
"""

from typing import List, Optional, Dict, Any
from ..core.result_enhanced import Result, Success, Failure

from ..core.autocomplete import (
    EducationalAutocompleteService,
    SuggestionRequest,
    EducationalSuggestion,
    SpecificationContext as DomainContext,
    TargetLanguage,
    CompletionType
)
from ..core.domain_types import SourceText, PositionInfo


class AutocompleteAdapter:
    """Adapts API requests to educational autocomplete service."""
    
    def __init__(self, autocomplete_service: EducationalAutocompleteService):
        """Initialize with autocomplete service dependency."""
        self._service = autocomplete_service
    
    async def get_suggestions_async(
        self,
        text: str,
        position: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Result[List[Dict[str, Any]], str]:
        """Transform API request and get suggestions."""
        request_result = self._create_domain_request(text, position, context)
        if isinstance(request_result, Failure):
            return request_result
        
        suggestions_result = await self._service.get_suggestions_async(
            request_result.unwrap()
        )
        return suggestions_result.map(self._transform_suggestions_to_api)
    
    def _create_domain_request(
        self,
        text: str,
        position: int,
        context: Optional[Dict[str, Any]]
    ) -> Result[SuggestionRequest]:
        """Create domain request from API parameters."""
        try:
            source = SourceText(text)
            pos_info = PositionInfo(position=position)
            domain_context = self._create_domain_context(context)
            return Success(SuggestionRequest(
                text=source,
                position=pos_info,
                context=domain_context
            ))
        except Exception as e:
            return Failure(f"Failed to create request: {e}")
    
    def _create_domain_context(
        self,
        api_context: Optional[Dict[str, Any]]
    ) -> Optional[DomainContext]:
        """Transform API context to domain context."""
        if not api_context:
            return None
        
        language = self._detect_target_language(api_context)
        completion_type = self._detect_completion_type(api_context)
        
        return DomainContext(
            target_language=language,
            completion_type=completion_type,
            custom_data=api_context
        )
    
    def _detect_target_language(
        self,
        context: Dict[str, Any]
    ) -> TargetLanguage:
        """Detect target language from context."""
        language = context.get('language', '').lower()
        if language == 'tau':
            return TargetLanguage.TAU
        elif language == 'tce':
            return TargetLanguage.TCE
        return TargetLanguage.AUTO_DETECT
    
    def _detect_completion_type(
        self,
        context: Dict[str, Any]
    ) -> CompletionType:
        """Detect completion type from context."""
        comp_type = context.get('completion_type', '').lower()
        type_map = {
            'keyword': CompletionType.KEYWORD,
            'concept': CompletionType.CONCEPT,
            'pattern': CompletionType.PATTERN,
            'example': CompletionType.EXAMPLE
        }
        return type_map.get(comp_type, CompletionType.AUTO)
    
    def _transform_suggestions_to_api(
        self,
        suggestions: List[EducationalSuggestion]
    ) -> List[Dict[str, Any]]:
        """Transform domain suggestions to API format."""
        return [self._suggestion_to_dict(s) for s in suggestions]
    
    def _suggestion_to_dict(
        self,
        suggestion: EducationalSuggestion
    ) -> Dict[str, Any]:
        """Convert single suggestion to API dictionary."""
        return {
            'text': suggestion.text.value,
            'type': suggestion.suggestion_type.value,
            'confidence': suggestion.confidence,
            'description': suggestion.description,
            'example': suggestion.example,
            'category': suggestion.category,
            'metadata': suggestion.metadata or {}
        }
    
    async def get_backward_compatible_suggestions(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Result[List[str]]:
        """Provide backward compatible simple string suggestions."""
        api_context = {'context': context} if context else None
        result = await self.get_suggestions_async(text, len(text), api_context)
        return result.map(lambda suggs: [s['text'] for s in suggs])