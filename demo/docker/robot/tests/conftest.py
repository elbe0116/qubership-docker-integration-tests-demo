"""Demo pytest fixtures."""

import pytest
from pytest_bdd import given

from PlatformLibrary import PlatformLibrary


@pytest.fixture(scope="session")
def platform():
    """Create PlatformLibrary instance."""
    return PlatformLibrary(managed_by_operator="true")


@pytest.fixture
def test_context():
    """Shared context between steps."""
    return {}


@given("Kubernetes cluster is available")
def kubernetes_available(platform):
    """Check Kubernetes is available."""
    assert platform is not None

