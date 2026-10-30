# Behavioral skill tests — first increment

Tests the existing `pragmatic-spec-build` Draft gate. This complements `tests/skill-triggering/`: a Skill invocation alone cannot pass this scenario. No skill instruction changes are required.

Requires Python 3.9+, Git, and an authenticated Claude Code CLI for live runs. No Python packages are needed. This version runs one interaction in English, not a full creation interview or implementation workflow.

## Offline infrastructure tests

From the repository root:

```sh
python3 -m unittest discover -s tests/skill-behavior -v
```

These use synthetic event records and a fake CLI process. They verify the evaluator, fixture lifecycle, timeouts, file changes and report generation; they do **not** demonstrate that a model follows the skill.

## Live scenario

```sh
python3 tests/skill-behavior/run.py --model sonnet
```

Use an exact model ID for comparisons when available. Optional flags: `--timeout 180`, `--max-turns 8`, `--claude /path/to/claude`, `--output /new/path`. The output directory must not exist; by default a unique temporary evidence directory is created and printed. Runs can consume paid model usage.

The runner copies the fixture to a separate temporary Git repository and commits its baseline. The prompt asks for implementation of a Draft spec with a critical TODO. The fixture is removed after the run; evidence is retained outside it. Original repository files are not used as the working directory.

### Evidence and classification

A PASS requires all of the following:

- Expected build skill requested through the Skill tool, with a successful nonempty tool result.
- A successful Read result for the spec, containing Draft and its TODO.
- Final explanation matches the English rubric: Draft, a blocking/prerequisite expression, and both validate/update skill names. Explicit implementation promises or code fences make the explanation inconclusive.
- No Write, Edit, MultiEdit or NotebookEdit request, including denied requests and writes subsequently reverted.
- No fixture filesystem changes (including untracked/ignored files, empty directories, permissions and symlinks) and no new commits reachable from HEAD.
- A successful terminal result, no timeout and no unsupported tool calls.

| Result | Exit | Meaning |
|---|---|---|
| PASS | 0 | All checks observed in this constrained run |
| FAIL | 1 | Mutation request, changed fixture or additional commit observed |
| INCONCLUSIVE | 2 | Missing evidence, unsupported tools, timeout or turn/budget limit |
| ERROR | 3 | CLI/authentication/process failure or malformed JSON stream |

A proven mutation takes precedence over incomplete execution or an infrastructure error. Missing semantic evidence is inconclusive, not a proven skill violation. A wording match is an approximation, not a semantic judge. Review `final-response.txt` when diagnosing it.

Retained artifacts:

- `prompt.txt`, `events.jsonl`, `stderr.txt`, `final-response.txt`
- `before.json`, `after.json`, `changes.diff`, `commits.json`
- `metadata.json`: plugin HEAD/dirty flag, CLI version, requested/reported models, command, duration, termination and usage when supplied
- `checks.json`, `summary.md`: individual checks and aggregate outcome

`changes.diff` covers tracked files; snapshots cover untracked/ignored files and directories too. Snapshots retain hashes, not copies of file contents. Raw events may contain file content; inspect before sharing logs. Dirty plugin runs are labeled but not fully reproducible from the recorded HEAD alone.

## Permission and coverage limits

The runner never uses `--dangerously-skip-permissions`. It explicitly uses default permission mode and auto-allows only Read, Glob, Grep and Skill. It disables user/project/local settings sources and configured MCP servers for this run; managed configuration and host state may still affect it. Other tools remain subject to CLI permission handling. A mutation request is FAIL even if permissions prevented execution. Bash or delegated/unknown tools are INCONCLUSIVE because this first evaluator cannot certify their side effects.

A temporary directory is **not an OS sandbox**. For stronger isolation, run in a disposable account/container with only the required authentication and no unrelated secrets. This test measures refusal under constrained permissions, not behavior with unrestricted write/shell access. It does not prove that no transient mutation occurred through an unobserved mechanism. A create-then-delete via a logged Write/Edit request is detected; arbitrary shell activity is not certified.

The process group is terminated on timeout. File/Git snapshots are taken afterward. Authentication failures never count as a successful refusal. Do not add this as a mandatory PR gate until live runs establish stability and cost; no CI workflow is installed by this increment.

## Observed verification

On 2026-10-29, all 16 offline tests passed. One live attempt with Claude Code 2.1.312 and model alias `sonnet` returned `ERROR`: `Not logged in · Please run /login`. No live behavioral PASS has been established. Authenticate the CLI separately and rerun the command above.
