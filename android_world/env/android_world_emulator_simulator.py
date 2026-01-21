# Copyright 2025 The android_world Authors.
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

"""Extended EmulatorSimulator for android_world project."""

import os

from android_env.components.simulators.emulator import emulator_simulator


def _is_remote_mode() -> bool:
  """Check if running in remote/Docker mode."""
  return os.getenv("ANDROID_CONNECTION_TYPE") == "Remote"


def _get_remote_device_name() -> str:
  """Get device name for remote mode (host:port format)."""
  host = os.getenv("ANDROID_REMOTE_HOST", "localhost")
  port = os.getenv("ANDROID_ADB_PORT", "5555")
  return f"{host}:{port}"


class AndroidWorldEmulatorSimulator(emulator_simulator.EmulatorSimulator):
  """Extended EmulatorSimulator for android_world project.

  Supports both local and remote ADB connections:
  - Local mode: uses default "emulator-<port>" format
  - Remote mode: uses "host:port" format (e.g., "localhost:5555")
  """

  def adb_device_name(self) -> str:
    """Returns the ADB device name based on connection mode."""
    if _is_remote_mode():
      return _get_remote_device_name()
    return super().adb_device_name()
