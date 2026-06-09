# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import uuid
from echo_env.server.echo_environment import EchoEnvironment

def test_echo_environment_reset_default():
    """Test the default reset behavior."""
    env = EchoEnvironment()

    # Initialize values to check state change
    env._state.step_count = 10
    env._reset_count = 5

    obs = env.reset()

    # Check returned observation
    assert obs.done is False
    assert obs.reward == 0.0
    assert "status" in obs.metadata
    assert obs.metadata["status"] == "ready"
    assert "message" in obs.metadata

    # Check updated state
    assert env._state.step_count == 0
    assert env._reset_count == 6
    assert isinstance(env._state.episode_id, str)

    # Verify episode_id is a valid UUID
    uuid_obj = uuid.UUID(env._state.episode_id)
    assert str(uuid_obj) == env._state.episode_id

def test_echo_environment_reset_with_episode_id():
    """Test reset with a specific episode ID."""
    env = EchoEnvironment()
    custom_episode_id = "test-episode-123"

    obs = env.reset(episode_id=custom_episode_id)

    assert obs.done is False
    assert env._state.episode_id == custom_episode_id
    assert env._state.step_count == 0

def test_echo_environment_reset_with_kwargs():
    """Test reset gracefully handles extra kwargs."""
    env = EchoEnvironment()

    # Shouldn't raise an error
    obs = env.reset(seed=42, custom_kwarg="value", another_kwarg=123)

    assert obs.done is False
    assert env._state.step_count == 0
    assert isinstance(env._state.episode_id, str)
