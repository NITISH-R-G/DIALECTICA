import pytest
from echo_env.server.echo_environment import EchoEnvironment
from openenv.core.env_server.mcp_types import CallToolAction

def test_step():
    """Test that EchoEnvironment.step correctly delegates and increments step count."""
    env = EchoEnvironment()
    env.reset()

    # Verify initial step count
    assert env.state.step_count == 0

    # Execute a step with CallToolAction
    action = CallToolAction(tool_name="echo_message", arguments={"message": "test_sync"})
    obs = env.step(action)

    # Verify step count incremented
    assert env.state.step_count == 1

    # Verify the observation result matches expected output
    assert getattr(obs, "result", None) is not None
    assert obs.result.data == "test_sync"

@pytest.mark.asyncio
async def test_step_async():
    """Test that EchoEnvironment.step_async correctly delegates and increments step count."""
    env = EchoEnvironment()
    env.reset()

    # Verify initial step count
    assert env.state.step_count == 0

    # Execute an async step with CallToolAction
    action = CallToolAction(tool_name="echo_message", arguments={"message": "test_async"})
    obs = await env.step_async(action)

    # Verify step count incremented
    assert env.state.step_count == 1

    # Verify the observation result matches expected output
    assert getattr(obs, "result", None) is not None
    assert obs.result.data == "test_async"
