# one round of humpy ChatSession.turn — function + script (same as message/openai.py)
from humpy.bot import Bot
from humpy.session import ChatSession
from humpy.memory import pick,store
from humpy.message import complete
from humpy.prompt import DEV_PROMPT_DEFAULT

botName='main'
sessionId=None          # set id + resume=True to continue an existing session
resume=True
userText='Say hello in one short line; mention which model you are.'

# list sessions for this bot (pick an id above)
_bot=Bot.adopt(botName)
_row=store.listAllSession(_bot.indexFile)
print('sessions for bot',botName,'(',len(_row),'):')
for _r in _row:
    _sid=_r.get('sessionId') or ''
    _hl=(_r.get('headline') or '').strip() or '(untitled)'
    _sp=_r.get('sessionFile') or ''
    _tc=store.sessionTurnCount(_sp)
    print(' ',_sid,'|',_hl,'| turns',_tc)
print()
sessionId='2607170341-e1a0'

# --- function ---
sess=ChatSession(botName,sessionId=sessionId,resume=resume)
out=sess.turn(userText)

# --- script  ---
maxToken=sess.botCfg['maxOutputTokens']
history,devFromFile=store.loadSessionHistory(sess.sessionPath)
developer=devFromFile or sess.bot.loadDeveloper() or DEV_PROMPT_DEFAULT
picked=pick.buildModelInput(
    developer=developer,
    history=history,
    userMessage=userText,
    botCfg=sess.botCfg,
)
result=complete(
    sess.cfg,
    sess.sdk,
    picked['messages'],
    picked['system'],
    maxToken=maxToken,
    temperature=sess.botCfg['temperature'],
)
if sess.botCfg['saveSessions']:
    nextTurn=sess.turnCount+1
    store.appendTurn(
        sess.sessionPath,
        nextTurn,
        userText,
        result['text'],
        sess.modelName,
        usage=result.get('usage'),
    )
    sess.turnCount=nextTurn
    if sess.botCfg['autoTitle'] and sess.turnCount==1:
        sess.applyAutoTitle(userText)

print('bot:',sess.botName,'session:',sess.sessionId)
print('input userText:',userText)
print('input system:',picked['system'][:120]+('...' if len(picked['system'])>120 else ''))
print('input messages:',picked['messages'])
print('output text:',result['text'])
print('output usage:',result.get('usage'))
print('function out text:',out['text'])
print('saved',sess.sessionPath)
