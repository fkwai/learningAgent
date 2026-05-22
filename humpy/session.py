import os
from datetime import datetime,timezone

from humpy.bot import Bot
from humpy.config import loadModel,resolveBotSettings
from humpy.memory import pick,store
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
        resolved=resolveBotSettings(bot.name)
        self.agentCfg=resolved['agent']
        self.botCfg=resolved['bot']
        self.sdk=self.botCfg['sdk']
        modelId=pickId or self.botCfg['model']
        modelRow=loadModel(modelId)
        self.cfg=modelRow
        self.pickId=modelRow.get('id')
        self.modelName=modelRow.get('model')
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
            meta=store.getSessionMeta(self.indexFile,sid)
            if meta is not None and 'turnCount' in meta:
                self.turnCount=int(meta['turnCount'])
            else:
                self.turnCount=store.maxTurnInSession(self.sessionPath)
            if meta and (meta.get('headline') or '').strip():
                self.headline=(meta.get('headline') or '').strip()
                self.needsHeadline=False
            else:
                self.needsHeadline=self.botCfg['autoTitle']
        else:
            if exists:
                raise SystemExit(f'session already exists (use resume): {self.sessionPath}')
            if self.botCfg['saveSessions']:
                open(self.sessionPath,'a',encoding='utf-8').close()
            if not store.indexHasSession(self.indexFile,sid):
                store.registerSession(self.indexFile,{
                    'sessionId':sid,
                    'botName':bot.name,
                    'sessionFile':self.sessionPath.replace('\\','/'),
                    'modelId':self.pickId,
                    'model':self.modelName,
                    'headline':headline,
                    'createdAt':store.nowIso(),
                    'turnCount':0,
                })
            self.turnCount=0
            self.needsHeadline=self.botCfg['autoTitle'] and not (headline or '').strip()

    def maybeSummarizeHeadline(self,userText,assistantText):
        if not self.needsHeadline:
            return None
        self.needsHeadline=False
        snippet=(assistantText or '')[:self.botCfg['titleSnippetMaxChars']]
        prompt=f'User: {userText}\nAssistant: {snippet}'
        result=complete(
            self.cfg,
            self.sdk,
            [{'role':'user','content':prompt}],
            TITLE_PROMPT,
            maxTokens=self.botCfg['titleMaxOutputTokens'],
            temperature=self.botCfg['temperature'],
        )
        title=(result.get('text') or '').strip().split('\n')[0].strip()
        titleMax=self.botCfg['sessionTitleMaxChars']
        if not title:
            title=(userText or '').strip()[:titleMax] or self.sessionId
        title=title[:titleMax]
        if self.botCfg['saveSessions']:
            store.updateIndexHeadline(self.indexFile,self.sessionId,title)
        self.headline=title
        return title

    def turn(self,userText,maxTokens=None):
        if maxTokens is None:
            maxTokens=self.botCfg['maxOutputTokens']
        history,devFromFile=store.loadSessionHistory(self.sessionPath)
        developer=devFromFile or self.bot.loadDeveloper() or DEV_PROMPT_DEFAULT
        picked=pick.buildModelInput(
            developer=developer,
            history=history,
            userMessage=userText,
            botCfg=self.botCfg,
        )
        try:
            result=complete(
                self.cfg,
                self.sdk,
                picked['messages'],
                picked['system'],
                maxTokens=maxTokens,
                temperature=self.botCfg['temperature'],
            )
        except Exception as exc:
            raise SystemExit(f'model call failed: {exc}') from exc
        newHeadline=None
        if self.botCfg['saveSessions']:
            nextTurn=self.turnCount+1
            store.appendTurn(
                self.sessionPath,
                nextTurn,
                userText,
                result['text'],
                self.modelName,
                usage=result.get('usage'),
            )
            store.updateSessionMeta(self.indexFile,self.sessionId,{'turnCount':nextTurn})
            self.turnCount=nextTurn
            if self.botCfg['autoTitle'] and self.turnCount==1:
                newHeadline=self.maybeSummarizeHeadline(userText,result['text'])
        else:
            self.turnCount+=1
        return {
            'text':result['text'],
            'usage':result.get('usage'),
            'turn':self.turnCount,
            'sessionId':self.sessionId,
            'sessionPath':self.sessionPath,
            'botName':self.botName,
            'headline':newHeadline,
        }
