#!/usr/bin/env python3
import argparse
from pathlib import Path

from common import call_gitlab, encode_component, handle_error, print_result, resolve_credentials


def build_path(project: str, iid: str) -> str:
    return f"/api/v4/projects/{encode_component(project)}/merge_requests/{iid}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Get GitLab merge request details.")
    parser.add_argument("--project", required=True, help="Project ID or path (for path use group/project).")
    parser.add_argument("--iid", required=True, help="Merge request IID.")
    parser.add_argument(
        "--env-file",
        default=str(Path.cwd() / ".env"),
        help="Path to .env file (default: ./.env in current working directory).",
    )
    return parser.parse_args()


def main() -> int:
    try:
        args = parse_args()
        base_url, token = resolve_credentials(args.env_file)
        result = call_gitlab(base_url, token, build_path(args.project, args.iid))
        print_result(result)
        return 0
    except Exception as exc:
        return handle_error(exc)


if __name__ == "__main__":
    raise SystemExit(main())

