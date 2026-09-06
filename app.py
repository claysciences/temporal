import asyncio
import os
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError
from temporalio.worker import Worker

TASK_QUEUE = "ai-orchestrator"


@activity.defn
async def prepare(name: str) -> str:
    return name.strip() or "World"


@activity.defn
async def simulated_ai(request: dict) -> dict:
    attempt = activity.info().attempt
    if request.get("retry") and attempt == 1:
        raise ApplicationError("Simulated transient model failure")
    # Replace this activity body with a model call when integrating an AI provider.
    return {"message": f"Hello, {request['name']}!", "attempt": attempt,
            "provider": "local-simulation"}


@workflow.defn
class HelloAI:
    @workflow.run
    async def run(self, request: dict) -> dict:
        name = await workflow.execute_activity(
            prepare, request["name"], start_to_close_timeout=timedelta(seconds=10))
        # Durable timer: the pause survives worker/server restarts.
        # Preserve replay compatibility with histories created before this change.
        if workflow.patched("two-second-step-delay"):
            await workflow.sleep(timedelta(seconds=2))
        return await workflow.execute_activity(
            simulated_ai, {"name": name, "retry": request.get("retry", False)},
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=2),
                                     maximum_interval=timedelta(seconds=2),
                                     maximum_attempts=3))


async def main():
    client = await Client.connect(os.getenv("TEMPORAL_ADDRESS", "localhost:7233"))
    worker = Worker(client, task_queue=TASK_QUEUE, workflows=[HelloAI],
                    activities=[prepare, simulated_ai])
    print(f"Worker ready on {TASK_QUEUE}", flush=True)
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
