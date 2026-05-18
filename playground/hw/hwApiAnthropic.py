import json
import os
import sys
from anthropic import Anthropic

modelJson='.env/model.json'
pickId='minimax-m27-highspeed'

with open(modelJson,encoding='utf-8') as f:
    dictModel=json.load(f)

for m in dictModel:
    if isinstance(m,dict) and m.get('id')==pickId:
        cfg=m
        break
apiKey=cfg.get('apiKey')
baseUrl=cfg.get('baseUrl',{}).get('anthropic')
modelName=cfg.get('model')

client=Anthropic(api_key=apiKey,base_url=baseUrl)
userMsg='Say hello in one short line; mention which model you are.'


msg=client.messages.create(
    model=modelName,
    max_tokens=256,
    messages=[{'role':'user','content':userMsg}]
)

out=[]
for block in msg.content:
    if block.type=='text':
        out.append(block.text)
text='\n'.join(out).strip()
if not text:
    raise SystemExit('empty response from API')
print(text)
