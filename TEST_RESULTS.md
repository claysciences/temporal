# Test results — 2026-09-06

Command: `./manage.sh all`

Final exit status: 0.

| Check | Result |
| --- | --- |
| Compose build and launch | PASS |
| Temporal cluster health | PASS — SERVING |
| UI HTTP GET on localhost:8233 | PASS |
| HelloAI normal workflow | PASS — Hello, Temporal AI!; attempt 1 |
| Transient activity retry | PASS — Hello, Temporal AI!; attempt 2 |
| Submission with worker stopped | PASS |
| Queued workflow completion after worker restart | PASS — Hello, Restart! |
| Results and history after Temporal restart | PASS — all three workflows, 17 events each |

Workflow IDs:

- `hello-ai-1788693577-hello`
- `hello-ai-1788693577-retry`
- `hello-ai-1788693577-queued`

Raw evidence is in `evidence/`. Temporal and the worker were left running. The storage initialization container successfully exited, as intended.

The AI activity is a local simulation, so these tests validate Temporal orchestration and recovery, not a real model/provider integration. This is a persistent local development server, not a production cluster.
