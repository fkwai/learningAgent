# One-round XiaoBa-shaped probe (no tool execution).
# Run line-by-line in a Python REPL or paste blocks into terminal.
#
# Source refs: src/core/conversation-runner.ts ConversationRunner.run
#              src/providers/openai-provider.ts buildRequestBody
#              prompts/system-prompt.md

import json
import os
import sys

# --- inputs ---
repoRoot=r'D:/git/learningAgent'
userTask='Read this repo and figure out what it is doing. Start by inspecting the project structure.'
modelId='minimax-m27-highspeed'
maxOutputTokens=2000

rootDir=r'D:/git/learningAgent'
outDir=r'D:/git/learningAgent/playground/agentProbe/out'
sys.path.insert(0,rootDir)

from humpy.config import loadModel,loadAgentCfg

# --- load model config ---
modelRow=loadModel(modelId)
agentCfg=loadAgentCfg()
botProf=agentCfg.get('defaultBotProfile',{})
if not modelRow.get('sdk'):
    modelRow['sdk']=botProf.get('sdk','anthropic')
sdk=modelRow['sdk'].lower()

# --- XiaoBa system + user messages (chat completions shape) ---
xiaobaSystem=(
    'You are the user\'s personal assistant: careful, reliable, and able to collaborate over time.\n\n'
    'Operating rules: act only on the current conversation, real context, and capabilities available '
    'in this runtime; do not invent tools, skills, or work already done; understand what the user '
    'wants before deciding whether to reply directly or call a tool.\n'
    'When you need to inspect a codebase, use read_file / grep / list_dir to get facts; '
    'do not guess file contents.\n'
    'Treat the working directory injected in this system message as authoritative.'
)
workspaceBlock=f'Working directory: {repoRoot}\nPlatform: cli-probe\n'
systemText=f'{xiaobaSystem}\n\n{workspaceBlock}'
userText=f'{userTask}\n\n(Repository root: {repoRoot})'

# --- tools: OpenAI chat shape (function nested under function key) ---
tools=[
    {
        'type':'function',
        'function':{
            'name':'list_dir',
            'description':'List files and subdirectories. Prefer when exploring unknown layout.',
            'parameters':{
                'type':'object',
                'properties':{'path':{'type':'string','description':'Directory path.'}},
                'required':['path'],
            },
        },
    },
    {
        'type':'function',
        'function':{
            'name':'read_file',
            'description':'Read file contents (text/code). Probe does not execute tools.',
            'parameters':{
                'type':'object',
                'properties':{
                    'file_path':{'type':'string','description':'File path.'},
                    'offset':{'type':'number','description':'Start line (optional).'},
                    'limit':{'type':'number','description':'Max lines (optional).'},
                },
                'required':['file_path'],
            },
        },
    },
    {
        'type':'function',
        'function':{
            'name':'grep',
            'description':'Search file contents for a pattern.',
            'parameters':{
                'type':'object',
                'properties':{
                    'pattern':{'type':'string','description':'Regex or substring.'},
                    'path':{'type':'string','description':'File or dir (optional).'},
                },
                'required':['pattern'],
            },
        },
    },
]

# --- XiaoBa-shaped request body ---
req={
    '_probe':'xiaoba_openai_chat_shape',
    '_note':'Matches XiaoBa OpenAIProvider first turn: system + user, tools[], no tool history.',
    'model':modelRow.get('model'),
    'messages':[
        {'role':'system','content':systemText},
        {'role':'user','content':userText},
    ],
    'tools':tools,
    'temperature':botProf.get('temperature',0.7),
    'max_tokens':maxOutputTokens,
    'stream':False,
}

os.makedirs(outDir,exist_ok=True)
reqPath=outDir+r'/xiaobaOneRoundRequest.json'
respPath=outDir+r'/xiaobaOneRoundResponse.json'

with open(reqPath,'w',encoding='utf-8') as f:
    json.dump(req,f,ensure_ascii=False,indent=2)

