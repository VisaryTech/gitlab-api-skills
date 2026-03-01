#!/usr/bin/env python3
import argparse
from pathlib import Path
from urllib.parse import urlencode

from common import call_gitlab, encode_component, handle_error, print_result, resolve_credentials


JOB_STATUSES = (
    "canceled",
    "canceling",
    "created",
    "failed",
    "manual",
    "pending",
    "preparing",
    "running",
    "scheduled",
    "skipped",
    "success",
    "waiting_for_callback",
    "waiting_for_resource",
)


def build_path(project: str, pipeline_id: str, scopes: list[str] | None = None) -> str:
    path = f"/api/v4/projects/{encode_component(project)}/pipelines/{pipeline_id}/jobs"
    if not scopes:
        return path
    query = urlencode({"scope[]": scopes}, doseq=True)
    return f"{path}?{query}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Get GitLab pipeline jobs.")
    parser.add_argument("--project", required=True, help="Project ID or path (for path use group/project).")
    parser.add_argument("--pipeline-id", required=True, help="Pipeline ID.")
    parser.add_argument(
        "--scope",
        action="append",
        choices=JOB_STATUSES,
        help="Filter by job status. Repeat option to pass multiple statuses.",
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
        result = call_gitlab(base_url, token, build_path(args.project, args.pipeline_id, args.scope))
        print_result(result)
        return 0
    except Exception as exc:
        return handle_error(exc)


if __name__ == "__main__":
    raise SystemExit(main())
