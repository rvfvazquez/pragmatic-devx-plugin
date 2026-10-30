"""Conservative normalization of Codex exec JSONL into the runner evidence schema.

Reading a local SKILL.md proves loading, not spontaneous Skill-tool activation.
Unknown commands/tools remain visible and prevent PASS.
"""
import re
import shlex


def unwrap_command(command):
    try:
        parts = shlex.split(command)
        if len(parts) == 3 and parts[0] in ('/bin/zsh', '/bin/bash', '/bin/sh', 'zsh', 'bash', 'sh') and parts[1] in ('-lc', '-c'):
            return parts[2]
    except ValueError:
        pass
    return command


def command_reads(command):
    """Return paths for plain cat/sed reads; None means not certified read-only."""
    try:
        command = unwrap_command(command)
        parts = shlex.split(command)
        if any(token in command for token in (';', '&', '|', '>', '<', '$', '`', '\n', '\r')):
            return None
        if parts and parts[0] == 'cat' and len(parts) > 1 and all(not p.startswith('-') for p in parts[1:]):
            return parts[1:]
        if len(parts) == 4 and parts[:2] == ['sed', '-n'] and re.fullmatch(r'\d+(,\d+)?p', parts[2]):
            return parts[3:]
        if parts in (['pwd'], ['ls'], ['rg', '--files']):
            return []
    except ValueError:
        pass
    return None


def normalize(events, skill):
    normalized = []
    errors = []

    def call(name, args, output='', failed=False):
        ident = 'codex-{}'.format(len(normalized))
        normalized.append({'type': 'assistant', 'message': {'content': [
            {'type': 'tool_use', 'id': ident, 'name': name, 'input': args}]}})
        normalized.append({'type': 'user', 'message': {'content': [
            {'type': 'tool_result', 'tool_use_id': ident, 'content': output, 'is_error': failed}]}})

    for event in events:
        if event.get('type') == 'turn.completed':
            normalized.append({'type': 'result', 'subtype': 'success', 'usage': event.get('usage', {}), 'is_error': False})
        elif event.get('type') in ('turn.failed', 'error'):
            errors.append(str(event.get('error', event.get('message', ''))))
            normalized.append({'type': 'result', 'subtype': 'error', 'is_error': True, 'result': str(event.get('error', event.get('message', '')) )})
        elif event.get('type') == 'item.started' and event.get('item', {}).get('type') == 'file_change':
            call('Edit', {'changes': event['item'].get('changes', [])})
        elif event.get('type') == 'item.completed':
            item = event.get('item', {})
            kind = item.get('type')
            if kind == 'agent_message':
                normalized.append({'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': item.get('text', '')}]}})
            elif kind == 'command_execution':
                command = unwrap_command(item.get('command', ''))
                output = item.get('aggregated_output', '')
                failed = item.get('exit_code') != 0 or item.get('status') != 'completed'
                paths = command_reads(command)
                if paths is not None:
                    for path in paths:
                        if path.endswith('/' + skill + '/SKILL.md'):
                            call('Skill', {'skill': skill}, output, failed)
                        call('Read', {'file_path': path}, output, failed)
                elif re.fullmatch(r'python3? (?:-B )?-m unittest discover -s tests -v', command):
                    call('TestRun', {'command': command, 'exit_code': item.get('exit_code')}, output, failed)
                else:
                    call('UnsupportedCodexTool', {'command': command}, output, failed)
            elif kind == 'file_change':
                call('Edit', {'changes': item.get('changes', [])})
            elif kind not in ('reasoning', 'plan', 'todo_list'):
                call('UnsupportedCodexTool', {'item': item})
    if errors:
        normalized.append({'type': 'result', 'subtype': 'error', 'is_error': True, 'result': '\n'.join(errors)})
    return normalized
