import pytest
from echo_env.server.echo_environment import EchoEnvironment
from openenv.core.env_server.mcp_types import CallToolAction

@pytest.mark.asyncio
async def test_echo_environment_step_async():
    env = EchoEnvironment()
    env.reset()

    assert env.state.step_count == 0

    action = CallToolAction(tool_name="echo_message", arguments={"message": "hello"})
    obs = await env.step_async(action)

    assert env.state.step_count == 1
    assert obs.result.data == "hello"
