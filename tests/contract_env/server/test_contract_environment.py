import pytest
from contract_env.server.contract_environment import ContractComplianceEnvironment
from openenv.core.env_server.types import Action, Observation

class DummyAction(Action):
    """A dummy action class for testing."""
    pass

class AnotherDummyAction(Action):
    """Another dummy action class to verify class name formatting."""
    pass

@pytest.fixture
def env():
    return ContractComplianceEnvironment()

def test_step_impl_returns_observation(env):
    """Verify _step_impl returns a valid Observation."""
    action = DummyAction()
    obs = env._step_impl(action)

    assert isinstance(obs, Observation)
    assert obs.done is False
    assert obs.reward == 0.0

def test_step_impl_error_metadata(env):
    """Verify the error message in metadata is formatted correctly with the action class name."""
    action1 = DummyAction()
    obs1 = env._step_impl(action1)

    assert "error" in obs1.metadata
    assert "Unknown action type: DummyAction" in obs1.metadata["error"]
    assert "Use ListToolsAction or CallToolAction for MCP interactions." in obs1.metadata["error"]

    action2 = AnotherDummyAction()
    obs2 = env._step_impl(action2)

    assert "error" in obs2.metadata
    assert "Unknown action type: AnotherDummyAction" in obs2.metadata["error"]
    assert "Use ListToolsAction or CallToolAction for MCP interactions." in obs2.metadata["error"]
