def _estToken(text):
    return max(1,len(text or '')//4)

def _msgToken(msg):
    return _estToken(msg.get('content') or '')

def _groupTurnPair(history):
    pair=[]
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
            pair.append((user,assistant))
    return pair

def _pairToMessage(pair):
    out=[]
    for user,assistant in pair:
        out.append({'role':'user','content':user.get('content') or ''})
        out.append({'role':'assistant','content':assistant.get('content') or ''})
    return out

def _trimByTokenCap(message,developer,userMessage,maxContextToken):
    if not maxContextToken or maxContextToken<=0:
        return message
    budget=maxContextToken
    budget-=_estToken(developer)
    budget-=_estToken(userMessage)
    trimmed=[]
    for msg in reversed(message):
        cost=_msgToken(msg)
        if trimmed and budget-cost<0:
            break
        trimmed.insert(0,msg)
        budget-=cost
    return trimmed

def buildModelInput(*,developer,history,userMessage,botCfg):
    maxRecent=botCfg['maxRecentTurns']
    maxCtx=botCfg['maxContextTokens']
    pair=_groupTurnPair(history)
    if maxRecent and maxRecent>0:
        pair=pair[-maxRecent:]
    message=_pairToMessage(pair)
    message=_trimByTokenCap(message,developer,userMessage,maxCtx)
    message.append({'role':'user','content':userMessage})
    return {'system':developer or '','messages':message}
