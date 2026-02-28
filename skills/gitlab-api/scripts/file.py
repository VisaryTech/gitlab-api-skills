#!/usr/bin/env python3
import argparse
from pathlib import Path
from urllib.parse import urlencode

from common import call_gitlab, encode_component, handle_error, print_result, resolve_credentials


def build_path(project: str, file_path: str, ref: str) -> str:
    query = urlencode({"ref": ref})
    return f"/api/v4/projects/{encode_component(project)}/repository/files/{encode_component(file_path)}?{query}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Get GitLab repository file metadata/content.")
    parser.add_argument("--project", required=True, help="Project ID or path (for path use group/project).")
    parser.add_argument("--file-path", required=True, help="Repository file path.")
    parser.add_argument("--ref", required=True, help="Git ref (branch/tag/commit).")
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
        result = call_gitlab(base_url, token, build_path(args.project, args.file_path, args.ref))
        print_result(result)
        return 0
    except Exception as exc:
        return handle_error(exc)


if __name__ == "__main__":
    raise SystemExit(main())

