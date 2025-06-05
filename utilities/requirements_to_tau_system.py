#!/usr/bin/env python3
"""
Requirements to Tau System with Iterative Feedback
=================================================

Complete system for converting natural language requirements
to formal Tau specifications with user feedback loop.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our refactored components
from refactored_llm_translator import (
    TranslatorFactory,
    TranslationRequest,
    TranslationResponse,
    ValidationResult
)
from nlp_requirements_engine import (
    NLPRequirementsEngine,
    RequirementType,
    TauSpecification
)


@dataclass
class RequirementsSession:
    """Represents a complete requirements engineering session."""
    session_id: str
    created_at: datetime
    language: str = "en"
    requirements_text: str = ""
    iterations: List['IterationData'] = field(default_factory=list)
    final_specification: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IterationData:
    """Data for a single iteration in the feedback loop."""
    iteration_number: int
    timestamp: datetime
    input_text: str
    generated_tau: str
    validation_result: Dict[str, Any]
    user_feedback: Optional[str] = None
    refinements_made: List[str] = field(default_factory=list)
    confidence_score: float = 0.0


class RequirementsToTauSystem:
    """
    Main system for converting requirements to Tau with feedback loop.
    Uses efficient algorithms and clean architecture.
    """
    
    def __init__(self, 
                 save_sessions: bool = True,
                 session_dir: Path = Path("sessions")):
        """Initialize the system."""
        self.translator = TranslatorFactory.create("auto")
        self.nlp_engine = NLPRequirementsEngine(
            use_spacy=False,  # Start with lightweight mode
            use_transformers=False
        )
        self.save_sessions = save_sessions
        self.session_dir = session_dir
        
        if save_sessions:
            self.session_dir.mkdir(exist_ok=True)
    
    async def start_interactive_session(self, initial_requirements: str = "") -> RequirementsSession:
        """
        Start an interactive requirements engineering session.
        
        Args:
            initial_requirements: Optional initial requirements text
            
        Returns:
            Completed session data
        """
        session = RequirementsSession(
            session_id=self._generate_session_id(),
            created_at=datetime.now(),
            requirements_text=initial_requirements
        )
        
        print("\n" + "="*70)
        print("🚀 TauTranslator Requirements Engineering System")
        print("="*70)
        print("\nThis system will help you convert natural language requirements")
        print("into formal Tau specifications through an iterative process.")
        print("\nType 'done' when satisfied, 'help' for commands, or 'quit' to exit.")
        print("="*70)
        
        # Get initial requirements if not provided
        if not initial_requirements:
            session.requirements_text = await self._get_initial_requirements()
        
        # Main iteration loop
        iteration_num = 0
        max_iterations = 10
        
        while iteration_num < max_iterations:
            iteration_num += 1
            
            # Process current requirements
            iteration_data = await self._process_iteration(
                session.requirements_text,
                iteration_num,
                session
            )
            
            session.iterations.append(iteration_data)
            
            # Check if user is satisfied
            if await self._check_satisfaction(iteration_data):
                session.final_specification = iteration_data.generated_tau
                break
            
            # Get refinement input
            refinement = await self._get_refinement_input(iteration_data)
            
            if refinement.lower() == 'quit':
                print("\nSession terminated by user.")
                break
            
            # Apply refinements
            session.requirements_text = self._apply_refinements(
                session.requirements_text,
                refinement,
                iteration_data
            )
        
        # Save session if enabled
        if self.save_sessions:
            self._save_session(session)
        
        # Display final summary
        self._display_session_summary(session)
        
        return session
    
    async def _process_iteration(self, 
                                requirements_text: str,
                                iteration_num: int,
                                session: RequirementsSession) -> IterationData:
        """Process a single iteration of requirements refinement."""
        print(f"\n{'='*70}")
        print(f"Iteration {iteration_num}")
        print(f"{'='*70}")
        
        # Extract structured requirements
        print("\n📋 Analyzing requirements...")
        extracted_reqs = self.nlp_engine.extract_requirements(requirements_text)
        
        # Display extracted information
        self._display_extracted_requirements(extracted_reqs)
        
        # Generate initial Tau specification
        print("\n🔄 Generating Tau specification...")
        
        # Use NLP engine for initial structure
        tau_spec = self.nlp_engine.requirements_to_tau(extracted_reqs)
        initial_tau = self.nlp_engine.generate_tau_code(tau_spec)
        
        # Refine with LLM translator
        request = TranslationRequest(
            text=requirements_text,
            max_iterations=2,
            interactive=False
        )
        
        response = await self.translator.translate(request)
        
        # Combine results for best output
        final_tau = self._combine_specifications(initial_tau, response.tau_code)
        
        # Validate the result
        validation = self.translator.validator.validate(final_tau)
        
        # Create iteration data
        iteration_data = IterationData(
            iteration_number=iteration_num,
            timestamp=datetime.now(),
            input_text=requirements_text,
            generated_tau=final_tau,
            validation_result=asdict(validation),
            confidence_score=validation.confidence
        )
        
        # Display results
        self._display_iteration_results(iteration_data)
        
        return iteration_data
    
    def _combine_specifications(self, spec1: str, spec2: str) -> str:
        """Intelligently combine two Tau specifications."""
        # Extract unique components from both
        components = {
            'streams': set(),
            'rules': set(),
            'invariants': set(),
            'functions': set()
        }
        
        for spec in [spec1, spec2]:
            lines = spec.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('sbf'):
                    components['streams'].add(line)
                elif line.startswith('r '):
                    components['rules'].add(line)
                elif line.startswith('always') or line.startswith('sometimes'):
                    components['invariants'].add(line)
                elif ':=' in line:
                    components['functions'].add(line)
        
        # Build combined specification
        result_lines = ["# Generated Tau Specification", "#" + "="*40, ""]
        
        if components['streams']:
            result_lines.append("# Stream Declarations")
            result_lines.extend(sorted(components['streams']))
            result_lines.append("")
        
        if components['functions']:
            result_lines.append("# Function Definitions")
            result_lines.extend(sorted(components['functions']))
            result_lines.append("")
        
        if components['rules']:
            result_lines.append("# Rules")
            result_lines.extend(sorted(components['rules']))
            result_lines.append("")
        
        if components['invariants']:
            result_lines.append("# Invariants and Temporal Properties")
            result_lines.extend(sorted(components['invariants']))
            result_lines.append("")
        
        return '\n'.join(result_lines)
    
    def _display_extracted_requirements(self, requirements: List):
        """Display extracted requirements in a user-friendly format."""
        if not requirements:
            print("  ⚠️  No structured requirements extracted")
            return
        
        print(f"\n  Found {len(requirements)} requirement(s):")
        for i, req in enumerate(requirements, 1):
            print(f"\n  {i}. {req.type.value.title()} Requirement")
            print(f"     Text: {req.text}")
            if req.entities.get('variables'):
                print(f"     Variables: {', '.join(req.entities['variables'])}")
            if req.temporal_markers:
                print(f"     Temporal: {', '.join(req.temporal_markers)}")
            if req.constraints:
                print(f"     Constraints: {', '.join(req.constraints)}")
            print(f"     Confidence: {req.confidence:.2f}")
    
    def _display_iteration_results(self, iteration_data: IterationData):
        """Display the results of an iteration."""
        print("\n📄 Generated Tau Specification:")
        print("-" * 70)
        print(iteration_data.generated_tau)
        print("-" * 70)
        
        validation = iteration_data.validation_result
        status = "✅ Valid" if validation['valid'] else "❌ Invalid"
        print(f"\n{status} - Confidence: {iteration_data.confidence_score:.2f}")
        
        if validation['errors']:
            print("\n⚠️  Errors found:")
            for error in validation['errors']:
                print(f"   - {error}")
        
        if validation['patterns_found']:
            print(f"\n✓ Patterns detected: {', '.join(validation['patterns_found'])}")
    
    async def _check_satisfaction(self, iteration_data: IterationData) -> bool:
        """Check if the user is satisfied with the current specification."""
        print("\n" + "-"*70)
        response = input("Are you satisfied with this specification? (yes/no/done): ").strip().lower()
        
        if response in ['yes', 'y', 'done']:
            iteration_data.user_feedback = "Accepted"
            return True
        
        return False
    
    async def _get_refinement_input(self, iteration_data: IterationData) -> str:
        """Get refinement input from the user."""
        print("\nHow would you like to refine the requirements?")
        print("Options:")
        print("  - Add more details about specific aspects")
        print("  - Clarify constraints or conditions")
        print("  - Specify temporal properties")
        print("  - Add new requirements")
        print("  - Type 'help' for more options")
        print("  - Type 'quit' to exit")
        
        refinement = input("\nRefinement: ").strip()
        iteration_data.user_feedback = refinement
        
        return refinement
    
    def _apply_refinements(self, 
                          current_requirements: str,
                          refinement: str,
                          iteration_data: IterationData) -> str:
        """Apply user refinements to requirements."""
        # Handle special commands
        if refinement.lower() == 'help':
            self._show_help()
            return current_requirements
        
        # Check if refinement is a complete replacement
        if refinement.lower().startswith("replace:"):
            new_requirements = refinement[8:].strip()
            iteration_data.refinements_made.append("Complete replacement")
            return new_requirements
        
        # Check if adding specific types of requirements
        refinement_lower = refinement.lower()
        
        additions = []
        
        if "temporal" in refinement_lower or "always" in refinement_lower:
            additions.append("Added temporal properties")
        
        if "constraint" in refinement_lower or "limit" in refinement_lower:
            additions.append("Added constraints")
        
        if "monitor" in refinement_lower or "log" in refinement_lower:
            additions.append("Added monitoring requirements")
        
        iteration_data.refinements_made.extend(additions)
        
        # Append refinement to requirements
        return f"{current_requirements}\n{refinement}"
    
    async def _get_initial_requirements(self) -> str:
        """Get initial requirements from user."""
        print("\nPlease describe your system requirements in natural language.")
        print("You can describe:")
        print("  - What the system should do")
        print("  - Constraints and limits")
        print("  - Safety requirements")
        print("  - Temporal properties (always, never, sometimes)")
        print("\nPress Enter twice when done.\n")
        
        lines = []
        while True:
            line = input()
            if not line and lines and not lines[-1]:
                break
            lines.append(line)
        
        return '\n'.join(lines).strip()
    
    def _show_help(self):
        """Show help information."""
        print("\n" + "="*70)
        print("HELP - Refinement Options")
        print("="*70)
        print("\nYou can refine requirements by:")
        print("  1. Adding more specific details")
        print("  2. Clarifying ambiguous terms")
        print("  3. Adding temporal properties (always, sometimes, never)")
        print("  4. Specifying exact constraints (e.g., 'temperature between 20 and 80')")
        print("  5. Adding monitoring/logging requirements")
        print("\nSpecial commands:")
        print("  - replace: <new requirements> - Replace all requirements")
        print("  - done - Accept current specification")
        print("  - quit - Exit without saving")
        print("  - help - Show this help")
        print("="*70)
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _save_session(self, session: RequirementsSession):
        """Save session data to file."""
        filename = self.session_dir / f"session_{session.session_id}.json"
        
        # Convert to serializable format
        session_data = {
            'session_id': session.session_id,
            'created_at': session.created_at.isoformat(),
            'language': session.language,
            'requirements_text': session.requirements_text,
            'final_specification': session.final_specification,
            'iterations': [
                {
                    'iteration_number': it.iteration_number,
                    'timestamp': it.timestamp.isoformat(),
                    'input_text': it.input_text,
                    'generated_tau': it.generated_tau,
                    'validation_result': it.validation_result,
                    'user_feedback': it.user_feedback,
                    'refinements_made': it.refinements_made,
                    'confidence_score': it.confidence_score
                }
                for it in session.iterations
            ],
            'metadata': session.metadata
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        logger.info(f"Session saved to {filename}")
    
    def _display_session_summary(self, session: RequirementsSession):
        """Display summary of the session."""
        print("\n" + "="*70)
        print("SESSION SUMMARY")
        print("="*70)
        print(f"\nSession ID: {session.session_id}")
        print(f"Total iterations: {len(session.iterations)}")
        
        if session.iterations:
            avg_confidence = sum(it.confidence_score for it in session.iterations) / len(session.iterations)
            print(f"Average confidence: {avg_confidence:.2f}")
        
        if session.final_specification:
            print("\n✅ Final Tau Specification:")
            print("-" * 70)
            print(session.final_specification)
            print("-" * 70)
            
            # Count specification components
            lines = session.final_specification.split('\n')
            streams = sum(1 for line in lines if line.strip().startswith('sbf'))
            rules = sum(1 for line in lines if line.strip().startswith('r '))
            invariants = sum(1 for line in lines if any(line.strip().startswith(kw) for kw in ['always', 'sometimes', 'never']))
            
            print(f"\nSpecification contains:")
            print(f"  - {streams} stream declaration(s)")
            print(f"  - {rules} rule(s)")
            print(f"  - {invariants} temporal property/properties")
        
        if self.save_sessions:
            print(f"\n💾 Session saved to: {self.session_dir}/session_{session.session_id}.json")


# Batch processing for multiple requirements
class BatchRequirementsProcessor:
    """Process multiple requirements documents in batch."""
    
    def __init__(self, system: RequirementsToTauSystem):
        self.system = system
    
    async def process_batch(self, requirements_files: List[Path]) -> Dict[str, Any]:
        """Process multiple requirements files."""
        results = {}
        
        for file_path in requirements_files:
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue
            
            try:
                with open(file_path, 'r') as f:
                    requirements = f.read()
                
                # Process without interaction
                request = TranslationRequest(
                    text=requirements,
                    max_iterations=3,
                    interactive=False
                )
                
                response = await self.system.translator.translate(request)
                
                results[str(file_path)] = {
                    'success': True,
                    'tau_specification': response.tau_code,
                    'confidence': response.confidence,
                    'iterations': response.iterations_used
                }
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                results[str(file_path)] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results


# Example usage and entry point
async def main():
    """Main entry point for the requirements to Tau system."""
    system = RequirementsToTauSystem()
    
    # Example: Start with predefined requirements
    example_requirements = """
    Create a smart home temperature control system.
    
    The system must monitor temperature sensors in each room.
    Temperature must be maintained between 18 and 25 degrees Celsius.
    
    If temperature drops below 18, activate heating.
    If temperature rises above 25, activate cooling.
    
    The system should log all temperature readings every minute.
    Emergency override must always be available.
    
    Energy saving mode activates between 23:00 and 06:00.
    """
    
    # Run interactive session
    session = await system.start_interactive_session(example_requirements)
    
    return session


if __name__ == "__main__":
    asyncio.run(main())