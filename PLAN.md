# Self-hosted Temporal implementation plan

1. Inspect Docker and existing workspace instructions. Docker Desktop is installed but stopped; its CLI is not on PATH.
2. Create an isolated `temporal-orchestrator` directory with Compose, a Python worker, and integration tests.
3. Run the official open-source `temporalio/temporal` development server with SQLite persisted in a named Docker volume. Bind gRPC 7233 and UI 8233 to localhost only. This is a development environment, not a production cluster.
4. Build a Python SDK worker with a hello-world orchestration: prepare input, execute a simulated AI activity, and return its result. Demonstrate retries without credentials or external AI calls.
5. Launch Docker Desktop if needed, pull images, build the worker, wait for health, and execute success/retry tests.
6. Restart the worker and server and verify workflow history survives. Leave healthy services running.
7. Save evidence and instructions, including start, test, logs, and stop commands.

## Up-front permission scope

Request execution of the project-local `manage.sh` script outside the sandbox, with a reusable permission for this script. It starts the installed Docker Desktop, downloads public images and Python dependencies, builds this project's worker image, creates this project's network/containers/named volume, binds localhost ports 7233/8233, runs test containers, and restarts this project's services. It can inspect status/logs and stop this project without deleting its volume. No system package installation, paid service, credentials, unrelated container changes, or data deletion is planned. Docker Desktop may require interactive first-run setup if it has never been initialized; that cannot be preapproved through a shell permission.

## Acceptance criteria

- Temporal health check and UI HTTP request pass.
- Worker completes an actual Temporal workflow with an asserted result.
- A deliberately transient activity fails once and succeeds on retry.
- A workflow queued while the worker is stopped completes after restart.
- Completed workflow results remain available after server restart.
- Document resolved image identities and test output.

## Sources

- https://github.com/temporalio/cli (official Docker image and development server)
- https://github.com/temporalio/temporal (open-source server)
- https://github.com/temporalio/sdk-python (Python SDK)

## Completion — 2026-09-06

All acceptance criteria passed. Docker Desktop was started using the single saved management-script permission. Added a one-time storage initializer to assign the named volume to Temporal UID/GID 1000; the server remains unprivileged. Both Temporal and the worker are running. Test run `hello-ai-1788693577` verified normal execution, second-attempt retry, worker outage recovery, and persisted results/history after server restart. Cluster health returned `SERVING`; UI HTTP request succeeded. See `evidence/` and `README.md`.
