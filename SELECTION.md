# Repository selection (collected 2026-11-01)

## Repository searches (GitHub search API, `search/repositories`, first page of 50 results per query)

Each query string below was combined with ` in:name,description,topics stars:>=150`:

1. `mcp server postgres`
2. `mcp server mysql`
3. `mcp server sql`
4. `mcp database`
5. `mcp server sqlite`
6. `mcp bigquery`
7. `mcp clickhouse`
8. `mcp snowflake`
9. `mcp mongodb`
10. `mcp duckdb`
11. `mcp redis`
12. `mcp supabase`
13. `mcp server oracle`
14. `mcp sql server mssql`
15. `mcp elasticsearch`
16. `mcp neo4j`

Union of results: 155 repositories (`raw/repo_candidates.tsv`). Only the first page (up to 50 results) of each
query was read; repositories ranked lower by GitHub search are not in the candidate list.

## Named checks

18 repositories were looked up by name with `repo:` qualifiers in one repository search:
crystaldba/postgres-mcp, qdrant/mcp-server-qdrant, modelcontextprotocol/servers-archived, awslabs/mcp,
LucasHild/mcp-server-bigquery, StarRocks/mcp-server-starrocks, Couchbase-Ecosystem/mcp-server-couchbase,
milvus-io/mcp-server-milvus, singlestore-labs/mcp-server-singlestore, tinybirdco/mcp-tinybird,
pinecone-io/pinecone-mcp, isaacwasserman/mcp-snowflake-server, datastax/astra-db-mcp, yugabyte/yugabytedb-mcp-server,
MariaDB/mcp, opensearch-project/opensearch-mcp-server-py, influxdata/influxdb3_mcp_server, modelcontextprotocol/servers.
Two qualified (crystaldba/postgres-mcp, qdrant/mcp-server-qdrant); the rest had fewer than 300 stars or are
multi-server repositories (see `repo_selection.csv`).

## Inclusion rule

Primary purpose is an MCP server that exposes a user's own database, warehouse, search or vector store to LLM agents;
at least 300 stars on 2026-11-01. Every candidate with at least 300 stars and its decision is listed in
`repo_selection.csv` with an exclusion code:

| Code | Meaning |
|---|---|
| engine_or_platform | database engine, query engine, API builder, BI/ETL or agent platform whose MCP interface is secondary (e.g. dosco/graphjin, julien040/anyquery, Azure/data-api-builder, orneryd/NornicDB) |
| client_or_ide | database client, IDE or GUI |
| memory | agent memory or knowledge store that uses a database internally |
| domain_app | server or app over a fixed application dataset rather than a user's database |
| docs | documentation or skills server (timescale/pg-aiguide) |
| mixed_suite | repository of many MCP servers, mostly non-database (oracle/mcp, awslabs/mcp, modelcontextprotocol/servers) |
| unrelated | keyword match only |
| tutorial | tutorial, template or demo |

These decisions are a single judgement made from repository descriptions; they are released so that they can be
contested.
