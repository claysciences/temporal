import asyncio
import json
import os
import sys
from datetime import timedelta
from temporalio.client import Client
from app import HelloAI, TASK_QUEUE


async def main():
    mode, prefix = sys.argv[1:3]
    client = await Client.connect(os.getenv("TEMPORAL_ADDRESS", "localhost:7233"))
    if mode == "run":
        for suffix, retry in [("hello", False), ("retry", True)]:
            result = await client.execute_workflow(
                HelloAI.run, {"name": " Temporal AI ", "retry": retry},
                id=f"{prefix}-{suffix}", task_queue=TASK_QUEUE,
                execution_timeout=timedelta(seconds=90))
            assert result == {"message": "Hello, Temporal AI!", "attempt": 2 if retry else 1,
                              "provider": "local-simulation"}, result
            print(json.dumps({"test": suffix, "result": result, "status": "PASS"}))
    elif mode == "queue":
        await client.start_workflow(HelloAI.run, {"name": "Restart"},
                                    id=f"{prefix}-queued", task_queue=TASK_QUEUE,
                                    execution_timeout=timedelta(seconds=180))
        print("PASS: workflow submitted while worker stopped")
    elif mode == "verify":
        for suffix, name in [("hello", "Temporal AI"), ("retry", "Temporal AI"), ("queued", "Restart")]:
            handle = client.get_workflow_handle(f"{prefix}-{suffix}")
            result = await asyncio.wait_for(handle.result(), timeout=90)
            assert result["message"] == f"Hello, {name}!", result
            events = [event async for event in handle.fetch_history_events()]
            assert len(events) > 5
            prepared = next(e for e in events if e.HasField("activity_task_completed_event_attributes"))
            ai_scheduled = next(e for e in events
                                if e.HasField("activity_task_scheduled_event_attributes")
                                and e.activity_task_scheduled_event_attributes.activity_type.name == "simulated_ai")
            gap = (ai_scheduled.event_time.ToDatetime() - prepared.event_time.ToDatetime()).total_seconds()
            assert gap >= 2, f"Activity steps only {gap}s apart"
            timers = [e for e in events if e.HasField("timer_started_event_attributes")]
            assert any(e.timer_started_event_attributes.start_to_fire_timeout.seconds == 2 for e in timers)
            print(f"PASS: durable two-second step delay ({gap:.3f}s observed)")
            print(f"PASS: {prefix}-{suffix}: result and {len(events)} history events persisted")
    else:
        raise ValueError(mode)


asyncio.run(main())
