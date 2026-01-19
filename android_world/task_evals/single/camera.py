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

"""Tasks for the camera app."""

from typing import Any

from absl import logging
from android_world.env import adb_utils
from android_world.env import device_constants
from android_world.env import interface
from android_world.task_evals import task_eval
from android_world.utils import file_utils


class _Camera(task_eval.TaskEval):
  """Base class for Camera tasks."""

  app_names = ("camera",)

  def _clear_app_data(self, env: interface.AsyncEnv) -> None:
    """Clears the app data."""
    file_utils.clear_directory(device_constants.PHOTOS_DATA, env.controller)
    file_utils.clear_directory(device_constants.VIDEOS_DATA, env.controller)

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    self._clear_app_data(env)

  def tear_down(self, env: interface.AsyncEnv):
    super().tear_down(env)
    self._clear_app_data(env)


class CameraTakeVideo(_Camera):
  """Task for checking that one single video has been taken."""

  complexity = 1
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "Take one video."

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    contents = adb_utils.issue_generic_request(
        ["shell", "ls", device_constants.VIDEOS_DATA],
        env.controller,
    )
    logging.info("before_videos: %s", contents.generic.output.decode())
    self.before_videos = set(
        contents.generic.output.decode().replace("\r", "").split("\n")
    )
    logging.info("num before_videos: %s", self.before_videos)

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    contents = adb_utils.issue_generic_request(
        ["shell", "ls", device_constants.VIDEOS_DATA],
        env.controller,
    )
    logging.info("before_videos: %s", contents.generic.output.decode())
    after_videos = set(
        contents.generic.output.decode().replace("\r", "").split("\n")
    )
    logging.info("num after_videos: %s", after_videos)
    new_videos = after_videos - self.before_videos
    logging.info(
        "number of after_videos - number of before_videos: %s",
        len(new_videos),
    )
    success = len(new_videos) == 1

    # Output detailed evaluation information with protection
    try:
      print('\n====================== Task Result Validation ======================')
      print('CameraTakeVideo Evaluation Details:')
      print(f'  - Videos before: {len(self.before_videos)}')
      print(f'  - Videos after: {len(after_videos)}')
      print(f'  - New videos: {new_videos}')
      print(f'  - Expected new videos: 1')
      print(f'  - Validation result: {success}')
      print('====================== Task Result Validation ======================\n')
    except Exception as e:
      print(f'[Warning] Failed to print evaluation details: {e}')

    return 1.0 if success else 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CameraTakePhoto(_Camera):
  """Task for checking that one single photo has been taken."""

  complexity = 1
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "Take one photo."

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    contents = adb_utils.issue_generic_request(
        ["shell", "ls", device_constants.PHOTOS_DATA], env.controller
    )
    logging.info("before_photos: %s", contents.generic.output.decode())
    self.before_photos = set(
        contents.generic.output.decode().replace("\r", "").split("\n")
    )
    logging.info("num before_photos: %s", self.before_photos)

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    contents = adb_utils.issue_generic_request(
        ["shell", "ls", device_constants.PHOTOS_DATA], env.controller
    )
    logging.info("after_photos: %s", contents.generic.output.decode())
    after_photos = set(
        contents.generic.output.decode().replace("\r", "").split("\n")
    )
    logging.info("num after_photos: %s", after_photos)
    new_photos = after_photos - self.before_photos
    logging.info(
        "number of after_photos - number of before_photos: %s",
        len(new_photos),
    )
    success = len(new_photos) == 1

    # Output detailed evaluation information with protection
    try:
      print('\n====================== Task Result Validation ======================')
      print('CameraTakePhoto Evaluation Details:')
      print(f'  - Photos before: {len(self.before_photos)}')
      print(f'  - Photos after: {len(after_photos)}')
      print(f'  - New photos: {new_photos}')
      print(f'  - Expected new photos: 1')
      print(f'  - Validation result: {success}')
      print('====================== Task Result Validation ======================\n')
    except Exception as e:
      print(f'[Warning] Failed to print evaluation details: {e}')

    return 1.0 if success else 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}
