@services
Feature: Kubernetes Service Discovery

    Background:
        Given Kubernetes cluster is available

    @sample_test @smoke
    Scenario: Get elasticsearch service
        When I get service "elasticsearch" in namespace "elasticsearch-service"
        Then service should be available

    @second_sample_test @smoke
    Scenario: Get first zookeeper service
        When I get service "zookeeper-1" in namespace "zookeeper-service"
        Then service should be available

    @third @smoke
    Scenario: Get second zookeeper service
        When I get service "zookeeper-2" in namespace "zookeeper-service"
        Then service should be available

