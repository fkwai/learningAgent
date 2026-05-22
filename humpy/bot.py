import copy
import json
import os

from humpy.config import defaultBotProfile,loadAgentCfg,loadBotCfg
from humpy.hPath import getBotDir,getBotIndexFile,getBotJsonPath,getBotPromptPath,getBotSessionsDir,getDataDir
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
        self._botCfg=None
        self._agentCfg=None

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
            if os.path.isdir(botDir) and os.path.isfile(getBotJsonPath(name)):
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
    def botJsonPath(self):
        return getBotJsonPath(self.name)

    @property
    def sessionsDir(self):
        return getBotSessionsDir(self.name)

    @property
    def indexFile(self):
        return getBotIndexFile(self.name)

    @property
    def agentCfg(self):
        if self._agentCfg is None:
            self._agentCfg=loadAgentCfg()
        return self._agentCfg

    @property
    def botCfg(self):
        if self._botCfg is None:
            self._botCfg=loadBotCfg(self.name)
        return self._botCfg

    def resolvedCfg(self):
        return {'agent':self.agentCfg,'bot':self.botCfg}

    def _writeBotJson(self,cfg):
        os.makedirs(self.dir,exist_ok=True)
        with open(self.botJsonPath,'w',encoding='utf-8') as f:
            json.dump(cfg,f,ensure_ascii=False,indent=2)
            f.write('\n')
        self._botCfg=cfg

    def _seedBotJson(self):
        cfg=defaultBotProfile(self.agentCfg)
        promptPath=getBotPromptPath(self.name)
        if os.path.isfile(promptPath):
            with open(promptPath,encoding='utf-8') as f:
                data=json.load(f)
            dev=(data.get('developer') or '').strip()
            if dev:
                cfg['developer']=dev
        self._writeBotJson(cfg)

    def ensure(self):
        os.makedirs(self.sessionsDir,exist_ok=True)
        if not os.path.isfile(self.botJsonPath):
            self._seedBotJson()

    def loadDeveloper(self):
        return (self.botCfg.get('developer') or '').strip() or DEV_PROMPT_DEFAULT
