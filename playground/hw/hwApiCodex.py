# API path: OpenAI SDK (MiniMax "compatible OpenAI API" — same key/model as Anthropic script)
# pip install openai
# run: cd D:\git\learningAgent
import json
from openai import OpenAI

modelJson='.env/model.json'
pickId='minimax-m27-highspeed'

with open(modelJson,encoding='utf-8') as f:
    dictModel=json.load(f)

for m in dictModel:
    if isinstance(m,dict) and m.get('id')==pickId:
        cfg=m
        break

apiKey=cfg.get('apiKey')
baseUrl=cfg.get('baseUrl',{}).get('openai')
modelName=cfg.get('model')

client=OpenAI(api_key=apiKey,base_url=baseUrl)
userMsg='Say hello in one short line; mention which model you are.'

resp=client.chat.completions.create(
    model=modelName,
    max_tokens=256,
    messages=[{'role':'user','content':userMsg}],
)

text=(resp.choices[0].message.content or '').strip()
if not text:
    raise SystemExit('empty response from API')
print(text)
