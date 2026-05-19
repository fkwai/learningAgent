import os
from datetime import datetime,timezone

from humpy.bot import Bot
from humpy.config import loadHumpyCfg,loadModel
from humpy.memory import (
    appendAssistant,
    appendUser,
    indexHasSession,
    loadMessages,
    maxTurnInSession,
    nowIso,
    registerSession,
    updateIndexHeadline,
)
from humpy.message import complete
from humpy.prompt import DEV_PROMPT_DEFAULT,TITLE_PROMPT

class ChatSession:
    def __init__(self,bot,sessionId=None,resume=False,headline='',pickId=None,prefix=''):
        if isinstance(bot,str):
            bot=Bot.adopt(bot)
            if not bot:
                raise ValueError('invalid bot name')
        elif not isinstance(bot,Bot):
            raise TypeError('bot must be Bot or str')
        self.bot=bot
        self.botName=bot.name
        bot.ensure()
        humpyCfg=loadHumpyCfg()
        self.sdk=humpyCfg['sdk']
        cfg=loadModel(pickId)
        self.cfg=cfg
        self.pickId=cfg.get('id')
        self.modelName=cfg.get('model')
        self.indexFile=bot.indexFile
        if sessionId:
            sid=sessionId
        else:
            stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
            sid=(prefix+stamp) if prefix else stamp
        self.sessionId=sid
        self.sessionPath=os.path.join(bot.sessionsDir,sid+'.jsonl')
        self.headline=headline
        self.needsHeadline=False
        exists=os.path.isfile(self.sessionPath)
        if resume:
            if not exists:
                raise SystemExit(f'session not found: {self.sessionPath}')
            self.turnNum=maxTurnInSession(self.sessionPath)
        else:
            if exists:
                raise SystemExit(f'session already exists (use resume): {self.sessionPath}')
            open(self.sessionPath,'a',encoding='utf-8').close()
            if not indexHasSession(self.indexFile,sid):
                registerSession(self.indexFile,{
                    'sessionId':sid,
                    'botName':bot.name,
                    'sessionFile':self.sessionPath.replace('\\','/'),
                    'modelId':self.pickId,
                    'model':self.modelName,
                    'headline':headline,
                    'createdAt':nowIso(),
                })
            self.turnNum=0
            self.needsHeadline=not (headline or '').strip()

    def maybeSummarizeHeadline(self,userText,assistantText,maxTokens=64):
        if not self.needsHeadline:
            return None
        self.needsHeadline=False
        snippet=(assistantText or '')[:500]
        prompt=f'User: {userText}\nAssistant: {snippet}'
        result=complete(
            self.cfg,
            self.sdk,
            [{'role':'user','content':prompt}],
            TITLE_PROMPT,
            maxTokens=maxTokens,
        )
        title=(result.get('text') or '').strip().split('\n')[0].strip()
        if not title:
            title=(userText or '').strip()[:48] or self.sessionId
        title=title[:80]
        updateIndexHeadline(self.indexFile,self.sessionId,title)
        self.headline=title
        return title

    def turn(self,userText,maxTokens=1024):
        self.turnNum+=1
        appendUser(self.sessionPath,self.turnNum,userText)
        messages,devFromFile=loadMessages(self.sessionPath)
        dev=devFromFile or self.bot.loadDeveloper() or DEV_PROMPT_DEFAULT
        result=complete(self.cfg,self.sdk,messages,dev,maxTokens=maxTokens)
        appendAssistant(
            self.sessionPath,
            self.turnNum,
            result['text'],
            self.modelName,
            usage=result.get('usage'),
        )
        newHeadline=None
        if self.turnNum==1:
            newHeadline=self.maybeSummarizeHeadline(userText,result['text'])
        return {
            'text':result['text'],
            'usage':result.get('usage'),
            'turn':self.turnNum,
            'sessionId':self.sessionId,
            'sessionPath':self.sessionPath,
            'botName':self.botName,
            'headline':newHeadline,
        }
