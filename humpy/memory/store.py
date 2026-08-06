import json
import os
from datetime import datetime,timezone

def nowIso():
    return datetime.now(timezone.utc).isoformat()

def appendLine(path,obj):
    with open(path,'a',encoding='utf-8') as f:
        f.write(json.dumps(obj,ensure_ascii=False)+'\n')

def loadSessionHistory(sessionPath):
    if not os.path.isfile(sessionPath):
        return [],None
    devPart=[]
    out=[]
    with open(sessionPath,encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            row=json.loads(line)
            if row.get('entryType'):
                continue
            role=row.get('role')
            if role=='developer':
                devPart.append(row.get('content') or '')
                continue
            if role in ('user','assistant'):
                out.append({
                    'role':role,
                    'content':row.get('content') or '',
                    'turn':row.get('turn'),
                })
    devFromFile='\n\n'.join(p for p in devPart if p).strip() or None
    return out,devFromFile

def maxTurnInSession(sessionPath):
    mx=0
    if not os.path.isfile(sessionPath):
        return 0
    with open(sessionPath,encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            row=json.loads(line)
            t=row.get('turn')
            if isinstance(t,int) and t>mx:
                mx=t
    return mx

def sessionTurnCount(sessionPath):
    '''Turn count from session jsonl only (index is not updated per turn).'''
    return maxTurnInSession(sessionPath)

def appendTurn(sessionPath,turnNum,user,assistant,model,usage=None,ts=None):
    t=ts or nowIso()
    appendLine(sessionPath,{'role':'user','turn':turnNum,'content':user,'ts':t})
    if usage is not None:
        row={'role':'assistant','turn':turnNum,'model':model,'usage':usage,'content':assistant,'ts':t}
    else:
        row={'role':'assistant','turn':turnNum,'model':model,'content':assistant,'ts':t}
    appendLine(sessionPath,row)

def indexHasSession(indexFile,sid):
    if not os.path.isfile(indexFile):
        return False
    with open(indexFile,encoding='utf-8') as f:
        for line in f:
            if line.strip() and json.loads(line).get('sessionId')==sid:
                return True
    return False

def registerSession(indexFile,meta):
    appendLine(indexFile,meta)

def loadIndexEntry(indexFile,limit=20):
    if not os.path.isfile(indexFile):
        return []
    row=[]
    with open(indexFile,encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if line:
                row.append(json.loads(line))
    return row[-limit:]

def _readIndexRow(indexFile):
    if not os.path.isfile(indexFile):
        return []
    row=[]
    with open(indexFile,encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if line:
                row.append(json.loads(line))
    return row

def getSessionMeta(indexFile,sessionId):
    for r in _readIndexRow(indexFile):
        if r.get('sessionId')==sessionId:
            return r
    return None

def updateSessionMeta(indexFile,sessionId,patch):
    if not patch:
        return
    row=_readIndexRow(indexFile)
    if not row:
        return
    found=False
    for r in row:
        if r.get('sessionId')==sessionId:
            r.update(patch)
            found=True
    if not found:
        return
    with open(indexFile,'w',encoding='utf-8') as f:
        for r in row:
            f.write(json.dumps(r,ensure_ascii=False)+'\n')

def updateIndexHeadline(indexFile,sessionId,headline):
    updateSessionMeta(indexFile,sessionId,{'headline':headline})

def listAllSession(indexFile):
    return _readIndexRow(indexFile)

def sessionLastUpdated(sessionPath,fallback=''):
    last=''
    if not os.path.isfile(sessionPath):
        return fallback or ''
    with open(sessionPath,encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            r=json.loads(line)
            if r.get('role') in ('user','assistant') and r.get('ts'):
                last=r['ts']
    return last or fallback or ''

def exportSessionMarkdown(outPath,*,botName,sessionId,title,turnCount,sessionPath):
    history,_=loadSessionHistory(sessionPath)
    line=[
        f'# {title or "(untitled)"}',
        '',
        f'- bot: {botName}',
        f'- sessionId: {sessionId}',
        f'- turnCount: {turnCount}',
        '',
        '---',
        '',
    ]
    for msg in history:
        role=msg.get('role') or ''
        if role not in ('user','assistant'):
            continue
        label='User' if role=='user' else 'Assistant'
        line.append(f'## {label}')
        line.append('')
        line.append(msg.get('content') or '')
        line.append('')
    parent=os.path.dirname(os.path.abspath(outPath))
    if parent:
        os.makedirs(parent,exist_ok=True)
    with open(outPath,'w',encoding='utf-8') as f:
        f.write('\n'.join(line))
        if line and line[-1]:
            f.write('\n')
