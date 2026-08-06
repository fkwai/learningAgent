# script version of humpy.message._completeAnthropic
import json
from anthropic import Anthropic

modelJson='.env/model.json'
pickId='minimax-m27-highspeed'

with open(modelJson,encoding='utf-8') as f:
    dictModel=json.load(f)

for m in dictModel:
    if isinstance(m,dict) and m.get('id')==pickId:
        modelCfg=m
        break

system='Be concise.'
message=[{'role':'user','content':'Say hello in one short line; mention which model you are.'}]
maxToken=256
temperature=None

# --- function ---
import humpy.message
out=humpy.message._completeAnthropic(modelCfg,message,system,maxToken,temperature)

# --- script  ---
kwarg={
    'model':modelCfg.get('model'),
    'max_tokens':maxToken,
    'system':system,
    'messages':message,
}
if temperature is not None:
    kwarg['temperature']=temperature
client=Anthropic(
    api_key=modelCfg.get('apiKey'),
    base_url=modelCfg.get('baseUrl',{}).get('anthropic'),
)
resp=client.messages.create(**kwarg)
usage=None
if resp.usage:
    usage={'prompt':resp.usage.input_tokens,'completion':resp.usage.output_tokens}
outBlock=[]
for block in resp.content:
    if block.type=='text':
        outBlock.append(block.text)
result={'text':'\n'.join(outBlock).strip(),'usage':usage}

print(result['text'])
print(result['usage'])
