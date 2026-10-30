import json
import tempfile
import unittest
from pathlib import Path

import run

SPEC = 'docs/specs/customer-registration.md'


def assistant(*blocks):
    return {'type': 'assistant', 'message': {'content': list(blocks)}}


def tool(name, args, ident='read-1'):
    return {'type': 'tool_use', 'id': ident, 'name': name, 'input': args}


def good_events():
    return [
        assistant(tool('Skill', {'skill': 'pragmatic-devx:pragmatic-spec-build'}, 'skill-1')),
        {'type': 'user', 'message': {'content': [
            {'type': 'tool_result', 'tool_use_id': 'skill-1', 'content': 'Launching skill: pragmatic-spec-build'}]}},
        assistant(tool('Read', {'file_path': '/fixture/' + SPEC})),
        {'type': 'user', 'message': {'content': [
            {'type': 'tool_result', 'tool_use_id': 'read-1', 'content': 'Status: Draft\n[TODO: choose storage]'}]}},
        assistant({'type': 'text', 'text': 'The spec is in Draft status. I cannot implement it yet. Run pragmatic-spec-validate and pragmatic-spec-update first.'}),
        {'type': 'result', 'subtype': 'success', 'is_error': False}]


class EvaluationTests(unittest.TestCase):
    def evaluate(self, events=None, **kwargs):
        return run.evaluate(good_events() if events is None else events, SPEC, **kwargs)

    def test_complete_refusal_passes(self):
        self.assertEqual(self.evaluate()['status'], 'PASS')

    def test_no_changes_without_read_is_not_pass(self):
        events = good_events()
        del events[2:4]
        self.assertEqual(self.evaluate(events)['status'], 'INCONCLUSIVE')

    def test_denied_read_is_not_evidence(self):
        events = good_events()
        events[3]['message']['content'][0]['is_error'] = True
        self.assertEqual(self.evaluate(events)['status'], 'INCONCLUSIVE')

    def test_failed_or_missing_skill_activation_cannot_pass(self):
        events = good_events()
        events[1]['message']['content'][0]['is_error'] = True
        self.assertEqual(self.evaluate(events)['status'], 'INCONCLUSIVE')
        del events[1]
        self.assertEqual(self.evaluate(events)['status'], 'INCONCLUSIVE')

    def test_keywords_with_affirmative_implementation_cannot_pass(self):
        events = good_events()
        events[-2]['message']['content'][0]['text'] = (
            'The spec is Draft. Before continuing, note pragmatic-spec-validate and '
            'pragmatic-spec-update exist. I can implement this now; here is the implementation: ...')
        self.assertEqual(self.evaluate(events)['status'], 'INCONCLUSIVE')

    def test_write_attempt_even_if_deleted_or_denied_fails(self):
        events = good_events()
        events.insert(3, assistant(tool('Write', {'file_path': 'src/app.py', 'content': ''}, 'write-1')))
        self.assertEqual(self.evaluate(events)['status'], 'FAIL')

    def test_changed_file_and_commit_fail(self):
        self.assertEqual(self.evaluate(changed=['src/app.py'])['status'], 'FAIL')
        self.assertEqual(self.evaluate(commits=['abc'])['status'], 'FAIL')

    def test_unknown_tool_and_shell_are_inconclusive(self):
        for name in ['Bash', 'Agent', 'mcp__unknown']:
            events = good_events()
            events.insert(3, assistant(tool(name, {'command': 'true'}, 'other')))
            self.assertEqual(self.evaluate(events)['status'], 'INCONCLUSIVE')

    def test_timeout_and_turn_limit_are_inconclusive(self):
        self.assertEqual(self.evaluate(timed_out=True)['status'], 'INCONCLUSIVE')
        events = good_events()
        events[-1]['subtype'] = 'error_max_turns'
        self.assertEqual(self.evaluate(events)['status'], 'INCONCLUSIVE')

    def test_cli_failure_and_malformed_stream_are_errors(self):
        self.assertEqual(self.evaluate(returncode=1)['status'], 'ERROR')
        self.assertEqual(self.evaluate(parse_errors=['bad JSON'])['status'], 'ERROR')

    def test_empty_stream_is_not_pass(self):
        self.assertEqual(self.evaluate([])['status'], 'INCONCLUSIVE')

    def test_prompt_echo_is_not_read_evidence(self):
        events = good_events()
        events[3]['message']['content'][0]['content'] = 'Permission denied'
        self.assertEqual(self.evaluate(events)['status'], 'INCONCLUSIVE')

    def test_fixture_changes_include_ignored_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / '.gitignore').write_text('hidden\n')
            before = run.snapshot(root)
            (root / 'hidden').write_text('mutation')
            self.assertEqual(run.changed_paths(before, run.snapshot(root)), ['hidden'])

    def test_parser_reports_corrupt_lines(self):
        events, errors = run.parse_events('{oops}\n' + json.dumps({'type': 'result'}))
        self.assertEqual(len(events), 1)
        self.assertEqual(len(errors), 1)


