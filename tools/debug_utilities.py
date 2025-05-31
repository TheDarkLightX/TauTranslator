#!/usr/bin/env python3
"""
Advanced Debugging Utilities for TauTranslator
=============================================

Comprehensive debugging tools following VibeArchitect principles.
"""

import sys
import traceback
import functools
import time
import logging
import json
import inspect
from typing import Any, Callable, Dict, List, Optional
from contextlib import contextmanager
from pathlib import Path
import psutil
import os


class AdvancedDebugger:
    """Advanced debugging with multiple inspection modes."""
    
    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file or Path("debug.log")
        self.traces = []
        self.performance_data = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def trace_function(self, detailed: bool = False):
        """Decorator to trace function execution."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_name = f"{func.__module__}.{func.__qualname__}"
                
                # Capture call context
                frame = inspect.currentframe()
                call_info = {
                    'function': func_name,
                    'args': self._safe_repr(args) if detailed else f"<{len(args)} args>",
                    'kwargs': self._safe_repr(kwargs) if detailed else f"<{len(kwargs)} kwargs>",
                    'caller': self._get_caller_info(frame),
                    'timestamp': time.time()
                }
                
                self.logger.debug(f"ENTER: {func_name}")
                if detailed:
                    self.logger.debug(f"  Args: {call_info['args']}")
                    self.logger.debug(f"  Kwargs: {call_info['kwargs']}")
                
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.perf_counter() - start_time
                    
                    call_info.update({
                        'result': self._safe_repr(result) if detailed else f"<{type(result).__name__}>",
                        'execution_time': execution_time,
                        'success': True
                    })
                    
                    self.logger.debug(f"EXIT:  {func_name} ({execution_time:.4f}s)")
                    if detailed and result is not None:
                        self.logger.debug(f"  Result: {call_info['result']}")
                    
                    self.traces.append(call_info)
                    return result
                
                except Exception as e:
                    execution_time = time.perf_counter() - start_time
                    call_info.update({
                        'error': str(e),
                        'exception_type': type(e).__name__,
                        'execution_time': execution_time,
                        'success': False,
                        'traceback': traceback.format_exc()
                    })
                    
                    self.logger.error(f"ERROR: {func_name} after {execution_time:.4f}s: {e}")
                    self.traces.append(call_info)
                    raise
            
            return wrapper
        return decorator
    
    def monitor_performance(self, func: Callable) -> Callable:
        """Decorator to monitor function performance."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            process = psutil.Process()
            
            # Before execution
            start_time = time.perf_counter()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            start_cpu = process.cpu_percent()
            
            try:
                result = func(*args, **kwargs)
                
                # After execution  
                end_time = time.perf_counter()
                end_memory = process.memory_info().rss / 1024 / 1024  # MB
                end_cpu = process.cpu_percent()
                
                perf_data = {
                    'function': f"{func.__module__}.{func.__qualname__}",
                    'execution_time': end_time - start_time,
                    'memory_before_mb': start_memory,
                    'memory_after_mb': end_memory,
                    'memory_delta_mb': end_memory - start_memory,
                    'cpu_before': start_cpu,
                    'cpu_after': end_cpu,
                    'timestamp': time.time()
                }
                
                self.performance_data.append(perf_data)
                
                # Log performance warnings
                if perf_data['execution_time'] > 1.0:
                    self.logger.warning(f"SLOW: {perf_data['function']} took {perf_data['execution_time']:.2f}s")
                
                if perf_data['memory_delta_mb'] > 50:
                    self.logger.warning(f"MEMORY: {perf_data['function']} used {perf_data['memory_delta_mb']:.1f}MB")
                
                return result
                
            except Exception:
                end_time = time.perf_counter()
                end_memory = process.memory_info().rss / 1024 / 1024
                
                self.performance_data.append({
                    'function': f"{func.__module__}.{func.__qualname__}",
                    'execution_time': end_time - start_time,
                    'memory_before_mb': start_memory,
                    'memory_after_mb': end_memory,
                    'memory_delta_mb': end_memory - start_memory,
                    'error': True,
                    'timestamp': time.time()
                })
                raise
        
        return wrapper
    
    @contextmanager
    def debug_context(self, context_name: str):
        """Context manager for debugging blocks of code."""
        self.logger.debug(f"CONTEXT ENTER: {context_name}")
        start_time = time.perf_counter()
        
        try:
            yield self
        except Exception as e:
            self.logger.error(f"CONTEXT ERROR in {context_name}: {e}")
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            self.logger.debug(f"CONTEXT EXIT: {context_name} ({elapsed:.4f}s)")
    
    def breakpoint_if(self, condition: bool, message: str = "Conditional breakpoint"):
        """Conditional breakpoint."""
        if condition:
            self.logger.critical(f"BREAKPOINT: {message}")
            # Start debugger if available
            try:
                import pdb
                pdb.set_trace()
            except:
                print(f"BREAKPOINT HIT: {message}")
                print("Stack trace:")
                traceback.print_stack()
    
    def assert_performance(self, func: Callable, max_time: float = 1.0, max_memory_mb: float = 100.0):
        """Assert performance constraints on function."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            process = psutil.Process()
            start_time = time.perf_counter()
            start_memory = process.memory_info().rss / 1024 / 1024
            
            result = func(*args, **kwargs)
            
            elapsed = time.perf_counter() - start_time
            memory_used = process.memory_info().rss / 1024 / 1024 - start_memory
            
            if elapsed > max_time:
                raise AssertionError(f"Performance assertion failed: {func.__name__} took {elapsed:.3f}s (max: {max_time}s)")
            
            if memory_used > max_memory_mb:
                raise AssertionError(f"Memory assertion failed: {func.__name__} used {memory_used:.1f}MB (max: {max_memory_mb}MB)")
            
            return result
        
        return wrapper
    
    def dump_traces(self, output_file: Optional[Path] = None):
        """Dump execution traces to file."""
        output_file = output_file or Path("execution_traces.json")
        
        with open(output_file, 'w') as f:
            json.dump({
                'traces': self.traces,
                'performance_data': self.performance_data,
                'summary': {
                    'total_function_calls': len(self.traces),
                    'successful_calls': len([t for t in self.traces if t.get('success', False)]),
                    'failed_calls': len([t for t in self.traces if not t.get('success', True)]),
                    'average_execution_time': sum(t.get('execution_time', 0) for t in self.traces) / len(self.traces) if self.traces else 0
                }
            }, f, indent=2)
        
        self.logger.info(f"Traces dumped to {output_file}")
    
    def _safe_repr(self, obj: Any, max_length: int = 100) -> str:
        """Safe representation of objects for logging."""
        try:
            repr_str = repr(obj)
            if len(repr_str) > max_length:
                return repr_str[:max_length] + "..."
            return repr_str
        except:
            return f"<{type(obj).__name__} object>"
    
    def _get_caller_info(self, frame) -> Dict[str, Any]:
        """Get information about the caller."""
        try:
            caller_frame = frame.f_back.f_back  # Skip wrapper frame
            return {
                'filename': caller_frame.f_code.co_filename,
                'line_number': caller_frame.f_lineno,
                'function_name': caller_frame.f_code.co_name
            }
        except:
            return {'filename': 'unknown', 'line_number': 0, 'function_name': 'unknown'}


class InteractiveDebugger:
    """Interactive debugging utilities."""
    
    @staticmethod
    def inspect_object(obj: Any, max_depth: int = 2) -> Dict[str, Any]:
        """Deep inspection of Python objects."""
        def _inspect_recursive(obj, depth=0):
            if depth > max_depth:
                return f"<max depth reached: {type(obj).__name__}>"
            
            if obj is None:
                return None
            elif isinstance(obj, (str, int, float, bool)):
                return obj
            elif isinstance(obj, (list, tuple)):
                return [_inspect_recursive(item, depth + 1) for item in obj[:10]]  # Limit to 10 items
            elif isinstance(obj, dict):
                return {k: _inspect_recursive(v, depth + 1) for k, v in list(obj.items())[:10]}
            elif hasattr(obj, '__dict__'):
                return {
                    '__class__': obj.__class__.__name__,
                    '__module__': getattr(obj.__class__, '__module__', 'unknown'),
                    'attributes': {k: _inspect_recursive(v, depth + 1) 
                                 for k, v in obj.__dict__.items() if not k.startswith('_')}
                }
            else:
                return f"<{type(obj).__name__}>"
        
        return {
            'type': type(obj).__name__,
            'module': getattr(type(obj), '__module__', 'unknown'),
            'content': _inspect_recursive(obj),
            'methods': [method for method in dir(obj) if callable(getattr(obj, method)) and not method.startswith('_')],
            'size_bytes': sys.getsizeof(obj)
        }
    
    @staticmethod
    def trace_execution_path(func: Callable):
        """Trace execution path through code."""
        execution_path = []
        
        def trace_calls(frame, event, arg):
            if event == 'call':
                execution_path.append({
                    'function': frame.f_code.co_name,
                    'filename': frame.f_code.co_filename,
                    'line': frame.f_lineno,
                    'event': event
                })
            return trace_calls
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            old_trace = sys.gettrace()
            sys.settrace(trace_calls)
            
            try:
                result = func(*args, **kwargs)
                return result, execution_path
            finally:
                sys.settrace(old_trace)
        
        return wrapper
    
    @staticmethod
    def memory_tracker():
        """Track memory usage over time."""
        import tracemalloc
        
        class MemoryTracker:
            def __init__(self):
                self.snapshots = []
                tracemalloc.start()
            
            def snapshot(self, label: str = ""):
                snapshot = tracemalloc.take_snapshot()
                top_stats = snapshot.statistics('lineno')
                
                self.snapshots.append({
                    'label': label,
                    'timestamp': time.time(),
                    'total_memory': sum(stat.size for stat in top_stats),
                    'top_allocations': [
                        {
                            'filename': stat.traceback.format()[0].split(':')[0],
                            'line': stat.traceback.format()[0].split(':')[1] if ':' in stat.traceback.format()[0] else 'unknown',
                            'size_mb': stat.size / 1024 / 1024
                        }
                        for stat in top_stats[:10]
                    ]
                })
            
            def compare_snapshots(self, idx1: int = -2, idx2: int = -1):
                if len(self.snapshots) < 2:
                    return "Need at least 2 snapshots to compare"
                
                snap1 = self.snapshots[idx1]
                snap2 = self.snapshots[idx2]
                
                return {
                    'memory_diff_mb': (snap2['total_memory'] - snap1['total_memory']) / 1024 / 1024,
                    'time_diff': snap2['timestamp'] - snap1['timestamp'],
                    'snap1_label': snap1['label'],
                    'snap2_label': snap2['label']
                }
            
            def stop(self):
                tracemalloc.stop()
        
        return MemoryTracker()


# Debug utilities for TauTranslator specific debugging
class TauTranslatorDebugger(AdvancedDebugger):
    """Specialized debugger for TauTranslator components."""
    
    def debug_translation(self, input_text: str, expected_output: str = None):
        """Debug translation process step by step."""
        from production_translator import ProductionTranslator
        
        with self.debug_context("translation_debug"):
            translator = ProductionTranslator()
            
            # Step 1: Input validation
            self.logger.debug(f"Input: {input_text}")
            self.breakpoint_if(not input_text.strip(), "Empty input detected")
            
            # Step 2: Translation
            result = translator.translate(input_text, "tau_to_tce")
            self.logger.debug(f"Translation result: {result}")
            
            # Step 3: Validation
            if expected_output:
                if result.get("output") != expected_output:
                    self.logger.warning(f"Expected: {expected_output}")
                    self.logger.warning(f"Got: {result.get('output')}")
                    self.breakpoint_if(True, "Output mismatch detected")
            
            return result
    
    def debug_requirements_parsing(self, requirements_text: str):
        """Debug requirements parsing process."""
        from nlp_requirements_engine import NLPRequirementsEngine
        
        with self.debug_context("requirements_parsing"):
            engine = NLPRequirementsEngine(use_spacy=False, use_transformers=False)
            
            # Step by step parsing
            self.logger.debug("Starting requirements extraction...")
            requirements = engine.extract_requirements(requirements_text)
            
            for i, req in enumerate(requirements):
                self.logger.debug(f"Requirement {i+1}: {req.text}")
                self.logger.debug(f"  Type: {req.type}")
                self.logger.debug(f"  Confidence: {req.confidence}")
                self.logger.debug(f"  Entities: {req.entities}")
            
            return requirements


# Create global debugger instance
debugger = TauTranslatorDebugger()

# Convenience decorators
trace = debugger.trace_function
monitor_performance = debugger.monitor_performance
debug_context = debugger.debug_context

def main():
    """Demonstrate debugging utilities."""
    print("🐛 TauTranslator Debug Utilities")
    print("=" * 50)
    
    # Example usage
    @trace(detailed=True)
    @monitor_performance
    def example_function(x: int, y: int) -> int:
        time.sleep(0.1)  # Simulate work
        return x + y
    
    # Test the debugging
    result = example_function(5, 3)
    print(f"Result: {result}")
    
    # Dump traces
    debugger.dump_traces()
    
    # Interactive inspection
    inspector = InteractiveDebugger()
    inspection = inspector.inspect_object(debugger)
    print(f"\nDebugger inspection: {json.dumps(inspection, indent=2)[:200]}...")
    
    print("\n🔧 Available Debug Tools:")
    print("  - @trace: Function call tracing")
    print("  - @monitor_performance: Performance monitoring")
    print("  - debug_context(): Context debugging")
    print("  - debugger.debug_translation(): Translation debugging")
    print("  - InteractiveDebugger.inspect_object(): Object inspection")


if __name__ == "__main__":
    main()