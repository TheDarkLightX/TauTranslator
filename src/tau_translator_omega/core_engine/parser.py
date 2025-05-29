"""
Provides the GrammarDrivenParser for parsing source code using a loaded grammar plugin
and transforming the result into the project's AST.
"""

from typing import Optional, Any, Type # Any will be replaced by Lark's Tree later
import os
from pathlib import Path
import logging # Import logging
import importlib # Import importlib

# Assuming Plugin class is in plugin_manager
from tau_translator_omega.core_engine.plugin_manager import Plugin 
from tau_translator_omega.core_engine.ast_nodes import ASTNode # ModuleNode removed as transformer returns expression node directly for simple_math
from tau_translator_omega.core_engine.lark_transformer import SimpleMathTransformer # Import the transformer

# Import Lark exceptions for specific handling
from lark import Lark, Tree, UnexpectedInput, ParseError as LarkParseError, LarkError


class ParserError(Exception):
    """Custom exception for errors related to parsing or parser setup."""
    pass


class GrammarDrivenParser:
    """
    Parses source code using a grammar definition provided by a plugin
    and transforms the resulting CST into a project-specific AST.
    """

    def __init__(self, grammar_plugin: Plugin):
        """
        Initializes the parser with a loaded grammar plugin.

        Args:
            grammar_plugin: A loaded Plugin object of type 'grammar_definition'.
                            It's expected to have 'grammar_config' populated by
                            GrammarPluginValidator, including 'grammar_formalism'
                            and 'grammar_file_path'.
        """
        if not grammar_plugin or grammar_plugin.plugin_type != "grammar_definition":
            raise ValueError(
                "GrammarDrivenParser requires a valid 'grammar_definition' plugin."
            )
        
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initializing GrammarDrivenParser with plugin: {grammar_plugin}")

        # Determine project root directory (assuming parser.py is in src/tau_translator_omega/core_engine/)
        # This navigates up three levels from parser.py's directory.
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        self.logger.debug(f"Project root directory determined as: {self.project_root_dir}")

        self.plugin = grammar_plugin
        self.grammar_config = grammar_plugin.grammar_config
        self.grammar_file_path = self.grammar_config.get('grammar_file_path')
        self.parser_instance = None
        self.transformer_instance = None
        self.transformer_class_name = None

        if not self.grammar_config or not self.grammar_file_path:
            msg = "Grammar configuration or grammar file path is missing."
            self.logger.error(msg)
            raise ParserError(msg)

        formalism = self.grammar_config.get('formalism', 'Lark') # Default to Lark
        self.logger.debug(f"Parser Init: manifest_dict from self.plugin.manifest is: {getattr(self.plugin, 'manifest', {})}")

        try:
            if formalism == 'Lark':
                if not os.path.isfile(self.grammar_file_path):
                    self.logger.error(f"Grammar file not found: {self.grammar_file_path}")
                    raise FileNotFoundError(f"Grammar file not found: {self.grammar_file_path}")
                
                with open(self.grammar_file_path, 'r', encoding='utf-8') as f:
                    grammar_content = f.read()
                if not grammar_content.strip():
                    self.logger.error(f"Lark grammar file is empty: {self.grammar_file_path}")
                    raise ValueError(f"Lark grammar file is empty: {self.grammar_file_path}")

                # Log the grammar content for debugging
                self.logger.debug(f"Grammar content before Lark instantiation:\n{grammar_content}")

                # Determine the directory for common grammars
                common_grammars_dir = os.path.join(
                    self.project_root_dir, # Use absolute project root
                    "src", "tau_translator_omega", "core_engine", "grammars"
                )
                self.logger.debug(f"Common grammars directory for Lark import_paths: {common_grammars_dir}")

                # Initialize Lark parser instance
                try:
                    if self.transformer_instance:
                        logging.debug(f"Parser Init: Transformer instance will be used post-parsing: {self.transformer_instance}")
                        # Do NOT pass the transformer to Lark constructor here.
                        # It will be used explicitly in the parse() method via .transform(cst)
                        self.parser_instance = Lark(
                            grammar_content,
                            parser=self.grammar_config.get('parser_type', 'lalr'),
                            lexer='contextual',
                            start=self.grammar_config.get('start_symbol', 'start'),
                            keep_all_tokens=self.grammar_config.get('keep_all_tokens', False),
                            propagate_positions=self.grammar_config.get('propagate_positions', True), # Crucial for locations
                            maybe_placeholders=self.grammar_config.get('maybe_placeholders', False),
                            debug=self.grammar_config.get('debug_lark', False) # Lark's internal debug
                        )
                    else:
                        # No transformer instance, Lark handles parsing alone.
                        logging.debug("Parser Init: No transformer instance provided. Lark will produce CST.")
                        self.parser_instance = Lark(
                            grammar_content,
                            parser=self.grammar_config.get('parser_type', 'lalr'),
                            lexer='contextual',
                            start=self.grammar_config.get('start_symbol', 'start'),
                            keep_all_tokens=self.grammar_config.get('keep_all_tokens', False),
                            propagate_positions=self.grammar_config.get('propagate_positions', True),
                            maybe_placeholders=self.grammar_config.get('maybe_placeholders', False),
                            debug=self.grammar_config.get('debug_lark', False)
                        )
                    logging.info(f"Lark parser initialized successfully with grammar: {self.grammar_file_path}")
                except LarkError as e:
                    # Catch Lark-specific errors during grammar processing or parser creation
                    self.logger.error(f"Error processing Lark grammar file: {self.grammar_file_path}. Lark error: {e}")
                    raise ParserError(f"Error processing Lark grammar file: {self.grammar_file_path}. Lark error details: {e}") from e
                except ValueError as e:
                    # This will now catch "Grammar is empty", "Unsupported formalism", "Unknown formalism"
                    self.logger.error(f"Parser initialization error due to ValueError: {e}")
                    raise ParserError(f"Parser initialization error due to ValueError: {e}") from e
                except Exception as e: # Generic catch-all for other unexpected init issues
                    self.logger.error(f"An unexpected error occurred during parser initialization: {e}", exc_info=True)
                    raise ParserError(f"An unexpected error occurred during parser initialization: {e}") from e

            elif formalism == 'ANTLR':
                # Correctly wrap ValueError in ParserError
                msg = f"Unsupported grammar formalism: {formalism}"
                self.logger.error(msg)
                raise ValueError(msg) # This will be caught by the general ValueError handler below
            else:
                # Correctly wrap ValueError in ParserError
                msg = f"Unknown grammar formalism: {formalism}"
                self.logger.error(msg)
                raise ValueError(msg) # This will be caught by the general ValueError handler below

            # Transformer loading logic (common for Lark, potentially adaptable)
            # manifest_dict = getattr(self.plugin, 'manifest', {})
            # Using grammar_config which should have manifest details resolved by PluginManager/Validator
            manifest_dict = self.grammar_config.get('manifest', {})
            self.logger.debug(f"Parser Init: transformer_path_str from manifest_dict.get is: {manifest_dict.get('transformer_class')}")
            transformer_fqn_from_manifest = manifest_dict.get('transformer_class')

            if transformer_fqn_from_manifest:
                self.logger.debug(f"Parser: Attempting to load transformer module '{transformer_fqn_from_manifest.rsplit('.', 1)[0]}' and class '{transformer_fqn_from_manifest.rsplit('.', 1)[-1]}'.")
                self.transformer_class_name = transformer_fqn_from_manifest
                try:
                    module_path, class_name = self.transformer_class_name.rsplit('.', 1)
                    module = importlib.import_module(module_path)
                    TransformerClass = getattr(module, class_name)
                    self.transformer_instance = TransformerClass() # Instantiate the transformer
                    self.logger.info(f"Successfully instantiated transformer: {self.transformer_class_name}")
                except ImportError as e:
                    self.logger.error(f"Failed to import transformer module {module_path} for {self.transformer_class_name}: {e}", exc_info=True)
                    self.transformer_instance = None # Ensure it's None on failure
                    raise ParserError(f"Failed to import or instantiate transformer class '{self.transformer_class_name}': {e}") from e
                except AttributeError as e:
                    self.logger.error(f"Failed to find transformer class {class_name} in module {module_path} for {self.transformer_class_name}: {e}", exc_info=True)
                    self.transformer_instance = None # Ensure it's None on failure
                    raise ParserError(f"Failed to import or instantiate transformer class '{self.transformer_class_name}': {e}") from e
                except Exception as e: # Catch any other exception during instantiation
                    self.logger.error(f"An unexpected error occurred while loading/instantiating transformer {self.transformer_class_name}: {e}", exc_info=True)
                    self.transformer_instance = None # Ensure it's None on failure
                    raise ParserError(f"Failed to import or instantiate transformer class '{self.transformer_class_name}': {e}") from e
            else:
                self.logger.warning("No 'transformer_class' specified in plugin manifest. "
                                  "Transformation step will not be available.")
        except FileNotFoundError as e:
            self.logger.error(f"Grammar file processing error: {e}")
            raise ParserError(f"Grammar file processing error: {e}") from e
        except ValueError as e:
            # This will now catch "Grammar is empty", "Unsupported formalism", "Unknown formalism"
            self.logger.error(f"Parser initialization error due to ValueError: {e}")
            raise ParserError(f"Parser initialization error due to ValueError: {e}") from e
        except LarkParseError as e:
            self.logger.error(f"Error processing Lark grammar file: {self.grammar_file_path}. Lark error: {e}")
            raise ParserError(f"Error processing Lark grammar file: {self.grammar_file_path}. Lark error details: {e}") from e
        except Exception as e: # Generic catch-all for other unexpected init issues
            self.logger.error(f"An unexpected error occurred during parser initialization: {e}", exc_info=True)
            raise ParserError(f"An unexpected error occurred during parser initialization: {e}") from e

    def parse(self, source_code: str) -> Any:
        """
        Parses the given source code string.

        Args:
            source_code: The source code to parse.

        Returns:
            An ASTNode representing the root of the parsed Abstract Syntax Tree.
        """
        if not self.parser_instance:
            raise ParserError("Parser not initialized. Call _initialize_parser first or ensure plugin is valid.")
        
        grammar_path_for_log = "unknown (plugin not fully initialized)"
        if hasattr(self, 'plugin') and self.plugin and hasattr(self.plugin, 'grammar_config') and isinstance(self.plugin.grammar_config, dict):
            grammar_path_for_log = self.plugin.grammar_config.get('grammar_file_path', 'unknown (path not in config)')
        
        logging.debug(f"Attempting to parse source code: '{source_code}'")
        try:
            cst = self.parser_instance.parse(source_code)
            logging.debug(f"Successfully parsed source code. CST:\n{cst.pretty() if cst else 'None'}")
        except LarkError as e:
            # Catching generic LarkError and providing more context
            error_message = f"Lark parsing error: {e}\n"
            if hasattr(e, 'context') and e.context:
                error_message += f"Context: {e.context}\n"
            if hasattr(e, 'allowed') and e.allowed:
                error_message += f"Allowed tokens: {e.allowed}\n"
            if hasattr(e, 'considered_tokens') and e.considered_tokens:
                error_message += f"Considered tokens: {e.considered_tokens}\n"
            logging.error(error_message)
            raise ParserError(error_message) from e
        except Exception as e:
            logging.error(f"An unexpected error occurred during CST generation: {e}", exc_info=True)
            raise ParserError(f"An unexpected error occurred during CST generation: {e}") from e

        if self.transformer_instance:
            logging.debug(f"Transforming CST to AST using: {type(self.transformer_instance)}")
            if source_code == "-5": # Log specific details for a known failing case
                logging.error(f"DIAGNOSTIC (for input '-5'): Transformer type: {type(self.transformer_instance)}")
                logging.error(f"DIAGNOSTIC (for input '-5'): Transformer methods: {dir(self.transformer_instance)}")
                logging.error(f"DIAGNOSTIC (for input '-5'): CST for '-5':\n{cst.pretty()}")
            try:
                ast = self.transformer_instance.transform(cst) # CST is lark.Tree
                logging.debug(f"Successfully transformed CST to AST. AST root type: {type(ast)}")
                return ast
            except Exception as e:
                logging.error(f"An unexpected error occurred during AST transformation: {e}", exc_info=True)
                raise ParserError(f"An unexpected error occurred during AST transformation: {e}") from e
        return cst # Return CST if no transformer

    def transform(self, cst: Tree) -> Any:
        """Transforms a Concrete Syntax Tree (CST) to an Abstract Syntax Tree (AST)
        using the loaded transformer instance.

        Args:
            cst: The lark.Tree object (CST) to transform.

        Returns:
            The transformed AST, or the original CST if no transformer is available
            or an error occurs during transformation.
            
        Raises:
            NotImplementedError: If no transformer instance is available.
        """
        if not self.transformer_instance:
            self.logger.error("Transformation called, but no transformer instance is available. "
                              "Ensure 'transformer_class' is correctly specified in the grammar plugin manifest.")
            # Option 1: Raise an error
            raise NotImplementedError("No transformer instance available for AST transformation.")
            # Option 2: Return CST with a warning (less strict)
            # self.logger.warning("Returning raw CST as no transformer is available.")
            # return cst

        try:
            self.logger.debug(f"Transforming CST using {self.transformer_class_name}")
            # The CST from Lark is directly passable to the transformer's transform method
            ast = self.transformer_instance.transform(cst)
            self.logger.debug("CST successfully transformed to AST.")
            return ast
        except LarkError as e:
            # Catch Lark-specific errors during transformation (e.g., VisitError)
            self.logger.error(f"Lark error during transformation with {self.transformer_class_name}: {e}", exc_info=True)
            raise ParserError(f"Lark error during AST transformation with '{self.transformer_class_name}': {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error during transformation with {self.transformer_class_name}: {e}", exc_info=True)
            raise ParserError(f"Unexpected error during AST transformation with '{self.transformer_class_name}': {e}") from e

    def _load_class_from_fqn(self, fqn: str):
        # Placeholder for actual implementation if needed for dynamic loading
        pass
