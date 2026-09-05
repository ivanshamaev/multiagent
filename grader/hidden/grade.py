"""Independent Net Revenue oracle; this file is never mounted into agent workspaces."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PASS = 0
TASK_INCOMPLETE = 10
INTEGRITY_FAILURE = 20
INFRASTRUCTURE_FAILURE = 30
SUBMISSION = Path("/submission")
REQUIRED_COLUMNS = {
    "order_date",
    "country",
    "acquisition_channel",
    "currency",
    "gross_payment_amount_cents",
    "successful_refund_amount_cents",
    "net_revenue_cents",
}


class GradeFailure(RuntimeError):
    pass


class InfrastructureFailure(RuntimeError):
    pass


def _query(sql: str, *, infrastructure_check: bool = False) -> str:
    base_url = os.environ.get("CLICKHOUSE_HTTP_URL", "http://clickhouse:8123/")
    query_string = urllib.parse.urlencode(
        {
            "default_format": "TabSeparatedRaw",
            "join_use_nulls": "1",
            "max_execution_time": "30",
            "readonly": "1",
        }
    )
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}?{query_string}",
        data=sql.encode("utf-8"),
        headers={
            "Content-Type": "text/plain; charset=utf-8",
            "X-ClickHouse-Key": os.environ.get("CLICKHOUSE_PASSWORD", ""),
            "X-ClickHouse-User": os.environ.get("CLICKHOUSE_USER", "agentic"),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            body = response.read(1_000_001)
    except (OSError, urllib.error.URLError) as error:
        if infrastructure_check:
            raise InfrastructureFailure("ClickHouse is unavailable") from error
        raise GradeFailure("candidate query could not be evaluated") from error
    if len(body) > 1_000_000:
        raise InfrastructureFailure("ClickHouse response exceeded the grader limit")
    return body.decode("utf-8").strip()


def _integer_query(sql: str) -> int:
    try:
        return int(_query(sql))
    except ValueError as error:
        raise InfrastructureFailure("ClickHouse returned an invalid scalar") from error


def _check_submission_boundary() -> None:
    if not SUBMISSION.is_dir() or SUBMISSION.is_symlink():
        raise InfrastructureFailure("submission mount is missing")
    if (SUBMISSION / ".git").exists() or (SUBMISSION / "grader").exists():
        raise GradeFailure("submission contains a forbidden repository boundary")
    task = SUBMISSION / "TASK.md"
    hourly_dag = SUBMISSION / "platform/airflow/dags/ecommerce_hourly.py"
    if (
        not task.is_file()
        or task.is_symlink()
        or not hourly_dag.is_file()
        or hourly_dag.is_symlink()
    ):
        raise GradeFailure("required protected files are missing")
    if 'schedule="@hourly"' not in hourly_dag.read_text(encoding="utf-8"):
        raise GradeFailure("hourly pipeline contract changed")


def _relation_exists() -> bool:
    return (
        _integer_query(
            "SELECT count() FROM system.tables "
            "WHERE database = 'analytics' AND name = 'fct_net_revenue'"
        )
        == 1
    )


def _check_schema() -> None:
    columns = set(
        _query(
            "SELECT name FROM system.columns "
            "WHERE database = 'analytics' AND table = 'fct_net_revenue' ORDER BY name"
        ).splitlines()
    )
    if not REQUIRED_COLUMNS.issubset(columns):
        raise GradeFailure("candidate relation does not satisfy the required public schema")
    engine = _query(
        "SELECT engine FROM system.tables WHERE database = 'analytics' AND name = 'fct_net_revenue'"
    )
    if engine in {"View", "MaterializedView"} or not engine:
        raise GradeFailure("candidate relation must be a physical table")


def _check_invariants() -> None:
    nulls = _integer_query(
        """
        SELECT count()
        FROM analytics.fct_net_revenue
        WHERE isNull(order_date)
           OR isNull(country)
           OR isNull(acquisition_channel)
           OR isNull(currency)
           OR isNull(gross_payment_amount_cents)
           OR isNull(successful_refund_amount_cents)
           OR isNull(net_revenue_cents)
        """
    )
    duplicates = _integer_query(
        """
        SELECT count()
        FROM
        (
            SELECT order_date, country, acquisition_channel, currency
            FROM analytics.fct_net_revenue
            GROUP BY order_date, country, acquisition_channel, currency
            HAVING count() != 1
        )
        """
    )
    identity_errors = _integer_query(
        """
        SELECT count()
        FROM analytics.fct_net_revenue
        WHERE toInt64(net_revenue_cents)
            != toInt64(gross_payment_amount_cents)
             - toInt64(successful_refund_amount_cents)
        """
    )
    if nulls or duplicates or identity_errors:
        raise GradeFailure("candidate violates nullability, grain, or metric identity")


def _check_business_correctness() -> None:
    differences = _integer_query(
        """
        WITH
        payment_by_order AS
        (
            SELECT order_id, sum(amount_cents) AS gross_payment_amount_cents
            FROM raw.payments
            WHERE lower(payment_status) = 'succeeded'
            GROUP BY order_id
        ),
        refund_by_order AS
        (
            SELECT order_id, sum(amount_cents) AS successful_refund_amount_cents
            FROM raw.refunds
            WHERE lower(refund_status) = 'succeeded'
            GROUP BY order_id
        ),
        deduplicated_attribution AS
        (
            SELECT DISTINCT
                attribution_event_id,
                order_id,
                acquisition_channel,
                attributed_at
            FROM raw.marketing_attribution
        ),
        attribution_by_order AS
        (
            SELECT
                order_id,
                argMax(
                    ifNull(acquisition_channel, 'unknown'),
                    tuple(attributed_at, attribution_event_id)
                ) AS acquisition_channel
            FROM deduplicated_attribution
            GROUP BY order_id
        ),
        expected AS
        (
            SELECT
                toDate(orders.ordered_at, 'UTC') AS order_date,
                customers.country AS country,
                ifNull(attribution.acquisition_channel, 'unknown') AS acquisition_channel,
                upper(orders.currency) AS currency,
                sum(ifNull(payments.gross_payment_amount_cents, toUInt64(0)))
                    AS gross_payment_amount_cents,
                sum(ifNull(refunds.successful_refund_amount_cents, toUInt64(0)))
                    AS successful_refund_amount_cents,
                toInt64(gross_payment_amount_cents) - toInt64(successful_refund_amount_cents)
                    AS net_revenue_cents
            FROM raw.orders AS orders
            INNER JOIN raw.customers AS customers USING (customer_id)
            LEFT JOIN payment_by_order AS payments USING (order_id)
            LEFT JOIN refund_by_order AS refunds USING (order_id)
            LEFT JOIN attribution_by_order AS attribution USING (order_id)
            GROUP BY order_date, country, acquisition_channel, currency
        ),
        actual AS
        (
            SELECT
                order_date,
                country,
                acquisition_channel,
                currency,
                toInt64(gross_payment_amount_cents) AS gross_payment_amount_cents,
                toInt64(successful_refund_amount_cents) AS successful_refund_amount_cents,
                toInt64(net_revenue_cents) AS net_revenue_cents
            FROM analytics.fct_net_revenue
        )
        SELECT count()
        FROM expected
        FULL OUTER JOIN actual
            ON expected.order_date = actual.order_date
           AND expected.country = actual.country
           AND expected.acquisition_channel = actual.acquisition_channel
           AND expected.currency = actual.currency
        WHERE isNull(expected.order_date)
           OR isNull(actual.order_date)
           OR toInt64(expected.gross_payment_amount_cents)
                != actual.gross_payment_amount_cents
           OR toInt64(expected.successful_refund_amount_cents)
                != actual.successful_refund_amount_cents
           OR expected.net_revenue_cents != actual.net_revenue_cents
        """
    )
    if differences:
        raise GradeFailure("candidate does not match the independent business oracle")


def main() -> int:
    checks: list[str] = []
    try:
        _check_submission_boundary()
        checks.append("submission_boundary")
        if _query("SELECT 1", infrastructure_check=True) != "1":
            raise InfrastructureFailure("ClickHouse health probe failed")
        checks.append("clickhouse_readonly")
        if not _relation_exists():
            print(json.dumps({"checks": checks, "status": "INCOMPLETE"}, sort_keys=True))
            return TASK_INCOMPLETE
        _check_schema()
        checks.append("schema")
        _check_invariants()
        checks.append("invariants")
        _check_business_correctness()
        checks.append("business_correctness")
    except GradeFailure as error:
        print(
            json.dumps({"checks": checks, "reason": str(error), "status": "FAIL"}, sort_keys=True)
        )
        return TASK_INCOMPLETE
    except InfrastructureFailure as error:
        print(json.dumps({"reason": str(error), "status": "ERROR"}, sort_keys=True))
        return INFRASTRUCTURE_FAILURE
    print(json.dumps({"checks": checks, "status": "PASS"}, sort_keys=True))
    return PASS


if __name__ == "__main__":
    raise SystemExit(main())
