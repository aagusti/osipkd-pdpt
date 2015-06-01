from datetime import datetime
from urllib import unquote_plus
from urlparse import urlparse
from time import sleep
import re
import demon
import sys
import signal


def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)

# Dibutuhkan MS SQL Server
def vs(s):
    return s and unicode(s).encode('utf-8') or None

def print_log(s, category='INFO'):
    print('%s %s %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
          category, s))
        
def is_odbc(driver):
    return driver.split('+')[-1] == 'pyodbc'

def extract_netloc(s): # sugiana:a@localhost:5432
    r = {}
    t = s.split('@')
    if t[1:]: # localhost:5432
        h = t[1].split(':')
        if h[1:]:
            r['port'] = int(h[1])
        r['host'] = h[0]
    auth = t[0].split(':')
    if auth[1:]:
        r['pass'] = auth[1]
    r['user'] = auth[0]
    return r

def extract_tds(s):
    items = s.split(';')
    r = {}
    for item in items:
        key, value = item.split('=')
        if key == 'UID':
            r['user'] = value
        elif key == 'PWD':
            r['pass'] = value
        elif key == 'Server':
            r['host'] = value
        elif key == 'Database':
            r['name'] = value
        elif key == 'Port':
            r['port'] = int(value)
    return r

def extract_db_url(db_url):
    p = urlparse(db_url)
    r = {'driver': p.scheme}
    if is_odbc(p.scheme):
        if p.query:
            s = p.query
        else:
            s = p.path.split('?')[-1]
        t = s.split('=')
        s = unquote_plus(t[1])    
        r.update(extract_tds(s))
        return r
    if p.netloc:
        r.update(extract_netloc(p.netloc))
    if p.path[1:]:
        r['name'] = p.path.lstrip('/')
    return r

def eng_profile(db_url):
    url = extract_db_url(db_url)
    return 'driver:%s user:%s host:%s port:%s database:%s' % (
        url['driver'], url['user'], url['host'], url['port'], url['name'])

def trigger_name(sql):
    sql = sql.lower().replace('\n', ' ')
    match = re.compile('trigger (.*) (after|before)').search(sql)
    return match and match.group(1)

def stop_daemon(pid_file):
    pid = demon.isLive(pid_file)
    if not pid:
        sys.exit()
    print('kill %d by signal' % pid)
    os.kill(pid, signal.SIGTERM)
    i = 0
    while i < 5:
        sleep(1)
        i += 1
        if not demon.isLive(pid_file):
            sys.exit()
    print('kill %d by force' % pid)
    os.kill(pid, signal.SIGKILL)
    sys.exit()
