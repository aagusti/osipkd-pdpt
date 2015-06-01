from datetime import datetime
from urllib import unquote_plus
from urlparse import urlparse
from time import sleep
from types import StringType, UnicodeType
import re
import demon
import sys
import os
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
    
def rt_rw(s):
    s = s and s.strip() or ''
    s = re.sub('[-]', '/', s)
    t = s.split('/')
    if t[1:]: # Ada karakter / ?
        rt = t and t[0] or ''
        rw = t[1:] and t[1] or ''
    else:
        rt = s[:3]
        rw = s[3:]
    return rt.zfill(3), rw.zfill(3)

def clean(s):
    r = ''
    for ch in s:
        ascii = ord(ch)
        if ascii > 126 or ascii < 32:
            ch = ' '
        r += ch
    return r

def to_str(s):
    s = s or ''
    s = type(s) in [StringType, UnicodeType] and s or str(s)
    return clean(s)

def left(s, width):
    s = to_str(s)
    return s.ljust(width)[:width]

def right(s, width):
    s = to_str(s)
    return s.zfill(width)[:width]


class FixLength(object):
    def __init__(self, struct):
        self.set_struct(struct)

    def set_struct(self, struct):
        self.struct = struct
        self.fields = {}
        for s in struct:
            name = s[0]
            size = s[1:] and s[1] or 1
            typ = s[2:] and s[2] or 'A' # N: numeric, A: alphanumeric
            self.fields[name] = {'value': None, 'type': typ, 'size': size} 

    def set(self, name, value):
        self.fields[name]['value'] = value

    def get(self, name):
        return self.fields[name]['value']

    def __setitem__(self, name, value):
        self.set(name, value)        

    def __getitem__(self, name):
        return self.get(name)
 
    def get_raw(self):
        s = ''
        for name, size, typ in self.struct:
            v = self.fields[name]['value']
            pad_func = typ == 'N' and right or left
            if v and typ == 'N':
                i = int(v)
                if v == i:
                    v = i
            s += pad_func(v, size)
        return s

    def set_raw(self, raw):
        awal = 0
        for t in self.struct:
            name = t[0]
            size = t[1:] and t[1] or 1
            akhir = awal + size
            value = raw[awal:akhir]
            if not value:
                return
            self.set(name, value)
            awal += size
        return True

    def from_dict(self, d):
        for name in d:
            value = d[name]
            self.set(name, value)
