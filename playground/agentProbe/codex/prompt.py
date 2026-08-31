# Codex Responses API request body (instructions + input items).
# Ref: codex-rs/core/src/client.rs build_responses_request


def buildCodexInstructions():
    return (
        'You are Codex, based on GPT-5. You are an interactive CLI agent that helps users with '
        'software engineering tasks. Use the provided tools to investigate and make progress. '
        'Prefer exploring the codebase before guessing. When you need filesystem access, call a tool '
        'instead of assuming file contents. Set workdir when running shell-like operations.'
    )


def buildCodexUserText(repoRoot,userTask):
    return (
        f'{userTask}\n\n'
        f'Repository root (cwd): {repoRoot}\n'
        'You have not read any files yet. Start by listing or reading project files.'
    )


def buildCodexInput(userText):
    return [{
        'type':'message',
        'role':'user',
        'content':[{'type':'input_text','text':userText}],
    }]


def buildCodexRequest(*,modelRow,botProf,repoRoot,userTask,tools,maxOutputTokens):
    instructions=buildCodexInstructions()
    userText=buildCodexUserText(repoRoot,userTask)
    return {
        '_probe':'codex_responses_api_shape',
        '_note':'Canonical Codex ResponsesApiRequest wire shape. HTTP uses chat/tools adapter in call.py.',
        'model':modelRow.get('model'),
        'instructions':instructions,
        'input':buildCodexInput(userText),
        'tools':tools,
        'tool_choice':'auto',
        'parallel_tool_calls':False,
        'stream':False,
        'store':False,
        'include':[],
        'temperature':botProf.get('temperature',0.7),
        'max_output_tokens':maxOutputTokens,
    }


def buildCodexCallContext(req):
    userText=req['input'][0]['content'][0]['text']
    instructions=req['instructions']
    return {
        'system':instructions,
        'userText':userText,
        'messages':[{'role':'user','content':userText}],
        'openaiMessages':[
            {'role':'system','content':instructions},
            {'role':'user','content':userText},
        ],
        'toolShape':'flat',
    }
