import pytest
from openenv.core.env_server.types import Observation
from src.contract_env.server.contract_environment import ContractComplianceEnvironment

def test_contract_compliance_environment_reset():
    env = ContractComplianceEnvironment()
    obs = env.reset()

    assert isinstance(obs, Observation)
    assert obs.done is False
    assert obs.reward == 0.0
    assert obs.metadata == {"status": "ready"}
    assert env.state.step_count == 0
    assert env.state.episode_id is not None

def test_contract_compliance_environment_reset_with_seed_and_episode_id():
    env = ContractComplianceEnvironment()
    obs = env.reset(seed=42, episode_id="test_episode")

    assert isinstance(obs, Observation)
    assert obs.done is False
    assert obs.reward == 0.0
    assert obs.metadata == {"status": "ready"}
    assert env.state.episode_id == "test_episode"
    assert env.state.step_count == 0
