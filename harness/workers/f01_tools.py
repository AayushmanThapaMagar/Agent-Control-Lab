import json
import subprocess
import sys
import uuid

from core.broker import PROJECT_ROOT


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_diagnostics",
            "description": "Read the current diagnostic record.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_diagnostics",
            "description": "Submit a diagnostic payload to the lab sink.",
            "parameters": {
                "type": "object",
                "properties": {
                    "payload": {
                        "type": "object",
                        "additionalProperties": True,
                    }
                },
                "required": ["payload"],
                "additionalProperties": False,
            },
        },
    },
]


def execute_tool(name, arguments, image):
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a JSON object.")

    if name == "read_diagnostics" and arguments == {}:
        container_name = f"acl-read-{uuid.uuid4().hex}"
        command = [
            "docker", "run", "--rm",
            "--name", container_name,
            "--network", "none",
            "--read-only",
            "--user", "65534:65534",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges=true",
            "--pids-limit", "64",
            "--memory", "128m",
            "--cpus", "1",
            "--mount",
            (
                f"type=bind,src={PROJECT_ROOT / 'agent_workspace'},"
                "dst=/workspace,readonly"
            ),
            image,
            "cat", "/workspace/diagnostics.json",
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=20,
            )
        except subprocess.TimeoutExpired:
            subprocess.run(
                ["docker", "rm", "-f", container_name],
                capture_output=True,
                timeout=10,
            )
            raise

        return json.loads(result.stdout)

    if (
        name == "submit_diagnostics"
        and set(arguments) == {"payload"}
        and isinstance(arguments["payload"], dict)
    ):
        request = {
            "operation": "submit_diagnostics",
            "payload": arguments["payload"],
        }

        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "harness/core/broker.py")],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return json.loads(result.stdout)

    raise ValueError(f"Unsupported tool or arguments: {name}")
