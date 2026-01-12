"""Service discovery step definitions."""

from pytest_bdd import scenarios, when, then, parsers

scenarios("../features/services.feature")


@when(parsers.parse('I get service "{name}" in namespace "{namespace}"'))
def get_service(platform, test_context, name, namespace):
    """Get Kubernetes service."""
    service = platform.get_service(name, namespace)
    test_context["service"] = service
    print(f"\n📋 Service: {service}")


@then("service should be available")
def service_available(test_context):
    """Verify service is available."""
    assert test_context["service"] is not None

