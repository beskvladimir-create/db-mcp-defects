# Appendix to "Silent, Unsafe or Misleading"

All numbers are produced by `scripts/analyze.py` (results.json, results_extra.json, results_round1.json).

## A. Sampling frame and sample by repository

Window: PRs created 2024-11-01..2026-10-31, merged by collection on 2026-11-01.

| Repository | Merged PRs | Fix-like | Auto-excl. | Frame | Sampled | Included |
|---|---:|---:|---:|---:|---:|---:|
| googleapis/mcp-toolbox | 2566 | 474 | 174 | 300 | 40 | 26 |
| mongodb-js/mongodb-mcp-server | 1145 | 192 | 25 | 167 | 40 | 26 |
| bytebase/dbhub | 215 | 77 | 2 | 75 | 40 | 37 |
| neondatabase/mcp-server-neon | 244 | 62 | 3 | 59 | 40 | 33 |
| supabase/mcp | 226 | 46 | 2 | 44 | 40 | 31 |
| FreePeak/db-mcp-server | 64 | 22 | 0 | 22 | 22 | 12 |
| neo4j-contrib/mcp-neo4j | 175 | 19 | 0 | 19 | 19 | 10 |
| redis/mcp-redis | 132 | 21 | 3 | 18 | 18 | 11 |
| Snowflake-Labs/mcp | 97 | 18 | 2 | 16 | 16 | 11 |
| neo4j/mcp | 280 | 16 | 1 | 15 | 15 | 6 |
| ClickHouse/mcp-clickhouse | 94 | 14 | 1 | 13 | 13 | 11 |
| cr7258/elasticsearch-mcp-server | 46 | 14 | 1 | 13 | 13 | 7 |
| crystaldba/postgres-mcp | 73 | 12 | 0 | 12 | 12 | 8 |
| alexander-zuev/supabase-mcp-server | 18 | 8 | 0 | 8 | 8 | 4 |
| benborla/mcp-server-mysql | 44 | 8 | 0 | 8 | 8 | 5 |
| motherduckdb/mcp-server-motherduck | 41 | 8 | 0 | 8 | 8 | 4 |
| elastic/mcp-server-elasticsearch | 128 | 19 | 14 | 5 | 5 | 3 |
| qdrant/mcp-server-qdrant | 49 | 6 | 1 | 5 | 5 | 3 |
| centralmind/gateway | 37 | 4 | 0 | 4 | 4 | 2 |
| designcomputer/mysql_mcp_server | 12 | 4 | 0 | 4 | 4 | 2 |
| chroma-core/chroma-mcp | 23 | 3 | 0 | 3 | 3 | 3 |
| subnetmarco/pgmcp | 6 | 3 | 1 | 2 | 2 | 0 |
| RichardHan/mssql_mcp_server | 7 | 1 | 0 | 1 | 1 | 1 |
| Anarkh-Lee/universal-db-mcp | 0 | 0 | 0 | 0 | 0 | 0 |
| executeautomation/mcp-database-server | 9 | 0 | 0 | 0 | 0 | 0 |
| runekaagaard/mcp-alchemy | 11 | 0 | 0 | 0 | 0 | 0 |
| **Total** | 5742 | 1051 | 230 | 821 | 376 | 256 |

## B. Agent-facing symptom examples (all included fixes with these symptoms)

