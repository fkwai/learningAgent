# shell tool — run a CLI command (covers most cmds: ls/dir, git, python, …)
import os
import subprocess
import time

NAME='shell'
DEFAULT_TIMEOUT_MS=30000
MAX_OUT=8000

SCHEMA={
    'type':'function',
    'function':{
        'name':NAME,
        'description':(
            'Run a shell command on the host (PowerShell/cmd on Windows, sh elsewhere). '
            'Use for listing dirs, reading files via type/cat, git, scripts, etc. '
            'Prefer a working directory under the repo when possible.'
        ),
        'parameters':{
            'type':'object',
            'properties':{
                'command':{'type':'string','description':'Command line to execute.'},
                'cwd':{'type':'string','description':'Working directory (relative to repo root or absolute).'},
                'timeout_ms':{'type':'number','description':'Timeout in milliseconds (default 30000).'},
            },
            'required':['command'],
        },
    },
}

def run(command,cwd=None,timeout_ms=None,repoRoot=None):
    cmd=(command or '').strip()
    if not cmd:
        return {
            'ok':False,
            'exitCode':None,
            'stdout':'',
            'stderr':'empty command',
            'durationMs':0,
            'truncated':False,
            'interrupted':False,
            'text':'error: empty command',
        }
    root=repoRoot or os.getcwd()
    work=root
    if cwd:
        work=cwd if os.path.isabs(cwd) else os.path.join(root,cwd)
    if not os.path.isdir(work):
        return {
            'ok':False,
            'exitCode':None,
            'stdout':'',
            'stderr':f'cwd not found: {work}',
            'durationMs':0,
            'truncated':False,
            'interrupted':False,
            'text':f'error: cwd not found: {work}',
        }
    timeoutMs=int(timeout_ms) if timeout_ms is not None else DEFAULT_TIMEOUT_MS
    if timeoutMs<=0:
        timeoutMs=DEFAULT_TIMEOUT_MS
    timeoutSec=timeoutMs/1000.0
    t0=time.perf_counter()
    interrupted=False
    truncated=False
    try:
        proc=subprocess.run(
            cmd,
            shell=True,
            cwd=work,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeoutSec,
        )
        exitCode=proc.returncode
        stdout=proc.stdout or ''
        stderr=proc.stderr or ''
    except subprocess.TimeoutExpired as exc:
        interrupted=True
        exitCode=None
        stdout=(exc.stdout or '') if isinstance(exc.stdout,str) else (exc.stdout or b'').decode('utf-8','replace')
        stderr=(exc.stderr or '') if isinstance(exc.stderr,str) else (exc.stderr or b'').decode('utf-8','replace')
        if stderr:
            stderr=stderr+'\n'
        stderr=stderr+f'timeout after {timeoutMs}ms'
    except Exception as exc:
        durationMs=int((time.perf_counter()-t0)*1000)
        return {
            'ok':False,
            'exitCode':None,
            'stdout':'',
            'stderr':str(exc),
            'durationMs':durationMs,
            'truncated':False,
            'interrupted':False,
            'cwd':work.replace('\\','/'),
            'text':f'error: {exc}',
        }
    durationMs=int((time.perf_counter()-t0)*1000)
    if len(stdout)>MAX_OUT:
        stdout=stdout[:MAX_OUT]+'\n...[truncated]'
        truncated=True
    if len(stderr)>MAX_OUT:
        stderr=stderr[:MAX_OUT]+'\n...[truncated]'
        truncated=True
    part=[]
    if stdout:
        part.append(stdout.rstrip())
    if stderr:
        part.append('[stderr]\n'+stderr.rstrip())
    part.append(f'[exitCode={exitCode} durationMs={durationMs}]')
    text='\n'.join(part)
    return {
        'ok':(exitCode==0) and not interrupted,
        'exitCode':exitCode,
        'stdout':stdout,
        'stderr':stderr,
        'durationMs':durationMs,
        'truncated':truncated,
        'interrupted':interrupted,
        'cwd':work.replace('\\','/'),
        'text':text,
    }
