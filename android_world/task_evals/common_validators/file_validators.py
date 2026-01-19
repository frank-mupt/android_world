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

"""Logic for checking file changes using `adb shell`."""

from typing import Any
from absl import logging
from android_world.env import adb_utils
from android_world.env import interface
from android_world.task_evals import task_eval
from android_world.task_evals.utils import user_data_generation
from android_world.utils import file_utils
from android_world.utils import fuzzy_match_lib


class MoveFile(task_eval.TaskEval):
  """For checking that a file has been moved."""

  app_names = ("",)
  complexity = None
  schema = {
      "type": "object",
      "properties": {
          "file_name": {"type": "string"},
          "source_folder": {"type": "string"},
          "destination_folder": {"type": "string"},
      },
      "required": ["file_name", "source_folder", "destination_folder"],
  }
  template = ""

  def __init__(self, params: dict[str, Any], data_directory: str):
    """Initialize the task."""
    super().__init__(params)
    self.source_directory = file_utils.convert_to_posix_path(
        data_directory, self.params["source_folder"]
    )
    self.dest_directory = file_utils.convert_to_posix_path(
        data_directory, self.params["destination_folder"]
    )

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    """Creates the file in the source folder, ensuring it exists before the move operation."""
    super().initialize_task(env)
    user_data_generation.clear_device_storage(env)
    user_data_generation.generate_noise_files(
        self.params["file_name"],
        self.source_directory,
        env.controller,
        self.params["noise_candidates"],
    )
    file_utils.create_file(
        self.params["file_name"], self.source_directory, env.controller
    )
    file_utils.mkdir(self.dest_directory, env.controller)

    if not file_utils.check_file_or_folder_exists(
        self.params["file_name"], self.source_directory, env.controller
    ):
      raise RuntimeError("File was not created in the source folder.")
    if file_utils.check_file_or_folder_exists(
        self.params["file_name"], self.dest_directory, env.controller
    ):
      raise RuntimeError(
          "Something went wrong. File somehow already exists in the destination"
          " folder."
      )

  def tear_down(self, env: interface.AsyncEnv):
    super().tear_down(env)
    user_data_generation.clear_device_storage(env)

  def is_successful(self, env: interface.AsyncEnv) -> float:
    """Check if the file has been moved successfully."""
    super().is_successful(env)
    src_exists = file_utils.check_file_or_folder_exists(
        self.params["file_name"], self.source_directory, env.controller
    )
    dest_exists = file_utils.check_file_or_folder_exists(
        self.params["file_name"], self.dest_directory, env.controller
    )
    succeeded = not src_exists and dest_exists

    # Output detailed evaluation information with protection
    try:
      print('\n====================== Task Result Validation ======================')
      print('MoveFile Evaluation Details:')
      print(f'  - File name: {self.params["file_name"]}')
      print(f'  - Source directory: {self.source_directory}')
      print(f'  - Destination directory: {self.dest_directory}')
      print(f'  - File exists in source: {src_exists} (expected: False)')
      print(f'  - File exists in destination: {dest_exists} (expected: True)')
      print(f'  - Validation result: {succeeded}')
      print('====================== Task Result Validation ======================\n')
    except Exception as e:
      print(f'[Warning] Failed to print evaluation details: {e}')

    return 1.0 if succeeded else 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class DeleteFile(task_eval.TaskEval):
  """For checking that a file has been deleted."""

  app_names = ("",)
  complexity = None
  schema = {
      "type": "object",
      "properties": {
          "file_name": {"type": "string"},
          "subfolder": {"type": "string"},
      },
      "required": ["file_name"],
  }
  template = ""

  def __init__(self, params: dict[str, Any], data_directory: str):
    """Extends base class with data_directory.

    Args:
      params: See base class.
      data_directory: The parent directory to operate in.
    """
    super().__init__(params)
    if "subfolder" in self.params:
      self.data_directory = file_utils.convert_to_posix_path(
          data_directory, self.params["subfolder"]
      )
    else:
      self.data_directory = data_directory

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    """Creates file that should be deleted, along with random files."""
    super().initialize_task(env)
    user_data_generation.clear_device_storage(env)

    file_utils.create_file(
        self.params["file_name"], self.data_directory, env.controller
    )
    user_data_generation.generate_noise_files(
        self.params["file_name"],
        self.data_directory,
        env.controller,
        self.params["noise_candidates"],
    )
    if not file_utils.check_file_or_folder_exists(
        self.params["file_name"], self.data_directory, env.controller
    ):
      raise RuntimeError("Something went wrong, file was not created.")

  def tear_down(self, env: interface.AsyncEnv) -> None:
    super().tear_down(env)
    user_data_generation.clear_device_storage(env)

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    exists = file_utils.check_file_or_folder_exists(
        self.params["file_name"], self.data_directory, env.controller
    )

    # Output detailed evaluation information with protection
    try:
      print('\n====================== Task Result Validation ======================')
      print('DeleteFile Evaluation Details:')
      print(f'  - File name: {self.params["file_name"]}')
      print(f'  - Directory: {self.data_directory}')
      print(f'  - File still exists: {exists} (expected: False)')
      print(f'  - Validation result: {not exists}')
      print('====================== Task Result Validation ======================\n')
    except Exception as e:
      print(f'[Warning] Failed to print evaluation details: {e}')

    return 0.0 if exists else 1.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CreateFile(task_eval.TaskEval):
  """For checking that a new file has been created with a specific name and text."""

  app_names = ("",)
  complexity = None
  schema = {
      "type": "object",
      "properties": {
          "file_name": {"type": "string"},
          "text": {"type": "string"},
      },
      "required": ["file_name", "text"],
  }
  template = ""

  def __init__(self, params: dict[str, Any], data_directory: str):
    """Extends base class with data_directory.

    Args:
      params: See base class.
      data_directory: The parent directory to operate in.
    """
    super().__init__(params)
    self.data_directory = data_directory

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    user_data_generation.clear_device_storage(env)

  def tear_down(self, env: interface.AsyncEnv) -> None:
    super().tear_down(env)
    user_data_generation.clear_device_storage(env)

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    file_name = self.params["file_name"]

    exists = file_utils.check_file_or_folder_exists(
        file_name, self.data_directory, env.controller
    )

    if not exists:
      # Output detailed evaluation information with protection
      try:
        print()
        print('====================== Task Result Validation ======================')
        print('CreateFile Evaluation Details:')
        print(f'  - File name: {file_name}')
        print(f'  - Directory: {self.data_directory}')
        print(f'  - File exists: {exists}')
        print(f'  - Validation result: False (file not found)')
        print('====================== Task Result Validation ======================')
        print()
      except Exception as e:
        print(f'[Warning] Failed to print evaluation details: {e}')
      logging.info("%s not found", file_name)
      return 0.0

    # Check the contents of the new file
    res = adb_utils.issue_generic_request(
        [
            "shell",
            "cat",
            file_utils.convert_to_posix_path(self.data_directory, file_name),
        ],
        env.controller,
    )
    file_contents = res.generic.output.decode().replace("\r", "").strip()
    match = fuzzy_match_lib.fuzzy_match(file_contents, self.params["text"])

    # Output detailed evaluation information with protection
    try:
      print('\n====================== Task Result Validation ======================')
      print('CreateFile Evaluation Details:')
      print(f'  - File name: {file_name}')
      print(f'  - Directory: {self.data_directory}')
      print(f'  - File exists: {exists}')
      print(f'  - Expected content: {self.params["text"]}')
      print(f'  - Actual content: {file_contents}')
      print(f'  - Content match: {match}')
      print(f'  - Validation result: {match}')
      print('====================== Task Result Validation ======================\n')
    except Exception as e:
      print(f'[Warning] Failed to print evaluation details: {e}')

    if not match:
      logging.info("%s does not match %s", file_contents, self.params["text"])
      return 0.0

    return 1.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}
