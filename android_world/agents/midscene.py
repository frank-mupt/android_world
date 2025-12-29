
""" Midscene Agent"""


from android_world.agents import base_agent
from android_world.env import interface

import subprocess
import re
import json
import requests
import os
import time


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
    self.task_no = 0

  def reset(self, go_home: bool = False) -> None:
    super().reset(go_home)
    self.history = []
    self.run_log = []
    self.task_status = {}
    self.task_no = 0
    self.step_count = 0

  def start_new_task(self, task_name: str) -> None:
    """Starts a new task."""
    print("[MidsceneAgent] Starting new task: " + task_name)
    self.task_no += 1
    self.current_task_name = "Task-" + str(self.task_no) + "-" +  str(task_name)

    self._send_rpc_request("new-agent", {"type": "Android", "deviceId": os.environ.get("MIDSCENE_DEVICE_ID"), "id": self.current_task_name})

    self.step_count = 0


  def step(self, goal: str, ) -> base_agent.AgentInteractionResult:
    """Performs a step of the agent on the environment.
    goal: The goal.
    """
    self.step_count += 1
    
    print("[MidsceneAgent] Step: " + str(self.step_count)  + "; Goal: " + goal  )

    midscene_res = self._send_rpc_request("run-ai-method", {"id": self.current_task_name, "task": goal})

    self.run_log.append(midscene_res)

    if midscene_res['result']['code'] == 1:
       return base_agent.AgentInteractionResult(
        done=True,
        data=midscene_res['result']['data'],
      )
    else:
      return base_agent.AgentInteractionResult(
        done=False,
        data={},
      )
  
  def update_task_status(self, status: str = 'Failed') -> None:
    self.task_status[self.current_task_name] = status
    self._send_rpc_request("terminate-agent", {"id": self.current_task_name, "userTaskStatus": self.task_status.get(self.current_task_name, 'Failed')})

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
    response = requests.post(self.rpc_url, headers=headers, json=payload)
    print("[MidsceneAgent] RPC Response: " + response.text)

    response.raise_for_status()
    return response.json()
    

    
    

