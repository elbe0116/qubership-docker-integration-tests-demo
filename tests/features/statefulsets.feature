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

@statefulsets
Feature: Kubernetes StatefulSet Management
    As an engineer
    I want to manage Kubernetes StatefulSets
    So that I can control stateful application instances

    Background:
        Given Kubernetes cluster is available

    @health
    Scenario: Verify StatefulSet replicas are ready
        Given statefulset "cassandra" exists in namespace "cassandra-ns"
        When I check statefulset "cassandra" ready replicas in namespace "cassandra-ns"
        Then all replicas should be ready

    @scaling
    Scenario: Scale StatefulSet to specific replica count
        Given statefulset "cassandra" exists in namespace "cassandra-ns"
        When I set replicas to 3 for statefulset "cassandra" in namespace "cassandra-ns"
        Then statefulset "cassandra" should have 3 replicas

    @scaling
    Scenario: Scale down StatefulSets by service name
        Given service "cassandra-svc" exists in namespace "cassandra-ns"
        When I scale down statefulsets by service name "cassandra-svc" in namespace "cassandra-ns" with check
        Then all related statefulsets should be scaled down

    @pods
    Scenario: Get expected pod names for StatefulSet
        Given statefulset "cassandra" exists in namespace "cassandra-ns"
        When I get pod names for statefulset "cassandra" in namespace "cassandra-ns"
        Then I should receive a list of pod names with pattern "cassandra-N"

