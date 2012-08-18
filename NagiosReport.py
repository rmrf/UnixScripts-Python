#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: Qian, Ryan
    Date: 18-Aug-2012

    This script is used for generate Nagios report for last7days
    usage:
        NagiosReport.py <username> <password>

    username and password are used for auth regarding Nagios cgi
    It will generate PDF files at currently directory
    Please change username/passwords/nagios_hosts for different env

    NOTE: this script need xhtml2pdf module for create PDF file

"""

import os
import re
import sys
import base64
import urllib2
import cStringIO
import datetime
import xhtml2pdf.pisa as pisa


# our Nagios host need auth to get data from cgi
# TODO: create role account in nagios for this report purpose

username = sys.argv[1]
password = sys.argv[2]
# all hosts
hostgroup = "all"
# last week
timeperiod = "last7days"

nagios_hosts = ["nagios.abc.com", "crp-nagios01.abc.com"]

# we bypass this kind of host, as they are good one
good_boy = "<td CLASS='hostUP'>100.000% (100.000%)</td><td CLASS='hostDOWN'>" \
    "0.000% (0.000%)</td><td CLASS='hostUNREACHABLE'>0.000% (0.000%)</td>"


# Get today's work
def get_today():
    td = datetime.date.today()
    return str(td.year) + "-" + str(td.month) + "-" + str(td.day)

today = get_today()


# convert HTML to pdf file
def HTML2PDF(data, filename, open=False):
    print "Generating PDF file"
    pisa.CreatePDF(cStringIO.StringIO(data), file(filename, "wb"))

    #if open and (not pdf.err):
        #os.startfile(str(filename))

    #return not pdf.err


def main():
    for nagios_host in nagios_hosts:
        pdf_name = today + "_" + nagios_host + "_" + hostgroup + ".pdf"
        temp_file = "/tmp/nagios_temp_%s_%s.html" % (nagios_host, hostgroup)

        nagios_uri = "%s/nagios/cgi-bin/avail.cgi" % (nagios_host)

        # long url ...
        url = "http://%s?show_log_entries=&hostgroup=%s&timeperiod=%s" \
            "&assumeinitialstates=yes&assumestateretention=yes" \
            "&assumestatesduringnotrunning=yes&includesoftstates=no" \
            "&initialassumedhoststate=3&initialassumedservicestate=6&backtrack=4" \
            % (nagios_uri, hostgroup, timeperiod)

        # Get the data from nagios host
        print "Getting data from %s for hostgroup %s " % (nagios_host, hostgroup)
        # if Nagios cgi need auth to get report data
        if username:
            request = urllib2.Request(url)
            base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
            r = urllib2.urlopen(request).readlines()
        # no need auth
        else:
            r = urllib2.urlopen(url).readlines()

        html_content = []
        aver_dict = []

        # filter the content, skip the Good boy and keep Average entry
        for line in r:
            if good_boy not in line or "Average" in line:
                html_content.append(line.rstrip())
                if "Average" in line:
                    p = re.compile('\d+.\d+%')
                    aver_up = p.findall(line)[1]
                    aver_dict.append(aver_up)

        try:
            aver_f = [float(i.rstrip("%")) for i in aver_dict]
            aver_all = sum(aver_f) / len(aver_f)
            all_record = "\n<center><h2>Average for All hosts: %.4f" % (aver_all) + \
                "% </h2></center>\n"
            #print all_record
            html_content.append(all_record)

            with open(temp_file, 'w') as f:
                f.write(''.join(html_content))
            f.close()

            with open(temp_file, 'r') as f:
                data = f.read()
                # Generate the pdf file
                HTML2PDF(data, pdf_name, open=False)

            f.close()
        except:
            print "Failed to open tempfile"
        finally:
            os.remove(temp_file)


if __name__ == "__main__":
    main()
