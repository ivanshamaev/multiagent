FROM apache/airflow:3.3.1-python3.12@sha256:b01a795dfbd113bbbfdf3ee169b8f27e9a0090ccef105f1a452b3594a11ed316

# Keep the Airflow dependency graph unchanged. dbt has its own interpreter path
# and site-packages; installation never occurs at task/container startup.
COPY platform/dbt/requirements.lock /tmp/dbt-requirements.lock
RUN python -m venv /opt/airflow/dbt-venv \
    && /opt/airflow/dbt-venv/bin/python -m pip install \
       --no-cache-dir --require-hashes -r /tmp/dbt-requirements.lock \
    && /opt/airflow/dbt-venv/bin/python -m pip check \
    && python -m pip check
COPY platform/airflow/requirements.lock /tmp/airflow-requirements.lock
RUN python -m pip install --no-cache-dir --no-deps --require-hashes \
       -r /tmp/airflow-requirements.lock \
    && python -m pip check