print('=== REQUEST PAYLOAD ===')
print(json.dumps(req,ensure_ascii=False,indent=2))

# --- call model (pick one branch: openai or anthropic) ---
raw=None

# --- openAI ---
from openai import OpenAI
client=OpenAI(
    api_key=modelRow.get('apiKey'),
    base_url=(modelRow.get('baseUrl') or {}).get('openai'),
)
resp=client.chat.completions.create(
    model=req['model'],
    messages=req['messages'],
    tools=tools,
    tool_choice='auto',
    max_tokens=maxOutputTokens,
    temperature=req.get('temperature'),
)
msg=resp.choices[0].message
raw={
    '_transport':'openai_chat_completions',
    'id':resp.id,
    'model':resp.model,
    'message':{
        'role':msg.role,
        'content':msg.content,
        'tool_calls':[
            {
                'id':tc.id,
                'type':tc.type,
                'function':{'name':tc.function.name,'arguments':tc.function.arguments},
            }
            for tc in (msg.tool_calls or [])
        ],
    },
    'usage':{
        'prompt_tokens':getattr(resp.usage,'prompt_tokens',None),
        'completion_tokens':getattr(resp.usage,'completion_tokens',None),
    },
}

# --- anthropic ---
from anthropic import Anthropic
anthropicTools=[]
for t in tools:
    fn=t['function']
    anthropicTools.append({
        'name':fn['name'],
        'description':fn['description'],
        'input_schema':fn['parameters'],
    })
client=Anthropic(
    api_key=modelRow.get('apiKey'),
    base_url=(modelRow.get('baseUrl') or {}).get('anthropic'),
)
resp=client.messages.create(
    model=req['model'],
    max_tokens=maxOutputTokens,
    system=systemText,
    messages=[{'role':'user','content':userText}],
    tools=anthropicTools,
    temperature=req.get('temperature'),
)
blocks=[]
toolUses=[]
for b in resp.content:
    if b.type=='text':
        blocks.append({'type':'text','text':b.text})
    elif b.type=='tool_use':
        toolUses.append({'id':b.id,'name':b.name,'input':b.input})
raw={
    '_transport':'anthropic_messages',
    'id':resp.id,
    'model':resp.model,
    'stop_reason':resp.stop_reason,
    'content_blocks':blocks,
    'tool_uses':toolUses,
    'usage':{
        'input_tokens':resp.usage.input_tokens,
        'output_tokens':resp.usage.output_tokens,
    },
}

with open(respPath,'w',encoding='utf-8') as f:
    json.dump(raw,f,ensure_ascii=False,indent=2)

print('\n=== RAW MODEL RESPONSE ===')
print(json.dumps(raw,ensure_ascii=False,indent=2))

# --- parse first action ---
action=None
if raw.get('message',{}).get('tool_calls'):
    action={
        'kind':'tool_calls',
        'calls':[
            {'name':tc['function']['name'],'arguments':tc['function']['arguments']}
            for tc in raw['message']['tool_calls']
        ],
    }
elif raw.get('tool_uses'):
    action={
        'kind':'tool_calls',
        'calls':[
            {'name':tu['name'],'arguments':json.dumps(tu['input'],ensure_ascii=False)}
            for tu in raw['tool_uses']
        ],
    }
else:
    text=''
    if raw.get('message',{}).get('content'):
        text=raw['message']['content'] or ''
    elif raw.get('content_blocks'):
        text='\n'.join(b.get('text','') for b in raw['content_blocks'] if b.get('type')=='text')
    if text.strip():
        action={'kind':'assistant_text','content':text.strip()}
    else:
        action={'kind':'unknown'}

print('\n=== PARSED ACTION IF POSSIBLE ===')
print(json.dumps(action,ensure_ascii=False,indent=2))
print(f'\nSaved: {reqPath}')
print(f'Saved: {respPath}')
