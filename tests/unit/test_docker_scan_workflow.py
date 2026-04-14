from pathlib import Path

import yaml

WORKFLOW_PATH = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "docker-scan.yml"


def load_workflow() -> dict:
    with WORKFLOW_PATH.open(encoding="utf-8") as handle:
        workflow = yaml.safe_load(handle)
    if True in workflow and "on" not in workflow:
        workflow["on"] = workflow.pop(True)
    return workflow


def test_docker_scan_triggers_on_changed_container_files():
    workflow = load_workflow()
    push_paths = workflow["on"]["push"]["paths"]
    pr_paths = workflow["on"]["pull_request"]["paths"]

    for expected in [
        "Containerfile",
        "Containerfile.lite",
        "a2a-agents/go/a2a-echo-agent/**",
        "mcp-servers/python/python_sandbox_server/docker/**",
        "docker-compose.yml",
        "docker-compose-embedded.yml",
        "docker-compose-verbose-logging.yml",
    ]:
        assert expected in push_paths
        assert expected in pr_paths


def test_docker_scan_builds_changed_dockerfiles():
    workflow = load_workflow()
    matrix = workflow["jobs"]["container-smoke"]["strategy"]["matrix"]["include"]

    assert matrix == [
        {
            "name": "main",
            "context": ".",
            "file": "Containerfile",
            "tag": "mcp-context-forge-main-smoke:scan",
        },
        {
            "name": "a2a-echo-agent",
            "context": "a2a-agents/go/a2a-echo-agent",
            "file": "a2a-agents/go/a2a-echo-agent/Dockerfile",
            "tag": "mcp-context-forge-a2a-echo-agent:scan",
        },
        {
            "name": "python-sandbox",
            "context": "mcp-servers/python/python_sandbox_server",
            "file": "mcp-servers/python/python_sandbox_server/docker/Dockerfile.sandbox",
            "tag": "mcp-context-forge-python-sandbox:scan",
        },
    ]
