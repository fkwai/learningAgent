import argparse

from humpy.bot import Bot
from humpy.commands import dispatch,isCommand
from humpy.memory.store import loadIndexEntries,sessionTurnCount
from humpy.config import loadAgentCfg
from humpy.utils import fmtTs

RESERVED_BOT_INPUT={'new','others'}

def primaryBots(allBots,defaultBot,n):
    primary=[]
    if defaultBot in allBots and not Bot.isReserved(defaultBot):
        primary.append(defaultBot)
    for b in allBots:
        if b in primary or Bot.isReserved(b):
            continue
        primary.append(b)
        if len(primary)>=n:
            break
    return primary

def pickNewBot():
    while True:
        name=input('new bot name> ').strip()
        bot=Bot.adopt(name)
        if bot:
            return bot
        print('cannot use "new" or "others" as a bot name')

def pickFromOthers(primary,allBots,limit):
    rest=[b for b in allBots if b not in primary and not Bot.isReserved(b)][:limit]
    if not rest:
        print('no other bots')
        return None
    print('other bots:',', '.join(rest))
    while True:
        pick=input('bot name> ').strip()
        if not pick:
            return None
        if pick.lower() in RESERVED_BOT_INPUT:
            print('pick a bot name from the list above')
            continue
        bot=Bot.adopt(pick)
        if bot:
            return bot

def pickBotInteractive(cfg):
    allBots=Bot.listNames()
    primary=primaryBots(allBots,cfg['defaultBot'],cfg['primaryBotShow'])
    if primary:
        shown=', '.join(primary)
    else:
        shown='(none yet)'
    print(f'who you want to talk to, {shown} or others or new ?')
    while True:
        pick=input('> ').strip()
        if not pick:
            bot=Bot.adopt(cfg['defaultBot'])
            if bot:
                return bot
            print('default bot name is reserved; pick another')
            continue
        pl=pick.lower()
        if pl=='new':
            bot=pickNewBot()
            if bot:
                return bot
            continue
        if pl=='others':
            bot=pickFromOthers(primary,allBots,cfg['othersBotLimit'])
            if bot:
                return bot
            continue
        bot=Bot.adopt(pick)
        if bot:
            return bot

def pickBot(argBot,cfg):
    if argBot:
        if Bot.isReserved(argBot):
            raise SystemExit('bot name cannot be "new" or "others"')
        bot=Bot.adopt(argBot)
        if not bot:
            raise SystemExit('invalid bot name')
        return bot
    return pickBotInteractive(cfg)

def pickSession(bot,argNew,argResume,menuLimit):
    if argResume:
        return argResume,True
    if argNew:
        return None,False
    entries=loadIndexEntries(bot.indexFile,limit=menuLimit)
    entries=list(reversed(entries))
    print('0. new session')
    for i,e in enumerate(entries,1):
        hl=(e.get('headline') or '').strip() or '(untitled)'
        sid=e.get('sessionId') or ''
        ts=fmtTs(e.get('createdAt'))
        sp=e.get('sessionFile') or ''
        tc=sessionTurnCount(sp) if sp else e.get('turnCount',0)
        print(f'{i}. {hl} | {sid} | turns {tc} | {ts}')
    maxPick=len(entries)
    pick=input(f'pick 0-{maxPick}> ').strip()
    if pick in ('','0'):
        return None,False
    if pick.isdigit():
        n=int(pick)
        if n==0:
            return None,False
        if 1<=n<=len(entries):
            return entries[n-1]['sessionId'],True
    print('invalid pick; starting new session')
    return None,False

def cmdChat(args):
    from humpy.session import ChatSession
    cfg=loadAgentCfg()
    bot=pickBot(args.bot,cfg)
    sessionId,resume=pickSession(bot,args.new,args.resume,cfg['sessionMenuLimit'])
    sess=ChatSession(bot,sessionId=sessionId,resume=resume,pickId=args.model_id)
    mode='resume' if resume else 'new'
    titleHint=f" | {sess.headline}" if sess.headline else ''
    listLimit=cfg.get('sessionsListLimit',cfg['sessionMenuLimit'])
    print(f'humpy chat | bot {bot.name} | {mode} | session {sess.sessionId}{titleHint}')
    print('message or /help')
    while True:
        userText=input('you> ').strip()
        if not userText:
            continue
        if isCommand(userText):
            shouldExit,sess=dispatch(userText,sess,pickId=args.model_id,listLimit=listLimit)
            if shouldExit:
                break
            continue
        if userText.lower() in ('exit','quit'):
            break
        maxTok=args.max_tokens
        out=sess.turn(userText,maxTokens=maxTok)
        print('assistant>',out['text'])
        if out.get('headline'):
            print('  title:',out['headline'])
        if out.get('usage'):
            print('  tokens:',out['usage'])
    print('saved',sess.sessionPath)

def main():
    parser=argparse.ArgumentParser(prog='humpy',description='Humpy AI agent CLI')
    parser.add_argument('--bot',default=None,help='bot name (.data/<bot>/)')
    parser.add_argument('--new',action='store_true',help='force new session')
    parser.add_argument('--resume',default=None,metavar='SESSION_ID',help='resume session id')
    parser.add_argument('--model-id',default=None,help='override model id from bot.json')
    parser.add_argument('--max-tokens',type=int,default=None,help='override maxOutputTokens from config')
    args=parser.parse_args()
    if args.new and args.resume:
        raise SystemExit('use --new or --resume, not both')
    cmdChat(args)
