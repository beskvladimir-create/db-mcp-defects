# DB-MCP-Fixes: how defects in database MCP tool servers reach LLM agents

Repository: https://github.com/beskvladimir-create/db-mcp-defects

Dataset, codebook and scripts for the paper *Silent, Unsafe or Misleading: How Defects in Database
MCP Servers Reach LLM Agents* (Vladimir Beskorovainyi, Besk Tech, 2026).

## What is here

| Path | Content |
|---|---|
| `data/dataset.csv` | **Main dataset.** 376 sampled fix-like merged PRs from 26 database MCP servers, one row per PR: URL, title, author, merge date, inclusion decision, exclusion reason, contract element, agent-visible symptom, client-specific flag, agent-authorship signals, sampling weights, annotator note. 256 rows have `include=yes`. |
| `CODEBOOK.md` | Definitions of every label and the decision rules used (v1.2 adds `unsafe_kind`). |
| `APPENDIX.md` | Per-repository table, all SILENT/UNSAFE/MISLEAD and client-specific fixes, agent-authorship detail, sensitivity table, label corrections. |
| `SELECTION.md`, `repo_selection.csv` | The 16 repository searches, the 18 named checks and a decision for every candidate with at least 300 stars. |
| `data/defect_groups.csv`, `data/policy_mechanism.csv` | Follow-up series used for the de-duplicated sensitivity analysis; mechanism of each policy-violating UNSAFE fix. |
| `data/labels_pass1.csv` | Final labels, assigned by the author against the codebook. `data/labels_pass1_v1.csv` is an earlier draft (history). |
| `data/labels_pass2.csv`, `data/relabel_indices.json`, `data/agreement.json` | Second-pass labels for 60 random units (shuffled view without identifiers or labels; same session, not blind to the first pass) and self-consistency statistics (`agreement.json` vs the original first pass, `agreement_after_corrections.json` vs the final labels). |
| `data/frame.csv`, `data/auto_excluded.csv`, `data/frame_stats.json` | Sampling frame (821 PRs), automatically excluded PRs (230), per-repository counts. |
| `data/sample.jsonl` | Full evidence shown to the annotator for each sampled PR (body, linked issues, changed files). |
| `data/agentic.json` | Coding-agent signals for all 5,742 merged PRs. |
| `data/results.json`, `data/results_extra.json`, `data/tables.md`, `data/fig1_symptoms.png` | All numbers, tables and the figure in the paper. |
| `raw/gh_search_results.tar.gz` | Raw GitHub search API responses (merged PRs and issues, created 2024-11-01..2026-10-31, collected 2026-11-01). |
| `raw/pr_files.json.gz` | PR number -> merge/squash commit and changed files, from bare clones. |
| `raw/repo_candidates.tsv` | Repository search results used to choose the 26 repositories. |
| `c3/` | RQ5 schema audit: `tools/*.json` (tools/list output, 1 Nov 2026: 25 attempts, 18 succeeded; failed attempts keep their error), `gemma4_v5.jinja` (template used), `c3_summary.json` and `c3_tools.csv` (one row per tool for the raw schema and for the schema after the C3 normaliser), `c3_optional.json`. |
| `paper.md` | The paper. |
| `scripts/` | Collection, frame building, labelling view, agent detection, agreement, analysis, figure, appendix, reference check, tools/list client, schema audit, word count. |

## Labels in brief

- **element**: TOOL_DEF, INPUT, INTROSPECT, EXEC, OUTPUT, ERROR, GUARD, SESSION, CONFIG, PROTOCOL
- **symptom** (what the calling agent observes): SILENT, UNSAFE, MISLEAD, REJECT, TOOLS, UNAVAIL, OPERATOR, UNKNOWN
- **client_specific**: the defect appears only with a particular client, host or model toolchain

See `CODEBOOK.md` for definitions.

## Reproduce

Requires Python 3.10+, `gh` CLI (search API), `git`, matplotlib.

