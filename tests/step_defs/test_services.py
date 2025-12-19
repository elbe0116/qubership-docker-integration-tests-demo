# Copyright 2024-2025 NetCracker Technology Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Step definitions for Kubernetes Services feature.

This module contains steps for:
- Getting and verifying Kubernetes services
- Checking service availability
- Service discovery operations

Engineers can write feature files using these steps without Python knowledge.
"""

import pytest
from pytest_bdd import scenarios, when, then, parsers

# Import all scenarios from the feature file
scenarios("../features/services.feature")


# ============================================================================
# When Steps
# ============================================================================

@when(parsers.parse('I get service "{name}" in namespace "{namespace}"'))
def get_service(platform, test_context, name: str, namespace: str):
    """
    Get a Kubernetes service by name and namespace.
    
    Args:
        name: Service name (e.g., "elasticsearch", "zookeeper-1")
        namespace: Kubernetes namespace where service is located
    
    Example usage in feature file:
        When I get service "elasticsearch" in namespace "elasticsearch-service"
    """
    service = platform.get_service(name, namespace)
    test_context["service"] = service
    test_context["service_name"] = name
    test_context["namespace"] = namespace


# ============================================================================
# Then Steps
# ============================================================================

@then("service should be available")
def service_should_be_available(test_context):
    """
    Verify that the service was successfully retrieved.
    
    This step checks that the service object exists and has a valid spec.
    
    Example usage in feature file:
        Then service should be available
    """
    service = test_context.get("service")
    assert service is not None, "Service was not retrieved"
    assert service.metadata is not None, "Service has no metadata"
    assert service.spec is not None, "Service has no spec"


@then("I log the service details")
def log_service_details(test_context):
    """
    Log service details to console for debugging/verification.
    
    This is equivalent to Robot Framework's "Log To Console" keyword.
    
    Example usage in feature file:
        And I log the service details
    """
    service = test_context.get("service")
    if service:
        print(f"\n📋 Service Details:")
        print(f"   Name: {service.metadata.name}")
        print(f"   Namespace: {service.metadata.namespace}")
        print(f"   Cluster IP: {service.spec.cluster_ip}")
        print(f"   Type: {service.spec.type}")
        if service.spec.ports:
            print(f"   Ports: {[f'{p.port}/{p.protocol}' for p in service.spec.ports]}")


@then(parsers.parse('service type should be "{expected_type}"'))
def service_type_should_be(test_context, expected_type: str):
    """
    Verify service type matches expected value.
    
    Args:
        expected_type: Expected service type (ClusterIP, NodePort, LoadBalancer)
    
    Example usage in feature file:
        Then service type should be "ClusterIP"
    """
    service = test_context.get("service")
    assert service is not None, "Service was not retrieved"
    assert service.spec.type == expected_type, \
        f"Expected service type {expected_type}, got {service.spec.type}"


@then(parsers.parse('service should have port {port:d}'))
def service_should_have_port(test_context, port: int):
    """
    Verify service has expected port.
    
    Args:
        port: Expected port number
    
    Example usage in feature file:
        Then service should have port 9200
    """
    service = test_context.get("service")
    assert service is not None, "Service was not retrieved"
    service_ports = [p.port for p in service.spec.ports] if service.spec.ports else []
    assert port in service_ports, \
        f"Expected port {port} not found in service ports: {service_ports}"

