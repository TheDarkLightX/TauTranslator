"""
Multi-Stage Parser Pipeline following Craftsmanship Principles
Copyright: DarkLightX/Dana Edwards

Pipeline: Natural Language → ILR → TCE → Tau Code
Each method follows the 10-line limit rule.
"""

from typing import List, Optional
from dataclasses import dataclass
from .domain_types import Result, Success, Failure, AppError
from abc import ABC, abstractmethod

from .domain_types import SourceText, TranslationResult
from .interfaces import Parser, Transformer, Generator


@dataclass(frozen=True)
class NaturalLanguageInput:
    """Natural language text with metadata."""
    text: str
    context: dict = None


@dataclass(frozen=True) 
class ILRNode:
    """Intermediate Language Representation."""
    node_type: str
    content: str
    children: List['ILRNode'] = None
    metadata: dict = None


@dataclass(frozen=True)
class TCEStatement:
    """Tau Controlled English statement."""
    pattern: str
    bindings: dict
    constraints: List[str] = None


@dataclass(frozen=True)
class TauProgram:
    """Generated Tau program."""
    code: str
    ast: dict
    metadata: dict = None


class NaturalToILRParser(ABC):
    """Parses natural language into ILR."""
    
    @abstractmethod
    def parse_async(self, input: NaturalLanguageInput) -> Result[ILRNode]:
        """Parse natural language to ILR."""
        pass


class ILRToTCETransformer(ABC):
    """Transforms ILR to TCE statements."""
    
    @abstractmethod
    def transform_async(self, ilr: ILRNode) -> Result[List[TCEStatement]]:
        """Transform ILR node to TCE statements."""
        pass


class TCEToTauGenerator(ABC):
    """Generates Tau code from TCE."""
    
    @abstractmethod
    def generate_async(self, tce: List[TCEStatement]) -> Result[TauProgram]:
        """Generate Tau program from TCE statements."""
        pass


class ParserPipelineOrchestrator:
    """Orchestrates the parsing pipeline with clean separation."""
    
    def __init__(
        self,
        nl_parser: NaturalToILRParser,
        ilr_transformer: ILRToTCETransformer,
        tau_generator: TCEToTauGenerator
    ):
        self._nl_parser = nl_parser
        self._ilr_transformer = ilr_transformer
        self._tau_generator = tau_generator
    
    async def parse_natural_to_tau_async(self, text: str) -> Result[TauProgram]:
        """Full pipeline: Natural Language → Tau."""
        input_data = self._prepare_input(text)
        ilr_result = await self._parse_to_ilr_async(input_data)
        return await self._process_ilr_to_tau_async(ilr_result)
    
    async def parse_natural_to_tce_async(self, text: str) -> Result[List[TCEStatement]]:
        """Partial pipeline: Natural Language → TCE."""
        input_data = self._prepare_input(text)
        ilr_result = await self._parse_to_ilr_async(input_data)
        return await self._transform_ilr_to_tce_async(ilr_result)
    
    async def parse_tce_to_tau_async(self, tce: List[TCEStatement]) -> Result[TauProgram]:
        """Direct TCE → Tau conversion."""
        return await self._tau_generator.generate_async(tce)
    
    def _prepare_input(self, text: str) -> NaturalLanguageInput:
        """Prepare natural language input."""
        return NaturalLanguageInput(text=text, context={})
    
    async def _parse_to_ilr_async(self, input: NaturalLanguageInput) -> Result[ILRNode]:
        """Parse to ILR with error handling."""
        return await self._nl_parser.parse_async(input)
    
    async def _process_ilr_to_tau_async(self, ilr_result: Result[ILRNode]) -> Result[TauProgram]:
        """Process ILR through remaining stages."""
        tce_result = await self._transform_ilr_to_tce_async(ilr_result)
        return await self._generate_tau_from_tce_async(tce_result)
    
    async def _transform_ilr_to_tce_async(self, ilr_result: Result[ILRNode]) -> Result[List[TCEStatement]]:
        """Transform ILR to TCE with monadic chaining."""
        if isinstance(ilr_result, Success):
            return await self._ilr_transformer.transform_async(ilr_result.value)
        return ilr_result
    
    async def _generate_tau_from_tce_async(self, tce_result: Result[List[TCEStatement]]) -> Result[TauProgram]:
        """Generate Tau from TCE with monadic chaining."""
        if isinstance(tce_result, Success):
            return await self._tau_generator.generate_async(tce_result.value)
        return tce_result