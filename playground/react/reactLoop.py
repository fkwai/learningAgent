# ReAct loop — tools until the model stops calling them
# task: find where this repo sets up paths (expect humpy/hPath.py)
import json
from openai import OpenAI
from humpy.prompt import DEV_PROMPT_DEFAULT
from humpy import tools as humpyTools

repoRoot='D:/git/learningAgent'
userText=(
    'In this repo (root: D:/git/learningAgent), find the code that sets up '
    'paths for .env, .data, and bot dirs. Name the file and briefly explain '
    'how ROOT_DIR / PKG_DIR work. Use list_dir and read_file; do not invent paths.'
)
modelJson='.env/model.json'
pickId='minimax-m27-highspeed'
maxRound=6

with open(modelJson,encoding='utf-8') as f:
    dictModel=json.load(f)
for m in dictModel:
    if isinstance(m,dict) and m.get('id')==pickId:
        modelCfg=m
        break

toolLst=humpyTools.schema()
system=DEV_PROMPT_DEFAULT
message=[
    {'role':'system','content':system},
    {'role':'user','content':userText},
]

client=OpenAI(
    api_key=modelCfg.get('apiKey'),
    base_url=modelCfg.get('baseUrl',{}).get('openai'),
)

iRound=0


while iRound < maxRound:
    print(f'\n===== round {iRound} =====')
    resp = client.chat.completions.create(
        model=modelCfg.get('model'),
        messages=message,
        tools=toolLst,
        tool_choice='auto',
        max_tokens=2048,
    )
    msg = resp.choices[0].message
    toolCall = msg.tool_calls or []

    print('content:', msg.content)
    if toolCall:
        print(
            'tool_calls:',
            json.dumps([{
                'id': tc.id,
                'name': tc.function.name,
                'arguments': tc.function.arguments
            } for tc in toolCall],
                       ensure_ascii=False,
                       indent=2))

    if not toolCall:
        print('\n=== final answer (no more tools) ===')
        print(msg.content)
        break

    message.append({
        'role':
        'assistant',
        'content':
        msg.content,
        'tool_calls': [{
            'id': tc.id,
            'type': 'function',
            'function': {
                'name': tc.function.name,
                'arguments': tc.function.arguments
            },
        } for tc in toolCall],
    })

    for tc in toolCall:
        arg = json.loads(tc.function.arguments or '{}')
        print(f'execute {tc.function.name}', arg)
        result = humpyTools.run(tc.function.name, arg, repoRoot=repoRoot)
        obs = result.get('text') or result.get('error') or json.dumps(
            result, ensure_ascii=False)
        if len(obs) > 8000:
            obs = obs[:8000] + '\n...[truncated]'
        print('observation preview:',
              obs[:400] + ('...' if len(obs) > 400 else ''))
        message.append({
            'role': 'tool',
            'tool_call_id': tc.id,
            'content': obs,
        })
    iRound += 1
else:
    print('\n=== stopped: hit maxRound ===')
