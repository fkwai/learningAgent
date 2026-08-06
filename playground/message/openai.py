# script version of humpy.message._completeOpenai
import json
from openai import OpenAI

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
out=humpy.message._completeOpenai(modelCfg,message,system,maxToken,temperature)

# --- script  ---
client=OpenAI(
    api_key=modelCfg.get('apiKey'),
    base_url=modelCfg.get('baseUrl',{}).get('openai'),
)
apiMessage=[{'role':'system','content':system}]
apiMessage.extend(message)
kwarg={
    'model':modelCfg.get('model'),
    'max_tokens':maxToken,
    'messages':apiMessage,
}
if temperature is not None:
    kwarg['temperature']=temperature
resp=client.chat.completions.create(**kwarg)
usage=None
if resp.usage:
    usage={'prompt':resp.usage.prompt_tokens,'completion':resp.usage.completion_tokens}
text=(resp.choices[0].message.content or '').strip()
result={'text':text,'usage':usage}

print(result['text'])
print(result['usage'])
