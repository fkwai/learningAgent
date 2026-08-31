import json
import os


def ensureDir(path):
    os.makedirs(path,exist_ok=True)


def saveJson(path,payload):
    ensureDir(os.path.dirname(path))
    with open(path,'w',encoding='utf-8') as f:
        json.dump(payload,f,ensure_ascii=False,indent=2)


def printSection(title,payload):
    print(title)
    print(json.dumps(payload,ensure_ascii=False,indent=2))
