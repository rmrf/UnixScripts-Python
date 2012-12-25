#!/usr/bin/env python

#
# Send me email when Nexus 4 get rid if "Sold out" status
#

import urllib2
import smtplib
from email.mime.text import MIMEText
import time

ctime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


URL = "https://play.google.com/store/devices/details?id=nexus_4_8gb"

r = urllib2.urlopen(URL).readlines()
p = ''.join(r)
me = "ryan.qian@gmail.com"
you = "ryan.qian@gmail.com"

if "Sold out" not in p:
    print "%s doing the sending email..." % ctime

    mail_content = "Google Nexus 4 is Ready! %s" % ctime

    msg = MIMEText(mail_content)

    msg['Subject'] = mail_content
    msg['From'] = me
    msg['To'] = you

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    s.quit()

else:
    print "%s do nothing" % ctime
