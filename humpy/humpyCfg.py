import json
import os

from humpy import getHumpyJsonPath

def loadHumpyCfg():
    path=getHumpyJsonPath()
    if os.path.isfile(path):
        with open(path,encoding='utf-8') as f:
            cfg=json.load(f)
    else:
        cfg={}
    sdk=(os.environ.get('HUMPY_SDK','').strip() or cfg.get('sdk') or 'anthropic').lower()
    modelId=os.environ.get('LOCAL_MODEL_ID','').strip() or cfg.get('modelId') or 'minimax-m27-highspeed'
    defaultBot=os.environ.get('HUMPY_BOT','').strip() or cfg.get('defaultBot') or 'main'
    return {'sdk':sdk,'modelId':modelId,'defaultBot':defaultBot}
