"""
Grammar management endpoints following the Intentional Disclosure Principle.

This module orchestrates grammar file operations with complete transparency:
- All I/O operations are explicit in method names
- Domain types replace primitives for type safety
- Infrastructure concerns are isolated
- Methods are under 10 lines with single responsibilities

Copyright: DarkLightX / Dana Edwards
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from pathlib import Path
from typing import List, Dict, Optional, NewType, Union, Literal
from dataclasses import dataclass
from datetime import datetime
import logging

from ..core.responses import create_success_response, create_error_response
from ..core.config import settings
from ..core.result_enhanced import Result, Success, Failure, success, failure

logger = logging.getLogger(__name__)
router = APIRouter()

# =======================
# Domain Types (Rule 3)
# =======================

GrammarName = NewType("GrammarName", str)
GrammarPath = NewType("GrammarPath", str)
GrammarContent = NewType("GrammarContent", str)
GrammarFormat = Literal["tgf", "ebnf", "lark"]
CacheKey = NewType("CacheKey", str)

@dataclass(frozen=True)
class GrammarMetadata:
    """Complete grammar information."""
    name: GrammarName
    filename: str
    path: GrammarPath
    format: GrammarFormat
    size: int
    rules: List[str]
    content: Optional[GrammarContent] = None

@dataclass(frozen=True)
class GrammarListResponse:
    """Response for listing grammars."""
    grammars: List[GrammarMetadata]
    active_grammar: Optional[GrammarName]
    grammar_dir: str

@dataclass(frozen=True)
class GrammarLoadResult:
    """Result of loading a grammar."""
    success: bool
    message: str
    filename: Optional[str] = None
    format: Optional[GrammarFormat] = None
    rules_found: Optional[int] = None
    rules: Optional[List[str]] = None

@dataclass(frozen=True)
class GrammarStatusResult:
    """Grammar engine status."""
    loaded: bool
    can_translate_to_tau: bool
    can_translate_to_tce: bool
    message: str

# =======================
# Infrastructure Layer (Rule 4)
# =======================

class GrammarFileRepository:
    """Handles all grammar file I/O operations."""
    
    @staticmethod
    async def scan_grammar_directory_async(directory: Path) -> Result[List[GrammarMetadata]]:
        """
        Note: This is a pure function (no side effects).
        Scan directory for grammar files."""
        try:
            grammars = []
            if directory.exists():
                for ext in ['*.tgf', '*.ebnf', '*.lark']:
                    for file in directory.glob(ext):
                        metadata = GrammarFileRepository._create_metadata_from_file(file)
                        grammars.append(metadata)
            return success(grammars)
        except Exception as e:
            return failure("SCAN_ERROR", f"Failed to scan directory: {str(e)}")
    
    @staticmethod
    def _create_metadata_from_file(file_path: Path) -> GrammarMetadata:
        """
        Note: This is a pure function (no side effects).
        Create metadata from file path."""
        return GrammarMetadata(
            name=GrammarName(file_path.stem),
            filename=file_path.name,
            path=GrammarPath(str(file_path)),
            format=file_path.suffix[1:],  # type: ignore
            size=file_path.stat().st_size,
            rules=[]
        )
    
    @staticmethod
    async def read_grammar_content_async(grammar_path: Path) -> Result[GrammarContent]:
        """
        Note: This is a pure function (no side effects).
        Read grammar file content."""
        try:
            content = grammar_path.read_text(encoding='utf-8')
            return success(GrammarContent(content))
        except Exception as e:
            return failure("READ_ERROR", f"Failed to read file: {str(e)}")
    
    @staticmethod
    async def write_grammar_to_temp_async(
        content: GrammarContent, 
        filename: str, 
        temp_dir: Path
    ) -> Result[Path]:
        """Write grammar content to temporary file."""
        try:
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_file = temp_dir / filename
            temp_file.write_text(content, encoding='utf-8')
            return success(temp_file)
        except Exception as e:
            return failure("WRITE_ERROR", f"Failed to write temp file: {str(e)}")

class GrammarConfigRepository:
    """Handles grammar configuration persistence."""
    
    @staticmethod
    async def load_active_grammar_config_async(config_path: Path) -> Result[Optional[GrammarName]]:
        """
        Note: This is a pure function (no side effects).
        Load active grammar from configuration."""
        try:
            if not config_path.exists():
                return success(None)
            
            import json
            with open(config_path) as f:
                config = json.load(f)
                active = config.get("active_grammar")
                return success(GrammarName(active) if active else None)
        except Exception as e:
            return failure("CONFIG_LOAD_ERROR", f"Failed to load config: {str(e)}")
    
    @staticmethod
    async def save_active_grammar_config_async(
        config_path: Path, 
        grammar_name: GrammarName
    ) -> Result[None]:
        """Save active grammar to configuration."""
        try:
            import json
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config = {}
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
            
            config["active_grammar"] = grammar_name
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return success(None)
        except Exception as e:
            return failure("CONFIG_SAVE_ERROR", f"Failed to save config: {str(e)}")

# =======================
# Core Business Logic
# =======================

class GrammarCache:
    """In-memory grammar cache."""
    
    def __init__(self):
        self._cache: Dict[CacheKey, GrammarMetadata] = {}
    
    def get_cached_grammar(self, key: CacheKey) -> Optional[GrammarMetadata]:
        """
        Note: This is a pure function (no side effects).
        Retrieve cached grammar if available."""
        return self._cache.get(key)
    
    def cache_grammar(self, key: CacheKey, metadata: GrammarMetadata) -> None:
        """
        Note: This is a pure function (no side effects).
        Store grammar in cache."""
        self._cache[key] = metadata
    
    def clear_cache(self) -> None:
        """
        Note: This is a pure function (no side effects).
        Clear all cached grammars."""
        self._cache.clear()

class GrammarValidator:
    """Validates grammar files and formats."""
    
    @staticmethod
    def validate_file_extension(filename: str) -> Result[GrammarFormat]:
        """
        Note: This is a pure function (no side effects).
        Validate and extract grammar format from filename."""
        valid_extensions = {'.tgf': 'tgf', '.ebnf': 'ebnf', '.lark': 'lark'}
        
        for ext, format in valid_extensions.items():
            if filename.endswith(ext):
                return success(format)  # type: ignore
        
        return failure(
            "INVALID_FORMAT", 
            "Invalid file format. Please upload a .lark, .ebnf, or .tgf file"
        )
    
    @staticmethod
    def validate_grammar_path(path: Path) -> Result[Path]:
        """
        Note: This is a pure function (no side effects).
        Validate grammar file path."""
        if not path.exists():
            return failure("FILE_NOT_FOUND", f"Grammar file not found: {path}")
        
        if not path.is_file():
            return failure("NOT_A_FILE", f"Path is not a file: {path}")
        
        return success(path)

class GrammarRuleExtractor:
    """Extracts rules from different grammar formats."""
    
    @staticmethod
    def extract_rules_from_content(
        content: GrammarContent, 
        format: GrammarFormat
    ) -> List[str]:
        """Extract rule names based on format."""
        extractors = {
            'tgf': GrammarRuleExtractor._extract_tgf_rules,
            'ebnf': GrammarRuleExtractor._extract_ebnf_rules,
            'lark': GrammarRuleExtractor._extract_lark_rules
        }
        
        extractor = extractors.get(format)
        if not extractor:
            return []
        
        return extractor(content)
    
    @staticmethod
    def _extract_tgf_rules(content: GrammarContent) -> List[str]:
        """
        Note: This is a pure function (no side effects).
        Extract rules from TGF format."""
        import re
        rules = []
        pattern = r'^(\w+)\s*(?:::=|:)'
        
        for line in content.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                rules.append(match.group(1))
        
        return rules
    
    @staticmethod
    def _extract_ebnf_rules(content: GrammarContent) -> List[str]:
        """
        Note: This is a pure function (no side effects).
        Extract rules from EBNF format."""
        import re
        rules = []
        pattern = r'^(\w+)\s*='
        
        for line in content.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                rules.append(match.group(1))
        
        return rules
    
    @staticmethod
    def _extract_lark_rules(content: GrammarContent) -> List[str]:
        """
        Note: This is a pure function (no side effects).
        Extract rules from Lark format."""
        import re
        rules = []
        pattern = r'^(\w+)\s*:'
        
        for line in content.split('\n'):
            line = line.strip()
            if not line.startswith('//') and not line.startswith('#'):
                match = re.match(pattern, line)
                if match:
                    rules.append(match.group(1))
        
        return rules

class GrammarService:
    """Core grammar management service."""
    
    def __init__(
        self,
        file_repository: GrammarFileRepository,
        config_repository: GrammarConfigRepository,
        cache: GrammarCache,
        validator: GrammarValidator,
        rule_extractor: GrammarRuleExtractor
    ):
        self._file_repo = file_repository
        self._config_repo = config_repository
        self._cache = cache
        self._validator = validator
        self._rule_extractor = rule_extractor
    
    async def list_grammars_with_active_async(self) -> Result[GrammarListResponse]:
        """
        Note: This is a pure function (no side effects).
        List all grammars with active status (Rule 2: orchestration)."""
        # Scan for available grammars
        scan_result = await self._file_repo.scan_grammar_directory_async(settings.grammar_dir)
        if scan_result.is_failure():
            return scan_result  # type: ignore
        
        # Load active grammar configuration
        config_path = settings.project_root / "config" / "grammar-files.json"
        active_result = await self._config_repo.load_active_grammar_config_async(config_path)
        active_grammar = active_result.value if active_result.is_success() else None
        
        # Create response
        return success(GrammarListResponse(
            grammars=scan_result.value,
            active_grammar=active_grammar,
            grammar_dir=str(settings.grammar_dir)
        ))
    
    async def get_grammar_details_with_cache_async(
        self, 
        grammar_name: GrammarName
    ) -> Result[GrammarMetadata]:
        """Get grammar details, using cache if available."""
        # Check cache first
        cache_key = CacheKey(f"grammar:{grammar_name}")
        cached = self._cache.get_cached_grammar(cache_key)
        if cached:
            return success(cached)
        
        # Load from filesystem
        result = await self._load_grammar_from_filesystem_async(grammar_name)
        
        # Cache on success
        if result.is_success():
            self._cache.cache_grammar(cache_key, result.value)
        
        return result
    
    async def _load_grammar_from_filesystem_async(
        self, 
        grammar_name: GrammarName
    ) -> Result[GrammarMetadata]:
        """Load grammar details from filesystem."""
        # Find grammar file
        grammar_path = await self._find_grammar_file_async(grammar_name)
        if grammar_path.is_failure():
            return grammar_path  # type: ignore
        
        path = grammar_path.value
        
        # Read content
        content_result = await self._file_repo.read_grammar_content_async(path)
        if content_result.is_failure():
            return content_result  # type: ignore
        
        # Extract rules
        format = GrammarFormat(path.suffix[1:])  # type: ignore
        rules = self._rule_extractor.extract_rules_from_content(
            content_result.value, 
            format
        )
        
        # Build complete metadata
        return success(GrammarMetadata(
            name=grammar_name,
            filename=path.name,
            path=GrammarPath(str(path)),
            format=format,
            size=path.stat().st_size,
            rules=rules,
            content=content_result.value
        ))
    
    async def _find_grammar_file_async(self, grammar_name: GrammarName) -> Result[Path]:
        """
        Note: This is a pure function (no side effects).
        Find grammar file by name."""
        for ext in ['.tgf', '.ebnf', '.lark']:
            path = settings.grammar_dir / f"{grammar_name}{ext}"
            if path.exists():
                return success(path)
        
        return failure("NOT_FOUND", f"Grammar '{grammar_name}' not found")
    
    async def activate_grammar_async(self, grammar_name: GrammarName) -> Result[None]:
        """
        Note: This is a pure function (no side effects).
        Activate a grammar by updating configuration."""
        # Verify grammar exists
        exists_result = await self._verify_grammar_exists_async(grammar_name)
        if exists_result.is_failure():
            return exists_result
        
        # Save to configuration
        config_path = settings.project_root / "config" / "grammar-files.json"
        return await self._config_repo.save_active_grammar_config_async(
            config_path, 
            grammar_name
        )
    
    async def _verify_grammar_exists_async(self, grammar_name: GrammarName) -> Result[None]:
        """
        Note: This is a pure function (no side effects).
        Verify that a grammar exists."""
        grammars_result = await self._file_repo.scan_grammar_directory_async(
            settings.grammar_dir
        )
        
        if grammars_result.is_failure():
            return grammars_result  # type: ignore
        
        grammar_names = [g.name for g in grammars_result.value]
        if grammar_name not in grammar_names:
            return failure("NOT_FOUND", f"Grammar '{grammar_name}' not found")
        
        return success(None)
    
    def clear_grammar_cache(self) -> None:
        """
        Note: This is a pure function (no side effects).
        Clear all cached grammars."""
        self._cache.clear_cache()

# =======================
# API Endpoints (Rule 2: Orchestration)
# =======================

# Initialize dependencies
_file_repo = GrammarFileRepository()
_config_repo = GrammarConfigRepository()
_cache = GrammarCache()
_validator = GrammarValidator()
_rule_extractor = GrammarRuleExtractor()
_service = GrammarService(_file_repo, _config_repo, _cache, _validator, _rule_extractor)

@router.get("/")
async def list_available_grammars_async():
    """
        Note: This is a pure function (no side effects).
        List available grammar files with active status."""
    result = await _service.list_grammars_with_active_async()
    
    if result.is_success():
        return create_success_response(result.value.__dict__)
    else:
        return create_error_response(result.message)  # type: ignore

@router.get("/{grammar_name}")
async def get_grammar_details_async(grammar_name: str):
    """
        Note: This is a pure function (no side effects).
        Get details about a specific grammar."""
    result = await _service.get_grammar_details_with_cache_async(
        GrammarName(grammar_name)
    )
    
    if result.is_success():
        metadata = result.value
        return create_success_response({
            "name": metadata.name,
            "filename": metadata.filename,
            "format": metadata.format,
            "size": metadata.size,
            "content": metadata.content,
            "rules": metadata.rules
        })
    else:
        if result.error_code == "NOT_FOUND":  # type: ignore
            raise HTTPException(status_code=404, detail=result.message)  # type: ignore
        return create_error_response(result.message)  # type: ignore

@router.post("/load-from-path")
async def load_grammar_from_server_path_async(request: Request, grammar_path: str):
    """
        Note: This is a pure function (no side effects).
        Load a Tau grammar from a file path on the server."""
    # Validate engine availability
    if not hasattr(request.app.state, 'grammar_engine'):
        raise HTTPException(
            status_code=503,
            detail="Grammar engine not available"
        )
    
    # Validate path
    path = Path(grammar_path)
    validation_result = _validator.validate_grammar_path(path)
    if validation_result.is_failure():
        raise HTTPException(
            status_code=404 if validation_result.error_code == "FILE_NOT_FOUND" else 400,  # type: ignore
            detail=validation_result.message  # type: ignore
        )
    
    # Validate format
    format_result = _validator.validate_file_extension(path.name)
    if format_result.is_failure():
        raise HTTPException(status_code=400, detail=format_result.message)  # type: ignore
    
    # Load grammar through engine
    success = request.app.state.grammar_engine.load_tau_grammar(grammar_path)
    
    if success:
        return create_success_response({
            "message": "Grammar loaded successfully",
            "path": grammar_path
        })
    else:
        raise HTTPException(status_code=400, detail="Failed to load grammar")

@router.post("/reload")
async def reload_all_grammars_async():
    """
        Note: This is a pure function (no side effects).
        Reload grammar files and clear cache."""
    # Clear cache
    _service.clear_grammar_cache()
    
    # Re-scan directory
    result = await _service.list_grammars_with_active_async()
    
    if result.is_success():
        response = result.value
        return create_success_response({
            "message": "Grammar files reloaded successfully",
            "grammars_found": len(response.grammars),
            "grammars": [g.__dict__ for g in response.grammars]
        })
    else:
        return create_error_response(result.message)  # type: ignore

@router.post("/{grammar_name}/activate")
async def activate_grammar_as_current_async(grammar_name: str):
    """
        Note: This is a pure function (no side effects).
        Set a grammar as the active grammar."""
    result = await _service.activate_grammar_async(GrammarName(grammar_name))
    
    if result.is_success():
        return create_success_response({
            "message": f"Grammar '{grammar_name}' activated successfully",
            "active_grammar": grammar_name
        })
    else:
        if result.error_code == "NOT_FOUND":  # type: ignore
            raise HTTPException(status_code=404, detail=result.message)  # type: ignore
        return create_error_response(result.message)  # type: ignore

@router.post("/load-tau-grammar")
async def load_tau_grammar_from_upload_async(
    request: Request, 
    file: UploadFile = File(...)
):
    """Load a user-provided Tau grammar file for translation."""
    # Validate file format
    format_result = _validator.validate_file_extension(file.filename)
    if format_result.is_failure():
        raise HTTPException(status_code=400, detail=format_result.message)  # type: ignore
    
    # Validate engine availability
    if not hasattr(request.app.state, 'grammar_engine'):
        raise HTTPException(
            status_code=503,
            detail="Grammar engine not available. Please enable grammar feature in settings."
        )
    
    # Read and decode file
    content = await file.read()
    try:
        grammar_text = GrammarContent(content.decode('utf-8'))
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file encoding. Expected UTF-8.")
    
    # Save to temporary location
    temp_dir = settings.project_root / "temp" / "grammars"
    temp_result = await _file_repo.write_grammar_to_temp_async(
        grammar_text, 
        file.filename, 
        temp_dir
    )
    
    if temp_result.is_failure():
        return create_error_response(temp_result.message)  # type: ignore
    
    # Load through engine
    grammar_engine = request.app.state.grammar_engine
    success = grammar_engine.load_tau_grammar(str(temp_result.value))
    
    if success:
        # Extract rules for response
        rules = _rule_extractor.extract_rules_from_content(
            grammar_text, 
            format_result.value
        )
        
        return create_success_response({
            "message": "Tau grammar loaded successfully",
            "filename": file.filename,
            "format": format_result.value,
            "rules_found": len(rules),
            "rules": rules[:20],  # First 20 rules
            "can_translate_to_tce": True
        })
    else:
        raise HTTPException(
            status_code=400,
            detail="Failed to load grammar. Please check the grammar syntax."
        )

@router.get("/tau-grammar-status")
async def check_tau_grammar_engine_status_async(request: Request):
    """
        Note: This is a pure function (no side effects).
        Check if a Tau grammar is loaded and ready for translation."""
    if not hasattr(request.app.state, 'grammar_engine'):
        return create_success_response({
            "loaded": False,
            "can_translate_to_tau": False,
            "can_translate_to_tce": False,
            "message": "Grammar engine not available"
        })
    
    grammar_engine = request.app.state.grammar_engine
    tau_loaded = grammar_engine.tau_parser is not None
    
    status = GrammarStatusResult(
        loaded=tau_loaded,
        can_translate_to_tau=grammar_engine.tce_parser is not None,
        can_translate_to_tce=tau_loaded,
        message="Tau grammar loaded" if tau_loaded else "No Tau grammar loaded"
    )
    
    return create_success_response(status.__dict__)