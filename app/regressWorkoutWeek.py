# regression: Mon-Sun workout questions, 7 turns, jsonl memory
# run from repo root: python app/regressWorkoutWeek.py
import argparse

from humpy.session import ChatSession

days=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

parser=argparse.ArgumentParser(description='regression: workout week chat loop')
parser.add_argument('--model-id',default=None)
parser.add_argument('--max-tokens',type=int,default=1024)
args=parser.parse_args()

botName='regress-workout'
sess=ChatSession(botName,prefix='regress-',headline='workout plan Mon-Sun',pickId=args.model_id)
print('regress workout week | bot',botName,'|',sess.sessionId,'\n')

for day in days:
    userText=f'What is the workout plan for {day}?'
    print('user>',userText)
    out=sess.turn(userText,maxTokens=args.max_tokens)
    print('assistant>',out['text'])
    if out.get('usage'):
        print('  tokens:',out['usage'])
    print()

print('saved',sess.sessionPath)
