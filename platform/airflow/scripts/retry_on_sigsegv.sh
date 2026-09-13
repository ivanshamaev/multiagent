#!/usr/bin/env bash
set -u

attempt=1
while true; do
    "$@" && exit 0
    status=$?
    if [[ ${status} -ne 139 || ${attempt} -ge 3 ]]; then
        exit "${status}"
    fi
    printf 'Airflow CLI received SIGSEGV; retrying (%s/3)\n' "${attempt}" >&2
    attempt=$((attempt + 1))
done
