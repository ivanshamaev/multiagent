"""Create an out-of-band approval for one controlled local Airflow trigger."""

from __future__ import annotations

import argparse
import json
import sys

from runtime.scenario_harness import REPOSITORY_ROOT
from runtime.tools.airflow_approval import AirflowApprovalError, AirflowApprovalStore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--idempotency-key", required=True)
    parser.add_argument("--approved-by", required=True)
    parser.add_argument("--dag", default="ecommerce_acceptance")
    parser.add_argument("--ttl-seconds", type=int, default=300)
    args = parser.parse_args(argv)
    try:
        approval = AirflowApprovalStore(REPOSITORY_ROOT).create(
            task_id=args.task_id,
            dag_id=args.dag,
            idempotency_key=args.idempotency_key,
            approved_by=args.approved_by,
            ttl_seconds=args.ttl_seconds,
        )
    except AirflowApprovalError as error:
        print(json.dumps({"error": str(error), "status": "DENIED"}, sort_keys=True))
        return 1
    print(
        json.dumps(
            {
                "approval_id": approval.approval_id,
                "dag_id": approval.dag_id,
                "expires_at": approval.expires_at.isoformat(),
                "status": "APPROVED",
                "task_id": approval.task_id,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
