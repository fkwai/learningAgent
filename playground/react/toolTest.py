# read_file as an LLM tool — call humpy.tools (schema + run)
# task: "Read humpy/README.md and summarize the package."
import json
from openai import OpenAI
from humpy.prompt import DEV_PROMPT_DEFAULT
from humpy import tools as humpyTools

repoRoot='D:/git/learningAgent'
userText='Read humpy/README.md and summarize the package.'
modelJson='.env/model.json'
pickId='minimax-m27-highspeed'

with open(modelJson,encoding='utf-8') as f:
    dictModel=json.load(f)
for m in dictModel:
    if isinstance(m,dict) and m.get('id')==pickId:
        modelCfg=m
        break

toolLst=humpyTools.schema()
system=DEV_PROMPT_DEFAULT
message=[{'role':'user','content':userText}]

client=OpenAI(
    api_key=modelCfg.get('apiKey'),
    base_url=modelCfg.get('baseUrl',{}).get('openai'),
)
resp=client.chat.completions.create(
    model=modelCfg.get('model'),
    messages=[{'role':'system','content':system}]+message,
    tools=toolLst,
    tool_choice='auto',
    max_tokens=1024,
)
msg=resp.choices[0].message
toolCall=msg.tool_calls or []

print('=== model content ===')
print(msg.content)
print('=== tool_calls ===')
print(json.dumps([
    {'id':tc.id,'name':tc.function.name,'arguments':tc.function.arguments}
    for tc in toolCall
],ensure_ascii=False,indent=2))

if not toolCall:
    print('no tool call — model answered without tools')
else:
    tc=toolCall[0]
    arg=json.loads(tc.function.arguments or '{}')
    print('\n=== execute',tc.function.name,'===')
    print('args:',arg)
    result=humpyTools.run(tc.function.name,arg,repoRoot=repoRoot)
    print('ok:',result.get('ok'),'path:',result.get('path'))
    preview=(result.get('text') or result.get('error') or '')[:500]
    print('--- observation ---')
    print(preview+('...' if len(result.get('text') or '')>500 else ''))
