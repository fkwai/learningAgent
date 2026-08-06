# ReAct loop — model ↔ tools until final text (or maxRound)
import json

from humpy import tools as humpyTools
from humpy.message import appendToolRound,complete

OBS_MAX=8000

def run(modelCfg,sdk,system,message,*,toolLst,repoRoot,maxRound=6,maxToken=None,temperature=None):
    '''
    message: mutable list of chat turns (no system row; system passed separately).
    returns {text, usage, round}
    '''
    if maxRound is None or maxRound<1:
        maxRound=6
    if toolLst is None:
        toolLst=humpyTools.schema()
    iRound=0
    last={'text':'','usage':None,'toolCall':[]}
    while iRound<maxRound:
        last=complete(
            modelCfg,
            sdk,
            message,
            system,
            maxToken=maxToken,
            temperature=temperature,
            toolLst=toolLst,
        )
        toolCall=last.get('toolCall') or []
        if not toolCall:
            return {
                'text':last.get('text') or '',
                'usage':last.get('usage'),
                'round':iRound+1,
            }
        observationLst=[]
        for tc in toolCall:
            result=humpyTools.run(tc['name'],tc.get('arg') or {},repoRoot=repoRoot)
            obs=result.get('text') or result.get('error') or json.dumps(result,ensure_ascii=False)
            if len(obs)>OBS_MAX:
                obs=obs[:OBS_MAX]+'\n...[truncated]'
            observationLst.append({'id':tc['id'],'content':obs})
        appendToolRound(sdk,message,last,observationLst)
        iRound+=1
    return {
        'text':last.get('text') or '',
        'usage':last.get('usage'),
        'round':iRound,
    }
