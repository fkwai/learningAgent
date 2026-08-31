# Minimal repo review agent — remote GitHub (no local checkout).
# pip install openai
# Optional: gh and/or opencli (https://github.com/jackwener/opencli) for richer GitHub CLI.
# Paste blocks line-by-line in a Python REPL, or run whole file.

import json
import os
import shutil
import subprocess
from openai import OpenAI

# --- inputs ---
repoUrl='https://github.com/fkwai/XiaoBa-CLI'
repoSlug='fkwai/XiaoBa-CLI'
outDir=r'/Users/kuaifang/git/learningAgent/playground/mini'
apiKey='sk-cp-4QikF0aquFjMICmg8oDQXD406DQxyXwmobWmh330CByUwPMFCHbS_cAd6Y8Mzk0oFVxgCNaDLBTsgoK4UBvihkqaYW75r32wihbuGerf_5cXckOAUukVcB0'
baseUrl='https://api.minimaxi.com/v1'
modelName='MiniMax-M2.7-highspeed'
maxOutputTokens=2000
temperature=0.7
maxToolChars=8000
reviewTask=(
    'Review this GitHub repository online (do not assume a local clone). '
    'Cover architecture, code quality, risks, bugs, and test gaps. '
    'Explore with the cli tool before judging. Cite specific file paths. '
    'When done exploring, write the final review as plain text (no more tool calls).'
)

# --- client ---
client=OpenAI(api_key=apiKey,base_url=baseUrl)

# --- tools: one cli skill (remote explore via curl / gh / opencli) ---
chatTools=[
    {
        'type':'function',
        'function':{
            'name':'cli',
            'description':(
                'Run a shell command to explore the remote GitHub repo. '
                'Prefer: curl/gh against api.github.com, or opencli if installed. '
                'Examples: '
                f'`curl -sL https://api.github.com/repos/{repoSlug}/contents/` ; '
                f'`curl -sL https://raw.githubusercontent.com/{repoSlug}/main/README.md` ; '
                f'`gh api repos/{repoSlug}/contents/src` ; '
                '`opencli list` / opencli github helpers if available. '
                'Do not rely on a local checkout of the target repo.'
            ),
            'parameters':{
                'type':'object',
                'properties':{
                    'command':{'type':'string','description':'Shell command to run.'},
                },
                'required':['command'],
            },
        },
    },
]

# --- system + user messages ---
systemText=(
    'You are a code review agent. Your only tool is cli. '
    'The target repo is online on GitHub — there is no local working copy. '
    'Explore with curl, gh, or opencli against GitHub. '
    'Do not guess file contents. When you have enough evidence, stop calling tools and deliver a structured review.'
)
userText=(
    f'{reviewTask}\n\n'
    f'Repository URL: {repoUrl}\n'
    f'Repo slug: {repoSlug}\n'
    'You have not fetched any files yet. Start by listing the repo root via GitHub API.'
)
messages=[
    {'role':'system','content':systemText},
    {'role':'user','content':userText},
]

os.makedirs(outDir,exist_ok=True)
histDir=os.path.join(outDir,'historyWeb')
if os.path.isdir(histDir):
    shutil.rmtree(histDir)
os.makedirs(histDir)

# --- agent loop: stop when model returns no tool calls ---
finalReview=''
roundNum=0
while True:
    roundNum+=1
    print(f'round {roundNum}...')

    histDump=[]
    for m in messages:
        row=dict(m)
        c=row.get('content')
        if isinstance(c,str) and '\n' in c:
            row['content']=c.splitlines()
        tcs=row.get('tool_calls')
        if tcs:
            nice=[]
            for tc in tcs:
                tcRow=dict(tc)
                fn=dict(tc.get('function') or {})
                rawArgs=fn.get('arguments')
                if isinstance(rawArgs,str):
                    try:
                        fn['arguments']=json.loads(rawArgs)
                    except json.JSONDecodeError:
                        if '\n' in rawArgs:
                            fn['arguments']=rawArgs.splitlines()
                tcRow['function']=fn
                nice.append(tcRow)
            row['tool_calls']=nice
        histDump.append(row)
    inPath=os.path.join(histDir,f'r{roundNum}_input.json')
    with open(inPath,'w',encoding='utf-8') as f:
        json.dump(histDump,f,ensure_ascii=False,indent=2)

    resp=client.chat.completions.create(
        model=modelName,
        messages=messages,
        tools=chatTools,
        tool_choice='auto',
        max_tokens=maxOutputTokens,
        temperature=temperature,
    )
    msg=resp.choices[0].message
    toolCalls=msg.tool_calls or []
    asstEntry={'role':'assistant','content':msg.content}
    if toolCalls:
        asstEntry['tool_calls']=[
            {
                'id':tc.id,
                'type':tc.type,
                'function':{'name':tc.function.name,'arguments':tc.function.arguments},
            }
            for tc in toolCalls
        ]

    outDump=dict(asstEntry)
    c=outDump.get('content')
    if isinstance(c,str) and '\n' in c:
        outDump['content']=c.splitlines()
    if outDump.get('tool_calls'):
        nice=[]
        for tc in outDump['tool_calls']:
            tcRow=dict(tc)
            fn=dict(tc.get('function') or {})
            rawArgs=fn.get('arguments')
            if isinstance(rawArgs,str):
                try:
                    fn['arguments']=json.loads(rawArgs)
                except json.JSONDecodeError:
                    if '\n' in rawArgs:
                        fn['arguments']=rawArgs.splitlines()
            tcRow['function']=fn
            nice.append(tcRow)
        outDump['tool_calls']=nice
    outPath=os.path.join(histDir,f'r{roundNum}_output.json')
    with open(outPath,'w',encoding='utf-8') as f:
        json.dump(outDump,f,ensure_ascii=False,indent=2)

    messages.append(asstEntry)

    if not toolCalls:
        finalReview=(msg.content or '').strip()
        break

    for tc in toolCalls:
        toolName=tc.function.name
        try:
            toolArgs=json.loads(tc.function.arguments or '{}')
        except json.JSONDecodeError:
            toolArgs={}

        if toolName!='cli':
            toolResult=f'error: unknown tool: {toolName}'
        else:
            cmd=toolArgs.get('command') or ''
            if not cmd.strip():
                toolResult='error: command required'
            else:
                proc=subprocess.run(
                    cmd,
                    shell=True,
                    cwd=outDir,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                )
                parts=[]
                if proc.stdout:
                    parts.append(proc.stdout.rstrip())
                if proc.stderr:
                    parts.append(f'stderr:\n{proc.stderr.rstrip()}')
                if proc.returncode!=0:
                    parts.append(f'exit_code={proc.returncode}')
                toolResult='\n'.join(parts) if parts else '(no output)'

        if len(toolResult)>maxToolChars:
            toolResult=toolResult[:maxToolChars]+'\n... truncated'
        messages.append({'role':'tool','tool_call_id':tc.id,'content':toolResult})
        print(f'  tool {toolName} -> {len(toolResult)} chars')

# --- output ---
reviewPath=os.path.join(outDir,'reviewWeb.md')
with open(reviewPath,'w',encoding='utf-8') as f:
    f.write(finalReview or '(empty review)')

print('\n=== REVIEW ===')
print(finalReview or '(empty review)')
print(f'\nSaved: {reviewPath}')
print(f'Saved: {histDir}/r*_input.json, r*_output.json ({roundNum} rounds)')
