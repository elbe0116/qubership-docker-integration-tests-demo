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

@pods
Feature: Kubernetes Pod Operations
    As an engineer
    I want to interact with Kubernetes pods
    So that I can verify application behavior and execute commands

    Background:
        Given Kubernetes cluster is available

    @info
    Scenario: Get pods by service name
        Given service "elasticsearch" exists in namespace "elasticsearch-ns"
        When I get pods by service name "elasticsearch" in namespace "elasticsearch-ns"
        Then I should receive a list of pods

    @commands
    Scenario: Execute command in pod
        Given pod "elasticsearch-0" exists in namespace "elasticsearch-ns"
        When I execute command "ls -la" in pod "elasticsearch-0" namespace "elasticsearch-ns"
        Then command should execute successfully
        And I should receive command output

    @commands
    Scenario: Execute command in specific container
        Given pod "multi-container-pod" exists in namespace "my-ns"
        When I execute command "cat /etc/hosts" in pod "multi-container-pod" container "app" namespace "my-ns"
        Then command should execute successfully

    @health
    Scenario: Verify pods are in ready status
        Given service "my-service" exists in namespace "my-ns"
        When I count pods in ready status for service "my-service" in namespace "my-ns"
        Then ready pods count should match expected count

    @lookup
    Scenario: Look up pod name by IP
        Given I have pod IP "10.129.2.61"
        When I look up pod name by IP "10.129.2.61" in namespace "my-ns"
        Then I should receive the pod name

    @cleanup
    Scenario: Delete pod by name
        Given pod "test-pod-12345" exists in namespace "my-ns"
        When I delete pod "test-pod-12345" in namespace "my-ns"
        Then pod should be deleted

