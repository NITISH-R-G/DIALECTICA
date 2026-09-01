import pytest
from echo_env.server.echo_environment import EchoEnvironment
from openenv.core.env_server.types import Action, Observation

def test_step_impl_unsupported_action():
    env = EchoEnvironment()

    class DummyAction(Action):
        pass

    dummy_action = DummyAction()

    obs: Observation = env._step_impl(dummy_action)

    assert obs.done is False
    assert obs.reward == 0.0
    assert "error" in obs.metadata
    assert obs.metadata["error"].startswith("Unknown action type: DummyAction")
