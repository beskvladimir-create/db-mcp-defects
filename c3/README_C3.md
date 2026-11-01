# RQ5: schema audit against the Gemma 4 chat template

Date: 2026-11-01. Client: `scripts/mcp_tools_list.py` (stdio; initialize with protocol 2025-06-18, then paginated
tools/list). Template: `gemma4_v5.jinja` = huggingface/trl commit a03b8fe, `trl/chat_templates/gemma4_v5.jinja`,
described there as the template shipped with `google/gemma-4-E2B-it` at revision 8995379 (header: "Google Gemma 4
Canonical Chat Template", published 2026-07-09); sha256 0a2c8073c878ab1da004bee933a998606537bbb62016310352c7285c3f01c5b5.
The parameter-rendering logic (`standard_keys`, `format_parameters`) was also compared with
huggingface.co/google/gemma-4-31B-it/raw/main/chat_template.jinja via a web reader (same keys read).

## What is measured

`scripts/c3_schema_audit.py` renders every tool through the template, once with the raw `inputSchema` and once after
`normalise()` (proposed check C3: `anyOf`/`oneOf` of one type plus null -> that type with `nullable: true`; list types
`[T, "null"]` -> `T` + `nullable`; local `$ref` inlined from `$defs`). A tool is counted as *type or structure lost* if a
parameter has a union or `$ref`, no single string type, a `$ref` inside `items`, an object without `properties`
(the template then prints the object's own keys such as `additionalProperties` as parameters), or an empty rendered
type field. Unions inside `items` are emitted verbatim by the template and are counted separately
(`items_union_passthrough`), not as lost. Undescribed parameters are a property of the server, not a template loss.

## Commands that produced tools/*.json (25 attempts, 18 succeeded) (latest packages resolved by npx/uvx on 2026-11-01)

| File | Command (environment) | Result |
|---|---|---|
| bytebase__dbhub | `npx -y @bytebase/dbhub --demo --transport stdio` | ok |
| mongodb-js__mongodb-mcp-server | `npx -y mongodb-mcp-server` (no connection string; default tool set) | ok |
| executeautomation__mcp-database-server | `npx -y @executeautomation/database-server x.db` | ok |
| ClickHouse__mcp-clickhouse | `uvx mcp-clickhouse` (dummy CLICKHOUSE_HOST/USER/PASSWORD) | ok |
| motherduckdb__mcp-server-motherduck | `uvx mcp-server-motherduck --db-path :memory: --read-write` | ok |
| chroma-core__chroma-mcp | `uvx --with 'pydantic<2.12' chroma-mcp --client-type ephemeral` (fails without the pin) | ok |
| redis__mcp-redis | `uvx --from redis-mcp-server redis-mcp-server --url redis://localhost:6379` | ok |
| neo4j-contrib__mcp-neo4j__cypher / __data-modeling / __aura-manager | `uvx mcp-neo4j-cypher`, `uvx mcp-neo4j-data-modeling`, `uvx mcp-neo4j-aura-manager` (dummy credentials) | ok |
| neo4j-contrib__mcp-neo4j__memory | `uvx mcp-neo4j-memory` | failed: connects to Neo4j at start-up |
| designcomputer__mysql_mcp_server | `uvx mysql_mcp_server` (dummy MYSQL_*) | ok |
| RichardHan__mssql_mcp_server | `uvx --with 'mcp<2' --from microsoft_sql_server_mcp mssql_mcp_server` | ok (fails with mcp 2.x) |
| runekaagaard__mcp-alchemy | `uvx --with 'mcp<2' --with sqlalchemy mcp-alchemy` (DB_URL sqlite) | ok (fails with mcp 2.x) |
| alexander-zuev__supabase-mcp-server | `uvx --with 'mcp<2' --from supabase-mcp-server supabase-mcp-server` (dummy SUPABASE_*) | ok |
| cr7258__elasticsearch-mcp-server | `uvx elasticsearch-mcp-server` (dummy ELASTICSEARCH_*) | ok |
| Anarkh-Lee__universal-db-mcp | `npx -y universal-db-mcp --type sqlite --file x.db` | ok |
| googleapis__mcp-toolbox__postgres | `npx -y @toolbox-sdk/server --prebuilt postgres --stdio` against a local PostgreSQL 16 | ok |
| googleapis__mcp-toolbox__sqlite | `npx -y @toolbox-sdk/server --prebuilt sqlite --stdio` | ok |
| crystaldba__postgres-mcp | `uvx --from postgres-mcp==0.3.0 ...` | failed: dependency pglast==7.2.0 not installable here (an older cached 0.1.0 with one tool was not used) |
| supabase__mcp | `npx -y @supabase/mcp-server-supabase --access-token <dummy>` | failed: tools/list fetches from the Supabase API |
| neondatabase__mcp-server-neon | `npx -y @neondatabase/mcp-server-neon start <dummy>` | failed: a git-hosted dependency blocked by the network policy |
| benborla__mcp-server-mysql | `npx -y @benborla29/mcp-server-mysql` | failed: needs a MySQL server at start-up |
| qdrant__mcp-server-qdrant | `uvx mcp-server-qdrant` (local path) | failed: embedding model download blocked |
| Snowflake-Labs__mcp | `uvx snowflake-labs-mcp --service-config-file sf.yaml ...` | failed: connects to Snowflake at start-up |
| neo4j/mcp, FreePeak/db-mcp-server, centralmind/gateway, subnetmarco/pgmcp | `go install ...` | not built: Go module proxy unreachable |
| elastic/mcp-server-elasticsearch | — | not attempted (Rust / container image) |

Several Python servers report the MCP SDK version (1.30.0) as their server version; the package version is the latest
on PyPI on the collection date. The mongodb server was run without a connection, so tools that appear only after
connecting are not included.
