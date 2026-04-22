# Mark Core v2

Mark Core v2 is the new backend core for this repository. It is being built from the official documents in `contextos/` and does not reuse the old Mark Alfa backend as the implementation base.

## Current State

What is already working locally:

- FastAPI backend bootstrap in `src/backend/main.py`
- HTTP healthcheck at `/health`
- WebSocket channel at `/ws`
- Initial `sync_state` event on connect
- Protocol actions already implemented and validated:
  - `healthcheck`
  - `get_status`
  - `get_config`
  - `get_models`
  - `get_providers`
  - `get_credentials_status`
  - `change_model`
  - `change_provider`
  - `update_config`
  - `set_active_credential`
  - `add_custom_model`
  - `remove_custom_model`
  - `get_history`
  - `clear_session`
  - `execute_task`
  - `interrupt`
  - `shutdown_backend`
- Structured error responses for:
  - invalid payloads
  - unknown actions
- Centralized runtime path resolution with fallback support
- Session, history, and basic state persistence

## Stack

- Python 3.12
- FastAPI
- WebSocket
- asyncio-oriented backend flow
- SQLite for structured history/session-related persistence
- JSON files for lightweight runtime state
- Real Google AI API client for `google_ai`
- Real Vertex AI client for `vertex_ai`

## Repository Layout

- Official docs: `contextos/`
- Operational TODO: `contextos/TODOList.md`
- Backend code: `src/backend/`
- Backend dependencies: `requirements-backend.txt`

Important official documents:

- `contextos/01-arquitetura-mark-core-v2.md`
- `contextos/02-contrato-operacional-mark-core-v2.md`
- `contextos/03-roadmap-de-implementacao-mark-core-v2.md`
- `contextos/04-contrato-json-mark-core-v2.md`
- `contextos/05-estrutura-de-diretorios-mark-core-v2.md`
- `contextos/06-politica-de-providers-modelos-e-credenciais.md`
- `contextos/07-guia-de-implementacao-fase-1-mark-core-v2.md`

## Local Setup

Create and activate a virtual environment from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r requirements-backend.txt
```

If you are reusing the existing workspace `.venv`, you can activate that one instead of creating a fresh environment.

## Run the Backend

Start the API locally with Uvicorn:

```bash
source .venv/bin/activate
uvicorn src.backend.main:app --reload --host 127.0.0.1 --port 8000
```

Healthcheck:

- `GET http://127.0.0.1:8000/health`

WebSocket:

- `ws://127.0.0.1:8000/ws`

## Test the Current WebSocket

Run this from the repository root after activating `.venv`:

```bash
python - <<'PY'
from fastapi.testclient import TestClient
from src.backend.main import create_app

client = TestClient(create_app())
with client.websocket_connect('/ws') as ws:
    print(ws.receive_json())
    print(ws.receive_json())

    ws.send_json({"protocol_version": "2.0", "action": "healthcheck", "payload": {}})
    print(ws.receive_json())

    ws.send_json({"protocol_version": "2.0", "action": "get_status", "payload": {}})
    print(ws.receive_json())

    ws.send_json({"protocol_version": "2.0", "action": "get_config", "payload": {}})
    print(ws.receive_json())

    ws.send_json({"protocol_version": "2.0", "action": "get_history", "payload": {}})
    print(ws.receive_json())

    ws.send_json({"protocol_version": "2.0", "action": "clear_session", "payload": {}})
    print(ws.receive_json())
    print(ws.receive_json())
PY
```

## Environment Variables

These are the runtime variables the backend is expected to use:

- `GOOGLE_API_KEY` for Google AI API
- `GOOGLE_APPLICATION_CREDENTIALS` for Vertex AI service account credentials
- `VERTEXAI_PROJECT` for the Vertex AI project id
- `VERTEXAI_LOCATION` for the Vertex AI region/location
- `MARK_STATE_DIR` to override the writable runtime directory

## Runtime Path Behavior

The backend now resolves runtime storage through a central runtime layer instead of doing path handling inside the WebSocket handler.

Resolution order:

1. `MARK_STATE_DIR`, if defined and writable
2. `/var/lib/jarvis-mark/estado`, if writable
3. `.mark-runtime/estado` inside the repository workspace as a local fallback

This directory is used for state, session, history, provider metadata, and model metadata persistence.

The backend also loads `src/backend/product_config/initial_rules.txt` on boot and exposes its path in `sync_state.state.paths.rules_file`. That content is the initial context for the minimal task execution flow.

## Protocol Status

The WebSocket currently emits `sync_state` on connect and handles these actions:

- `healthcheck`
- `get_status`
- `get_config`
- `get_models`
- `get_providers`
- `get_credentials_status`
- `change_model`
- `change_provider`
- `update_config`
- `set_active_credential`
- `add_custom_model`
- `remove_custom_model`
- `get_history`
- `clear_session`
- `execute_task`
- `interrupt`
- `shutdown_backend`

Remaining work now sits in the later tooling and provider integration layers.

## Provider Execution Path

The `execute_task` action now uses the active `provider` and `model` from backend state and routes execution through the real provider clients:

- `google_ai` via `src/backend/models/providers/google_ai_client.py`
- `vertex_ai` via `src/backend/models/providers/vertex_ai_client.py`

Routing is resolved through:

- `src/backend/models/registry.py` for builtin/custom catalog and model metadata
- `src/backend/models/router.py` for `model_id -> provider`

Credential resolution behavior:

- `google_ai`: active credential from runtime store, fallback to `GOOGLE_API_KEY`
- `vertex_ai`: active credential from runtime store, fallback to `GOOGLE_APPLICATION_CREDENTIALS` + `VERTEXAI_PROJECT` + `VERTEXAI_LOCATION`

`change_provider` now fails with structured error when the target provider has no configured credential.

Provider failures are normalized and surfaced as structured protocol errors, including at least:

- `AUTHENTICATION_FAILED`
- `RATE_LIMIT`
- `QUOTA_EXCEEDED`
- `PROJECT_INVALID`
- `REGION_INVALID`
- `MODEL_NOT_FOUND`

The current backend has been validated with real positive WebSocket `execute_task` inference for both providers using the active environment variables.

## Working Notes

- The operational TODO is in `contextos/TODOList.md`.
- The official source documents are all under `contextos/`.
- No frontend redesign is being done in this phase.
- The backend is being developed incrementally and validated locally after each real item.
