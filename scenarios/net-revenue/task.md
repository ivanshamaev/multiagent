# Net Revenue by Country and Acquisition Channel

Implement a dbt mart exposed as `analytics.fct_net_revenue` for the hourly ecommerce pipeline.
Do not modify raw fixtures, connection profiles, dependency locks, Airflow policy code, or public
validation commands.

## Business contract

- Grain: one row per UTC `order_date`, `country`, normalized `acquisition_channel`, and `currency`.
- `gross_payment_amount_cents`: sum of every `succeeded` payment event. Split payments are distinct
  events and must both be counted.
- `successful_refund_amount_cents`: sum of every `succeeded` refund event, including partial,
  multiple, and late refunds; failed refunds do not count.
- `net_revenue_cents = gross_payment_amount_cents - successful_refund_amount_cents`. It must be a
  signed integer. Refunds are attributed to the original order's UTC date.
- Use the order's customer country. Deduplicate identical marketing attribution events by
  `attribution_event_id`; map a missing or NULL channel to `unknown`.
- Never combine currencies: `currency` is a required dimension because no FX rates are supplied.

## Required output

The `analytics.fct_net_revenue` relation must be a physical table with non-NULL columns:
`order_date`, `country`, `acquisition_channel`, `currency`, `gross_payment_amount_cents`,
`successful_refund_amount_cents`, and `net_revenue_cents`. Its declared grain must be unique.
Add dbt tests covering the grain, required fields, and the metric identity.

The existing `ecommerce_hourly` schedule already satisfies the hourly requirement and must remain
unchanged. Public validation runs the complete dbt project. An independent hidden grader checks
behavior and protected-path integrity; its SQL and expected results are unavailable in this
workspace.