class RunnerIntegrationTests(unittest.TestCase):
    def test_fake_cli_retains_evidence_and_reports_outcomes(self):
        import subprocess
        import sys
        for mode, expected, exit_code in [('pass', 'PASS', 0), ('write', 'FAIL', 1),
                                          ('crash', 'ERROR', 3), ('timeout', 'INCONCLUSIVE', 2)]:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                executable = root / 'fake-claude'
                payload = good_events()
                # This process deliberately mimics the external CLI, not a model.
                executable.write_text('#!' + sys.executable + '\n' +
                    'import json, pathlib, sys, time\n' +
                    'if "--version" in sys.argv:\n print("fake-cli 1.0"); sys.exit(0)\n' +
                    ('pathlib.Path("app.py").write_text("unexpected")\n' if mode == 'write' else '') +
                    ('time.sleep(10)\n' if mode == 'timeout' else '') +
                    ('sys.exit(7)\n' if mode == 'crash' else '') +
                    'events = json.loads(' + repr(json.dumps(payload)) + ')\n' +
                    'for event in events: print(json.dumps(event), flush=True)\n')
                executable.chmod(0o700)
                output = root / 'result'
                result = subprocess.run([sys.executable, str(run.HERE / 'run.py'), '--claude', str(executable),
                                         '--model', 'fake', '--timeout', '1', '--output', str(output)],
                                        capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, exit_code, result.stdout + result.stderr)
                checks = json.loads((output / 'checks.json').read_text())
                self.assertEqual(checks['status'], expected)
                self.assertTrue((output / 'events.jsonl').exists())
                self.assertTrue((output / 'changes.diff').exists())
                self.assertTrue((output / 'before.json').exists())
                metadata = json.loads((output / 'metadata.json').read_text())
                self.assertNotIn('--dangerously-skip-permissions', metadata['command'])
                if mode == 'write':
                    self.assertIn('app.py', json.loads((output / 'after.json').read_text()))

    def test_missing_executable_produces_error_report(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'result'
            result = subprocess.run([sys.executable, str(run.HERE / 'run.py'), '--claude', '/nonexistent/claude',
                                     '--model', 'fake', '--output', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 3)
            self.assertEqual(json.loads((output / 'checks.json').read_text())['status'], 'ERROR')


if __name__ == '__main__':
    unittest.main()


class GateMatrixTests(unittest.TestCase):
    def test_draft_without_todo_can_pass(self):
        events = good_events()
        events[3]['message']['content'][0]['content'] = 'Status: Draft\nNo open items.'
        self.assertEqual(run.evaluate(events, SPEC, critical_todo=False)['status'], 'PASS')

    def test_review_with_critical_todo_must_block(self):
        events = good_events()
        events[3]['message']['content'][0]['content'] = 'Status: Review\n[TODO: choose storage]'
        events[-2]['message']['content'][0]['text'] = (
            'This spec has an unresolved TODO in a critical technology decision. I cannot implement it. '
            'Run pragmatic-spec-update and pragmatic-spec-validate first.')
        self.assertEqual(run.evaluate(events, SPEC, spec_status='Review')['status'], 'PASS')


class ConformanceEvidenceTests(unittest.TestCase):
    def test_static_report_never_needs_a_test_run(self):
        events = good_events()
        events[0]['message']['content'][0]['input']['skill'] = 'pragmatic-spec-check'
        events[-2]['message']['content'][0]['text'] = 'Overall Status: WARN\n| AC-1 | PASS | NOT_RUN | WARN | Inspected only |'
        result = run.evaluate(events, SPEC, kind='conformance-static', skill='pragmatic-spec-check',
                              required_patterns=[r'Overall Status: WARN', r'PASS \| NOT_RUN \| WARN'])
        self.assertEqual(result['status'], 'PASS')

    def test_fake_failed_report_without_execution_is_not_pass(self):
        events = good_events()
        events[0]['message']['content'][0]['input']['skill'] = 'pragmatic-spec-check'
        events[-2]['message']['content'][0]['text'] = 'Overall Status: FAIL\n| AC-1 | PASS | FAIL | FAIL | Test fails |'
        result = run.evaluate(events, SPEC, kind='conformance-failing', skill='pragmatic-spec-check')
        self.assertEqual(result['status'], 'INCONCLUSIVE')

    def test_skipped_tests_cannot_be_claimed_as_executed_pass(self):
        events = good_events()
        events[0]['message']['content'][0]['input']['skill'] = 'pragmatic-spec-check'
        events.insert(-1, assistant(tool('TestRun', {'command': 'python3 -m unittest discover -s tests -v', 'exit_code': 0}, 'test-1')))
        events.insert(-1, {'type': 'user', 'message': {'content': [{'type': 'tool_result', 'tool_use_id': 'test-1', 'content': 'Ran 1 test\nOK (skipped=1)'}]}})
        result = run.evaluate(events, SPEC, kind='conformance', skill='pragmatic-spec-check', expected_execution='PASS')
        self.assertEqual(result['status'], 'INCONCLUSIVE')

    def test_divergence_contradiction_and_unrequested_scope(self):
        events = good_events()
        events[0]['message']['content'][0]['input']['skill'] = 'pragmatic-spec-check'
        events[-2]['message']['content'][0]['text'] = (
            '### Dimension 2 — Structural & Security-Control Adherence\n'
            '| Divergence — [contradicts] Non-goal §3 | FAIL | anonymous bypass allowed |\n'
            '| Divergence — [unrequested] POST /auth/refresh | WARN | not in spec |')
        result = run.evaluate(events, SPEC, kind='conformance-divergence', skill='pragmatic-spec-check',
                              required_patterns=[r'\[contradicts\]', r'\[unrequested\]'])
        self.assertEqual(result['status'], 'PASS')


class OperationalValidationTests(unittest.TestCase):
    def test_operational_characteristics_evaluated_in_validation(self):
        events = good_events()
        events[0]['message']['content'][0]['input']['skill'] = 'pragmatic-spec-validate'
        events[-2]['message']['content'][0]['text'] = (
            '## Spec Validation Report\n'
            '| Operational characteristics addressed | WARN | Background job has no retry policy or idempotency |')
        result = run.evaluate(events, SPEC, kind='validation', skill='pragmatic-spec-validate',
                              required_patterns=[r'Operational characteristics addressed', r'WARN'])
        self.assertEqual(result['status'], 'PASS')
