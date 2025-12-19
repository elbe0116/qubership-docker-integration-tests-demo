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

@deployments
Feature: Kubernetes Deployment Management
    As an engineer
    I want to manage Kubernetes deployments
    So that I can control application scaling and availability

    Background:
        Given Kubernetes cluster is available

    @scaling
    Scenario: Scale deployment up
        Given deployment "my-app" exists in namespace "my-namespace"
        When I scale up deployment "my-app" in namespace "my-namespace"
        Then deployment should have more replicas than before

    @scaling
    Scenario: Scale deployment down
        Given deployment "my-app" exists in namespace "my-namespace"
        When I scale down deployment "my-app" in namespace "my-namespace"
        Then deployment should have fewer replicas than before

    @scaling
    Scenario: Set specific replica count
        Given deployment "my-app" exists in namespace "my-namespace"
        When I set replicas to 3 for deployment "my-app" in namespace "my-namespace"
        Then deployment "my-app" should have 3 replicas

    @health
    Scenario: Verify all deployments are active for service
        When I get active deployments count for service "my-service" in namespace "my-namespace"
        Then all deployments should be active

    @pods
    Scenario: Get pod names for deployment
        Given deployment "my-app" exists in namespace "my-namespace"
        When I get pod names for deployment "my-app" in namespace "my-namespace"
        Then I should receive a list of pod names

