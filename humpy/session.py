import os

from humpy.bot import Bot
from humpy.config import loadModel,resolveBotSettings
from humpy.hPath import ROOT_DIR
from humpy.memory import pick,store
from humpy import react
from humpy import tools as humpyTools
from humpy.prompt import DEV_PROMPT_DEFAULT
from humpy.utils import newSessionId

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
        sid=sessionId or newSessionId(prefix)
        self.sessionId=sid
        self.sessionPath=os.path.join(bot.sessionDir,sid+'.jsonl')
        self.headline=headline
        self.needsHeadline=False
        exists=os.path.isfile(self.sessionPath)
        if resume:
            if not exists:
                raise SystemExit(f'session not found: {self.sessionPath}')
            meta=store.getSessionMeta(self.indexFile,sid)
            self.turnCount=store.sessionTurnCount(self.sessionPath)
            if meta and (meta.get('headline') or '').strip():
                self.headline=(meta.get('headline') or '').strip()
            else:
                self.needsHeadline=self.botCfg['autoTitle']
        else:
            if exists:
                raise SystemExit(f'session already exists (use resume): {self.sessionPath}')
            if self.botCfg['saveSessions']:
                open(self.sessionPath,'a',encoding='utf-8').close()
            if not store.indexHasSession(self.indexFile,sid):
                store.registerSession(self.indexFile,{
                    'sessionId':sid,'botName':bot.name,'sessionFile':self.sessionPath.replace('\\','/'),
                    'modelId':self.pickId,'model':self.modelName,'headline':headline,'createdAt':store.nowIso(),
                })
            self.turnCount=0
            self.needsHeadline=self.botCfg['autoTitle'] and not (headline or '').strip()

    def applyAutoTitle(self,userText):
        if not self.needsHeadline:
            return None
        self.needsHeadline=False
        titleMax=self.botCfg['sessionTitleMaxChars']
        title=(userText or '').strip()[:titleMax] or self.sessionId
        if self.botCfg['saveSessions']:
            store.updateIndexHeadline(self.indexFile,self.sessionId,title)
        self.headline=title
        return title

    def turn(self,userText,maxToken=None):
        if maxToken is None:
            maxToken=self.botCfg['maxOutputTokens']
        history,devFromFile=store.loadSessionHistory(self.sessionPath)
        developer=devFromFile or self.bot.loadDeveloper() or DEV_PROMPT_DEFAULT
        picked=pick.buildModelInput(developer=developer,history=history,userMessage=userText,botCfg=self.botCfg)
        turnNum=self.turnCount+1
        eventSink=None
        if self.botCfg['saveSessions']:
            store.appendUser(self.sessionPath,turnNum,userText)
            self.turnCount=turnNum

            def eventSink(event):
                row=dict(event)
                entryType=row.pop('entryType')
                roundNum=row.pop('round',None)
                store.appendTraceEvent(self.sessionPath,turnNum,entryType,roundNum=roundNum,**row)
        try:
            result=react.run(
                self.cfg,self.sdk,picked['system'],list(picked['messages']),
                toolLst=humpyTools.schema(),repoRoot=str(ROOT_DIR),
                maxRound=self.botCfg.get('maxAgentRound',6),maxToken=maxToken,
                temperature=self.botCfg['temperature'],eventSink=eventSink,
            )
        except Exception as exc:
            if self.botCfg['saveSessions']:
                store.appendTraceEvent(self.sessionPath,turnNum,'turn_end',status='model_error',error=str(exc))
            else:
                self.turnCount=turnNum
            raise SystemExit(f'model call failed: {exc}') from exc
        newHeadline=None
        if self.botCfg['saveSessions']:
            store.appendAssistant(self.sessionPath,turnNum,result['text'],self.modelName,usage=result.get('usage'))
            store.appendTraceEvent(
                self.sessionPath,turnNum,'turn_end',
                status=result.get('stopReason') or 'completed',rounds=result.get('round'),
            )
            if self.botCfg['autoTitle'] and self.turnCount==1:
                newHeadline=self.applyAutoTitle(userText)
        else:
            self.turnCount=turnNum
        return {
            'text':result['text'],'usage':result.get('usage'),'round':result.get('round'),
            'stopReason':result.get('stopReason'),'turn':self.turnCount,'sessionId':self.sessionId,
            'sessionPath':self.sessionPath,'botName':self.botName,'headline':newHeadline,
        }
