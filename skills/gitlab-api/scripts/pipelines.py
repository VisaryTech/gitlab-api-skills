#!/usr/bin/env python3
import argparse
from pathlib import Path
from urllib.parse import urlencode

from common import call_gitlab, encode_component, handle_error, print_result, resolve_credentials


def build_path(project: str, ref: str, per_page: int) -> str:
    query = urlencode({"ref": ref, "per_page": per_page})
    return f"/api/v4/projects/{encode_component(project)}/pipelines?{query}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List GitLab pipelines for a ref.")
    parser.add_argument("--project", required=True, help="Project ID or path (for path use group/project).")
    parser.add_argument("--ref", required=True, help="Git ref (branch/tag).")
    parser.add_argument(
        "--per-page",
        type=int,
        default=1,
        help="Number of records per page (default: 1).",
    )
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
        result = call_gitlab(base_url, token, build_path(args.project, args.ref, args.per_page))
        print_result(result)
        return 0
    except Exception as exc:
        return handle_error(exc)


if __name__ == "__main__":
    raise SystemExit(main())
