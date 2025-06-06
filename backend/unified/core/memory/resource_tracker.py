"""
Resource Tracking and Memory Analytics

Provides detailed resource tracking and analytics for memory optimization.
Tracks object lifecycles, memory allocations, and performance patterns.

Author: DarkLightX / Dana Edwards
"""

import gc
import logging
import threading
import time
import tracemalloc
import weakref
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import psutil
import os


class ResourceType(Enum):
    """Types of tracked resources."""
    MEMORY = "memory"
    FILE_HANDLE = "file_handle"
    NETWORK_SOCKET = "network_socket"
    THREAD = "thread"
    DATABASE_CONNECTION = "database_connection"
    TRANSLATION_CONTEXT = "translation_context"
    PATTERN_MATCHER = "pattern_matcher"
    CACHE_ENTRY = "cache_entry"


class AllocationEvent(Enum):
    """Resource allocation events."""
    ALLOCATED = "allocated"
    DEALLOCATED = "deallocated"
    LEAKED = "leaked"
    REUSED = "reused"


@dataclass
class ResourceInfo:
    """Information about a tracked resource."""
    resource_id: str
    resource_type: ResourceType
    size: int  # bytes
    created_at: float
    location: str  # where it was created
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_accessed: Optional[float] = None
    access_count: int = 0
    
    @property
    def age(self) -> float:
        """Get resource age in seconds."""
        return time.time() - self.created_at
    
    @property
    def size_mb(self) -> float:
        """Get size in MB."""
        return self.size / (1024 * 1024)


@dataclass
class AllocationRecord:
    """Record of resource allocation/deallocation."""
    timestamp: float
    event: AllocationEvent
    resource_info: ResourceInfo
    stack_trace: Optional[str] = None


@dataclass
class MemorySnapshot:
    """Memory state snapshot."""
    timestamp: float
    total_memory: int
    process_memory: int
    tracked_resources: int
    resource_breakdown: Dict[ResourceType, int]
    large_objects: List[ResourceInfo]  # Objects > 1MB
    gc_stats: Dict[int, int]
    
    @property
    def total_tracked_size(self) -> int:
        """Total size of tracked resources."""
        return sum(self.resource_breakdown.values())


