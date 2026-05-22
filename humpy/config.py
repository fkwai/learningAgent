import copy
import json
import os

from humpy.hPath import getBotJsonPath,getHumpyJsonPath,getModelJsonPath

def _loadJson(path):
    if not os.path.isfile(path):
        raise SystemExit(f'config not found: {path}')
    with open(path,encoding='utf-8') as f:
        return json.load(f)

def loadAgentCfg():
    return _loadJson(getHumpyJsonPath())

def loadHumpyCfg():
    return loadAgentCfg()

def loadBotCfg(botName):
    return _loadJson(getBotJsonPath(botName))

def loadModels():
    return _loadJson(getModelJsonPath())

def defaultBotProfile(agentCfg=None):
    agent=agentCfg or loadAgentCfg()
    return copy.deepcopy(agent['defaultBotProfile'])

def resolveBotSettings(botName):
    agent=loadAgentCfg()
    bot=loadBotCfg(botName)
    return {'agent':agent,'bot':bot}

def loadModel(pickId=None,botName=None):
    pid=pickId
    if not pid:
        if botName:
            pid=loadBotCfg(botName)['model']
        else:
            raise SystemExit('model id required')
    for m in loadModels():
        if isinstance(m,dict) and m.get('id')==pid:
            return m
    raise SystemExit(f'model id not found: {pid}')
