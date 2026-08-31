import importlib.util

PATHS_PY=r'D:/git/learningAgent/playground/agentProbe/_lib/paths.py'
spec=importlib.util.spec_from_file_location('agent_probe_paths',PATHS_PY)
paths=importlib.util.module_from_spec(spec)
spec.loader.exec_module(paths)
paths.load('codex')

from tools import buildCodexTools
from prompt import buildCodexCallContext,buildCodexRequest
from call import runCodexModelCall

from paths import OUT_CODEX
from task import DEFAULT_MAX_OUTPUT_TOKENS,DEFAULT_MODEL_ID,REPO_ROOT,USER_TASK
from model import loadProbeModel
from parse import parseFirstAction
from probe_io import printSection,saveJson

modelRow,botProf=loadProbeModel(DEFAULT_MODEL_ID)
tools=buildCodexTools()
req=buildCodexRequest(
    modelRow=modelRow,
    botProf=botProf,
    repoRoot=REPO_ROOT,
    userTask=USER_TASK,
    tools=tools,
    maxOutputTokens=DEFAULT_MAX_OUTPUT_TOKENS,
)
ctx=buildCodexCallContext(req)

reqPath=OUT_CODEX+r'/request.json'
respPath=OUT_CODEX+r'/response.json'
saveJson(reqPath,req)

printSection('=== REQUEST PAYLOAD (Codex wire) ===',req)

raw=runCodexModelCall(
    modelRow=modelRow,
    openaiMessages=ctx['openaiMessages'],
    messages=ctx['messages'],
    system=ctx['system'],
    tools=tools,
    maxOutputTokens=DEFAULT_MAX_OUTPUT_TOKENS,
    temperature=req.get('temperature'),
)
saveJson(respPath,raw)
action=parseFirstAction(raw,textKind='final_text')

printSection('\n=== RAW MODEL RESPONSE ===',raw)
printSection('\n=== PARSED FIRST ACTION ===',action)
print(f'\nSaved: {reqPath}')
print(f'Saved: {respPath}')
