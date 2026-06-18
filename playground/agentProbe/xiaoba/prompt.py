# XiaoBa OpenAI chat request (system + user messages).
# Ref: conversation-runner.ts, openai-provider.ts buildRequestBody


def buildXiaoBaSystem(repoRoot):
    core=(
        'You are the user\'s personal assistant: careful, reliable, and able to collaborate over time.\n\n'
        'Operating rules: act only on the current conversation, real context, and capabilities available '
        'in this runtime; do not invent tools, skills, or work already done; understand what the user '
        'wants before deciding whether to reply directly or call a tool.\n'
        'When you need to inspect a codebase, use read_file / grep / list_dir to get facts; '
        'do not guess file contents.\n'
        'Treat the working directory injected in this system message as authoritative.'
    )
    workspace=f'Working directory: {repoRoot}\nPlatform: cli-probe\n'
    return f'{core}\n\n{workspace}'


def buildXiaoBaUserText(repoRoot,userTask):
    return f'{userTask}\n\n(Repository root: {repoRoot})'


def buildXiaoBaRequest(*,modelRow,botProf,repoRoot,userTask,tools,maxOutputTokens):
    systemText=buildXiaoBaSystem(repoRoot)
    userText=buildXiaoBaUserText(repoRoot,userTask)
    return {
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


def buildXiaoBaCallContext(req):
    system=req['messages'][0]['content']
    userMessages=[m for m in req['messages'] if m['role']!='system']
    return {
        'system':system,
        'messages':userMessages,
        'toolShape':'nested',
    }
