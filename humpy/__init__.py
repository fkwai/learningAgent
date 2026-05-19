import json
import os

from humpy.prompt import DEV_PROMPT_DEFAULT

def getRepoPath():
    envRepo=os.environ.get('REPO_PATH','').strip()
    if envRepo:
        return os.path.abspath(envRepo)
    cwd=os.getcwd()
    if os.path.isdir(os.path.join(cwd,'.env')):
        return cwd
    localJson=os.environ.get('LOCAL_JSON','').strip()
    if not localJson:
        cur=cwd
        for _ in range(20):
            cand=os.path.join(cur,'.env','local.json')
            if os.path.isfile(cand):
                localJson=cand
                break
            parent=os.path.dirname(cur)
            if parent==cur:
                break
            cur=parent
    if localJson and os.path.isfile(localJson):
        with open(localJson,encoding='utf-8') as f:
            data=json.load(f)
        repo=data.get('repoPath') or data.get('repo')
        if repo:
            return os.path.abspath(repo)
    return cwd

def getDataDir():
    return os.path.join(getRepoPath(),'.data')

def getHumpyJsonPath():
    envPath=os.environ.get('HUMPY_JSON','').strip()
    if envPath:
        return os.path.abspath(envPath)
    return os.path.join(getRepoPath(),'.env','humpy.json')

def getModelJsonPath():
    envPath=os.environ.get('MODEL_JSON','').strip()
    if envPath:
        return os.path.abspath(envPath)
    return os.path.join(getRepoPath(),'.env','model.json')

def getBotDir(botName):
    return os.path.join(getDataDir(),botName)

def getBotPromptPath(botName):
    return os.path.join(getBotDir(botName),'prompt.json')

def getBotSessionsDir(botName):
    return os.path.join(getBotDir(botName),'sessions')

def getBotIndexFile(botName):
    return os.path.join(getBotDir(botName),'index.jsonl')

def listBots():
    dataDir=getDataDir()
    if not os.path.isdir(dataDir):
        return []
    out=[]
    for name in sorted(os.listdir(dataDir)):
        botDir=os.path.join(dataDir,name)
        if os.path.isdir(botDir) and os.path.isfile(getBotPromptPath(name)):
            out.append(name)
    return out

def ensureBotDirs(botName):
    os.makedirs(getBotSessionsDir(botName),exist_ok=True)
    promptPath=getBotPromptPath(botName)
    if not os.path.isfile(promptPath):
        os.makedirs(getBotDir(botName),exist_ok=True)
        with open(promptPath,'w',encoding='utf-8') as f:
            json.dump({'developer':DEV_PROMPT_DEFAULT},f,ensure_ascii=False,indent=2)
            f.write('\n')

def loadBotDeveloper(botName):
    promptPath=getBotPromptPath(botName)
    if not os.path.isfile(promptPath):
        return DEV_PROMPT_DEFAULT
    with open(promptPath,encoding='utf-8') as f:
        data=json.load(f)
    return (data.get('developer') or '').strip() or DEV_PROMPT_DEFAULT

__all__=[
    'DEV_PROMPT_DEFAULT',
    'getRepoPath',
    'getDataDir',
    'getHumpyJsonPath',
    'getModelJsonPath',
    'getBotDir',
    'getBotPromptPath',
    'getBotSessionsDir',
    'getBotIndexFile',
    'listBots',
    'ensureBotDirs',
    'loadBotDeveloper',
]
