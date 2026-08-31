# list_dir tool — schema (for LLM) + run (your code)
import os

NAME='list_dir'

SCHEMA={
    'type':'function',
    'function':{
        'name':NAME,
        'description':'List files and subdirectories at a path under the repo.',
        'parameters':{
            'type':'object',
            'properties':{
                'path':{'type':'string','description':'Directory path relative to repo root or absolute.'},
            },
            'required':['path'],
        },
    },
}

def run(path,repoRoot=None):
    root=repoRoot or ''
    full=path if os.path.isabs(path) else os.path.join(root,path)
    if not os.path.isdir(full):
        return {'ok':False,'path':full.replace('\\','/'),'error':f'not a directory: {full}','entry':[]}
    name=sorted(os.listdir(full))
    entry=[]
    for n in name:
        p=os.path.join(full,n)
        kind='dir' if os.path.isdir(p) else 'file'
        entry.append({'name':n,'kind':kind})
    return {
        'ok':True,
        'path':full.replace('\\','/'),
        'entry':entry,
        'text':'\n'.join(f"{e['kind']}\t{e['name']}" for e in entry),
    }
