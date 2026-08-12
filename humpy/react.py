# ReAct loop: model <-> tools until final text (or maxRound)
import json

from humpy import tools as humpyTools
from humpy.message import appendToolRound,complete

OBS_MAX=8000

def run(modelCfg,sdk,system,message,*,toolLst,repoRoot,maxRound=6,maxToken=None,temperature=None,eventSink=None):
    '''
    message: mutable list of chat turns (no system row; system passed separately).
    eventSink(event): optional normalized per-round/tool trace callback.
    returns {text, usage, round, stopReason}
    '''
    if maxRound is None or maxRound<1:
        maxRound=6
    if toolLst is None:
        toolLst=humpyTools.schema()
    iRound=0
    last={'text':'','usage':None,'toolCall':[]}
    while iRound<maxRound:
        last=complete(modelCfg,sdk,message,system,maxToken=maxToken,temperature=temperature,toolLst=toolLst)
        toolCall=last.get('toolCall') or []
        roundNum=iRound+1
        if eventSink:
            eventSink({
                'entryType':'agent_round',
                'round':roundNum,
                'text':last.get('text') or '',
                'usage':last.get('usage'),
                'toolCalls':[{'id':tc['id'],'name':tc['name'],'arguments':tc.get('arg') or {}} for tc in toolCall],
            })
        if not toolCall:
            return {'text':last.get('text') or '','usage':last.get('usage'),'round':roundNum,'stopReason':'completed'}
        observationLst=[]
        for tc in toolCall:
            try:
                result=humpyTools.run(tc['name'],tc.get('arg') or {},repoRoot=repoRoot)
            except Exception as exc:
                result={'ok':False,'error':str(exc),'text':f'error: {exc}'}
            obs=result.get('text') or result.get('error') or json.dumps(result,ensure_ascii=False)
            if len(obs)>OBS_MAX:
                obs=obs[:OBS_MAX]+'\n...[truncated]'
            observationLst.append({'id':tc['id'],'content':obs})
            if eventSink:
                eventSink({
                    'entryType':'tool_result',
                    'round':roundNum,
                    'toolCallId':tc['id'],
                    'name':tc['name'],
                    'arguments':tc.get('arg') or {},
                    'result':result,
                    'observation':obs,
                })
        appendToolRound(sdk,message,last,observationLst)
        iRound+=1
    return {'text':last.get('text') or '','usage':last.get('usage'),'round':iRound,'stopReason':'max_round_exceeded'}
