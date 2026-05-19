import json
import os

from humpy import getModelJsonPath

def loadModel(pickId=None):
    pid=pickId or os.environ.get('LOCAL_MODEL_ID','').strip()
    if not pid:
        from humpy.humpyCfg import loadHumpyCfg
        pid=loadHumpyCfg()['modelId']
    with open(getModelJsonPath(),encoding='utf-8') as f:
        dictModel=json.load(f)
    for m in dictModel:
        if isinstance(m,dict) and m.get('id')==pid:
            return m
    raise SystemExit(f'model id not found: {pid}')
