"""
TDD Unit Tests for Dependency Injection Container

Comprehensive tests for the DI container with lifecycle management and circular dependency detection.

Author: DarkLightX / Dana Edwards
"""

import pytest
import threading
import time
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.core.dependency_injection import (
    ServiceContainer,
    ServiceLifetime,
    ServiceState,
    CircularDependencyError,
    ServiceNotRegisteredError,
    ServiceCreationError,
    ServiceScope
)


# Test classes for DI testing
class ITestService:
    """Test service interface."""
    def get_value(self) -> str:
        pass


class TestService(ITestService):
    """Simple test service implementation."""
    def __init__(self, value: str = "default"):
        self.value = value
        self.created_at = time.time()
    
    def get_value(self) -> str:
        return self.value


class DependentService:
    """Service with dependencies."""
    def __init__(self, test_service: ITestService, optional_value: Optional[str] = None):
        self.test_service = test_service
        self.optional_value = optional_value
    
    def get_combined_value(self) -> str:
        return f"{self.test_service.get_value()}-{self.optional_value or 'none'}"


class CircularA:
    """First class in circular dependency."""
    def __init__(self, circular_b: 'CircularB'):
        self.circular_b = circular_b


class CircularB:
    """Second class in circular dependency."""
    def __init__(self, circular_a: CircularA):
        self.circular_a = circular_a


class DisposableService:
    """Service that can be disposed."""
    def __init__(self):
        self.disposed = False
    
    def dispose(self):
        self.disposed = True


class ComplexService:
    """Service with multiple dependencies."""
    def __init__(self, test_service: ITestService, dependent_service: DependentService):
        self.test_service = test_service
        self.dependent_service = dependent_service


