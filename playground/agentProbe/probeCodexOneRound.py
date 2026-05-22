# One-round Codex-shaped probe (no tool execution).
# Run line-by-line in a Python REPL or paste blocks into terminal.
#
# Source refs: codex-rs/core/src/client.rs build_responses_request
#              codex-rs/codex-api/src/common.rs ResponsesApiRequest
#              codex-rs/tools/src/tool_spec.rs

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

# --- Codex instructions + user message (Responses API input item) ---
codexInstructions=(
    'You are Codex, based on GPT-5. You are an interactive CLI agent that helps users with '
    'software engineering tasks. Use the provided tools to investigate and make progress. '
    'Prefer exploring the codebase before guessing. When you need filesystem access, call a tool '
    'instead of assuming file contents. Set workdir when running shell-like operations.'
)
userText=(
    f'{userTask}\n\n'
    f'Repository root (cwd): {repoRoot}\n'
    'You have not read any files yet. Start by listing or reading project files.'
)
codexInput=[{
    'type':'message',
    'role':'user',
    'content':[{'type':'input_text','text':userText}],
}]

# --- tools: Responses API shape (type + top-level name) ---
codexTools=[
    {
        'type':'function',
        'name':'list_dir',
        'description':'List files and directories at a path. Use before reading unknown layouts.',
        'strict':False,
        'parameters':{
            'type':'object',
            'properties':{'path':{'type':'string','description':'Directory path.'}},
            'required':['path'],
        },
    },
    {
        'type':'function',
        'name':'read_file',
        'description':'Read a text file from the repository.',
        'strict':False,
        'parameters':{
            'type':'object',
            'properties':{
                'path':{'type':'string','description':'File path.'},
                'offset':{'type':'integer','description':'1-based start line (optional).'},
                'limit':{'type':'integer','description':'Max lines (optional).'},
            },
            'required':['path'],
        },
    },
    {
        'type':'function',
        'name':'grep',
        'description':'Search file contents for a pattern under a path.',
        'strict':False,
        'parameters':{
            'type':'object',
            'properties':{
                'pattern':{'type':'string','description':'Regex or substring.'},
                'path':{'type':'string','description':'File or directory.'},
            },
            'required':['pattern','path'],
        },
    },
]

# --- Codex-shaped request body (saved as canonical probe payload) ---
req={
    '_probe':'codex_responses_api_shape',
    '_note':'Matches Codex ResponsesApiRequest. HTTP may use chat/tools adapter below.',
    'model':modelRow.get('model'),
    'instructions':codexInstructions,
    'input':codexInput,
    'tools':codexTools,
    'tool_choice':'auto',
    'parallel_tool_calls':False,
    'stream':False,
    'store':False,
    'include':[],
    'temperature':botProf.get('temperature',0.7),
    'max_output_tokens':maxOutputTokens,
}

os.makedirs(outDir,exist_ok=True)
reqPath=outDir+r'/codexOneRoundRequest.json'
respPath=outDir+r'/codexOneRoundResponse.json'

with open(reqPath,'w',encoding='utf-8') as f:
    json.dump(req,f,ensure_ascii=False,indent=2)

print('=== REQUEST PAYLOAD ===')
print(json.dumps(req,ensure_ascii=False,indent=2))

# --- call model (pick one branch: openai or anthropic) ---
raw=None
if sdk=='openai':
    from openai import OpenAI
    chatTools=[]
    for t in codexTools:
        chatTools.append({
            'type':'function',
            'function':{
                'name':t['name'],
                'description':t['description'],
                'parameters':t['parameters'],
            },
        })
    client=OpenAI(
        api_key=modelRow.get('apiKey'),
        base_url=(modelRow.get('baseUrl') or {}).get('openai'),
    )
    resp=client.chat.completions.create(
        model=req['model'],
        messages=[
            {'role':'system','content':codexInstructions},
            {'role':'user','content':userText},
        ],
        tools=chatTools,
        tool_choice='auto',
        max_tokens=maxOutputTokens,
        temperature=req.get('temperature'),
    )
    msg=resp.choices[0].message
    raw={
        '_transport':'openai_chat_completions_from_codex_shape',
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
else:
    from anthropic import Anthropic
    anthropicTools=[]
    for t in codexTools:
        anthropicTools.append({
            'name':t['name'],
            'description':t['description'],
            'input_schema':t['parameters'],
        })
    client=Anthropic(
        api_key=modelRow.get('apiKey'),
        base_url=(modelRow.get('baseUrl') or {}).get('anthropic'),
    )
    resp=client.messages.create(
        model=req['model'],
        max_tokens=maxOutputTokens,
        system=codexInstructions,
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
        '_transport':'anthropic_messages_from_codex_shape',
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

# --- parse first action (inline, no function) ---
action=None
if raw and raw.get('message',{}).get('tool_calls'):
    action={
        'kind':'tool_calls',
        'calls':[
            {'name':tc['function']['name'],'arguments':tc['function']['arguments']}
            for tc in raw['message']['tool_calls']
        ],
    }
elif raw and raw.get('tool_uses'):
    action={
        'kind':'tool_calls',
        'calls':[
            {'name':tu['name'],'arguments':json.dumps(tu['input'],ensure_ascii=False)}
            for tu in raw['tool_uses']
        ],
    }
else:
    text=''
    if raw and raw.get('message',{}).get('content'):
        text=raw['message']['content'] or ''
    elif raw and raw.get('content_blocks'):
        text='\n'.join(b.get('text','') for b in raw['content_blocks'] if b.get('type')=='text')
    if text.strip():
        action={'kind':'final_text','content':text.strip()}
    else:
        action={'kind':'unknown','raw_keys':list(raw.keys()) if raw else []}

print('\n=== PARSED ACTION IF POSSIBLE ===')
print(json.dumps(action,ensure_ascii=False,indent=2))
print(f'\nSaved: {reqPath}')
print(f'Saved: {respPath}')
