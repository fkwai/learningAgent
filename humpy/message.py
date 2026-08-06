def complete(modelCfg,sdk,message,system,maxToken=None,temperature=None):
    sdk=sdk.lower()
    if maxToken is None:
        maxToken=1024
    if sdk=='openai':
        return _completeOpenai(modelCfg,message,system,maxToken,temperature)
    return _completeAnthropic(modelCfg,message,system,maxToken,temperature)

def _completeAnthropic(modelCfg,message,system,maxToken,temperature):
    from anthropic import Anthropic
    kwarg={
        'model':modelCfg.get('model'),
        'max_tokens':maxToken,
        'system':system,
        'messages':message,
    }
    if temperature is not None:
        kwarg['temperature']=temperature
    client=Anthropic(
        api_key=modelCfg.get('apiKey'),
        base_url=modelCfg.get('baseUrl',{}).get('anthropic'),
    )
    resp=client.messages.create(**kwarg)
    usage=None
    if resp.usage:
        usage={'prompt':resp.usage.input_tokens,'completion':resp.usage.output_tokens}
    out=[]
    for block in resp.content:
        if block.type=='text':
            out.append(block.text)
    return {'text':'\n'.join(out).strip(),'usage':usage}

def _completeOpenai(modelCfg,message,system,maxToken,temperature):
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
    resp=client.chat.completions.create(**kwarg)
    usage=None
    if resp.usage:
        usage={'prompt':resp.usage.prompt_tokens,'completion':resp.usage.completion_tokens}
    text=(resp.choices[0].message.content or '').strip()
    return {'text':text,'usage':usage}
