#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote
from urllib.request import Request, urlopen


def load_env(env_path: Path) -> dict:
    data = {}
    if not env_path.exists():
        return data

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" in line:
            key, value = line.split("=", 1)
        elif ":" in line:
            key, value = line.split(":", 1)
        else:
            continue

        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def pick_value(env_data: dict, *keys: str) -> str:
    for key in keys:
        if key in os.environ and os.environ[key].strip():
            return os.environ[key].strip()
        if key in env_data and env_data[key].strip():
            return env_data[key].strip()
    return ""


def resolve_credentials(env_file: str) -> tuple[str, str]:
    env_data = load_env(Path(env_file))
    base_url = pick_value(env_data, "gitlab_server", "GITLAB_SERVER")
    token = pick_value(env_data, "access_token", "ACCESS_TOKEN", "GITLAB_TOKEN")
    if not base_url:
        raise ValueError("Missing gitlab_server/GITLAB_SERVER in environment or .env")
    if not token:
        raise ValueError("Missing access_token/ACCESS_TOKEN/GITLAB_TOKEN in environment or .env")
    return base_url.rstrip("/"), token


def encode_component(value: str) -> str:
    # Accept both raw and already URL-encoded values without double encoding.
    return quote(unquote(value), safe="")


def call_gitlab(base_url: str, token: str, path: str) -> object:
    url = f"{base_url}{path}"
    headers = {"PRIVATE-TOKEN": token, "Accept": "application/json"}
    request = Request(url, method="GET", headers=headers)
    with urlopen(request, timeout=30) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def print_result(result: object) -> None:
    print(json.dumps(result, ensure_ascii=False, indent=2))


def handle_error(exc: Exception) -> int:
    if isinstance(exc, HTTPError):
        body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP error {exc.code}: {exc.reason}\n{body}", file=sys.stderr)
        return 1
    if isinstance(exc, URLError):
        print(f"Network error: {exc.reason}", file=sys.stderr)
        return 1
    if isinstance(exc, ValueError):
        print(f"Argument/config error: {exc}", file=sys.stderr)
        return 2
    print(f"Execution error: {exc}", file=sys.stderr)
    return 1

