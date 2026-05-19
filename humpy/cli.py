import argparse

from humpy import ensureBotDirs,getBotIndexFile,listBots
from humpy.memory import loadIndexEntries
from humpy.chatSession import ChatSession
from humpy.humpyCfg import loadHumpyCfg

def pickBot(argBot):
    if argBot:
        ensureBotDirs(argBot)
        return argBot
    bots=listBots()
    print('bots:',', '.join(bots) if bots else '(none)')
    name=input('bot name> ').strip()
    if not name:
        name=loadHumpyCfg()['defaultBot']
    ensureBotDirs(name)
    return name

SESSION_MENU_LIMIT=5

def pickSession(botName,argNew,argResume):
    if argResume:
        return argResume,True
    if argNew:
        return None,False
    entries=loadIndexEntries(getBotIndexFile(botName),limit=SESSION_MENU_LIMIT)
    entries=list(reversed(entries))
    print('0. new session')
    for i,e in enumerate(entries,1):
        hl=(e.get('headline') or '').strip() or '(untitled)'
        print(f"  {i}. {hl} | {e.get('sessionId')} | {e.get('createdAt','')}")
    pick=input(f'pick 0-{SESSION_MENU_LIMIT}> ').strip()
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
    botName=pickBot(args.bot)
    sessionId,resume=pickSession(botName,args.new,args.resume)
    sess=ChatSession(botName,sessionId=sessionId,resume=resume,pickId=args.model_id)
    mode='resume' if resume else 'new'
    titleHint=f" | {sess.headline}" if sess.headline else ''
    print(f'humpy chat | bot {botName} | {mode} | session {sess.sessionId}{titleHint} | exit to quit')
    while True:
        userText=input('you> ').strip()
        if not userText:
            continue
        if userText.lower() in ('exit','quit'):
            break
        out=sess.turn(userText,maxTokens=args.max_tokens)
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
    parser.add_argument('--model-id',default=None,help='override model id from humpy.json')
    parser.add_argument('--max-tokens',type=int,default=1024)
    args=parser.parse_args()
    if args.new and args.resume:
        raise SystemExit('use --new or --resume, not both')
    cmdChat(args)
