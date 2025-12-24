
import subprocess
import re

def test_subprocess_regex():
    # Echo a string that matches the pattern
    # simulating the node script output
    output_str = "___ANDROID_WORLD_RESULT_START___ \n{\"code\": 1, \"data\": {}} \n___ANDROID_WORLD_RESULT_END___"
    
    # We use 'echo' to simulate the command
    res = subprocess.run(['echo', output_str], capture_output=True, text=True)
    
    print(f"Type of res: {type(res)}")
    print(f"Type of res.stdout: {type(res.stdout)}")
    print(f"res.stdout: {res.stdout!r}")

    pattern = r"___ANDROID_WORLD_RESULT_START___\s*(.*?)\s*___ANDROID_WORLD_RESULT_END___"
    match = re.search(pattern, res.stdout, re.DOTALL)
    
    if match:
        print("Match found!")
        print(f"Group 1: {match.group(1)}")
    else:
        print("No match found.")

if __name__ == "__main__":
    test_subprocess_regex()
