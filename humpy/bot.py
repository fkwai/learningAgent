import json
import os

from humpy.hPath import getBotDir,getBotIndexFile,getBotPromptPath,getBotSessionsDir,getDataDir
from humpy.prompt import DEV_PROMPT_DEFAULT

class Bot:
    RESERVED={'new','others'}

    def __init__(self,name):
        n=(name or '').strip()
        if not n:
            raise ValueError('bot name required')
        if self.isReserved(n):
            raise ValueError('bot name cannot be "new" or "others"')
        self.name=n

    @classmethod
    def isReserved(cls,name):
        return (name or '').strip().lower() in cls.RESERVED

    @classmethod
    def list(cls):
        dataDir=getDataDir()
        if not os.path.isdir(dataDir):
            return []
        out=[]
        for name in sorted(os.listdir(dataDir)):
            if cls.isReserved(name):
                continue
            botDir=os.path.join(dataDir,name)
            if os.path.isdir(botDir) and os.path.isfile(getBotPromptPath(name)):
                out.append(cls(name))
        return out

    @classmethod
    def listNames(cls):
        return [b.name for b in cls.list()]

    @classmethod
    def adopt(cls,name):
        n=(name or '').strip()
        if not n or cls.isReserved(n):
            return None
        bot=cls(n)
        bot.ensure()
        return bot

    @property
    def dir(self):
        return getBotDir(self.name)

    @property
    def promptPath(self):
        return getBotPromptPath(self.name)

    @property
    def sessionsDir(self):
        return getBotSessionsDir(self.name)

    @property
    def indexFile(self):
        return getBotIndexFile(self.name)

    def ensure(self):
        os.makedirs(self.sessionsDir,exist_ok=True)
        if not os.path.isfile(self.promptPath):
            os.makedirs(self.dir,exist_ok=True)
            with open(self.promptPath,'w',encoding='utf-8') as f:
                json.dump({'developer':DEV_PROMPT_DEFAULT},f,ensure_ascii=False,indent=2)
                f.write('\n')

    def loadDeveloper(self):
        if not os.path.isfile(self.promptPath):
            return DEV_PROMPT_DEFAULT
        with open(self.promptPath,encoding='utf-8') as f:
            data=json.load(f)
        return (data.get('developer') or '').strip() or DEV_PROMPT_DEFAULT