### SILENT
- [ClickHouse/mcp-clickhouse#229](https://github.com/ClickHouse/mcp-clickhouse/pull/229) INPUT: page_size=0 returned empty page
- [FreePeak/db-mcp-server#36](https://github.com/FreePeak/db-mcp-server/pull/36) OUTPUT: result rendered in Go format not JSON
- [FreePeak/db-mcp-server#56](https://github.com/FreePeak/db-mcp-server/pull/56) CONFIG: sqlite path not unmarshalled -> empty db file created and used
- [FreePeak/db-mcp-server#66](https://github.com/FreePeak/db-mcp-server/pull/66) EXEC: regression fix of #63 (round-1 correction): identifier quoting in WHERE vs TEXT column -> column-not-found errors; ListHypertables flags silently false; not an injection
- [FreePeak/db-mcp-server#67](https://github.com/FreePeak/db-mcp-server/pull/67) OUTPUT: MCP envelope Go-stringified into text
- [Snowflake-Labs/mcp#175](https://github.com/Snowflake-Labs/mcp/pull/175) OUTPUT: agent API response parse -> always 'No final response found'
- [alexander-zuev/supabase-mcp-server#15](https://github.com/alexander-zuev/supabase-mcp-server/pull/15) INTROSPECT: get_tables omitted foreign tables and views
- [benborla/mcp-server-mysql#132](https://github.com/benborla/mcp-server-mysql/pull/132) OUTPUT: BIGINT precision loss
- [bytebase/dbhub#116](https://github.com/bytebase/dbhub/pull/116) SESSION: multi-source sqlite: all source_ids query last db
- [bytebase/dbhub#132](https://github.com/bytebase/dbhub/pull/132) SESSION: multi-source postgres same overwrite
- [bytebase/dbhub#364](https://github.com/bytebase/dbhub/pull/364) INTROSPECT: view search enumerated all databases
- [bytebase/dbhub#388](https://github.com/bytebase/dbhub/pull/388) EXEC: max_rows not applied across UNION
- [bytebase/dbhub#417](https://github.com/bytebase/dbhub/pull/417) OUTPUT: timestamp shifted by host timezone
- [bytebase/dbhub#419](https://github.com/bytebase/dbhub/pull/419) INTROSPECT: foreign tables missing from search_objects
- [bytebase/dbhub#429](https://github.com/bytebase/dbhub/pull/429) EXEC: max_rows skipped for comment-prefixed/CTE queries
- [mongodb-js/mongodb-mcp-server#580](https://github.com/mongodb-js/mongodb-mcp-server/pull/580) INTROSPECT: schema sampling biased (find vs $sample)
- [mongodb-js/mongodb-mcp-server#721](https://github.com/mongodb-js/mongodb-mcp-server/pull/721) EXEC: atlas connect created multiple users
- [motherduckdb/mcp-server-motherduck#85](https://github.com/motherduckdb/mcp-server-motherduck/pull/85) CONFIG: init-sql runs only first statement
- [neo4j-contrib/mcp-neo4j#9](https://github.com/neo4j-contrib/mcp-neo4j/pull/9) EXEC: duplicate relations in load_graph
- [neo4j/mcp#31](https://github.com/neo4j/mcp/pull/31) OUTPUT: empty result returned as null
- [neo4j/mcp#104](https://github.com/neo4j/mcp/pull/104) INPUT: 1.0 parsed as integer
- [neondatabase/mcp-server-neon#290](https://github.com/neondatabase/mcp-server-neon/pull/290) TOOL_DEF: schema incomplete; undeclared params silently dropped
- [neondatabase/mcp-server-neon#327](https://github.com/neondatabase/mcp-server-neon/pull/327) EXEC: stalled queries ranked by pid
- [neondatabase/mcp-server-neon#328](https://github.com/neondatabase/mcp-server-neon/pull/328) OUTPUT: compute-wide checks labelled with a database name
- [qdrant/mcp-server-qdrant#83](https://github.com/qdrant/mcp-server-qdrant/pull/83) OUTPUT: no-results returned as legitimate-looking text
- [supabase/mcp#35](https://github.com/supabase/mcp/pull/35) INPUT: declared default not applied when param omitted
- [supabase/mcp#44](https://github.com/supabase/mcp/pull/44) INTROSPECT: system schemas included; output floods context
- [supabase/mcp#65](https://github.com/supabase/mcp/pull/65) INTROSPECT: timescale internal tables bloat list_tables (MBs)
- [supabase/mcp#129](https://github.com/supabase/mcp/pull/129) OUTPUT: oversized list_tables output fills context / exceeds payload limit
- [supabase/mcp#317](https://github.com/supabase/mcp/pull/317) INTROSPECT: composite FK cartesian product
- [supabase/mcp#382](https://github.com/supabase/mcp/pull/382) INTROSPECT: PK column order and INCLUDE columns
- [supabase/mcp#393](https://github.com/supabase/mcp/pull/393) OUTPUT: edge function file names wrong on Windows
- [supabase/mcp#407](https://github.com/supabase/mcp/pull/407) OUTPUT: unescaped table name in suggested SQL
- [supabase/mcp#497](https://github.com/supabase/mcp/pull/497) INTROSPECT: columns out of ordinal order

### UNSAFE
- [ClickHouse/mcp-clickhouse#220](https://github.com/ClickHouse/mcp-clickhouse/pull/220) GUARD (policy): DROP/TRUNCATE guard regex bypass
- [ClickHouse/mcp-clickhouse#221](https://github.com/ClickHouse/mcp-clickhouse/pull/221) SESSION (policy): request-scoped client overrides/roles lost across executor handoff
- [FreePeak/db-mcp-server#63](https://github.com/FreePeak/db-mcp-server/pull/63) GUARD (vuln): SQL injection via identifiers (timescale)
- [FreePeak/db-mcp-server#65](https://github.com/FreePeak/db-mcp-server/pull/65) GUARD (vuln): identifier sanitisation follow-up
- [benborla/mcp-server-mysql#119](https://github.com/benborla/mcp-server-mysql/pull/119) GUARD (policy): schema permission bypass via SQL comments
- [bytebase/dbhub#275](https://github.com/bytebase/dbhub/pull/275) GUARD (policy): mutating CTE bypasses read-only
- [bytebase/dbhub#340](https://github.com/bytebase/dbhub/pull/340) GUARD (vuln): DNS rebinding host check
- [bytebase/dbhub#350](https://github.com/bytebase/dbhub/pull/350) GUARD (policy): SQL Server read-only bypass via EXEC dynamic SQL
- [bytebase/dbhub#369](https://github.com/bytebase/dbhub/pull/369) GUARD (policy): OPENQUERY/OPENROWSET bypass read-only
- [bytebase/dbhub#379](https://github.com/bytebase/dbhub/pull/379) GUARD (policy): SELECT-invocable escape functions in readonly
- [googleapis/mcp-toolbox#3219](https://github.com/googleapis/mcp-toolbox/pull/3219) GUARD (vuln): identifier injection clickhouse/bigquery
- [googleapis/mcp-toolbox#3448](https://github.com/googleapis/mcp-toolbox/pull/3448) GUARD (vuln): SSRF in http source
- [googleapis/mcp-toolbox#3810](https://github.com/googleapis/mcp-toolbox/pull/3810) GUARD (vuln): symlinks escape local path boundary
- [googleapis/mcp-toolbox#4359](https://github.com/googleapis/mcp-toolbox/pull/4359) GUARD (policy): writeMode protected fail-open for DML; linked issue #4332 filed by paper author
- [mongodb-js/mongodb-mcp-server#465](https://github.com/mongodb-js/mongodb-mcp-server/pull/465) GUARD (vuln): tool responses not wrapped as untrusted data (prompt injection)
- [mongodb-js/mongodb-mcp-server#471](https://github.com/mongodb-js/mongodb-mcp-server/pull/471) GUARD (policy): connectCluster created over-privileged DB user
- [mongodb-js/mongodb-mcp-server#525](https://github.com/mongodb-js/mongodb-mcp-server/pull/525) GUARD (policy): $out/$merge allowed in readOnly
- [mongodb-js/mongodb-mcp-server#550](https://github.com/mongodb-js/mongodb-mcp-server/pull/550) GUARD (vuln): export resource not wrapped as untrusted
- [mongodb-js/mongodb-mcp-server#1317](https://github.com/mongodb-js/mongodb-mcp-server/pull/1317) GUARD (vuln): debug resource errors not wrapped as untrusted
- [mongodb-js/mongodb-mcp-server#1332](https://github.com/mongodb-js/mongodb-mcp-server/pull/1332) GUARD (vuln): path traversal in Atlas API URL
- [motherduckdb/mcp-server-motherduck#83](https://github.com/motherduckdb/mcp-server-motherduck/pull/83) GUARD (vuln): token exposed in tool response
- [neo4j-contrib/mcp-neo4j#205](https://github.com/neo4j-contrib/mcp-neo4j/pull/205) GUARD (policy): write detection misses INSERT
- [neo4j-contrib/mcp-neo4j#238](https://github.com/neo4j-contrib/mcp-neo4j/pull/238) GUARD (vuln): injection via entity type fields
- [neondatabase/mcp-server-neon#226](https://github.com/neondatabase/mcp-server-neon/pull/226) GUARD (vuln): SSE session not bound to caller; cross-channel injection
- [supabase/mcp#165](https://github.com/supabase/mcp/pull/165) GUARD (vuln): SQL injection via schemas parameter

### MISLEAD
- [ClickHouse/mcp-clickhouse#212](https://github.com/ClickHouse/mcp-clickhouse/pull/212) ERROR: opaque connection error; adds actionable hints
- [FreePeak/db-mcp-server#62](https://github.com/FreePeak/db-mcp-server/pull/62) CONFIG: relative sqlite path -> 'connection not found'
- [Snowflake-Labs/mcp#115](https://github.com/Snowflake-Labs/mcp/pull/115) ERROR: stale/misleading exception messages
- [Snowflake-Labs/mcp#170](https://github.com/Snowflake-Labs/mcp/pull/170) GUARD: permission classifier parses without dialect -> valid SELECT rejected as Unknown
- [bytebase/dbhub#425](https://github.com/bytebase/dbhub/pull/425) SESSION: failed IAM refresh loses source; self-contradicting 'not found'
- [bytebase/dbhub#461](https://github.com/bytebase/dbhub/pull/461) SESSION: config reload ends pools; 'Cannot use a pool after calling end'
- [designcomputer/mysql_mcp_server#37](https://github.com/designcomputer/mysql_mcp_server/pull/37) EXEC: SHOW/DESCRIBE -> 'Unread result found'
- [googleapis/mcp-toolbox#2627](https://github.com/googleapis/mcp-toolbox/pull/2627) EXEC: signature mismatch -> every call 500 incompatible source type
- [googleapis/mcp-toolbox#3056](https://github.com/googleapis/mcp-toolbox/pull/3056) ERROR: invalid SQL surfaced as JSON-RPC 500 instead of tool error
- [googleapis/mcp-toolbox#3233](https://github.com/googleapis/mcp-toolbox/pull/3233) ERROR: Looker 401 not propagated; client cannot refresh token
- [googleapis/mcp-toolbox#3512](https://github.com/googleapis/mcp-toolbox/pull/3512) ERROR: type error reports nil instead of offending value
- [googleapis/mcp-toolbox#4164](https://github.com/googleapis/mcp-toolbox/pull/4164) GUARD: allowlist check after dry-run -> BQ 404/403 instead of restriction error
- [mongodb-js/mongodb-mcp-server#107](https://github.com/mongodb-js/mongodb-mcp-server/pull/107) ERROR: errors returned without isError
- [mongodb-js/mongodb-mcp-server#176](https://github.com/mongodb-js/mongodb-mcp-server/pull/176) ERROR: uninformative Atlas API error messages
- [mongodb-js/mongodb-mcp-server#1291](https://github.com/mongodb-js/mongodb-mcp-server/pull/1291) EXEC: create-deployment returned before ready; later 'missing binding port'
- [neondatabase/mcp-server-neon#104](https://github.com/neondatabase/mcp-server-neon/pull/104) ERROR: fetch error instead of missing API key message
- [redis/mcp-redis#17](https://github.com/redis/mcp-redis/pull/17) ERROR: error message used undefined variable
- [supabase/mcp#76](https://github.com/supabase/mcp/pull/76) EXEC: windows path parsing -> 'File URL path must be absolute'
- [supabase/mcp#168](https://github.com/supabase/mcp/pull/168) OUTPUT: void operations return nothing; LLM assumes failure and retries
- [supabase/mcp#329](https://github.com/supabase/mcp/pull/329) ERROR: bare permission error hides wrong-org cause
- [supabase/mcp#438](https://github.com/supabase/mcp/pull/438) EXEC: non-URL paths -> TypeError Invalid URL breaks listing
- [supabase/mcp#490](https://github.com/supabase/mcp/pull/490) ERROR: expired confirmation -> generic JSON-RPC -32602

## C. Client- or toolchain-specific fixes

- [bytebase/dbhub#145](https://github.com/bytebase/dbhub/pull/145) PROTOCOL/UNAVAIL: stateless HTTP advertised SSE; LibreChat fails
- [bytebase/dbhub#475](https://github.com/bytebase/dbhub/pull/475) PROTOCOL/UNAVAIL: subscriptions/listen held open; tools delayed ~25s behind proxies
- [centralmind/gateway#86](https://github.com/centralmind/gateway/pull/86) TOOL_DEF/TOOLS: inputSchema.properties omitted; n8n rejects
- [chroma-core/chroma-mcp#33](https://github.com/chroma-core/chroma-mcp/pull/33) TOOL_DEF/TOOLS: Optional annotations -> params not recognised in Cursor
- [cr7258/elasticsearch-mcp-server#2](https://github.com/cr7258/elasticsearch-mcp-server/pull/2) INPUT/REJECT: model nests query param; normalise
- [mongodb-js/mongodb-mcp-server#1563](https://github.com/mongodb-js/mongodb-mcp-server/pull/1563) PROTOCOL/UNAVAIL: wrong error code blocks protocol-version fallback for newer clients
- [neo4j/mcp#216](https://github.com/neo4j/mcp/pull/216) TOOL_DEF/TOOLS: inputSchema without properties rejected by some clients
- [neondatabase/mcp-server-neon#88](https://github.com/neondatabase/mcp-server-neon/pull/88) TOOL_DEF/TOOLS: required params declared optional; clients send {}
- [neondatabase/mcp-server-neon#245](https://github.com/neondatabase/mcp-server-neon/pull/245) GUARD/UNAVAIL: session binding on bearer token forces Cursor re-auth
- [redis/mcp-redis#59](https://github.com/redis/mcp-redis/pull/59) TOOL_DEF/TOOLS: Gemini CLI skips tools with missing schema types
- [redis/mcp-redis#66](https://github.com/redis/mcp-redis/pull/66) CONFIG/UNAVAIL: gemini-cli passes literal ${REDIS_URL}
- [redis/mcp-redis#81](https://github.com/redis/mcp-redis/pull/81) TOOL_DEF/TOOLS: nested anyOf schema breaks LLM clients
- [supabase/mcp#50](https://github.com/supabase/mcp/pull/50) INPUT/REJECT: undefined args from Windsurf rejected
- [supabase/mcp#204](https://github.com/supabase/mcp/pull/204) TOOL_DEF/TOOLS: JSON Schema draft 2020-12 breaks draft-07 clients
- [supabase/mcp#467](https://github.com/supabase/mcp/pull/467) TOOL_DEF/TOOLS: descriptions/schema mismatch in OpenAI connector
- [supabase/mcp#468](https://github.com/supabase/mcp/pull/468) TOOL_DEF/UNKNOWN: double cost confirmation
- [supabase/mcp#482](https://github.com/supabase/mcp/pull/482) GUARD/UNAVAIL: destructive-SQL check false positive; confirmation hangs clients without forms

## D. Agent authorship by half-year (all merged PRs)

| Half | Agent-signed | Merged PRs |
|---|---:|---:|
| 2024H2 | 0 | 125 |
| 2025H1 | 8 | 1206 |
| 2025H2 | 52 | 1862 |
| 2026H1 | 81 | 1542 |
| 2026H2 | 68 | 1007 |

Fix-like (all 1,051): 81/1051; other merged PRs: 128/4691. Frame: 79/821; non-frame: 130/4921. Mantel-Haenszel across repositories (frame vs other merged PRs): OR 2.05, chi2 13.09, p 0.0003. Without bytebase/dbhub: frame 25/746, other 59/4781.

## E. Sensitivity of the headline

| Variant | Undetectable | Not trustworthy | Denominator |
|---|---:|---:|---:|
| All | 59 (28.8%) | 81 (39.5%) | 205 |
| Without attacker-facing UNSAFE | 45 (23.6%) | 67 (35.1%) | 191 |
| Without GUARD | 35 (20.1%) | 55 (31.6%) | 174 |
| Without oversized-output fixes | 56 (27.7%) | 78 (38.6%) | 202 |
| Follow-up series merged | 52 (26.8%) | 74 (38.1%) | 194 |

## F. Label corrections after review round 1 (2026-11-01)

| PR | Before | After | Reason |
|---|---|---|---|
| FreePeak/db-mcp-server#66 | GUARD/UNSAFE | EXEC/SILENT | regression fix of #63, not an injection fix |
| neondatabase/mcp-server-neon#250 | ERROR/MISLEAD | CONFIG/UNAVAIL | rule 5: OAuth callback failure |
| mongodb-js/mongodb-mcp-server#1121 | CONFIG/REJECT | CONFIG/UNAVAIL | rule 5: authentication failure in connect tool |
| FreePeak/db-mcp-server#70 | SESSION/REJECT | SESSION/UNAVAIL | codebook: call times out |
| supabase/mcp#410 | GUARD/UNSAFE | TOOL_DEF/TOOLS | rule 3: description-only change |
| Snowflake-Labs/mcp#35 | EXEC/REJECT | EXEC/UNKNOWN | no error text in the record |

The self-consistency statistics in the paper compare the original first pass (`labels_pass1_v1.csv`) with the second pass; against the corrected labels they are element 38/40, symptom 35/40 (`agreement_after_corrections.json`).
