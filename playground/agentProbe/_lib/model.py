from humpy.config import loadAgentCfg,loadModel


def loadProbeModel(modelId):
    modelRow=loadModel(modelId)
    agentCfg=loadAgentCfg()
    botProf=agentCfg.get('defaultBotProfile',{})
    if not modelRow.get('sdk'):
        modelRow['sdk']=botProf.get('sdk','anthropic')
    return modelRow,botProf
