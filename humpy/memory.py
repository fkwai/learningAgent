import json
import os
from datetime import datetime,timezone

def nowIso():
    return datetime.now(timezone.utc).isoformat()

def appendLine(path,obj):
    with open(path,'a',encoding='utf-8') as f:
        f.write(json.dumps(obj,ensure_ascii=False)+'\n')

def loadMessages(sessionPath):
    if not os.path.isfile(sessionPath):
        return [],None
    devParts=[]
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
                devParts.append(row.get('content') or '')
                continue
            if role in ('user','assistant'):
                out.append({'role':role,'content':row.get('content') or ''})
    devFromFile='\n\n'.join(p for p in devParts if p).strip() or None
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

def indexHasSession(indexFile,sid):
    if not os.path.isfile(indexFile):
        return False
    with open(indexFile,encoding='utf-8') as f:
        for line in f:
            if line.strip() and json.loads(line).get('sessionId')==sid:
                return True
    return False

def appendUser(sessionPath,turn,content,ts=None):
    appendLine(sessionPath,{'role':'user','turn':turn,'content':content,'ts':ts or nowIso()})

def appendAssistant(sessionPath,turn,content,model,usage=None,ts=None):
    if usage is not None:
        row={'role':'assistant','turn':turn,'model':model,'usage':usage,'content':content,'ts':ts or nowIso()}
    else:
        row={'role':'assistant','turn':turn,'model':model,'content':content,'ts':ts or nowIso()}
    appendLine(sessionPath,row)

def registerSession(indexFile,meta):
    appendLine(indexFile,meta)

def loadIndexEntries(indexFile,limit=20):
    if not os.path.isfile(indexFile):
        return []
    rows=[]
    with open(indexFile,encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if line:
                rows.append(json.loads(line))
    return rows[-limit:]

def updateIndexHeadline(indexFile,sessionId,headline):
    if not os.path.isfile(indexFile):
        return
    rows=[]
    with open(indexFile,encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            row=json.loads(line)
            if row.get('sessionId')==sessionId:
                row['headline']=headline
            rows.append(row)
    with open(indexFile,'w',encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row,ensure_ascii=False)+'\n')
