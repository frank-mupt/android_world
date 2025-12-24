
""" Midscene Agent"""


from android_world.agents import base_agent
from android_world.env import interface

import subprocess
import re
import json


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

  def reset(self, go_home: bool = False) -> None:
    super().reset(go_home)
    self.history = []
    self.run_log = []

  def step(self, goal: str) -> base_agent.AgentInteractionResult:
    """Performs a step of the agent on the environment.
    goal: The goal.
    """

    print("MidsceneAgent step: " + goal)

    midscene_res = subprocess.run(
        ['node', "/Users/bytedance/work/Frank/midscene-project/midscene/benchmarks/android-world/dist/runner.js", f"--goal={goal}"],
        capture_output=True,
        text=True
    )

    self.run_log.append(midscene_res)

    pattern = r"___ANDROID_WORLD_RESULT_START___\s*(.*?)\s*___ANDROID_WORLD_RESULT_END___"

    print(midscene_res.stderr);
    print(midscene_res.stdout);
    
    match = re.search(pattern, midscene_res.stdout, re.DOTALL)
    if match:
        result_info = match.group(1).strip()
        formatted_result = json.loads(result_info)
        self.history.append(formatted_result)

        if formatted_result["code"] == 1:
          return base_agent.AgentInteractionResult(
            done=True,
            data=formatted_result["data"],
          )
        else:
          print(formatted_result["data"])
          return base_agent.AgentInteractionResult(
            done=False,
            data=formatted_result["data"],
          )
    else:
      return base_agent.AgentInteractionResult(
        done=False,
        data={},
      )
    

    
    

