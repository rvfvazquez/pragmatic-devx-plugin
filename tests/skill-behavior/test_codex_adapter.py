import unittest
from codex_adapter import normalize, command_reads

SKILL = '.agents/skills/pragmatic-spec-build/SKILL.md'
SPEC = 'docs/specs/customer-registration.md'


def command(text, output='', code=0):
    return {'type': 'item.completed', 'item': {'id': 'cmd-1', 'type': 'command_execution',
            'command': text, 'aggregated_output': output, 'exit_code': code, 'status': 'completed'}}


class CodexAdapterTests(unittest.TestCase):
    def test_read_commands_are_narrowly_recognized(self):
        self.assertEqual(command_reads('/bin/zsh -lc "cat ' + SPEC + '"'), [SPEC])
        self.assertEqual(command_reads("sed -n '1,80p' " + SKILL), [SKILL])
        for text in ['cat spec; touch app.py', 'cat spec > app.py', 'python3 evil.py', 'cat $(touch app.py)',
                     "cat <(touch app.py)", "cat `touch app.py`", 'cat spec && cat other', 'env cat spec']:
            self.assertIsNone(command_reads(text), text)

    def test_completed_read_produces_successful_skill_evidence(self):
        events = normalize([command('cat ' + SKILL, '# pragmatic-spec-build\nDraft hard gate'),
                            {'type': 'turn.completed', 'usage': {'input_tokens': 1}}], 'pragmatic-spec-build')
        self.assertTrue(any(e.get('type') == 'user' for e in events))
        self.assertEqual(events[-1]['subtype'], 'success')

    def test_failed_skill_read_does_not_activate(self):
        events = normalize([command('cat ' + SKILL, 'permission denied', 1)], 'pragmatic-spec-build')
        self.assertFalse(any(e.get('type') == 'user' and not e['message']['content'][0].get('is_error') for e in events))

    def test_file_change_and_unknown_commands_do_not_disappear(self):
        events = normalize([{'type': 'item.completed', 'item': {'id': 'x', 'type': 'file_change', 'status': 'completed', 'changes': []}},
                            command('python3 -c "pass"')], 'pragmatic-spec-build')
        names = [b['name'] for e in events for b in e.get('message', {}).get('content', []) if b.get('type') == 'tool_use']
        self.assertIn('Edit', names)
        self.assertIn('UnsupportedCodexTool', names)

    def test_failure_after_turn_completion_overrides_success(self):
        events = normalize([{'type': 'turn.completed'}, {'type': 'turn.failed', 'error': {'message': 'auth'}}], 'pragmatic-spec-build')
        self.assertTrue(events[-1]['is_error'])

    def test_top_level_error_without_turn_failed_cannot_pass(self):
        events = normalize([{'type': 'error', 'message': 'connection failed'}], 'pragmatic-spec-build')
        self.assertTrue(events[-1]['is_error'])

    def test_skipped_command_is_not_successful_evidence(self):
        event = command('cat ' + SPEC, 'Status: Draft [TODO: storage]')
        event['item']['status'] = 'failed'
        events = normalize([event], 'pragmatic-spec-build')
        results = [b for e in events for b in e.get('message', {}).get('content', []) if b.get('type') == 'tool_result']
        self.assertTrue(all(r['is_error'] for r in results))

    def test_error_before_completed_turn_stays_error(self):
        events = normalize([{'type': 'error', 'message': 'failed'}, {'type': 'turn.completed'}], 'pragmatic-spec-build')
        self.assertTrue(events[-1]['is_error'])

    def test_shell_wrapped_test_run_preserves_failed_assertion(self):
        events = normalize([command('/bin/zsh -lc "python3 -m unittest discover -s tests -v"', 'AssertionError: 1 != 2', 1)], 'pragmatic-spec-check')
        call = events[0]['message']['content'][0]
        self.assertEqual(call['name'], 'TestRun')
        self.assertEqual(call['input']['exit_code'], 1)
