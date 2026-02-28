---
name: gitlab-api
description: Read GitLab data through REST API to fetch merge request details, merge request changes, merge request notes, or repository file metadata/content by project ID/path and merge request IID.
---

# gitlab-api

Use `scripts/gitlab_api.py` to call GitLab REST API with credentials from `.env`.

## Configure

Create `.env` in the current working directory (where you run the command), or pass values from environment variables.

Expected keys:

```env
gitlab_server=
access_token=
```

Supported aliases:
- `gitlab_server` or `GITLAB_SERVER`
- `access_token` or `ACCESS_TOKEN` or `GITLAB_TOKEN`

## Run

Use one command per API method.

```bash
python scripts/gitlab_api.py mr --project 123 --iid 45
python scripts/gitlab_api.py changes --project group%2Fproject --iid 45
python scripts/gitlab_api.py notes --project 123 --iid 45
python scripts/gitlab_api.py note-create --project 123 --iid 45 --body "string"
python scripts/gitlab_api.py file --project 123 --file-path path/to/file.py --ref main
```

## Method Mapping

- `mr` -> `GET /projects/:id/merge_requests/:merge_request_iid`
- `changes` -> `GET /projects/:id/merge_requests/:merge_request_iid/changes`
- `notes` -> `GET /projects/:id/merge_requests/:merge_request_iid/notes`
- `note-create` -> `POST /projects/:id/merge_requests/:merge_request_iid/notes` (requires `body`)
- `file` -> `GET /projects/:id/repository/files/:file_path` (requires `ref`)

## Implementation Notes

- Return parsed JSON with pretty formatting.
- Send `PRIVATE-TOKEN` header for authentication.
- URL-encode project and file path safely.
- Fail with clear HTTP error text and status code.
