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
Step definitions for Kubernetes Deployments feature.

This module contains steps for:
- Scaling deployments up and down
- Setting replica counts
- Verifying deployment health
- Getting pod information

Engineers can write feature files using these steps without Python knowledge.
"""

import pytest
from pytest_bdd import scenarios, when, then, parsers

# Import all scenarios from the feature file
scenarios("../features/deployments.feature")


# ============================================================================
# When Steps
# ============================================================================

@when(parsers.parse('I scale up deployment "{name}" in namespace "{namespace}"'))
def scale_up_deployment(platform, test_context, name: str, namespace: str):
    """
    Scale up a deployment by one replica.
    
    Args:
        name: Deployment name
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I scale up deployment "my-app" in namespace "my-namespace"
    """
    # Store current replica count before scaling
    deployment = platform.get_deployment_entity(name, namespace)
    test_context["replicas_before"] = deployment.spec.replicas or 0
    
    platform.scale_up_deployment_entity(name, namespace)
    
    # Get updated deployment
    deployment = platform.get_deployment_entity(name, namespace)
    test_context["deployment"] = deployment
    test_context["replicas_after"] = deployment.spec.replicas


@when(parsers.parse('I scale down deployment "{name}" in namespace "{namespace}"'))
def scale_down_deployment(platform, test_context, name: str, namespace: str):
    """
    Scale down a deployment by one replica.
    
    Args:
        name: Deployment name
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I scale down deployment "my-app" in namespace "my-namespace"
    """
    # Store current replica count before scaling
    deployment = platform.get_deployment_entity(name, namespace)
    test_context["replicas_before"] = deployment.spec.replicas or 0
    
    platform.scale_down_deployment_entity(name, namespace)
    
    # Get updated deployment
    deployment = platform.get_deployment_entity(name, namespace)
    test_context["deployment"] = deployment
    test_context["replicas_after"] = deployment.spec.replicas


@when(parsers.parse('I set replicas to {count:d} for deployment "{name}" in namespace "{namespace}"'))
def set_deployment_replicas(platform, test_context, count: int, name: str, namespace: str):
    """
    Set specific replica count for deployment.
    
    Args:
        count: Desired number of replicas
        name: Deployment name
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I set replicas to 3 for deployment "my-app" in namespace "my-namespace"
    """
    platform.set_replicas_for_deployment_entity(name, namespace, replicas=count)
    
    deployment = platform.get_deployment_entity(name, namespace)
    test_context["deployment"] = deployment
    test_context["replicas_after"] = deployment.spec.replicas


@when(parsers.parse('I get active deployments count for service "{service}" in namespace "{namespace}"'))
def get_active_deployments_count(platform, test_context, service: str, namespace: str):
    """
    Get count of active deployments for a service.
    
    Args:
        service: Service name to filter deployments
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I get active deployments count for service "my-service" in namespace "my-namespace"
    """
    active_count = platform.get_active_deployment_entities_count_for_service(namespace, service)
    total_count = platform.get_deployment_entities_count_for_service(namespace, service)
    
    test_context["active_deployments_count"] = active_count
    test_context["total_deployments_count"] = total_count


@when(parsers.parse('I get pod names for deployment "{name}" in namespace "{namespace}"'))
def get_deployment_pod_names(platform, test_context, name: str, namespace: str):
    """
    Get list of pod names managed by a deployment.
    
    Args:
        name: Deployment name
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I get pod names for deployment "my-app" in namespace "my-namespace"
    """
    pod_names = platform.get_pod_names_for_deployment_entity(name, namespace)
    test_context["pod_names"] = pod_names


# ============================================================================
# Then Steps
# ============================================================================

@then("deployment should have more replicas than before")
def deployment_has_more_replicas(test_context):
    """
    Verify deployment was scaled up.
    
    Example usage in feature file:
        Then deployment should have more replicas than before
    """
    before = test_context.get("replicas_before", 0)
    after = test_context.get("replicas_after", 0)
    assert after > before, f"Expected more replicas, but got {after} (was {before})"


@then("deployment should have fewer replicas than before")
def deployment_has_fewer_replicas(test_context):
    """
    Verify deployment was scaled down.
    
    Example usage in feature file:
        Then deployment should have fewer replicas than before
    """
    before = test_context.get("replicas_before", 0)
    after = test_context.get("replicas_after", 0)
    assert after < before, f"Expected fewer replicas, but got {after} (was {before})"


@then(parsers.parse('deployment "{name}" should have {count:d} replicas'))
def deployment_has_specific_replicas(test_context, name: str, count: int):
    """
    Verify deployment has specific replica count.
    
    Args:
        name: Deployment name (for error messages)
        count: Expected number of replicas
    
    Example usage in feature file:
        Then deployment "my-app" should have 3 replicas
    """
    actual = test_context.get("replicas_after", 0)
    assert actual == count, f"Expected {count} replicas for {name}, got {actual}"


@then("all deployments should be active")
def all_deployments_active(test_context):
    """
    Verify all deployments are in active state.
    
    Example usage in feature file:
        Then all deployments should be active
    """
    active = test_context.get("active_deployments_count", 0)
    total = test_context.get("total_deployments_count", 0)
    assert active == total, f"Only {active} of {total} deployments are active"


@then("I should receive a list of pod names")
def received_pod_names_list(test_context):
    """
    Verify pod names list was retrieved.
    
    Example usage in feature file:
        Then I should receive a list of pod names
    """
    pod_names = test_context.get("pod_names")
    assert pod_names is not None, "Pod names list was not retrieved"
    assert isinstance(pod_names, list), "Pod names should be a list"
    print(f"\n📋 Found {len(pod_names)} pods: {pod_names}")

