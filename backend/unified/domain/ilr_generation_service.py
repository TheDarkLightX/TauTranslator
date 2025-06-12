"""
ILR generation service following the Intentional Disclosure Principle.

Handles ILR structure generation with all methods ≤10 lines following IDP Rule 2.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Dict, Any
from returns.result import Result, Success, Failure

from .ilr_types import (
    ILRNode, ILRProgram, FunctionDeclaration, VariableDeclaration,
    AssignmentStatement, AssertionStatement, TemporalStatement,
    QuantifierExpression, LogicalExpression, VariableReference,
    NumericConstant, FunctionParameter, PatternType, PatternMatch,
    DataType, QuantifierType, LogicalOperator, TemporalOperator,
    FunctionName, VariableName, ILRJson
)
from .ilr_expression_service import ExpressionParsingService, TemporalExpressionService
from ..infrastructure.ilr_infrastructure import PatternMatcher, ValidationHelper


class ILRGenerationService:
    """Generates ILR structures from pattern matches."""
    
    def __init__(self):
        self._expression_parser = ExpressionParsingService()
        self._temporal_parser = TemporalExpressionService()
    
    def generate_ilr_from_pattern(self, pattern_match: PatternMatch, text: str) -> Result[ILRJson, str]:
        """Generate ILR JSON from pattern match."""
        components = PatternMatcher.extract_pattern_components(pattern_match)
        
        # Route to appropriate generator based on pattern type
        generator_map = {
            PatternType.PREDICATE_DEFINITION: self._generate_predicate_ilr,
            PatternType.FUNCTION_DEFINITION: self._generate_function_ilr,
            PatternType.UNIVERSAL: self._generate_universal_ilr,
            PatternType.EXISTENTIAL: self._generate_existential_ilr,
            PatternType.CONDITIONAL: self._generate_conditional_ilr,
            PatternType.ASSIGNMENT: self._generate_assignment_ilr,
            PatternType.BOOLEAN_EXPR: self._generate_boolean_ilr,
            PatternType.NEGATION: self._generate_negation_ilr,
            PatternType.STREAM_ASSIGNMENT: self._generate_stream_ilr,
            PatternType.STREAM_RULE: self._generate_stream_rule_ilr,
            PatternType.TEMPORAL_ALWAYS: self._generate_temporal_always_ilr,
            PatternType.SBF_INPUT: self._generate_sbf_input_ilr,
            PatternType.SBF_OUTPUT: self._generate_sbf_output_ilr,
        }
        
        generator = generator_map.get(pattern_match.pattern_type)
        if not generator:
            return Failure(f"No generator for pattern type: {pattern_match.pattern_type}")
        
        return generator(components)
    
    def _generate_predicate_ilr(self, components: Dict[str, str]) -> Result[ILRJson, str]:
        """Generate ILR for predicate definition."""
        # Parse predicate body
        body_result = self._expression_parser.parse_expression(components['body'])
        if isinstance(body_result, Failure):
            return Failure(f"Failed to parse predicate body: {body_result.failure()}")
        
        # Create parameters
        params = self._create_function_parameters(components['parameters'])
        
        # Create function declaration
        func_decl = FunctionDeclaration(
            name=FunctionName(components['predicate_name']),
            parameters=params,
            return_type=DataType.BOOLEAN,
            body=[{"type": "RETURN", "value": body_result.unwrap().to_dict()}]
        )
        
        # Create ILR program
        program = ILRProgram(declarations=[func_decl], statements=[])
        return Success(program.to_json())
    
    def _generate_function_ilr(self, components: Dict[str, str]) -> Result[ILRJson, str]:
        """Generate ILR for function definition."""
        # Parse function body
        body_result = self._expression_parser.parse_expression(components['body'])
        if isinstance(body_result, Failure):
            return Failure(f"Failed to parse function body: {body_result.failure()}")
        
        # Create parameters
        params = self._create_function_parameters(components['parameters'])
        
        # Create function declaration
        func_decl = FunctionDeclaration(
            name=FunctionName(components['function_name']),
            parameters=params,
            return_type=DataType.AUTO,  # Infer from body
            body=[{"type": "RETURN", "value": body_result.unwrap().to_dict()}]
        )
        
        # Create ILR program
        program = ILRProgram(declarations=[func_decl], statements=[])
        return Success(program.to_json())
    
    def _generate_universal_ilr(self, components: Dict[str, str]) -> Result[ILRJson, str]:
        """Generate ILR for universal quantification."""
        # Parse condition
        condition_result = self._expression_parser.parse_expression(components['condition'])
        if isinstance(condition_result, Failure):
            return Failure(f"Failed to parse condition: {condition_result.failure()}")
        
        # Create bound variables
        bound_vars = self._create_bound_variables(components)
        
        # Create quantifier expression
        quantifier = QuantifierExpression(
            quantifier=QuantifierType.FOR_ALL,
            bound_variables=bound_vars,
            body=condition_result.unwrap()
        )
        
        # Wrap in assertion
        assertion = AssertionStatement(quantifier)
        program = ILRProgram(declarations=[], statements=[assertion])
        return Success(program.to_json())
    
    def _generate_existential_ilr(self, components: Dict[str, str]) -> Result[ILRJson, str]:
        """Generate ILR for existential quantification."""
        # Parse condition
        condition_result = self._expression_parser.parse_expression(components['condition'])
        if isinstance(condition_result, Failure):
            return Failure(f"Failed to parse condition: {condition_result.failure()}")
        
        # Create bound variables
        bound_vars = self._create_bound_variables(components)
        
        # Create quantifier expression
        quantifier = QuantifierExpression(
            quantifier=QuantifierType.EXISTS,
            bound_variables=bound_vars,
            body=condition_result.unwrap()
        )
        
        # Wrap in assertion
        assertion = AssertionStatement(quantifier)
        program = ILRProgram(declarations=[], statements=[assertion])
        return Success(program.to_json())
    
    def _generate_conditional_ilr(self, components: Dict[str, str]) -> Result[ILRJson, str]:
        """Generate ILR for conditional statement."""
        # Parse condition and consequence
        cond_result = self._expression_parser.parse_expression(components['condition'])
        if isinstance(cond_result, Failure):
            return Failure(f"Failed to parse condition: {cond_result.failure()}")
        
        cons_result = self._expression_parser.parse_expression(components['consequence'])
        if isinstance(cons_result, Failure):
            return Failure(f"Failed to parse consequence: {cons_result.failure()}")
        
        # Create implication
        implication = LogicalExpression(
            LogicalOperator.IMPLIES,
            [cond_result.unwrap(), cons_result.unwrap()]
        )
        
        # Wrap in assertion
        assertion = AssertionStatement(implication)
        program = ILRProgram(declarations=[], statements=[assertion])
        return Success(program.to_json())
    
    def _generate_assignment_ilr(self, components: Dict[str, str]) -> Result[ILRJson, str]:
        """Generate ILR for assignment statement."""
        # Parse value expression
        value_result = self._expression_parser.parse_expression(components['value'])
        if isinstance(value_result, Failure):
            return Failure(f"Failed to parse value: {value_result.failure()}")
        
        # Create variable declaration with initial value
        var_decl = VariableDeclaration(
            name=VariableName(components['variable']),
            data_type=DataType.AUTO,
            initial_value=value_result.unwrap()
        )
        
        # Create ILR program
        program = ILRProgram(declarations=[var_decl], statements=[])
        return Success(program.to_json())
    
    def _generate_boolean_ilr(self, components: Dict[str, str]) -> Result[ILRJson, str]:
        """Generate ILR for boolean expression."""
        # Parse expression
        expr_result = self._expression_parser.parse_expression(components['expression'])
        if isinstance(expr_result, Failure):
            return Failure(f"Failed to parse expression: {expr_result.failure()}")
        
        # Wrap in assertion
        assertion = AssertionStatement(expr_result.unwrap())
        program = ILRProgram(declarations=[], statements=[assertion])
        return Success(program.to_json())
    
    def _generate_negation_ilr(self, components: Dict[str, str]) -> Result[ILRJson, str]:
        """Generate ILR for negation."""
        # Parse inner expression
        expr_result = self._expression_parser.parse_expression(components['expression'])
        if isinstance(expr_result, Failure):
            return Failure(f"Failed to parse expression: {expr_result.failure()}")
        
        # Create NOT expression
        negation = LogicalExpression(LogicalOperator.NOT, [expr_result.unwrap()])
        
        # Wrap in assertion
        assertion = AssertionStatement(negation)
        program = ILRProgram(declarations=[], statements=[assertion])
        return Success(program.to_json())
    
    def _generate_stream_ilr(self, components: Dict[str, str]) -> Result[ILRJson, str]:
        """Generate ILR for stream assignment."""
        # Create stream variable with temporal qualifier
        stream_ref = VariableReference(
            VariableName(components['stream_name']),
            TemporalQualifier(0)  # at time t
        )
        
        # Parse value
        value_result = self._expression_parser.parse_expression(components['value'])
        if isinstance(value_result, Failure):
            return Failure(f"Failed to parse value: {value_result.failure()}")
        
        # Create assignment
        assignment = AssignmentStatement(
            target=VariableName(components['stream_name']),
            value=value_result.unwrap()
        )
        
        # Create stream declaration
        stream_decl = VariableDeclaration(
            name=VariableName(components['stream_name']),
            data_type=DataType.STREAM
        )
        
        program = ILRProgram(declarations=[stream_decl], statements=[assignment])
        return Success(program.to_json())
    
    def _generate_stream_rule_ilr(self, components: Dict[str, str]) -> Result[ILRJson, str]:
        """Generate ILR for stream rule."""
        # Parse left side (stream reference)
        left_parts = components['left_side'].split('[')
        stream_name = left_parts[0]
        
        # Parse right side expression
        right_result = self._temporal_parser.parse_temporal_expression(components['right_side'])
        if isinstance(right_result, Failure):
            return Failure(f"Failed to parse stream rule: {right_result.failure()}")
        
        # Create assignment
        assignment = AssignmentStatement(
            target=VariableName(stream_name),
            value=right_result.unwrap()
        )
        
        program = ILRProgram(declarations=[], statements=[assignment])
        return Success(program.to_json())
    
    def _generate_temporal_always_ilr(self, components: Dict[str, str]) -> Result[ILRJson, str]:
        """Generate ILR for temporal always."""
        # Parse temporal expression
        expr_result = self._temporal_parser.parse_temporal_expression(components['expression'])
        if isinstance(expr_result, Failure):
            return Failure(f"Failed to parse temporal expression: {expr_result.failure()}")
        
        # Create temporal statement
        temporal_stmt = TemporalStatement(
            operator=TemporalOperator.ALWAYS,
            expression=expr_result.unwrap()
        )
        
        program = ILRProgram(declarations=[], statements=[temporal_stmt])
        return Success(program.to_json())
    
    def _generate_sbf_input_ilr(self, components: Dict[str, str]) -> Result[ILRJson, str]:
        """Generate ILR for SBF input declaration."""
        # Extract stream names from sbf_input(i1, i2, ...)
        params_text = components.get('group_0', '')
        stream_names = ValidationHelper.parse_parameter_list(params_text)
        
        # Create stream declarations
        declarations = [
            VariableDeclaration(
                name=VariableName(name),
                data_type=DataType.STREAM
            )
            for name in stream_names
        ]
        
        # Add SBF metadata
        sbf_declaration = {
            "type": "SBF_DECLARATION",
            "direction": "INPUT",
            "streams": stream_names
        }
        
        program_dict = ILRProgram(declarations=declarations, statements=[]).to_dict()
        program_dict["program"]["sbf_declaration"] = sbf_declaration
        
        import json
        return Success(ILRJson(json.dumps(program_dict, indent=2)))
    
    def _generate_sbf_output_ilr(self, components: Dict[str, str]) -> Result[ILRJson, str]:
        """Generate ILR for SBF output declaration."""
        # Extract stream names from sbf_output(o1, o2, ...)
        params_text = components.get('group_0', '')
        stream_names = ValidationHelper.parse_parameter_list(params_text)
        
        # Create stream declarations
        declarations = [
            VariableDeclaration(
                name=VariableName(name),
                data_type=DataType.STREAM
            )
            for name in stream_names
        ]
        
        # Add SBF metadata
        sbf_declaration = {
            "type": "SBF_DECLARATION",
            "direction": "OUTPUT",
            "streams": stream_names
        }
        
        program_dict = ILRProgram(declarations=declarations, statements=[]).to_dict()
        program_dict["program"]["sbf_declaration"] = sbf_declaration
        
        import json
        return Success(ILRJson(json.dumps(program_dict, indent=2)))
    
    # Helper methods (all ≤10 lines)
    
    def _create_function_parameters(self, params_str: str) -> List[FunctionParameter]:
        """Create function parameters from parameter string."""
        param_names = ValidationHelper.parse_parameter_list(params_str)
        return [
            FunctionParameter(name=name, data_type=DataType.AUTO)
            for name in param_names
        ]
    
    def _create_bound_variables(self, components: Dict[str, str]) -> List[Dict[str, str]]:
        """Create bound variables for quantifiers."""
        bound_vars = []
        
        if components.get('variable1'):
            bound_vars.append({
                "name": components['variable1'],
                "data_type": DataType.INTEGER.value
            })
        
        if components.get('variable2'):
            bound_vars.append({
                "name": components['variable2'],
                "data_type": DataType.INTEGER.value
            })
        
        return bound_vars