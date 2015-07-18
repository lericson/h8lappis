
import os
import sys
import shelve
import subprocess
from datetime import datetime, timedelta
from contextlib import closing
from email.mime.text import MIMEText

import jinja2


proj_path = os.path.dirname(__file__)
db_path = os.path.join(proj_path, 'db.shelve')


def connect_db():
    return shelve.open(db_path)


def desirable(obj):
    return 'student' in obj['labels']


def iter_new(db, providers=['sthlm']):
    provider_mods = map(__import__, providers)
    objs = (obj for p in provider_mods for obj in p.iter())

    for obj in objs:
        key = obj['permalink']
        if key not in db:
            db[key] = obj
            if desirable(obj):
                yield obj


def soon(d, delta=timedelta(days=5)):
    return (datetime.today().date() - d) <= delta


def render_notification(new_objs):
    loader = jinja2.FileSystemLoader(proj_path)
    env = jinja2.Environment(loader=loader)
    env.tests['soon'] = soon
    tmpl = env.get_template('notif.html')
    return tmpl.render({'objects': new_objs})


def format_email(new_objs):
    msg = MIMEText(render_notification(new_objs), 'html', 'utf-8')
    msg['Subject'] = '#h8lappis: {} nya objekt'.format(len(new_objs))
    msg['To'] = ('Ludvig Ericson <ludvig@lericson.se>, '
                 'Marie Kindblom <mariekindblom@hotmail.com>')
    msg['From'] = 'h8lappis <h8lappis@lericson.se>'
    return msg.as_string()


def sendmail(data, from_='h8lappis@lericson.se'):
    p = subprocess.Popen(['/usr/sbin/sendmail', '-t', '-f', from_],
                         stdin=subprocess.PIPE,
                         stdout=sys.stdout,
                         stderr=sys.stderr)
    p.stdin.write(data.encode('utf-8'))
    p.stdin.close()
    if p.wait():
        raise RuntimeError('blah')


def main():
    with closing(connect_db()) as db:
        new = list(iter_new(db))
        if new:
            sendmail(format_email(new))


if __name__ == "__main__":
    main()
