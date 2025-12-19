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
Step definitions for Kubernetes StatefulSets feature.

This module contains steps for:
- Managing StatefulSet replicas
- Checking StatefulSet health
- Scaling operations by service name

Engineers can write feature files using these steps without Python knowledge.
"""

import pytest
from pytest_bdd import scenarios, when, then, parsers

# Import all scenarios from the feature file
scenarios("../features/statefulsets.feature")


# ============================================================================
# When Steps
# ============================================================================

@when(parsers.parse('I check statefulset "{name}" ready replicas in namespace "{namespace}"'))
def check_statefulset_ready_replicas(platform, test_context, name: str, namespace: str):
    """
    Check ready replicas count for a StatefulSet.
    
    Args:
        name: StatefulSet name
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I check statefulset "cassandra" ready replicas in namespace "cassandra-ns"
    """
    ready_count = platform.get_stateful_set_ready_replicas_count(name, namespace)
    total_count = platform.get_stateful_set_replicas_count(name, namespace)
    
    test_context["ready_replicas"] = ready_count
    test_context["total_replicas"] = total_count
    test_context["statefulset_name"] = name


@when(parsers.parse('I set replicas to {count:d} for statefulset "{name}" in namespace "{namespace}"'))
def set_statefulset_replicas(platform, test_context, count: int, name: str, namespace: str):
    """
    Set specific replica count for StatefulSet.
    
    Args:
        count: Desired number of replicas
        name: StatefulSet name
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I set replicas to 3 for statefulset "cassandra" in namespace "cassandra-ns"
    """
    platform.set_replicas_for_stateful_set(name, namespace, replicas=count)
    
    statefulset = platform.get_stateful_set(name, namespace)
    test_context["statefulset"] = statefulset
    test_context["replicas_after"] = statefulset.spec.replicas


@when(parsers.parse('I scale down statefulsets by service name "{service}" in namespace "{namespace}" with check'))
def scale_down_statefulsets_by_service_with_check(platform, test_context, service: str, namespace: str):
    """
    Scale down all StatefulSets related to a service and wait for completion.
    
    Args:
        service: Service name to find related StatefulSets
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I scale down statefulsets by service name "cassandra-svc" in namespace "cassandra-ns" with check
    """
    # Get statefulset names before scaling
    statefulset_names = platform.get_stateful_set_names_by_service_name(service, namespace)
    test_context["statefulset_names"] = statefulset_names
    
    # Scale down with check (waits for completion)
    platform.scale_down_stateful_sets_by_service_name(
        service, 
        namespace, 
        with_check=True, 
        timeout=300
    )
    
    test_context["scale_operation"] = "down"


@when(parsers.parse('I get pod names for statefulset "{name}" in namespace "{namespace}"'))
def get_statefulset_pod_names(platform, test_context, name: str, namespace: str):
    """
    Get expected pod names for a StatefulSet.
    
    StatefulSets have predictable pod naming: <name>-0, <name>-1, etc.
    
    Args:
        name: StatefulSet name
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I get pod names for statefulset "cassandra" in namespace "cassandra-ns"
    """
    pod_names = platform.get_pod_names_for_stateful_set(name, namespace)
    test_context["pod_names"] = pod_names
    test_context["statefulset_name"] = name


# ============================================================================
# Then Steps
# ============================================================================

@then("all replicas should be ready")
def all_replicas_ready(test_context):
    """
    Verify all StatefulSet replicas are in ready state.
    
    Example usage in feature file:
        Then all replicas should be ready
    """
    ready = test_context.get("ready_replicas", 0)
    total = test_context.get("total_replicas", 0)
    name = test_context.get("statefulset_name", "unknown")
    
    assert ready == total, \
        f"StatefulSet {name}: only {ready} of {total} replicas are ready"
    print(f"\n✅ StatefulSet {name}: all {total} replicas are ready")


@then(parsers.parse('statefulset "{name}" should have {count:d} replicas'))
def statefulset_has_specific_replicas(test_context, name: str, count: int):
    """
    Verify StatefulSet has specific replica count.
    
    Args:
        name: StatefulSet name (for error messages)
        count: Expected number of replicas
    
    Example usage in feature file:
        Then statefulset "cassandra" should have 3 replicas
    """
    actual = test_context.get("replicas_after", 0)
    assert actual == count, f"Expected {count} replicas for {name}, got {actual}"


@then("all related statefulsets should be scaled down")
def statefulsets_scaled_down(platform, test_context):
    """
    Verify all StatefulSets were scaled down (0 replicas).
    
    Example usage in feature file:
        Then all related statefulsets should be scaled down
    """
    statefulset_names = test_context.get("statefulset_names", [])
    namespace = test_context.get("namespace")
    
    for name in statefulset_names:
        statefulset = platform.get_stateful_set(name, namespace)
        replicas = statefulset.spec.replicas or 0
        assert replicas == 0, \
            f"StatefulSet {name} still has {replicas} replicas"
    
    print(f"\n✅ All {len(statefulset_names)} StatefulSets scaled down to 0 replicas")


@then(parsers.parse('I should receive a list of pod names with pattern "{pattern}"'))
def received_pod_names_with_pattern(test_context, pattern: str):
    """
    Verify pod names follow expected pattern.
    
    For StatefulSets, pods are named: <statefulset-name>-0, <statefulset-name>-1, etc.
    Pattern uses "N" as placeholder for number.
    
    Args:
        pattern: Expected naming pattern (e.g., "cassandra-N")
    
    Example usage in feature file:
        Then I should receive a list of pod names with pattern "cassandra-N"
    """
    pod_names = test_context.get("pod_names", [])
    statefulset_name = test_context.get("statefulset_name")
    
    assert pod_names is not None, "Pod names list was not retrieved"
    assert isinstance(pod_names, list), "Pod names should be a list"
    
    # Verify pattern
    base_name = pattern.replace("-N", "")
    for i, pod_name in enumerate(pod_names):
        expected = f"{base_name}-{i}"
        assert pod_name == expected, \
            f"Expected pod name {expected}, got {pod_name}"
    
    print(f"\n📋 StatefulSet pods: {pod_names}")

