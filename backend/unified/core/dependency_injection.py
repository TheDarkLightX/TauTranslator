"""
Dependency Injection Container

Implements a comprehensive dependency injection system with lifecycle management,
circular dependency detection, and configuration binding.

Author: DarkLightX / Dana Edwards
"""

import threading
import inspect
import logging
from typing import (
    Dict, List, Type, TypeVar, Callable, Any, Optional, 
    Generic, Union, get_type_hints, get_origin, get_args
)
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


T = TypeVar('T')
logger = logging.getLogger(__name__)


class ServiceLifetime(Enum):
    """Service lifetime management options."""
    SINGLETON = "singleton"      # Single instance for entire application
    TRANSIENT = "transient"      # New instance for each request
    SCOPED = "scoped"           # Single instance per scope/request
    FACTORY = "factory"          # Custom factory function


class ServiceState(Enum):
    """Service registration state."""
    REGISTERED = "registered"
    CREATING = "creating"
    CREATED = "created"
    ERROR = "error"


@dataclass
class ServiceDescriptor:
    """Describes a registered service."""
    service_type: Type
    implementation_type: Optional[Type] = None
    instance: Optional[Any] = None
    factory: Optional[Callable] = None
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    configuration: Optional[Dict[str, Any]] = None
    dependencies: List[Type] = field(default_factory=list)
    state: ServiceState = ServiceState.REGISTERED
    creation_count: int = 0
    
    @property
    def identifier(self) -> str:
        """Get unique identifier for this service."""
        return f"{self.service_type.__module__}.{self.service_type.__name__}"


