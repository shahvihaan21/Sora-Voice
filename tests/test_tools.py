import pytest
from sora.intelligence.llm import parse_llm_output
from sora.tools.base import PermissionLevel, Tool, ToolResult
from sora.tools.registry import ToolRegistry

def test_parse_tool_json():
    decision = parse_llm_output('{"tool":"set_volume","args":{"percent":40}}')
    assert decision.is_tool_call and decision.tool == 'set_volume'
    assert decision.args['percent'] == 40

def test_parse_plain_reply():
    assert parse_llm_output('Hello there').reply == 'Hello there'

def test_validation_rejects_unknown_argument():
    tool = Tool('demo','demo',{'type':'object','properties':{'x':{'type':'integer'}},'required':['x']},lambda x: ToolResult.ok('ok'))
    registry = ToolRegistry(); registry.register(tool)
    assert registry.execute('demo', x=1, extra=2).error == 'invalid_arguments'

def test_confirmation_does_not_execute_until_confirmed():
    called=[]
    tool=Tool('danger','restart the machine',{'type':'object','properties':{}},lambda: (called.append(True) or ToolResult.ok('done')),PermissionLevel.DESTRUCTIVE)
    registry=ToolRegistry(); registry.register(tool)
    pending=registry.execute('danger')
    assert pending.needs_confirmation and not called
    assert registry.confirm().success and called

def test_confirmation_cancel():
    tool=Tool('danger','shutdown the machine',{'type':'object','properties':{}},lambda: ToolResult.ok('bad'),PermissionLevel.DESTRUCTIVE)
    registry=ToolRegistry(); registry.register(tool)
    registry.execute('danger'); result=registry.cancel()
    assert result.success and registry.pending_confirmation is None

def test_default_registry_has_core_tools():
    from sora.tools.registry import build_default_registry
    names=build_default_registry().names()
    for name in ('set_volume','set_brightness','open_app','run_diagnostic','shutdown_computer'):
        assert name in names
