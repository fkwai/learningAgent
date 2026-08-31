# Codex Responses API tool shape (top-level name, strict, parameters).
# Ref: codex-rs/tools/src/tool_spec.rs, responses_api.rs


def buildCodexTools():
    return [
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