class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected."""
    
    def __init__(self, dependency_chain: List[Type]):
        self.dependency_chain = dependency_chain
        chain_str = " -> ".join(t.__name__ for t in dependency_chain)
        super().__init__(f"Circular dependency detected: {chain_str}")


class ServiceNotRegisteredError(Exception):
    """Raised when attempting to resolve unregistered service."""
    
    def __init__(self, service_type: Type):
        self.service_type = service_type
        super().__init__(f"Service not registered: {service_type.__name__}")


class ServiceCreationError(Exception):
    """Raised when service creation fails."""
    
    def __init__(self, service_type: Type, original_error: Exception):
        self.service_type = service_type
        self.original_error = original_error
        super().__init__(f"Failed to create service {service_type.__name__}: {original_error}")


class IServiceScope(ABC):
    """Interface for service scopes."""
    
    @abstractmethod
    def get_service(self, service_type: Type[T]) -> T:
        """Get service instance within this scope."""
        pass
    
    @abstractmethod
    def dispose(self) -> None:
        """Dispose of scoped services."""
        pass


class ServiceScope(IServiceScope):
    """Implementation of service scope."""
    
    def __init__(self, container: 'ServiceContainer'):
        self.container = container
        self.scoped_instances: Dict[Type, Any] = {}
        self._disposed = False
    
    def get_service(self, service_type: Type[T]) -> T:
        """Get service instance within this scope."""
        if self._disposed:
            raise RuntimeError("Cannot use disposed scope")
        
        # Check if we have a scoped instance
        if service_type in self.scoped_instances:
            return self.scoped_instances[service_type]
        
        # For scoped services, create directly here to avoid infinite recursion
        descriptor = self.container._get_descriptor(service_type)
        if descriptor and descriptor.lifetime == ServiceLifetime.SCOPED:
            # Create the instance directly
            instance = self.container._create_instance(descriptor)
            self.scoped_instances[service_type] = instance
            return instance
        
        # For non-scoped services, delegate to container
        return self.container.get_service(service_type, scope=self)
    
    def dispose(self) -> None:
        """Dispose of scoped services."""
        if self._disposed:
            return
        
        for instance in self.scoped_instances.values():
            if hasattr(instance, 'dispose'):
                try:
                    instance.dispose()
                except Exception as e:
                    logger.warning(f"Error disposing service: {e}")
        
        self.scoped_instances.clear()
        self._disposed = True


class ServiceContainer:
    """
    Dependency injection container with comprehensive features.
    
    Features:
    - Multiple lifetime management (singleton, transient, scoped, factory)
    - Circular dependency detection
    - Auto-wiring based on type annotations
    - Configuration binding
    - Service scoping
    - Thread-safe operations
    """
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._lock = threading.RLock()
        self._creation_stack: List[Type] = []
        
        # Register self
        self.register_instance(ServiceContainer, self)
    
    def register_singleton(self, service_type: Type[T], implementation_type: Optional[Type[T]] = None) -> 'ServiceContainer':
        """Register a service as singleton."""
        return self.register(service_type, implementation_type, ServiceLifetime.SINGLETON)
    
    def register_transient(self, service_type: Type[T], implementation_type: Optional[Type[T]] = None) -> 'ServiceContainer':
        """Register a service as transient."""
        return self.register(service_type, implementation_type, ServiceLifetime.TRANSIENT)
    
    def register_scoped(self, service_type: Type[T], implementation_type: Optional[Type[T]] = None) -> 'ServiceContainer':
        """Register a service as scoped."""
        return self.register(service_type, implementation_type, ServiceLifetime.SCOPED)
    
    def register(
        self, 
        service_type: Type[T], 
        implementation_type: Optional[Type[T]] = None, 
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        configuration: Optional[Dict[str, Any]] = None
    ) -> 'ServiceContainer':
        """
        Register a service with the container.
        
        Args:
            service_type: The service interface/type
            implementation_type: The concrete implementation (defaults to service_type)
            lifetime: Service lifetime management
            configuration: Optional configuration for the service
        """
        with self._lock:
            impl_type = implementation_type or service_type
            
            # Analyze dependencies
            dependencies = self._analyze_dependencies(impl_type)
            
            descriptor = ServiceDescriptor(
                service_type=service_type,
                implementation_type=impl_type,
                lifetime=lifetime,
                configuration=configuration or {},
                dependencies=dependencies
            )
            
            self._services[service_type] = descriptor
            logger.debug(f"Registered service: {service_type.__name__} -> {impl_type.__name__} ({lifetime.value})")
            
            return self
    
    def register_instance(self, service_type: Type[T], instance: T) -> 'ServiceContainer':
        """Register a specific instance as singleton."""
        with self._lock:
            descriptor = ServiceDescriptor(
                service_type=service_type,
                instance=instance,
                lifetime=ServiceLifetime.SINGLETON,
                state=ServiceState.CREATED
            )
            
            self._services[service_type] = descriptor
            self._singletons[service_type] = instance
            logger.debug(f"Registered instance: {service_type.__name__}")
            
            return self
    
    def register_factory(
        self, 
        service_type: Type[T], 
        factory: Callable[['ServiceContainer'], T],
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    ) -> 'ServiceContainer':
        """Register a factory function for creating services."""
        with self._lock:
            descriptor = ServiceDescriptor(
                service_type=service_type,
                factory=factory,
                lifetime=lifetime
            )
            
            self._services[service_type] = descriptor
            logger.debug(f"Registered factory: {service_type.__name__} ({lifetime.value})")
            
            return self
    
    def get_service(self, service_type: Type[T], scope: Optional[ServiceScope] = None) -> T:
        """
        Resolve and return a service instance.
        
        Args:
            service_type: The service type to resolve
            scope: Optional service scope for scoped services
        """
        with self._lock:
            return self._resolve_service(service_type, scope)
    
    def get_services(self, service_type: Type[T]) -> List[T]:
        """Get all registered implementations of a service type."""
        # For now, return single service - could be extended for multiple implementations
        try:
            service = self.get_service(service_type)
            return [service] if service else []
        except ServiceNotRegisteredError:
            return []
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered."""
        return service_type in self._services
    
    def create_scope(self) -> ServiceScope:
        """Create a new service scope."""
        return ServiceScope(self)
    
    def get_service_info(self, service_type: Optional[Type] = None) -> Dict[str, Any]:
        """Get information about registered services."""
        with self._lock:
            if service_type:
                if service_type not in self._services:
                    return {}
                return self._descriptor_to_dict(self._services[service_type])
            
            return {
                service_type.__name__: self._descriptor_to_dict(descriptor)
                for service_type, descriptor in self._services.items()
            }
    
    def validate_registrations(self) -> List[str]:
        """Validate all service registrations and return any errors."""
        errors = []
        
        with self._lock:
            for service_type, descriptor in self._services.items():
                try:
                    # Check for circular dependencies
                    self._check_circular_dependencies(service_type, [])
                    
                    # Validate implementation can be created
                    if descriptor.implementation_type:
                        self._validate_implementation(descriptor.implementation_type)
                    
                except Exception as e:
                    errors.append(f"{service_type.__name__}: {str(e)}")
        
        return errors
    
    def _resolve_service(self, service_type: Type[T], scope: Optional[ServiceScope] = None) -> T:
        """Internal service resolution with circular dependency detection."""
        # Check for circular dependencies
        if service_type in self._creation_stack:
            self._creation_stack.append(service_type)
            raise CircularDependencyError(self._creation_stack.copy())
        
        # Check if service is registered
        if service_type not in self._services:
            raise ServiceNotRegisteredError(service_type)
        
        descriptor = self._services[service_type]
        
        try:
            # Handle different lifetime scenarios
            if descriptor.lifetime == ServiceLifetime.SINGLETON:
                return self._get_singleton(descriptor)
            
            elif descriptor.lifetime == ServiceLifetime.SCOPED:
                if scope:
                    # Check if scope already has instance
                    if service_type in scope.scoped_instances:
                        return scope.scoped_instances[service_type]
                    # Create and store in scope
                    instance = self._create_instance(descriptor)
                    scope.scoped_instances[service_type] = instance
                    return instance
                # Fall back to singleton behavior if no scope
                return self._get_singleton(descriptor)
            
            elif descriptor.lifetime == ServiceLifetime.TRANSIENT:
                return self._create_instance(descriptor)
            
            elif descriptor.lifetime == ServiceLifetime.FACTORY:
                return self._create_from_factory(descriptor)
            
            else:
                raise ServiceCreationError(service_type, ValueError(f"Unknown lifetime: {descriptor.lifetime}"))
        
        except Exception as e:
            if not isinstance(e, (CircularDependencyError, ServiceNotRegisteredError, ServiceCreationError)):
                raise ServiceCreationError(service_type, e)
            raise
    
    def _get_singleton(self, descriptor: ServiceDescriptor) -> Any:
        """Get or create singleton instance."""
        if descriptor.service_type in self._singletons:
            return self._singletons[descriptor.service_type]
        
        instance = self._create_instance(descriptor)
        self._singletons[descriptor.service_type] = instance
        return instance
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create new instance of service."""
        if descriptor.instance:
            return descriptor.instance
        
        if descriptor.factory:
            return self._create_from_factory(descriptor)
        
        if not descriptor.implementation_type:
            raise ServiceCreationError(
                descriptor.service_type, 
                ValueError("No implementation type or factory provided")
            )
        
        # Add to creation stack for circular dependency detection
        self._creation_stack.append(descriptor.service_type)
        
        try:
            # Resolve dependencies
            constructor_args = self._resolve_dependencies(descriptor.implementation_type)
            
            # Apply configuration if available
            if descriptor.configuration:
                constructor_args.update(descriptor.configuration)
            
            # Create instance
            instance = descriptor.implementation_type(**constructor_args)
            
            # Update descriptor state
            descriptor.state = ServiceState.CREATED
            descriptor.creation_count += 1
            
            return instance
        
        finally:
            # Remove from creation stack
            if self._creation_stack and self._creation_stack[-1] == descriptor.service_type:
                self._creation_stack.pop()
    
    def _create_from_factory(self, descriptor: ServiceDescriptor) -> Any:
        """Create instance using factory function."""
        if not descriptor.factory:
            raise ServiceCreationError(descriptor.service_type, ValueError("No factory function provided"))
        
        try:
            return descriptor.factory(self)
        except Exception as e:
            raise ServiceCreationError(descriptor.service_type, e)
    
    def _resolve_dependencies(self, implementation_type: Type) -> Dict[str, Any]:
        """Resolve constructor dependencies for a type."""
        constructor_args = {}
        
        # Get constructor signature
        try:
            sig = inspect.signature(implementation_type.__init__)
            # Try to get type hints, handling forward references
            try:
                type_hints = get_type_hints(implementation_type.__init__)
            except NameError:
                # Forward references - for now, skip resolution
                type_hints = {}
        except (ValueError, TypeError):
            return constructor_args
        
        # Resolve each parameter
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Get parameter type from type hints
            param_type = type_hints.get(param_name)
            if not param_type:
                # Skip parameters without type hints
                continue
            
            # Handle Optional types
            if get_origin(param_type) is Union:
                args = get_args(param_type)
                if len(args) == 2 and type(None) in args:
                    param_type = args[0] if args[1] is type(None) else args[1]
                    # Optional parameter - skip if not registered
                    if not self.is_registered(param_type):
                        continue
            
            # Resolve dependency
            if self.is_registered(param_type):
                constructor_args[param_name] = self._resolve_service(param_type)
        
        return constructor_args
    
    def _analyze_dependencies(self, implementation_type: Type) -> List[Type]:
        """Analyze dependencies of an implementation type."""
        dependencies = []
        
        try:
            sig = inspect.signature(implementation_type.__init__)
            # Try to get type hints, but handle forward references gracefully
            try:
                type_hints = get_type_hints(implementation_type.__init__)
            except NameError:
                # Forward references not resolvable, use annotations directly
                type_hints = {}
                if hasattr(implementation_type.__init__, '__annotations__'):
                    type_hints = implementation_type.__init__.__annotations__
        except (ValueError, TypeError):
            return dependencies
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            param_type = type_hints.get(param_name)
            if param_type and not self._is_primitive_type(param_type):
                dependencies.append(param_type)
        
        return dependencies
    
    def _check_circular_dependencies(self, service_type: Type, visited: List[Type]) -> None:
        """Check for circular dependencies in service graph."""
        if service_type in visited:
            visited.append(service_type)
            raise CircularDependencyError(visited)
        
        if service_type not in self._services:
            return
        
        descriptor = self._services[service_type]
        new_visited = visited + [service_type]
        
        for dependency in descriptor.dependencies:
            self._check_circular_dependencies(dependency, new_visited)
    
    def _validate_implementation(self, implementation_type: Type) -> None:
        """Validate that implementation can be instantiated."""
        try:
            sig = inspect.signature(implementation_type.__init__)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Cannot inspect constructor: {e}")
        
        # Check for unresolvable dependencies
        type_hints = get_type_hints(implementation_type.__init__)
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            if param.default == inspect.Parameter.empty:
                param_type = type_hints.get(param_name)
                if param_type and not self._is_primitive_type(param_type) and not self.is_registered(param_type):
                    raise ValueError(f"Unresolvable dependency: {param_type}")
    
    def _is_primitive_type(self, type_obj: Type) -> bool:
        """Check if type is a primitive type."""
        # Handle string annotations (forward references)
        if isinstance(type_obj, str):
            return False  # String annotations are not primitives
            
        primitive_types = {int, float, str, bool, bytes, type(None)}
        return type_obj in primitive_types or (hasattr(type_obj, '__module__') and type_obj.__module__ == 'builtins')
    
    def _get_descriptor(self, service_type: Type) -> Optional[ServiceDescriptor]:
        """Get service descriptor for type."""
        return self._services.get(service_type)
    
    def _get_type_name(self, type_hint: Type) -> str:
        """Get string representation of type hint."""
        if hasattr(type_hint, '__name__'):
            return type_hint.__name__
        else:
            # Handle Optional, Union, etc.
            return str(type_hint)
    
    def _descriptor_to_dict(self, descriptor: ServiceDescriptor) -> Dict[str, Any]:
        """Convert ServiceDescriptor to dictionary."""
        return {
            'service_type': descriptor.service_type.__name__,
            'implementation_type': descriptor.implementation_type.__name__ if descriptor.implementation_type else None,
            'lifetime': descriptor.lifetime.value,
            'state': descriptor.state.value,
            'creation_count': descriptor.creation_count,
            'has_instance': descriptor.instance is not None,
            'has_factory': descriptor.factory is not None,
            'dependencies': [self._get_type_name(dep) for dep in descriptor.dependencies]
        }


# Global container instance
_global_container = ServiceContainer()


def get_container() -> ServiceContainer:
    """Get the global service container."""
    return _global_container


def configure_services(config_func: Callable[[ServiceContainer], None]) -> None:
    """Configure services using a configuration function."""
    config_func(_global_container)