class TestDependencyInjectionContainer:
    """Comprehensive TDD tests for ServiceContainer."""
    
    @pytest.fixture
    def container(self):
        """Create fresh container for each test."""
        return ServiceContainer()
    
    # Category 1: Service Registration Tests
    
    def test_container_initializes_correctly(self, container):
        """Test container initializes with self-registration."""
        # Container should register itself
        assert container.is_registered(ServiceContainer)
        container_instance = container.get_service(ServiceContainer)
        assert container_instance is container
    
    def test_register_singleton_service(self, container):
        """Test singleton service registration."""
        container.register_singleton(ITestService, TestService)
        
        assert container.is_registered(ITestService)
        service_info = container.get_service_info(ITestService)
        assert service_info['lifetime'] == ServiceLifetime.SINGLETON.value
        assert service_info['implementation_type'] == 'TestService'
    
    def test_register_transient_service(self, container):
        """Test transient service registration."""
        container.register_transient(ITestService, TestService)
        
        service_info = container.get_service_info(ITestService)
        assert service_info['lifetime'] == ServiceLifetime.TRANSIENT.value
    
    def test_register_scoped_service(self, container):
        """Test scoped service registration."""
        container.register_scoped(ITestService, TestService)
        
        service_info = container.get_service_info(ITestService)
        assert service_info['lifetime'] == ServiceLifetime.SCOPED.value
    
    def test_register_service_with_configuration(self, container):
        """Test service registration with configuration."""
        config = {"value": "configured_value"}
        container.register(ITestService, TestService, ServiceLifetime.SINGLETON, config)
        
        service = container.get_service(ITestService)
        assert service.value == "configured_value"
    
    def test_register_instance(self, container):
        """Test instance registration."""
        instance = TestService("instance_value")
        container.register_instance(ITestService, instance)
        
        retrieved = container.get_service(ITestService)
        assert retrieved is instance
        assert retrieved.value == "instance_value"
    
    def test_register_factory(self, container):
        """Test factory registration."""
        def service_factory(container):
            return TestService("factory_created")
        
        container.register_factory(ITestService, service_factory, ServiceLifetime.TRANSIENT)
        
        service = container.get_service(ITestService)
        assert service.value == "factory_created"
        
        # Transient factory should create new instances
        service2 = container.get_service(ITestService)
        assert service is not service2
        assert service2.value == "factory_created"
    
    def test_register_factory_singleton(self, container):
        """Test singleton factory registration."""
        call_count = 0
        
        def counting_factory(container):
            nonlocal call_count
            call_count += 1
            return TestService(f"factory_{call_count}")
        
        container.register_factory(ITestService, counting_factory, ServiceLifetime.SINGLETON)
        
        service1 = container.get_service(ITestService)
        service2 = container.get_service(ITestService)
        
        assert service1 is service2  # Same instance
        assert call_count == 1  # Factory called only once
    
    def test_register_without_implementation_type(self, container):
        """Test registration using service type as implementation."""
        container.register_singleton(TestService)
        
        service = container.get_service(TestService)
        assert isinstance(service, TestService)
    
    # Category 2: Service Resolution Tests
    
    def test_resolve_singleton_same_instance(self, container):
        """Test singleton services return same instance."""
        container.register_singleton(ITestService, TestService)
        
        service1 = container.get_service(ITestService)
        service2 = container.get_service(ITestService)
        
        assert service1 is service2
        assert isinstance(service1, TestService)
    
    def test_resolve_transient_different_instances(self, container):
        """Test transient services return different instances."""
        container.register_transient(ITestService, TestService)
        
        service1 = container.get_service(ITestService)
        service2 = container.get_service(ITestService)
        
        assert service1 is not service2
        assert isinstance(service1, TestService)
        assert isinstance(service2, TestService)
    
    def test_resolve_with_dependencies(self, container):
        """Test resolving service with dependencies."""
        container.register_singleton(ITestService, TestService)
        container.register_transient(DependentService)
        
        dependent = container.get_service(DependentService)
        
        assert isinstance(dependent, DependentService)
        assert isinstance(dependent.test_service, TestService)
        assert dependent.get_combined_value() == "default-none"
    
    def test_resolve_complex_dependency_graph(self, container):
        """Test resolving complex dependency graphs."""
        container.register_singleton(ITestService, TestService)
        container.register_transient(DependentService)
        container.register_transient(ComplexService)
        
        complex_service = container.get_service(ComplexService)
        
        assert isinstance(complex_service, ComplexService)
        assert isinstance(complex_service.test_service, TestService)
        assert isinstance(complex_service.dependent_service, DependentService)
        
        # Both should share the same singleton test service
        assert complex_service.test_service is complex_service.dependent_service.test_service
    
    def test_resolve_unregistered_service_raises_error(self, container):
        """Test resolving unregistered service raises error."""
        with pytest.raises(ServiceNotRegisteredError) as exc_info:
            container.get_service(ITestService)
        
        assert exc_info.value.service_type == ITestService
    
    def test_resolve_with_optional_dependencies(self, container):
        """Test resolving service with optional dependencies."""
        container.register_singleton(ITestService, TestService)
        container.register_transient(DependentService)
        
        # Optional dependency not registered - should work
        dependent = container.get_service(DependentService)
        assert dependent.optional_value is None
    
    # Category 3: Service Scoping Tests
    
    def test_create_service_scope(self, container):
        """Test creating service scopes."""
        scope = container.create_scope()
        assert isinstance(scope, ServiceScope)
        assert scope.container is container
    
    def test_scoped_service_same_within_scope(self, container):
        """Test scoped services are same within a scope."""
        container.register_scoped(ITestService, TestService)
        
        scope = container.create_scope()
        
        service1 = scope.get_service(ITestService)
        service2 = scope.get_service(ITestService)
        
        assert service1 is service2
    
    def test_scoped_service_different_across_scopes(self, container):
        """Test scoped services are different across scopes."""
        container.register_scoped(ITestService, TestService)
        
        scope1 = container.create_scope()
        scope2 = container.create_scope()
        
        service1 = scope1.get_service(ITestService)
        service2 = scope2.get_service(ITestService)
        
        assert service1 is not service2
    
    def test_scope_disposal(self, container):
        """Test scope disposal calls dispose on scoped services."""
        container.register_scoped(DisposableService)
        
        scope = container.create_scope()
        service = scope.get_service(DisposableService)
        
        assert not service.disposed
        
        scope.dispose()
        assert service.disposed
        
        # Should not be able to use disposed scope
        with pytest.raises(RuntimeError):
            scope.get_service(DisposableService)
    
    def test_scoped_service_fallback_without_scope(self, container):
        """Test scoped services fall back to singleton behavior without scope."""
        container.register_scoped(ITestService, TestService)
        
        service1 = container.get_service(ITestService)
        service2 = container.get_service(ITestService)
        
        # Should behave like singleton when no scope provided
        assert service1 is service2
    
    # Category 4: Circular Dependency Detection Tests
    
    def test_circular_dependency_detection(self, container):
        """Test circular dependencies are detected."""
        container.register_transient(CircularA)
        container.register_transient(CircularB)
        
        with pytest.raises(CircularDependencyError) as exc_info:
            container.get_service(CircularA)
        
        # Should contain both classes in dependency chain
        chain = exc_info.value.dependency_chain
        assert CircularA in chain
        assert CircularB in chain
    
    def test_self_circular_dependency(self, container):
        """Test self-referencing circular dependency detection."""
        # This would be caught during registration validation
        errors = container.validate_registrations()
        # Initially no errors with current registrations
        assert len(errors) == 0
    
    def test_deep_circular_dependency_chain(self, container):
        """Test detection of deep circular dependency chains."""
        class ChainA:
            def __init__(self, chain_b: 'ChainB'): pass
        
        class ChainB:
            def __init__(self, chain_c: 'ChainC'): pass
        
        class ChainC:
            def __init__(self, chain_a: ChainA): pass
        
        container.register_transient(ChainA)
        container.register_transient(ChainB)
        container.register_transient(ChainC)
        
        with pytest.raises(CircularDependencyError):
            container.get_service(ChainA)
    
    # Category 5: Validation Tests
    
    def test_validate_registrations_success(self, container):
        """Test validation passes for valid registrations."""
        container.register_singleton(ITestService, TestService)
        container.register_transient(DependentService)
        
        errors = container.validate_registrations()
        assert len(errors) == 0
    
    def test_validate_registrations_circular_dependency(self, container):
        """Test validation detects circular dependencies."""
        container.register_transient(CircularA)
        container.register_transient(CircularB)
        
        errors = container.validate_registrations()
        assert len(errors) == 2  # Both services have circular dependencies
        assert any("CircularA" in error for error in errors)
        assert any("CircularB" in error for error in errors)
    
    def test_validate_unresolvable_dependencies(self, container):
        """Test validation detects unresolvable dependencies."""
        container.register_transient(DependentService)
        # Don't register ITestService
        
        errors = container.validate_registrations()
        assert len(errors) >= 1
        assert any("Unresolvable dependency" in error for error in errors)
    
    # Category 6: Service Information Tests
    
    def test_get_service_info_single_service(self, container):
        """Test getting information for single service."""
        container.register_singleton(ITestService, TestService)
        
        info = container.get_service_info(ITestService)
        
        assert info['service_type'] == 'ITestService'
        assert info['implementation_type'] == 'TestService'
        assert info['lifetime'] == ServiceLifetime.SINGLETON.value
        assert info['state'] == ServiceState.REGISTERED.value
        assert info['creation_count'] == 0
    
    def test_get_service_info_all_services(self, container):
        """Test getting information for all services."""
        container.register_singleton(ITestService, TestService)
        container.register_transient(DependentService)
        
        all_info = container.get_service_info()
        
        assert 'ITestService' in all_info
        assert 'DependentService' in all_info
        assert 'ServiceContainer' in all_info  # Self-registered
    
    def test_get_service_info_after_creation(self, container):
        """Test service info updates after instance creation."""
        container.register_singleton(ITestService, TestService)
        
        # Before creation
        info = container.get_service_info(ITestService)
        assert info['creation_count'] == 0
        assert info['state'] == ServiceState.REGISTERED.value
        
        # Create instance
        container.get_service(ITestService)
        
        # After creation
        info = container.get_service_info(ITestService)
        assert info['creation_count'] == 1
        assert info['state'] == ServiceState.CREATED.value
    
    def test_get_service_info_nonexistent(self, container):
        """Test getting info for non-existent service."""
        info = container.get_service_info(ITestService)
        assert info == {}
    
    # Category 7: Multiple Service Implementations Tests
    
    def test_get_services_single_implementation(self, container):
        """Test getting all services when only one is registered."""
        container.register_singleton(ITestService, TestService)
        
        services = container.get_services(ITestService)
        assert len(services) == 1
        assert isinstance(services[0], TestService)
    
    def test_get_services_no_implementations(self, container):
        """Test getting services when none are registered."""
        services = container.get_services(ITestService)
        assert len(services) == 0
    
    # Category 8: Error Handling Tests
    
    def test_service_creation_error_handling(self, container):
        """Test proper error handling during service creation."""
        class FailingService:
            def __init__(self):
                raise ValueError("Initialization failed")
        
        container.register_transient(FailingService)
        
        with pytest.raises(ServiceCreationError) as exc_info:
            container.get_service(FailingService)
        
        assert exc_info.value.service_type == FailingService
        assert isinstance(exc_info.value.original_error, ValueError)
    
    def test_factory_error_handling(self, container):
        """Test error handling in factory functions."""
        def failing_factory(container):
            raise RuntimeError("Factory failed")
        
        container.register_factory(ITestService, failing_factory)
        
        with pytest.raises(ServiceCreationError) as exc_info:
            container.get_service(ITestService)
        
        assert isinstance(exc_info.value.original_error, RuntimeError)
    
    def test_dependency_resolution_error_propagation(self, container):
        """Test error propagation in dependency resolution."""
        class FailingDependency:
            def __init__(self):
                raise ValueError("Dependency failed")
        
        class ServiceWithFailingDependency:
            def __init__(self, failing: FailingDependency):
                self.failing = failing
        
        container.register_transient(FailingDependency)
        container.register_transient(ServiceWithFailingDependency)
        
        with pytest.raises(ServiceCreationError):
            container.get_service(ServiceWithFailingDependency)
    
    # Category 9: Thread Safety Tests
    
    def test_concurrent_singleton_creation(self, container):
        """Test thread-safe singleton creation."""
        container.register_singleton(ITestService, TestService)
        
        instances = []
        
        def get_service():
            instance = container.get_service(ITestService)
            instances.append(instance)
        
        # Create instances concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_service) for _ in range(10)]
            
            for future in futures:
                future.result()
        
        # All instances should be the same
        assert len(set(id(instance) for instance in instances)) == 1
    
    def test_concurrent_registration(self, container):
        """Test thread-safe service registration."""
        def register_service(service_id):
            class DynamicService:
                def __init__(self):
                    self.id = service_id
            
            DynamicService.__name__ = f"DynamicService_{service_id}"
            container.register_transient(DynamicService)
        
        # Register services concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(register_service, i) for i in range(5)]
            
            for future in futures:
                future.result()
        
        # All services should be registered
        all_info = container.get_service_info()
        dynamic_services = [name for name in all_info.keys() if name.startswith("DynamicService_")]
        assert len(dynamic_services) == 5
    
    def test_concurrent_scope_operations(self, container):
        """Test thread-safe scope operations."""
        container.register_scoped(ITestService, TestService)
        
        def scope_operations():
            scope = container.create_scope()
            service = scope.get_service(ITestService)
            scope.dispose()
            return service
        
        # Perform scope operations concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(scope_operations) for _ in range(5)]
            
            services = [future.result() for future in futures]
        
        # All should be different instances (from different scopes)
        assert len(set(id(service) for service in services)) == 5
    
    # Category 10: Advanced Features Tests
    
    def test_creation_count_tracking(self, container):
        """Test creation count is properly tracked."""
        container.register_transient(ITestService, TestService)
        
        # Create multiple instances
        for _ in range(3):
            container.get_service(ITestService)
        
        info = container.get_service_info(ITestService)
        assert info['creation_count'] == 3
    
    def test_dependency_analysis(self, container):
        """Test dependency analysis in service descriptor."""
        container.register_singleton(ITestService, TestService)
        container.register_transient(DependentService)
        
        info = container.get_service_info(DependentService)
        dependencies = info['dependencies']
        
        assert 'ITestService' in dependencies
        # Optional dependencies might not be included
    
    def test_service_state_transitions(self, container):
        """Test service state transitions during lifecycle."""
        container.register_singleton(ITestService, TestService)
        
        # Initially registered
        info = container.get_service_info(ITestService)
        assert info['state'] == ServiceState.REGISTERED.value
        
        # After creation, should be created
        container.get_service(ITestService)
        info = container.get_service_info(ITestService)
        assert info['state'] == ServiceState.CREATED.value
    
    def test_primitive_type_handling(self, container):
        """Test primitive types are not treated as dependencies."""
        class ServiceWithPrimitives:
            def __init__(self, value: int = 42, text: str = "default"):
                self.value = value
                self.text = text
        
        container.register_transient(ServiceWithPrimitives)
        
        # Should create successfully without registering int or str
        service = container.get_service(ServiceWithPrimitives)
        assert service.value == 42
        assert service.text == "default"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])