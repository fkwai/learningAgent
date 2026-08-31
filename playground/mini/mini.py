# Minimal multi-cycle review + change agent (local checkout).
# Flow: checkout -> (review -> change)* -> PR
# History tags: CHK, R1C0, R1C1, R2C1, R2C2, ..., PR  (+ react step: R1C0r1_input.json)
# pip install openai
# Needs: git; gh (or curl + GITHUB_TOKEN) for PR create.

import json
import os
import shutil
import subprocess
from datetime import datetime
from openai import OpenAI

# --- inputs (absolute paths — safe in REPL from any cwd) ---
repoRoot=r'/Users/kuaifang/git/XiaoBa-CLI-fork-copy'
outDir=r'/Users/kuaifang/git/learningAgent/playground/mini'
apiKey='sk-cp-4QikF0aquFjMICmg8oDQXD406DQxyXwmobWmh330CByUwPMFCHbS_cAd6Y8Mzk0oFVxgCNaDLBTsgoK4UBvihkqaYW75r32wihbuGerf_5cXckOAUukVcB0'
baseUrl='https://api.minimaxi.com/v1'
modelName='MiniMax-M2.7-highspeed'
maxOutputTokens=2000
temperature=0.7
maxToolChars=8000
maxCycles=3
branchName='dev_'+datetime.now().strftime('%Y%m%d_%H%M%S')

# --- client ---
client=OpenAI(api_key=apiKey,base_url=baseUrl)

repoRootAbs=os.path.abspath(repoRoot)
if not os.path.isdir(repoRootAbs):
    raise SystemExit(f'repo not found: {repoRootAbs}')
if not os.path.isfile(os.path.join(repoRootAbs,'package.json')):
    raise SystemExit(f'repo looks empty (no package.json): {repoRootAbs}')

# --- tools: one cli skill ---
chatTools=[
    {
        'type':'function',
        'function':{
            'name':'cli',
            'description':'Run a shell command in the repository root.',
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

# --- message builders ---
def createMessageCheckout(repoRootAbs,branchName):
    system=(
        'You are a coding agent. Your only tool is cli. '
        'Create and check out the given git branch. Stop when done.'
    )
    user=(
        f'Create and check out branch {branchName}.\n'
        f'Repository root: {repoRootAbs}\n'
    )
    return [
        {'role':'system','content':system},
        {'role':'user','content':user},
    ]

def createMessageR(repoRootAbs):
    system=(
        'You are a code review agent. Your only tool is cli. '
        'Explore the repo, then write a review. Stop when the review is done.'
    )
    user=f'Review this repo.\nRepository root: {repoRootAbs}\n'
    return [
        {'role':'system','content':system},
        {'role':'user','content':user},
    ]

def createMessageC(repoRootAbs,lastReview):
    system=(
        'You are a coding agent. Your only tool is cli. '
        'Revise the repo based on the review, then commit. '
        'Stop when the change is done.'
    )
    user=(
        f'Revise this repo and commit.\n'
        f'Repository root: {repoRootAbs}\n\n'
        f'Review:\n{lastReview}\n'
    )
    return [
        {'role':'system','content':system},
        {'role':'user','content':user},
    ]

def createMessagePR(repoRootAbs,branchName):
    system=(
        'You are a coding agent. Your only tool is cli. '
        'Push the branch and create a pull request. Stop when the PR exists; include its URL.'
    )
    user=(
        f'Push branch {branchName} and create a pull request to main.\n'
        f'Repository root: {repoRootAbs}\n'
    )
    return [
        {'role':'system','content':system},
        {'role':'user','content':user},
    ]

# --- history dump ---
def dumpHistory(path,payload):
    def pretty(m):
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
        return row
    if isinstance(payload,list):
        dump=[pretty(m) for m in payload]
    else:
        dump=pretty(payload)
    with open(path,'w',encoding='utf-8') as f:
        json.dump(dump,f,ensure_ascii=False,indent=2)

# --- shared react loop ---
def runReact(tagBase,kind,messages,outName):
    finalText=''
    stepNum=0
    while True:
        stepNum+=1
        tag=f'{tagBase}r{stepNum}'
        print(f'[{tag}/{kind}] ...')

        dumpHistory(os.path.join(histDir,f'{tag}_input.json'),messages)

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

        dumpHistory(os.path.join(histDir,f'{tag}_output.json'),asstEntry)
        messages.append(asstEntry)

        if not toolCalls:
            finalText=(msg.content or '').strip()
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
                        cwd=repoRootAbs,
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

    savePath=os.path.join(outDir,outName)
    with open(savePath,'w',encoding='utf-8') as f:
        f.write(finalText or '(empty)')
    print(f'\n=== {tagBase} {kind} ===')
    print(finalText or '(empty)')
    print(f'Saved: {savePath}')
    return finalText

os.makedirs(outDir,exist_ok=True)
histDir=os.path.join(outDir,'history')
if os.path.isdir(histDir):
    shutil.rmtree(histDir)
os.makedirs(histDir)

# --- top: checkout ---
runReact('CHK','checkout',createMessageCheckout(repoRootAbs,branchName),'checkout.md')

# --- major loop: R1C0 R1C1 R2C1 R2C2 ... ---
lastReview=''
lastChange=''
for rev in range(1,maxCycles+1):
    cBefore=rev-1
    cAfter=rev
    lastReview=runReact(
        f'R{rev}C{cBefore}',
        'review',
        createMessageR(repoRootAbs),
        f'review_R{rev}.md',
    )
    lastChange=runReact(
        f'R{rev}C{cAfter}',
        'change',
        createMessageC(repoRootAbs,lastReview),
        f'change_R{rev}.md',
    )

# --- end: PR ---
lastPr=runReact('PR','pr',createMessagePR(repoRootAbs,branchName),'pr.md')

with open(os.path.join(outDir,'review.md'),'w',encoding='utf-8') as f:
    f.write(lastReview or '(empty)')

print(f'\nHistory: {histDir}/CHK|RnCm|PR + r*_input/output.json')
print(f'Branch: {branchName}')
print(f'Cycles: {maxCycles}')
