# Local Temporal AI orchestration example

Runs the official open-source Temporal server in Docker with an embedded UI and SQLite storage in the `temporal-ai-orchestrator_temporal-data` named volume. A separate Python worker executes a real Temporal workflow containing input preparation and a simulated AI activity. No Temporal Cloud account or API key is used.

This uses Temporal's development server: suitable for local orchestration experiments, not a production deployment. A production service needs a supported database deployment, authentication/TLS, backups, and operational configuration.

## Run

From this directory:

```sh
./manage.sh all     # start Docker if needed, build, launch, and test
./manage.sh test    # rerun tests; briefly restarts this project's services
./manage.sh status
./manage.sh hello   # execute a new workflow with a unique ID and print its history
./manage.sh logs
./manage.sh stop    # stop/remove project containers; retain workflow volume
```

The script supports Docker on PATH and the installed macOS Docker Desktop CLI. Starting a stopped Docker engine automatically requires macOS Docker Desktop.

- UI: http://localhost:8233
- Temporal gRPC address on host: `localhost:7233`
- Address inside the Compose network: `temporal:7233`
- Namespace: `default`
- Task queue: `ai-orchestrator`
- Workflow type: `HelloAI`

Both host ports bind only to loopback. The server and worker remain running after successful tests and have an `unless-stopped` restart policy.

## Submit a workflow

With Docker on PATH, run from this directory:

```sh
docker compose exec temporal temporal workflow execute \
  --address temporal:7233 --type HelloAI --task-queue ai-orchestrator \
  --workflow-id my-hello-ai-1 --input '{"name":"World","retry":true}'
```

Use a fresh workflow ID for each run. Expected result: `{"message":"Hello, World!","attempt":2,"provider":"local-simulation"}`. The first simulated model attempt deliberately fails when `retry` is true.

## Connect an AI orchestrator

Workflow activity steps are separated by a durable two-second Temporal timer. Simulated AI retries also wait two seconds between attempts. The timer survives restarts without blocking the worker's event loop.

`app.py` contains the `HelloAI` workflow and its activities. Replace `simulated_ai` with your model/tool integration; keep external I/O inside activities so Temporal can durably orchestrate and retry it. Configure credentials only when choosing an actual provider. Activities can execute more than once; use idempotency keys for side effects. This sample does not run an LLM.

## Tests and evidence

`test_workflow.py` asserts exact hello-world and retry results. `manage.sh test` submits a workflow while the worker is stopped, restores it, restarts Temporal, then checks all three results and their persisted event histories. It also checks cluster health and the UI HTTP endpoint. Artifacts are written to `evidence/`, including workflow IDs, test results, service status, and resolved image identities.

Initial image selection uses the official `temporalio/temporal:latest` image; the exact downloaded digest is recorded in `evidence/temporal-image.json`. The Python SDK is pinned in `requirements.txt`.

## Upstream sources

- [Temporal open-source server](https://github.com/temporalio/temporal)
- [Official CLI/server Docker instructions](https://github.com/temporalio/cli)
- [Official Python SDK](https://github.com/temporalio/sdk-python)

Implementation and up-front permissions are recorded in `PLAN.md`.
