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

@services
Feature: Kubernetes Service Discovery
    As an engineer
    I want to verify that Kubernetes services are available
    So that I can ensure the platform is functioning correctly

    Background:
        Given Kubernetes cluster is available

    @sample_test @smoke
    Scenario: Verify elasticsearch service is available
        When I get service "elasticsearch" in namespace "elasticsearch-service"
        Then service should be available
        And I log the service details

    @second_sample_test @smoke
    Scenario: Verify first zookeeper service is available
        When I get service "zookeeper-1" in namespace "zookeeper-service"
        Then service should be available
        And I log the service details

    @third @smoke
    Scenario: Verify second zookeeper service is available
        When I get service "zookeeper-2" in namespace "zookeeper-service"
        Then service should be available
        And I log the service details

    @parametrized
    Scenario Outline: Verify service availability
        When I get service "<service_name>" in namespace "<namespace>"
        Then service should be available

        Examples:
            | service_name  | namespace              |
            | elasticsearch | elasticsearch-service  |
            | zookeeper-1   | zookeeper-service      |
            | zookeeper-2   | zookeeper-service      |

