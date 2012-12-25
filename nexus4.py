#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import urllib2
import smtplib
import sqlite3 as lite
from email.mime.text import MIMEText

ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
it_ready = "Google Nexus 4 is Ready! %s" % ctime
me = "money@eyelu.com"
you = "ryan.qian@gmail.com"


def emailit():
    print "%s doing the sending email..." % ctime
    mail_content = "Google Nexus 4 is Ready! %s" % ctime
    msg = MIMEText(mail_content)

    msg['Subject'] = mail_content
    msg['From'] = me
    msg['To'] = you

    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    s.quit()


def main():

    URL = "https://play.google.com/store/devices/details?id=nexus_4_8gb"
    r = urllib2.urlopen(URL).readlines()
    p = ''.join(r)

    try:
        con = lite.connect('DB/nexus4.db')
        cur = con.cursor()

        if "Sold out" not in p:
            cur.execute("select count(id) from haveit;")
            # how many times we have send the email
            email_times = cur.fetchall()[0][0]

            cur.execute("select count(content) from log;")
            # how many times we have log it
            log_times = cur.fetchall()[0][0]

            CMD = """INSERT INTO  log VALUES("%s");
                    INSERT INTO  haveit VALUES(1);
                """ % it_ready
            cur.executescript(CMD)
            con.commit()

            # don't send more than 3 emails, I don't want to spam
            if email_times < 3:
                emailit()

            # Clean up log table
            if log_times > 1000:
                CMD = "delete from log;"
                cur.executescript(CMD)
                con.commit()

        else:
            not_ready = "%s do nothing" % ctime
            CMD = """INSERT INTO  log VALUES("%s"); """ % not_ready
            cur.executescript(CMD)
            con.commit()
            print not_ready

    except lite.Error, e:

        if con:
            con.rollback()
        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        if con:
            con.close()


if __name__ == '__main__':
    main()
