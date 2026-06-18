import json


def parseFirstAction(raw,textKind='assistant_text'):
    if not raw:
        return {'kind':'unknown'}
    if raw.get('message',{}).get('tool_calls'):
        return {
            'kind':'tool_calls',
            'calls':[
                {'name':tc['function']['name'],'arguments':tc['function']['arguments']}
                for tc in raw['message']['tool_calls']
            ],
        }
    if raw.get('tool_uses'):
        return {
            'kind':'tool_calls',
            'calls':[
                {'name':tu['name'],'arguments':json.dumps(tu['input'],ensure_ascii=False)}
                for tu in raw['tool_uses']
            ],
        }
    text=''
    if raw.get('message',{}).get('content'):
        text=raw['message']['content'] or ''
    elif raw.get('content_blocks'):
        text='\n'.join(b.get('text','') for b in raw['content_blocks'] if b.get('type')=='text')
    if text.strip():
        return {'kind':textKind,'content':text.strip()}
    return {'kind':'unknown','raw_keys':list(raw.keys())}
