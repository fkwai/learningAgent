import importlib.util

PATHS_PY=r'D:/git/learningAgent/playground/agentProbe/_lib/paths.py'
spec=importlib.util.spec_from_file_location('agent_probe_paths',PATHS_PY)
paths=importlib.util.module_from_spec(spec)
spec.loader.exec_module(paths)
paths.load('xiaoba')

from tools import buildXiaoBaTools
from prompt import buildXiaoBaCallContext,buildXiaoBaRequest
from call import runXiaoBaModelCall

from paths import OUT_XIAOBA
from task import DEFAULT_MAX_OUTPUT_TOKENS,DEFAULT_MODEL_ID,REPO_ROOT,USER_TASK
from model import loadProbeModel
from parse import parseFirstAction
from probe_io import printSection,saveJson

modelRow,botProf=loadProbeModel(DEFAULT_MODEL_ID)
tools=buildXiaoBaTools()
req=buildXiaoBaRequest(
    modelRow=modelRow,
    botProf=botProf,
    repoRoot=REPO_ROOT,
    userTask=USER_TASK,
    tools=tools,
    maxOutputTokens=DEFAULT_MAX_OUTPUT_TOKENS,
)
ctx=buildXiaoBaCallContext(req)

reqPath=OUT_XIAOBA+r'/request.json'
respPath=OUT_XIAOBA+r'/response.json'
saveJson(reqPath,req)

printSection('=== REQUEST PAYLOAD (XiaoBa wire) ===',req)

raw=runXiaoBaModelCall(
    modelRow=modelRow,
    openaiMessages=req['messages'],
    messages=ctx['messages'],
    system=ctx['system'],
    tools=tools,
    maxOutputTokens=DEFAULT_MAX_OUTPUT_TOKENS,
    temperature=req.get('temperature'),
)
saveJson(respPath,raw)
action=parseFirstAction(raw,textKind='assistant_text')

printSection('\n=== RAW MODEL RESPONSE ===',raw)
printSection('\n=== PARSED FIRST ACTION ===',action)
print(f'\nSaved: {reqPath}')
print(f'Saved: {respPath}')
