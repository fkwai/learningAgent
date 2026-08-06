# script + function version of humpy.react.run
# task: find path setup code (humpy/hPath.py)
import json
from openai import OpenAI
from humpy.hPath import ROOT_DIR
from humpy.prompt import DEV_PROMPT_DEFAULT
from humpy import tools as humpyTools
from humpy.config import loadModel

repoRoot=str(ROOT_DIR)
userText=(
    'In this repo (root: '+repoRoot+'), find the code that sets up '
    'paths for .env, .data, and bot dirs. Name the file and briefly explain '
    'how ROOT_DIR / PKG_DIR work. Use tools; do not invent paths.'
)
pickId='minimax-m27-highspeed'
sdk='openai'
maxRound=6
maxToken=2048
temperature=0.7
OBS_MAX=8000

modelCfg=loadModel(pickId)
toolLst=humpyTools.schema()
system=DEV_PROMPT_DEFAULT

# --- function ---
import humpy.react
messageFn=[{'role':'user','content':userText}]
out=humpy.react.run(
    modelCfg,
    sdk,
    system,
    messageFn,
    toolLst=toolLst,
    repoRoot=repoRoot,
    maxRound=maxRound,
    maxToken=maxToken,
    temperature=temperature,
)

# --- script  ---
message=[{'role':'user','content':userText}]
client=OpenAI(
    api_key=modelCfg.get('apiKey'),
    base_url=modelCfg.get('baseUrl',{}).get('openai'),
)
iRound=0
last={'text':'','usage':None}
while iRound<maxRound:
    apiMessage=[{'role':'system','content':system}]
    apiMessage.extend(message)
    kwarg={
        'model':modelCfg.get('model'),
        'max_tokens':maxToken,
        'messages':apiMessage,
        'tools':toolLst,
        'tool_choice':'auto',
    }
    if temperature is not None:
        kwarg['temperature']=temperature
    resp=client.chat.completions.create(**kwarg)
    usage=None
    if resp.usage:
        usage={'prompt':resp.usage.prompt_tokens,'completion':resp.usage.completion_tokens}
    msg=resp.choices[0].message
    text=(msg.content or '').strip()
    toolCall=msg.tool_calls or []
    last={'text':text,'usage':usage}
    if not toolCall:
        result={'text':text,'usage':usage,'round':iRound+1}
        break
    message.append({
        'role':'assistant',
        'content':msg.content,
        'tool_calls':[
            {
                'id':tc.id,
                'type':'function',
                'function':{'name':tc.function.name,'arguments':tc.function.arguments or '{}'},
            }
            for tc in toolCall
        ],
    })
    for tc in toolCall:
        try:
            arg=json.loads(tc.function.arguments or '{}')
        except json.JSONDecodeError:
            arg={}
        toolResult=humpyTools.run(tc.function.name,arg,repoRoot=repoRoot)
        obs=toolResult.get('text') or toolResult.get('error') or json.dumps(toolResult,ensure_ascii=False)
        if len(obs)>OBS_MAX:
            obs=obs[:OBS_MAX]+'\n...[truncated]'
        message.append({
            'role':'tool',
            'tool_call_id':tc.id,
            'content':obs,
        })
    iRound+=1
else:
    result={'text':last.get('text') or '','usage':last.get('usage'),'round':iRound}

print('=== function out ===')
print(out.get('text'))
print('usage:',out.get('usage'),'round:',out.get('round'))
print('\n=== script result ===')
print(result.get('text'))
print('usage:',result.get('usage'),'round:',result.get('round'))
