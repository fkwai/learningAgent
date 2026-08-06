# tool registry — schema for the LLM + dispatch to run()
from . import listDir as listDirMod
from . import readFile as readFileMod
from . import shell as shellMod

SCHEMA=[listDirMod.SCHEMA,readFileMod.SCHEMA,shellMod.SCHEMA]

_RUNNER={
    listDirMod.NAME:listDirMod.run,
    readFileMod.NAME:readFileMod.run,
    shellMod.NAME:shellMod.run,
}

def schema():
    return list(SCHEMA)

def run(name,arg,repoRoot=None):
    fn=_RUNNER.get(name)
    if not fn:
        return {'ok':False,'error':f'unknown tool: {name}','text':''}
    kwarg=dict(arg or {})
    if repoRoot is not None:
        kwarg['repoRoot']=repoRoot
    if name==listDirMod.NAME:
        kwarg={k:kwarg[k] for k in ('path','repoRoot') if k in kwarg}
    elif name==readFileMod.NAME:
        kwarg={k:kwarg[k] for k in ('file_path','offset','limit','repoRoot') if k in kwarg}
    elif name==shellMod.NAME:
        # LLM may send timeoutMs; accept both timeout_ms and timeoutMs
        if 'timeoutMs' in kwarg and 'timeout_ms' not in kwarg:
            kwarg['timeout_ms']=kwarg.pop('timeoutMs')
        else:
            kwarg.pop('timeoutMs',None)
        kwarg={k:kwarg[k] for k in ('command','cwd','timeout_ms','repoRoot') if k in kwarg}
    return fn(**kwarg)