class ResourceTracker:
    """
    Tracks resource allocation and usage patterns.
    
    Features:
    - Resource lifecycle tracking
    - Memory leak detection
    - Allocation pattern analysis
    - Performance hotspot identification
    - Automatic cleanup suggestions
    """
    
    def __init__(self, enable_tracemalloc: bool = True):
        self.active_resources: Dict[str, ResourceInfo] = {}
        self.allocation_history: deque[AllocationRecord] = deque(maxlen=10000)
        self.snapshots: List[MemorySnapshot] = []
        
        # Configuration
        self.enable_tracemalloc = enable_tracemalloc
        self.large_object_threshold = 1024 * 1024  # 1MB
        self.leak_detection_enabled = True
        self.max_snapshots = 100
        
        # Statistics
        self.stats = {
            'total_allocations': 0,
            'total_deallocations': 0,
            'peak_memory': 0,
            'leak_count': 0,
            'reuse_count': 0
        }
        
        # Weak references for automatic cleanup detection
        self.weak_refs: Dict[str, weakref.ref] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize tracemalloc if enabled
        if self.enable_tracemalloc and not tracemalloc.is_tracing():
            tracemalloc.start()
        
        self.logger = logging.getLogger(__name__)
    
    def track_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        size: int,
        obj: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track a new resource allocation."""
        with self._lock:
            # Get stack trace for allocation location
            location = self._get_allocation_location()
            
            resource_info = ResourceInfo(
                resource_id=resource_id,
                resource_type=resource_type,
                size=size,
                created_at=time.time(),
                location=location,
                metadata=metadata or {}
            )
            
            self.active_resources[resource_id] = resource_info
            
            # Create weak reference if object provided
            if obj is not None:
                self.weak_refs[resource_id] = weakref.ref(
                    obj, 
                    lambda ref: self._handle_weak_ref_callback(resource_id)
                )
            
            # Record allocation event
            self._record_event(AllocationEvent.ALLOCATED, resource_info)
            
            # Update statistics
            self.stats['total_allocations'] += 1
            current_memory = self._get_current_memory_usage()
            if current_memory > self.stats['peak_memory']:
                self.stats['peak_memory'] = current_memory
            
            self.logger.debug(f"Tracked resource {resource_id} ({resource_type.value}, {size} bytes)")
    
    def untrack_resource(self, resource_id: str, reused: bool = False) -> bool:
        """Untrack a resource (deallocation)."""
        with self._lock:
            if resource_id not in self.active_resources:
                return False
            
            resource_info = self.active_resources.pop(resource_id)
            
            # Remove weak reference
            self.weak_refs.pop(resource_id, None)
            
            # Record deallocation event
            event = AllocationEvent.REUSED if reused else AllocationEvent.DEALLOCATED
            self._record_event(event, resource_info)
            
            # Update statistics
            if reused:
                self.stats['reuse_count'] += 1
            else:
                self.stats['total_deallocations'] += 1
            
            self.logger.debug(f"Untracked resource {resource_id}")
            return True
    
    def access_resource(self, resource_id: str) -> bool:
        """Record resource access."""
        with self._lock:
            if resource_id in self.active_resources:
                resource_info = self.active_resources[resource_id]
                resource_info.last_accessed = time.time()
                resource_info.access_count += 1
                return True
            return False
    
    def take_snapshot(self) -> MemorySnapshot:
        """Take a memory snapshot."""
        with self._lock:
            # System memory info
            memory = psutil.virtual_memory()
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info().rss
            
            # Resource breakdown
            breakdown = defaultdict(int)
            large_objects = []
            
            for resource_info in self.active_resources.values():
                breakdown[resource_info.resource_type] += resource_info.size
                
                if resource_info.size >= self.large_object_threshold:
                    large_objects.append(resource_info)
            
            # Sort large objects by size
            large_objects.sort(key=lambda r: r.size, reverse=True)
            
            # GC statistics
            gc_stats = {}
            for i in range(3):
                gc_stats[i] = gc.get_count()[i]
            
            snapshot = MemorySnapshot(
                timestamp=time.time(),
                total_memory=memory.total,
                process_memory=process_memory,
                tracked_resources=len(self.active_resources),
                resource_breakdown=dict(breakdown),
                large_objects=large_objects[:10],  # Top 10 largest
                gc_stats=gc_stats
            )
            
            self.snapshots.append(snapshot)
            
            # Limit snapshot history
            if len(self.snapshots) > self.max_snapshots:
                self.snapshots.pop(0)
            
            return snapshot
    
    def detect_leaks(self, age_threshold: float = 3600.0) -> List[ResourceInfo]:
        """Detect potential memory leaks."""
        if not self.leak_detection_enabled:
            return []
        
        current_time = time.time()
        potential_leaks = []
        
        with self._lock:
            for resource_info in self.active_resources.values():
                # Consider resources as potential leaks if they're old and rarely accessed
                if (resource_info.age > age_threshold and 
                    resource_info.access_count == 0):
                    potential_leaks.append(resource_info)
                    
                    # Record as leak
                    self._record_event(AllocationEvent.LEAKED, resource_info)
        
        if potential_leaks:
            self.stats['leak_count'] += len(potential_leaks)
            self.logger.warning(f"Detected {len(potential_leaks)} potential memory leaks")
        
        return potential_leaks
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get resource tracking statistics."""
        with self._lock:
            current_snapshot = self.take_snapshot()
            
            return {
                'active_resources': len(self.active_resources),
                'total_allocations': self.stats['total_allocations'],
                'total_deallocations': self.stats['total_deallocations'],
                'reuse_count': self.stats['reuse_count'],
                'leak_count': self.stats['leak_count'],
                'peak_memory': self.stats['peak_memory'],
                'current_memory': current_snapshot.process_memory,
                'tracked_memory': current_snapshot.total_tracked_size,
                'resource_breakdown': current_snapshot.resource_breakdown,
                'large_objects_count': len(current_snapshot.large_objects)
            }
    
    def get_allocation_patterns(self) -> Dict[str, Any]:
        """Analyze allocation patterns."""
        with self._lock:
            patterns = {
                'allocation_rate': 0.0,
                'deallocation_rate': 0.0,
                'peak_allocation_time': None,
                'resource_type_distribution': defaultdict(int),
                'allocation_locations': defaultdict(int)
            }
            
            if len(self.allocation_history) < 2:
                return patterns
            
            # Calculate rates
            time_span = self.allocation_history[-1].timestamp - self.allocation_history[0].timestamp
            if time_span > 0:
                allocations = sum(1 for record in self.allocation_history 
                                if record.event == AllocationEvent.ALLOCATED)
                deallocations = sum(1 for record in self.allocation_history 
                                  if record.event == AllocationEvent.DEALLOCATED)
                
                patterns['allocation_rate'] = allocations / time_span
                patterns['deallocation_rate'] = deallocations / time_span
            
            # Analyze distribution
            for record in self.allocation_history:
                if record.event == AllocationEvent.ALLOCATED:
                    patterns['resource_type_distribution'][record.resource_info.resource_type.value] += 1
                    patterns['allocation_locations'][record.resource_info.location] += 1
            
            return patterns
    
    def get_top_consumers(self, limit: int = 10) -> List[Tuple[str, ResourceInfo]]:
        """Get top memory consuming resources."""
        with self._lock:
            sorted_resources = sorted(
                self.active_resources.items(),
                key=lambda item: item[1].size,
                reverse=True
            )
            return sorted_resources[:limit]
    
    def cleanup_suggestions(self) -> List[str]:
        """Generate cleanup suggestions based on analysis."""
        suggestions = []
        
        # Detect potential leaks
        leaks = self.detect_leaks()
        if leaks:
            suggestions.append(f"Found {len(leaks)} potential memory leaks - consider cleanup")
        
        # Check for large objects
        large_objects = [r for r in self.active_resources.values() 
                        if r.size >= self.large_object_threshold]
        if large_objects:
            suggestions.append(f"Found {len(large_objects)} large objects (>1MB) - review necessity")
        
        # Check allocation/deallocation balance
        if self.stats['total_allocations'] > self.stats['total_deallocations'] * 2:
            suggestions.append("High allocation to deallocation ratio - check for proper cleanup")
        
        # Check for unused resources
        unused_resources = [r for r in self.active_resources.values() 
                           if r.access_count == 0 and r.age > 300]  # 5 minutes
        if unused_resources:
            suggestions.append(f"Found {len(unused_resources)} unused resources - consider cleanup")
        
        return suggestions
    
    def export_snapshot_data(self, filename: str) -> None:
        """Export snapshot data for analysis."""
        import json
        
        export_data = {
            'snapshots': [
                {
                    'timestamp': s.timestamp,
                    'process_memory_mb': s.process_memory / (1024 * 1024),
                    'tracked_resources': s.tracked_resources,
                    'resource_breakdown': {k.value: v for k, v in s.resource_breakdown.items()},
                    'large_objects_count': len(s.large_objects)
                }
                for s in self.snapshots
            ],
            'stats': self.get_resource_stats(),
            'patterns': self.get_allocation_patterns(),
            'suggestions': self.cleanup_suggestions()
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Exported snapshot data to {filename}")
    
    def _record_event(self, event: AllocationEvent, resource_info: ResourceInfo) -> None:
        """Record allocation/deallocation event."""
        stack_trace = None
        if event in [AllocationEvent.ALLOCATED, AllocationEvent.LEAKED]:
            stack_trace = self._get_stack_trace()
        
        record = AllocationRecord(
            timestamp=time.time(),
            event=event,
            resource_info=resource_info,
            stack_trace=stack_trace
        )
        
        self.allocation_history.append(record)
    
    def _get_allocation_location(self) -> str:
        """Get allocation location from stack trace."""
        try:
            import inspect
            frame = inspect.currentframe()
            # Go up the stack to find the caller
            for _ in range(3):
                frame = frame.f_back
                if frame is None:
                    break
            
            if frame:
                return f"{frame.f_code.co_filename}:{frame.f_lineno}"
            else:
                return "unknown"
        except Exception:
            return "unknown"
    
    def _get_stack_trace(self) -> str:
        """Get current stack trace."""
        try:
            import traceback
            return ''.join(traceback.format_stack())
        except Exception:
            return "unavailable"
    
    def _get_current_memory_usage(self) -> int:
        """Get current process memory usage."""
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss
        except Exception:
            return 0
    
    def _handle_weak_ref_callback(self, resource_id: str) -> None:
        """Handle weak reference callback (object was garbage collected)."""
        # Automatically untrack resource when object is garbage collected
        self.untrack_resource(resource_id)


class ResourceContext:
    """
    Context manager for automatic resource tracking.
    
    Example:
        with ResourceContext(tracker, "my_resource", ResourceType.MEMORY, 1024):
            # Resource is automatically tracked
            pass
        # Resource is automatically untracked
    """
    
    def __init__(
        self,
        tracker: ResourceTracker,
        resource_id: str,
        resource_type: ResourceType,
        size: int,
        obj: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.tracker = tracker
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.size = size
        self.obj = obj
        self.metadata = metadata
    
    def __enter__(self) -> str:
        self.tracker.track_resource(
            self.resource_id,
            self.resource_type,
            self.size,
            self.obj,
            self.metadata
        )
        return self.resource_id
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.tracker.untrack_resource(self.resource_id)


# Global resource tracker
_global_resource_tracker = ResourceTracker()


def get_resource_tracker() -> ResourceTracker:
    """Get the global resource tracker."""
    return _global_resource_tracker


def track_resource(
    resource_id: str,
    resource_type: ResourceType,
    size: int,
    obj: Optional[Any] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Track a resource using the global tracker."""
    _global_resource_tracker.track_resource(resource_id, resource_type, size, obj, metadata)


def untrack_resource(resource_id: str, reused: bool = False) -> bool:
    """Untrack a resource using the global tracker."""
    return _global_resource_tracker.untrack_resource(resource_id, reused)


def resource_context(
    resource_id: str,
    resource_type: ResourceType,
    size: int,
    obj: Optional[Any] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> ResourceContext:
    """Create a resource context using the global tracker."""
    return ResourceContext(_global_resource_tracker, resource_id, resource_type, size, obj, metadata)