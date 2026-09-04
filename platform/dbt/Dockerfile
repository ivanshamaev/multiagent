FROM python:3.12.14-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DBT_PROFILES_DIR=/workspace

RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 dbt \
    && useradd --uid 1000 --gid 1000 --create-home dbt

COPY requirements.lock /tmp/requirements.lock
RUN python -m pip install --requirement /tmp/requirements.lock

USER dbt
WORKDIR /workspace

ENTRYPOINT ["dbt"]