```bash
mkdir work && cd work
python3 ../scripts/collect.py raw/gh                      # or: tar xzf ../raw/gh_search_results.tar.gz -C raw
# bare clones: git clone --bare --filter=blob:none https://github.com/<owner>/<repo> raw/git/<owner>__<repo>.git
python3 ../scripts/pr_files.py raw/git raw/pr_files.json
python3 ../scripts/build_frame.py raw/gh raw/pr_files.json analysis 40
cp ../data/labels_pass1.csv analysis/                     # the final labels (see Caveats)
python3 ../scripts/agentic.py raw/gh raw/git analysis/agentic.json
python3 ../scripts/analyze.py .                            # also needs defect_groups.csv, policy_mechanism.csv in analysis/
python3 ../scripts/agreement.py analysis/labels_pass1_v1.csv analysis/labels_pass2.csv analysis/relabel_indices.json analysis/agreement.json
python3 ../scripts/figure.py .
python3 ../scripts/appendix.py analysis APPENDIX.md
python3 ../scripts/check_refs.py ../paper.md analysis/dataset.csv   # every PR cited in the paper vs the dataset (paper.md is in the release root)
```

Re-collecting from GitHub will return a slightly different PR set (new merges, edited text). To reproduce the
paper's numbers exactly, unpack `raw/gh_search_results.tar.gz` and copy `data/sample.jsonl`, `data/frame.csv`,
`data/frame_stats.json`, `data/agentic.json`, `data/auto_excluded.csv`, `data/defect_groups.csv`, `data/policy_mechanism.csv` and `data/labels_pass1.csv` into `analysis/` before running
`analyze.py`.

### Reproduce the paper's numbers exactly (no network needed)

```bash
mkdir -p work/raw work/analysis && cd work
tar xzf ../raw/gh_search_results.tar.gz -C raw
cp ../data/{sample.jsonl,frame.csv,frame_stats.json,agentic.json,auto_excluded.csv,defect_groups.csv,policy_mechanism.csv,labels_pass1.csv,labels_pass1_v1.csv,labels_pass2.csv,relabel_indices.json} analysis/
python3 ../scripts/analyze.py .            # results.json, results_extra.json, results_round1.json, tables.md, dataset.csv
# with a corrected labels file (same columns, '|' or ',' delimited): python3 ../scripts/analyze.py . corrected_labels.csv
python3 ../scripts/agreement.py analysis/labels_pass1_v1.csv analysis/labels_pass2.csv analysis/relabel_indices.json analysis/agreement.json
python3 ../scripts/agreement.py analysis/labels_pass1.csv analysis/labels_pass2.csv analysis/relabel_indices.json analysis/agreement_after_corrections.json
python3 ../scripts/figure.py .
python3 ../scripts/check_refs.py ../paper.md analysis/dataset.csv
python3 ../scripts/c3_schema_audit.py ../c3/tools ../c3/gemma4_v5.jinja c3_summary.json c3_tools.csv   # needs jinja2
python3 ../scripts/c3_optional.py ../c3/tools c3_optional.json
```

To re-run the tools/list collection itself, see `c3/README_C3.md` (commands and environment used).

## Caveats

- The author labelled all 376 units against the codebook. There is no independent second coder. Earlier draft labels
  and an LLM self-consistency pass (`data/labels_pass1_v1.csv`, `data/labels_pass2.csv`, `data/agreement*.json`) are
  kept as history and are not reported in the paper.
- Issue links written as URLs were added to the evidence after the first 30 units had been labelled; 12 sampled PRs
  have no changed-file list (11 without a matching merge commit, 1 with an empty diff).
- Symptoms are inferred from PR and issue text, not from running agents.
- The schema audit (RQ5) renders unmodified MCP schemas through one Gemma 4 chat template; it does not run the model.
- Agent authorship is detected from self-disclosed signatures and is a lower bound.
- Disclosure: the author contributes to googleapis/mcp-toolbox. His PRs there were unmerged at collection time and
  are not in the frame; his issue #4332 is referenced by sampled PR #4359 (another contributor).

## Licence

Scripts, labels and documentation: Apache License 2.0 (see `LICENSE`). PR titles, bodies and issue texts in
`data/sample.jsonl` and `raw/` are quoted from public GitHub repositories, remain the property of their authors,
and are included only so the labels can be audited.
