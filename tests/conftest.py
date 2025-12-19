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
Pytest configuration and fixtures for BDD tests.

This module provides:
- PlatformLibrary fixture for Kubernetes interactions
- Shared test context for passing data between steps
- Common pytest-bdd hooks and configurations
"""

import os
import pytest
from pytest_bdd import given, parsers

from PlatformLibrary import PlatformLibrary


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def platform() -> PlatformLibrary:
    """
    Session-scoped fixture that provides PlatformLibrary instance.
    
    The library uses in-cluster config by default, or falls back to
    ~/.kube/config for local development.
    
    Environment variables for custom configuration:
        - KUBECONFIG_FILE: Path to custom kubeconfig file
        - KUBECONFIG_CONTEXT: Kubernetes context to use
    """
    config_file = os.environ.get("KUBECONFIG_FILE")
    context = os.environ.get("KUBECONFIG_CONTEXT")
    
    return PlatformLibrary(
        config_file=config_file,
        context=context,
        persist_config=True
    )


@pytest.fixture
def test_context() -> dict:
    """
    Test-scoped fixture for sharing data between steps.
    
    Use this to pass results from 'When' steps to 'Then' steps.
    
    Example:
        @when('I get service...')
        def get_service(test_context, platform):
            test_context['service'] = platform.get_service(...)
        
        @then('service should be available')
        def verify_service(test_context):
            assert test_context['service'] is not None
    """
    return {}


# ============================================================================
# Common Given Steps (registered here for use across all step_defs)
# ============================================================================

@given("Kubernetes cluster is available")
def kubernetes_cluster_available(platform):
    """
    Verifies that we can connect to Kubernetes cluster.
    This step is used in Background sections.
    """
    # If PlatformLibrary was created without errors, cluster is available
    assert platform is not None, "Failed to initialize PlatformLibrary"
    assert platform.k8s_core_v1_client is not None, "Kubernetes client not initialized"


@given(parsers.parse('deployment "{name}" exists in namespace "{namespace}"'))
def deployment_exists(platform, test_context, name: str, namespace: str):
    """Verify deployment exists and store reference in context."""
    deployment = platform.get_deployment_entity(name, namespace)
    assert deployment is not None, f"Deployment {name} not found in {namespace}"
    test_context["deployment"] = deployment
    test_context["deployment_name"] = name
    test_context["namespace"] = namespace


@given(parsers.parse('statefulset "{name}" exists in namespace "{namespace}"'))
def statefulset_exists(platform, test_context, name: str, namespace: str):
    """Verify statefulset exists and store reference in context."""
    statefulset = platform.get_stateful_set(name, namespace)
    assert statefulset is not None, f"StatefulSet {name} not found in {namespace}"
    test_context["statefulset"] = statefulset
    test_context["statefulset_name"] = name
    test_context["namespace"] = namespace


@given(parsers.parse('service "{name}" exists in namespace "{namespace}"'))
def service_exists(platform, test_context, name: str, namespace: str):
    """Verify service exists and store reference in context."""
    service = platform.get_service(name, namespace)
    assert service is not None, f"Service {name} not found in {namespace}"
    test_context["service"] = service
    test_context["service_name"] = name
    test_context["namespace"] = namespace


@given(parsers.parse('pod "{name}" exists in namespace "{namespace}"'))
def pod_exists(platform, test_context, name: str, namespace: str):
    """Verify pod exists and store reference in context."""
    pod = platform.get_pod(name, namespace)
    assert pod is not None, f"Pod {name} not found in {namespace}"
    test_context["pod"] = pod
    test_context["pod_name"] = name
    test_context["namespace"] = namespace


@given(parsers.parse('I have pod IP "{pod_ip}"'))
def have_pod_ip(test_context, pod_ip: str):
    """Store pod IP in context for lookup."""
    test_context["pod_ip"] = pod_ip


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    """
    Hook called when a step fails.
    Useful for debugging and enhanced error reporting.
    """
    print(f"\n❌ Step failed: {step}")
    print(f"   Feature: {feature.name}")
    print(f"   Scenario: {scenario.name}")
    print(f"   Exception: {exception}")


def pytest_bdd_after_scenario(request, feature, scenario):
    """
    Hook called after each scenario completes.
    Can be used for cleanup or logging.
    """
    pass  # Add cleanup logic if needed

