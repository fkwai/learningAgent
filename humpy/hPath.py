from pathlib import Path

PKG_DIR=Path(__file__).resolve().parent
ROOT_DIR=PKG_DIR.parent

def getDataDir():
    return str(ROOT_DIR/'.data')

def getHumpyJsonPath():
    return str(ROOT_DIR/'.env'/'humpy.json')

def getModelJsonPath():
    return str(ROOT_DIR/'.env'/'model.json')

def getBotDir(botName):
    return str(ROOT_DIR/'.data'/botName)

def getBotPromptPath(botName):
    return str(Path(getBotDir(botName))/'prompt.json')

def getBotSessionsDir(botName):
    return str(Path(getBotDir(botName))/'sessions')

def getBotIndexFile(botName):
    return str(Path(getBotDir(botName))/'index.jsonl')
