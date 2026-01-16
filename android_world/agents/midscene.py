
""" Midscene Agent"""


from android_world.agents import base_agent
from android_world.env import interface

import requests
import os
import time
import math


class MidsceneAgent(base_agent.EnvironmentInteractingAgent):
  def __init__(
      self,
      env: interface.AsyncEnv,
  ):
    """Initializes a Midscene Agent.
    name: The agent name.
    """
    super().__init__(env, "MidsceneAgent")
    self.history = []
    self.run_log = []
    self._init_json_rpc();
    self.step_count = 0
    self.task_status = {}
    self.failed_step_reason = ''

  def reset(self, go_home: bool = False) -> None:
    super().reset(go_home)
    self.step_count = 0

  def start_new_task(self, task_name: str, task_id: str) -> None:
    """Starts a new task."""
    self._formatted_console("Starting new task, name:  " + task_name + " id: " + task_id)
    self.current_task_name = "Task-" + task_id + "-" +  str(task_name)

    device = { "type": "Android" }

    if os.environ.get("MIDSCENE_DEVICE_TYPE") == "Local":
      device["deviceId"] = os.environ.get("MIDSCENE_DEVICE_ID", "")
    else:
      device["host"] = os.environ.get("MIDSCENE_DEVICE_HOST", "")
      device["port"] = os.environ.get("MIDSCENE_DEVICE_PORT", "")

    self._send_rpc_request("new-agent", {"type": "Android", "device": device, "id": self.current_task_name})

    self.step_count = 0


  # Set max steps of all tasks to be 1
  def set_max_steps(self, max_steps: int) -> None:
    self._max_steps = 1


  def step(self, goal: str, ) -> base_agent.AgentInteractionResult:
    """Performs a step of the agent on the environment.
    goal: The goal.
    """
    self.step_count += 1

    self._formatted_console("Step: " + str(self.step_count)  + "; Goal: " + goal  )

    midscene_res = self._send_rpc_request("run-ai-method", {"id": self.current_task_name, "task": goal})


    self.run_log.append(midscene_res)

    self.failed_step_reason = '';

    if midscene_res['result']['code'] == 1:
       
      action_raw_res = midscene_res['result'].get('data', '')

      self.env.interaction_cache = str(action_raw_res)

      return base_agent.AgentInteractionResult(
        done=True,
        data={ 
          "midscene_action_response": action_raw_res
        },
      )
    else:
      self.failed_step_reason = midscene_res['result']['data'].get('reason', '')
      return base_agent.AgentInteractionResult(
        done=False,
        data={},
      )

  def update_task_status(self, status: str = 'Failed') -> None:
    self.task_status[self.current_task_name] = status
    self._send_rpc_request("terminate-agent", {"id": self.current_task_name, "userTaskStatus": self.task_status.get(self.current_task_name, 'Failed'),  'agentStepError':  self.failed_step_reason })

  def _init_json_rpc(self):
    """Initializes the JSON-RPC connection to the Midscene server."""
    self.rpc_url = os.environ.get("MIDSCENE_BENCH_RPC_URL")
    if not self.rpc_url:
      raise RuntimeError("MIDSCENE_BENCH_RPC_URL environment variable not set.")

  def _send_rpc_request(self, method: str, params: dict) -> dict:
    """Sends a JSON-RPC request to the Midscene server."""
    headers = {'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": time.time()
    }

    request_cnt = 0;
    response = None

    while request_cnt < 3:
      request_cnt += 1
      try:
        response = requests.post(self.rpc_url, headers=headers, json=payload)
        break
      except Exception as e:
        self._formatted_console("RPC Request Failed: " + str(e) + "; Retry: " + str(request_cnt))


    if response is None:
      raise RuntimeError(self._formatted_console("Failed to send RPC request"))

    response.raise_for_status()
    result = response.json()
    self._formatted_console("RPC Response: " + str(result))

    return result

  def _formatted_console(self, content: str) -> None:
    """Formats the console output."""
    print("[MidsceneAgent] " + content)