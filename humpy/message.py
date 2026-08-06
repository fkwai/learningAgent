import json

def complete(modelCfg,sdk,message,system,maxToken=None,temperature=None,toolLst=None):
    sdk=sdk.lower()
    if maxToken is None:
        maxToken=1024
    if sdk=='openai':
        return _completeOpenai(modelCfg,message,system,maxToken,temperature,toolLst)
    return _completeAnthropic(modelCfg,message,system,maxToken,temperature,toolLst)

def _openaiToolLst(toolLst):
    if not toolLst:
        return None
    return list(toolLst)

def _anthropicToolLst(toolLst):
    if not toolLst:
        return None
    out=[]
    for t in toolLst:
        fn=t.get('function') or t
        out.append({
            'name':fn['name'],
            'description':fn.get('description') or '',
            'input_schema':fn.get('parameters') or {'type':'object','properties':{}},
        })
    return out

def _completeAnthropic(modelCfg,message,system,maxToken,temperature,toolLst=None):
    from anthropic import Anthropic
    kwarg={
        'model':modelCfg.get('model'),
        'max_tokens':maxToken,
        'system':system,
        'messages':message,
    }
    if temperature is not None:
        kwarg['temperature']=temperature
    apiTool=_anthropicToolLst(toolLst)
    if apiTool:
        kwarg['tools']=apiTool
    client=Anthropic(
        api_key=modelCfg.get('apiKey'),
        base_url=modelCfg.get('baseUrl',{}).get('anthropic'),
    )
    resp=client.messages.create(**kwarg)
    usage=None
    if resp.usage:
        usage={'prompt':resp.usage.input_tokens,'completion':resp.usage.output_tokens}
    textPart=[]
    toolCall=[]
    rawBlock=[]
    for block in resp.content:
        if block.type=='text':
            textPart.append(block.text)
            rawBlock.append({'type':'text','text':block.text})
        elif block.type=='tool_use':
            arg=block.input if isinstance(block.input,dict) else {}
            toolCall.append({'id':block.id,'name':block.name,'arg':arg})
            rawBlock.append({'type':'tool_use','id':block.id,'name':block.name,'input':arg})
    return {
        'text':'\n'.join(textPart).strip(),
        'usage':usage,
        'toolCall':toolCall,
        '_sdk':'anthropic',
        '_assistantBlock':rawBlock,
    }

def _completeOpenai(modelCfg,message,system,maxToken,temperature,toolLst=None):
    from openai import OpenAI
    client=OpenAI(
        api_key=modelCfg.get('apiKey'),
        base_url=modelCfg.get('baseUrl',{}).get('openai'),
    )
    apiMessage=[{'role':'system','content':system}]
    apiMessage.extend(message)
    kwarg={
        'model':modelCfg.get('model'),
        'max_tokens':maxToken,
        'messages':apiMessage,
    }
    if temperature is not None:
        kwarg['temperature']=temperature
    apiTool=_openaiToolLst(toolLst)
    if apiTool:
        kwarg['tools']=apiTool
        kwarg['tool_choice']='auto'
    resp=client.chat.completions.create(**kwarg)
    usage=None
    if resp.usage:
        usage={'prompt':resp.usage.prompt_tokens,'completion':resp.usage.completion_tokens}
    msg=resp.choices[0].message
    text=(msg.content or '').strip()
    toolCall=[]
    toolCallWire=[]
    for tc in (msg.tool_calls or []):
        try:
            arg=json.loads(tc.function.arguments or '{}')
        except json.JSONDecodeError:
            arg={}
        toolCall.append({'id':tc.id,'name':tc.function.name,'arg':arg})
        toolCallWire.append({
            'id':tc.id,
            'type':'function',
            'function':{'name':tc.function.name,'arguments':tc.function.arguments or '{}'},
        })
    return {
        'text':text,
        'usage':usage,
        'toolCall':toolCall,
        '_sdk':'openai',
        '_assistantToolCall':toolCallWire,
        '_assistantContent':msg.content,
    }

def appendToolRound(sdk,message,completeResult,observationLst):
    '''Mutate message: append assistant tool-call turn + tool observations.'''
    sdk=(sdk or completeResult.get('_sdk') or '').lower()
    if sdk=='openai':
        _appendOpenaiToolRound(message,completeResult,observationLst)
    else:
        _appendAnthropicToolRound(message,completeResult,observationLst)

def _appendOpenaiToolRound(message,completeResult,observationLst):
    message.append({
        'role':'assistant',
        'content':completeResult.get('_assistantContent'),
        'tool_calls':completeResult.get('_assistantToolCall') or [],
    })
    for obs in observationLst:
        message.append({
            'role':'tool',
            'tool_call_id':obs['id'],
            'content':obs['content'],
        })

def _appendAnthropicToolRound(message,completeResult,observationLst):
    block=completeResult.get('_assistantBlock')
    if not block:
        block=[]
        if completeResult.get('text'):
            block.append({'type':'text','text':completeResult['text']})
        for tc in completeResult.get('toolCall') or []:
            block.append({
                'type':'tool_use',
                'id':tc['id'],
                'name':tc['name'],
                'input':tc.get('arg') or {},
            })
    message.append({'role':'assistant','content':block})
    message.append({
        'role':'user',
        'content':[
            {
                'type':'tool_result',
                'tool_use_id':obs['id'],
                'content':obs['content'],
            }
            for obs in observationLst
        ],
    })
