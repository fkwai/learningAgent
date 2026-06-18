# Single source of truth for probe paths. Entry scripts load this file by PATHS_PY
# (importlib), then call setup_sys_path(agent).

PATHS_PY=r'D:/git/learningAgent/playground/agentProbe/_lib/paths.py'
ROOT=r'D:/git/learningAgent'
AGENT_PROBE=f'{ROOT}/playground/agentProbe'
LIB_PROBE=f'{AGENT_PROBE}/_lib'
CODEX_PROBE=f'{AGENT_PROBE}/codex'
XIAOBA_PROBE=f'{AGENT_PROBE}/xiaoba'
OUT_CODEX=f'{AGENT_PROBE}/out/codex'
OUT_XIAOBA=f'{AGENT_PROBE}/out/xiaoba'
DEFAULT_REPO=ROOT


def setup_sys_path(agent=None):
    import sys
    extra=[]
    if agent=='codex':
        extra=[CODEX_PROBE]
    elif agent=='xiaoba':
        extra=[XIAOBA_PROBE]
    for p in (*extra,ROOT,LIB_PROBE):
        if p not in sys.path:
            sys.path.insert(0,p)


def load(agent=None):
    setup_sys_path(agent)
    import sys
    return sys.modules[__name__]
