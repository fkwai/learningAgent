def _openaiToolsNested(tools):
    return [
        {
            'type':'function',
            'function':{
                'name':t['function']['name'],
                'description':t['function']['description'],
                'parameters':t['function']['parameters'],
            },
        }
        for t in tools
    ]


def _openaiToolsFlat(tools):
    return [
        {
            'type':'function',
            'function':{
                'name':t['name'],
                'description':t['description'],
                'parameters':t['parameters'],
            },
        }
        for t in tools
    ]


def _anthropicToolsNested(tools):
    out=[]
    for t in tools:
        fn=t['function']
        out.append({
            'name':fn['name'],
            'description':fn['description'],
            'input_schema':fn['parameters'],
        })
    return out


def _anthropicToolsFlat(tools):
    return [
        {
            'name':t['name'],
            'description':t['description'],
            'input_schema':t['parameters'],
        }
        for t in tools
    ]


def executeOneRound(*,sdk,modelRow,messages,system,tools,toolShape,maxOutputTokens,temperature,transportTag):
    sdk=sdk.lower()
    if sdk=='openai':
        raw=_callOpenai(
            modelRow=modelRow,
            messages=messages,
            tools=tools,
            toolShape=toolShape,
            maxOutputTokens=maxOutputTokens,
            temperature=temperature,
        )
        raw['_transport']=transportTag+'_openai'
        return raw
    raw=_callAnthropic(
        modelRow=modelRow,
        messages=messages,
        system=system,
        tools=tools,
        toolShape=toolShape,
        maxOutputTokens=maxOutputTokens,
        temperature=temperature,
    )
    raw['_transport']=transportTag+'_anthropic'
    return raw


def _callOpenai(*,modelRow,messages,tools,toolShape,maxOutputTokens,temperature):
    from openai import OpenAI
    apiTools=_openaiToolsNested(tools) if toolShape=='nested' else _openaiToolsFlat(tools)
    client=OpenAI(
        api_key=modelRow.get('apiKey'),
        base_url=(modelRow.get('baseUrl') or {}).get('openai'),
    )
    resp=client.chat.completions.create(
        model=modelRow.get('model'),
        messages=messages,
        tools=apiTools,
        tool_choice='auto',
        max_tokens=maxOutputTokens,
        temperature=temperature,
    )
    msg=resp.choices[0].message
    return {
        'id':resp.id,
        'model':resp.model,
        'message':{
            'role':msg.role,
            'content':msg.content,
            'tool_calls':[
                {
                    'id':tc.id,
                    'type':tc.type,
                    'function':{'name':tc.function.name,'arguments':tc.function.arguments},
                }
                for tc in (msg.tool_calls or [])
            ],
        },
        'usage':{
            'prompt_tokens':getattr(resp.usage,'prompt_tokens',None),
            'completion_tokens':getattr(resp.usage,'completion_tokens',None),
        },
    }


def _callAnthropic(*,modelRow,messages,system,tools,toolShape,maxOutputTokens,temperature):
    from anthropic import Anthropic
    apiTools=_anthropicToolsNested(tools) if toolShape=='nested' else _anthropicToolsFlat(tools)
    client=Anthropic(
        api_key=modelRow.get('apiKey'),
        base_url=(modelRow.get('baseUrl') or {}).get('anthropic'),
    )
    resp=client.messages.create(
        model=modelRow.get('model'),
        max_tokens=maxOutputTokens,
        system=system,
        messages=messages,
        tools=apiTools,
        temperature=temperature,
    )
    blocks=[]
    toolUses=[]
    for b in resp.content:
        if b.type=='text':
            blocks.append({'type':'text','text':b.text})
        elif b.type=='tool_use':
            toolUses.append({'id':b.id,'name':b.name,'input':b.input})
    return {
        'id':resp.id,
        'model':resp.model,
        'stop_reason':resp.stop_reason,
        'content_blocks':blocks,
        'tool_uses':toolUses,
        'usage':{
            'input_tokens':resp.usage.input_tokens,
            'output_tokens':resp.usage.output_tokens,
        },
    }
