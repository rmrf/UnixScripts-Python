#!/usr/bin/python
"""
    This script is used for generate Nagios report for last24hours
    usage:
        NagiosReport.py


"""

import re
import base64
import urllib2
import datetime
#import xhtml2pdf.pisa as pisa


# our Nagios host need auth to get data from cgi
# TODO: create role account in nagios for this report purpose

username = ""
password = ""
# all hosts
hostgroup = "all"
hosts = "all"
#hostgroup = "BuildFarm-Win"
# last week
timeperiod = "last24hours"

nagios_host = "nagios.example.com"

# we bypass this kind of host, as they are good one
good_boy = "<td CLASS='hostUP'>100.000% (100.000%)</td><td CLASS='hostDOWN'>" \
    "0.000% (0.000%)</td><td CLASS='hostUNREACHABLE'>0.000% (0.000%)</td>"


# Get today's work
def get_today():
    td = datetime.date.today()
    month = "%.2d" % td.month
    day = "%.2d" % td.day
    return str(td.year) + str(month) + str(day)


def daily_avg():

    nagios_uri = "%s/nagios/cgi-bin/avail.cgi" % (nagios_host)
    host_up = {}

    # long url ...
    avgurl = "http://%s?show_log_entries=&host=%s&timeperiod=%s" \
        "&assumeinitialstates=yes&assumestateretention=yes" \
        "&assumestatesduringnotrunning=yes&includesoftstates=no" \
        "&initialassumedhoststate=3&initialassumedservicestate=6&backtrack=4" \
        % (nagios_uri, hosts, timeperiod)

    # Get the data from nagios host
    print "Getting data from %s for hosts %s " % (nagios_host, hosts)
    request = urllib2.Request(avgurl)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    r = urllib2.urlopen(request).readlines()


    # Get all hosts up statics , only care the UP number
    pup = re.compile(">(\S+)</a></td><td CLASS='hostUP'>(\S+)")

    for line in r:
        a = pup.findall(line)
        if a:
            hostname = a[0][0]
            up = a[0][1]
            host_up[hostname] = up

    # filter the content, skip the Good boy and keep Average entry
    for line in r:
        if "Average" in line:
            p = re.compile('\d+.\d+%')
            all_up = p.findall(line)[1]

    return all_up,host_up


def hostgroup_up():

    nagios_uri = "%s/nagios/cgi-bin/avail.cgi" % (nagios_host)

    # long url ...
    url = "http://%s?show_log_entries=&hostgroup=%s&timeperiod=%s" \
        "&assumeinitialstates=yes&assumestateretention=yes" \
        "&assumestatesduringnotrunning=yes&includesoftstates=no" \
        "&initialassumedhoststate=3&initialassumedservicestate=6&backtrack=4" \
        % (nagios_uri, hostgroup, timeperiod)

    # Get the data from nagios host
    print "Getting data from %s for hostgroup %s " % (nagios_host, hostgroup)
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    r = urllib2.urlopen(request).readlines()

    html_content = []
    aver_dict = []
    hg_dict = {}

    # filter the content, skip the Good boy and keep Average entry
    for line in r:
        if "Hostgroup '" in line or "Average" in line:

            #html_content.append(line.rstrip())
            if "Hostgroup '" in line:
                p = re.compile("Hostgroup\s+\'\S+\'")
                hg_name = p.findall(line)[0].split()[1].strip("'")
                #print hg_name, "hg_name....."
            elif "Average" in line:
                p = re.compile('\d+.\d+%')
                aver_up = p.findall(line)[1]
                aver_dict.append(aver_up)
                hg_dict[hg_name] = aver_up

    for key in hg_dict.keys():
        html_content.append("  " + key + "=" + hg_dict[key])

    return html_content


def main():

    today = get_today()
    temp_file = "/tmp/nagios_report.log"
    daily_static = "/data/nagios/reports/dailystatic.txt"

    # get the average up statics
    (all_up,host_up) = daily_avg()

    print "generate %s" % (daily_static)
    with open(daily_static, 'w') as f:
        f.write("date   "+ today+"\n")
        for k in sorted(host_up.keys()):
            f.write(k+"    "+host_up[k]+"\n")

    group_up = hostgroup_up()

    try:
        all_record = "  All_Hosts=%s" % (all_up) + "  collect_date=" + today

        group_up.append(all_record)
        #print group_up

        with open(temp_file, 'w') as f:
            f.write(''.join(group_up))
        f.close()

    except:
        print "Failed to open tempfile"
    finally:
        pass


if __name__ == "__main__":
    main()
