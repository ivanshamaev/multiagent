CREATE USER IF NOT EXISTS mcp_reader
IDENTIFIED WITH sha256_password BY {mcp_reader_password:String};

ALTER USER mcp_reader
IDENTIFIED WITH sha256_password BY {mcp_reader_password:String};

REVOKE ALL ON *.* FROM mcp_reader;
GRANT SELECT ON raw.* TO mcp_reader;
GRANT SELECT ON analytics.* TO mcp_reader;

CREATE USER IF NOT EXISTS dbt_agent
IDENTIFIED WITH sha256_password BY {dbt_agent_password:String};

ALTER USER dbt_agent
IDENTIFIED WITH sha256_password BY {dbt_agent_password:String};

REVOKE ALL ON *.* FROM dbt_agent;
GRANT SELECT ON raw.* TO dbt_agent;
GRANT SELECT, INSERT, ALTER, CREATE TABLE, CREATE VIEW, DROP TABLE, DROP VIEW, TRUNCATE
ON analytics.* TO dbt_agent;
