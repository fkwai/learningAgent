import importlib.util

PATHS_PY=r'D:/git/learningAgent/playground/agentProbe/_lib/paths.py'
spec=importlib.util.spec_from_file_location('agent_probe_paths',PATHS_PY)
paths=importlib.util.module_from_spec(spec)
spec.loader.exec_module(paths)
paths.load('codex')

from http_call import executeOneRound as _executeOneRound


def runCodexModelCall(*,modelRow,openaiMessages,messages,system,tools,maxOutputTokens,temperature):
    sdk=modelRow['sdk'].lower()
    apiMessages=openaiMessages if sdk=='openai' else messages
    return _executeOneRound(
        sdk=modelRow['sdk'],
        modelRow=modelRow,
        messages=apiMessages,
        system=system,
        tools=tools,
        toolShape='flat',
        maxOutputTokens=maxOutputTokens,
        temperature=temperature,
        transportTag='codex_shape',
    )
