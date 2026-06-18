# XiaoBa OpenAI chat tool shape (function nested under function key).
# Ref: XiaoBa-CLI src/types/tool.ts, src/providers/openai-provider.ts


def buildXiaoBaTools():
    return [
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
