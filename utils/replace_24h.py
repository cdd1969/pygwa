#!/usr/bin python
# -*- coding: utf-8 -*-
import fileinput
import re
import datetime



def replace_and_standardize_date(fname, inplace=0):
    """ Function is able to treat <date 24:00:00> and convert it to <date+1day 00:00:00>,
        i.e.
        01/10/2014  24:00:00 >>> 02/10/2014 00:00:00
        31/12/2014  24:00:00 >>> 01/01/2015 00:00:00
        -----------------------------------------------------------------
        NOTE: it is highly reccomended to use <inplace=0> as a first step
        -----------------------------------------------------------------

        Note that the format of the passed string is HARDCODED by the regex pattern <p>:
            p = re.compile(r'''
                        (?P<space1>\s*)                # Skip leading whitespace
                        (?P<date>\d\d/\d\d/\d\d\d\d)   # date
                        (?P<space2>\s*)                # Whitespace
                        (?P<time>\d\d:\d\d:\d\d)       # time
                        (?P<else>.*?)\n                # everything else to end-of-line
                        ''', re.VERBOSE)
        
        This pattern has been written to match following string
            "01/10/2014  00:55:00    345,000000  Ued 41913,038194    -1,56   "

        If you would like to cahnge <p>, do not forget to change also <newline> definition:
            newline = p.sub(r'\g<space1>'+newDateStr+r'\g<space2>'+newTimeStr+r'\g<rests>', line)




        API:
            <inplace=0> - only SHOW replacement
            <inplace=1> - create backupfile and DO replacement

    """
    i = 0
    for line in fileinput.input(fname, inplace=inplace, backup='.bak'):
        i += 1
        if '24:00:00' in line:
            if inplace == 0:
                print i, ') ', line
            p = re.compile(r'''
                (?P<space1>\s*)                # Skip leading whitespace
                (?P<date>\d\d/\d\d/\d\d\d\d)   # date
                (?P<space2>\s*)                # Whitespace
                (?P<time>\d\d:\d\d:\d\d)       # time
                (?P<rests>.*?)\n                # everything else to end-of-line
                ''', re.VERBOSE)
            m = p.search(line)
            oldDatetimeStr = m.group('date')+' '+m.group('time')
            newDatetime = datetime.datetime.strptime(m.group('date'), '%d/%m/%Y')+datetime.timedelta(days=1)

            newDateStr  = datetime.datetime.strftime(newDatetime, '%d/%m/%Y')
            newTimeStr  = datetime.datetime.strftime(newDatetime, '%H:%M:%S')
            newDatetimeStr = newDateStr+' '+newTimeStr
            newline = p.sub(r'\g<space1>'+newDateStr+r'\g<space2>'+newTimeStr+r'\g<rests>', line)

            if inplace == 0:
                print "\t I have performed datetime conversion:", oldDatetimeStr, '>>>', newDatetimeStr
                print '\t old line:', line
                print '\t new line:', newline
                print '\t old line:', repr(line)
                print '\t new line:', repr(newline)

            if inplace == 1:
                print newline
        else:
            if inplace == 1:
                print re.sub(r'\n', '', line)



if __name__ == '__main__':
    fname = '/home/nck/prj/FARGE_project_work/data/farge_GW_data_ORIGINAL/Farge-GW6_HB-25_10min_071014_130415.all'
    replace_and_standardize_date(fname, inplace=0)