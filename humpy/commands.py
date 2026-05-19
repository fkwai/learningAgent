import shlex

from humpy.memory import store
from humpy.session import ChatSession

def fmtTs(ts):
    s=(ts or '').strip()
    if not s:
        return ''
    if 'T' in s:
        base=s.split('+')[0].split('Z')[0]
        if '.' in base:
            base=base.split('.')[0]
        return base[:19]
    return s[:19]

def _helpText():
    return '\n'.join([
        'commands:',
        '  /exit              quit',
        '  /help              this list',
        '  /status            bot, session, title, turns, model, limits',
        '  /sessions          list sessions for current bot',
        '  /load <sessionId>  resume a session',
        '  /reset             new session (same bot)',
        '  /export <path>     export session to markdown',
        '  /title <text>      set session title',
    ])

def _cmdStatus(sess):
    title=(sess.headline or '').strip() or '(untitled)'
    print(f'botName: {sess.botName}')
    print(f'sessionId: {sess.sessionId}')
    print(f'title: {title}')
    print(f'turnCount: {sess.turnCount}')
    print(f'model: {sess.modelName} ({sess.pickId})')
    print(f'maxRecentTurns: {sess.humpyCfg["maxRecentTurns"]}')
    print(f'maxContextTokens: {sess.humpyCfg["maxContextTokens"]}')

def _cmdSessions(sess,listLimit):
    rows=store.listAllSessions(sess.indexFile)
    if not rows:
        print('(no sessions)')
        return
    rows=list(reversed(rows[-listLimit:]))
    for row in rows:
        sid=row.get('sessionId') or ''
        title=(row.get('headline') or '').strip() or '(untitled)'
        tc=row.get('turnCount')
        if tc is None:
            sp=row.get('sessionFile') or ''
            tc=store.maxTurnInSession(sp) if sp else 0
        sp=row.get('sessionFile') or ''
        updated=fmtTs(store.sessionLastUpdated(sp,row.get('createdAt','')))
        print(f'{sid} | {title} | turns {tc} | {updated}')

def _cmdLoad(sess,pickId,arg):
    if not arg:
        print('usage: /load <sessionId>')
        return None,sess
    meta=store.getSessionMeta(sess.indexFile,arg)
    if not meta:
        print(f'session not found: {arg}')
        return None,sess
    try:
        newSess=ChatSession(sess.bot,sessionId=arg,resume=True,pickId=pickId)
    except SystemExit as exc:
        print(exc)
        return None,sess
    title=(newSess.headline or '').strip()
    hint=f' | {title}' if title else ''
    print(f'loaded {newSess.sessionId}{hint} | turnCount {newSess.turnCount}')
    return None,newSess

def _cmdReset(sess,pickId):
    newSess=ChatSession(sess.bot,resume=False,pickId=pickId)
    print(f'new session {newSess.sessionId}')
    return None,newSess

def _cmdExport(sess,arg):
    if not arg:
        print('usage: /export <path>')
        return None,sess
    title=(sess.headline or '').strip() or '(untitled)'
    store.exportSessionMarkdown(
        arg,
        botName=sess.botName,
        sessionId=sess.sessionId,
        title=title,
        turnCount=sess.turnCount,
        sessionPath=sess.sessionPath,
    )
    print(f'exported to {arg}')
    return None,sess

def _cmdTitle(sess,arg):
    if not arg:
        print('usage: /title <text>')
        return None,sess
    titleMax=sess.humpyCfg['sessionTitleMaxChars']
    title=arg.strip()[:titleMax]
    if sess.humpyCfg['saveSessions']:
        store.updateIndexHeadline(sess.indexFile,sess.sessionId,title)
    sess.headline=title
    sess.needsHeadline=False
    print(f'title: {title}')
    return None,sess

def dispatch(line,sess,pickId=None,listLimit=20):
    '''Returns (shouldExit, session).'''
    parts=shlex.split(line)
    cmd=(parts[0] or '').lower()
    arg=' '.join(parts[1:]).strip() if len(parts)>1 else ''
    if cmd in ('/exit','/quit'):
        return True,sess
    if cmd=='/help':
        print(_helpText())
        return False,sess
    if cmd=='/status':
        _cmdStatus(sess)
        return False,sess
    if cmd=='/sessions':
        _cmdSessions(sess,listLimit)
        return False,sess
    if cmd=='/load':
        return _cmdLoad(sess,pickId,arg)
    if cmd=='/reset':
        return _cmdReset(sess,pickId)
    if cmd=='/export':
        return _cmdExport(sess,arg)
    if cmd=='/title':
        return _cmdTitle(sess,arg)
    print(f'unknown command: {cmd}  (/help for list)')
    return False,sess

def isCommand(line):
    return (line or '').strip().startswith('/')
