def _estTokens(text):
    return max(1,len(text or '')//4)

def _msgTokens(msg):
    return _estTokens(msg.get('content') or '')

def _groupTurnPairs(history):
    pairs=[]
    i=0
    n=len(history)
    while i<n:
        row=history[i]
        if row.get('role')!='user':
            i+=1
            continue
        user=row
        assistant=None
        if i+1<n and history[i+1].get('role')=='assistant':
            nxt=history[i+1]
            if user.get('turn') is None or nxt.get('turn') is None or user.get('turn')==nxt.get('turn'):
                assistant=nxt
                i+=2
            else:
                i+=1
        else:
            i+=1
        if assistant is not None:
            pairs.append((user,assistant))
    return pairs

def _pairsToMessages(pairs):
    out=[]
    for user,assistant in pairs:
        out.append({'role':'user','content':user.get('content') or ''})
        out.append({'role':'assistant','content':assistant.get('content') or ''})
    return out

def _trimByTokenCap(messages,developer,userMessage,maxContextTokens):
    if not maxContextTokens or maxContextTokens<=0:
        return messages
    budget=maxContextTokens
    budget-= _estTokens(developer)
    budget-= _estTokens(userMessage)
    trimmed=[]
    for msg in reversed(messages):
        cost=_msgTokens(msg)
        if trimmed and budget-cost<0:
            break
        trimmed.insert(0,msg)
        budget-=cost
    return trimmed

def buildModelInput(*,developer,history,userMessage,botCfg):
    maxRecent=botCfg['maxRecentTurns']
    maxCtx=botCfg['maxContextTokens']
    pairs=_groupTurnPairs(history)
    if maxRecent and maxRecent>0:
        pairs=pairs[-maxRecent:]
    messages=_pairsToMessages(pairs)
    messages=_trimByTokenCap(messages,developer,userMessage,maxCtx)
    messages.append({'role':'user','content':userMessage})
    return {'system':developer or '','messages':messages}
