# read_file tool — schema (for LLM) + run (your code)
import os

NAME='read_file'

SCHEMA={
    'type':'function',
    'function':{
        'name':NAME,
        'description':'Read a text file from the repository.',
        'parameters':{
            'type':'object',
            'properties':{
                'file_path':{'type':'string','description':'Path relative to repo root or absolute.'},
                'offset':{'type':'number','description':'1-based start line (optional).'},
                'limit':{'type':'number','description':'Max lines (optional).'},
            },
            'required':['file_path'],
        },
    },
}

def run(file_path,offset=None,limit=None,repoRoot=None):
    root=repoRoot or ''
    path=file_path if os.path.isabs(file_path) else os.path.join(root,file_path)
    if not os.path.isfile(path):
        return {'ok':False,'path':path.replace('\\','/'),'error':f'not a file: {path}','text':''}
    with open(path,encoding='utf-8') as f:
        line=f.readlines()
    start=0
    if offset is not None and int(offset)>0:
        start=int(offset)-1
    chunk=line[start:]
    if limit is not None and int(limit)>0:
        chunk=chunk[:int(limit)]
    return {
        'ok':True,
        'path':path.replace('\\','/'),
        'text':''.join(chunk),
        'lineCount':len(line),
        'returnedLine':len(chunk),
    }
