# thin demo: same as humpy chat with bot main (pip install -e . first)
from humpy.chatSession import ChatSession

botName='main'
sess=ChatSession(botName)
print('chatLoop | bot',botName,'| session',sess.sessionId,'| exit to quit')
while True:
    userText=input('you> ').strip()
    if not userText:
        continue
    if userText.lower() in ('exit','quit'):
        break
    out=sess.turn(userText)
    print('assistant>',out['text'])
    if out.get('usage'):
        print('  tokens:',out['usage'])
print('saved',sess.sessionPath)
