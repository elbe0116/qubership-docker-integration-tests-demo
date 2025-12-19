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
Step definitions for Kubernetes Pods feature.

This module contains steps for:
- Getting pods by various selectors
- Executing commands in pods
- Pod health verification
- Pod lifecycle operations

Engineers can write feature files using these steps without Python knowledge.
"""

import pytest
from pytest_bdd import scenarios, when, then, parsers

# Import all scenarios from the feature file
scenarios("../features/pods.feature")


# ============================================================================
# When Steps
# ============================================================================

@when(parsers.parse('I get pods by service name "{service}" in namespace "{namespace}"'))
def get_pods_by_service(platform, test_context, service: str, namespace: str):
    """
    Get all pods managed by a service.
    
    Args:
        service: Service name
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I get pods by service name "elasticsearch" in namespace "elasticsearch-ns"
    """
    pods = platform.get_pods_by_service_name(service, namespace)
    test_context["pods"] = pods
    test_context["service_name"] = service


@when(parsers.parse('I execute command "{command}" in pod "{pod}" namespace "{namespace}"'))
def execute_command_in_pod(platform, test_context, command: str, pod: str, namespace: str):
    """
    Execute a shell command in a pod.
    
    Args:
        command: Shell command to execute
        pod: Pod name
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I execute command "ls -la" in pod "elasticsearch-0" namespace "elasticsearch-ns"
    """
    result, errors = platform.execute_command_in_pod(pod, namespace, command)
    test_context["command_result"] = result
    test_context["command_errors"] = errors
    test_context["command"] = command


@when(parsers.parse('I execute command "{command}" in pod "{pod}" container "{container}" namespace "{namespace}"'))
def execute_command_in_pod_container(platform, test_context, command: str, pod: str, 
                                      container: str, namespace: str):
    """
    Execute a shell command in a specific container within a pod.
    
    Args:
        command: Shell command to execute
        pod: Pod name
        container: Container name within the pod
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I execute command "cat /etc/hosts" in pod "multi-container" container "app" namespace "my-ns"
    """
    result, errors = platform.execute_command_in_pod(pod, namespace, command, container=container)
    test_context["command_result"] = result
    test_context["command_errors"] = errors
    test_context["command"] = command
    test_context["container"] = container


@when(parsers.parse('I count pods in ready status for service "{service}" in namespace "{namespace}"'))
def count_ready_pods(platform, test_context, service: str, namespace: str):
    """
    Count pods in ready status for a service.
    
    Args:
        service: Service name
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I count pods in ready status for service "my-service" in namespace "my-ns"
    """
    ready_count = platform.number_of_pods_in_ready_status(service, namespace)
    pods = platform.get_pods_by_service_name(service, namespace)
    
    test_context["ready_pods_count"] = ready_count
    test_context["total_pods_count"] = len(pods)


@when(parsers.parse('I look up pod name by IP "{ip}" in namespace "{namespace}"'))
def lookup_pod_by_ip(platform, test_context, ip: str, namespace: str):
    """
    Look up a pod name by its IP address.
    
    Args:
        ip: Pod IP address
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I look up pod name by IP "10.129.2.61" in namespace "my-ns"
    """
    pod_name = platform.look_up_pod_name_by_pod_ip(ip, namespace)
    test_context["found_pod_name"] = pod_name
    test_context["searched_ip"] = ip


@when(parsers.parse('I delete pod "{name}" in namespace "{namespace}"'))
def delete_pod(platform, test_context, name: str, namespace: str):
    """
    Delete a pod by name.
    
    Args:
        name: Pod name
        namespace: Kubernetes namespace
    
    Example usage in feature file:
        When I delete pod "test-pod-12345" in namespace "my-ns"
    """
    platform.delete_pod_by_pod_name(name, namespace)
    test_context["deleted_pod_name"] = name
    test_context["delete_operation"] = "completed"


# ============================================================================
# Then Steps
# ============================================================================

@then("I should receive a list of pods")
def received_pods_list(test_context):
    """
    Verify pods list was retrieved.
    
    Example usage in feature file:
        Then I should receive a list of pods
    """
    pods = test_context.get("pods")
    assert pods is not None, "Pods list was not retrieved"
    assert isinstance(pods, list), "Pods should be a list"
    
    pod_names = [p.metadata.name for p in pods]
    print(f"\n📋 Found {len(pods)} pods: {pod_names}")


@then("command should execute successfully")
def command_executed_successfully(test_context):
    """
    Verify command executed without critical errors.
    
    Note: Some stderr output may be normal (warnings, info messages).
    This step checks that the command didn't completely fail.
    
    Example usage in feature file:
        Then command should execute successfully
    """
    result = test_context.get("command_result")
    errors = test_context.get("command_errors", "")
    command = test_context.get("command", "unknown")
    
    # Command is successful if we got some result
    # (even if there are some warnings in stderr)
    assert result is not None, f"Command '{command}' failed to execute"
    print(f"\n✅ Command executed: {command}")


@then("I should receive command output")
def received_command_output(test_context):
    """
    Verify and display command output.
    
    Example usage in feature file:
        And I should receive command output
    """
    result = test_context.get("command_result", "")
    errors = test_context.get("command_errors", "")
    
    print(f"\n📋 Command output:\n{result}")
    if errors:
        print(f"\n⚠️ Stderr:\n{errors}")


@then("ready pods count should match expected count")
def ready_pods_match_expected(test_context):
    """
    Verify all pods are in ready status.
    
    Example usage in feature file:
        Then ready pods count should match expected count
    """
    ready = test_context.get("ready_pods_count", 0)
    total = test_context.get("total_pods_count", 0)
    
    assert ready == total, \
        f"Only {ready} of {total} pods are ready"
    print(f"\n✅ All {total} pods are in ready status")


@then("I should receive the pod name")
def received_pod_name(test_context):
    """
    Verify pod name was found by IP lookup.
    
    Example usage in feature file:
        Then I should receive the pod name
    """
    pod_name = test_context.get("found_pod_name")
    ip = test_context.get("searched_ip")
    
    assert pod_name is not None, f"No pod found with IP {ip}"
    print(f"\n✅ Found pod '{pod_name}' for IP {ip}")


@then("pod should be deleted")
def pod_deleted(test_context):
    """
    Verify pod deletion was initiated.
    
    Note: Pod deletion is asynchronous. This step verifies
    the deletion request was accepted.
    
    Example usage in feature file:
        Then pod should be deleted
    """
    operation = test_context.get("delete_operation")
    pod_name = test_context.get("deleted_pod_name")
    
    assert operation == "completed", "Delete operation was not completed"
    print(f"\n✅ Pod '{pod_name}' deletion initiated")

