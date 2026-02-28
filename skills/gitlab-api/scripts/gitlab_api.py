#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
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


def normalize_base_url(url: str) -> str:
    return url.rstrip("/")


def build_path(project: str, command: str, iid: str, file_path: str, ref: str) -> str:
    project_encoded = quote(project, safe="")
    if command == "mr":
        return f"/api/v4/projects/{project_encoded}/merge_requests/{iid}"
    if command == "changes":
        return f"/api/v4/projects/{project_encoded}/merge_requests/{iid}/changes"
    if command == "notes":
        return f"/api/v4/projects/{project_encoded}/merge_requests/{iid}/notes"
    if command == "file":
        file_encoded = quote(file_path, safe="")
        query = urlencode({"ref": ref})
        return f"/api/v4/projects/{project_encoded}/repository/files/{file_encoded}?{query}"
    raise ValueError(f"Unsupported command: {command}")


def call_gitlab(base_url: str, token: str, path: str) -> object:
    url = f"{base_url}{path}"
    request = Request(url, headers={"PRIVATE-TOKEN": token, "Accept": "application/json"})
    with urlopen(request, timeout=30) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Call selected GitLab REST API endpoints.")
    parser.add_argument("command", choices=["mr", "changes", "notes", "file"])
    parser.add_argument("--project", required=True, help="Project ID or path (for path use group/project).")
    parser.add_argument("--iid", help="Merge request IID (required for mr/changes/notes).")
    parser.add_argument("--file-path", help="Repository file path (required for file).")
    parser.add_argument("--ref", default="main", help="Ref for repository file endpoint (default: main).")
    parser.add_argument(
        "--env-file",
        default=str(Path(__file__).resolve().parent.parent / ".env"),
        help="Path to .env file (default: skill root .env).",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.command in {"mr", "changes", "notes"} and not args.iid:
        raise ValueError("--iid is required for mr/changes/notes")
    if args.command == "file" and not args.file_path:
        raise ValueError("--file-path is required for file")


def main() -> int:
    try:
        args = parse_args()
        validate_args(args)

        env_data = load_env(Path(args.env_file))
        base_url = pick_value(env_data, "gitlab_server", "GITLAB_SERVER")
        token = pick_value(env_data, "access_token", "ACCESS_TOKEN", "GITLAB_TOKEN")

        if not base_url:
            raise ValueError("Missing gitlab_server/GITLAB_SERVER in environment or .env")
        if not token:
            raise ValueError("Missing access_token/ACCESS_TOKEN/GITLAB_TOKEN in environment or .env")

        path = build_path(
            project=args.project,
            command=args.command,
            iid=args.iid or "",
            file_path=args.file_path or "",
            ref=args.ref,
        )

        result = call_gitlab(normalize_base_url(base_url), token, path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP error {e.code}: {e.reason}\n{body}", file=sys.stderr)
        return 1
    except URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Argument/config error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
