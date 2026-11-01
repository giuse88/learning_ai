#/usr/bin/env python3


"""Harness v1: a chat loop. The array IS the conversation."""
from pprint import pprint
import json, os, urllib.request
import subprocess

URL="https://api.anthropic.com/v1/messages"
API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-sonnet-5"
SYSTEM = "You are a concise assistant."
HEADERS = {"content-type": "application/json", "x-api-key": API_KEY, "anthropic-version": "2023-06-01"}

TOOLS = [                                            # NEW: the menu
    {"name": "read_file",
     "description": "Read a text file and return its contents.",
     "input_schema": {"type": "object",
                      "properties": {"path": {"type": "string"}},
                      "required": ["path"]}},
    {"name": "run_command",
     "description": "Run a shell command and return stdout+stderr.",
     "input_schema": {"type": "object",
                      "properties": {"command": {"type": "string"}},
                      "required": ["command"]}},
]


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def execute_tool(name, args): 
    """Map the model's JSON request to a real function call."""
    try:
        if name == "read_file":
            return open(args["path"]).read()
        if name == "run_command":
            out = subprocess.run(
                args["command"], 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=60)
            return out.stdout + out.stderr
        return f"ERROR: unknown tool {name}"
    except Exception as e:
        return f"ERROR: {e}"


def call_llm(messages):
    body = {"model": MODEL, "max_tokens": 4096, 
            "system": SYSTEM, "messages": messages, 
            "tools":TOOLS}
    print("Sending...")
    pprint(body)
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def main():
    messages = []                                   # the entire "session"
    while True:

        user_text = input(f"\n{Colors.OKGREEN }You>{Colors.ENDC}").strip()

        if user_text in ("/quit", "", "/exit"):
            break
                      
        if user_text == "/clear":
            messages = []                           # "new conversation"
            continue

        messages.append({"role": "user", "content": user_text})
        reply = call_llm(messages)                  # resend EVERYTHING

        print("Reply...")
        pprint(reply)
        messages.append({"role": "assistant", "content": reply["content"]})


        for block in reply["content"]:

            if block["type"] == "tool_use":        # NEW: honor ONE request
                print(f"{Colors.WARNING}\n[tool] {block['name']}({json.dumps(block['input'])}){Colors.ENDC}")
                result = execute_tool(block["name"], block["input"])
                messages.append({"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": block["id"],
                     "content": result}]})
                reply2 = call_llm(messages)          # let the model react once
                messages.append({"role": "assistant",
                                 "content": reply2["content"]})
                for b2 in reply2["content"]:
                    if b2["type"] == "text":
                        print(f"{Colors.OKBLUE}\nassistant>{Colors.ENDC} {Colors.BOLD}{b2['text']}{Colors.ENDC}")
                # If reply2 asks for ANOTHER tool, v2 drops it. Chapter 4.
            elif block["type"] == "text":
                print(f"\nassistant> {block['text']}")
                print(f"{Colors.OKBLUE}\nassistant>{Colors.ENDC} {Colors.BOLD}{block['text']}{Colors.ENDC}")


if __name__ == "__main__":
    main()
