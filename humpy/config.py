import json
import os

from humpy.hPath import ROOT_DIR,getHumpyJsonPath,getModelJsonPath

def _loadJson(path):
    if not os.path.isfile(path):
        raise SystemExit(f'config not found: {path}')
    with open(path,encoding='utf-8') as f:
        return json.load(f)

def _mergeDict(base,over):
    out=dict(base)
    for k,v in (over or {}).items():
        if isinstance(v,dict) and isinstance(out.get(k),dict):
            out[k]=_mergeDict(out[k],v)
        else:
            out[k]=v
    return out

def loadHumpyCfg():
    return _loadJson(getHumpyJsonPath())

def loadModels():
    return _loadJson(getModelJsonPath())

def resolvePromptPath(promptFile,botPromptPath):
    if not promptFile:
        return botPromptPath
    p=str(promptFile).strip()
    if os.path.isabs(p):
        return p
    return str(ROOT_DIR/p)

def resolveBotSettings(botName):
    cfg=loadHumpyCfg()
    bots=cfg['bots']
    botCfg=_mergeDict(bots['default'],bots.get(botName) or {})
    botCfg['model']=botCfg.get('model') or cfg['modelId']
    botCfg['sdk']=cfg['sdk']
    botCfg['promptPath']=resolvePromptPath(botCfg.get('promptFile'),'')
    return {'cfg':cfg,'bot':botCfg}

def loadModel(pickId=None):
    cfg=loadHumpyCfg()
    pid=pickId or cfg['modelId']
    for m in loadModels():
        if isinstance(m,dict) and m.get('id')==pid:
            return m
    raise SystemExit(f'model id not found: {pid}')
