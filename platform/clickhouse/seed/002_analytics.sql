-- Derived state is rebuilt by dbt; reset it independently from the raw seed.
DROP DATABASE IF EXISTS analytics SYNC;
CREATE DATABASE analytics;
