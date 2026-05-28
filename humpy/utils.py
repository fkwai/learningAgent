import secrets
from datetime import datetime,timezone

def fmtTs(ts):
    s=(ts or '').strip()
    if not s:
        return ''
    try:
        if s.endswith('Z'):
            s=s[:-1]+'+00:00'
        dt=datetime.fromisoformat(s)
        return dt.strftime('%Y-%m-%dT%H:%M:%S')
    except ValueError:
        pass
    base=s.split('+')[0].split('Z')[0]
    if '.' in base:
        base=base.split('.')[0]
    return base[:19]

def newSessionId(prefix=''):
    '''UTC id: YYMMDDHHMM-hex4 (optional prefix for scripts).'''
    stamp=datetime.now(timezone.utc).strftime('%y%m%d%H%M')
    code=secrets.token_hex(2)
    sid=f'{stamp}-{code}'
    if prefix:
        return f'{prefix}{sid}'
    return sid
