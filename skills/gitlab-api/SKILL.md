---
name: gitlab-api
description: Read GitLab data through REST API to fetch merge request details, merge request changes, merge request notes, or repository file metadata/content by project ID/path and merge request IID.
---

# gitlab-api

Use method-specific scripts in `scripts/` to call GitLab REST API with credentials from `.env`.

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
python scripts/mr.py --project 123 --iid 45
python scripts/changes.py --project group%2Fproject --iid 45
python scripts/notes.py --project 123 --iid 45
python scripts/create_note.py --project 123 --iid 45 --body "string"
python scripts/file.py --project 123 --file-path path/to/file.py --ref main
```

## Implementation Notes

- Return parsed JSON with pretty formatting.
- Send `PRIVATE-TOKEN` header for authentication.
- URL-encode project and file path safely.
- Fail with clear HTTP error text and status code.
- `create_note.py` posts form field `body` to `POST /projects/:id/merge_requests/:merge_request_iid/notes`.
