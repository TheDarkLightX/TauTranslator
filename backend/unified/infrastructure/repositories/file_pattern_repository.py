"""
File-based implementation of IPatternRepository.
All file I/O operations are isolated in this infrastructure layer.

Copyright: DarkLightX/Dana Edwards
"""

import json
import yaml
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from ...core.domain_types import FilePath, Result, Success, Failure
from ...core.interfaces import IPatternRepository, IEventBus


class PatternFileHandler(FileSystemEventHandler):
    """Handles file system events for pattern files."""
    
    def __init__(self, event_bus: IEventBus, loop: asyncio.AbstractEventLoop):
        self.event_bus = event_bus
        self.loop = loop
        self.logger = logging.getLogger(__name__)
    
    def on_modified(self, event: FileModifiedEvent):
        """Handle file modification events."""
        if not event.is_directory:
            self.logger.info(f"Pattern file modified: {event.src_path}")
            # Schedule async event publishing
            asyncio.run_coroutine_threadsafe(
                self.event_bus.publish_event_async(
                    "file_changed",
                    {"path": event.src_path, "event_type": "modified"}
                ),
                self.loop
            )


class FilePatternRepository(IPatternRepository):
    """
    File-based pattern repository implementation.
    All file I/O operations are contained here following Rule 4.
    """
    
    def __init__(self, event_bus: Optional[IEventBus] = None):
        """Initialize with optional event bus for file watching."""
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self._observers: Dict[str, Observer] = {}
        self._loop = asyncio.get_event_loop()
    
    async def load_patterns_from_source_async(self, source_path: FilePath) -> Result[Dict[str, Any]]:
        """
        Load patterns from a file source.
        Rule 1: Name explicitly indicates async I/O from source.
        """
        try:
            path = Path(source_path)
            
            if not path.exists():
                return Failure("FILE_NOT_FOUND", f"Pattern file not found: {source_path}")
            
            if not path.is_file():
                return Failure("NOT_A_FILE", f"Path is not a file: {source_path}")
            
            # Determine file type and load accordingly
            if path.suffix.lower() == '.json':
                return await self._load_json_file_async(path)
            elif path.suffix.lower() in ['.yaml', '.yml']:
                return await self._load_yaml_file_async(path)
            else:
                return Failure("UNSUPPORTED_FORMAT", f"Unsupported file format: {path.suffix}")
                
        except Exception as e:
            self.logger.error(f"Error loading patterns from {source_path}: {e}")
            return Failure("LOAD_ERROR", str(e))
    
    async def save_patterns_to_destination_async(self, patterns: Dict[str, Any], destination: FilePath) -> Result[None]:
        """
        Save patterns to a file destination.
        Rule 1: Name explicitly indicates async I/O to destination.
        """
        try:
            path = Path(destination)
            
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save based on file extension
            if path.suffix.lower() == '.json':
                return await self._save_json_file_async(patterns, path)
            elif path.suffix.lower() in ['.yaml', '.yml']:
                return await self._save_yaml_file_async(patterns, path)
            else:
                return Failure("UNSUPPORTED_FORMAT", f"Unsupported file format: {path.suffix}")
                
        except Exception as e:
            self.logger.error(f"Error saving patterns to {destination}: {e}")
            return Failure("SAVE_ERROR", str(e))
    
    async def watch_for_pattern_changes_async(self, source_path: FilePath) -> Result[None]:
        """
        Watch for changes in pattern file.
        Uses watchdog for file system monitoring.
        """
        if not self.event_bus:
            return Failure("NO_EVENT_BUS", "Event bus required for file watching")
        
        try:
            path = Path(source_path)
            
            if not path.exists():
                return Failure("FILE_NOT_FOUND", f"Cannot watch non-existent file: {source_path}")
            
            # Stop existing observer if any
            if source_path in self._observers:
                self._observers[source_path].stop()
                self._observers[source_path].join()
            
            # Create new observer
            event_handler = PatternFileHandler(self.event_bus, self._loop)
            observer = Observer()
            observer.schedule(event_handler, str(path.parent), recursive=False)
            observer.start()
            
            self._observers[source_path] = observer
            
            return Success(None)
            
        except Exception as e:
            self.logger.error(f"Error setting up file watch for {source_path}: {e}")
            return Failure("WATCH_ERROR", str(e))
    
    async def export_patterns_as_json_async(self, patterns: Dict[str, Any]) -> Result[str]:
        """Export patterns as JSON string."""
        try:
            json_str = await asyncio.to_thread(
                json.dumps, patterns, indent=2, sort_keys=True
            )
            return Success(json_str)
        except Exception as e:
            return Failure("EXPORT_ERROR", f"Failed to export patterns: {e}")
    
    # --- Private I/O Methods ---
    
    async def _load_json_file_async(self, path: Path) -> Result[Dict[str, Any]]:
        """Load JSON file asynchronously."""
        try:
            content = await asyncio.to_thread(path.read_text, encoding='utf-8')
            data = await asyncio.to_thread(json.loads, content)
            return Success(data)
        except json.JSONDecodeError as e:
            return Failure("JSON_PARSE_ERROR", f"Invalid JSON: {e}")
        except Exception as e:
            return Failure("READ_ERROR", f"Failed to read JSON file: {e}")
    
    async def _load_yaml_file_async(self, path: Path) -> Result[Dict[str, Any]]:
        """Load YAML file asynchronously."""
        try:
            content = await asyncio.to_thread(path.read_text, encoding='utf-8')
            data = await asyncio.to_thread(yaml.safe_load, content)
            return Success(data)
        except yaml.YAMLError as e:
            return Failure("YAML_PARSE_ERROR", f"Invalid YAML: {e}")
        except Exception as e:
            return Failure("READ_ERROR", f"Failed to read YAML file: {e}")
    
    async def _save_json_file_async(self, data: Dict[str, Any], path: Path) -> Result[None]:
        """Save data as JSON file asynchronously."""
        try:
            content = await asyncio.to_thread(
                json.dumps, data, indent=2, sort_keys=True
            )
            await asyncio.to_thread(path.write_text, content, encoding='utf-8')
            return Success(None)
        except Exception as e:
            return Failure("WRITE_ERROR", f"Failed to write JSON file: {e}")
    
    async def _save_yaml_file_async(self, data: Dict[str, Any], path: Path) -> Result[None]:
        """Save data as YAML file asynchronously."""
        try:
            content = await asyncio.to_thread(
                yaml.dump, data, default_flow_style=False, sort_keys=True
            )
            await asyncio.to_thread(path.write_text, content, encoding='utf-8')
            return Success(None)
        except Exception as e:
            return Failure("WRITE_ERROR", f"Failed to write YAML file: {e}")
    
    def __del__(self):
        """Clean up observers on deletion."""
        for observer in self._observers.values():
            observer.stop()
            observer.join()