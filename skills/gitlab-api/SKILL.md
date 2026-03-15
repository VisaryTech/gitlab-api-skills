---
name: gitlab-api
description: Read GitLab data through REST API to fetch merge request details/changes/notes, create notes, list pipeline runs, fetch pipeline details/jobs, or read repository file metadata/content.
---

# gitlab-api

Use method-specific scripts in `scripts/` to call GitLab REST API with credentials from `.env`.

## Configure

Create `.env` in the current working directory (where you run the command), or pass values from environment variables.

Expected keys:

```env
gitlab_server=
gitlab_access_token=
```

Supported aliases:
- `gitlab_server` or `GITLAB_SERVER`
- `gitlab_access_token` or `ACCESS_TOKEN` or `GITLAB_TOKEN`

## Run

Use one command per API method.

```bash
python scripts/mr.py --project 123 --iid 45
python scripts/changes.py --project group%2Fproject --iid 45
python scripts/notes.py --project 123 --iid 45
python scripts/create_note.py --project 123 --iid 45 --body "string"
python scripts/pipelines.py --project 123 --ref 7.3.0 --per-page 1
python scripts/pipeline.py --project 123 --pipeline-id 98765
python scripts/pipeline_jobs.py --project 123 --pipeline-id 98765
python scripts/pipeline_jobs.py --project 123 --pipeline-id 98765 --scope pending --scope running
python scripts/file.py --project 123 --file-path path/to/file.py --ref main
```

## Methods

### `mr.py`

- Purpose: get merge request details.
- Endpoint: `GET /api/v4/projects/:id/merge_requests/:iid`
- Required args: `--project`, `--iid`
- Use when you need MR status, title, author, source/target branches, and metadata.

### `changes.py`

- Purpose: get merge request details together with changed files and diff fragments.
- Endpoint: `GET /api/v4/projects/:id/merge_requests/:iid/changes`
- Required args: `--project`, `--iid`
- Use when you need the list of changed paths and patch content per file.

### `notes.py`

- Purpose: list merge request notes (discussion comments).
- Endpoint: `GET /api/v4/projects/:id/merge_requests/:iid/notes`
- Required args: `--project`, `--iid`
- Use when you need comment history for MR review context.

### `create_note.py`

- Purpose: create a new note in a merge request.
- Endpoint: `POST /api/v4/projects/:id/merge_requests/:iid/notes`
- Required args: `--project`, `--iid`, `--body`
- Request body format: form-encoded field `body=<text>`.
- Use when you need to publish an MR comment programmatically.

### `pipelines.py`

- Purpose: list pipelines for a specific ref.
- Endpoint: `GET /api/v4/projects/:id/pipelines`
- Required args: `--project`, `--ref`
- Optional args: `--per-page` (default: `1`)
- Query params sent: `ref`, `per_page`.
- Use when you need the latest pipeline IDs for a branch or tag.

### `pipeline.py`

- Purpose: get a single pipeline details by ID.
- Endpoint: `GET /api/v4/projects/:id/pipelines/:pipeline_id`
- Required args: `--project`, `--pipeline-id`
- Use when you need overall pipeline status, timestamps, and ref/sha details.

### `pipeline_jobs.py`

- Purpose: list jobs in a pipeline.
- Endpoint: `GET /api/v4/projects/:id/pipelines/:pipeline_id/jobs`
- Required args: `--project`, `--pipeline-id`
- Optional args: repeatable `--scope <status>` (mapped to `scope[]` query params).
- Allowed `--scope` values: `canceled`, `canceling`, `created`, `failed`, `manual`, `pending`, `preparing`, `running`, `scheduled`, `skipped`, `success`, `waiting_for_callback`, `waiting_for_resource`.
- Use when you need job-level status for CI diagnostics.

### `file.py`

- Purpose: get repository file metadata and content for a ref.
- Endpoint: `GET /api/v4/projects/:id/repository/files/:file_path`
- Required args: `--project`, `--file-path`, `--ref`
- Use when you need file blob metadata (`blob_id`, `last_commit_id`, etc.) and Base64 content from GitLab.

## Shared Behavior

- Return parsed JSON with pretty formatting.
- Send `PRIVATE-TOKEN` header for authentication.
- Resolve credentials from env vars first, then from `.env`.
- URL-encode project and file path safely and avoid double encoding.
- Fail with clear HTTP error text and status code.
- Return exit code `2` for argument/config errors (for example missing token/server), `1` for HTTP/network/runtime errors.
- Use `--env-file` in every script to override the default `.env` path when needed.
