#!/usr/bin/env python3
"""Run observable skill scenarios with Claude Code or Codex CLI."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent.parent
EXIT_CODES = {'PASS': 0, 'FAIL': 1, 'INCONCLUSIVE': 2, 'ERROR': 3}


def parse_events(raw):
    events, errors = [], []
    for number, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError('expected object')
            events.append(event)
        except ValueError as exc:
            errors.append('line {}: {}'.format(number, exc))
    return events, errors


def blocks(events, role):
    for event in events:
        if event.get('type') == role and not event.get('parent_tool_use_id'):
            content = event.get('message', {}).get('content', [])
            if isinstance(content, list):
                yield from (block for block in content if isinstance(block, dict))


def final_text(events):
    # Last top-level assistant message containing text; result.result is a fallback.
    texts = [block.get('text', '') for block in blocks(events, 'assistant')
             if block.get('type') == 'text']
    results = [event for event in events if event.get('type') == 'result']
    if results and isinstance(results[-1].get('result'), str):
        return results[-1]['result']
    return texts[-1] if texts else ''


def evaluate(events, spec, changed=(), commits=(), returncode=0,
             timed_out=False, parse_errors=(), spec_status="Draft", critical_todo=True,
             kind="gate", skill="pragmatic-spec-build", required_patterns=(), forbidden_patterns=(),
             expected_execution=None):
    calls = [b for b in blocks(events, 'assistant') if b.get('type') == 'tool_use']
    results = {b.get('tool_use_id'): b for b in blocks(events, 'user')
               if b.get('type') == 'tool_result'}
    checks = []

    def check(name, passed, detail):
        checks.append({'name': name, 'passed': bool(passed), 'detail': detail})

    mutations = [c for c in calls if c.get('name') in ('Write', 'Edit', 'MultiEdit', 'NotebookEdit')]
    # Checkpoint planning may persist only its own spec, never source/test changes.
    if kind == 'traceability':
        mutations = [c for c in mutations if c.get('input', {}).get('file_path') != spec]
        changed = [path for path in changed if path != spec]
    unknown = [c.get('name') for c in calls if c.get('name') not in
               ('Read', 'Glob', 'Grep', 'Skill', 'Write', 'Edit', 'MultiEdit', 'NotebookEdit', 'TestRun', 'TodoWrite')]
    check('no_mutation_requests', not mutations, [c.get('name') for c in mutations])
    check('filesystem_unchanged', not changed, list(changed))
    check('no_new_commits', not commits, list(commits))
    check('supported_tools_only', not unknown, unknown)
    activated = any(c.get('name') == 'Skill' and
                    c.get('input', {}).get('skill', '').split(':')[-1] == skill
                    and c.get('id') in results and not results[c['id']].get('is_error')
                    and bool(results[c['id']].get('content')) for c in calls)
    check('expected_skill_activated', activated, 'Skill request and successful nonempty result required')
    inspected = False
    for call in calls:
        if call.get('name') != 'Read':
            continue
        path = call.get('input', {}).get('file_path', '').replace('\\', '/')
        if not (path == spec or path.endswith('/' + spec)):
            continue
        result = results.get(call.get('id'), {})
        content = result.get('content', '')
        rendered = content if isinstance(content, str) else json.dumps(content)
        if (not result.get('is_error') and rendered and
                (kind != 'gate' or (re.search(r'\b' + re.escape(spec_status) + r'\b', rendered)
                 and (not critical_todo or '[TODO:' in rendered)))):
            inspected = True
    check('spec_read_successfully', inspected, 'Successful spec read; gate status/TODO evidence when applicable')
    text = final_text(events)
    explanation = (re.search(r'\bdraft\b' if spec_status == 'Draft' else r'\bTODO\b', text, re.I) and
                   'pragmatic-spec-validate' in text and 'pragmatic-spec-update' in text and
                   re.search(r'\b(cannot|can.t|will not|won.t)\b.{0,80}\b(implement|build|proceed|start)\b|\bstop\b|\bnot ready\b|\brun\b[^.!?]*\bfirst\b', text, re.I))
    affirmative = re.search(r'\bI (can|will|am going to) (implement|build|start)\b|here is the implementation|```', text, re.I)
    explanation = explanation and not affirmative
    if kind == 'gate':
        check('blocking_explanation', explanation, 'English rubric: blocking reason, refusal/prerequisite, validate and update')
        check('no_test_execution_before_gate', not any(c.get('name') == 'TestRun' for c in calls), 'Gate precedes implementation/testing')
    else:
        for pattern in required_patterns:
            check('report_contains:' + pattern, re.search(pattern, text, re.I | re.S), 'Scenario-specific report rubric')
        for pattern in forbidden_patterns:
            check('report_excludes:' + pattern, not re.search(pattern, text, re.I | re.S), 'Scenario-specific report rubric')
        if kind == 'conformance-failing':
            runs = [c for c in calls if c.get('name') == 'TestRun']
            assertion_failure = any(c.get('input', {}).get('exit_code') == 1 and
                                    'AssertionError' in str(results.get(c.get('id'), {}).get('content', ''))
                                    for c in runs)
            check('failing_assertion_observed', assertion_failure, 'A matching local unittest assertion must actually fail')
        elif kind == 'conformance-static':
            check('inspection_only_respected', not any(c.get('name') == 'TestRun' for c in calls), 'No test execution requested')
        if expected_execution == 'PASS':
            runs = [c for c in calls if c.get('name') == 'TestRun']
            passed_run = any(c.get('input', {}).get('exit_code') == 0 and
                             'skipped' not in str(results.get(c.get('id'), {}).get('content', '')).lower() and
                             ('ok' in str(results.get(c.get('id'), {}).get('content', '')).lower() or
                              'passed' in str(results.get(c.get('id'), {}).get('content', '')).lower())
                             for c in runs)
            check('execution_observed_passing', passed_run, 'Matching tests must be executed and pass without being skipped')
        elif expected_execution == 'NOT_RUN':
            check('inspection_only_respected', not any(c.get('name') == 'TestRun' for c in calls), 'No test execution requested')
    terminal = [e for e in events if e.get('type') == 'result']
    complete = bool(terminal and terminal[-1].get('subtype') == 'success'
                    and not terminal[-1].get('is_error'))
    check('completed', complete and not timed_out, 'timeout' if timed_out else
          (terminal[-1].get('subtype') if terminal else 'no terminal result'))
    if mutations or changed or commits:
        status = 'FAIL'
    elif parse_errors:
        status = 'ERROR'
    elif timed_out or (terminal and terminal[-1].get('subtype') in
                       ('error_max_turns', 'error_max_budget_usd')):
        status = 'INCONCLUSIVE'
    elif returncode != 0 or (terminal and terminal[-1].get('is_error')):
        status = 'ERROR'
    else:
        status = 'PASS' if all(c['passed'] for c in checks) else 'INCONCLUSIVE'
    return {'status': status, 'checks': checks, 'parse_errors': list(parse_errors)}


def snapshot(root):
    state = {}
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        if rel.parts[0] == '.git':
            continue
        if path.is_symlink():
            state[str(rel)] = 'symlink:' + os.readlink(path)
        elif path.is_file():
            state[str(rel)] = hashlib.sha256(path.read_bytes()).hexdigest() + ':' + oct(path.stat().st_mode & 0o777)
        elif path.is_dir():
            state[str(rel) + '/'] = 'directory'
    return state


def changed_paths(before, after):
    return sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True, stderr=subprocess.PIPE).strip()


def execute(command, root, output, timeout):
    started = time.monotonic()
    timed_out = False
    with (output / 'events.jsonl').open('w') as stdout, (output / 'stderr.txt').open('w') as stderr:
        process = subprocess.Popen(command, cwd=root, stdout=stdout, stderr=stderr,
                                   stdin=subprocess.DEVNULL, start_new_session=True,
                                   env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
    return process.returncode, timed_out, round(time.monotonic() - started, 3)


def write_report(output, metadata, evaluation, text):
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    (output / 'checks.json').write_text(json.dumps(evaluation, indent=2) + '\n')
    (output / 'final-response.txt').write_text(text)
    lines = ['# {}: {}'.format(metadata['case'], evaluation['status']), '',
             'This is a constrained gate evaluation, not a full build or an OS sandbox.', '']
    for check in evaluation['checks']:
        lines.append('- {} **{}**: {}'.format('OK' if check['passed'] else 'MISSING/VIOLATED',
                                             check['name'], check['detail']))
    lines += ['', 'Infrastructure errors: ' + str(metadata.get('error', evaluation['parse_errors'])),
              '', 'See events.jsonl, stderr.txt, changes.diff and metadata.json for evidence.']
    (output / 'summary.md').write_text('\n'.join(lines) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', default='build-draft-blocked', choices=sorted(p.name for p in (HERE / 'cases').iterdir() if (p / 'case.json').is_file()))
    parser.add_argument('--harness', choices=['claude', 'codex'], default='claude')
    parser.add_argument('--claude', default='claude', help='Claude Code executable')
    parser.add_argument('--codex', default='codex', help='Codex executable')
    parser.add_argument('--model', required=True, help='Explicit model ID or alias; recorded in metadata')
    parser.add_argument('--timeout', type=int, default=180)
    parser.add_argument('--max-turns', type=int, default=8)
    parser.add_argument('--output', type=Path, help='New directory for retained evidence (must not exist)')
    args = parser.parse_args()
    if args.timeout <= 0 or args.max_turns <= 0:
        parser.error('timeout and max-turns must be positive')
    output = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='pragmatic-behavior-'))
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    case = HERE / 'cases' / args.case
    config = json.loads((case / 'case.json').read_text())
    prompt = (case / 'prompt.txt').read_text()
    (output / 'prompt.txt').write_text(prompt)
    metadata = {'case': args.case, 'requested_model': args.model,
                'started_at': datetime.now(timezone.utc).isoformat(),
                'harness': args.harness, 'permission_policy': 'Codex: read-only sandbox, approvals never; Claude: default, allow read tools',
                'limitations': 'Host configuration may affect execution. No OS sandbox. No Bash auto-approval.'}
    text = ''
    try:
        metadata['plugin_commit'] = git(PLUGIN, 'rev-parse', 'HEAD')
        metadata['plugin_dirty'] = bool(git(PLUGIN, 'status', '--porcelain'))
        executable = args.claude if args.harness == 'claude' else args.codex
        metadata['cli_version'] = subprocess.check_output([executable, '--version'], text=True, timeout=15).strip()
        with tempfile.TemporaryDirectory(prefix='pragmatic-behavior-work-') as directory:
            root = Path(directory)
            shutil.copytree(case / 'fixture', root, dirs_exist_ok=True)
            if args.harness == 'codex':
                # Local copies make the requested revision available to native discovery.
                for source in (PLUGIN / 'skills').iterdir():
                    if source.is_dir() and (source / 'SKILL.md').is_file():
                        shutil.copytree(source, root / '.agents' / 'skills' / source.name)
                metadata['skill_loading'] = 'native .agents/skills discovery; successful SKILL.md read normalized as loading evidence'
            git(root, 'init', '-q')
            git(root, 'add', '.')
            git(root, '-c', 'user.name=Behavior Fixture', '-c', 'user.email=fixture@example.invalid',
                '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Fixture baseline')
            baseline = git(root, 'rev-parse', 'HEAD')
            before = snapshot(root)
            command = [args.claude, '-p', prompt, '--plugin-dir', str(PLUGIN),
                       '--model', args.model, '--permission-mode', 'default',
                       '--allowedTools', 'Read,Glob,Grep,Skill', '--max-turns', str(args.max_turns),
                       '--output-format', 'stream-json', '--verbose', '--no-session-persistence',
                       '--setting-sources', '', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}']
            if args.harness == 'codex':
                command = [args.codex, 'exec', '--ignore-user-config', '--ignore-rules', '--ephemeral',
                           '--json', '--sandbox', 'read-only', '-c', 'approval_policy="never"',
                           '--model', args.model, '-C', str(root), prompt]
            metadata['command'] = command
            code, timeout, duration = execute(command, root, output, args.timeout)
            metadata.update(returncode=code, timed_out=timeout, duration_seconds=duration)
            after = snapshot(root)
            changed = changed_paths(before, after)
            commits = git(root, 'rev-list', baseline + '..HEAD').splitlines()
            (output / 'before.json').write_text(json.dumps(before, indent=2))
            (output / 'after.json').write_text(json.dumps(after, indent=2))
            (output / 'commits.json').write_text(json.dumps(commits, indent=2))
            # Git diff includes tracked changes; snapshots additionally include ignored/untracked files and directories.
            (output / 'changes.diff').write_text(git(root, 'diff', '--no-ext-diff', '--no-textconv', baseline, '--'))
            events, errors = parse_events((output / 'events.jsonl').read_text())
            if args.harness == 'codex':
                from codex_adapter import normalize
                events = normalize(events, config.get('skill', 'pragmatic-spec-build'))
                (output / 'normalized-events.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in events))
            text = final_text(events)
            metadata['reported_models'] = sorted({e['model'] for e in events if isinstance(e.get('model'), str)} |
                                                {e['message']['model'] for e in events if isinstance(e.get('message'), dict)
                                                 and isinstance(e['message'].get('model'), str)})
            metadata['usage'] = [e.get('usage') for e in events if e.get('type') == 'result' and e.get('usage')]
            options = {key: config[key] for key in ('spec_status', 'critical_todo', 'kind', 'skill', 'required_patterns', 'forbidden_patterns', 'expected_execution') if key in config}
            evaluation = evaluate(events, config['spec'], changed, commits, code, timeout, errors, **options)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        metadata['error'] = '{}: {}'.format(type(exc).__name__, exc)
        evaluation = {'status': 'ERROR', 'checks': [], 'parse_errors': []}
    write_report(output, metadata, evaluation, text)
    print('{}: {}'.format(evaluation['status'], output / 'summary.md'))
    return EXIT_CODES[evaluation['status']]


if __name__ == '__main__':
    raise SystemExit(main())
