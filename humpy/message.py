from anthropic import Anthropic
from openai import OpenAI

def complete(modelCfg,sdk,messages,system,maxTokens=None,temperature=None):
    sdk=sdk.lower()
    if maxTokens is None:
        maxTokens=1024
    if sdk=='openai':
        return _completeOpenai(modelCfg,messages,system,maxTokens,temperature)
    return _completeAnthropic(modelCfg,messages,system,maxTokens,temperature)

def _completeAnthropic(modelCfg,messages,system,maxTokens,temperature):
    kwargs={
        'model':modelCfg.get('model'),
        'max_tokens':maxTokens,
        'system':system,
        'messages':messages,
    }
    if temperature is not None:
        kwargs['temperature']=temperature
    client=Anthropic(
        api_key=modelCfg.get('apiKey'),
        base_url=modelCfg.get('baseUrl',{}).get('anthropic'),
    )
    resp=client.messages.create(**kwargs)
    usage=None
    if resp.usage:
        usage={'prompt':resp.usage.input_tokens,'completion':resp.usage.output_tokens}
    out=[]
    for block in resp.content:
        if block.type=='text':
            out.append(block.text)
    return {'text':'\n'.join(out).strip(),'usage':usage}

def _completeOpenai(modelCfg,messages,system,maxTokens,temperature):
    client=OpenAI(
        api_key=modelCfg.get('apiKey'),
        base_url=modelCfg.get('baseUrl',{}).get('openai'),
    )
    apiMessages=[{'role':'system','content':system}]
    apiMessages.extend(messages)
    kwargs={
        'model':modelCfg.get('model'),
        'max_tokens':maxTokens,
        'messages':apiMessages,
    }
    if temperature is not None:
        kwargs['temperature']=temperature
    resp=client.chat.completions.create(**kwargs)
    usage=None
    if resp.usage:
        usage={'prompt':resp.usage.prompt_tokens,'completion':resp.usage.completion_tokens}
    text=(resp.choices[0].message.content or '').strip()
    return {'text':text,'usage':usage}
