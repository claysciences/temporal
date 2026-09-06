#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
compose() { docker compose -f compose.yaml "$@"; }
case "${1:-all}" in
  all)
    if ! docker info >/dev/null 2>&1; then open -a Docker; fi
    for ((i=0; i<120; i++)); do
      if docker info >/dev/null 2>&1; then break; fi
      sleep 2
    done
    docker info >/dev/null
    compose config --quiet
    compose pull temporal
    compose build worker test
    compose up -d --force-recreate --wait --wait-timeout 180 temporal worker
    ./manage.sh test
    ;;
  test)
    mkdir -p evidence
    run_id="hello-ai-$(date +%s)"
    echo "$run_id" > evidence/latest-run.txt
    compose run --rm --no-deps test run "$run_id" | tee evidence/workflows.txt
    compose stop worker
    trap 'compose up -d worker' EXIT
    compose run --rm --no-deps test queue "$run_id" | tee evidence/queued.txt
    compose up -d --wait worker
    trap - EXIT
    compose restart temporal
    compose up -d --wait --wait-timeout 180 temporal worker
    compose run --rm --no-deps test verify "$run_id" | tee evidence/persistence.txt
    curl --fail --silent --output evidence/ui.html http://127.0.0.1:8233/
    compose exec -T temporal temporal operator cluster health --address 127.0.0.1:7233 | tee evidence/health.txt
    compose ps | tee evidence/services.txt
    docker image inspect temporalio/temporal:latest --format '{{json .RepoDigests}}' > evidence/temporal-image.json
    compose images > evidence/images.txt
    echo 'PASS: UI, health, workflows, retry, queued work, and restart persistence'
    ;;
  status) compose ps ;;
  hello)
    compose exec -T temporal temporal workflow execute --address temporal:7233 --type HelloAI --task-queue ai-orchestrator --workflow-id "hello-two-second-delay-$(date +%s)" --input '{"name":"World","retry":true}'
    ;;
  verify-worker)
    compose exec -T worker cat /app/app.py | cmp app.py -
    echo 'PASS: running container app.py matches local app.py byte-for-byte'
    compose exec -T worker python -c 'from pathlib import Path; cmd = Path("/proc/1/cmdline").read_bytes(); print("Worker process:", cmd.replace(b"\x00", b" ").decode()); assert b"app.py" in cmd'
    compose ps
    ;;
  logs) compose logs --tail 100 ;;
  inspect) docker image inspect temporalio/temporal:latest --format '{{json .Config}}'; compose run --rm --no-deps --entrypoint /bin/sh temporal -c 'id; ls -ld /data /home/temporal' ;;
  stop) compose down ;;
  *) echo 'Usage: ./manage.sh [all|hello|test|status|verify-worker|logs|stop]' >&2; exit 2 ;;
esac
